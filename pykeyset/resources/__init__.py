# -*- coding: utf-8 -*-

import sys
from os import path

if sys.version_info[:2] >= (3, 7):
    import importlib.resources as ilr  # pragma: no cover
else:
    import importlib_resources as ilr  # pragma: no cover

import click.core
import typer.core

from . import fonts, icons, profiles

fonts = {
    path.splitext(res)[0]: ilr.path(fonts, res)
    for res in ilr.contents(fonts)
    if ilr.is_resource(fonts, res) and res.endswith(".xml")
}

icons = {
    path.splitext(res)[0]: ilr.path(icons, res)
    for res in ilr.contents(icons)
    if ilr.is_resource(icons, res) and res.endswith(".xml")
}

profiles = {
    path.splitext(res)[0]: ilr.path(profiles, res)
    for res in ilr.contents(profiles)
    if ilr.is_resource(profiles, res) and res.endswith(".toml")
}


def format_options(ctx: typer.Context, formatter: click.HelpFormatter):
    """Formats the help options for the available builtin resources"""

    with formatter.section("Built in resources"):
        formatter.write_text(f"Fonts: {', '.join(fonts.keys())}")
        formatter.write_text(f"Icons: {', '.join(icons.keys())}")
        formatter.write_text(f"Profiles: {', '.join(profiles.keys())}")
