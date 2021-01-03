# -*- coding: utf-8 -*-

from xml.etree import ElementTree as et

from ..utils.types import Size, Point, Dist
from ..utils.error import error, warning
from ..utils.path import Path
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
            self.drawlegend(ctx, key, g)

        self.root.insert(0, ctx.profile.defs)

        et.ElementTree(self.root).write(".a.svg")

    def drawlegend(self, ctx, key, g):

        if config.config.showalignment:
            for size in set(key.legsize):
                rect = ctx.profile.getlegendrect(key, size)
                g.append(self.drawlegendrect(key, rect))

        for i, (legend, size, color) in enumerate(zip(key.legend, key.legsize, key.fgcol)):

            halign, valign = i % 3, i // 3

            if len(legend) == 0:
                continue

            rect = ctx.profile.getlegendrect(key, size)
            size = ctx.profile.getlegendsize(size)

            if key.size == "iso" and valign == 0:
                rect.x -= 0.25
                rect.w += 0.25

            legend = self.parselegend(legend)
            prevlegend = [None] + legend

            result = Path()
            position = Point(0, 0)

            for leg, prev in zip(legend, prevlegend):

                for icons in reversed(ctx.icons):
                    path, advance = icons.geticon(ctx, leg, size, valign)
                    if path is not None:
                        break
                else:
                    path, advance = ctx.font.getglyph(ctx, leg, size)

                if path is None:
                    if len(leg) > 1:
                        warning(f"no glyph for character '{leg}'")

                        prevl = [prev] + list(leg)
                        for l, p in zip(leg, prevl):  # noqa: E741

                            path, advance = ctx.font.getglyph(ctx, l, size)
                            if path is None:
                                path, advance = ctx.font.replacement(size)
                                warning(
                                    f"no glyph for character '{l}', using replacement glyph "
                                    "instead"
                                )

                            position.x -= ctx.font.getkerning(p, l, size)
                            path.translate(position)
                            position.x += advance
                            result.append(path)
                    else:
                        path, advance = ctx.font.replacement(size)
                        warning(f"no glyph for character '{leg}', using replacement glyph instead")

                        path.translate(position)
                        position.x += advance
                        result.append(path)
                else:
                    position.x -= ctx.font.getkerning(prev, leg, size)
                    path.translate(position)
                    position.x += advance
                    result.append(path)

            legendsize = result.boundingbox

            if legendsize.w > rect.w:
                warning(
                    f"squishing legend '{''.join(legend)}' to {100 * rect.w / legendsize.w:.3f}% "
                    "of its natural width to fit"
                )
                pos = Point(legendsize.x, legendsize.y)
                result.scale(Dist(rect.w / legendsize.w, 1))
                legendsize = result.boundingbox
            legendsize.h = size

            pos = Dist(
                rect.x - legendsize.x + (halign / 2) * (rect.w - legendsize.w),
                rect.y + legendsize.h + (valign / 2) * (rect.h - legendsize.h),
            )

            result.translate(pos)
            result.scale(Dist(self.unit, self.unit))

            if config.config.showalignment:
                legendsize = result.boundingbox
                et.SubElement(
                    g,
                    "rect",
                    {
                        "x": _format(legendsize.x),
                        "y": _format(legendsize.y),
                        "width": _format(legendsize.w),
                        "height": _format(legendsize.h),
                        "fill": "none",
                        "stroke": "#f00",
                        "stroke-width": _format(self.unit / config.config.dpi / 0.75 / 3),
                    },
                )

            et.SubElement(
                g,
                "path",
                {
                    "d": str(result),
                    "fill": str(color),
                    "stroke": "none",
                },
            )

    def drawlegendrect(self, key, rect):

        if key.size == "iso":
            result = et.Element(
                "path",
                {
                    "d": str(
                        Path()
                        .M(Point(rect.x - 0.25, rect.y))
                        .h(rect.w + 0.25)
                        .v(rect.h)
                        .h(-rect.w)
                        .v(-1)
                        .h(-0.25)
                        .z()
                        .scale(Dist(self.unit, self.unit))
                    ),
                    "fill": "none",
                    "stroke": "#f00",
                    "stroke-width": _format(self.unit / config.config.dpi / 0.75 / 3),
                },
            )
        else:
            result = et.Element(
                "rect",
                {
                    "x": _format(rect.x * self.unit),
                    "y": _format(rect.y * self.unit),
                    "width": _format(rect.w * self.unit),
                    "height": _format(rect.h * self.unit),
                    "fill": "none",
                    "stroke": "#f00",
                    "stroke-width": _format(self.unit / config.config.dpi / 0.75 / 3),
                },
            )

        return result

    def parselegend(self, legend):

        result = []

        while len(legend) > 0:

            # Reduce {{ and }} to a single { and }
            if legend.startswith("{{") or legend.startswith("}}"):
                result.append(legend[0])
                legend = legend[2:]

            # Parse {name} sequences in the text
            elif legend[0] == "{":
                end = legend.find("}")

                # If there is no matching closing } or there is another { before the closing }
                if end < 1 or "{" in legend[1:end]:
                    result.append(legend[0])
                    legend = legend[1:]

                else:
                    name = legend[0 : end + 1]
                    result.append(name)
                    legend = legend[end + 1 :]

            else:
                result.append(legend[0])
                legend = legend[1:]

        return result


# Format a number as efficiently as possible
def _format(num):
    return f"{float(num):.3f}".rstrip("0").rstrip(".")
