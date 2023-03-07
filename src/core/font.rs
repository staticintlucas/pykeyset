use pyo3::prelude::*;
use pyo3::exceptions::PyNotImplementedError;

use super::Context;

pub fn module<'p>(py: Python<'p>) -> PyResult<&'p PyModule> {
    let font = PyModule::new(py, "font")?;
    font.add_class::<Font>()?;
    font.add_class::<Glyph>()?;
    font.add_class::<Kerning>()?;
    font.add_function(wrap_pyfunction!(load_builtin, font)?)?;
    font.add_function(wrap_pyfunction!(load_file, font)?)?;
    font.add_function(wrap_pyfunction!(load, font)?)?;
    Ok(font)
}

#[pyclass(module = "pykeyset.core.font")]
pub struct Font {}

#[pyclass(module = "pykeyset.core.font")]
pub struct Kerning {}

#[pyclass(module = "pykeyset.core.font", get_all, set_all)]
#[derive(Clone)]
pub struct Glyph {
    pub name: String,
    pub path: String,
    pub advance: f32,
}

#[pymethods]
impl Font {
    #[new]
    fn new(
        _name: String,
        _em_size: PyObject,
        _cap_height: PyObject,
        _x_height: PyObject,
        _line_height: PyObject,
        _slope: PyObject,
        _char_spacing: PyObject,
    ) -> PyResult<Self> {
        Err(PyNotImplementedError::new_err(()))
    }

    /// Returns the number of glyphs in the font
    fn __len__(&self) -> PyResult<usize> {
        Err(PyNotImplementedError::new_err(()))
    }

    /// Returns a copy of the glyph for the chosen character scaled to the given size, or None if the Glyph does not exist in the font
    fn glyph(&self, _char: PyObject, _size: PyObject) -> PyResult<Glyph> {
        Err(PyNotImplementedError::new_err(()))
    }

    fn line_spacing(&self, _size: PyObject) -> PyResult<()> {
        Err(PyNotImplementedError::new_err(()))
    }

    /// Adds a glyph to the font. The glyph should have the same metrics as set when creating the Font object
    fn add_glyph(&self, _glyph: Glyph) -> PyResult<()> {
        Err(PyNotImplementedError::new_err(()))
    }

    /// Returns a copy of this font's replacement character (or the default if none exists) scaled to the given size
    fn replacement(&self, _size: PyObject) -> PyResult<Glyph> {
        Err(PyNotImplementedError::new_err(()))
    }
}

#[pymethods]
impl Kerning {
    #[new]
    fn new(_cap_height: PyObject) -> PyResult<Self> {
        Err(PyNotImplementedError::new_err(()))
    }

    /// Returns the kerning between the given pair of glyph names if set, otherwise returns the default value of 0
    fn get(&self, _lhs: PyObject, _rhs: PyObject, _size: PyObject) -> PyResult<f32> {
        Err(PyNotImplementedError::new_err(()))
    }

    /// Sets the kerning between the given pair of glyph names
    fn set(&self, _lhs: PyObject, _rhs: PyObject, _kerning: PyObject) -> PyResult<()> {
        Err(PyNotImplementedError::new_err(()))
    }

    /// Resets the kerning between the given pair of glyph names. This will not modify the anything if the kerning between these characters has not been previously set
    fn delete(&self, _lhs: PyObject, _rhs: PyObject) -> PyResult<()> {
        Err(PyNotImplementedError::new_err(()))
    }

    /// Returns the number of kerning pair explicitly set
    fn __len__(&self) -> PyResult<usize> {
        Err(PyNotImplementedError::new_err(()))
    }
}

/// Load a builtin font by name, returning a Font object
#[pyfunction]
fn load_builtin(_name: String) -> PyResult<()> {
    Err(PyNotImplementedError::new_err(()))
}

/// Load a font from the given path, returning a Font object
#[pyfunction]
fn load_file(_path: String) -> PyResult<()> {
    Err(PyNotImplementedError::new_err(()))
}

// TODO this function is used by the cmdlist parser. Move it somewhere more appropriate?
/// load a built in font or an XML font file
#[pyfunction]
fn load(_ctx: Context, _file: String) -> PyResult<()> {
    Err(PyNotImplementedError::new_err(()))
}
