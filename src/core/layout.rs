use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

pub fn module<'p>(py: Python<'p>) -> PyResult<&'p PyModule> {
    let layout = PyModule::new(py, "layout")?;
    layout.add_class::<Layout>()?;
    Ok(layout)
}

#[pyclass(module = "pykeyset._impl.core.layout")]
#[derive(Debug, Clone)]
pub struct Layout(pub Vec<keyset::Key>);

#[pymethods]
impl Layout {
    #[staticmethod]
    fn from_kle(kle: &str) -> PyResult<Self> {
        match keyset::kle::from_json(kle) {
            Ok(layout) => Ok(Self(layout)),
            Err(error) => Err(PyValueError::new_err(error.to_string())),
        }
    }
}
