use std::fs;
use std::path::PathBuf;

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

#[pyfunction]
pub fn load(path: PathBuf) -> PyResult<Font> {
    Font::new(fs::read(path)?).map_err(Into::into)
}

#[pyfunction]
pub fn loadb(bytes: Vec<u8>) -> PyResult<Font> {
    Font::new(bytes).map_err(Into::into)
}

#[derive(Debug, Clone)]
struct FontError(keyset::font::Error);

impl From<FontError> for PyErr {
    #[inline]
    fn from(FontError(error): FontError) -> Self {
        PyValueError::new_err(format!("unable to parse font: {error}"))
    }
}

impl From<keyset::font::Error> for FontError {
    #[inline]
    fn from(other: keyset::font::Error) -> Self {
        Self(other)
    }
}

#[pyclass(module = "pykeyset.font", frozen)]
#[derive(Debug, Clone)]
pub struct Font(keyset::Font);

#[pymethods]
impl Font {
    #[new]
    fn new(ttf: Vec<u8>) -> Result<Self, FontError> {
        keyset::Font::from_ttf(ttf).map(Font).map_err(Into::into)
    }

    #[getter]
    fn family(&self) -> &str {
        self.0.family()
    }

    #[getter]
    fn name(&self) -> &str {
        self.0.name()
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

    fn has_glyph(&self, code_point: char) -> bool {
        self.0.has_glyph(code_point)
    }
}
