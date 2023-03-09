use std::collections::HashMap;
use std::sync::Mutex;

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyDict;

use super::Verbosity;

pub fn module<'p>(py: Python<'p>) -> PyResult<&'p PyModule> {
    let utils = PyModule::new(py, "utils.config")?;

    utils.add_function(wrap_pyfunction!(config, utils)?)?;
    utils.add_function(wrap_pyfunction!(set_config, utils)?)?;
    utils.add_function(wrap_pyfunction!(reset_config, utils)?)?;

    Ok(utils)
}

#[pyclass(module = "pykeyset.utils.config", get_all)]
#[derive(Debug, Clone)]
struct Config {
    show_align: bool,
    dpi: isize,
    profile: bool,
    color: Option<bool>,
    verbosity: Verbosity,
    raise_warnings: bool,
    is_script: bool,
}

static CONFIG: Mutex<Config> = Mutex::new(default_config());

const fn default_config() -> Config {
    Config {
        show_align: false,
        dpi: 96,
        profile: false,
        color: None,
        verbosity: Verbosity::NONE,
        raise_warnings: false,
        is_script: false,
    }
}

/// Returns the global configuration object
#[pyfunction]
fn config() -> Config {
    CONFIG.lock().unwrap().clone()
}

/// Set the global configuration object
#[pyfunction]
#[pyo3(signature = (**kwargs))]
fn set_config(kwargs: Option<&PyDict>) -> PyResult<()> {
    fn pop_or<T, 'v>(map: &mut HashMap<String, &'v PyAny>, key: &str, default: T) -> PyResult<T>
    where
        T: FromPyObject<'v> + Copy,
    {
        map.remove(key)
            .map_or(Ok(default), |v| v.extract().map_err(PyErr::from))
    }

    if let Some(kwargs) = kwargs {
        let mut kwargs: HashMap<String, &PyAny> = kwargs.extract()?;

        let mut config = CONFIG.lock().unwrap();

        config.show_align = pop_or(&mut kwargs, "show_align", config.show_align)?;
        config.dpi = pop_or(&mut kwargs, "dpi", config.dpi)?;
        config.profile = pop_or(&mut kwargs, "profile", config.profile)?;
        config.color = pop_or(&mut kwargs, "color", config.color)?;
        config.verbosity = pop_or(&mut kwargs, "verbosity", config.verbosity)?;
        config.raise_warnings = pop_or(&mut kwargs, "raise_warnings", config.raise_warnings)?;
        config.is_script = pop_or(&mut kwargs, "is_script", config.is_script)?;

        if kwargs.len() > 0 {
            return Err(PyValueError::new_err(format!(
                "unknown config option {} in call to set_config",
                kwargs.iter().next().unwrap().0 // Unwrap is ok since we checked len > 0
            )));
        }
    }

    Ok(())
}

/// Reset the global configuration object to it's default values
#[pyfunction]
fn reset_config() {
    *CONFIG.lock().unwrap() = default_config();
}
