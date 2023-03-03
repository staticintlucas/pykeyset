mod built;

use std::collections::HashMap;
use std::convert::Into;
use std::str::FromStr;
use std::{error, fmt};

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::pyclass::CompareOp;
use pyo3::types::{PySequence, PyTuple};

pub fn version() -> Result<Version, VersionError> {
    Version::from_str(env!("CARGO_PKG_VERSION"))
}

pub fn dep_version(dep: &str) -> Result<Version, VersionError> {
    Version::from_str(
        built::DEPENDENCIES
            .into_iter()
            .collect::<HashMap<_, _>>()
            .get(dep)
            .ok_or(VersionError(format!("cannot determine version for {dep}")))?,
    )
}

// Error type errors parsing a version string
#[derive(Debug, Clone)]
pub struct VersionError(String);

impl error::Error for VersionError {}

impl fmt::Display for VersionError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        self.0.fmt(f)
    }
}

impl From<VersionError> for PyErr {
    fn from(value: VersionError) -> Self {
        PyValueError::new_err(value.0)
    }
}

// Release Level similar to what Python uses
#[derive(Debug, Clone, Copy)]
enum ReleaseLevel {
    Alpha,
    Beta,
    Candidate,
    Final,
}

impl FromStr for ReleaseLevel {
    type Err = VersionError;
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s {
            "alpha" => Ok(Self::Alpha),
            "beta" => Ok(Self::Beta),
            "candidate" => Ok(Self::Candidate),
            "final" => Ok(Self::Final),
            _ => Err(VersionError(format!("invalid release level '{s}'"))),
        }
    }
}

impl fmt::Display for ReleaseLevel {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let s = match &self {
            Self::Alpha => "alpha",
            Self::Beta => "beta",
            Self::Candidate => "candidate",
            Self::Final => "final",
        };
        write!(f, "{s}")
    }
}

impl IntoPy<PyObject> for ReleaseLevel {
    fn into_py(self, py: Python<'_>) -> PyObject {
        format!("{self}").into_py(py)
    }
}

// Reimplementation of sys.version_info's type
#[pyclass(
    sequence,
    get_all,
    frozen,
    module = "pykeyset",
    name = "__version_info__"
)]
#[derive(Debug, Clone, Copy)]
pub struct Version {
    major: u8,
    minor: u8,
    patch: u8,
    releaselevel: ReleaseLevel,
    serial: u8,
}

impl FromStr for Version {
    type Err = VersionError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        fn from_str_impl(s: &str) -> Option<Version> {
            let (major, rest) = s.split_once('.')?;
            let (minor, rest) = rest.split_once('.')?;
            let (patch, rest) = rest.split_once('-').unwrap_or((rest, ""));

            let (releaselevel, serial) = if rest.is_empty() {
                ("final", "0")
            } else if let Some(tuple) = rest.split_once('.') {
                tuple
            } else {
                rest.split_at(rest.find(char::is_numeric)?)
            };

            Some(Version {
                major: major.parse().ok()?,
                minor: minor.parse().ok()?,
                patch: patch.parse().ok()?,
                releaselevel: releaselevel.parse().ok()?,
                serial: serial.parse().ok()?,
            })
        }

        from_str_impl(s).ok_or(VersionError(format!("invalid version string {s}")))
    }
}

impl fmt::Display for Version {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let Self {
            major,
            minor,
            patch,
            releaselevel,
            serial,
        } = self;

        if let ReleaseLevel::Final = self.releaselevel {
            write!(f, "{major}.{minor}.{patch}")
        } else {
            write!(f, "{major}.{minor}.{patch}-{releaselevel}{serial}")
        }
    }
}

impl Version {
    fn as_tuple(&self, py: Python) -> Py<PyTuple> {
        PyTuple::new(
            py,
            [
                self.major.into_py(py),
                self.minor.into_py(py),
                self.patch.into_py(py),
                self.releaselevel.into_py(py),
                self.serial.into_py(py),
            ],
        )
        .into()
    }
}

#[pymethods]
impl Version {
    pub fn count(&self, value: &PyAny) -> PyResult<usize> {
        Python::with_gil(|py| self.as_tuple(py).as_ref(py).as_sequence().count(value))
    }

    pub fn index(
        &self,
        value: &PyAny,
        start: Option<&PyAny>,
        stop: Option<&PyAny>,
    ) -> PyResult<PyObject> {
        Python::with_gil(|py| {
            // TODO calling index here with call_method because PySequence::index doesn't take
            // start/stop values
            let start = start.unwrap_or(0_isize.into_py(py).into_ref(py));
            let stop = stop.unwrap_or(isize::MAX.into_py(py).into_ref(py));

            self.as_tuple(py)
                .call_method1(py, "index", (value, start, stop))
        })
    }

    fn __str__(&self) -> String {
        format!("{self}")
    }

    fn __repr__(&self) -> String {
        format!(
            "pykeyset.__version_info__(major={}, minor={}, patch={}, releaselevel='{}', serial={})",
            self.major, self.minor, self.patch, self.releaselevel, self.serial
        )
    }

    fn __richcmp__(&self, other: PyObject, compare_op: CompareOp) -> PyResult<PyObject> {
        Python::with_gil(|py| {
            self.as_tuple(py)
                .as_ref(py)
                .rich_compare(other, compare_op)
                .map(Into::into)
        })
    }

    fn __len__(&self) -> usize {
        Python::with_gil(|py| self.as_tuple(py).as_ref(py).len())
    }

    fn __getitem__(&self, index: usize) -> PyResult<PyObject> {
        Python::with_gil(|py| self.as_tuple(py).as_ref(py).get_item(index).map(Into::into))
    }

    fn __concat__(&self, other: &PySequence) -> PyResult<PyObject> {
        Python::with_gil(|py| {
            self.as_tuple(py)
                .as_ref(py)
                .as_sequence()
                .concat(other)?
                .tuple()
                .map(Into::into)
        })
    }

    fn __contains__(&self, value: PyObject) -> PyResult<bool> {
        Python::with_gil(|py| self.as_tuple(py).as_ref(py).contains(value))
    }

    #[getter]
    fn __match_args__(&self) -> (&str, &str, &str, &str, &str) {
        ("major", "minor", "micro", "releaselevel", "serial")
    }

    fn __repeat__(&self, count: usize) -> PyResult<PyObject> {
        Python::with_gil(|py| {
            self.as_tuple(py)
                .as_ref(py)
                .as_sequence()
                .repeat(count)?
                .tuple()
                .map(Into::into)
        })
    }

    fn __iter__(&self) -> PyResult<PyObject> {
        Python::with_gil(|py| {
            self.as_tuple(py)
                .as_ref(py)
                .as_sequence()
                .iter()
                .map(Into::into)
        })
    }
}
