use std::fmt;

use indoc::formatdoc;
use pyo3::exceptions::{PyTypeError, PyValueError};
#[cfg(feature = "experimental-inspect")]
use pyo3::inspect::types::TypeInfo;
use pyo3::prelude::*;
use pyo3::pyclass::CompareOp;
use pyo3::types::{PyIterator, PySequence, PySlice, PySliceIndices, PyString, PyTuple};

shadow_rs::shadow!(shadow);

pub const VERSION: Version = const {
    let releaselevel = match shadow::PKG_VERSION_RELEASELEVEL {
        shadow::ReleaseLevel::Alpha => ReleaseLevel::Alpha,
        shadow::ReleaseLevel::Beta => ReleaseLevel::Beta,
        shadow::ReleaseLevel::Candidate => ReleaseLevel::Candidate,
        shadow::ReleaseLevel::Final => ReleaseLevel::Final,
    };
    Version {
        major: shadow::PKG_VERSION_MAJOR_INT,
        minor: shadow::PKG_VERSION_MINOR_INT,
        patch: shadow::PKG_VERSION_PATCH_INT,
        releaselevel,
        serial: shadow::PKG_VERSION_SERIAL,
    }
};
pub const VERSION_STR: &str = shadow::PKG_VERSION_STRING;

// Release Level similar to what Python uses
#[derive(Debug, Clone, Copy)]
enum ReleaseLevel {
    Alpha,
    Beta,
    Candidate,
    Final,
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

impl<'py> IntoPyObject<'py> for ReleaseLevel {
    type Target = PyString;
    type Output = Bound<'py, Self::Target>;
    type Error = std::convert::Infallible;

    fn into_pyobject(self, py: Python<'py>) -> Result<Self::Output, Self::Error> {
        format!("{self}").into_pyobject(py)
    }

    #[cfg(feature = "experimental-inspect")]
    fn type_output() -> TypeInfo {
        TypeInfo::builtin("str")
    }
}

#[cfg(feature = "test")]
impl<'py> FromPyObject<'py> for ReleaseLevel {
    #[cfg(feature = "experimental-inspect")]
    const INPUT_TYPE: &'static str = "typing.Any";

    fn extract_bound(ob: &Bound<'py, PyAny>) -> PyResult<Self> {
        let val = ob.extract::<String>()?;
        match &*val {
            "alpha" => Ok(Self::Alpha),
            "beta" => Ok(Self::Beta),
            "candidate" => Ok(Self::Candidate),
            "final" => Ok(Self::Final),
            _ => Err(PyValueError::new_err(format!(
                "invalid releaselevel str: '{val}'"
            ))),
        }
    }

    #[cfg(feature = "experimental-inspect")]
    fn type_input() -> TypeInfo {
        TypeInfo::builtin("str")
    }
}

// TODO: why is this needed to make PyO3 happy?
#[cfg(not(feature = "test"))]
impl<'py> FromPyObject<'py> for ReleaseLevel {
    #[cfg(feature = "experimental-inspect")]
    const INPUT_TYPE: &'static str = "typing.Any";

    fn extract_bound(_ob: &Bound<'py, PyAny>) -> PyResult<Self> {
        unimplemented!()
    }

