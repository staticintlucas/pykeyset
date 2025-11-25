use pyo3::exceptions::PyValueError;
use pyo3::intern;
use pyo3::prelude::*;
use pyo3::sync::PyOnceLock;
use pyo3::types::PyBytes;
use pyo3::types::PyString;

fn io(py: Python<'_>) -> PyResult<&Bound<'_, PyModule>> {
    static IO: PyOnceLock<Py<PyModule>> = PyOnceLock::new();
    Ok(IO
        .get_or_try_init(py, || py.import(intern!(py, "io")).map(Bound::unbind))?
        .bind(py))
}

fn io_base(py: Python<'_>) -> PyResult<&Bound<'_, PyAny>> {
    static IO_BASE: PyOnceLock<Py<PyAny>> = PyOnceLock::new();
    Ok(IO_BASE
        .get_or_try_init(py, || {
            io(py)?.getattr(intern!(py, "IOBase")).map(Bound::unbind)
        })?
        .bind(py))
}

fn text_io_base(py: Python<'_>) -> PyResult<&Bound<'_, PyAny>> {
    static TEXT_IO_BASE: PyOnceLock<Py<PyAny>> = PyOnceLock::new();
    Ok(TEXT_IO_BASE
        .get_or_try_init(py, || {
            io(py)?
                .getattr(intern!(py, "TextIOBase"))
                .map(Bound::unbind)
        })?
        .bind(py))
}

pub trait Mode {
    fn assert(inner: Borrowed<'_, '_, PyAny>) -> PyResult<()>;
}

#[derive(Debug, Clone, Copy)]
pub struct ReadText;

impl Mode for ReadText {
    fn assert(inner: Borrowed<'_, '_, PyAny>) -> PyResult<()> {
        let py = inner.py();

        if inner.is_instance(io_base(py)?)? {
            if !inner
                .call_method0(intern!(py, "readable"))
                .is_ok_and(|r| r.extract::<bool>().unwrap_or(false))
            {
                return Err(PyValueError::new_err(
                    "expected a readable file-like object",
                ));
            }

            if !inner.is_instance(text_io_base(py)?)? {
                return Err(PyValueError::new_err("expected a text file-like object"));
            }
        } else {
            // Fall back to trying to read and checking the return type
            if !inner
                .call_method1(intern!(py, "read"), (0,))
                .is_ok_and(|r| r.is_instance_of::<PyString>())
            {
                return Err(PyValueError::new_err("expected a text file-like object"));
            }
        }

        Ok(())
    }
}

#[derive(Debug, Clone, Copy)]
pub struct ReadBinary;

impl Mode for ReadBinary {
    fn assert(inner: Borrowed<'_, '_, PyAny>) -> PyResult<()> {
        let py = inner.py();

        if inner.is_instance(io_base(py)?)? {
            if !inner
                .call_method0(intern!(py, "readable"))
                .is_ok_and(|r| r.extract::<bool>().unwrap_or(false))
            {
                return Err(PyValueError::new_err(
                    "expected a readable file-like object",
                ));
            }

            if inner.is_instance(text_io_base(py)?)? {
                return Err(PyValueError::new_err("expected a binary file-like object"));
            }
        } else {
            // Fall back to trying to read and checking the return type
            if !inner
                .call_method1(intern!(py, "read"), (0,))
                .is_ok_and(|r| r.is_instance_of::<PyBytes>())
            {
                return Err(PyValueError::new_err("expected a binary file-like object"));
            }
        }

        Ok(())
    }
}

#[derive(Debug, Clone, Copy)]
pub struct ReadAny;

impl Mode for ReadAny {
    fn assert(inner: Borrowed<'_, '_, PyAny>) -> PyResult<()> {
        let py = inner.py();

        if inner.is_instance(io_base(py)?)? {
            if !inner
                .call_method0(intern!(py, "readable"))
                .is_ok_and(|r| r.extract::<bool>().unwrap_or(false))
            {
                return Err(PyValueError::new_err(
                    "expected a readable file-like object",
                ));
            }
        } else {
            // Fall back to trying to read and checking the return type
            if !inner
                .call_method1(intern!(py, "read"), (0,))
                .is_ok_and(|r| r.is_instance_of::<PyBytes>() || r.is_instance_of::<PyString>())
            {
                return Err(PyValueError::new_err(
                    "expected a readable file-like object",
                ));
            }
        }

        Ok(())
    }
}

#[derive(Debug, Clone, Copy)]
pub struct WriteText;

impl Mode for WriteText {
    fn assert(inner: Borrowed<'_, '_, PyAny>) -> PyResult<()> {
        let py = inner.py();

        if inner.is_instance(io_base(py)?)? {
            if !inner
                .call_method0(intern!(py, "writable"))
                .is_ok_and(|r| r.extract::<bool>().unwrap_or(false))
            {
                return Err(PyValueError::new_err(
                    "expected a writeable file-like object",
                ));
            }

            if !inner.is_instance(text_io_base(py)?)? {
                return Err(PyValueError::new_err("expected a text file-like object"));
            }
        } else {
            // Fall back to trying to write and checking for errors
            if inner.call_method1(intern!(py, "write"), ("",)).is_err() {
                return Err(PyValueError::new_err("expected a text file-like object"));
            }
        }

        Ok(())
    }
}

#[derive(Debug, Clone, Copy)]
pub struct WriteBinary;

impl Mode for WriteBinary {
    fn assert(inner: Borrowed<'_, '_, PyAny>) -> PyResult<()> {
        let py = inner.py();

        if inner.is_instance(io_base(py)?)? {
            if !inner
                .call_method0(intern!(py, "writable"))
                .is_ok_and(|r| r.extract::<bool>().unwrap_or(false))
            {
                return Err(PyValueError::new_err(
                    "expected a writeable file-like object",
                ));
            }

            if inner.is_instance(text_io_base(py)?)? {
                return Err(PyValueError::new_err("expected a binary file-like object"));
            }
        } else {
            // Fall back to trying to write and checking for errors
            if inner
                .call_method1(intern!(py, "write"), ([0u8; 0],))
                .is_err()
            {
                return Err(PyValueError::new_err("expected a binary file-like object"));
            }
        }

        Ok(())
    }
}

#[derive(Debug, Clone, Copy)]
pub struct WriteAny;

impl Mode for WriteAny {
    fn assert(inner: Borrowed<'_, '_, PyAny>) -> PyResult<()> {
        let py = inner.py();

        if inner.is_instance(io_base(py)?)? {
            if !inner
                .call_method0(intern!(py, "writable"))
                .is_ok_and(|r| r.extract::<bool>().unwrap_or(false))
            {
                return Err(PyValueError::new_err(
                    "expected a writeable file-like object",
                ));
            }
        } else {
            // Fall back to trying to write and checking for errors
            if inner
                .call_method1(intern!(py, "write"), ([0u8; 0],))
                .is_err()
                && inner.call_method1(intern!(py, "write"), ("",)).is_err()
            {
                return Err(PyValueError::new_err(
                    "expected a writeable file-like object",
                ));
            }
        }

        Ok(())
    }
}

#[derive(Debug)]
#[repr(transparent)]
pub struct File<Mode> {
    inner: Py<PyAny>,
    _mode: std::marker::PhantomData<Mode>,
}

impl File<ReadText> {
    pub fn read_string(&self, py: Python<'_>) -> PyResult<String> {
        self.inner
            .bind(py)
            .call_method0(intern!(py, "read"))?
            .extract()
    }
}

impl File<ReadBinary> {
    pub fn read_bytes(&self, py: Python<'_>) -> PyResult<Vec<u8>> {
        self.inner
            .bind(py)
            .call_method0(intern!(py, "read"))?
            .extract()
    }
}

impl File<ReadAny> {
    pub fn read_bytes(&self, py: Python<'_>) -> PyResult<Vec<u8>> {
        let result = self.inner.bind(py).call_method0(intern!(py, "read"))?;

        match result.extract() {
            Ok(bytes) => Ok(bytes),
            Err(error) => {
                if let Ok(bytes) = result.extract().map(String::into_bytes) {
                    Ok(bytes)
                } else {
                    Err(error)
                }
            }
        }
    }

    pub fn read_string(&self, py: Python<'_>) -> PyResult<String> {
        let result = self.inner.bind(py).call_method0(intern!(py, "read"))?;

        match result.extract() {
            Ok(string) => Ok(string),
            Err(error) => {
                if let Ok(bytes) = result.extract() {
                    Ok(String::from_utf8(bytes)?)
                } else {
                    Err(error)
                }
            }
        }
    }
}

impl File<WriteText> {
    pub fn write_string(&self, py: Python<'_>, str: &str) -> PyResult<()> {
        self.inner
            .bind(py)
            .call_method1(intern!(py, "write"), (str,))?;
        Ok(())
    }
}

impl File<WriteBinary> {
    pub fn write_bytes(&self, py: Python<'_>, bytes: &[u8]) -> PyResult<()> {
        self.inner
            .bind(py)
            .call_method1(intern!(py, "write"), (bytes,))?;
        Ok(())
    }
}

impl File<WriteAny> {
    pub fn write_bytes(&self, py: Python<'_>, bytes: &[u8]) -> PyResult<()> {
        let inner = self.inner.bind(py);

        match inner.call_method1(intern!(py, "write"), (bytes,)) {
            Ok(_) => Ok(()),
            Err(error) => {
                if inner
                    .call_method1(intern!(py, "write"), (std::str::from_utf8(bytes)?,))
                    .is_ok()
                {
                    Ok(())
                } else {
                    Err(error)
                }
            }
        }
    }

    pub fn write_string(&self, py: Python<'_>, str: &str) -> PyResult<()> {
        let inner = self.inner.bind(py);

        match inner.call_method1(intern!(py, "write"), (str,)) {
            Ok(_) => Ok(()),
            Err(error) => {
                if inner
                    .call_method1(intern!(py, "write"), (str.as_bytes(),))
                    .is_ok()
                {
                    Ok(())
                } else {
                    Err(error)
                }
            }
        }
    }
}

impl<'a, 'py, M> FromPyObject<'a, 'py> for File<M>
where
    M: Mode,
{
    type Error = PyErr;

    fn extract(ob: Borrowed<'a, 'py, PyAny>) -> PyResult<Self> {
        M::assert(ob)?;

        Ok(File {
            inner: ob.as_unbound().clone_ref(ob.py()),
            _mode: std::marker::PhantomData,
        })
    }
}

#[cfg(feature = "test")]
pub mod test {
    use super::*;

    #[pyfunction]
    pub fn read_text_file_noop(_file: File<ReadText>) {}

    #[pyfunction]
    pub fn read_binary_file_noop(_file: File<ReadBinary>) {}

    #[pyfunction]
    pub fn read_any_file_noop(_file: File<ReadAny>) {}

    #[pyfunction]
    pub fn write_text_file_noop(_file: File<WriteText>) {}

    #[pyfunction]
    pub fn write_binary_file_noop(_file: File<WriteBinary>) {}

    #[pyfunction]
    pub fn write_any_file_noop(_file: File<WriteAny>) {}
}
