use pyo3::{prelude::*, types::PyTuple};

#[pyclass(module = "pykeyset.utils.types")]
#[derive(Debug, Clone, Copy)]
enum VerticalAlign {
    TOP = 0,
    MIDDLE = 1,
    BOTTOM = 2,
}

impl From<VerticalAlign> for f32 {
    fn from(value: VerticalAlign) -> Self {
        (value as usize as f32) * 0.5
    }
}

#[pyclass(module = "pykeyset.utils.types")]
#[derive(Debug, Clone, Copy)]
enum HorizontalAlign {
    LEFT = 0,
    CENTER = 1,
    RIGHT = 2,
}

impl From<HorizontalAlign> for f32 {
    fn from(value: HorizontalAlign) -> Self {
        (value as usize as f32) * 0.5
    }
}

#[pyclass(module = "pykeyset.utils.types", sequence, get_all, set_all)]
#[derive(Debug, Clone, Copy)]
struct Vector {
    x: f32,
    y: f32,
}

impl Vector {
    fn as_tuple(&self, py: Python) -> Py<PyTuple> {
        PyTuple::new(py, [self.x, self.y]).into()
    }
}

#[pymethods]
impl Vector {
    pub fn count(&self, value: &PyAny) -> PyResult<usize> {
        Python::with_gil(|py| self.as_tuple(py).as_ref(py).as_sequence().count(value))
    }

    pub fn index(
        &self,
        value: &PyAny,
        start: Option<&PyAny>,
        stop: Option<&PyAny>,
    ) -> PyResult<PyObject> {
        Python::with_gil(|py| {
            // TODO calling index here with call_method because PySequence::index doesn't take
            // start/stop values
            let start = start.unwrap_or(0_isize.into_py(py).into_ref(py));
            let stop = stop.unwrap_or(isize::MAX.into_py(py).into_ref(py));

            self.as_tuple(py)
                .call_method1(py, "index", (value, start, stop))
        })
    }

    #[getter]
    fn magnitude(&self) -> f32 {
        (self.x * self.x + self.y * self.y).sqrt()
    }

    #[getter]
    fn angle(&self) -> f32 {
        f32::atan2(self.y, self.x)
    }

    fn __neg__(&self) -> Self {
        Self {
            x: -self.x,
            y: -self.y,
        }
    }

    fn __add__(&self, other: Self) -> Self {
        Self {
            x: self.x + other.x,
            y: self.y + other.y,
        }
    }

    fn __sub__(&self, other: Self) -> Self {
        Self {
            x: self.x - other.x,
            y: self.y - other.y,
        }
    }

    fn __mul__(&self, other: VectorOrFloat) -> Self {
        match other {
            VectorOrFloat::Vector(other) => Self {
                x: self.x * other.x,
                y: self.y * other.y,
            },
            VectorOrFloat::Float(other) => Self {
                x: self.x * other,
                y: self.y * other,
            },
        }
    }

    fn __truediv__(&self, other: VectorOrFloat) -> Self {
        match other {
            VectorOrFloat::Vector(other) => Self {
                x: self.x / other.x,
                y: self.y / other.y,
            },
            VectorOrFloat::Float(other) => Self {
                x: self.x / other,
                y: self.y / other,
            },
        }
    }

    fn rotate(&self, angle: f32) -> Self {
        let (sin, cos) = angle.sin_cos();
        Self {
            x: self.x * cos - self.y * sin,
            y: self.x * sin + self.y * cos,
        }
    }
}

#[derive(FromPyObject, Debug, Clone, Copy)]
enum VectorOrFloat {
    #[pyo3(transparent)]
    Vector(Vector),
    #[pyo3(transparent)]
    Float(f32),
}

// class Rect(NamedTuple):
//     x: float
//     y: float
//     w: float
//     h: float

//     @property
//     def width(self) -> float:
//         return self.w

//     @property
//     def height(self) -> float:
//         return self.h

//     @property
//     def position(self) -> Vector:
//         return Vector(self.x, self.y)

//     @property
//     def size(self) -> Vector:
//         return Vector(self.w, self.h)

