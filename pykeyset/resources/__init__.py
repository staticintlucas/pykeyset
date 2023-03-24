from __future__ import annotations

import sys
from os import path
from pathlib import Path

# We use the new API introduced in Python 3.9, otherwise use the backport
if sys.version_info >= (3, 9):
    import importlib.resources as ilr
else:
    import importlib_resources as ilr

import click
import typer


class ResourcePath:
    """Yields the path to a resource (just like importlib.resources.path), but can be used
    multiple times"""

    def __init__(self, package: ilr.Package, resource: ilr.Resource) -> None:
        self.package = package
        self.resource = resource
        self.context = None

    def __enter__(self, *args, **kwargs) -> Path:
        assert self.context is None
        self.context = ilr.path(self.package, self.resource)  # type: ignore
        return self.context.__enter__(*args, **kwargs)  # type: ignore

    def __exit__(self, *args, **kwargs) -> bool | None:
        try:
            return self.context.__exit__(*args, **kwargs)  # type: ignore
        finally:
            self.context = None


fonts = {
    path.splitext(res.name)[0]: res
    for res in (ilr.files(__package__) / "fonts").iterdir()
    if res.is_file() and res.name.endswith(".ttf")
}

icons = {
    path.splitext(res.name)[0]: res
    for res in (ilr.files(__package__) / "icons").iterdir()
    if res.is_file() and res.name.endswith(".xml")
}

profiles = {
    path.splitext(res.name)[0]: res
    for res in (ilr.files(__package__) / "profiles").iterdir()
    if res.is_file() and res.name.endswith(".toml")
}


def format_options(ctx: typer.Context, formatter: click.HelpFormatter):
    """Formats the help options for the available builtin resources"""

    with formatter.section("Built in resources"):
        formatter.write_text(f"Fonts: {', '.join(fonts.keys())}")
        formatter.write_text(f"Icons: {', '.join(icons.keys())}")
        formatter.write_text(f"Profiles: {', '.join(profiles.keys())}")
