use pyo3::prelude::*;
use pyo3::types::PyBytes;

use super::font::Font;
use super::layout::Layout;
use super::profile::Profile;

pub fn module<'p>(py: Python<'p>) -> PyResult<&'p PyModule> {
    let drawing = PyModule::new(py, "drawing")?;
    drawing.add_class::<Drawing>()?;
    Ok(drawing)
}

#[pyclass(module = "pykeyset._impl.core.drawing")]
#[derive(Debug, Clone)]
pub struct Drawing(keyset::Drawing);

#[pymethods]
impl Drawing {
    #[new]
    fn new(layout: Layout, profile: Profile, font: Font) -> PyResult<Self> {
        let mut options = keyset::DrawingOptions::default();
        options.profile(profile.0).font(font.0);
        Ok(Self(options.draw(&layout.0)))
    }

    fn to_svg(&self) -> PyResult<String> {
        Ok(self.0.to_svg())
    }

    fn to_png(&self) -> PyResult<Py<PyBytes>> {
        let result = self.0.to_png(96.);
        Ok(Python::with_gil(|py| PyBytes::new(py, &result).into()))
    }

    fn to_pdf(&self) -> PyResult<Py<PyBytes>> {
        let result = self.0.to_pdf();
        Ok(Python::with_gil(|py| PyBytes::new(py, &result).into()))
    }

    fn to_ai(&self) -> PyResult<Py<PyBytes>> {
        let result = self.0.to_ai();
        Ok(Python::with_gil(|py| PyBytes::new(py, &result).into()))
    }
}
