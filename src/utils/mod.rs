mod config;
mod types;

use pyo3::class::basic::CompareOp;
use pyo3::prelude::*;

pub fn module<'p>(py: Python<'p>) -> PyResult<&'p PyModule> {
    let utils = PyModule::new(py, "utils")?;

    let config = config::module(py)?;
    utils.add_submodule(config)?;

    utils.add_class::<Verbosity>()?;
    utils.add_class::<Severity>()?;

    // Work around https://github.com/PyO3/pyo3/issues/759
    let sys_modules = py.import("sys")?.getattr("modules")?;
    sys_modules.set_item("pykeyset.utils.config", config)?;

    Ok(utils)
}

#[pyclass(module = "pykeyset.utils")]
#[derive(Debug, Clone, Copy, PartialEq, PartialOrd)]
pub enum Verbosity {
    NONE,
    QUIET,
    NORMAL,
    VERBOSE,
    DEBUG,
}

#[pyclass(module = "pykeyset.utils")]
#[derive(Debug, Clone, Copy, PartialEq, PartialOrd)]
pub enum Severity {
    DEBUG,
    INFO,
    WARNING,
    ERROR,
}

#[derive(FromPyObject, Debug, Clone, Copy)]
enum VerbosityOrInt {
    #[pyo3(transparent)]
    Verbosity(Verbosity),
    #[pyo3(transparent)]
    Int(isize),
}

#[pymethods]
impl Verbosity {
    fn __richcmp__(&self, other: VerbosityOrInt, op: CompareOp) -> bool {
        let other = match other {
            VerbosityOrInt::Verbosity(verbosity) => verbosity as isize,
            VerbosityOrInt::Int(int) => int,
        };
        op.matches((*self as isize).cmp(&other))
    }

    fn __hash__(&self) -> usize {
        *self as usize
    }
}

#[derive(FromPyObject, Debug, Clone, Copy)]
enum SeverityOrInt {
    #[pyo3(transparent)]
    Severity(Severity),
    #[pyo3(transparent)]
    Int(isize),
}

#[pymethods]
impl Severity {
    fn __richcmp__(&self, other: SeverityOrInt, op: CompareOp) -> bool {
        let other = match other {
            SeverityOrInt::Severity(severity) => severity as isize,
            SeverityOrInt::Int(int) => int,
        };
        op.matches((*self as isize).cmp(&other))
    }

    fn __hash__(&self) -> usize {
        *self as usize
    }
}
