use pyo3::prelude::*;
use pyo3::types::PyBytes;

use super::font::Font;
use super::layout::Layout;
use super::profile::Profile;

#[pyclass(module = "pykeyset._impl")]
#[derive(Debug, Clone)]
pub struct Drawing(keyset::drawing::Drawing);

#[pymethods]
impl Drawing {
    #[new]
    fn new(layout: Layout, profile: Profile, font: Font) -> PyResult<Self> {
        let options = keyset::drawing::Template {
            profile: profile.0,
            font: font.0,
            ..Default::default()
        };
        Ok(Self(options.draw(&layout.0).unwrap().0)) // TODO: handle errors
    }

    fn to_svg(&self) -> String {
        self.0.to_svg()
    }

    fn to_png(&self) -> Py<PyBytes> {
        let result = self.0.to_png(96.).unwrap(); // TODO: handle errors
        Python::attach(|py| PyBytes::new(py, &result).into())
    }

    fn to_pdf(&self) -> Py<PyBytes> {
        let result = self.0.to_pdf();
        Python::attach(|py| PyBytes::new(py, &result).into())
    }

    fn to_ai(&self) -> Py<PyBytes> {
        let result = self.0.to_ai();
        Python::attach(|py| PyBytes::new(py, &result).into())
    }
}
