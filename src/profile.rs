use std::fs;
use std::path::PathBuf;

use const_format::concatcp;
use keyset::geom::{ConvertFrom as _, ConvertInto as _, Mm, Unit, Vector};
use pyo3::exceptions::{PyNotImplementedError, PyTypeError, PyValueError};
#[cfg(feature = "experimental-inspect")]
use pyo3::inspect::types::{ModuleName, TypeInfo};
use pyo3::prelude::*;
use pyo3::types::PyString;
use pyo3::PyTypeInfo;

#[derive(Debug, Clone, Copy, Default)]
pub enum ProfileFormat {
    #[default]
    Toml,
    Json,
}

impl<'py> IntoPyObject<'py> for ProfileFormat {
    type Target = PyString;
    type Output = Bound<'py, Self::Target>;
    type Error = std::convert::Infallible;

    #[cfg(feature = "experimental-inspect")]
    const OUTPUT_TYPE: &'static str = "str";

    fn into_pyobject(self, py: Python<'py>) -> Result<Self::Output, Self::Error> {
        match self {
            Self::Toml => "toml",
            Self::Json => "json",
        }
        .into_pyobject(py)
    }

    #[cfg(feature = "experimental-inspect")]
    fn type_output() -> TypeInfo {
        TypeInfo::builtin("str")
    }
}

impl<'a, 'py> FromPyObject<'a, 'py> for ProfileFormat {
    type Error = PyErr;

    #[cfg(feature = "experimental-inspect")]
    const INPUT_TYPE: &'static str = "str";

    fn extract(ob: Borrowed<'a, 'py, PyAny>) -> PyResult<Self> {
        let val = ob.cast::<PyString>()?;
        if val == "toml" {
            Ok(Self::Toml)
        } else if val == "json" {
            Ok(Self::Json)
        } else {
            Err(PyValueError::new_err(format!(
                "'{}' is not a valid format, expected 'toml' or 'json'.",
                val.to_string_lossy()
            )))
        }
    }

    #[cfg(feature = "experimental-inspect")]
    fn type_input() -> TypeInfo {
        TypeInfo::builtin("str")
    }
}

#[pyfunction(signature = (path, *, format = ProfileFormat::default()))]
pub fn load(path: PathBuf, format: ProfileFormat) -> PyResult<Profile> {
    loadb(&fs::read(path)?, format)
}

#[pyfunction(signature = (bytes, *, format = ProfileFormat::default()))]
pub fn loadb(bytes: &[u8], format: ProfileFormat) -> PyResult<Profile> {
    match format {
        ProfileFormat::Toml => keyset::Profile::from_toml(bytes)
            .map(Into::into)
            .map_err(|error| {
                PyValueError::new_err(format!("unable to parse TOML profile: {error}"))
            }),
        ProfileFormat::Json => keyset::Profile::from_json(bytes)
            .map(Into::into)
            .map_err(|error| {
                PyValueError::new_err(format!("unable to parse JSON profile: {error}"))
            }),
    }
}

#[pyfunction(signature = (str, *, format = ProfileFormat::default()))]
pub fn loads(str: &str, format: ProfileFormat) -> PyResult<Profile> {
    loadb(str.as_bytes(), format)
}

#[pyclass(module = "pykeyset.profile", subclass)]
#[derive(Debug, Clone, Copy)]
pub struct ProfileType;

#[pymethods]
impl ProfileType {
    #[new]
    fn new() -> PyResult<Self> {
        Err(PyTypeError::new_err(concatcp!(
            "can't instantiate abstract class ",
            <ProfileType as PyTypeInfo>::NAME
        )))
    }

    #[getter]
    fn depth(&self) -> PyResult<f32> {
        Err(PyNotImplementedError::new_err(concatcp!(
            "attribute 'depth' of abstract class ",
            <ProfileType as PyTypeInfo>::NAME,
            " is not implemented"
        )))
    }
}

