# coding: utf-8

import os.path
from xml.etree import ElementTree as et

# from .. import fonts
from ..utils.error import error, warning
from ..utils.types import Point, Dist, Rect, Size
from ..utils import path, config
from .. import res
from .glyph import Glyph, Kern
from .kle import KeyType


class Font:
    def __init__(self):

        self.file = None

        # Glyph objects
        self.glyphs = []
        self.replacement = None

        # Font metrics
        self.emsize = 1000
        self.capheight = 800
        self.xheight = 500
        self.slope = 0
        self.lineheight = 1
        self.kerning = Kern()

    @classmethod
    def load(cls, ctx, fontfile):

        self = cls()
        self.file = fontfile
        self.glyphs = {}

        try:
            if not os.path.isfile(self.file):

                if self.file in res.fonts:
                    file = res.fonts[self.file]

                else:
                    error(f"cannot load font from '{os.path.abspath(self.file)}'. File not found")

                with file as f:
                    root = et.parse(f).getroot()
            else:
                root = et.parse(self.file).getroot()

        except IOError as e:
            error(f"cannot load font from '{self.file}'. {e.strerror}")
        except et.ParseError as e:
            error(f"cannot load font from '{self.file}'. {e.msg.capitalize()}")

        for a in ("em-size", "cap-height", "x-height"):
            if not a in root.attrib:
                error(f"no global '{a}' attribute for font '{self.file}'")

        self.emsize = float(root.get("em-size"))
        self.capheight = float(root.get("cap-height"))
        self.xheight = float(root.get("x-height"))

        if not "slope" in root.attrib:
            warning(
                f"no global 'slope' attribute for font '{self.file}'. " "Using default value (0)"
            )
        self.slope = float(root.get("slope", 0))
        if not "line-height" in root.attrib:
            warning(
                f"no global 'line-height' attribute for font '{self.file}'. "
                "Using default value (equal to em-size)"
            )
        self.lineheight = float(root.get("line-height", self.emsize))

        if not "horiz-adv-x" in root.attrib:
            warning(
                f"no global 'horiz-adv-x' attribute for font '{self.file}'. "
                "this attribute must for each individual glyph instead"
            )
            def_advance = None
        else:
            def_advance = float(root.get("horiz-adv-x"))
        global_xform = root.get("transform", None)

        for glyph in root.findall("glyph"):
            for a in ("char", "path"):
                if not a in glyph.attrib:
                    warning(
                        f"no '{a}' attribute for 'glyph' in '{self.file}'. Ignoring " "this glyph"
                    )
                    continue

            char = glyph.get("char")
            gp = path.Path(glyph.get("path"))

            if "transform" in glyph.attrib:
                gp.transform(glyph.get("transform"))

            if global_xform is not None:
                gp.transform(global_xform)

            if "horiz-adv-x" in glyph.attrib:
                advance = float(glyph.get("horiz-adv-x"))
            elif def_advance is not None:
                advance = def_advance
            else:
                warning(
                    f"no 'horiz-adv-x' attribute for 'glyph' and not default value "
                    f"set in '{self.file}'. Ignoring this glyph"
                )
                continue

            self.glyphs[char] = Glyph(gp, advance)

        if len(self.glyphs) == 0:
            error(f"no valid glyphs found in font '{self.file}'")

        for kern in root.findall("kern"):
            for a in ("u", "k"):
                if not a in kern.attrib:
                    warning(
                        f"no '{a}' attribute for 'kern' in '{self.file}'. Ignoring "
                        "this kerning value"
                    )
                    continue

            u = kern.get("u")
            if len(u) != 2:
                warning(
                    f"invalid 'u' attribute for 'kern' in '{self.file}'. Ignoring "
                    "this kerning value"
                )
                continue

            try:
                k = float(kern.get("k"))
            except ValueError:
                warning(
                    f"invalid 'k' attribute for 'kern' in '{self.file}'. Ignoring "
                    "this kerning value"
                )
                continue

            self.kerning.add(u[0], u[1], k)

        ctx.font = self

    def drawtext(self, ctx, key, g, unit):

        for i, (legend, size, color) in enumerate(zip(key.legend, key.legsize, key.fgcol)):

            x, y = i % 3, i // 3

            if len(legend) == 0:
                continue

            if size < 4:
                textscale = ctx.profile.textsize.mod / self.capheight
                textrect = Rect(*ctx.profile.textrect.mod)
            elif size == 4:
                textscale = ctx.profile.textsize.symbol / self.capheight
                textrect = Rect(*ctx.profile.textrect.symbol)
            else:
                textscale = ctx.profile.textsize.alpha / self.capheight
                textrect = Rect(*ctx.profile.textrect.alpha)

            if key.type == KeyType.NONE:
                r = ctx.profile.bottom
                textrect = Rect(r.x, r.y, r.w, r.h)

            if config.config.showalignment:
                et.SubElement(
                    g,
                    "rect",
                    {
                        "x": str(textrect.x * unit),
                        "y": str(textrect.y * unit),
                        "width": str(textrect.w * unit),
                        "height": str(textrect.h * unit),
                        "fill": "none",
                        "stroke": "#f00",
                        "stroke-width": str(unit / config.config.dpi / 0.75 / 3),
                    },
                )

            if key.size == "iso":
                textrect.x += 0.25
                textrect.w += 0.25
                textrect.h += 1
            elif key.size == "step":
                textrect.w += 0.25
            else:
                textrect.w += key.size.w - 1
                textrect.h += key.size.h - 1

            result = self.rendertext(ctx, legend)

            print(legend, self.capheight, result.rect())

            result.scale(Dist(textscale, textscale))

            rect = result.rect()
            if rect.w > textrect.w:
                warning(
                    f"squishing legend '{legend}' to {100 * textrect.w / rect.w:.3f}% of its "
                    "natural width to fit"
                )
                result.scale(Dist(textrect.w / rect.w, 1))
                rect = result.rect()
            rect.h = self.capheight * textscale

            pos = Dist(
                textrect.x - rect.x + (x / 2) * (textrect.w - rect.w),
                textrect.y + rect.h + (y / 2) * (textrect.h - rect.h),
            )

            result.translate(pos)
            result.scale(Dist(unit, unit))

            et.SubElement(
                g,
                "path",
                {
                    "d": str(result),
                    "fill": str(color),
                    "stroke": "none",
                },
            )

    def rendertext(self, ctx, legend):

        result = path.Path()
        position = Point(0, 0)

        glyphs = []
        remainder = legend
        while len(remainder) > 0:

            # Parse {name} sequences in the text
            if remainder[0] == "{":
                end = remainder.find("}")

                # If there is no matching closing } or there is another { before it
                if end < 1 or "{" in remainder[1:end]:
                    if "{" in self.glyphs:
                        glyphs.append(self.glyphs["{"])
                    else:
                        warning("no glyph for character '{{', using replacement glyph instead")
                        glyphs.append(self._replacement)
                    remainder = remainder[1:]

                else:
                    name = remainder[1:end]

                    # Try to find an icon with this name
                    for icons in ctx.icons[::-1]:
                        if name in icons:
                            glyphs.append(icons[name])
                            remainder = remainder[end + 1 :]
                            break

                    else:
                        # Else try to find a character with this name
                        if name in self.glyphs:
                            glyphs.append(self.glyphs[name])
                            remainder = remainder[end + 1 :]

                        # Or finally just print the characters literally
                        else:
                            if "{" in self.glyphs:
                                glyphs.append(self.glyphs["{"])
                            else:
                                warning(
                                    "no glyph for character '{', using replacement glyph instead"
                                )
                                glyphs.append(self._replacement)
                            remainder = remainder[1:]

            else:
                if remainder[0] in self.glyphs:
                    glyphs.append(self.glyphs[remainder[0]])
                else:
                    warning(
                        f"no glyph for character '{remainder[0]}', using replacement glyph instead"
                    )
                    glyphs.append(self._replacement)
                remainder = remainder[1:]

        for glyph in glyphs:
            textpath = glyph.path.copy()
            textpath.translate(position)
            position.x += glyph.advance
            result.append(textpath)

        return result

    @property
    def _replacement(self):
        g = Glyph(
            path.Path()
            .M(Point(146, 0))
            .a(Size(73, 73), 0, 0, 1, Dist(-73, -73))
            .l(Dist(0, -580))
            .a(Size(73, 73), 0, 0, 1, Dist(73, -73))
            .l(Dist(374, 0))
            .a(Size(73, 73), 0, 0, 1, Dist(73, 73))
            .l(Dist(0, 580))
            .a(Size(73, 73), 0, 0, 1, Dist(-73, 73))
            .z()
            .M(Point(283, -110))
            .a(Size(50, 50), 0, 0, 0, Dist(100, 0))
            .a(Size(50, 50), 0, 0, 0, Dist(-100, 0))
            .z()
            .M(Point(293, -236))
            .a(Size(40, 40), 0, 0, 0, Dist(80, 0))
            .a(Size(120, 108), 0, 0, 1, Dist(60, -94))
            .a(Size(200, 180), 0, 0, 0, Dist(100, -156))
            .a(Size(200, 180), 0, 0, 0, Dist(-400, 0))
            .a(Size(40, 40), 0, 0, 0, Dist(80, 0))
            .a(Size(120, 108), 0, 0, 1, Dist(240, 0))
            .a(Size(120, 108), 0, 0, 1, Dist(-60, 94))
            .a(Size(200, 180), 0, 0, 0, Dist(-100, 156))
            .z()
            .scale(Dist(self.emsize / 1000, self.emsize / 1000)),
            # This has an advance of 638, divide by its em-size (1000) and multiply by the used font's em-size
            0.638 * self.emsize,
        )

        return g
