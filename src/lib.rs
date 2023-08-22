mod core;
mod version;

use pyo3::prelude::*;

#[pymodule]
fn _impl(py: Python, m: &PyModule) -> PyResult<()> {
    let version = version::version()?;

    m.add("__version_info__", version)?;
    m.add("__version__", version.to_string())?;
    m.add("__build__", version::build_info(py)?)?;

    m.add_class::<core::Font>()?;
    // m.add_class::<core::icon::Icon>()?;
    // m.add_class::<core::icon::IconSet>()?;
    m.add_class::<core::Layout>()?;
    m.add_class::<core::Profile>()?;
    m.add_class::<core::Drawing>()?;
    // m.add_class::<core::drawing::DrawingOptions>()?;

    Ok(())
}