#[pyclass(module = "pykeyset.profile", extends = ProfileType)]
#[derive(Debug, Clone, Copy)]
pub struct Cylindrical {
    depth: Mm,
}

#[pymethods]
impl Cylindrical {
    #[new]
    fn new(depth: f32) -> (Self, ProfileType) {
        (Self { depth: Mm(depth) }, ProfileType)
    }

    #[getter]
    fn depth(&self) -> f32 {
        self.depth.get()
    }
}

impl From<Cylindrical> for keyset::profile::Type {
    fn from(value: Cylindrical) -> Self {
        keyset::profile::Type::Cylindrical {
            depth: value.depth.convert_into(),
        }
    }
}

impl<'py> IntoPyObject<'py> for Cylindrical {
    type Target = Self;
    type Output = Bound<'py, Self::Target>;
    type Error = PyErr;

    #[cfg(feature = "experimental-inspect")]
    const OUTPUT_TYPE: &'static str = "pykeyset.profile.Cylindrical";

    fn into_pyobject(self, py: Python<'py>) -> Result<Self::Output, Self::Error> {
        Bound::new(py, PyClassInitializer::from(ProfileType).add_subclass(self))
    }

    #[cfg(feature = "experimental-inspect")]
    fn type_output() -> TypeInfo {
        TypeInfo::Class {
            module: ModuleName::CurrentModule,
            name: "Cylindrical".into(),
            type_vars: vec![],
        }
    }
}

#[pyclass(module = "pykeyset.profile", extends = ProfileType)]
#[derive(Debug, Clone, Copy)]
pub struct Spherical {
    depth: Mm,
}

#[pymethods]
impl Spherical {
    #[new]
    fn new(depth: f32) -> (Self, ProfileType) {
        (Self { depth: Mm(depth) }, ProfileType)
    }

    #[getter]
    fn depth(&self) -> f32 {
        self.depth.get()
    }
}

impl From<Spherical> for keyset::profile::Type {
    fn from(value: Spherical) -> Self {
        keyset::profile::Type::Spherical {
            depth: value.depth.convert_into(),
        }
    }
}

impl<'py> IntoPyObject<'py> for Spherical {
    type Target = Self;
    type Output = Bound<'py, Self::Target>;
    type Error = PyErr;

    #[cfg(feature = "experimental-inspect")]
    const OUTPUT_TYPE: &'static str = "pykeyset.profile.Spherical";

    fn into_pyobject(self, py: Python<'py>) -> Result<Self::Output, Self::Error> {
        Bound::new(py, PyClassInitializer::from(ProfileType).add_subclass(self))
    }

    #[cfg(feature = "experimental-inspect")]
    fn type_output() -> TypeInfo {
        TypeInfo::Class {
            module: ModuleName::CurrentModule,
            name: "Spherical".into(),
            type_vars: vec![],
        }
    }
}

#[pyclass(module = "pykeyset.profile", extends = ProfileType)]
#[derive(Debug, Clone, Copy)]
pub struct Flat;

#[pymethods]
impl Flat {
    #[new]
    fn new() -> (Self, ProfileType) {
        (Self, ProfileType)
    }

    #[getter]
    fn depth(&self) -> f32 {
        0.0
    }
}

impl From<Flat> for keyset::profile::Type {
    fn from(_: Flat) -> Self {
        keyset::profile::Type::Flat
    }
}

impl<'py> IntoPyObject<'py> for Flat {
    type Target = Self;
    type Output = Bound<'py, Self::Target>;
    type Error = PyErr;

    #[cfg(feature = "experimental-inspect")]
    const OUTPUT_TYPE: &'static str = "pykeyset.profile.Flat";

    fn into_pyobject(self, py: Python<'py>) -> Result<Self::Output, Self::Error> {
        Bound::new(py, PyClassInitializer::from(ProfileType).add_subclass(self))
    }

    #[cfg(feature = "experimental-inspect")]
    fn type_output() -> TypeInfo {
        TypeInfo::Class {
            module: ModuleName::CurrentModule,
            name: "Flat".into(),
            type_vars: vec![],
        }
    }
}

