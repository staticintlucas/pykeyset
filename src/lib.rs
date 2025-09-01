use pyo3::prelude::*;

use version::{VERSION, VERSION_STR};

mod core;
mod version;

#[pymodule]
fn pykeyset(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add("version_info", VERSION)?;
    m.add("version", VERSION_STR)?;
    m.add("__version__", VERSION_STR)?;
    m.add_function(wrap_pyfunction!(version::build_info, m)?)?;

    m.add_class::<core::Font>()?;
    // m.add_class::<core::icon::Icon>()?;
    // m.add_class::<core::icon::IconSet>()?;
    m.add_class::<core::Layout>()?;
    m.add_class::<core::Profile>()?;
    m.add_class::<core::Drawing>()?;
    // m.add_class::<core::drawing::DrawingOptions>()?;

    Ok(())
}
