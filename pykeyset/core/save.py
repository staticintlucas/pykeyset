from __future__ import annotations

from pathlib import Path

from ..utils.logging import error, format_filename
from .ctx import Context


def as_svg(ctx: Context, filename: str):
    """save the generated graphic as an SVG graphic"""

    if ctx.drawing is None:
        error(ValueError("no layout has been generated"), file=ctx.name)

    try:
        Path(filename).write_text(ctx.drawing.to_svg())
    except OSError as e:
        error(
            OSError(f"cannot write to file {format_filename(filename)}: {e.strerror}"),
            file=ctx.name,
        )


def as_png(ctx: Context, filename: str):
    """save the graphic as a PNG image"""

    if ctx.drawing is None:
        error(ValueError("no layout has been generated"), file=ctx.name)

    try:
        Path(filename).write_bytes(ctx.drawing.to_png())
    except OSError as e:
        error(
            OSError(f"cannot write to file {format_filename(filename)}: {e.strerror}"),
            file=ctx.name,
        )


def as_pdf(ctx: Context, filename: str):
    """save the graphic as a PDF file"""

    if ctx.drawing is None:
        error(ValueError("no layout has been generated"), file=ctx.name)

    try:
        Path(filename).write_bytes(ctx.drawing.to_pdf())
    except OSError as e:
        error(
            OSError(f"cannot write to file {format_filename(filename)}: {e.strerror}"),
            file=ctx.name,
        )


def as_ai(ctx: Context, filename: str):
    """save the graphic as an AI file (experimental; requires Cairo)"""

    if ctx.drawing is None:
        error(ValueError("no layout has been generated"), file=ctx.name)

    try:
        Path(filename).write_bytes(ctx.drawing.to_ai())
    except OSError as e:
        error(
            OSError(f"cannot write to file {format_filename(filename)}: {e.strerror}"),
            file=ctx.name,
        )
