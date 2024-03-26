mod core;
mod version;

use pyo3::prelude::*;

#[pymodule]
fn _impl(m: &Bound<'_, PyModule>) -> PyResult<()> {
    let version = version::version()?;

    m.add("version_info", version)?;
    m.add("version", version.to_string())?;
    m.add_function(wrap_pyfunction!(version::build_info, m)?)?;

    m.add_class::<core::Font>()?;
    m.add_class::<core::Glyph>()?;
    m.add_class::<core::Path>()?;
    m.add_class::<core::Rect>()?;
    // m.add_class::<core::icon::Icon>()?;
    // m.add_class::<core::icon::IconSet>()?;
    m.add_class::<core::Layout>()?;
    m.add_class::<core::Profile>()?;
    m.add_class::<core::Drawing>()?;
    // m.add_class::<core::drawing::DrawingOptions>()?;

    Ok(())
}
