@_default: list

# list all available recipes
@list:
    just --list

# run the tests
@test: _venv
    #!/usr/bin/env -S bash -euo pipefail

    source .just-venv/bin/activate

    maturin develop --features=test
    pytest tests/

# run tests and compute test coverage; args are passed to `cargo llvm-cov report`
@coverage *args: _venv
    #!/usr/bin/env -S bash -euo pipefail

    source .just-venv/bin/activate
    export CARGO_TARGET_DIR=target/llvm-cov-target

    source <(cargo llvm-cov show-env --export-prefix --no-cfg-coverage)
    cargo llvm-cov clean --workspace

    # Maturin doesn't seem to fully respect the env var
    maturin develop --features=test --target-dir=$CARGO_TARGET_DIR
    pytest tests/

    cargo llvm-cov report {{args}}

@repl: _venv
    #!/usr/bin/env -S bash -euo pipefail

    source .just-venv/bin/activate

    maturin develop
    exec python3 -i -c "import pykeyset as ks; print('>>> import pykeyset as ks')"

# set up venv for testing
@_venv:
    #!/usr/bin/env -S bash -euo pipefail

    python3 -m venv .just-venv
    echo '*' > .just-venv/.gitignore

    source .just-venv/bin/activate

    pip install -U pip
    pip install -U maturin pytest
