from __future__ import annotations

from pathlib import Path

from ..utils.logging import error, format_filename, warning
from .ctx import Context


def as_svg(ctx: Context, filename: str):
    """save the generated graphic as an SVG graphic"""

    if ctx.drawing is None:
        error(ValueError("no layout has been generated"), file=ctx.name)

    try:
        Path(filename).write_text(ctx.drawing)
    except OSError as e:
        error(
            OSError(f"cannot write to file {format_filename(filename)}: {e.strerror}"),
            file=ctx.name,
        )


def as_png(ctx: Context, filename: str):
    """save the graphic as a PNG image (requires Cairo)"""

    if ctx.drawing is None:
        error(ValueError("no layout has been generated"), file=ctx.name)

    # TODO how does this fail if cairo is not installed?
    from cairosvg import svg2png

    try:
        svg2png(bytestring=ctx.drawing, write_to=filename, background_color="#fff")

    except OSError as e:
        error(
            OSError(f"cannot write to file {format_filename(filename)}: {e.strerror}"),
            file=ctx.name,
        )


def as_pdf(ctx: Context, filename: str):
    """save the graphic as a PDF file (requires Cairo)"""

    if ctx.drawing is None:
        error(ValueError("no layout has been generated"), file=ctx.name)

    # TODO how does this fail if cairo is not installed?
    from cairosvg import svg2pdf

    try:
        svg2pdf(bytestring=ctx.drawing, write_to=filename, background_color="#fff")

    except OSError as e:
        error(
            OSError(f"cannot write to file {format_filename(filename)}: {e.strerror}"),
            file=ctx.name,
        )


def as_ai(ctx, filename):
    """save the graphic as an AI file (experimental; requires Cairo)"""

    warning(
        ValueError("saving AI is an experimental feature"),
        "Please check that the generated files are correct",
    )

    as_pdf(ctx, filename)
