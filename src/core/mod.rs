mod drawing;
mod font;
mod icon;
mod layout;
mod profile;

use pyo3::prelude::*;

pub fn module<'p>(py: Python<'p>) -> PyResult<&'p PyModule> {
    let core = PyModule::new(py, "core")?;

    let font = font::module(py)?;
    core.add_submodule(font)?;
    core.add_class::<font::Font>()?;

    let icon = icon::module(py)?;
    core.add_submodule(icon)?;
    core.add_class::<icon::IconSet>()?;

    let layout = layout::module(py)?;
    core.add_submodule(layout)?;
    core.add_class::<layout::Layout>()?;

    let profile = profile::module(py)?;
    core.add_submodule(profile)?;
    core.add_class::<profile::Profile>()?;

    let drawing = drawing::module(py)?;
    core.add_submodule(drawing)?;
    core.add_class::<drawing::Drawing>()?;

    // Work around https://github.com/PyO3/pyo3/issues/759
    let sys_modules = py.import("sys")?.getattr("modules")?;
    sys_modules.set_item("pykeyset._impl.font", font)?;
    sys_modules.set_item("pykeyset._impl.icon", icon)?;
    sys_modules.set_item("pykeyset._impl.layout", layout)?;
    sys_modules.set_item("pykeyset._impl.profile", profile)?;
    sys_modules.set_item("pykeyset._impl.drawing", drawing)?;

    Ok(core)
}
