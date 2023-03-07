use pyo3::exceptions::PyNotImplementedError;
use pyo3::prelude::*;

use super::Context;

pub fn module<'p>(py: Python<'p>) -> PyResult<&'p PyModule> {
    let profile = PyModule::new(py, "profile")?;
    profile.add_class::<Profile>()?;
    profile.add_function(wrap_pyfunction!(load_builtin, profile)?)?;
    profile.add_function(wrap_pyfunction!(load_file, profile)?)?;
    profile.add_function(wrap_pyfunction!(load, profile)?)?;
    Ok(profile)
}

#[pyclass(module = "pykeyset.core.profile")]
pub struct Profile {}

#[pymethods]
impl Profile {
    #[new]
    fn new(
        _name: String,
        _type: PyObject,
        _depth: PyObject,
        _bottom_rect: PyObject,
        _top_rect: PyObject,
        _text_rect: PyObject,
        _text_size: PyObject,
        _homing: PyObject,
    ) -> PyResult<Self> {
        Err(PyNotImplementedError::new_err(()))
    }

    fn key(&self, _key: PyObject, _g: PyObject) -> PyResult<()> {
        Err(PyNotImplementedError::new_err(()))
    }

    fn legend_rect(&self, _key: PyObject, _size: PyObject) -> PyResult<()> {
        Err(PyNotImplementedError::new_err(()))
    }

    fn legend_size(&self, _size: PyObject) -> PyResult<()> {
        Err(PyNotImplementedError::new_err(()))
    }

    fn draw_key_bottom(&self, _g: PyObject, _size: PyObject, _color: PyObject) -> PyResult<()> {
        Err(PyNotImplementedError::new_err(()))
    }

    fn draw_key_top(
        &self,
        _g: PyObject,
        _keytype: PyObject,
        _size: PyObject,
        _color: PyObject,
    ) -> PyResult<()> {
        Err(PyNotImplementedError::new_err(()))
    }

    fn draw_iso_bottom(&self, _g: PyObject, _color: PyObject) -> PyResult<()> {
        Err(PyNotImplementedError::new_err(()))
    }

    fn draw_iso_top(&self, _g: PyObject, _color: PyObject) -> PyResult<()> {
        Err(PyNotImplementedError::new_err(()))
    }

    fn draw_step(&self, _g: PyObject, _color: PyObject) -> PyResult<()> {
        Err(PyNotImplementedError::new_err(()))
    }

    fn add_gradient(
        &self,
        _gradtype: PyObject,
        _color: PyObject,
        _depth: PyObject,
    ) -> PyResult<()> {
        Err(PyNotImplementedError::new_err(()))
    }
}

/// Load a builtin profile by name, returning a Profile object
#[pyfunction]
fn load_builtin(_name: String) -> PyResult<()> {
    Err(PyNotImplementedError::new_err(()))
}

/// Load a profile from the given path, returning a Profile object
#[pyfunction]
fn load_file(_path: String) -> PyResult<()> {
    Err(PyNotImplementedError::new_err(()))
}

// TODO this function is used by the cmdlist parser. Move it somewhere more appropriate?
/// load a built in profile or a profile config file
#[pyfunction]
fn load(_ctx: Context, _file: String) -> PyResult<()> {
    Err(PyNotImplementedError::new_err(()))
}
