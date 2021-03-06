# -*- coding: utf-8 -*-

from xml.etree import ElementTree as et

from ..utils.logging import error, format_filename, warning


def as_svg(ctx, filename):
    """save the generated graphic as an SVG graphic"""

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
    """save the graphic as a PNG image (requires Cairo)"""

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


def as_pdf(ctx, filename):
    """save the graphic as a PDF file (requires Cairo)"""

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


def as_ai(ctx, filename):
    """save the graphic as an AI file (experimental; requires Cairo)"""

    warning(
        ValueError("saving AI is an experimental feature"),
        "Please check that the generated files are correct",
    )

    as_pdf(ctx, filename)
