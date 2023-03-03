mod version;

use pyo3::prelude::*;
use pyo3::types::PyDict;

#[pymodule]
fn pykeyset(py: Python, m: &PyModule) -> PyResult<()> {
    let version = version::version()?;

    m.add("__version_info__", version)?;
    m.add("__version__", version.to_string())?;

    let build_dict = PyDict::new(py);
    build_dict.set_item("deps", {
        let deps = PyDict::new(py);
        // deps.set_item("keyset-rs", version::dep_version("keyset-rs")?.into_py(py))?;
        deps.set_item("pyo3", version::dep_version("pyo3")?.into_py(py))?;
        deps
    })?;

    m.add("__build__", build_dict)?;

    Ok(())
}
