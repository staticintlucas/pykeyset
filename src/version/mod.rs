mod built;

use std::collections::HashMap;
use std::ffi::c_long;
use std::str::FromStr;
use std::{error, fmt};

use pyo3::exceptions::{PyTypeError, PyValueError};
use pyo3::pyclass::CompareOp;
use pyo3::types::{PyDict, PyIterator, PySequence, PySlice, PySliceIndices, PyTuple};
use pyo3::{intern, prelude::*};

pub fn version() -> Result<Version, VersionError> {
    Version::from_str(built::PKG_VERSION)
}

pub fn build_info(py: Python) -> PyResult<Bound<'_, PyDict>> {
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

    pub fn index(
        slf: &Bound<'_, Self>,
        value: &Bound<'_, PyAny>,
        start: Option<&Bound<'_, PyAny>>,
        stop: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<usize> {
        let tuple = slf.to_tuple();
        let ilen = isize::try_from(tuple.len()).unwrap_or(isize::MAX);

        let start = if let Some(start) = start {
            let istart = if let Ok(start) = start.extract::<isize>() {
                start
            } else if start.hasattr("__index__")? {
                let index = start.call_method0("__index__")?;
                index
                    .extract::<isize>()
                    .or(Err(PyTypeError::new_err(format!(
                        "__index__ returned non-int (type {})",
                        typename(&index)
                    ))))?
            } else {
                Err(PyTypeError::new_err(
                    "slice indices must be integers or have an __index__ method",
                ))?
            };

            usize::try_from(if istart < 0 {
                isize::max(istart + ilen, 0)
            } else {
                istart
            })
            .expect("istart should always be >0")
        } else {
            0
        };

        let stop = if let Some(stop) = stop {
            let istop = if let Ok(stop) = stop.extract::<isize>() {
                stop
            } else if stop.hasattr("__index__")? {
                let index = stop.call_method0("__index__")?;
                index
                    .extract::<isize>()
                    .or(Err(PyTypeError::new_err(format!(
                        "__index__ returned non-int (type {})",
                        typename(&index)
                    ))))?
            } else {
                Err(PyTypeError::new_err(
                    "slice indices must be integers or have an __index__ method",
                ))?
            };

            usize::try_from(if istop < 0 {
                isize::max(istop + ilen, 0)
            } else {
                istop
            })
            .expect("istop should always be >0")
        } else {
            usize::MAX
        };

        tuple
            .get_slice(start, stop)
            .index(value)
            .map(|index| start + index)
            .map_err(|e| {
                if e.is_instance_of::<PyValueError>(tuple.py()) {
                    PyValueError::new_err("tuple.index(x): x not in tuple")
                } else {
                    e
                }
            })
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

    fn __getitem__<'py>(
        slf: &Bound<'py, Self>,
        index: Bound<'_, PyAny>,
    ) -> PyResult<Bound<'py, PyAny>> {
        // Yes I know there is a lot of conversion to/from isize/usize/c_long here, but that should
        // all be simplified when https://github.com/PyO3/pyo3/pull/3761 is merged
        let tuple = slf.to_tuple();
        let len = tuple.len();
        let ilen = isize::try_from(len).expect("length should be < isize::MAX");
        let llen = c_long::try_from(len).expect("length should be < c_long::MAX");

        if let Ok(slice) = index.downcast::<PySlice>() {
            let indices = slice.indices(llen)?;

            let PySliceIndices {
                start, stop, step, ..
            } = indices;

            let result = if let Ok(ustep) = usize::try_from(step) {
                PyTuple::new_bound(
                    slf.py(),
                    (start..stop).step_by(ustep).map(|idx| {
                        let idx = usize::try_from(idx).expect("index should not be negative");
                        tuple.get_item(idx).expect("get_item should always succeed")
                    }),
                )
            } else {
                let ustep = usize::try_from(-step).expect("negating a negative is always positive");
                PyTuple::new_bound(
                    slf.py(),
                    (start..stop).rev().step_by(ustep).map(|idx| {
                        let idx = usize::try_from(idx).expect("index should not be negative");
                        tuple.get_item(idx).expect("get_item should always succeed")
                    }),
                )
            };

            Ok(result.into_any())
        } else {
            let idx = if let Ok(idx) = index.extract::<isize>() {
                idx
            } else if index.hasattr("__index__")? {
                let idx = index.call_method0("__index__")?;
                idx.extract::<isize>().or(Err(PyTypeError::new_err(format!(
                    "__index__ returned non-int (type {})",
                    typename(&idx)
                ))))?
            } else {
                Err(PyTypeError::new_err(format!(
                    "tuple indices must be integers or slices, not {}",
                    typename(&index)
                )))?
            };

            let idx = if idx < 0 { idx + ilen } else { idx };

            tuple.get_item(usize::try_from(idx).unwrap_or(isize::MAX as usize))
        }
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

fn typename(slf: &Bound<'_, PyAny>) -> String {
    slf.get_type()
        .getattr(intern!(slf.py(), "__name__"))
        .map(|n| n.to_string())
        .unwrap_or("None".into())
}