#[derive(Debug, Clone, Copy)]
enum ProfileTypeEnum {
    Cylindrical(Cylindrical),
    Spherical(Spherical),
    Flat(Flat),
}

impl From<ProfileTypeEnum> for keyset::profile::Type {
    fn from(value: ProfileTypeEnum) -> Self {
        match value {
            ProfileTypeEnum::Cylindrical(typ) => typ.into(),
            ProfileTypeEnum::Spherical(typ) => typ.into(),
            ProfileTypeEnum::Flat(typ) => typ.into(),
        }
    }
}

impl From<keyset::profile::Type> for ProfileTypeEnum {
    fn from(value: keyset::profile::Type) -> Self {
        use keyset::profile::Type;
        match value {
            Type::Cylindrical { depth } => ProfileTypeEnum::Cylindrical(Cylindrical {
                depth: depth.convert_into(),
            }),
            Type::Spherical { depth } => ProfileTypeEnum::Spherical(Spherical {
                depth: depth.convert_into(),
            }),
            Type::Flat => ProfileTypeEnum::Flat(Flat),
        }
    }
}

impl<'a, 'py> FromPyObject<'a, 'py> for ProfileTypeEnum {
    type Error = PyErr;

    #[cfg(feature = "experimental-inspect")]
    const INPUT_TYPE: &'static str = <ProfileType as FromPyObject>::INPUT_TYPE;

    fn extract(obj: Borrowed<'a, 'py, PyAny>) -> PyResult<Self> {
        if let Ok(result) = obj.extract::<Cylindrical>() {
            return Ok(ProfileTypeEnum::Cylindrical(result));
        }
        if let Ok(result) = obj.extract::<Spherical>() {
            return Ok(ProfileTypeEnum::Spherical(result));
        }
        if let Ok(result) = obj.extract::<Flat>() {
            return Ok(ProfileTypeEnum::Flat(result));
        }
        Err(PyTypeError::new_err(format!(
            "'{}' can not be converted to ProfileType",
            obj.get_type().name()?
        )))
    }

    #[cfg(feature = "experimental-inspect")]
    fn type_input() -> TypeInfo {
        <ProfileType as FromPyObject>::type_input()
    }
}

impl<'py> IntoPyObject<'py> for ProfileTypeEnum {
    type Target = PyAny;
    type Output = Bound<'py, Self::Target>;
    type Error = PyErr;

    #[cfg(feature = "experimental-inspect")]
    const OUTPUT_TYPE: &'static str = <ProfileType as IntoPyObject>::OUTPUT_TYPE;

    fn into_pyobject(self, py: Python<'py>) -> Result<Self::Output, Self::Error> {
        match self {
            ProfileTypeEnum::Cylindrical(typ) => Ok(typ.into_pyobject(py)?.into_any()),
            ProfileTypeEnum::Spherical(typ) => Ok(typ.into_pyobject(py)?.into_any()),
            ProfileTypeEnum::Flat(typ) => Ok(typ.into_pyobject(py)?.into_any()),
        }
    }

    #[cfg(feature = "experimental-inspect")]
    fn type_output() -> TypeInfo {
        <ProfileType as IntoPyObject>::type_output()
    }
}

#[pyclass(module = "pykeyset.profile", get_all, set_all)]
#[derive(Debug, Clone, Copy)]
pub struct HomingScoop {
    depth: f32,
}

impl From<HomingScoop> for keyset::profile::ScoopProps {
    fn from(value: HomingScoop) -> Self {
        keyset::profile::ScoopProps {
            depth: Mm(value.depth).convert_into(),
        }
    }
}

impl From<keyset::profile::ScoopProps> for HomingScoop {
    fn from(value: keyset::profile::ScoopProps) -> Self {
        Self {
            depth: Mm::convert_from(value.depth).get(),
        }
    }
}

