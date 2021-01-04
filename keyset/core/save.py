# -*- coding: utf-8 -*-
from xml.etree import ElementTree as et

from ..utils.error import error


def as_svg(ctx, filename):

    if ctx.layout is None:
        error("no layout has been generated")

    try:
        et.ElementTree(ctx.layout.root).write(filename)
    except IOError as e:
        error(f"cannot save to file '{filename}'. {e.strerror}")
