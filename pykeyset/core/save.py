# -*- coding: utf-8 -*-

from xml.etree import ElementTree as et

from ..utils.logging import error, format_filename, warning


def as_svg(ctx, filename):
    """export the generated graphic as an SVG file"""

    if ctx.layout is None:
        error(ValueError("no layout has been generated"), file=ctx.name)

    try:
        et.ElementTree(ctx.layout.root).write(filename)
    except IOError as e:
        error(
            IOError(f"cannot write to file {format_filename(filename)}: {e.strerror}"),
            file=ctx.name,
        )


def as_png(ctx, filename):
    """export the generated graphic as a PNG file"""

    if ctx.layout is None:
        error(ValueError("no layout has been generated"), file=ctx.name)

    # TODO how does this fail if cairo is not installed?
    from cairosvg import svg2png

    try:
        svg2png(bytestring=et.tostring(ctx.layout.root), write_to=filename, background_color="#fff")

    except IOError as e:
        error(
            IOError(f"cannot write to file {format_filename(filename)}: {e.strerror}"),
            file=ctx.name,
        )


def as_ai(ctx, filename):
    """export the generated graphic as an AI file (experimental)"""

    warning(
        ValueError("saving AI is an experimental feature"),
        "Please check that the generated files are correct",
    )

    if ctx.layout is None:
        error(ValueError("no layout has been generated"), file=ctx.name)

    # TODO how does this fail if cairo is not installed?
    from cairosvg import svg2pdf

    try:
        svg2pdf(bytestring=et.tostring(ctx.layout.root), write_to=filename, background_color="#fff")

    except IOError as e:
        error(
            IOError(f"cannot write to file {format_filename(filename)}: {e.strerror}"),
            file=ctx.name,
        )
