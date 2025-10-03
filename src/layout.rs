use std::{fs, path::PathBuf};

use keyset::geom::{KeyUnit, Point, Unit, Vector};
use pyo3::exceptions::PyValueError;
#[cfg(feature = "experimental-inspect")]
use pyo3::inspect::types::TypeInfo;
use pyo3::prelude::*;
use pyo3::types::PyString;

use crate::color::Color;

#[pyfunction]
pub fn load(path: PathBuf) -> PyResult<Vec<Key>> {
    keyset::kle::from_json(&fs::read(path)?)
        .map(|a| a.iter().cloned().map(Key).collect())
        .map_err(|error| PyValueError::new_err(format!("unable to parse layout: {error}")))
}

#[pyfunction]
pub fn loadb(bytes: &[u8]) -> PyResult<Vec<Key>> {
    keyset::kle::from_json(bytes)
        .map(|a| a.iter().cloned().map(Key).collect())
        .map_err(|error| PyValueError::new_err(format!("unable to parse layout: {error}")))
}

#[pyfunction]
pub fn loads(str: &str) -> PyResult<Vec<Key>> {
    keyset::kle::from_json_str(str)
        .map(|a| a.iter().cloned().map(Key).collect())
        .map_err(|error| PyValueError::new_err(format!("unable to parse layout: {error}")))
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct HomingType(keyset::key::Homing);

impl<'py> IntoPyObject<'py> for HomingType {
    type Target = PyString;
    type Output = Bound<'py, Self::Target>;
    type Error = std::convert::Infallible;

    fn into_pyobject(self, py: Python<'py>) -> Result<Self::Output, Self::Error> {
        match self.0 {
            keyset::key::Homing::Scoop => "scoop",
            keyset::key::Homing::Bar => "bar",
            keyset::key::Homing::Bump => "bump",
        }
        .into_pyobject(py)
    }

    #[cfg(feature = "experimental-inspect")]
    fn type_output() -> TypeInfo {
        TypeInfo::builtin("str")
    }
}

impl<'py> FromPyObject<'py> for HomingType {
    #[cfg(feature = "experimental-inspect")]
    const INPUT_TYPE: &'static str = "str";

    fn extract_bound(ob: &Bound<'py, PyAny>) -> PyResult<Self> {
        let val = ob.extract::<String>()?;
        match &*val {
            "scoop" | "scooped" | "dish" | "dished" | "deepdish" | "deep-dish" | "deep_dish"
            | "deep dish" => Ok(Self(keyset::key::Homing::Scoop)),
            "bar" | "barred" | "line" => Ok(Self(keyset::key::Homing::Bar)),
            "bump" | "nub" | "dot" | "nipple" => Ok(Self(keyset::key::Homing::Bump)),
            _ => Err(PyValueError::new_err(format!(
                "invalid homing type str: '{val}'"
            ))),
        }
    }

    #[cfg(feature = "experimental-inspect")]
    fn type_input() -> TypeInfo {
        TypeInfo::builtin("str")
    }
}

#[pyclass(module = "pykeyset.layout", subclass)]
#[derive(Debug, Clone, Copy)]
pub struct KeyShape;

#[pyclass(module = "pykeyset.layout", extends = KeyShape, get_all, set_all)]
#[derive(Debug, Clone, Copy)]
pub struct NoneKey {
    width: f32,
    height: f32,
}

#[pymethods]
impl NoneKey {
    #[new]
    #[pyo3(signature = (/, width, height))]
    fn new(width: f32, height: f32) -> (Self, KeyShape) {
        (Self { width, height }, KeyShape)
    }

    #[getter]
    fn get_size(&self) -> (f32, f32) {
        (self.width, self.height)
    }

    #[setter]
    fn set_size(&mut self, size: (f32, f32)) {
        self.width = size.0;
        self.height = size.1;
    }
}

impl From<NoneKey> for keyset::key::Shape {
    fn from(value: NoneKey) -> Self {
        keyset::key::Shape::None(Vector::new(KeyUnit(value.width), KeyUnit(value.height)))
    }
}

#[pyclass(module = "pykeyset.layout", extends = KeyShape, get_all, set_all)]
#[derive(Debug, Clone, Copy)]
pub struct NormalKey {
    width: f32,
    height: f32,
}

#[pymethods]
impl NormalKey {
    #[new]
    #[pyo3(signature = (/, width, height))]
    fn new(width: f32, height: f32) -> (Self, KeyShape) {
        (Self { width, height }, KeyShape)
    }

    #[getter]
    fn get_size(&self) -> (f32, f32) {
        (self.width, self.height)
    }

    #[setter]
    fn set_size(&mut self, size: (f32, f32)) {
        self.width = size.0;
        self.height = size.1;
    }
}

impl From<NormalKey> for keyset::key::Shape {
    fn from(value: NormalKey) -> Self {
        keyset::key::Shape::Normal(Vector::new(KeyUnit(value.width), KeyUnit(value.height)))
    }
}

#[pyclass(module = "pykeyset.layout", extends = KeyShape, get_all, set_all)]
#[derive(Debug, Clone, Copy)]
pub struct SpaceKey {
    width: f32,
    height: f32,
}

#[pymethods]
impl SpaceKey {
    #[new]
    #[pyo3(signature = (/, width, height))]
    fn new(width: f32, height: f32) -> (Self, KeyShape) {
        (Self { width, height }, KeyShape)
    }

    #[getter]
    fn get_size(&self) -> (f32, f32) {
        (self.width, self.height)
    }

    #[setter]
    fn set_size(&mut self, size: (f32, f32)) {
        self.width = size.0;
        self.height = size.1;
    }
}

impl From<SpaceKey> for keyset::key::Shape {
    fn from(value: SpaceKey) -> Self {
        keyset::key::Shape::Space(Vector::new(KeyUnit(value.width), KeyUnit(value.height)))
    }
}

#[pyclass(module = "pykeyset.layout", extends = KeyShape, get_all, set_all)]
#[derive(Debug, Clone, Copy)]
pub struct HomingKey {
    r#type: Option<HomingType>,
}

#[pymethods]
impl HomingKey {
    #[new]
    #[pyo3(signature = (/, r#type = None))]
    fn new(r#type: Option<HomingType>) -> (Self, KeyShape) {
        (Self { r#type }, KeyShape)
    }
}

impl From<HomingKey> for keyset::key::Shape {
    fn from(value: HomingKey) -> Self {
        keyset::key::Shape::Homing(value.r#type.map(|t| t.0))
    }
}

#[pyclass(module = "pykeyset.layout", extends = KeyShape)]
#[derive(Debug, Clone, Copy)]
pub struct SteppedCaps;

#[pymethods]
impl SteppedCaps {
    #[new]
    fn new() -> (Self, KeyShape) {
        (Self, KeyShape)
    }
}

impl From<SteppedCaps> for keyset::key::Shape {
    fn from(value: SteppedCaps) -> Self {
        _ = value;
        keyset::key::Shape::SteppedCaps
    }
}

#[pyclass(module = "pykeyset.layout", extends = KeyShape)]
#[derive(Debug, Clone, Copy)]
pub struct IsoVertical;

#[pymethods]
impl IsoVertical {
    #[new]
    fn new() -> (Self, KeyShape) {
        (Self, KeyShape)
    }
}

impl From<IsoVertical> for keyset::key::Shape {
    fn from(value: IsoVertical) -> Self {
        _ = value;
        keyset::key::Shape::IsoVertical
    }
}

#[pyclass(module = "pykeyset.layout", extends = KeyShape)]
#[derive(Debug, Clone, Copy)]
pub struct IsoHorizontal;

#[pymethods]
impl IsoHorizontal {
    #[new]
    fn new() -> (Self, KeyShape) {
        (Self, KeyShape)
    }
}

impl From<IsoHorizontal> for keyset::key::Shape {
    fn from(value: IsoHorizontal) -> Self {
        _ = value;
        keyset::key::Shape::IsoHorizontal
    }
}

#[derive(Debug, Clone, Copy, FromPyObject)]
enum KeyShapeEnum {
    NoneKey(NoneKey),
    NormalKey(NormalKey),
    SpaceKey(SpaceKey),
    HomingKey(HomingKey),
    SteppedCaps(SteppedCaps),
    IsoVertical(IsoVertical),
    IsoHorizontal(IsoHorizontal),
}

impl From<KeyShapeEnum> for keyset::key::Shape {
    fn from(value: KeyShapeEnum) -> Self {
        match value {
            KeyShapeEnum::NoneKey(shape) => shape.into(),
            KeyShapeEnum::NormalKey(shape) => shape.into(),
            KeyShapeEnum::SpaceKey(shape) => shape.into(),
            KeyShapeEnum::HomingKey(shape) => shape.into(),
            KeyShapeEnum::SteppedCaps(shape) => shape.into(),
            KeyShapeEnum::IsoVertical(shape) => shape.into(),
            KeyShapeEnum::IsoHorizontal(shape) => shape.into(),
        }
    }
}

#[pyclass(module = "pykeyset.layout")]
#[derive(Debug, Clone)]
pub struct Key(keyset::Key);

#[pymethods]
impl Key {
    #[new]
    #[pyo3(signature = (*, x = 0.0, y = 0.0, shape = KeyShapeEnum::NormalKey(NormalKey { width: 1.0, height: 1.0 }), color = keyset::Key::default().color.into()))]
    fn new(
        x: f32,
        y: f32,
        shape: KeyShapeEnum,
        color: Color,
        // TODO: legends: [Legend; 9],
    ) -> PyResult<Self> {
        let result = keyset::Key {
            position: Point::new(KeyUnit(x), KeyUnit(y)),
            shape: shape.into(),
            color: color.into(),
            ..Default::default()
        };

        Ok(Self(result))
    }

    #[getter]
    fn get_x(&self) -> f32 {
        self.0.position.x.get()
    }

    #[setter]
    fn set_x(&mut self, x: f32) {
        self.0.position.x = KeyUnit(x);
    }

    #[getter]
    fn get_y(&self) -> f32 {
        self.0.position.y.get()
    }

    #[setter]
    fn set_y(&mut self, y: f32) {
        self.0.position.y = KeyUnit(y);
    }

    #[getter]
    fn get_position(&self) -> (f32, f32) {
        (self.0.position.x.get(), self.0.position.y.get())
    }

    #[setter]
    fn set_position(&mut self, position: (f32, f32)) {
        self.0.position.x = KeyUnit(position.0);
        self.0.position.y = KeyUnit(position.1);
    }

    // #[getter]
    // fn get_shape(&self) ->  {
    //     TODO
    // }

    #[setter]
    fn set_shape(&mut self, shape: KeyShapeEnum) {
        self.0.shape = shape.into();
    }

    #[getter]
    fn get_color(&self) -> Color {
        self.0.color.into()
    }

    #[setter]
    fn set_color(&mut self, color: Color) {
        self.0.color = color.into();
    }
}
