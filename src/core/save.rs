use pyo3::exceptions::PyNotImplementedError;
use pyo3::prelude::*;

use super::Context;

pub fn module<'p>(py: Python<'p>) -> PyResult<&'p PyModule> {
    let save = PyModule::new(py, "save")?;
    save.add_function(wrap_pyfunction!(as_svg, save)?)?;
    save.add_function(wrap_pyfunction!(as_png, save)?)?;
    save.add_function(wrap_pyfunction!(as_pdf, save)?)?;
    save.add_function(wrap_pyfunction!(as_ai, save)?)?;
    Ok(save)
}

#[pyfunction]
/// save the generated graphic as an SVG graphic
fn as_svg(_ctx: Context, _filename: String) -> PyResult<()> {
    Err(PyNotImplementedError::new_err(()))
}

#[pyfunction]
/// save the graphic as a PNG image (requires Cairo)
fn as_png(_ctx: Context, _filename: String) -> PyResult<()> {
    Err(PyNotImplementedError::new_err(()))
}

#[pyfunction]
/// save the graphic as a PDF file (requires Cairo)
fn as_pdf(_ctx: Context, _filename: String) -> PyResult<()> {
    Err(PyNotImplementedError::new_err(()))
}

#[pyfunction]
/// save the graphic as an AI file (experimental; requires Cairo)
fn as_ai(_ctx: Context, _filename: String) -> PyResult<()> {
    Err(PyNotImplementedError::new_err(()))
}
