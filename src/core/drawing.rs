use pyo3::prelude::*;

use keyset::ToSvg;

use super::font::Font;
use super::layout::Layout;
use super::profile::Profile;

pub fn module<'p>(py: Python<'p>) -> PyResult<&'p PyModule> {
    let drawing = PyModule::new(py, "drawing")?;
    drawing.add_class::<Drawing>()?;
    Ok(drawing)
}

#[pyclass(module = "pykeyset._impl.core.layout")]
#[derive(Debug, Clone)]
pub struct Drawing(pub String);

#[pymethods]
impl Drawing {
    #[new]
    fn new(layout: Layout, profile: Profile, font: Font) -> PyResult<Self> {
        let options = keyset::DrawingOptions::default();
        let drawing = keyset::Drawing::new(layout.0, profile.0, font.0, options);
        Ok(Self(drawing.to_svg()))
    }

    fn to_svg(&self) -> PyResult<String> {
        Ok(self.0.clone())
    }
}
