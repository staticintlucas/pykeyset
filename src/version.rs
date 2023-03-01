use pyo3::basic::CompareOp;
use pyo3::types::PyTuple;
use pyo3::prelude::*;

use konst::primitive::parse_u8;
use konst::result::unwrap_ctx;

// #[derive(Debug, Clone, Copy)]
#[pyclass(mapping, module="pykeyset.impl", name="version_info")]
pub struct Version {
    #[pyo3(get)]
    major: u8,
    #[pyo3(get)]
    minor: u8,
    #[pyo3(get)]
    patch: u8,
    #[pyo3(get, name="releaselevel")]
    prerelease: Option<&'static str>,
}

impl Version {
    fn as_vec(&self) -> Vec<PyObject> {
        Python::with_gil(|py|
               vec![
            self.major.to_object(py),
            self.minor.to_object(py),
            self.patch.to_object(py),
            self.prerelease.to_object(py),
        ])
    }

    fn as_tuple(&self) -> Py<PyTuple> {
        Python::with_gil(|py|
            PyTuple::new(py, self.as_vec()).into()
        )
    }

    pub fn get() -> Self {
        Self {
            major: unwrap_ctx!(parse_u8(env!("CARGO_PKG_VERSION_MAJOR"))),
            minor: unwrap_ctx!(parse_u8(env!("CARGO_PKG_VERSION_MINOR"))),
            patch: unwrap_ctx!(parse_u8(env!("CARGO_PKG_VERSION_PATCH"))),
            prerelease: option_env!("CARGO_PKG_VERSION_PRE"),
        }
    }
}

#[pyclass]
pub struct VersionIter(std::vec::IntoIter<PyObject>);

#[pymethods]
impl Version {
    pub fn count(&self, value: &PyAny) -> PyResult<PyObject> {
        Python::with_gil(|py|
            self.as_tuple().call_method1(py, "count", (value, ))
        )
    }

    pub fn index(&self, value: &PyAny, start: Option<&PyAny>, stop: Option<&PyAny>) -> PyResult<PyObject> {
        Python::with_gil(|py| {
            let start = start.unwrap_or(0_isize.into_py(py).into_ref(py));
            let stop = stop.unwrap_or(isize::MAX.into_py(py).into_ref(py));

            self.as_tuple().call_method1(py, "index", (value, start, stop))
        })
    }

    fn __str__(&self) -> String {
        if let Some(prerelease) = self.prerelease {
            format!("{}.{}.{}-{}", self.major, self.minor, self.patch, prerelease)
        } else {
            format!("{}.{}.{}", self.major, self.minor, self.patch)
        }
    }

    fn __repr__(&self) -> String {
        let prerelease = self.prerelease.unwrap_or("None");

        format!("pykeyset.impl.version_info(major={}, minor={}, patch={}, releaselevel={})", self.major, self.minor, self.patch, prerelease)
    }

    fn __richcmp__(&self, value: &PyAny, op: CompareOp) -> PyResult<PyObject> {
        let name = match op {
            CompareOp::Lt => "__lt__",
            CompareOp::Le => "__le__",
            CompareOp::Eq => "__eq__",
            CompareOp::Ne => "__ne__",
            CompareOp::Gt => "__gt__",
            CompareOp::Ge => "__ge__",
        };
        Python::with_gil(|py|
            self.as_tuple().call_method1(py, name, (value, ))
        )
    }

    fn __len__(&self) -> PyResult<usize> {
        Python::with_gil(|py|
            self.as_tuple().call_method0(py, "__len__")?.extract(py)
        )
    }

    fn __getitem__(&self, key: &PyAny) -> PyResult<PyObject> {
        Python::with_gil(|py|
            self.as_tuple().call_method1(py, "__getitem__", (key, ))
        )
    }

    fn __concat__(&self, value: PyObject) -> PyResult<PyObject> {
        Python::with_gil(|py|
            self.as_tuple().call_method1(py, "__add__", (value, ))
        )
    }

    fn __contains__(&self, key: PyObject) -> PyResult<bool> {
        Python::with_gil(|py|
            self.as_tuple().call_method1(py, "__contains__", (key, ))?.extract(py)
        )
    }

    fn __repeat__(&self, value: isize) -> PyResult<PyObject> {
        Python::with_gil(|py|
            self.as_tuple().call_method1(py, "__mul__", (value, ))
        )
    }

    fn __iter__(slf: PyRef<Self>) -> VersionIter {
        VersionIter((&*slf).as_vec().into_iter())
    }
}

#[pymethods]
impl VersionIter {
    fn __iter__(slf: PyRef<Self>) -> PyRef<Self> {
        slf
    }

    fn __next__(mut slf: PyRefMut<Self>) -> Option<PyObject> {
        slf.0.next()
    }
}
