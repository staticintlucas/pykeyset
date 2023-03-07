mod font;
mod fontgen;
mod icon;
mod kle;
mod layout;
mod profile;
mod save;

use pyo3::prelude::*;

#[pyclass(module = "pykeyset.core")]
#[derive(Debug, Clone)]
pub struct Context {
    pub name: String,
    pub kle: Option<()>,
    pub font: Option<()>,
    pub icons: Option<()>,
    pub profile: Option<()>,
    pub layout: Option<()>,
}

#[pymethods]
impl Context {
    #[new]
    fn new(name: String) -> Self {
        Self {
            name,
            kle: None,
            font: None,
            icons: None,
            profile: None,
            layout: None,
        }
    }
}

pub fn module<'p>(py: Python<'p>) -> PyResult<&'p PyModule> {
    let core = PyModule::new(py, "core")?;

    let fontgen = fontgen::module(py)?;
    core.add_submodule(fontgen)?;

    let save = save::module(py)?;
    core.add_submodule(save)?;

    let font = font::module(py)?;
    core.add_submodule(font)?;
    core.add_class::<font::Font>()?;

    let icon = icon::module(py)?;
    core.add_submodule(icon)?;
    core.add_class::<icon::IconSet>()?;

    let kle = kle::module(py)?;
    core.add_submodule(kle)?;
    core.add_class::<kle::KleFile>()?;

    let layout = layout::module(py)?;
    core.add_submodule(layout)?;
    core.add_class::<layout::Layout>()?;

    let profile = profile::module(py)?;
    core.add_submodule(profile)?;
    core.add_class::<profile::Profile>()?;

    core.add_class::<Context>()?;

    // Work around https://github.com/PyO3/pyo3/issues/759
    let sys_modules = py.import("sys")?.getattr("modules")?;
    sys_modules.set_item("pykeyset.core.fontgen", fontgen)?;
    sys_modules.set_item("pykeyset.core.save", save)?;
    sys_modules.set_item("pykeyset.core.font", font)?;
    sys_modules.set_item("pykeyset.core.icon", icon)?;
    sys_modules.set_item("pykeyset.core.kle", kle)?;
    sys_modules.set_item("pykeyset.core.layout", layout)?;
    sys_modules.set_item("pykeyset.core.profile", profile)?;

    Ok(core)
}
