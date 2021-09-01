use pyo3::exceptions::PyIndexError;
use pyo3::prelude::*;
use pyo3::{PyObjectProtocol, PySequenceProtocol};
use konst::primitive::parse_u8;
use konst::result::unwrap_ctx;

#[pyclass]
#[derive(Debug, Clone, Copy)]
pub struct Version {
    #[pyo3(get)]
    major: u8,
    #[pyo3(get)]
    minor: u8,
    #[pyo3(get)]
    micro: u8,
    #[pyo3(get, name="releaselevel")]
    release_level: &'static str,
}

#[pymethods]
impl Version {
    #[staticmethod]
    fn get() -> Self {
        Self {
            major: unwrap_ctx!(parse_u8(env!("CARGO_PKG_VERSION_MAJOR"))),
            minor: unwrap_ctx!(parse_u8(env!("CARGO_PKG_VERSION_MINOR"))),
            micro: unwrap_ctx!(parse_u8(env!("CARGO_PKG_VERSION_PATCH"))),
            release_level: option_env!("CARGO_PKG_VERSION_PRE").unwrap_or(""),
        }
    }
}

#[pyproto]
impl PyObjectProtocol for Version {
    fn __str__(&self) -> PyResult<String> {
        Ok(format!("{}.{}.{}-{}", self.major, self.minor, self.micro, self.release_level))
    }
}

#[pyproto]
impl PySequenceProtocol for Version {
    fn __len__(&self) -> PyResult<usize> {
        Ok(4)
    }

    fn __getitem__(&self, idx: isize) -> PyResult<PyObject> {
        // Since we impl __len__ pyo3 will always return a positive number

        Python::with_gil(|py|
            match idx {
                0 => Ok(self.major.into_py(py)),
                1 => Ok(self.minor.into_py(py)),
                2 => Ok(self.micro.into_py(py)),
                3 => Ok(self.release_level.into_py(py)),
                _ => Err(PyIndexError::new_err("tuple index out of range")),
            }
        )
    }
}
