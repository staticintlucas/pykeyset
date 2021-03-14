# -*- coding: utf-8 -*-

from xml.etree import ElementTree as et

from ...utils.logging import error
from ...utils.path import Path
from ...utils.types import Color, Rect, RoundRect, Vector
from ..kle import Key, KeyType
from .types import GradientType, HomingProperties, ProfileType, TextTypeProperty


class Profile:
    def __init__(
        self,
        name: str,
        type: ProfileType,
        depth: float,
        bottom_rect: RoundRect,
        top_rect: RoundRect,
        text_rect: TextTypeProperty[Rect],
        text_size: TextTypeProperty[float],
        homing: HomingProperties,
    ):

        self.name = name
        self.type = type
        self.depth = depth
        self.bottom = bottom_rect
        self.top = top_rect
        self.text_rect = text_rect
        self.text_size = text_size
        self.homing = homing

        self.defs = None
        self.gradients = []  # Keep track of which keytop gradients have already been generated

    def key(self, key: Key, g: et.Element) -> None:

        if key.type == KeyType.NONE:
            pass  # do nothing

        elif key.size in ("iso_h", "iso_v"):
            self.draw_iso_bottom(g, key.bgcol)
            self.draw_iso_top(g, key.bgcol)

        elif key.size == "step":
            self.draw_key_bottom(g, Vector(1.75, 1), key.bgcol)
            self.draw_key_top(g, key.type, Vector(1.25, 1), key.bgcol)
            self.draw_step(g, key.bgcol)

        else:
            self.draw_key_bottom(g, key.size, key.bgcol)
            self.draw_key_top(g, key.type, key.size, key.bgcol)

    def legend_rect(self, key: Key, size: int) -> Rect:

        if size < 4:
            rect = Rect(*self.text_rect.mod)  # type: ignore  # TODO when we drop 3.6 support
        elif size == 4:
            rect = Rect(*self.text_rect.symbol)  # type: ignore  # TODO when we drop 3.6 support
        else:
            rect = Rect(*self.text_rect.alpha)  # type: ignore  # TODO when we drop 3.6 support

        if key.type == KeyType.NONE:
            margin = Vector(
                rect.x - self.top.x,
                rect.y - self.top.y,
            )

            rect = Rect(
                self.bottom.x + margin.x,
                self.bottom.y + margin.y,
                self.bottom.w - 2 * margin.x,
                self.bottom.h - 2 * margin.y,
            )

        if key.size == "iso_v":
            rect = rect._replace(x=rect.x + 250, w=rect.w + 250, h=rect.h + 1000)
        elif key.size == "iso_h":
            rect = rect._replace(w=rect.w + 500)
        elif key.size == "step":
            rect = rect._replace(w=rect.w + 250)
        else:
            rect = rect._replace(
                w=rect.w + 1000 * (key.size.x - 1), h=rect.h + 1000 * (key.size.y - 1)
            )

        return rect

    def legend_size(self, size: int) -> float:
        if size < 4:
            return self.text_size.mod * (size / 3)  # type: ignore  # TODO when we drop 3.6 support
        elif size == 4:
            return self.text_size.symbol  # type: ignore  # TODO when we drop 3.6 support
        else:
            return self.text_size.alpha * (size / 5)  # type: ignore # TODO when we drop 3.6 support

    def draw_key_bottom(self, g: et.Element, size: Vector, color: Color) -> None:
        rect = self.bottom
        et.SubElement(
            g,
            "rect",
            {
                "fill": color.to_hex(),
                "stroke": color.highlight().to_hex(),
                "stroke-width": "10",
                "x": _format(rect.x),
                "y": _format(rect.y),
                "width": _format(rect.w + 1000 * (size.x - 1)),
                "height": _format(rect.h + 1000 * (size.y - 1)),
                "rx": _format(rect.r),
                "ry": _format(rect.r),
            },
        )

    def draw_key_top(self, g: et.Element, keytype: KeyType, size: Vector, color: Color) -> None:

        rect = self.top

        width = rect.w + 1000 * (size.x - 1) - 2 * rect.r
        height = rect.h + 1000 * (size.y - 1) - 2 * rect.r

        if keytype == KeyType.SCOOP:
            try:
                depth = self.homing.scoop.depth
            except AttributeError:  # pragma: no cover
                error(ValueError("no scooped homing keys for profile"), file=self.name)
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
                    "x": _format(rect.x),
                    "y": _format(rect.y),
                    "width": _format(rect.w + 1000 * (size.x - 1)),
                    "height": _format(rect.h + 1000 * (size.y - 1)),
                    "rx": _format(rect.r),
                    "ry": _format(rect.r),
                },
            )

        else:
            # curvature of the edges of the key top based on its depth. 0.381 is what "looks right",
            # there's no other magic behind it
            curve = depth * 0.381
            gradtype = GradientType.SCOOP if keytype == KeyType.SCOOP else GradientType.KEY

            if keytype == KeyType.SPACE:

                # radius of the curved edges of either side of the top surface of the spacebar
                vr = (curve ** 2 + (height ** 2 / 4)) / (2 * curve)

                path = (
                    Path()
                    .M(Vector(rect.x, rect.y + rect.r))
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(rect.r, -rect.r))
                    .h(width)
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(rect.r, rect.r))
                    .a(Vector(vr, vr), 0, False, False, Vector(0, height))
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(-rect.r, rect.r))
                    .h(-width)
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(-rect.r, -rect.r))
                    .a(Vector(vr, vr), 0, False, False, Vector(0, -height))
                    .z()
                )
                gradtype = GradientType.SPACE

            elif self.type == ProfileType.CYLINDRICAL:

                # radius of the curved edge at the bottom of the key top rectangle
                hr = (curve ** 2 + (width ** 2 / 4)) / (2 * curve)

                path = (
                    Path()
                    .M(Vector(rect.x, rect.y + rect.r))
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(rect.r, -rect.r))
                    .h(width)
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(rect.r, rect.r))
                    .v(height)
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(-rect.r, rect.r))
                    .a(Vector(hr, hr), 0, False, True, Vector(-width, 0))
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(-rect.r, -rect.r))
                    .z()
                )

            else:  # ProfileType.SPHERICAL

                # radius of the curved edges of the key top rectangle
                width = rect.w - 2 * rect.r
                height = rect.h - 2 * rect.r
                hr = (curve ** 2 + (width ** 2 / 4)) / (2 * curve)
                vr = (curve ** 2 + (height ** 2 / 4)) / (2 * curve)

                path = (
                    Path()
                    .M(Vector(rect.x, rect.y + rect.r))
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(rect.r, -rect.r))
                )
                if size.x > 1:
                    (
                        path.a(Vector(hr, hr), 0, False, True, Vector(width / 2, -curve))
                        .h(1000 * (size.x - 1))
                        .a(Vector(hr, hr), 0, False, True, Vector(width / 2, curve))
                    )
                else:
                    path.a(Vector(hr, hr), 0, False, True, Vector(width, 0))

                path.a(Vector(rect.r, rect.r), 0, False, True, Vector(rect.r, rect.r))

                if size.y > 1:
                    (
                        path.a(Vector(vr, vr), 0, False, True, Vector(curve, height / 2))
                        .v(1000 * (size.y - 1))
                        .a(Vector(vr, vr), 0, False, True, Vector(-curve, height / 2))
                    )
                else:
                    path.a(Vector(vr, vr), 0, False, True, Vector(0, height))

                path.a(Vector(rect.r, rect.r), 0, False, True, Vector(-rect.r, rect.r))

                if size.x > 1:
                    (
                        path.a(Vector(hr, hr), 0, False, True, Vector(-width / 2, curve))
                        .h(-1000 * (size.x - 1))
                        .a(Vector(hr, hr), 0, False, True, Vector(-width / 2, -curve))
                    )
                else:
                    path.a(Vector(hr, hr), 0, False, True, Vector(-width, 0))

                path.a(Vector(rect.r, rect.r), 0, False, True, Vector(-rect.r, -rect.r))

                if size.y > 1:
                    (
                        path.a(Vector(vr, vr), 0, False, True, Vector(-curve, -height / 2))
                        .v(-1000 * (size.y - 1))
                        .a(Vector(vr, vr), 0, False, True, Vector(curve, -height / 2))
                    )
                else:
                    path.a(Vector(vr, vr), 0, False, True, Vector(0, -height))

                path.z()

            et.SubElement(
                g,
                "path",
                {
                    "fill": self.add_gradient(gradtype, color, depth),
                    "stroke": color.highlight().to_hex(),
                    "stroke-width": "10",
                    "d": str(path),
                },
            )

        if size == (1, 1):
            if keytype == KeyType.BAR:

                et.SubElement(
                    g,
                    "rect",
                    {
                        "fill": color.to_hex(),
                        "stroke": color.highlight(0.25).to_hex(),
                        "stroke-width": "10",
                        "x": _format(500 - self.homing.bar.width / 2),
                        "y": _format(500 - self.homing.bar.height / 2 + self.homing.bar.offset),
                        "width": _format(self.homing.bar.width),
                        "height": _format(self.homing.bar.height),
                        "rx": _format(self.homing.bar.height / 2),
                        "ry": _format(self.homing.bar.height / 2),
                    },
                )

            elif keytype == KeyType.BUMP:

                et.SubElement(
                    g,
                    "circle",
                    {
                        "fill": color.to_hex(),
                        "stroke": color.highlight(0.25).to_hex(),
                        "stroke-width": "10",
                        "cx": _format(500),
                        "cy": _format(500 + self.homing.bump.offset),
                        "r": _format(self.homing.bump.radius),
                    },
                )

    def draw_iso_bottom(self, g: et.Element, color: Color) -> None:
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
                    .h(500 + rect.w - 2 * rect.r)
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(rect.r, rect.r))
                    .v(1000 + rect.h - 2 * rect.r)
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(-rect.r, rect.r))
                    .h(-(250 + rect.w - 2 * rect.r))
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(-rect.r, -rect.r))
                    .v(-(1000 - 2 * rect.r))
                    .a(Vector(rect.r, rect.r), 0, False, False, Vector(-rect.r, -rect.r))
                    .h(-(250 - 2 * rect.r))
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(-rect.r, -rect.r))
                    .v(-(rect.h - 2 * rect.r))
                    .z()
                ),
            },
        )

    def draw_iso_top(self, g: et.Element, color: Color) -> None:
        rect = self.top
        curve = self.depth * 0.381

        w_top = rect.w + 500 - 2 * rect.r
        w_btm = rect.w + 250 - 2 * rect.r
        h_lefttop = rect.h - 2 * rect.r
        h_leftbtm = 1000 - curve / 3 - 2 * rect.r
        h_right = rect.h + 1000 - 2 * rect.r

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
                .v(-(1000 - 2 * rect.r))
                .a(Vector(rect.r, rect.r), 0, False, False, Vector(-rect.r, -rect.r))
                .h(-(250 - 2 * rect.r))
                .a(Vector(rect.r, rect.r), 0, False, True, Vector(-rect.r, -rect.r))
                .v(-h_lefttop)
                .z()
            )

        else:

            if self.type == ProfileType.CYLINDRICAL:

                # radius of the curved edge at the bottom of the key top rectangle
                hr = (curve ** 2 + (w_btm ** 2 / 4)) / (2 * curve)

                path = (
                    Path()
                    .M(Vector(rect.x, rect.y + rect.r))
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(rect.r, -rect.r))
                    .h(w_top)
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(rect.r, rect.r))
                    .v(h_right)
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(-rect.r, rect.r))
                    .a(Vector(hr, hr), 0, False, True, Vector(-w_btm, 0))
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(-rect.r, -rect.r))
                    .v(-(h_leftbtm))
                    .a(Vector(rect.r, rect.r), 0, False, False, Vector(-rect.r, -rect.r))
                    .l(Vector(-(250 - 2 * rect.r), -curve / 3))
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(-rect.r, -rect.r))
                    .v(-(h_lefttop))
                    .z()
                )

            else:  # ProfileType.SPHERICAL

                # radius of the curved edges of the key top rectangle
                width = rect.w - 2 * rect.r
                height = rect.h - 2 * rect.r
                hr = (curve ** 2 + (width ** 2 / 4)) / (2 * curve)
                vr = (curve ** 2 + (height ** 2 / 4)) / (2 * curve)

                h_leftbtm = 1000 - curve / 2 - 2 * rect.r

                path = (
                    Path()
                    .M(Vector(rect.x, rect.y + rect.r))
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(rect.r, -rect.r))
                    .a(Vector(hr, hr), 0, False, True, Vector(width / 2, -curve))
                    .h(500)
                    .a(Vector(hr, hr), 0, False, True, Vector(width / 2, curve))
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(rect.r, rect.r))
                    .a(Vector(vr, vr), 0, False, True, Vector(curve, height / 2))
                    .v(1000)
                    .a(Vector(vr, vr), 0, False, True, Vector(-curve, height / 2))
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(-rect.r, rect.r))
                    .a(Vector(hr, hr), 0, False, True, Vector(-width / 2, curve))
                    .h(-250)
                    .a(Vector(hr, hr), 0, False, True, Vector(-width / 2, -curve))
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(-rect.r, -rect.r))
                    .a(Vector(vr, vr), 0, False, True, Vector(-curve, -height / 2))
                    .v(-(h_leftbtm - height / 2))
                    .a(Vector(rect.r, rect.r), 0, False, False, Vector(-rect.r, -rect.r))
                    .l(Vector(-(250 - 2 * rect.r - curve), -curve / 2))
                    .a(Vector(rect.r, rect.r), 0, False, True, Vector(-rect.r, -rect.r))
                    .a(Vector(vr, vr), 0, False, True, Vector(0, -h_lefttop))
                    .z()
                )

        et.SubElement(
            g,
            "path",
            {
                "fill": self.add_gradient(GradientType.KEY, color, self.depth),
                "stroke": color.highlight().to_hex(),
                "stroke-width": "10",
                "d": str(path),
            },
        )

    def draw_step(self, g: et.Element, color: Color) -> None:
        top = self.top
        btm = self.bottom

        rect = RoundRect(
            1250 - (top.x + btm.x) / 2,
            (top.y + btm.y) / 2,
            500,
            (top.h + btm.h) / 2,
            (top.r + btm.r) / 2,
        )

        et.SubElement(
            g,
            "path",
            {
                "fill": self.add_gradient(GradientType.SPACE, color, self.depth),
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
                ),
            },
        )

    def add_gradient(self, gradtype: GradientType, color: Color, depth: float) -> str:

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
                color.lighter(min(1, depth / 525)),
                color,
                color.darker(min(1, depth / 525)),
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
def _format(num: float) -> str:
    return f"{float(num):.3f}".rstrip("0").rstrip(".")
