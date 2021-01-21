# -*- coding: utf-8 -*-
from xml.etree import ElementTree as et

from ..utils.logging import error, format_filename


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
