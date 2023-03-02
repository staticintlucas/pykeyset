mod version;

use pyo3::prelude::*;

#[pymodule]
fn pykeyset(_py: Python, m: &PyModule) -> PyResult<()> {
    let version = version::version()?;

    m.add("__version_info__", version)?;
    m.add("__version__", version.to_string())?;

    Ok(())
}
