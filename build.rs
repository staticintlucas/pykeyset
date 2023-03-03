use std::env;
use std::path::Path;

fn main() {
    let mut opts = built::Options::default();
    opts.set_dependencies(true);

    built::write_built_file_with_opts(
        &opts,
        env::var("CARGO_MANIFEST_DIR").unwrap().as_ref(),
        Path::new(&env::var("OUT_DIR").unwrap())
            .join("built.rs")
            .as_path(),
    )
    .expect("built failed!");
}
