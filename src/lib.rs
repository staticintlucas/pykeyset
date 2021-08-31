use pyo3::prelude::*;
use konst::primitive::parse_u8;
use konst::result::unwrap_ctx;

#[pymodule]
fn pykeyset_rust(_py: Python, m: &PyModule) -> PyResult<()> {
    #[pyfn(m)]
    pub fn version() -> (u8, u8, u8) {
        (
            unwrap_ctx!(parse_u8(env!("CARGO_PKG_VERSION_MAJOR"))),
            unwrap_ctx!(parse_u8(env!("CARGO_PKG_VERSION_MINOR"))),
            unwrap_ctx!(parse_u8(env!("CARGO_PKG_VERSION_PATCH"))),
        )
    }

    Ok(())
}
