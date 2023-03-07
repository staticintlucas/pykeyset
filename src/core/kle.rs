use pyo3::prelude::*;
use pyo3::exceptions::PyNotImplementedError;
use pyo3::types::PyType;

use super::Context;

pub fn module<'p>(py: Python<'p>) -> PyResult<&'p PyModule> {
    let layout = PyModule::new(py, "layout")?;
    layout.add_class::<Key>()?;
    layout.add_class::<KeyType>()?;
    layout.add_class::<KleFile>()?;
    layout.add_function(wrap_pyfunction!(kle_to_ord, layout)?)?;
    Ok(layout)
}

#[pyclass(module = "pykeyset.core.kle", get_all, set_all)]
pub struct Key {
    pub pos: PyObject,
    pub size: PyObject,
    pub r#type: PyObject,
    pub legend: PyObject,
    pub legsize: PyObject,
    pub bgcol: PyObject,
    pub fgcol: PyObject,
}

#[pyclass(module = "pykeyset.core.kle", frozen)]
pub enum KeyType {
    NONE,
    NORM,
    DEFHOME,
    SCOOP,
    BAR,
    BUMP,
    SPACE,
}

#[pyclass(module = "pykeyset.core.kle")]
pub struct KleFile {}

const KLE_TO_ORD_MAP: [[u8; 12]; 8] = [
    [0, 6, 2, 8, 9, 11, 3, 5, 1, 4, 7, 10],  // 0 = no centering
    [1, 7, 0, 2, 9, 11, 4, 3, 5, 6, 8, 10],  // 1 = center x
    [3, 0, 5, 1, 9, 11, 2, 6, 4, 7, 8, 10],  // 2 = center y
    [4, 0, 1, 2, 9, 11, 3, 5, 6, 7, 8, 10],  // 3 = center x & y
    [0, 6, 2, 8, 10, 9, 3, 5, 1, 4, 7, 11],  // 4 = center front (default)
    [1, 7, 0, 2, 10, 3, 4, 5, 6, 8, 9, 11],  // 5 = center front & x
    [3, 0, 5, 1, 10, 2, 6, 7, 4, 8, 9, 11],  // 6 = center front & y
    [4, 0, 1, 2, 10, 3, 5, 6, 7, 8, 9, 11],  // 7 = center front & x & y
];

#[pyfunction]
fn kle_to_ord(mut legends: Vec<String>, index: usize) -> Vec<String> {
    let index = if index >= KLE_TO_ORD_MAP.len() { 0 } else { index };
    legends.resize(KLE_TO_ORD_MAP[0].len(), String::new());
    let mut legends: Vec<_> = KLE_TO_ORD_MAP[index].into_iter().zip(legends.into_iter()).collect();
    legends.sort_by_key(|(i, _l)| *i);
    legends.into_iter().map(|(_i, l)| l).collect()
}

#[pymethods]
impl KleFile {
    #[new]
    fn new() -> PyResult<Self> {
        Err(PyNotImplementedError::new_err(()))
    }

    #[staticmethod]
    fn _load_url(_ctx: Context, _url: String) -> PyResult<()> {
        Err(PyNotImplementedError::new_err(()))
    }

    #[staticmethod]
    fn _load_file(_ctx: Context, _path: String) -> PyResult<()> {
        Err(PyNotImplementedError::new_err(()))
    }

    #[classmethod]
    /// load a KLE Gist URL or local JSON file
    fn load(_cls: &PyType, _ctx: Context, _file: String) -> PyResult<()> {
        Err(PyNotImplementedError::new_err(()))
    }

    fn _parsekey(&self, _string: String, _props: PyObject) -> PyResult<()> {
        Err(PyNotImplementedError::new_err(()))
    }
}
