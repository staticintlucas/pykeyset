use pyo3::prelude::*;

use version::{VERSION, VERSION_STR};

mod core;
mod version;

#[pymodule]
mod pykeyset {
    use super::*;

    #[pymodule_export]
    use super::core::Font;
    #[pymodule_export]
    use super::core::Layout;
    #[pymodule_export]
    use super::core::Profile;
    #[pymodule_export]
    use super::core::Drawing;

    #[pymodule_init]
    fn init(m: &Bound<'_, PyModule>) -> PyResult<()> {
        // TODO can't add variables to declarative modules
        m.add("version_info", VERSION)?;
        m.add("version", VERSION_STR)?;
        m.add("__version__", VERSION_STR)?;
        m.add_function(wrap_pyfunction!(version::build_info, m)?)?;
        Ok(())
    }
}
