# -*- coding: utf-8 -*-

from xml.etree import ElementTree as et

from ..utils.config import config
from ..utils.logging import error, warning
from ..utils.path import Path
from ..utils.types import HorizontalAlign, Vector, VerticalAlign
from .kle import KeyType
from .profile.types import HomingType


class Layout:
    def __init__(self):

        self.root = et.Element("svg")

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
            ctx.kle.size.x * 1000,
            ctx.kle.size.y * 1000,
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
            x = _format(key.pos.x * 1000)
            y = _format(key.pos.y * 1000)
            g = et.SubElement(self.root, "g", {"transform": f"translate({x},{y})"})

            if key.type == KeyType.DEFHOME:
                if ctx.profile.homing.default == HomingType.SCOOP:
                    key.type = KeyType.SCOOP
                elif ctx.profile.homing.default == HomingType.BUMP:
                    key.type = KeyType.BUMP
                else:
                    key.type = KeyType.BAR

            ctx.profile.key(key, g)
            self.drawlegend(ctx, key, g)

        if ctx.profile.defs is not None:
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

            rect = ctx.profile.legend_rect(key, size)
            size = ctx.profile.legend_size(size)

            if key.size == "iso" and valign == 0:
                rect.x -= 250
                rect.w += 250

            legend = self.parselegend(legend)
            prevlegend = [None] + legend

            result = Path()
            position = Vector(0, 0)

            for leg, prev in zip(legend, prevlegend):

                for icons in reversed(ctx.icons):
                    icon = icons.icon(leg, 1000, size, valign)
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
                        "stroke-width": _format(1000 / config().dpi / 0.75 / 3),
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
                        .M(Vector(rect.x - 250, rect.y))
                        .h(rect.w + 250)
                        .v(rect.h)
                        .h(-rect.w)
                        .v(-1)
                        .h(-250)
                        .z()
                    ),
                    "fill": "none",
                    "stroke": "#f00",
                    "stroke-width": _format(1000 / config().dpi / 0.75 / 3),
                },
            )
        else:
            result = et.Element(
                "rect",
                {
                    "x": _format(rect.x),
                    "y": _format(rect.y),
                    "width": _format(rect.w),
                    "height": _format(rect.h),
                    "fill": "none",
                    "stroke": "#f00",
                    "stroke-width": _format(1000 / config().dpi / 0.75 / 3),
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
