use pyo3::prelude::*;

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
pub struct Drawing {
    keys: Vec<keyset::Key>,
    opts: keyset::DrawingOptions,
}

#[pymethods]
impl Drawing {
    #[new]
    fn new(layout: Layout, profile: Profile, font: Font) -> PyResult<Self> {
        let mut options = keyset::DrawingOptions::default();
        options.profile(profile.0).font(font.0);
        Ok(Self {
            keys: layout.0, opts: options })
    }

    fn to_svg(&self) -> PyResult<String> {
        Ok(self.opts.draw(&self.keys).to_svg())
    }

    fn to_png(&self) -> PyResult<Vec<u8>> {
        Ok(self.opts.draw(&self.keys).to_png(96.))
    }

    fn to_pdf(&self) -> PyResult<Vec<u8>> {
        Ok(self.opts.draw(&self.keys).to_pdf())
    }

    fn to_ai(&self) -> PyResult<Vec<u8>> {
        Ok(self.opts.draw(&self.keys).to_ai())
    }
}
