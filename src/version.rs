use std::str::FromStr;
use std::{error, fmt};

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::pyclass::CompareOp;
use pyo3::types::PyTuple;

#[derive(Debug, Clone)]
pub struct InvalidVersion(String);

impl error::Error for InvalidVersion {}

impl fmt::Display for InvalidVersion {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        self.0.fmt(f)
    }
}

impl From<InvalidVersion> for PyErr {
    fn from(value: InvalidVersion) -> Self {
        PyValueError::new_err(value.0)
    }
}

#[derive(Debug, Clone, Copy)]
enum ReleaseLevel {
    Alpha,
    Beta,
    Candidate,
    Final,
}

impl FromStr for ReleaseLevel {
    type Err = InvalidVersion;
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s {
            "alpha" => Ok(Self::Alpha),
            "beta" => Ok(Self::Beta),
            "candidate" => Ok(Self::Candidate),
            "final" => Ok(Self::Final),
            _ => Err(InvalidVersion(format!("invalid release level '{s}'"))),
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
        format!("{}", self).into_py(py)
    }
}

#[pyclass(
    mapping,
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
    type Err = InvalidVersion;
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        fn from_str_impl(s: &str) -> Option<Version> {
            let (major, rest) = s.split_once('.')?;
            let (minor, rest) = rest.split_once('.')?;
            let (patch, rest) = rest.split_once('-').unwrap_or((rest, ""));

            let (releaselevel, serial) = if let Some(tuple) = rest.split_once('.') {
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

        from_str_impl(s).ok_or(InvalidVersion(format!("invalid version string {s}")))
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
    fn as_vec(&self) -> Vec<PyObject> {
        Python::with_gil(|py| {
            vec![
                self.major.into_py(py),
                self.minor.into_py(py),
                self.patch.into_py(py),
                self.releaselevel.into_py(py),
                self.serial.into_py(py),
            ]
        })
    }

    fn as_tuple(&self) -> Py<PyTuple> {
        Python::with_gil(|py| {
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
        })
    }

    pub fn pykeyset() -> Result<Self, InvalidVersion> {
        Self::from_str(env!("CARGO_PKG_VERSION"))
    }
}

#[pyclass]
pub struct VersionIter(std::vec::IntoIter<PyObject>);

#[pymethods]
impl Version {
    pub fn count(&self, value: &PyAny) -> PyResult<PyObject> {
        Python::with_gil(|py| self.as_tuple().call_method1(py, "count", (value,)))
    }

    pub fn index(
        &self,
        value: &PyAny,
        start: Option<&PyAny>,
        stop: Option<&PyAny>,
    ) -> PyResult<PyObject> {
        Python::with_gil(|py| {
            let start = start.unwrap_or(0_isize.into_py(py).into_ref(py));
            let stop = stop.unwrap_or(isize::MAX.into_py(py).into_ref(py));

            self.as_tuple()
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

    fn __richcmp__(&self, value: &PyAny, op: CompareOp) -> PyResult<PyObject> {
        let name = match op {
            CompareOp::Lt => "__lt__",
            CompareOp::Le => "__le__",
            CompareOp::Eq => "__eq__",
            CompareOp::Ne => "__ne__",
            CompareOp::Gt => "__gt__",
            CompareOp::Ge => "__ge__",
        };
        Python::with_gil(|py| self.as_tuple().call_method1(py, name, (value,)))
    }

    fn __len__(&self) -> PyResult<usize> {
        Python::with_gil(|py| self.as_tuple().call_method0(py, "__len__")?.extract(py))
    }

    fn __getitem__(&self, key: &PyAny) -> PyResult<PyObject> {
        Python::with_gil(|py| self.as_tuple().call_method1(py, "__getitem__", (key,)))
    }

    fn __concat__(&self, value: PyObject) -> PyResult<PyObject> {
        Python::with_gil(|py| self.as_tuple().call_method1(py, "__add__", (value,)))
    }

    fn __contains__(&self, key: PyObject) -> PyResult<bool> {
        Python::with_gil(|py| {
            self.as_tuple()
                .call_method1(py, "__contains__", (key,))?
                .extract(py)
        })
    }

    #[getter]
    fn __match_args__(&self) -> (&str, &str, &str, &str, &str) {
        ("major", "minor", "micro", "releaselevel", "serial")
    }

    fn __repeat__(&self, value: isize) -> PyResult<PyObject> {
        Python::with_gil(|py| self.as_tuple().call_method1(py, "__mul__", (value,)))
    }

    fn __iter__(slf: PyRef<Self>) -> VersionIter {
        VersionIter((*slf).as_vec().into_iter())
    }
}

#[pymethods]
impl VersionIter {
    fn __iter__(slf: PyRef<Self>) -> PyRef<Self> {
        slf
    }

    fn __next__(mut slf: PyRefMut<Self>) -> Option<PyObject> {
        slf.0.next()
    }
}
