# -*- coding: utf-8 -*-

from xml.etree import ElementTree as et

from ..utils.types import Size
from ..utils.error import error
from ..utils import config
from .kle import KeyType


class Layout:
    def __init__(self):

        self.root = et.Element("svg")

        self.unit = 1000  # Number of SVG units in 1u size

    @classmethod
    def layout(cls, ctx):

        if ctx.kle is None:
            error("no KLE layout is loaded")
        elif ctx.font is None:
            error("no font is loaded")
        elif ctx.profile is None:
            error("no profile is loaded")

        self = cls()

        svg_size = Size(
            ctx.kle.size.w * 0.75 * config.config.dpi,  # 1u = 0.75in
            ctx.kle.size.h * 0.75 * config.config.dpi,
        )
        viewbox = Size(
            ctx.kle.size.w * self.unit,
            ctx.kle.size.h * self.unit,
        )

        self.root.attrib.update(
            {
                "width": _format(svg_size.w),
                "height": _format(svg_size.h),
                "viewBox": f"0 0 {_format(viewbox.w)} {_format(viewbox.h)}",
                "xmlns": "http://www.w3.org/2000/svg",
                "stroke-linecap": "round",
                "stroke-linejoin": "round",
            }
        )

        for key in ctx.kle.keys:
            x = _format(key.pos.x * self.unit)
            y = _format(key.pos.y * self.unit)
            g = et.SubElement(self.root, "g", {"transform": f"translate({x},{y})"})

            if key.type == KeyType.DEFHOME:
                if ctx.profile.defaulthoming == "scoop":
                    key.type = KeyType.SCOOP
                elif ctx.profile.defaulthoming == "bump":
                    key.type = KeyType.BUMP
                else:
                    key.type = KeyType.BAR

            ctx.profile.drawkey(ctx, key, g, self.unit)
            ctx.font.drawtext(ctx, key, g, self.unit)

        self.root.insert(0, ctx.profile.defs)

        et.ElementTree(self.root).write(".a.svg")


# Format a number as efficiently as possible
def _format(num):
    return f"{float(num):.3f}".rstrip("0").rstrip(".")
