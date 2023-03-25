use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

pub fn module<'p>(py: Python<'p>) -> PyResult<&'p PyModule> {
    let profile = PyModule::new(py, "profile")?;
    profile.add_class::<Profile>()?;
    Ok(profile)
}

#[pyclass(module = "pykeyset._impl.core.profile")]
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
