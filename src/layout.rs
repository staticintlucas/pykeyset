#[cfg(feature = "experimental-inspect")]
use std::borrow::Cow;
use std::fs;
use std::path::PathBuf;

use keyset::geom::{KeyUnit, Point, Unit, Vector};
use pyo3::exceptions::{PyTypeError, PyValueError};
#[cfg(feature = "experimental-inspect")]
use pyo3::inspect::types::{ModuleName, TypeInfo};
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

impl From<HomingType> for keyset::key::Homing {
    fn from(value: HomingType) -> Self {
        value.0
    }
}

impl From<keyset::key::Homing> for HomingType {
    fn from(value: keyset::key::Homing) -> Self {
        Self(value)
    }
}

impl<'py> IntoPyObject<'py> for HomingType {
    type Target = PyString;
    type Output = Bound<'py, Self::Target>;
    type Error = std::convert::Infallible;

    #[cfg(feature = "experimental-inspect")]
    const OUTPUT_TYPE: &'static str = "str";

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
        const SCOOP_ALIASES: [&str; 8] = [
            "scoop",
            "scooped",
            "dish",
            "dished",
            "deepdish",
            "deep-dish",
            "deep_dish",
            "deep dish",
        ];
        const BAR_ALIASES: [&str; 3] = ["bar", "barred", "line"];
        const BUMP_ALIASES: [&str; 4] = ["bump", "nub", "dot", "nipple"];

        let val = ob.cast::<PyString>()?;

