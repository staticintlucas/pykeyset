mod core;
mod utils;
mod version;

use pyo3::prelude::*;

#[pymodule]
fn pykeyset(py: Python, m: &PyModule) -> PyResult<()> {
    let version = version::version()?;

    m.add("__version_info__", version)?;
    m.add("__version__", version.to_string())?;
    m.add("__build__", version::build_info(py)?)?;

    let core = core::module(py)?;
    m.add_submodule(core)?;

    let utils = utils::module(py)?;
    m.add_submodule(utils)?;

    // Work around https://github.com/PyO3/pyo3/issues/759
    let sys_modules = py.import("sys")?.getattr("modules")?;
    sys_modules.set_item("pykeyset.core", core)?;
    sys_modules.set_item("pykeyset.utils", utils)?;

    Ok(())
}