    #[cfg(feature = "experimental-inspect")]
    fn type_input() -> TypeInfo {
        TypeInfo::builtin("str")
    }
}

// Reimplementation of sys.version_info's type
#[pyclass(sequence, get_all, frozen, module = "pykeyset", name = "version_info")]
#[derive(Debug, Clone, Copy)]
pub struct Version {
    major: u8,
    minor: u8,
    patch: u8,
    releaselevel: ReleaseLevel,
    serial: u8,
}

type VersionTuple = (u8, u8, u8, ReleaseLevel, u8);

impl Version {
    const fn to_tuple(self) -> VersionTuple {
        let Self {
            major,
            minor,
            patch,
            releaselevel,
            serial,
        } = self;
        (major, minor, patch, releaselevel, serial)
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

#[pymethods]
impl Version {
    /// We use this constructor so we can exercise version_info with a known
    /// fixed version number in our tests
    #[cfg(feature = "test")]
    #[new]
    #[allow(private_interfaces)]
    pub fn new(major: u8, minor: u8, patch: u8, releaselevel: ReleaseLevel, serial: u8) -> Self {
        Self {
            major,
            minor,
            patch,
            releaselevel,
            serial,
        }
    }

    #[pyo3(signature = (value, /))]
    pub fn count(slf: &Bound<'_, Self>, value: &Bound<'_, PyAny>) -> PyResult<usize> {
        slf.get()
            .to_tuple()
            .into_pyobject(slf.py())?
            .as_sequence()
            .count(value)
    }

    #[pyo3(signature = (value, start = None, end = None, /))]
    pub fn index(
        slf: &Bound<'_, Self>,
        value: &Bound<'_, PyAny>,
        start: Option<&Bound<'_, PyAny>>,
        end: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<usize> {
        let tuple = slf.get().to_tuple().into_pyobject(slf.py())?;
        let ilen = isize::try_from(tuple.len()).unwrap_or(isize::MAX);

        let start = if let Some(start) = start {
            // Note extract takes care of calling __index__ if required
            let istart = if let Ok(start) = start.extract::<isize>() {
                start
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

        let end = if let Some(end) = end {
            // Note extract takes care of calling __index__ if required
            let iend = if let Ok(end) = end.extract::<isize>() {
                end
            } else {
                Err(PyTypeError::new_err(
                    "slice indices must be integers or have an __index__ method",
                ))?
            };

            usize::try_from(if iend < 0 {
                isize::max(iend + ilen, 0)
            } else {
                iend
            })
            .expect("iend should always be >0")
        } else {
            usize::MAX
        };

        tuple
            .get_slice(start, end)
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

    fn __repr__(slf: &Bound<'_, Self>) -> PyResult<String> {
        let typename = slf.get_type().name()?;
        let module = slf.get_type().module()?;
        let &Self {
            major,
            minor,
            patch,
            releaselevel,
            serial,
        } = slf.get();
        Ok(format!(
            "{module}.{typename}(major={major}, minor={minor}, patch={patch}, \
                releaselevel='{releaselevel}', serial={serial})",
        ))
    }

    fn __richcmp__<'py>(
        slf: &Bound<'py, Self>,
        other: &Bound<'py, PyAny>,
        compare_op: CompareOp,
    ) -> PyResult<Bound<'py, PyAny>> {
        slf.get()
            .to_tuple()
            .into_pyobject(slf.py())?
            .rich_compare(other, compare_op)
    }

    fn __len__(slf: &Bound<'_, Self>) -> PyResult<usize> {
        Ok(slf.get().to_tuple().into_pyobject(slf.py())?.len())
    }

    fn __getitem__<'py>(
        slf: &Bound<'py, Self>,
        index: Bound<'_, PyAny>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let tuple = slf.get().to_tuple().into_pyobject(slf.py())?;
        let len = tuple.len();
        let ilen = isize::try_from(len).expect("length should be < isize::MAX");

        if let Ok(slice) = index.downcast::<PySlice>() {
            let indices = slice.indices(ilen)?;

            let PySliceIndices {
                start, stop, step, ..
            } = indices;

            let result = if let Ok(ustep) = usize::try_from(step) {
                PyTuple::new(
                    slf.py(),
                    (start..stop).step_by(ustep).map(|idx| {
                        let idx = usize::try_from(idx).expect("index should not be negative");
                        tuple.get_item(idx).expect("get_item should always succeed")
                    }),
                )?
            } else {
                let ustep = usize::try_from(-step).expect("negating a negative is always positive");
                let (start, stop) = (stop + 1, start + 1);
                PyTuple::new(
                    slf.py(),
                    (start..stop).rev().step_by(ustep).map(|idx| {
                        let idx = usize::try_from(idx).expect("index should not be negative");
                        tuple.get_item(idx).expect("get_item should always succeed")
                    }),
                )?
            };

            Ok(result.into_any())
        } else {
            // Note extract takes care of calling __index__ if required
            let idx = if let Ok(idx) = index.extract::<isize>() {
                idx
            } else {
                Err(PyTypeError::new_err(format!(
                    "tuple indices must be integers or slices, not {}",
                    index.get_type().getattr("__name__")?
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
        slf.get()
            .to_tuple()
            .into_pyobject(slf.py())?
            .into_sequence()
            .concat(other)?
            .to_tuple()
    }

    fn __contains__(slf: &Bound<'_, Self>, value: &Bound<'_, PyAny>) -> PyResult<bool> {
        slf.get()
            .to_tuple()
            .into_pyobject(slf.py())?
            .contains(value)
    }

    #[getter]
    fn __match_args__(&self) -> (&str, &str, &str, &str, &str) {
        ("major", "minor", "patch", "releaselevel", "serial")
    }

    fn __repeat__<'py>(slf: &Bound<'py, Self>, count: usize) -> PyResult<Bound<'py, PyTuple>> {
        slf.get()
            .to_tuple()
            .into_pyobject(slf.py())?
            .into_sequence()
            .repeat(count)?
            .to_tuple()
    }

    fn __iter__<'py>(slf: &Bound<'py, Self>) -> PyResult<Bound<'py, PyIterator>> {
        slf.get()
            .to_tuple()
            .into_pyobject(slf.py())?
            .into_sequence()
            .try_iter()
    }
}

#[pyfunction]
pub fn build_info(py: Python) -> String {
    let pkg_name = shadow::PROJECT_NAME;
    let pkg_ver = shadow::PKG_VERSION;
    let commit = shadow::PKG_COMMIT;

    let py_impl = shadow::PYO3_PY_IMPL;
    let py_build_ver = shadow::PYO3_PY_VER;
    let no_gil = if shadow::PYO3_NO_GIL { "t" } else { "" };
    let abi3 = if shadow::PYO3_ABI3 { "-abi3" } else { "" };
    let shared = if shadow::PYO3_SHARED {
        "shared"
    } else {
        "static"
    };

    let py_ver = py.version().replace(char::is_whitespace, " ");

    let rustc_ver = shadow::RUST_VERSION;
    let rustc_host = shadow::HOST;
    let rustc_profile = shadow::PROFILE;
    let rustc_opt_level = shadow::OPT_LEVEL;
    let rustc_debug = shadow::DEBUG;

    let target_triple = shadow::BUILD_TARGET;

    let dep_keyset_rs = shadow::DEP_KEYSET_RS_VER;
    let dep_pyo3 = shadow::DEP_PYO3_VER;

    formatdoc! {
        r#"
            {pkg_name} {pkg_ver} ({commit})
            python:
              target: {py_impl} {py_build_ver}{no_gil}{abi3} {shared}
              using: {py_ver}
            rust:
              compiler: {rustc_ver}
              host: {rustc_host}
              target: {target_triple}
            build:
              profile: {rustc_profile}
              opt_level: {rustc_opt_level}
              debug: {rustc_debug}
            dependencies:
              keyset-rs: {dep_keyset_rs}
              pyo3: {dep_pyo3}
        "#
    }
}
