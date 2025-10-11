#[cfg(feature = "experimental-inspect")]
use pyo3::inspect::types::TypeInfo;
use pyo3::prelude::*;
use pyo3::{exceptions::PyValueError, types::PyTuple};

pub struct Color(keyset::Color);

impl FromPyObject<'_> for Color {
    #[cfg(feature = "experimental-inspect")]
    const INPUT_TYPE: &'static str =
        "typing.Union[typing.Mapping[str, int], typing.Sequence[int], str]";

    fn extract_bound(ob: &Bound<'_, PyAny>) -> PyResult<Self> {
        let (r, g, b) = if let Ok(r) = ob.get_item("r") {
            (
                r.extract::<f32>()?,
                ob.get_item("g")?.extract::<f32>()?,
                ob.get_item("b")?.extract::<f32>()?,
            )
        } else if let Ok(r) = ob.get_item(0) {
            (
                r.extract::<f32>()?,
                ob.get_item(1)?.extract::<f32>()?,
                ob.get_item(2)?.extract::<f32>()?,
            )
        } else if let Ok(s) = ob.extract::<String>() {
            let csscolorparser::Color { r, g, b, a: _ } = csscolorparser::parse(s.as_str())
                .map_err(|e| PyValueError::new_err(format!("invalid color string: {e}")))?;
            (r as f32, g as f32, b as f32)
        } else {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "color must be a mapping with 'r', 'g', 'b' keys, a sequence of 3 or 4 integers, or a hex string",
            ));
        };

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
    type Error = pyo3::PyErr;

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
