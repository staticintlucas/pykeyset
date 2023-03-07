use pyo3::exceptions::PyNotImplementedError;
use pyo3::prelude::*;

use super::Context;

pub fn module<'p>(py: Python<'p>) -> PyResult<&'p PyModule> {
    let fontgen_mod = PyModule::new(py, "fontgen")?;
    fontgen_mod.add_function(wrap_pyfunction!(fontgen, fontgen_mod)?)?;
    Ok(fontgen_mod)
}

#[pyfunction]
/// create a new XML font file from a source font
fn fontgen(_ctx: Context, _output: String, _input: String) -> PyResult<()> {
    Err(PyNotImplementedError::new_err(()))
}
