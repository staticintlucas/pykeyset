mod version;

use pyo3::prelude::*;

use version::Version;

#[pymodule]
fn pykeyset_impl(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add("version_info", Version::get())?;

    Ok(())
}