#[pyclass(module = "pykeyset.profile", get_all, set_all)]
#[derive(Debug, Clone, Copy)]
pub struct HomingBar {
    width: f32,
    height: f32,
    y_offset: f32,
}

impl From<HomingBar> for keyset::profile::BarProps {
    fn from(value: HomingBar) -> Self {
        keyset::profile::BarProps {
            size: Vector::new(Mm(value.width), Mm(value.height)).convert_into(),
            y_offset: Mm(value.y_offset).convert_into(),
        }
    }
}

impl From<keyset::profile::BarProps> for HomingBar {
    fn from(value: keyset::profile::BarProps) -> Self {
        Self {
            width: Mm::convert_from(value.size.x).get(),
            height: Mm::convert_from(value.size.y).get(),
            y_offset: Mm::convert_from(value.y_offset).get(),
        }
    }
}

#[pymethods]
impl HomingBar {
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

#[pyclass(module = "pykeyset.profile", get_all, set_all)]
#[derive(Debug, Clone, Copy)]
pub struct HomingBump {
    diameter: f32,
    y_offset: f32,
}

impl From<HomingBump> for keyset::profile::BumpProps {
    fn from(value: HomingBump) -> Self {
        keyset::profile::BumpProps {
            diameter: Mm(value.diameter).convert_into(),
            y_offset: Mm(value.y_offset).convert_into(),
        }
    }
}

impl From<keyset::profile::BumpProps> for HomingBump {
    fn from(value: keyset::profile::BumpProps) -> Self {
        Self {
            diameter: Mm::convert_from(value.diameter).get(),
            y_offset: Mm::convert_from(value.y_offset).get(),
        }
    }
}

#[pymethods]
impl HomingBump {
    #[getter]
    fn get_radius(&self) -> f32 {
        self.diameter * 0.5
    }

