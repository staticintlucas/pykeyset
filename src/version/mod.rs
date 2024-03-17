mod built;

use std::collections::HashMap;
use std::str::FromStr;
use std::{error, fmt};

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::pyclass::CompareOp;
use pyo3::types::{PyDict, PyIterator, PySequence, PyTuple};

pub fn version() -> Result<Version, VersionError> {
    Version::from_str(built::PKG_VERSION)
}

pub fn build_info<'py>(py: Python<'py>) -> PyResult<Bound<'py, PyDict>> {
    let dependencies: HashMap<_, _> = built::DEPENDENCIES.into_iter().collect();

    let build = PyDict::new_bound(py);
    build.set_item("build", {
        let bld = PyDict::new_bound(py);
        bld.set_item("version", built::RUSTC_VERSION)?;
        bld.set_item("host", built::HOST)?;
        bld.set_item("profile", built::PROFILE)?;
        bld.set_item("optimization", built::OPT_LEVEL)?;
        bld.set_item("debug", built::DEBUG)?;
        bld
    })?;
    build.set_item("target", {
        let tgt = PyDict::new_bound(py);
        tgt.set_item("triple", built::TARGET)?;
        tgt.set_item("arch", built::CFG_TARGET_ARCH)?;
        tgt.set_item("endianness", built::CFG_ENDIAN)?;
        tgt.set_item("os", built::CFG_OS)?;
        tgt.set_item("family", built::CFG_FAMILY)?;
        tgt.set_item("env", built::CFG_ENV)?;
        tgt
    })?;
    build.set_item("dependencies", {
        let deps = PyDict::new_bound(py);
        // Don't list all dependencies, just the important ones
        deps.set_item("keyset-rs", dependencies["keyset"])?;
        deps.set_item("pyo3", dependencies["pyo3"])?;
        deps
    })?;
    Ok(build)
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

trait VerConv<'py> {
    fn to_tuple(&self) -> Bound<'py, PyTuple>;
}

impl<'py> VerConv<'py> for Bound<'py, Version> {
    fn to_tuple(&self) -> Bound<'py, PyTuple> {
        PyTuple::new_bound(
            self.py(),
            [
                self.get().major.into_py(self.py()),
                self.get().minor.into_py(self.py()),
                self.get().patch.into_py(self.py()),
                self.get().releaselevel.into_py(self.py()),
                self.get().serial.into_py(self.py()),
            ],
        )
    }
}

#[pymethods]
impl Version {
    pub fn count(slf: &Bound<'_, Self>, value: &PyAny) -> PyResult<usize> {
        slf.to_tuple().as_sequence().count(value)
    }

    pub fn index<'py>(
        slf: &Bound<'py, Self>,
        value: &Bound<'_, PyAny>,
        start: Option<&Bound<'_, PyAny>>,
        stop: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        // TODO calling index here with call_method because PySequence::index doesn't take
        // start/stop values
        let zero = Python::with_gil(|py| 0_usize.into_py(py));
        let max = Python::with_gil(|py| usize::MAX.into_py(py));
        let start = start.unwrap_or(zero.bind(value.py()));
        let stop = stop.unwrap_or(max.bind(value.py()));

        slf.to_tuple().call_method1("index", (value, start, stop))
    }

    fn __str__(&self) -> String {
        self.to_string()
    }

    fn __repr__(&self) -> String {
        let Self {
            major,
            minor,
            patch,
            releaselevel,
            serial,
        } = self;
        format!(
            "pykeyset.__version_info__(major={major}, minor={minor}, patch={patch}, releaselevel='{releaselevel}', serial={serial})",
        )
    }

    fn __richcmp__<'py>(
        slf: &Bound<'py, Self>,
        other: &Bound<'_, PyAny>,
        compare_op: CompareOp,
    ) -> PyResult<Bound<'py, PyAny>> {
        slf.to_tuple().rich_compare(other, compare_op)
    }

    fn __len__(slf: &Bound<'_, Self>) -> usize {
        slf.to_tuple().len()
    }

    fn __getitem__<'py>(slf: &Bound<'py, Self>, index: &PyAny) -> PyResult<Bound<'py, PyAny>> {
        // TODO calling __getitem__ with call_method because PyTuple::get_item doesn't take
        // a slice object (note: we just need a bit of logic and call either get_item or get_slice)
        slf.to_tuple().call_method1("__getitem__", (index,))
    }

    fn __concat__<'py>(
        slf: &Bound<'py, Self>,
        other: &Bound<'_, PySequence>,
    ) -> PyResult<Bound<'py, PyTuple>> {
        slf.to_tuple().as_sequence().concat(other)?.to_tuple()
    }

    fn __contains__(slf: &Bound<'_, Self>, value: &PyAny) -> PyResult<bool> {
        slf.to_tuple().contains(value)
    }

    #[getter]
    fn __match_args__(&self) -> (&str, &str, &str, &str, &str) {
        ("major", "minor", "micro", "releaselevel", "serial")
    }

    fn __repeat__<'py>(slf: &Bound<'py, Self>, count: usize) -> PyResult<Bound<'py, PyTuple>> {
        slf.to_tuple().as_sequence().repeat(count)?.to_tuple()
    }

    fn __iter__<'py>(slf: &Bound<'py, Self>) -> PyResult<Bound<'py, PyIterator>> {
        slf.to_tuple().as_sequence().iter()
    }
}
