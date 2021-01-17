# -*- coding: utf-8 -*-

import os.path
from enum import Enum
from numbers import Number
from xml.etree import ElementTree as et

from recordclass import recordclass
from toml import TomlDecodeError

from .. import res
from ..utils import tomlparser
from ..utils.error import error
from ..utils.path import Path
from ..utils.types import Rect, RoundRect, Vector
from .kle import KeyType

ProfileType = Enum("ProfileType", ("CYLINDRICAL", "SPHERICAL", "FLAT"))
GradientType = Enum("GradientType", ("KEY", "SCOOP", "SPACE"))

TextTypeProp = recordclass("TextTypeProp", ("alpha", "symbol", "mod"))


class Profile:
    def __init__(self):

        self.name = None

        self.type = ProfileType.CYLINDRICAL
        self.depth = 0
        self.bottom = RoundRect(0, 0, 0, 0, 0)
        self.top = RoundRect(0, 0, 0, 0, 0)
        self.textrect = TextTypeProp(Rect(0, 0, 0, 0), Rect(0, 0, 0, 0), Rect(0, 0, 0, 0))
        self.textsize = TextTypeProp(0, 0, 0)
        self.defaulthoming = None
        self.homing = {}

        self.defs = None
        self.gradients = []  # Keep track of which keytop gradients have already been generated

    @classmethod
    def load(cls, ctx, file):
        """load a built in profile or a keycap profile config file"""

        self = cls()
        self.name = file

        try:
            if not os.path.isfile(self.name):

                if self.name in res.profiles:
                    file = res.profiles[self.name]

                else:
                    error(
                        f"cannot load profile from '{os.path.abspath(self.name)}'. File not found"
                    )

                with file as f:
                    root = tomlparser.load(f)
            else:
                root = tomlparser.load(self.name)

        except IOError as e:
            error(f"cannot load profile from '{self.name}'. {e.strerror}")
        except TomlDecodeError as e:
            error(f"cannot load profile from '{self.name}'. {str(e).capitalize()}")

        try:
            proftype = root.getkey("type", type=str).upper()
            if proftype not in (t.name for t in ProfileType):
                error(f"invalid value '{proftype}' for 'type' in profile '{self.name}'")
            self.type = ProfileType[proftype]

            if self.type != ProfileType.FLAT:
                self.depth = root.getkey("depth", type=Number)
            else:
                self.depth = 0

        except KeyError as e:
            error(f"no key '{e.args[0]}' in profile '{self.name}'")
        except TypeError as e:
            error(f"invalid value for key '{e.args[0]}' in profile '{self.name}'")

        try:
            bottom = root.getsection("bottom")
            top = root.getsection("top")
            legend = root.getsection("legend")
            homing = root.getsection("homing")

        except KeyError as e:
            error(f"no section [{e.args[0]}] in profile '{self.name}'")

        try:
            w = bottom.getkey("width", type=Number) / 19.05
            h = bottom.getkey("height", type=Number) / 19.05
            r = bottom.getkey("radius", type=Number) / 19.05
            self.bottom = RoundRect(0.5 - (w / 2), 0.5 - (h / 2), w, h, r)

            w = top.getkey("width", type=Number) / 19.05
            h = top.getkey("height", type=Number) / 19.05
            r = top.getkey("radius", type=Number) / 19.05
            top_offset = top.getkey("y-offset", type=Number, default=0) / 19.05
            self.top = RoundRect(0.5 - (w / 2), 0.5 - (h / 2) + top_offset, w, h, r)

        except KeyError as e:
            error(f"no key '{e.args[0]}' in section [{e.args[1]}] in profile '{self.name}'")
        except ValueError as e:
            error(
                f"invalid value for key '{e.args[0]}' in section [{e.args[1]}] in profile "
                f"'{self.name}'"
            )

        try:
            default_w = legend.getkey("width", type=Number, default=None)
            default_h = legend.getkey("height", type=Number, default=None)
            default_offset = legend.getkey("y-offset", type=Number, default=0)

            for texttype in ("alpha", "symbol", "mod"):
                try:
                    section = legend.getsection(texttype)
                    textsize = float(section["size"]) / 19.05
                except KeyError as e:
                    error(f"no key '{e.args[0]}' in section [{e.args[1]}] in profile '{self.name}'")
                except ValueError as e:
                    error(
                        f"invalid value for key '{e.args[0]}' in section [{e.args[1]}] in profile "
                        f"'{self.name}'"
                    )

                w = section.getkey("width", Number, default_w) / 19.05
                h = section.getkey("height", Number, default_h) / 19.05
                offset = section.getkey("y-offset", Number, default_offset) / 19.05 + top_offset

                for key, value in {"width": w, "height": h}.items():
                    if value is None:
                        error(
                            f"no key '{key}' in section [{section.section}] or in section "
                            f"[{legend.section}] in profile '{self.name}'"
                        )

                setattr(self.textrect, texttype, Rect(0.5 - (w / 2), 0.5 - (h / 2) + offset, w, h))
                setattr(self.textsize, texttype, textsize)

        except ValueError as e:
            error(
                f"invalid value for key '{e.args[0]}' in section [{e.args[1]}] in profile "
                f"'{self.name}'"
            )

        try:
            if "scoop" in homing and isinstance(homing["scoop"], tomlparser.TomlNode):
                depth = homing["scoop"].getkey("depth", type=Number)

                self.homing["scoop"] = {"depth": depth}

            if "bar" in homing and isinstance(homing["bar"], tomlparser.TomlNode):
                width = homing["bar"].getkey("width", type=Number, default=0)
                height = homing["bar"].getkey("height", type=Number, default=0)
                offset = homing["bar"].getkey("y-offset", type=Number, default=0)

                self.homing["bar"] = {"width": width, "height": height, "offset": offset}

            if "bump" in homing and isinstance(homing["bump"], tomlparser.TomlNode):
                radius = homing["bump"].getkey("radius", type=Number, default=0)
                offset = homing["bump"].getkey("y-offset", type=Number, default=0)

                self.homing["bump"] = {"radius": radius, "offset": offset}

        except KeyError as e:
            error(f"no key '{e.args[0]}' in section [{e.args[1]}] in profile '{self.name}'")
        except ValueError as e:
            error(
                f"invalid value for key '{e.args[0]}' in section [{e.args[1]}] in profile "
                f"'{self.name}'"
            )

        try:
            default = homing.getkey("default", str)

            if default not in ("scoop", "bar", "bump"):
                error(
                    f"unknown default homing type '{default}' in section [{homing.section}] in "
                    f"file '{self.name}'"
                )
            elif default not in self.homing:
                error(
                    f"default homing type '{default}' has no corresponding section "
                    f"[{homing.section}.{default}] in '{self.name}'"
                )
            else:
                self.defaulthoming = default

        except KeyError as e:
            error(f"no key '{e.args[0]}' in section [{e.args[1]}] in profile '{self.name}'")
        except ValueError as e:
            error(
                f"invalid value for key '{e.args[0]}' in section [{e.args[1]}] in profile "
                f"'{self.name}'"
            )

        ctx.profile = self

    def drawkey(self, ctx, key, g, unit):

        if key.type == KeyType.NONE:
            pass  # do nothing

        elif key.size == "iso":
            self._drawisobottom(ctx, g, key.bgcol, unit)
            self._drawisotop(ctx, g, key.bgcol, unit)

        elif key.size == "step":
            self._drawkeybottom(ctx, g, Vector(1.75, 1), key.bgcol, unit)
            self._drawkeytop(ctx, g, key.type, Vector(1.25, 1), key.bgcol, unit)
            self._drawstep(ctx, g, key.bgcol, unit)

        else:
            self._drawkeybottom(ctx, g, key.size, key.bgcol, unit)
            self._drawkeytop(ctx, g, key.type, key.size, key.bgcol, unit)

    def getlegendrect(self, key, size):

        if size < 4:
            rect = Rect(*self.textrect.mod)
        elif size == 4:
            rect = Rect(*self.textrect.symbol)
        else:
            rect = Rect(*self.textrect.alpha)

        if key.type == KeyType.NONE:
            rect = Rect(self.bottom.x, self.bottom.y, self.bottom.w, self.bottom.h)

        if key.size == "iso":
            rect = rect._replace(x=rect.x + 0.25, w=rect.w + 0.25, h=rect.h + 1)
        elif key.size == "step":
            rect = rect._replace(w=rect.w + 0.25)
        else:
            rect = rect._replace(w=rect.w + key.size.x - 1, h=rect.h + key.size.y - 1)

        return rect

    def getlegendsize(self, size):
        if size < 4:
            return self.textsize.mod * (size / 3)
        elif size == 4:
            return self.textsize.symbol
        else:
            return self.textsize.alpha * (size / 5)

    def _drawkeybottom(self, ctx, g, size, color, unit):
        rect = self.bottom
        et.SubElement(
            g,
            "rect",
            {
                "fill": color.to_hex(),
                "stroke": color.highlight().to_hex(),
                "stroke-width": "10",
                "x": _format(rect.x * unit),
                "y": _format(rect.y * unit),
                "width": _format((rect.w + size.x - 1) * unit),
                "height": _format((rect.h + size.y - 1) * unit),
                "rx": _format(rect.r * unit),
                "ry": _format(rect.r * unit),
            },
        )

    def _drawkeytop(self, ctx, g, keytype, size, color, unit):

        rect = self.top

        w = rect.w + size.x - 1 - 2 * rect.r
        h = rect.h + size.y - 1 - 2 * rect.r

        if keytype == KeyType.SCOOP:
            try:
                depth = self.homing["scoop"]["depth"]
            except KeyError:
                error(f"no scooped homing keys for profile '{self.name}'")
        else:
            depth = self.depth

        if self.type == ProfileType.FLAT:
            et.SubElement(
                g,
                "rect",
                {
                    "fill": color.to_hex(),
                    "stroke": color.highlight().to_hex(),
                    "stroke-width": "10",
                    "x": _format(rect.x * unit),
                    "y": _format(rect.y * unit),
                    "width": _format((rect.w + size.w - 1) * unit),
                    "height": _format((rect.h + size.h - 1) * unit),
                    "rx": _format(rect.r * unit),
                    "ry": _format(rect.r * unit),
                },
            )

        else:

            curve = depth / 50
            gradtype = GradientType.SCOOP if keytype == KeyType.SCOOP else GradientType.KEY

            # Calculate the radius of the arc for horizontal and vertical (for spherical) curved
            # keytop edges using standard formula for segments of an arc using w/h as the widths
            # and curve as the height
            hr = (curve ** 2 + (w ** 2 / 4)) / (2 * curve)
            vr = (curve ** 2 + (h ** 2 / 4)) / (2 * curve)

            if keytype == KeyType.SPACE:
                path = (
                    Path()
                    .M(Vector(rect.x, rect.y + rect.r))
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(rect.r, -rect.r))
                    .h(w)
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(rect.r, rect.r))
                    .a(Vector(vr, vr), 0, False, False, Vector(0, h))
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(-rect.r, rect.r))
                    .h(-w)
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(-rect.r, -rect.r))
                    .a(Vector(vr, vr), 0, False, False, Vector(0, -h))
                    .z()
                    .scale(Vector(unit, unit))
                )
                gradtype = GradientType.SPACE

            elif self.type == ProfileType.CYLINDRICAL:
                path = (
                    Path()
                    .M(Vector(rect.x, rect.y + rect.r))
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(rect.r, -rect.r))
                    .h(w)
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(rect.r, rect.r))
                    .v(h)
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(-rect.r, rect.r))
                    .a(Vector(hr, hr), 0, False, True, Vector(-w, 0))
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(-rect.r, -rect.r))
                    .z()
                    .scale(Vector(unit, unit))
                )

            else:  # ProfileType.SPHERICAL
                path = (
                    Path()
                    .M(Vector(rect.x, rect.y + rect.r))
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(rect.r, -rect.r))
                    .a(Vector(hr, hr), 0, False, True, Vector(w, 0))
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(rect.r, rect.r))
                    .a(Vector(vr, vr), 0, False, True, Vector(0, h))
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(-rect.r, rect.r))
                    .a(Vector(hr, hr), 0, False, True, Vector(-w, 0))
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(-rect.r, -rect.r))
                    .a(Vector(vr, vr), 0, False, True, Vector(0, -h))
                    .z()
                    .scale(Vector(unit, unit))
                )

            et.SubElement(
                g,
                "path",
                {
                    "fill": self._addgradient(ctx, gradtype, color, depth),
                    "stroke": color.highlight().to_hex(),
                    "stroke-width": "10",
                    "d": str(path),
                },
            )

    def _drawisobottom(self, ctx, g, color, unit):
        rect = self.bottom
        et.SubElement(
            g,
            "path",
            {
                "fill": color.to_hex(),
                "stroke": color.highlight().to_hex(),
                "stroke-width": "10",
                "d": str(
                    Path()
                    .M(Vector(rect.x, rect.y + rect.r))
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(rect.r, -rect.r))
                    .h(0.5 + rect.w - 2 * rect.r)
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(rect.r, rect.r))
                    .v(1 + rect.h - 2 * rect.r)
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(-rect.r, rect.r))
                    .h(-(0.25 + rect.w - 2 * rect.r))
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(-rect.r, -rect.r))
                    .v(-(1 - 2 * rect.r))
                    .a(Vector(rect.r, rect.r), 0, False, False, Vector(-rect.r, -rect.r))
                    .h(-(0.25 - 2 * rect.r))
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(-rect.r, -rect.r))
                    .v(-(rect.h - 2 * rect.r))
                    .z()
                    .scale(Vector(unit, unit))
                ),
            },
        )

    def _drawisotop(self, ctx, g, color, unit):
        rect = self.top
        curve = self.depth / 100

        w_top = rect.w + 1.5 - 1 - 2 * rect.r
        w_btm = rect.w + 1.25 - 1 - 2 * rect.r
        h_lefttop = rect.h - 2 * rect.r
        h_leftbtm = 1 - curve / 3 - 2 * rect.r
        h_right = rect.h + 2 - 1 - 2 * rect.r

        if self.type == ProfileType.FLAT:
            path = (
                Path()
                .M(Vector(rect.x, rect.y + rect.r))
                .a(Vector(rect.r, rect.r), 0, False, True, Vector(rect.r, -rect.r))
                .h(w_top)
                .a(Vector(rect.r, rect.r), 0, False, True, Vector(rect.r, rect.r))
                .v(h_right)
                .a(Vector(rect.r, rect.r), 0, False, True, Vector(-rect.r, rect.r))
                .h(-w_btm)
                .a(Vector(rect.r, rect.r), 0, False, True, Vector(-rect.r, -rect.r))
                .v(-(1 - 2 * rect.r))
                .a(Vector(rect.r, rect.r), 0, False, False, Vector(-rect.r, -rect.r))
                .h(-(0.25 - 2 * rect.r))
                .a(Vector(rect.r, rect.r), 0, False, True, Vector(-rect.r, -rect.r))
                .v(-h_lefttop)
                .z()
                .scale(Vector(unit, unit))
            )

        else:

            # Calculate the radius of the arc for horizontal and vertical (for spherical) curved
            # keytop edges using standard formula for segments of an arc using w/h as the widths
            # and curve as the height
            top_r, btm_r, lefttop_r, leftbtm_r, right_r = (
                (curve ** 2 + (d ** 2 / 4)) / (2 * curve)
                for d in (w_top, w_btm, h_lefttop, h_leftbtm, h_right)
            )

            if self.type == ProfileType.CYLINDRICAL:
                path = (
                    Path()
                    .M(Vector(rect.x, rect.y + rect.r))
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(rect.r, -rect.r))
                    .h(w_top)
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(rect.r, rect.r))
                    .v(h_right)
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(-rect.r, rect.r))
                    .a(Vector(btm_r, btm_r), 0, False, True, Vector(-w_btm, 0))
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(-rect.r, -rect.r))
                    .v(-(h_leftbtm))
                    .a(Vector(rect.r, rect.r), 0, False, False, Vector(-rect.r, -rect.r))
                    .l(Vector(-(0.25 - 2 * rect.r), -curve / 3))
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(-rect.r, -rect.r))
                    .v(-(h_lefttop))
                    .z()
                    .scale(Vector(unit, unit))
                )

            else:  # ProfileType.SPHERICAL
                path = (
                    Path()
                    .M(Vector(rect.x, rect.y + rect.r))
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(rect.r, -rect.r))
                    .a(Vector(top_r, top_r), 0, False, True, Vector(w_top, 0))
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(rect.r, rect.r))
                    .a(Vector(right_r, right_r), 0, False, True, Vector(0, h_right))
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(-rect.r, rect.r))
                    .a(Vector(btm_r, btm_r), 0, False, True, Vector(-w_btm, 0))
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(-rect.r, -rect.r))
                    .a(Vector(leftbtm_r, leftbtm_r), 0, False, True, Vector(0, -h_leftbtm))
                    .a(Vector(rect.r, rect.r), 0, False, False, Vector(-rect.r, -rect.r))
                    .l(Vector(-(0.25 - 2 * rect.r), -curve / 3))
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(-rect.r, -rect.r))
                    .a(Vector(lefttop_r, lefttop_r), 0, False, True, Vector(0, -h_lefttop))
                    .z()
                    .scale(Vector(unit, unit))
                )

        et.SubElement(
            g,
            "path",
            {
                "fill": self._addgradient(ctx, GradientType.KEY, color, self.depth),
                "stroke": color.highlight().to_hex(),
                "stroke-width": "10",
                "d": str(path),
            },
        )

    def _drawstep(self, ctx, g, color, unit):
        top = self.top
        btm = self.bottom

        rect = RoundRect(
            1.25 - (top.x + btm.x) / 2,
            (top.y + btm.y) / 2,
            0.5,
            (top.h + btm.h) / 2,
            (top.r + btm.r) / 2,
        )

        et.SubElement(
            g,
            "path",
            {
                "fill": self._addgradient(ctx, GradientType.SPACE, color, self.depth),
                "stroke": color.highlight().to_hex(),
                "stroke-width": "10",
                "d": str(
                    Path()
                    .M(Vector(rect.x, rect.y + rect.r))
                    .a(Vector(rect.r, rect.r), 0, False, False, Vector(-rect.r, -rect.r))
                    .h(rect.w)
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(rect.r, rect.r))
                    .v(rect.h - 2 * rect.r)
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(-rect.r, rect.r))
                    .h(-rect.w)
                    .a(Vector(rect.r, rect.r), 0, False, False, Vector(rect.r, -rect.r))
                    .v(-(rect.h - 2 * rect.r))
                    .z()
                    .scale(Vector(unit, unit))
                ),
            },
        )

    def _addgradient(self, ctx, gradtype, color, depth):

        if self.type == ProfileType.FLAT:
            # Flat has not gradients so we just return the flat colour
            return color.to_hex()

        else:
            id = f"{gradtype.name.lower()}-{color.to_hex().lstrip('#')}"
            url = f"url(#{id})"

            if self.defs is None:
                self.defs = et.Element("defs")
                self.gradients = []

        if id not in self.gradients:

            if gradtype in (GradientType.KEY, GradientType.SCOOP):

                if self.type == ProfileType.CYLINDRICAL:
                    gradient = et.SubElement(
                        self.defs,
                        "linearGradient",
                        {
                            "id": id,
                            "x1": "100%",
                            "y1": "0%",
                            "x2": "0%",
                            "y2": "0%",
                        },
                    )
                else:  # if ProfileType.SPHERICAL
                    gradient = et.SubElement(
                        self.defs,
                        "radialGradient",
                        {
                            "id": id,
                            "cx": "100%",
                            "cy": "100%",
                            "fx": "100%",
                            "fy": "100%",
                            "fr": "0%",
                            "r": "141%",
                        },
                    )
            else:  # if GradientType.SPACE
                gradient = et.SubElement(
                    self.defs,
                    "linearGradient",
                    {
                        "id": id,
                        "x1": "0%",
                        "y1": "0%",
                        "x2": "0%",
                        "y2": "100%",
                    },
                )

            stopcolors = [
                color.lighter(min(1, depth / 10)),
                color,
                color.darker(min(1, depth / 10)),
            ]
            stopdists = [0, 50, 100]

            for col, dist in zip(stopcolors, stopdists):
                et.SubElement(
                    gradient,
                    "stop",
                    {
                        "offset": f"{_format(dist)}%",
                        "stop-color": col.to_hex(),
                    },
                )

            self.gradients.append(id)

        return url


# Format a number as efficiently as possible
def _format(num):
    return f"{float(num):.3f}".rstrip("0").rstrip(".")