    #[setter]
    fn set_radius(&mut self, radius: f32) {
        self.diameter = radius * 2.0;
    }
}

#[pyclass(module = "pykeyset.profile", get_all, set_all)]
#[derive(Debug, Clone, Copy)]
pub struct Homing {
    default: crate::layout::HomingType,
    scoop: HomingScoop,
    bar: HomingBar,
    bump: HomingBump,
}

impl From<Homing> for keyset::profile::HomingProps {
    fn from(value: Homing) -> Self {
        Self {
            default: value.default.into(),
            scoop: value.scoop.into(),
            bar: value.bar.into(),
            bump: value.bump.into(),
        }
    }
}

impl From<keyset::profile::HomingProps> for Homing {
    fn from(value: keyset::profile::HomingProps) -> Self {
        Self {
            default: value.default.into(),
            scoop: value.scoop.into(),
            bar: value.bar.into(),
            bump: value.bump.into(),
        }
    }
}

#[pyclass(module = "pykeyset.profile", get_all, set_all)]
#[derive(Debug, Clone, Copy)]
pub struct LegendMargin {
    top: f32,
    right: f32,
    bottom: f32,
    left: f32,
}

#[pymethods]
impl LegendMargin {
    #[new]
    #[pyo3(signature = (/, top, right, bottom, left))]
    fn new(top: f32, right: f32, bottom: f32, left: f32) -> Self {
        Self {
            top,
            right,
            bottom,
            left,
        }
    }
}

#[pyclass(module = "pykeyset.profile", get_all, set_all)]
#[derive(Debug, Clone, Copy)]
pub struct LegendGeometry {
    height: f32,
    margin: LegendMargin,
}

impl From<LegendGeometry> for keyset::profile::LegendGeom {
    fn from(value: LegendGeometry) -> Self {
        Self {
            height: Mm(value.height).convert_into(),
            margin: keyset::geom::OffsetRect::new(
                Mm(value.margin.top),
                Mm(value.margin.right),
                Mm(value.margin.bottom),
                Mm(value.margin.left),
            )
            .convert_into(),
        }
    }
}

impl From<keyset::profile::LegendGeom> for LegendGeometry {
    fn from(value: keyset::profile::LegendGeom) -> Self {
        Self {
            height: Mm::convert_from(value.height).get(),
            margin: LegendMargin {
                top: Mm::convert_from(value.margin.top()).get(),
                bottom: Mm::convert_from(value.margin.bottom()).get(),
                left: Mm::convert_from(value.margin.left()).get(),
                right: Mm::convert_from(value.margin.right()).get(),
            },
        }
    }
}

#[pyclass(module = "pykeyset.profile", get_all, set_all)]
#[derive(Debug, Clone, Copy)]
pub struct LegendGeometryMap {
    alpha: LegendGeometry,
    symbol: LegendGeometry,
    modifier: LegendGeometry,
}

impl From<LegendGeometryMap> for keyset::profile::LegendGeomMap {
    fn from(value: LegendGeometryMap) -> Self {
        Self {
            alpha: value.alpha.into(),
            symbol: value.symbol.into(),
            modifier: value.modifier.into(),
        }
    }
}

impl From<keyset::profile::LegendGeomMap> for LegendGeometryMap {
    fn from(value: keyset::profile::LegendGeomMap) -> Self {
        Self {
            alpha: value.alpha.into(),
            symbol: value.symbol.into(),
            modifier: value.modifier.into(),
        }
    }
}

#[pyclass(module = "pykeyset.profile", get_all, set_all)]
#[derive(Debug, Clone, Copy)]
pub struct TopSurface {
    width: f32,
    height: f32,
    radius: f32,
    y_offset: f32,
}

impl From<TopSurface> for keyset::profile::TopSurface {
    fn from(value: TopSurface) -> Self {
        Self {
            size: Vector::new(Mm(value.width), Mm(value.height)).convert_into(),
            radius: Mm(value.radius).convert_into(),
            y_offset: Mm(value.y_offset).convert_into(),
        }
    }
}

impl From<keyset::profile::TopSurface> for TopSurface {
    fn from(value: keyset::profile::TopSurface) -> Self {
        Self {
            width: Mm::convert_from(value.size.x).get(),
            height: Mm::convert_from(value.size.y).get(),
            radius: Mm::convert_from(value.radius).get(),
            y_offset: Mm::convert_from(value.y_offset).get(),
        }
    }
}

#[pyclass(module = "pykeyset.profile", get_all, set_all)]
#[derive(Debug, Clone, Copy)]
pub struct BottomSurface {
    width: f32,
    height: f32,
    radius: f32,
}

impl From<BottomSurface> for keyset::profile::BottomSurface {
    fn from(value: BottomSurface) -> Self {
        Self {
            size: Vector::new(Mm(value.width), Mm(value.height)).convert_into(),
            radius: Mm(value.radius).convert_into(),
        }
    }
}

impl From<keyset::profile::BottomSurface> for BottomSurface {
    fn from(value: keyset::profile::BottomSurface) -> Self {
        Self {
            width: Mm::convert_from(value.size.x).get(),
            height: Mm::convert_from(value.size.y).get(),
            radius: Mm::convert_from(value.radius).get(),
        }
    }
}

#[pyclass(module = "pykeyset.profile", get_all, set_all)]
#[derive(Debug, Clone, Copy)]
pub struct Profile {
    r#type: ProfileTypeEnum,
    bottom: BottomSurface,
    top: TopSurface,
    legend_geometry_map: LegendGeometryMap,
    homing: Homing,
}

impl From<Profile> for keyset::Profile {
    fn from(value: Profile) -> Self {
        Self {
            typ: value.r#type.into(),
            bottom: value.bottom.into(),
            top: value.top.into(),
            legend_geom: value.legend_geometry_map.into(),
            homing: value.homing.into(),
            ..Default::default()
        }
    }
}

impl From<keyset::Profile> for Profile {
    fn from(value: keyset::Profile) -> Self {
        Self {
            r#type: value.typ.into(),
            bottom: value.bottom.into(),
            top: value.top.into(),
            legend_geometry_map: value.legend_geom.into(),
            homing: value.homing.into(),
        }
    }
}
