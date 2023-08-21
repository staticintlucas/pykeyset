# pykeyset &emsp; [![Build Status]][actions]&thinsp;[![PyPI Version]][pypi]

A Python-based tool to create pretty keyset layout diagrams using correct fonts and icons.

<!-- TODO add coverage badge -->
[build status]: https://img.shields.io/github/actions/workflow/status/staticintlucas/pykeyset/ci.yml?branch=main&style=flat-square
[pypi version]: https://img.shields.io/pypi/v/pykeyset?style=flat-square
[actions]: https://github.com/staticintlucas/pykeyset/actions
[pypi]: https://pypi.org/project/pykeyset/

## Warning

**This project is currently in the early stages of development.
If you do find any bugs, please report them on the [GitHub repo][pykeyset].
In future I hope to stabilise this project, add more extensive support for different profiles, fonts, file formats, etc; and have a more extensive API.**

Feel free to help this project improve by opening bug reports, feature requests, etc; or contributing directly to the code by opening a pull request.

[pykeyset]: https://github.com/staticintlucas/pykeyset

## Example output

<!-- Use absolute links because relative won't work properly in PyPI -->
![example.svg](https://raw.githubusercontent.com/staticintlucas/pykeyset/main/example/example.png)

## Python API

Currently you *can* use `pykeyset` directly as a Python module, but as it is still in early development the API will probably change *a lot* until a 0.5 release.
After that there will be a relatively stable API, so you don't need to mess around with *.cmdlist* files if you're familiar with Python.

## Installation

`pykeyset` is available on [PyPI]. To install with `pip` run:

    pip install pykeyset

Or to install the latest source directly from GitHub, run:

    git clone https://github.com/staticintlucas/pykeyset.git pykeyset
    cd pykeyset
    pip install .

This project uses [Maturin] as its build system.
To install this package locally for development, run:

    maturin develop

To build the source distribution and wheel run:

    maturin build --release

Additionally, Linux releases should be compiled with `--manylinux 2014`

[pypi]: https://pypi.org/project/pykeyset/
[maturin]: https://github.com/PyO3/maturin

## Contributing

`pykeyset` uses [Black] and [isort] for formatting, and all code must pass [Flake8]'s checks.
These are checked by GitHub on all pull requests.
To run these tools automatically when committing, install the [pre-commit] hook in *[.pre-commit-config.yaml](.pre-commit-config.yaml)*.

[black]: https://github.com/psf/black
[isort]: https://pycqa.github.io/isort/
[flake8]: https://flake8.pycqa.org/en/latest/
[pre-commit]: https://pre-commit.com/

## Licence

This project is licensed under either of

* Apache License, Version 2.0 ([LICENCE-APACHE](LICENCE-APACHE) or [http://www.apache.org/licenses/LICENSE-2.0][apache-licence])
* MIT license ([LICENCE-MIT](LICENCE-MIT) or [http://opensource.org/licenses/MIT][mit-licence])

at your option.

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in
this project by you, as defined in the Apache-2.0 license, shall be dual licensed as above, without
any additional terms or conditions.

[apache-licence]: http://www.apache.org/licenses/LICENSE-2.0
[mit-licence]: http://opensource.org/licenses/MIT