        if SCOOP_ALIASES.iter().any(|&a| a == val) {
            Ok(Self(keyset::key::Homing::Scoop))
        } else if BAR_ALIASES.iter().any(|&a| a == val) {
            Ok(Self(keyset::key::Homing::Bar))
        } else if BUMP_ALIASES.iter().any(|&a| a == val) {
            Ok(Self(keyset::key::Homing::Bump))
        } else {
            Err(PyValueError::new_err(format!(
                "invalid homing type str: '{val}'"
            )))
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

impl NoneKey {
    pub fn from_size(size: Vector<KeyUnit>) -> Self {
        Self {
            width: size.x.get(),
            height: size.y.get(),
        }
    }
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

impl<'py> IntoPyObject<'py> for NoneKey {
    type Target = NoneKey;
    type Output = Bound<'py, Self::Target>;
    type Error = pyo3::PyErr;

    #[cfg(feature = "experimental-inspect")]
    const OUTPUT_TYPE: &'static str = "pykeyset.layout.NoneKey";

    fn into_pyobject(self, py: Python<'py>) -> Result<Self::Output, Self::Error> {
        Bound::new(py, PyClassInitializer::from(KeyShape).add_subclass(self))
    }

    #[cfg(feature = "experimental-inspect")]
    fn type_output() -> TypeInfo {
        TypeInfo::Class {
            module: ModuleName::CurrentModule,
            name: Cow::from("NoneKey"),
            type_vars: vec![],
        }
    }
}

#[pyclass(module = "pykeyset.layout", extends = KeyShape, get_all, set_all)]
#[derive(Debug, Clone, Copy)]
pub struct NormalKey {
    width: f32,
    height: f32,
}

impl NormalKey {
    pub fn with_size(size: Vector<KeyUnit>) -> Self {
        Self {
            width: size.x.get(),
            height: size.y.get(),
        }
    }
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

impl<'py> IntoPyObject<'py> for NormalKey {
    type Target = Self;
    type Output = Bound<'py, Self::Target>;
    type Error = pyo3::PyErr;

    #[cfg(feature = "experimental-inspect")]
    const OUTPUT_TYPE: &'static str = "pykeyset.layout.NormalKey";

    fn into_pyobject(self, py: Python<'py>) -> Result<Self::Output, Self::Error> {
        Bound::new(py, PyClassInitializer::from(KeyShape).add_subclass(self))
    }

    #[cfg(feature = "experimental-inspect")]
    fn type_output() -> TypeInfo {
        TypeInfo::Class {
            module: ModuleName::CurrentModule,
            name: Cow::from("NormalKey"),
            type_vars: vec![],
        }
    }
}

#[pyclass(module = "pykeyset.layout", extends = KeyShape, get_all, set_all)]
#[derive(Debug, Clone, Copy)]
pub struct SpaceKey {
    width: f32,
    height: f32,
}

impl SpaceKey {
    pub fn with_size(size: Vector<KeyUnit>) -> Self {
        Self {
            width: size.x.get(),
            height: size.y.get(),
        }
    }
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

impl<'py> IntoPyObject<'py> for SpaceKey {
    type Target = Self;
    type Output = Bound<'py, Self::Target>;
    type Error = pyo3::PyErr;

    #[cfg(feature = "experimental-inspect")]
    const OUTPUT_TYPE: &'static str = "pykeyset.layout.SpaceKey";

    fn into_pyobject(self, py: Python<'py>) -> Result<Self::Output, Self::Error> {
        Bound::new(py, PyClassInitializer::from(KeyShape).add_subclass(self))
    }

    #[cfg(feature = "experimental-inspect")]
    fn type_output() -> TypeInfo {
        TypeInfo::Class {
            module: ModuleName::CurrentModule,
            name: Cow::from("SpaceKey"),
            type_vars: vec![],
        }
    }
}

#[pyclass(module = "pykeyset.layout", extends = KeyShape, get_all, set_all)]
#[derive(Debug, Clone, Copy)]
pub struct HomingKey {
    r#type: Option<HomingType>,
}

impl HomingKey {
    pub fn with_type(r#type: Option<keyset::key::Homing>) -> Self {
        Self {
            r#type: r#type.map(Into::into),
        }
    }
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
        keyset::key::Shape::Homing(value.r#type.map(Into::into))
    }
}

impl<'py> IntoPyObject<'py> for HomingKey {
    type Target = Self;
    type Output = Bound<'py, Self::Target>;
    type Error = pyo3::PyErr;

    #[cfg(feature = "experimental-inspect")]
    const OUTPUT_TYPE: &'static str = "pykeyset.layout.HomingKey";

    fn into_pyobject(self, py: Python<'py>) -> Result<Self::Output, Self::Error> {
        Bound::new(py, PyClassInitializer::from(KeyShape).add_subclass(self))
    }

    #[cfg(feature = "experimental-inspect")]
    fn type_output() -> TypeInfo {
        TypeInfo::Class {
            module: ModuleName::CurrentModule,
            name: Cow::from("HomingKey"),
            type_vars: vec![],
        }
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

impl<'py> IntoPyObject<'py> for SteppedCaps {
    type Target = Self;
    type Output = Bound<'py, Self::Target>;
    type Error = pyo3::PyErr;

    #[cfg(feature = "experimental-inspect")]
    const OUTPUT_TYPE: &'static str = "pykeyset.layout.SteppedCaps";

    fn into_pyobject(self, py: Python<'py>) -> Result<Self::Output, Self::Error> {
        Bound::new(py, PyClassInitializer::from(KeyShape).add_subclass(self))
    }

    #[cfg(feature = "experimental-inspect")]
    fn type_output() -> TypeInfo {
        TypeInfo::Class {
            module: ModuleName::CurrentModule,
            name: Cow::from("SteppedCaps"),
            type_vars: vec![],
        }
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

impl<'py> IntoPyObject<'py> for IsoVertical {
    type Target = Self;
    type Output = Bound<'py, Self::Target>;
    type Error = pyo3::PyErr;

    #[cfg(feature = "experimental-inspect")]
    const OUTPUT_TYPE: &'static str = "pykeyset.layout.IsoVertical";

    fn into_pyobject(self, py: Python<'py>) -> Result<Self::Output, Self::Error> {
        Bound::new(py, PyClassInitializer::from(KeyShape).add_subclass(self))
    }

    #[cfg(feature = "experimental-inspect")]
    fn type_output() -> TypeInfo {
        TypeInfo::Class {
            module: ModuleName::CurrentModule,
            name: Cow::from("IsoVertical"),
            type_vars: vec![],
        }
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

impl<'py> IntoPyObject<'py> for IsoHorizontal {
    type Target = Self;
    type Output = Bound<'py, Self::Target>;
    type Error = pyo3::PyErr;

    #[cfg(feature = "experimental-inspect")]
    const OUTPUT_TYPE: &'static str = "pykeyset.layout.IsoHorizontal";

    fn into_pyobject(self, py: Python<'py>) -> Result<Self::Output, Self::Error> {
        Bound::new(py, PyClassInitializer::from(KeyShape).add_subclass(self))
    }

    #[cfg(feature = "experimental-inspect")]
    fn type_output() -> TypeInfo {
        TypeInfo::Class {
            module: ModuleName::CurrentModule,
            name: Cow::from("IsoHorizontal"),
            type_vars: vec![],
        }
    }
}

#[derive(Debug, Clone, Copy)]
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

impl From<keyset::key::Shape> for KeyShapeEnum {
    fn from(value: keyset::key::Shape) -> Self {
        match value {
            keyset::key::Shape::None(size) => Self::NoneKey(NoneKey::from_size(size)),
            keyset::key::Shape::Normal(size) => Self::NormalKey(NormalKey::with_size(size)),
            keyset::key::Shape::Space(size) => Self::SpaceKey(SpaceKey::with_size(size)),
            keyset::key::Shape::Homing(homing) => Self::HomingKey(HomingKey::with_type(homing)),
            keyset::key::Shape::SteppedCaps => Self::SteppedCaps(SteppedCaps),
            keyset::key::Shape::IsoVertical => Self::IsoVertical(IsoVertical),
            keyset::key::Shape::IsoHorizontal => Self::IsoHorizontal(IsoHorizontal),
        }
    }
}

impl<'py> FromPyObject<'py> for KeyShapeEnum {
    #[cfg(feature = "experimental-inspect")]
    const INPUT_TYPE: &'static str = <KeyShape as FromPyObject>::INPUT_TYPE;

    fn extract_bound(obj: &::pyo3::Bound<'py, ::pyo3::PyAny>) -> ::pyo3::PyResult<Self> {
        if let Ok(result) = obj.extract::<NoneKey>() {
            return Ok(KeyShapeEnum::NoneKey(result));
        }
        if let Ok(result) = obj.extract::<NormalKey>() {
            return Ok(KeyShapeEnum::NormalKey(result));
        }
        if let Ok(result) = obj.extract::<SpaceKey>() {
            return Ok(KeyShapeEnum::SpaceKey(result));
        }
        if let Ok(result) = obj.extract::<HomingKey>() {
            return Ok(KeyShapeEnum::HomingKey(result));
        }
        if let Ok(result) = obj.extract::<SteppedCaps>() {
            return Ok(KeyShapeEnum::SteppedCaps(result));
        }
        if let Ok(result) = obj.extract::<IsoVertical>() {
            return Ok(KeyShapeEnum::IsoVertical(result));
        }
        if let Ok(result) = obj.extract::<IsoHorizontal>() {
            return Ok(KeyShapeEnum::IsoHorizontal(result));
        }
        Err(PyTypeError::new_err(format!(
            "'{}' can not be converted to KeyShape",
            obj.get_type().name()?
        )))
    }

    #[cfg(feature = "experimental-inspect")]
    fn type_input() -> TypeInfo {
        <KeyShape as FromPyObject>::type_input()
    }
}

impl<'py> IntoPyObject<'py> for KeyShapeEnum {
    type Target = PyAny;
    type Output = Bound<'py, Self::Target>;
    type Error = pyo3::PyErr;

    #[cfg(feature = "experimental-inspect")]
    const OUTPUT_TYPE: &'static str = <KeyShape as IntoPyObject>::OUTPUT_TYPE;

    fn into_pyobject(self, py: Python<'py>) -> Result<Self::Output, Self::Error> {
        match self {
            KeyShapeEnum::NoneKey(shape) => Ok(shape.into_pyobject(py)?.into_any()),
            KeyShapeEnum::NormalKey(shape) => Ok(shape.into_pyobject(py)?.into_any()),
            KeyShapeEnum::SpaceKey(shape) => Ok(shape.into_pyobject(py)?.into_any()),
            KeyShapeEnum::HomingKey(shape) => Ok(shape.into_pyobject(py)?.into_any()),
            KeyShapeEnum::SteppedCaps(shape) => Ok(shape.into_pyobject(py)?.into_any()),
            KeyShapeEnum::IsoVertical(shape) => Ok(shape.into_pyobject(py)?.into_any()),
            KeyShapeEnum::IsoHorizontal(shape) => Ok(shape.into_pyobject(py)?.into_any()),
        }
    }

    #[cfg(feature = "experimental-inspect")]
    fn type_output() -> TypeInfo {
        <KeyShape as IntoPyObject>::type_output()
    }
}

#[pyclass(module = "pykeyset.layout")]
#[derive(Debug, Clone)]
pub struct Legend(keyset::key::Legend);

#[pymethods]
impl Legend {
    #[new]
    #[pyo3(signature = (*, text, size, color))]
    pub fn new(text: &str, size: usize, color: Color) -> Self {
        Self(keyset::key::Legend::new(text, size, color.into()))
    }

    #[getter]
    fn get_text(&self) -> String {
        self.0.text.to_string()
    }

    #[setter]
    fn set_text(&mut self, text: &str) {
        self.0.text = keyset::key::Text::parse_from(text);
    }

    #[getter]
    fn get_size(&self) -> usize {
        self.0.size_idx
    }

    #[setter]
    fn set_size(&mut self, size: usize) {
        self.0.size_idx = size;
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

#[pyclass(module = "pykeyset.layout")]
#[derive(Debug, Clone)]
pub struct Key(keyset::Key);

#[pymethods]
impl Key {
    #[new]
    #[pyo3(signature = (
        *,
        x = 0.0,
        y = 0.0,
        shape = KeyShapeEnum::NormalKey(NormalKey { width: 1.0, height: 1.0 }),
        color = keyset::Key::default().color.into(),
        legends = vec![],
    ))]
    fn new(
        x: f32,
        y: f32,
        shape: KeyShapeEnum,
        color: Color,
        mut legends: Vec<Bound<'_, PyAny>>,
    ) -> PyResult<Self> {
        legends.truncate(keyset::Key::LEGEND_COUNT);
        let mut legends = legends
            .into_iter()
            .map(|leg| {
                leg.extract::<Option<Legend>>()
                    .map(|opt| opt.map(|Legend(l)| Box::new(l)))
            })
            .collect::<Result<Vec<_>, _>>()?;
        legends.resize(keyset::Key::LEGEND_COUNT, None);

        let result = keyset::Key {
            position: Point::new(KeyUnit(x), KeyUnit(y)),
            shape: shape.into(),
            color: color.into(),
            legends: legends.try_into().unwrap(),
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

    #[getter]
    fn get_shape(&self) -> KeyShapeEnum {
        self.0.shape.into()
    }

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

    #[getter]
    fn get_legends(&self) -> Vec<Option<Legend>> {
        self.0
            .legends
            .iter()
            .map(|opt| opt.as_ref().map(|l| Legend(*l.clone())))
            .collect()
    }

    #[setter]
    fn set_legends(&mut self, mut legends: Vec<Bound<'_, PyAny>>) -> PyResult<()> {
        legends.truncate(keyset::Key::LEGEND_COUNT);
        let mut legends = legends
            .into_iter()
            .map(|leg| {
                leg.extract::<Option<Legend>>()
                    .map(|opt| opt.map(|Legend(l)| Box::new(l)))
            })
            .collect::<Result<Vec<_>, _>>()?;

        legends.resize(keyset::Key::LEGEND_COUNT, None);
        self.0.legends = legends.try_into().unwrap();

        Ok(())
    }
}
