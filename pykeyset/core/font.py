# -*- coding: utf-8 -*-

import os.path
from xml.etree import ElementTree as et

from .. import res
from ..utils.error import error, warning
from ..utils.path import Path
from ..utils.types import Vector


class Glyph:
    def __init__(self, name, path, advance):

        self.name = name
        self.path = path
        self.advance = advance


class Font:
    def __init__(self):

        self.file = None

        # Glyph objects
        self.glyphs = {}
        self.replacementchar = None

        # Font metrics
        self.emsize = 1000
        self.capheight = 800
        self.xheight = 500
        self.slope = 0
        # self.lineheight = 1  # TODO enable this when I enable multiline legend support
        self.kerning = {}

    @classmethod
    def load(cls, ctx, fontfile):

        self = cls()
        self.file = fontfile

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
            if a not in root.attrib:
                error(f"no global '{a}' attribute for font '{self.file}'")

        self.emsize = float(root.get("em-size"))
        self.capheight = float(root.get("cap-height"))
        self.xheight = float(root.get("x-height"))

        if "slope" not in root.attrib:
            warning(f"no global 'slope' attribute for font '{self.file}'. Using default value (0)")
        self.slope = float(root.get("slope", 0))
        # TODO enable this when I enable multiline legend support
        # if "line-height" not in root.attrib:
        #     warning(
        #         f"no global 'line-height' attribute for font '{self.file}'. "
        #         "Using default value (equal to em-size)"
        #     )
        # self.lineheight = float(root.get("line-height", self.emsize))

        if "horiz-adv-x" not in root.attrib:
            warning(
                f"no global 'horiz-adv-x' attribute for font '{self.file}'. "
                "this attribute must for each individual glyph instead"
            )
            def_advance = None
        else:
            def_advance = float(root.get("horiz-adv-x"))
        global_xform = root.get("transform", None)

        for glyph in root.findall("glyph"):

            skip = False
            for a in ("char", "path"):
                if a not in glyph.attrib:
                    warning(f"no '{a}' attribute for 'glyph' in '{self.file}'. Ignoring this glyph")
                    skip = True
            if skip:
                continue

            char = glyph.get("char")
            gp = Path(glyph.get("path"))

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

            self.glyphs[char] = Glyph(char, gp, advance)

        if len(self.glyphs) == 0:
            error(f"no valid glyphs found in font '{self.file}'")

        for kern in root.findall("kern"):

            skip = False
            for a in ("u", "k"):
                if a not in kern.attrib:
                    warning(
                        f"no '{a}' attribute for 'kern' in '{self.file}'. Ignoring "
                        "this kerning value"
                    )
                    skip = True
            if skip:
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

            for c1 in u[0]:
                for c2 in u[1]:
                    self.kerning[f"{c1}{c2}"] = k

        ctx.font = self

    def getglyph(self, ctx, legend, size):

        scale = size / self.capheight

        if legend not in self.glyphs:
            return None, 0

        glyph = self.glyphs[legend]
        path = glyph.path.copy()
        path.scale(Vector(scale, scale))

        return path, glyph.advance * scale

    def getkerning(self, c1, c2, size):
        if not c1 or not c2:
            return 0
        else:
            return self.kerning.get(f"{c1}{c2}", 0) * size / self.capheight

    def replacement(self, size):

        # Scale to match the loaded font's emsize, then to match the given size
        scale = (self.emsize / 1000) * (size / self.capheight)

        return (
            Path()
            .M(Vector(146, 0))
            .a(Vector(73, 73), 0, 0, 1, Vector(-73, -73))
            .l(Vector(0, -580))
            .a(Vector(73, 73), 0, 0, 1, Vector(73, -73))
            .l(Vector(374, 0))
            .a(Vector(73, 73), 0, 0, 1, Vector(73, 73))
            .l(Vector(0, 580))
            .a(Vector(73, 73), 0, 0, 1, Vector(-73, 73))
            .z()
            .M(Vector(283, -110))
            .a(Vector(50, 50), 0, 0, 0, Vector(100, 0))
            .a(Vector(50, 50), 0, 0, 0, Vector(-100, 0))
            .z()
            .M(Vector(293, -236))
            .a(Vector(40, 40), 0, 0, 0, Vector(80, 0))
            .a(Vector(120, 108), 0, 0, 1, Vector(60, -94))
            .a(Vector(200, 180), 0, 0, 0, Vector(100, -156))
            .a(Vector(200, 180), 0, 0, 0, Vector(-400, 0))
            .a(Vector(40, 40), 0, 0, 0, Vector(80, 0))
            .a(Vector(120, 108), 0, 0, 1, Vector(240, 0))
            .a(Vector(120, 108), 0, 0, 1, Vector(-60, 94))
            .a(Vector(200, 180), 0, 0, 0, Vector(-100, 156))
            .z()
            .scale(Vector(scale, scale)),
            # This has an advance of 638
            638 * scale,
        )
