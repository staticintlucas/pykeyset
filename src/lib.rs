mod version;

use pyo3::prelude::*;

use version::Version;

#[pymodule]
fn pykeyset(_py: Python, m: &PyModule) -> PyResult<()> {
    let pykeyset_version = Version::pykeyset()?;

    m.add("__version_info__", pykeyset_version)?;
    m.add("__version__", pykeyset_version.to_string())?;

    Ok(())
}
