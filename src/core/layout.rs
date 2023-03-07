use pyo3::prelude::*;
use pyo3::exceptions::PyNotImplementedError;
use pyo3::types::PyType;

use super::Context;

pub fn module<'p>(py: Python<'p>) -> PyResult<&'p PyModule> {
    let layout = PyModule::new(py, "layout")?;
    layout.add_class::<Layout>()?;
    Ok(layout)
}

#[pyclass(module = "pykeyset.core.layout")]
pub struct Layout {}

#[pymethods]
impl Layout {
    #[new]
    fn new() -> PyResult<Self> {
        Err(PyNotImplementedError::new_err(()))
    }

    #[classmethod]
    fn layout(_cls: &PyType, _ctx: Context) -> PyResult<()> {
        Err(PyNotImplementedError::new_err(()))
    }

    fn drawlegend(&self, _ctx: Context, _key: PyObject, _g: PyObject) -> PyResult<()> {
        Err(PyNotImplementedError::new_err(()))
    }

    fn drawlegendrect(&self, _rect: PyObject) -> PyResult<()> {
        Err(PyNotImplementedError::new_err(()))
    }

    fn parselegend(&self, _legend: PyObject) -> PyResult<()> {
        Err(PyNotImplementedError::new_err(()))
    }
}
