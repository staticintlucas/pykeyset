use pyo3::exceptions::PyTypeError;
#[cfg(feature = "experimental-inspect")]
use pyo3::inspect::types::TypeInfo;
use pyo3::intern;
use pyo3::prelude::*;
use pyo3::{exceptions::PyValueError, types::PyTuple};

pub struct Color(keyset::Color);

impl<'a, 'py> FromPyObject<'a, 'py> for Color {
    type Error = PyErr;

    #[cfg(feature = "experimental-inspect")]
    const INPUT_TYPE: &'static str =
        "typing.Union[typing.Mapping[str, int], typing.Sequence[int], str]";

    fn extract(ob: Borrowed<'a, 'py, PyAny>) -> PyResult<Self> {
        let py = ob.py();

        let (r, g, b) = if let Ok(r) = ob
            .get_item(intern!(py, "r"))
            .and_then(|el| el.extract::<f32>())
        {
            (
                r,
                ob.get_item(intern!(py, "g"))?.extract::<f32>()?,
                ob.get_item(intern!(py, "b"))?.extract::<f32>()?,
            )
        } else if let Ok(r) = ob.get_item(0).and_then(|el| el.extract::<f32>()) {
            (
                r,
                ob.get_item(1)?.extract::<f32>()?,
                ob.get_item(2)?.extract::<f32>()?,
            )
        } else if let Ok(s) = ob.extract::<String>() {
            let csscolorparser::Color { r, g, b, a: _ } = csscolorparser::parse(s.as_str())
                .map_err(|e| PyValueError::new_err(format!("invalid color string: {e}")))?;
            (r, g, b)
        } else {
            return Err(PyTypeError::new_err(
                "color must be a mapping with 'r', 'g', 'b' keys, a sequence of 3 or 4 integers, or a CSS color string",
            ));
        };

        for &component in &[r, g, b] {
            if !(0.0..=1.0).contains(&component) {
                return Err(PyValueError::new_err(
                    "color components must be in the range [0.0, 1.0]",
                ));
            }
        }

        Ok(Self(keyset::Color::new(r, g, b)))
    }

    #[cfg(feature = "experimental-inspect")]
    fn type_input() -> TypeInfo {
        TypeInfo::union_of(&[
            TypeInfo::mapping_of(TypeInfo::builtin("str"), TypeInfo::builtin("str")),
            TypeInfo::sequence_of(TypeInfo::builtin("int")),
            TypeInfo::builtin("str"),
        ])
    }
}

impl<'py> IntoPyObject<'py> for Color {
    type Target = PyTuple;
    type Output = Bound<'py, Self::Target>;
    type Error = PyErr;

    #[cfg(feature = "experimental-inspect")]
    const OUTPUT_TYPE: &'static str = "typing.Tuple[float, float, float]";

    fn into_pyobject(self, py: Python<'py>) -> Result<Self::Output, Self::Error> {
        PyTuple::new(py, [self.0.r(), self.0.g(), self.0.b()])
    }

    #[cfg(feature = "experimental-inspect")]
    fn type_output() -> TypeInfo {
        TypeInfo::Tuple(Some(vec![TypeInfo::builtin("float"); 3]))
    }
}

impl From<Color> for keyset::Color {
    #[inline]
    fn from(Color(c): Color) -> Self {
        c
    }
}

impl From<keyset::Color> for Color {
    #[inline]
    fn from(c: keyset::Color) -> Self {
        Self(c)
    }
}

#[cfg(feature = "test")]
pub mod test {
    use super::*;

    #[pyfunction]
    pub fn color_identity(color: Color) -> Color {
        color
    }

    #[pyfunction]
    pub fn color_round_trip(color: Color) -> Color {
        let color: keyset::Color = color.into();
        let color: Color = color.into();
        color
    }
}
