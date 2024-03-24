use std::error::Error;
use std::io::Write;
use std::path::{Path, PathBuf};
use std::{env, fs};

fn main() -> Result<(), Box<dyn Error>> {
    let file = Path::new(&env::var("OUT_DIR")?).join("built.rs");
    let manifest_dir = PathBuf::from(env::var("CARGO_MANIFEST_DIR")?);

    // Write build.rs
    built::write_built_file_with_opts(Some(&manifest_dir), &file)?;

    // Check that pyo3's version matches pyo3-build-config's version (else it gives bad results)
    check_pyo3_vers(&manifest_dir)?;

    // Add pyo3 info to build.rs
    write_pyo3_file(&file)?;

    Ok(())
}

fn check_pyo3_vers(manifest_dir: &Path) -> Result<(), Box<dyn Error>> {
    let lockfile = cargo_lock::Lockfile::load(manifest_dir.join("Cargo.lock"))?;

    let deps = lockfile.packages;

    let pyo3_ver = deps
        .iter()
        .find(|p| p.name.as_str() == "pyo3")
        .expect("pyo3 not found in Cargo.lock")
        .version
        .clone();

    for dep in deps {
        if dep.name.as_str().starts_with("pyo3") {
            assert_eq!(
                dep.version, pyo3_ver,
                "mismatching {} version {}, expected {}",
                dep.name, dep.version, pyo3_ver
            );
        }
    }

    Ok(())
}

fn write_pyo3_file(file: &Path) -> Result<(), Box<dyn Error>> {
    let str = fs::read_to_string(file)?;

    let (start, end) = str.rsplit_once(";\n").expect("failed to parse built file");

    let mut file = fs::OpenOptions::new()
        .write(true)
        .truncate(true)
        .open(file)?;
    writeln!(file, "{start};")?;

    let &pyo3_build_config::InterpreterConfig {
        implementation,
        version,
        shared,
        abi3,
        ..
    } = pyo3_build_config::get();

    writeln!(file, "#[doc=r#\"The Python implementation flavor\"#]")?;
    writeln!(file, "#[allow(dead_code)]")?;
    writeln!(file, "pub const PYO3_PY_IMPL: &str = \"{implementation}\";")?;
    writeln!(file, "#[doc=r#\"Python `X.Y` version. e.g. `3.9`.\"#]")?;
    writeln!(file, "#[allow(dead_code)]")?;
    writeln!(file, "pub const PYO3_PY_VER: &str = \"{version}\";")?;
    writeln!(file, "#[doc=r#\"Whether link library is shared.\"#]")?;
    writeln!(file, "#[allow(dead_code)]")?;
    writeln!(file, "pub const PYO3_PY_SHARED: bool = {shared};")?;
    writeln!(
        file,
        "#[doc=r#\"Whether linking against the stable/limited Python 3 API.\"#]"
    )?;
    writeln!(file, "#[allow(dead_code)]")?;
    writeln!(file, "pub const PYO3_PY_ABI3: bool = {abi3};")?;

    write!(file, "{end}")?;

    Ok(())
}
