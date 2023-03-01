mod version;

use pyo3::prelude::*;

use version::Version;

#[pymodule]
fn pykeyset(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add("version_info", Version::get())?;

    Ok(())
}
