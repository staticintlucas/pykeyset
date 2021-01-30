# -*- coding: utf-8 -*-

import sys
from os import path
from pathlib import Path
from typing import ContextManager

if sys.version_info[:2] >= (3, 7):
    import importlib.resources as ilr  # pragma: no cover
else:
    import importlib_resources as ilr  # pragma: no cover

import click.core
import typer.core

from . import fonts, icons, profiles


class ResourcePath:
    """Yields the path to a resource (just like importlib.resources.path), but can be used
    multiple times"""

    def __init__(self, package: ilr.Package, resource: ilr.Resource) -> ContextManager[Path]:
        self.package = package
        self.resource = resource
        self.context = None

    def __enter__(self, *args, **kwargs):
        assert self.context is None
        self.context = ilr.path(self.package, self.resource)
        return self.context.__enter__(*args, **kwargs)

    def __exit__(self, *args, **kwargs):
        try:
            return self.context.__exit__(*args, **kwargs)
        finally:
            self.context = None


fonts = {
    path.splitext(res)[0]: ResourcePath(fonts, res)
    for res in ilr.contents(fonts)
    if ilr.is_resource(fonts, res) and res.endswith(".xml")
}

icons = {
    path.splitext(res)[0]: ResourcePath(icons, res)
    for res in ilr.contents(icons)
    if ilr.is_resource(icons, res) and res.endswith(".xml")
}

profiles = {
    path.splitext(res)[0]: ResourcePath(profiles, res)
    for res in ilr.contents(profiles)
    if ilr.is_resource(profiles, res) and res.endswith(".toml")
}


def format_options(ctx: typer.Context, formatter: click.HelpFormatter):
    """Formats the help options for the available builtin resources"""

    with formatter.section("Built in resources"):
        formatter.write_text(f"Fonts: {', '.join(fonts.keys())}")
        formatter.write_text(f"Icons: {', '.join(icons.keys())}")
        formatter.write_text(f"Profiles: {', '.join(profiles.keys())}")
