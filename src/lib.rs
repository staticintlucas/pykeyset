use pyo3::prelude::*;

mod color;
mod drawing;
mod font;
mod layout;
mod profile;
mod utils;
mod version;

#[pymodule]
mod pykeyset {
    use super::*;

    #[pymodule]
    mod drawing {
        #[pymodule_export]
        use crate::drawing::Drawing;
    }

    #[pymodule]
    mod profile {
        #[pymodule_export]
        use crate::profile::{
            load, loadb, loads, BottomSurface, Cylindrical, Flat, Homing, HomingBar, HomingBump,
            HomingScoop, LegendGeometry, LegendGeometryMap, LegendMargin, Profile, ProfileType,
            Spherical, TopSurface,
        };
    }

    #[pymodule]
    mod layout {
        #[pymodule_export]
        use crate::layout::{
            load, loadb, loads, HomingKey, IsoHorizontal, IsoVertical, Key, KeyShape, Legend,
            NoneKey, NormalKey, SpaceKey, SteppedCaps,
        };
    }

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

    #[cfg(feature = "test")]
    #[pymodule]
    mod test {
        #[pymodule_export]
        use crate::color::test::{color_identity, color_round_trip};
    }
}
