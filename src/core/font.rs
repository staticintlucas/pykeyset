use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyString;

#[pyclass(module = "pykeyset._impl", frozen)]
#[derive(Debug, Clone)]
pub struct Font(pub(super) keyset::Font);

#[pymethods]
impl Font {
    #[new]
    fn new(ttf: Vec<u8>) -> PyResult<Self> {
        match keyset::font::Font::from_ttf(ttf) {
            Ok(font) => Ok(Self(font)),
            Err(error) => Err(PyValueError::new_err(format!(
                "unable to parse font: {error}"
            ))),
        }
    }

    #[getter]
    fn family<'py>(slf: &Bound<'py, Self>) -> Bound<'py, PyString> {
        PyString::new(slf.py(), slf.get().0.family())
    }

    #[getter]
    fn name<'py>(slf: &Bound<'py, Self>) -> Bound<'py, PyString> {
        PyString::new(slf.py(), slf.get().0.name())
    }

    #[getter]
    fn em_size(&self) -> f32 {
        self.0.em_size().0
    }

    #[getter]
    fn cap_height(&self) -> f32 {
        self.0.cap_height().0
    }

    #[getter]
    fn x_height(&self) -> f32 {
        self.0.x_height().0
    }

    #[getter]
    fn ascender(&self) -> f32 {
        self.0.ascender().0
    }

    #[getter]
    fn descender(&self) -> f32 {
        self.0.descender().0
    }

    #[getter]
    fn line_gap(&self) -> f32 {
        self.0.line_gap().0
    }

    #[getter]
    fn line_height(&self) -> f32 {
        self.0.line_height().0
    }

    #[getter]
    fn slope(&self) -> f32 {
        self.0.slope().to_degrees()
    }

    #[getter]
    fn num_glyphs(&self) -> usize {
        self.0.num_glyphs()
    }
}
