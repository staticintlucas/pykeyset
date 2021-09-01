mod version;

use pyo3::prelude::*;

use version::Version;

#[pymodule]
fn pykeyset_rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<Version>()?;

    Ok(())
}
