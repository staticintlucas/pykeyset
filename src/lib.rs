use pyo3::prelude::*;

mod core;
mod font;
mod version;

#[pymodule]
mod pykeyset {
    use super::*;

    #[pymodule_export]
    use super::core::Drawing;
    #[pymodule_export]
    use super::core::Layout;
    #[pymodule_export]
    use super::core::Profile;

    #[pymodule]
    mod font {
        #[pymodule_export]
        use crate::font::{load, loadb, Font};
    }

    #[pymodule_export]
    #[expect(non_upper_case_globals, reason = "Python naming convention")]
    const version: &str = version::VERSION_STR;

    #[pymodule_export]
    #[expect(non_upper_case_globals, reason = "Python naming convention")]
    const __version__: &str = version::VERSION_STR;

    #[pymodule_export]
    #[expect(non_upper_case_globals, reason = "Python naming convention")]
    const version_info: version::Version = version::VERSION;

    #[pymodule_export]
    use version::build_info;
}
