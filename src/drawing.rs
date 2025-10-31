use std::ffi::CString;
use std::io::Write;
use std::path::PathBuf;

use keyset::drawing::Stencil;
use keyset::geom::{ConvertFrom as _, ConvertInto as _, Mm, Unit as _};
use pyo3::exceptions::{PyUserWarning, PyValueError};
use pyo3::prelude::*;

use crate::font::Font;
use crate::layout::Key;
use crate::profile::Profile;
use crate::utils;

#[derive(Debug)]
pub enum PathOrFile<M: utils::Mode> {
    Path(PathBuf),
    File(utils::File<M>),
}

impl<M> FromPyObject<'_> for PathOrFile<M>
where
    M: utils::Mode,
{
    fn extract_bound(ob: &Bound<'_, PyAny>) -> PyResult<Self> {
        if let Ok(path) = ob.extract::<PathBuf>() {
            Ok(PathOrFile::Path(path))
        } else if let Ok(file) = ob.extract::<utils::File<M>>() {
            Ok(PathOrFile::File(file))
        } else {
            Err(PyErr::new::<PyValueError, _>(
                "expected a path or a file-like object",
            ))
        }
    }
}

#[pyclass(module = "pykeyset.drawing")]
pub struct Drawing(keyset::drawing::Drawing);

#[pymethods]
impl Drawing {
    #[new]
    #[pyo3(signature = (
        /,
        keys,
        *,
        profile = Stencil::default().profile.into(),
        font = Stencil::default().font.into(),
        scale = Stencil::default().scale,
        outline_width = Mm::convert_from(Stencil::default().outline_width).get(),
        show_keys = Stencil::default().show_keys,
        show_margin = Stencil::default().show_margin,
    ))]
    #[allow(clippy::too_many_arguments)]
    fn new(
        py: Python,
        keys: Vec<Key>,
        profile: Profile,
        font: Font,
        scale: f32,
        outline_width: f32,
        show_keys: bool,
        show_margin: bool,
    ) -> PyResult<Self> {
        let stencil = Stencil {
            profile: profile.into(),
            font: font.into(),
            scale,
            outline_width: Mm::new(outline_width).convert_into(),
            show_keys,
            show_margin,
            ..Default::default()
        };
        let keys: Vec<_> = keys.into_iter().map(Into::into).collect();

        match stencil.draw(&keys) {
            Ok(keyset::drawing::WithWarnings { value, warnings }) => {
                let user_warning = py.get_type::<PyUserWarning>();
                warnings.into_iter().try_for_each(|warning| {
                    PyErr::warn(
                        py,
                        &user_warning,
                        &CString::new(warning.to_string())
                            .expect("Strings cannot contain nul bytes"),
                        0,
                    )
                })?;
                Ok(Self(value))
            }
            Err(err) => Err(PyValueError::new_err(format!("unable to draw keys: {err}"))),
        }
    }

    #[pyo3(signature = (path_or_file = None, /))]
    pub fn to_svg(
        &self,
        py: Python,
        path_or_file: Option<PathOrFile<utils::WriteAny>>,
    ) -> PyResult<Option<String>> {
        let result = self.0.to_svg();

        match path_or_file {
            None => Ok(Some(result)),
            Some(PathOrFile::Path(path)) => {
                let mut file = std::fs::File::create(path)?;
                file.write_all(result.as_bytes())?;
                Ok(None)
            }
            Some(PathOrFile::File(file)) => {
                file.write_string(py, &result)?;
                Ok(None)
            }
        }
    }

    #[pyo3(signature = (path_or_file = None, /, *, ppi = 96.0))]
    pub fn to_png(
        &self,
        py: Python,
        path_or_file: Option<PathOrFile<utils::WriteBinary>>,
        ppi: f32,
    ) -> PyResult<Option<Vec<u8>>> {
        let result = self
            .0
            .to_png(ppi)
            .map_err(|err| PyValueError::new_err(err.to_string()))?;

        match path_or_file {
            None => Ok(Some(result)),
            Some(PathOrFile::Path(path)) => {
                let mut file = std::fs::File::create(path)?;
                file.write_all(&result)?;
                Ok(None)
            }
            Some(PathOrFile::File(file)) => {
                file.write_bytes(py, &result)?;
                Ok(None)
            }
        }
    }

    #[pyo3(signature = (path_or_file = None, /))]
    pub fn to_pdf(
        &self,
        py: Python,
        path_or_file: Option<PathOrFile<utils::WriteBinary>>,
    ) -> PyResult<Option<Vec<u8>>> {
        let result = self.0.to_pdf();

        match path_or_file {
            None => Ok(Some(result)),
            Some(PathOrFile::Path(path)) => {
                let mut file = std::fs::File::create(path)?;
                file.write_all(&result)?;
                Ok(None)
            }
            Some(PathOrFile::File(file)) => {
                file.write_bytes(py, &result)?;
                Ok(None)
            }
        }
    }

    #[pyo3(signature = (path_or_file = None, /))]
    pub fn to_ai(
        &self,
        py: Python,
        path_or_file: Option<PathOrFile<utils::WriteBinary>>,
    ) -> PyResult<Option<Vec<u8>>> {
        let result = self.0.to_ai();

        match path_or_file {
            None => Ok(Some(result)),
            Some(PathOrFile::Path(path)) => {
                let mut file = std::fs::File::create(path)?;
                file.write_all(&result)?;
                Ok(None)
            }
            Some(PathOrFile::File(file)) => {
                file.write_bytes(py, &result)?;
                Ok(None)
            }
        }
    }
}
