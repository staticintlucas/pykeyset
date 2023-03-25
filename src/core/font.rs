use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

pub fn module<'p>(py: Python<'p>) -> PyResult<&'p PyModule> {
    let font = PyModule::new(py, "font")?;
    font.add_class::<Font>()?;
    Ok(font)
}

#[pyclass(module = "pykeyset._impl.core.font")]
#[derive(Debug, Clone)]
pub struct Font(pub keyset::Font);

#[pymethods]
impl Font {
    #[new]
    fn new(ttf: &[u8]) -> PyResult<Self> {
        match keyset::Font::from_ttf(ttf) {
            Ok(font) => Ok(Self(font)),
            Err(error) => Err(PyValueError::new_err(error.to_string())),
        }
    }
}
