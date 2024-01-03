use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

#[pyclass(module = "pykeyset._impl")]
#[derive(Debug, Clone)]
pub struct Layout(pub Vec<keyset::key::Key>);

#[pymethods]
impl Layout {
    #[staticmethod]
    fn from_kle(kle: &str) -> PyResult<Self> {
        match keyset::key::kle::from_json(kle) {
            Ok(layout) => Ok(Self(layout)),
            Err(error) => Err(PyValueError::new_err(error.to_string())),
        }
    }
}
