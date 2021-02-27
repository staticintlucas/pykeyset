# -*- coding: utf-8 -*-

import sys
from os import path
from pathlib import Path
from typing import Optional

if sys.version_info >= (3, 7):
    import importlib.resources as ilr  # pragma: no cover
else:
    import importlib_resources as ilr  # pragma: no cover

import click
import typer

from . import fonts as _fonts
from . import icons as _icons
from . import profiles as _profiles


class ResourcePath:
    """Yields the path to a resource (just like importlib.resources.path), but can be used
    multiple times"""

    def __init__(self, package: ilr.Package, resource: ilr.Resource) -> None:
        self.package = package
        self.resource = resource
        self.context = None

    def __enter__(self, *args, **kwargs) -> Path:
        assert self.context is None
        self.context = ilr.path(self.package, self.resource)
        return self.context.__enter__(*args, **kwargs)

    def __exit__(self, *args, **kwargs) -> Optional[bool]:
        try:
            return self.context.__exit__(*args, **kwargs)
        finally:
            self.context = None


fonts = {
    path.splitext(res)[0]: ResourcePath(_fonts, res)
    for res in ilr.contents(_fonts)
    if ilr.is_resource(_fonts, res) and res.endswith(".xml")
}

icons = {
    path.splitext(res)[0]: ResourcePath(_icons, res)
    for res in ilr.contents(_icons)
    if ilr.is_resource(_icons, res) and res.endswith(".xml")
}

profiles = {
    path.splitext(res)[0]: ResourcePath(_profiles, res)
    for res in ilr.contents(_profiles)
    if ilr.is_resource(_profiles, res) and res.endswith(".toml")
}


def format_options(ctx: typer.Context, formatter: click.HelpFormatter):
    """Formats the help options for the available builtin resources"""

    with formatter.section("Built in resources"):
        formatter.write_text(f"Fonts: {', '.join(fonts.keys())}")
        formatter.write_text(f"Icons: {', '.join(icons.keys())}")
        formatter.write_text(f"Profiles: {', '.join(profiles.keys())}")
