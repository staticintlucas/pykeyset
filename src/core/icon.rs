use pyo3::exceptions::PyNotImplementedError;
use pyo3::prelude::*;

pub fn module<'p>(py: Python<'p>) -> PyResult<&'p PyModule> {
    let icon = PyModule::new(py, "icon")?;
    icon.add_class::<Icon>()?;
    icon.add_class::<IconSet>()?;
    Ok(icon)
}

#[pyclass(module = "pykeyset._impl.core.icon")]
pub struct IconSet {}

#[pyclass(module = "pykeyset._impl.core.icon", get_all, set_all)]
#[derive(Clone)]
pub struct Icon {
    pub name: String,
    pub path: String,
}

#[pymethods]
impl IconSet {
    #[new]
    fn new(_name: String, _icon_size: PyObject) -> PyResult<Self> {
        Err(PyNotImplementedError::new_err(()))
    }

    /// Returns the number of icons in the set
    fn __len__(&self) -> PyResult<usize> {
        Err(PyNotImplementedError::new_err(()))
    }

    /// Returns a copy of the icon for the chosen name scaled to the given size, or None if the icon does not exist
    fn icon(
        &self,
        _name: String,
        _icon_size: PyObject,
        _font_size: PyObject,
        _valign: PyObject,
    ) -> PyResult<Icon> {
        Err(PyNotImplementedError::new_err(()))
    }

    /// Adds a icon to the set
    fn add_icon(&self, _icon: Icon) -> PyResult<()> {
        Err(PyNotImplementedError::new_err(()))
    }
}
