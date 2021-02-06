# -*- coding: utf-8 -*-

from xml.etree import ElementTree as et

from ..utils.config import config
from ..utils.logging import error, warning
from ..utils.path import Path
from ..utils.types import HorizontalAlign, Vector, VerticalAlign
from .kle import KeyType


class Layout:
    def __init__(self):

        self.root = et.Element("svg")

        self.unit = 1000  # Number of SVG units in 1u size

    @classmethod
    def layout(cls, ctx):
        """generate a layout diagram from the loaded resources"""

        if ctx.kle is None:
            error(ValueError("no KLE layout is loaded"))
        elif ctx.font is None:
            error(ValueError("no font is loaded"))
        elif ctx.profile is None:
            error(ValueError("no profile is loaded"))

        self = cls()

        svg_size = Vector(
            ctx.kle.size.x * 0.75 * config().dpi,  # 1u = 0.75in
            ctx.kle.size.y * 0.75 * config().dpi,
        )
        viewbox = Vector(
            ctx.kle.size.x * self.unit,
            ctx.kle.size.y * self.unit,
        )

        self.root.attrib.update(
            {
                "width": _format(svg_size.x),
                "height": _format(svg_size.y),
                "viewBox": f"0 0 {_format(viewbox.x)} {_format(viewbox.y)}",
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

        ctx.layout = self

    def drawlegend(self, ctx, key, g):

        if config().show_align:
            for size in set(key.legsize):
                rect = ctx.profile.getlegendrect(key, size)
                g.append(self.drawlegendrect(key, rect))

        for i, (legend, size, color) in enumerate(zip(key.legend, key.legsize, key.fgcol)):

            halign = (HorizontalAlign.LEFT, HorizontalAlign.CENTER, HorizontalAlign.RIGHT)[i % 3]
            valign = (VerticalAlign.TOP, VerticalAlign.MIDDLE, VerticalAlign.BOTTOM)[i // 3]

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
            position = Vector(0, 0)

            for leg, prev in zip(legend, prevlegend):

                for icons in reversed(ctx.icons):
                    icon = icons.icon(leg, 1, size, valign)
                    if icon is not None:
                        path = icon.path
                        advance = path.boundingbox.width

                        path.translate(position)
                        position = position._replace(x=position.x + advance)
                        result.append(path)

                        break
                else:
                    glyph = ctx.font.glyph(leg, size)
                    if glyph is not None:
                        path = glyph.path
                        advance = glyph.advance

                        position = position._replace(
                            x=position.x - ctx.font.kerning.get(prev, leg, size)
                        )
                        path.translate(position)
                        position = position._replace(x=position.x + advance)
                        result.append(path)

                    elif len(leg) > 1:
                        warning(
                            ValueError(f"no glyph for character '{leg}'"),
                            "Drawing name literally instead",
                        )

                        prevl = [prev] + list(leg)
                        for l, p in zip(leg, prevl):  # noqa: E741

                            glyph = ctx.font.glyph(l, size)
                            if glyph is not None:
                                path = glyph.path
                                advance = glyph.advance
                            else:
                                glyph = ctx.font.replacement(size)
                                path = glyph.path
                                advance = glyph.advance
                                warning(
                                    ValueError(f"no glyph for character '{l}'"),
                                    "Using replacement glyph instead",
                                )

                            position = position._replace(
                                x=position.x - ctx.font.kerning.get(p, l, size)
                            )
                            path.translate(position)
                            position = position._replace(x=position.x + advance)
                            result.append(path)
                    else:
                        glyph = ctx.font.replacement(size)
                        path = glyph.path
                        advance = glyph.advance
                        warning(
                            ValueError(f"no glyph for character '{leg}'"),
                            "Using replacement glyph instead",
                        )

                        path.translate(position)
                        position = position._replace(x=position.x + advance)
                        result.append(path)

            legendsize = result.boundingbox

            if legendsize.w > rect.w:
                warning(
                    ValueError(
                        f"legend '{''.join(legend)}' is {legendsize.w / rect.w:.3f} times larger "
                        "than the bounding box"
                    ),
                    "squishing legend to fit",
                )
                pos = Vector(legendsize.x, legendsize.y)
                result.scale(Vector(rect.w / legendsize.w, 1))
                legendsize = result.boundingbox
            legendsize = legendsize._replace(h=size)

            pos = Vector(
                rect.x - legendsize.x + halign.value * (rect.w - legendsize.w),
                rect.y + legendsize.h + valign.value * (rect.h - legendsize.h),
            )

            result.translate(pos)
            result.scale(Vector(self.unit, self.unit))

            if config().show_align:
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
                        "stroke-width": _format(self.unit / config().dpi / 0.75 / 3),
                    },
                )

            et.SubElement(
                g,
                "path",
                {
                    "d": str(result),
                    "fill": color.to_hex(),
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
                        .M(Vector(rect.x - 0.25, rect.y))
                        .h(rect.w + 0.25)
                        .v(rect.h)
                        .h(-rect.w)
                        .v(-1)
                        .h(-0.25)
                        .z()
                        .scale(Vector(self.unit, self.unit))
                    ),
                    "fill": "none",
                    "stroke": "#f00",
                    "stroke-width": _format(self.unit / config().dpi / 0.75 / 3),
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
                    "stroke-width": _format(self.unit / config().dpi / 0.75 / 3),
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
