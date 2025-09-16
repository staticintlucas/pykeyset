use pyo3::prelude::*;

mod core;
mod font;
mod version;

#[pymodule]
mod pykeyset {
    use super::*;

    #[pymodule_export]
    use super::core::Layout;
    #[pymodule_export]
    use super::core::Profile;
    #[pymodule_export]
    use super::core::Drawing;

    #[pymodule]
    mod font {
        #[pymodule_export]
        use crate::font::{Font, load, loadb};
    }

    #[pymodule_init]
    fn init(m: &Bound<'_, PyModule>) -> PyResult<()> {
        // TODO can't add variables to declarative modules
        m.add("version_info", version::VERSION)?;
        m.add("version", version::VERSION_STR)?;
        m.add("__version__", version::VERSION_STR)?;
        m.add_function(wrap_pyfunction!(version::build_info, m)?)?;
        Ok(())
    }
}
