use std::env;
use std::error::Error;
use std::fs::File;
use std::io::Write;
use std::path::PathBuf;

use cargo_lock::Lockfile;
use indoc::writedoc;
use pyo3_build_config::{BuildFlag, BuildFlags, InterpreterConfig};
use shadow_rs::{SdResult, Shadow, ShadowBuilder, ShadowError, CARGO_CLIPPY_ALLOW_ALL};

macro_rules! write_vars {
    ($file:expr, $(#[$($attrs:tt)*])* $name:ident: & $($lt:lifetime)? str = $val:expr; $($rest:tt)*) => {
        write_vars!(@inner $file, $(#[$($attrs)*])* $name: &'static str = format!("{:?}", $val.to_string()));
        write_vars!($file, $($rest)*);
    };
    ($file:expr, $(#[$($attrs:tt)*])* $name:ident: $typ:ty = $val:expr; $($rest:tt)*) => {
        write_vars!(@inner $file, $(#[$($attrs)*])* $name: $typ = $val);
        write_vars!($file, $($rest)*);
    };
    ($file:expr,) => {};
    (@inner $file:expr, $(#[$($attrs:tt)*])* $name:ident: $typ:ty = $val:expr) => {
        match (stringify!($(#[$($attrs)*])*), stringify!($name), stringify!($typ), $val) {
            (attrs, name, typ, val) => writedoc!($file, r#"
                {attrs}
                #[allow(dead_code)]
                {CARGO_CLIPPY_ALLOW_ALL}
                pub const {name}: {typ} = {val};

            "#)?
        }
    };
}

fn pyo3_consts(mut file: &File, _shadow: &Shadow) -> SdResult<()> {
    let &InterpreterConfig {
        implementation,
        version,
        shared,
        abi3,
        build_flags: BuildFlags(ref build_flags),
        ..
    } = pyo3_build_config::get();

    write_vars! {
        file,

        /// Python implementation
        PYO3_PY_IMPL: &str = implementation.to_string().to_lowercase();

        /// Python version. e.g. 3.9
        PYO3_PY_VER: &str = version;

        /// Whether link library is shared
        PYO3_SHARED: bool = shared;

        /// Whether we're compiled against the stable ABI/limited API
        PYO3_ABI3: bool = abi3;

        /// Whether the GIL is disabled
        PYO3_NO_GIL: bool = build_flags.contains(&BuildFlag::Py_GIL_DISABLED);
    }

    Ok(())
}

fn keyset_consts(mut file: &File, shadow: &Shadow) -> SdResult<()> {
    // TODO use try_map when stabilized
    let [major, minor, patch, pre] = [
        shadow_rs::PKG_VERSION_MAJOR,
        shadow_rs::PKG_VERSION_MINOR,
        shadow_rs::PKG_VERSION_PATCH,
        shadow_rs::PKG_VERSION_PRE,
    ]
    .map(|key| {
        shadow
            .map
            .get(key)
            .ok_or(ShadowError::String(format!("{key} not set")))
    });
    let [major, minor, patch, pre] = [&major?.v, &minor?.v, &patch?.v, &pre?.v];

    let (releaselevel, serial) = if pre.is_empty() {
        ("final", "0")
    } else if let Some(tuple) = pre.split_once('.') {
        tuple
    } else {
        pre.split_at(
            pre.find(char::is_numeric)
                .ok_or(ShadowError::String(format!(
                    "Invalid PKG_VERSION_PRE value {pre}"
                )))?,
        )
    };
    let releaselevelenum = match releaselevel {
        "alpha" => "ReleaseLevel::Alpha",
        "beta" => "ReleaseLevel::Beta",
        "candidate" => "ReleaseLevel::Candidate",
        "final" => "ReleaseLevel::Final",
        _ => {
            return Err(ShadowError::String(format!(
                "Invalid PKG_VERSION_PRE value {pre}"
            )))
        }
    };

    let [hash, date, clean] = [
        shadow_rs::SHORT_COMMIT,
        shadow_rs::COMMIT_DATE,
        shadow_rs::GIT_CLEAN,
    ]
    .map(|key| {
        shadow
            .map
            .get(key)
            .ok_or(ShadowError::String(format!("{key} not set")))
    });
    let [hash, date, clean] = [&hash?.v, &date?.v, &clean?.v];

    let commit = if hash.is_empty() {
        "non-git source tree".to_string()
    } else {
        let date = date
            .split_once(' ')
            .ok_or_else(|| ShadowError::String(format!("Invalid date format {date}")))?
            .0;
        let dirty = if clean
            .parse::<bool>()
            .map_err(|e| ShadowError::String(e.to_string()))?
        {
            ""
        } else {
            " (dirty)"
        };
        format!("{hash} {date}{dirty}")
    };

    // Release Level similar to what Python uses
    writedoc!(
        file,
        "
            #[allow(dead_code)]
            {CARGO_CLIPPY_ALLOW_ALL}
            pub enum ReleaseLevel {{
                Alpha,
                Beta,
                Candidate,
                Final,
            }}
        "
    )?;

    write_vars! {
        file,

        /// The package's major version
        PKG_VERSION_MAJOR_INT: u8 = major;

        /// The package's minor version
        PKG_VERSION_MINOR_INT: u8 = minor;

        /// The package's patch version
        PKG_VERSION_PATCH_INT: u8 = patch;

        /// The package's (pre)release level
        PKG_VERSION_RELEASELEVEL: ReleaseLevel = releaselevelenum;

        /// The package's prerelease serial
        PKG_VERSION_SERIAL: u8 = serial;

        /// The package's version string in a format Python likes
        PKG_VERSION_STRING: &str = (if releaselevel == "final" {
            format!("{major}.{minor}.{patch}")
        } else {
            format!("{major}.{minor}.{patch}-{releaselevel}{serial}")
        });

        /// Package commit hash/date
        PKG_COMMIT: &str = commit;
    }

    let cargo_lock = PathBuf::from(env::var("CARGO_MANIFEST_DIR")?).join("Cargo.lock");
    let lockfile = Lockfile::load(cargo_lock).map_err(ShadowError::new)?;

    let pyo3_ver = lockfile
        .packages
        .iter()
        .find(|p| p.name.as_str() == "pyo3")
        .expect("pyo3 not found in Cargo.lock")
        .version
        .clone();

    let keyset_rs_ver = lockfile
        .packages
        .iter()
        .find(|p| p.name.as_str() == "keyset")
        .expect("keyset not found in Cargo.lock")
        .version
        .clone();

    write_vars! {
        file,

        /// The PyO3 version used
        DEP_PYO3_VER: &str = pyo3_ver;

        /// The keyset-rs version used
        DEP_KEYSET_RS_VER: &str = keyset_rs_ver;
    }

    Ok(())
}

fn misc_consts(mut file: &File, _shadow: &Shadow) -> SdResult<()> {
    write_vars! {
        file,

        /// The build host system triple
        HOST: &str = env::var("HOST")?;

        /// "release" for release builds, "debug" for other builds. Based on if
        /// the profile inherits from the dev or release profile
        PROFILE: &str = env::var("PROFILE")?;

        /// The optimization level
        OPT_LEVEL: &str = env::var("OPT_LEVEL")?;

        /// Whether debug assertions are enabled
        DEBUG: &str = env::var("DEBUG")?;

        /// Target endianness
        BUILD_TARGET_ENDIAN: &str = env::var("CARGO_CFG_TARGET_ENDIAN")?;

        /// Target operating system
        BUILD_TARGET_OS: &str = env::var("CARGO_CFG_TARGET_OS")?;

        /// Target family
        BUILD_TARGET_FAMILY: &str = env::var("CARGO_CFG_TARGET_FAMILY")?;

        /// Target environment ABI
        BUILD_TARGET_ENV: &str = env::var("CARGO_CFG_TARGET_ENV")?;
    }

    Ok(())
}

fn shadow_hook(file: &File, shadow: &Shadow) -> SdResult<()> {
    pyo3_consts(file, shadow)?;
    keyset_consts(file, shadow)?;
    misc_consts(file, shadow)?;
    Ok(())
}

fn check_pyo3_vers() -> Result<(), Box<dyn Error>> {
    let cargo_lock = PathBuf::from(env::var("CARGO_MANIFEST_DIR")?).join("Cargo.lock");
    let lockfile = Lockfile::load(cargo_lock)?;

    let pyo3_ver = lockfile
        .packages
        .iter()
        .find(|p| p.name.as_str() == "pyo3")
        .expect("pyo3 not found in Cargo.lock")
        .version
        .clone();

    for dep in lockfile.packages {
        if dep.name.as_str().starts_with("pyo3") {
            assert_eq!(
                dep.version, pyo3_ver,
                "mismatching {} version {}, expected {} to match pyo3",
                dep.name, dep.version, pyo3_ver
            );
        }
    }

    Ok(())
}

fn main() -> Result<(), Box<dyn Error>> {
    // Ensure pyo3-build-config's (and other pyo3-* crates) version matches
    // pyo3, otherwise it gives bad results
    check_pyo3_vers()?;

    // Write shadow.rs
    let shadow = ShadowBuilder::builder()
        .deny_const([shadow_rs::CARGO_TREE, shadow_rs::CARGO_METADATA].into())
        .build()?;
    shadow.hook(|file| shadow_hook(file, &shadow))?;

    Ok(())
}
