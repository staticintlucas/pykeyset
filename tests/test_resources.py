# -*- coding: utf-8 -*-

import re
from pathlib import Path

import click.core
import pytest
import typer

from pykeyset import resources


@pytest.mark.parametrize(
    "res, ext",
    [
        ("fonts", "xml"),
        ("icons", "xml"),
        ("profiles", "toml"),
    ],
)
def test_resource(res, ext):

    path = Path(resources.__file__).parent / res
    items = [p.stem for p in path.glob(f"*.{ext}")]

    assert items == list(getattr(resources, res))


def test_format_options():

    expected = re.sub(
        r"\s+",
        " ",
        f"""Built in resources:
        Fonts: {', '.join(resources.fonts)}
        Icons: {', '.join(resources.icons)}
        Profiles: {', '.join(resources.profiles)}
        """,
    )

    cmdclass = click.Command("test")
    ctx = typer.Context(cmdclass)
    fmt = click.HelpFormatter()

    resources.format_options(ctx, fmt)

    assert re.sub(r"\s+", " ", fmt.getvalue()) == expected


def test_acquire_resource():

    with resources.fonts["cherry"]:
        pass

    # Test it twice to ensure a resource can be used more than once. Previously reloading the same
    # resource failed because a resourcemangager cannot be used multiple times.
    with resources.fonts["cherry"]:
        pass
