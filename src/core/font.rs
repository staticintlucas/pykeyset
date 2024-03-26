use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyString;

#[pyclass(module = "pykeyset._impl", frozen)]
#[derive(Debug, Clone)]
pub struct Font(pub(super) keyset::font::Font);

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
        PyString::new_bound(slf.py(), slf.get().0.family())
    }

    #[getter]
    fn name<'py>(slf: &Bound<'py, Self>) -> Bound<'py, PyString> {
        PyString::new_bound(slf.py(), slf.get().0.name())
    }

    #[getter]
    fn em_size(&self) -> f64 {
        self.0.em_size()
    }

    #[getter]
    fn cap_height(&self) -> f64 {
        self.0.cap_height()
    }

    #[getter]
    fn x_height(&self) -> f64 {
        self.0.x_height()
    }

    #[getter]
    fn ascender(&self) -> f64 {
        self.0.ascender()
    }

    #[getter]
    fn descender(&self) -> f64 {
        self.0.descender()
    }

    #[getter]
    fn line_gap(&self) -> f64 {
        self.0.line_gap()
    }

    #[getter]
    fn line_height(&self) -> f64 {
        self.0.line_height()
    }

    #[getter]
    fn slope(&self) -> Option<f64> {
        self.0.slope()
    }

    #[getter]
    fn num_glyphs(&self) -> usize {
        self.0.num_glyphs()
    }

    fn glyph(&self, char: char) -> Option<Glyph> {
        self.0.glyph(char).map(Glyph)
    }

    fn glyph_or_default(&self, char: char) -> Glyph {
        Glyph(self.0.glyph_or_default(char))
    }

    fn notdef(&self) -> Glyph {
        Glyph(self.0.notdef())
    }

    fn kerning(&self, left: char, right: char) -> f64 {
        self.0.kerning(left, right)
    }
}

#[pyclass(module = "pykeyset._impl", frozen)]
#[derive(Debug, Clone)]
pub struct Glyph(keyset::font::Glyph);

#[pymethods]
impl Glyph {
    #[getter]
    fn path(&self) -> Path {
        Path
    }

    #[getter]
    fn bounds(&self) -> Rect {
        let r = self.0.bounds;
        Rect {
            x: r.min_x(),
            y: r.min_y(),
            w: r.width(),
            h: r.height(),
        }
    }

    #[getter]
    fn advance(&self) -> f64 {
        self.0.advance
    }
}

#[pyclass(module = "pykeyset._impl", frozen)]
#[derive(Debug, Clone)]
pub struct Path;

#[pyclass(module = "pykeyset._impl", frozen, get_all)]
#[derive(Debug, Clone)]
pub struct Rect {
    x: f64,
    y: f64,
    w: f64,
    h: f64,
}
