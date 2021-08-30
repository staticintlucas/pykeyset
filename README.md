# pykeyset

A Python-based tool to create pretty keyset layout diagrams using correct fonts and icons.

[![Build Status](https://img.shields.io/github/workflow/status/staticintlucas/pykeyset/Build?style=flat-square)][actions]
[![Test Status](https://img.shields.io/github/workflow/status/staticintlucas/pykeyset/Tests?label=tests&style=flat-square)][actions]
[![Test coverage](https://img.shields.io/codecov/c/github/staticintlucas/pykeyset?style=flat-square)][coverage]
[![Python Version](https://img.shields.io/pypi/pyversions/pykeyset?style=flat-square)][pypi]
[![Code style](https://img.shields.io/badge/code_style-black-black?style=flat-square)][black]
[![PyPI](https://img.shields.io/pypi/v/pykeyset?style=flat-square)][pypi]
[![PyPI downloads](https://img.shields.io/pypi/dm/pykeyset?style=flat-square)][pypi]
[![License](https://img.shields.io/github/license/staticintlucas/pykeyset?style=flat-square)][licence]

## Warning

**The source for the original pure-Python implementation is available in the v0.0.x branch.
The main branch is currently a work-in-progress port to using the [keyset-rs] backend.**

**This project is currently in the early stages of development.
If you do find any bugs, please report them on the [GitHub repo][pykeyset].
In future I hope to stabilise this project, add more extensive support for different profiles, fonts, file formats, etc; and have a more extensive API.**

Feel free to help this project improve by opening bug reports, feature requests, etc; or contributing directly to the code by opening a pull request.

## Example output

![example.svg](example/example.png)

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

    maturin build

Additionally, for release builds the following platform-specific flags are added:

* Linux:

      maturin build --manylinux 2014 --release

* MacOs:

      maturin build --universal2 --release

* Windows:

      maturin build --release

## Contributing

`pykeyset` uses [Black] and [isort] for formatting, and all code must pass [Flake8]'s checks.
These are checked by GitHub on all pull requests.
To run these tools automatically when committing, install the [pre-commit] hook in [`.pre-commit-config.yaml`].

## Credits

The builtin `cherry` font is based on [Open Cherry] by Dakota Felder.

[pykeyset]: https://github.com/staticintlucas/pykeyset
[actions]: https://github.com/staticintlucas/pykeyset/actions
[coverage]: https://codecov.io/gh/staticintlucas/pykeyset
[licence]: LICENCE
[pypi]: https://pypi.org/project/pykeyset/
[black]: https://github.com/psf/black
[keyset-rs]: https://github.com/staticintlucas/keyset-rs
[isort]: https://pycqa.github.io/isort/
[maturin]: https://github.com/PyO3/maturin/
[open cherry]: https://github.com/dakotafelder/open-cherry
[flake8]: https://flake8.pycqa.org/en/latest/
[pre-commit]: https://pre-commit.com/
[`.pre-commit-config.yaml`]: .pre-commit-config.yaml
