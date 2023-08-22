use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

#[pyclass(module = "pykeyset._impl")]
#[derive(Debug, Clone)]
pub struct Profile(pub keyset::Profile);

#[pymethods]
impl Profile {
    #[new]
    fn new(toml: &str) -> PyResult<Self> {
        match keyset::Profile::from_toml(toml) {
            Ok(profile) => Ok(Self(profile)),
            Err(error) => Err(PyValueError::new_err(error.to_string())),
        }
    }
}
