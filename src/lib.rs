mod core;
mod version;

use pyo3::prelude::*;

#[pymodule]
fn _impl(py: Python, m: &PyModule) -> PyResult<()> {
    let version = version::version()?;

    m.add("__version_info__", version)?;
    m.add("__version__", version.to_string())?;
    m.add("__build__", version::build_info(py)?)?;

    let core = core::module(py)?;
    m.add_submodule(core)?;

    // Work around https://github.com/PyO3/pyo3/issues/759
    let sys_modules = py.import("sys")?.getattr("modules")?;
    sys_modules.set_item("pykeyset._impl.core", core)?;

    Ok(())
}