//     def scale(self, scale: float | Vector) -> Rect:
//         if isinstance(scale, Vector):
//             x1, x2 = sorted([self.x * scale.x, (self.x + self.w) * scale.x])
//             y1, y2 = sorted([self.y * scale.y, (self.y + self.h) * scale.y])
//         else:
//             x1, x2 = sorted([self.x * scale, (self.x + self.w) * scale])
//             y1, y2 = sorted([self.y * scale, (self.y + self.h) * scale])
//         return Rect(x1, y1, x2 - x1, y2 - y1)

// class RoundRect(NamedTuple):
//     x: float
//     y: float
//     w: float
//     h: float
//     r: float

//     @property
//     def width(self) -> float:
//         return self.w

//     @property
//     def height(self) -> float:
//         return self.h

//     @property
//     def position(self) -> Vector:
//         return Vector(self.x, self.y)

//     @property
//     def size(self) -> Vector:
//         return Vector(self.w, self.h)

//     @property
//     def radius(self) -> float:
//         return self.r

//     def as_rect(self) -> Rect:
//         return Rect(self.x, self.y, self.w, self.h)

//     def scale(self, scale: float | Vector) -> RoundRect:
//         if isinstance(scale, Vector):
//             x1, x2 = sorted([self.x * scale.x, (self.x + self.w) * scale.x])
//             y1, y2 = sorted([self.y * scale.y, (self.y + self.h) * scale.y])
//             r = self.r * min(abs(scale.x), abs(scale.y))
//         else:
//             x1, x2 = sorted([self.x * scale, (self.x + self.w) * scale])
//             y1, y2 = sorted([self.y * scale, (self.y + self.h) * scale])
//             r = self.r * scale
//         return RoundRect(x1, y1, x2 - x1, y2 - y1, r)

// class Color(
//     # Note: We need to use this call to NamedTuple to make sure Color is a sub-subclass of
//     # NamedTuple otherwise it won't let us override __new__ to validate input
//     NamedTuple("Color", [("r", float), ("g", float), ("b", float)])
// ):
//     def __new__(cls, r: float, g: float, b: float):
//         for key, val in zip("rgb", (r, g, b)):
//             if not 0.0 <= val <= 1.0:
//                 raise ValueError(f"invalid value for '{key}' for Color(): '{val}'")

//         return super().__new__(cls, r, g, b)

//     @staticmethod
//     def from_hex(color: str) -> Color:
//         col = color.lstrip("#")

//         try:
//             if len(col) == 6:
//                 rgb = [int(col[i : i + 2], 16) / 255 for i in range(0, len(col), 2)]
//             elif len(col) == 3:
//                 rgb = [int(c, 16) / 15 for c in col]
//             else:
//                 raise ValueError()
//         except ValueError:
//             raise ValueError(f"invalid literal for Color(): '{color}'") from None

//         return Color(*rgb)

//     def to_hex(self) -> str:
//         return "#" + "".join(f"{int(c * 255 + 0.5):02x}" for c in (self.r, self.g, self.b))

//     def lighter(self, val: float = 0.15) -> Color:
//         if not 0.0 <= val <= 1.0:
//             raise ValueError(f"invalid value for 'val' in call to Color.lighter(): '{val}'")

//         return Color(*(val + (1 - val) * c for c in self))

//     def darker(self, val: float = 0.15) -> Color:
//         if not 0.0 <= val <= 1.0:
//             raise ValueError(f"invalid value for 'val' in call to Color.lighter(): '{val}'")

//         return Color(*((1 - val) * c for c in self))

//     def highlight(self, lum: float = 0.15) -> Color:
//         if not 0.0 <= lum <= 0.5:
//             raise ValueError(f"invalid value for 'val' in call to Color.lighter(): '{lum}'")

//         h, l, s = colorsys.rgb_to_hls(*self)
//         l += lum if l < 0.5 else -lum  # flake8 doesn't like the letter l  # noqa: E741
//         return Color(*colorsys.hls_to_rgb(h, l, s))
