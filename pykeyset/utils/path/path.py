# -*- coding: utf-8 -*-

import re
from math import cos, radians, sin, tan

from ..types import Rect, Union, Vector
from .arc_to_bezier import arc_to_bezier
from .segment import ClosePath, CubicBezier, Line, Move, QuadraticBezier


class Path:
    def __init__(self, d: str = "") -> None:

        token = iter(
            t
            for t in re.split(r"(-?\d+\.?\d*|[A-Za-z])", d)
            if len(t.strip()) > 0 and t.strip() != ","
        )

        self.point = Vector(0, 0)
        self.d = []
        self._bbox = None
        self.bboxoverride = False

        for t in token:
            try:
                if t.startswith("m"):
                    d = Vector(float(next(token)), float(next(token)))
                    self.m(d)

                elif t.startswith("M"):
                    d = Vector(float(next(token)), float(next(token)))
                    self.M(d)

                elif t.startswith("l"):
                    d = Vector(float(next(token)), float(next(token)))
                    self.l(d)

                elif t.startswith("L"):
                    d = Vector(float(next(token)), float(next(token)))
                    self.L(d)

                elif t.startswith("h"):
                    x = float(next(token))
                    self.h(x)

                elif t.startswith("H"):
                    x = float(next(token))
                    self.H(x)

                elif t.startswith("v"):
                    y = float(next(token))
                    self.v(y)

                elif t.startswith("V"):
                    y = float(next(token))
                    self.V(y)

                elif t.startswith("c"):
                    d1 = Vector(float(next(token)), float(next(token)))
                    d2 = Vector(float(next(token)), float(next(token)))
                    d = Vector(float(next(token)), float(next(token)))
                    self.c(d1, d2, d)

                elif t.startswith("C"):
                    d1 = Vector(float(next(token)), float(next(token)))
                    d2 = Vector(float(next(token)), float(next(token)))
                    d = Vector(float(next(token)), float(next(token)))
                    self.C(d1, d2, d)

                elif t.startswith("s"):
                    d2 = Vector(float(next(token)), float(next(token)))
                    d = Vector(float(next(token)), float(next(token)))
                    self.s(d2, d)

                elif t.startswith("S"):
                    d2 = Vector(float(next(token)), float(next(token)))
                    d = Vector(float(next(token)), float(next(token)))
                    self.S(d2, d)

                elif t.startswith("q"):
                    d1 = Vector(float(next(token)), float(next(token)))
                    d = Vector(float(next(token)), float(next(token)))
                    self.q(d1, d)

                elif t.startswith("Q"):
                    d1 = Vector(float(next(token)), float(next(token)))
                    d = Vector(float(next(token)), float(next(token)))
                    self.Q(d1, d)

                elif t.startswith("t"):
                    d = Vector(float(next(token)), float(next(token)))
                    self.t(d)

                elif t.startswith("T"):
                    d = Vector(float(next(token)), float(next(token)))
                    self.T(d)

                elif t.startswith("a"):
                    r = Vector(abs(float(next(token))), abs(float(next(token))))
                    xar = float(next(token))
                    laf = float(next(token)) > 0.5  # Use 0.5 as a threshold between True and False
                    sf = float(next(token)) > 0.5
                    d = Vector(float(next(token)), float(next(token)))
                    self.a(r, xar, laf, sf, d)

                elif t.startswith("A"):
                    r = Vector(abs(float(next(token))), abs(float(next(token))))
                    xar = float(next(token))
                    laf = float(next(token)) > 0.5  # Use 0.5 as a threshold between True and False
                    sf = float(next(token)) > 0.5
                    d = Vector(float(next(token)), float(next(token)))
                    self.A(r, xar, laf, sf, d)

                elif t.startswith("z"):
                    self.z()

                elif t.startswith("Z"):
                    self.Z()

                else:
                    raise ValueError(f"invalid path command '{t}'")

            except (StopIteration, ValueError):
                raise ValueError("invalid path")

        # Add the origin to the bounding box if we don't have an explicit move
        if len(self.d) > 0 and not isinstance(self.d[0], Move):
            self._updatebbox(Vector(0, 0))

    def __repr__(self) -> str:
        return "".join(str(d) for d in self.d)

    def append(self, other: "Path") -> "Path":
        if not other.d:
            return self

        if other._bbox is None:
            other._recalculatebbox()
            if other._bbox is None:
                raise ValueError(
                    "bounding box of path is None even though path is not empty. This should not "
                    "happen"
                )  # pragma: no cover
        self._updatebbox(other._bbox.position)
        self._updatebbox(other._bbox.position + other._bbox.size)
        self.d.extend(other.d[:])
        self.point = other.point
        return self

    def setboundingbox(self, bbox: Rect) -> None:
        self._bbox = bbox
        self.bboxoverride = True

    def copy(self) -> "Path":
        result = Path()
        result.point = self.point
        result.d = self.d[:]
        result._bbox = self._bbox
        result.bboxoverride = self.bboxoverride
        return result

    @property
    def boundingbox(self) -> Rect:
        """Return the bounding box of the path"""
        return self._bbox if self._bbox is not None else Rect(0, 0, 0, 0)

    def _rel(self, d: Vector) -> Vector:
        """Convert an absolute position d to a relative distance"""
        return d - self.point

    def _abs(self, d: Vector) -> Vector:
        """Convert a relative distance d to an absolute position"""
        return d + self.point

    def m(self, d: Vector) -> "Path":
        """SVG m path command"""
        return self.M(self._abs(d))

    # flake8 doesn't like the lowercase l, even though the rest are fine, so disable E741 & E743
    def l(self, d: Vector) -> "Path":  # noqa: E741, E743
        """SVG l path command"""
        self.d.append(Line(d))
        self.point = self.point + d
        self._updatebbox(self.point)
        return self

    def h(self, x: float) -> "Path":
        """SVG h path command"""
        return self.l(Vector(x, 0))

    def v(self, y: float) -> "Path":
        """SVG v path command"""
        return self.l(Vector(0, y))

    def c(self, d1: Vector, d2: Vector, d: Vector) -> "Path":
        """SVG c path command"""
        self.d.append(CubicBezier(d1, d2, d))
        self.point = self.point + d
        self._updatebbox(self.point)
        return self

    def s(self, d2: Vector, d: Vector) -> "Path":
        """SVG s path command"""
        last = self.d[-1] if len(self.d) > 0 else None
        if isinstance(last, CubicBezier):
            d1 = last.point - last.ctrl2
            self.d.append(CubicBezier(d1, d2, d))
        else:
            self.d.append(QuadraticBezier(d2, d))
        self.point = self.point + d
        self._updatebbox(self.point)
        return self

    def q(self, d1: Vector, d: Vector) -> "Path":
        """SVG q path command"""
        self.d.append(QuadraticBezier(d1, d))
        self.point = self.point + d
        self._updatebbox(self.point)
        return self

    def t(self, d: Vector) -> "Path":
        """SVG t path command"""
        last = self.d[-1] if len(self.d) > 0 else None
        if isinstance(last, QuadraticBezier):
            d1 = last.point - last.ctrl
            self.d.append(QuadraticBezier(d1, d))
        else:
            self.d.append(Line(d))
        self.point = self.point + d
        self._updatebbox(self.point)
        return self

    def a(self, r: Vector, xar: float, laf: bool, sf: bool, d: Vector) -> "Path":
        """SVG a path command"""
        for d1, d2, d in arc_to_bezier(r, xar, laf, sf, d):
            self.c(d1, d2, d)
        return self

    def z(self) -> "Path":
        """SVG z path command"""
        self.d.append(ClosePath())
        lastm = next((s for s in self.d[::-1] if isinstance(s, Move)), None)
        if lastm is not None:
            self.point = lastm.point
        else:
            self.point = Vector(0, 0)
        self._updatebbox(self.point)
        return self

    def M(self, d: Vector) -> "Path":
        """SVG M path command"""
        self.d.append(Move(d))
        self.point = d
        self._updatebbox(self.point)
        return self

    def L(self, d: Vector) -> "Path":
        """SVG L path command"""
        return self.l(self._rel(d))

    def H(self, x: float) -> "Path":
        """SVG H path command"""
        return self.h(x - self.point.x)

    def V(self, y: float) -> "Path":
        """SVG V path command"""
        return self.v(y - self.point.y)

    def C(self, d1: Vector, d2: Vector, d: Vector) -> "Path":
        """SVG C path command"""
        return self.c(self._rel(d1), self._rel(d2), self._rel(d))

    def S(self, d2: Vector, d: Vector) -> "Path":
        """SVG S path command"""
        return self.s(self._rel(d2), self._rel(d))

    def Q(self, d1: Vector, d: Vector) -> "Path":
        """SVG Q path command"""
        return self.q(self._rel(d1), self._rel(d))

    def T(self, d: Vector) -> "Path":
        """SVG T path command"""
        return self.t(self._rel(d))

    def A(self, r: Vector, xar: float, laf: float, sf: float, d: Vector) -> "Path":
        """SVG A path command"""
        return self.a(r, xar, laf, sf, self._rel(d))

    def Z(self) -> "Path":
        """SVG Z path command"""
        return self.z()

    def transform(self, trns: str) -> None:
        trns = re.sub(r",\s+", ",", trns).split()[::-1]

        for t in trns:
            try:
                if t.startswith("scale("):
                    val = [float(v) for v in t[6:-1].split(",", 1)]
                    s = Vector(val[0], val[1] if len(val) > 1 else val[0])
                    self.scale(s)

                elif t.startswith("translate("):
                    val = [float(v) for v in t[10:-1].split(",", 1)]
                    d = Vector(val[0], val[1] if len(val) > 1 else 0)
                    self.translate(d)

                elif t.startswith("rotate("):
                    val = float(t[7:-1])
                    self.rotate(val)

                elif t.startswith("skewX("):
                    val = float(t[6:-1])
                    self.skew_x(val)

                elif t.startswith("skewY("):
                    val = float(t[6:-1])
                    self.skew_y(val)

                else:
                    raise ValueError(f"unsupported transform '{t.split('(')[0]}'")

            except (ValueError, IndexError):
                raise ValueError("invalid transform")

    def scale(self, s: Union[float, "Vector"]) -> "Path":
        for i, seg in enumerate(self.d):
            self.d[i] = seg.scale(s)
        self.point = self.point * s
        if self._bbox is not None:
            self._bbox = self._bbox.scale(s)
        return self

    def translate(self, d: Vector) -> "Path":
        for i, seg in enumerate(self.d):
            self.d[i] = seg.translate(d)
        self.point = self.point + d
        if self._bbox is not None:
            self._bbox = self._bbox._replace(x=self._bbox.x + d.x, y=self._bbox.y + d.y)
        return self

    def rotate(self, t: float) -> "Path":
        for i, seg in enumerate(self.d):
            self.d[i] = seg.rotate(t)
        c, s = cos(radians(t)), sin(radians(t))
        x, y = self.point
        self.point = Vector(x * c - y * s, x * s + y * c)
        self._recalculatebbox()
        return self

    def skew_x(self, t: float) -> "Path":
        for i, seg in enumerate(self.d):
            self.d[i] = seg.skew_x(t)
        self.point = self.point._replace(x=self.point.x - self.point.y * tan(radians(t)))
        self._recalculatebbox()
        return self

    def skew_y(self, t: float) -> "Path":
        for i, seg in enumerate(self.d):
            self.d[i] = seg.skew_y(t)
        self.point = self.point._replace(y=self.point.y + self.point.x * tan(radians(t)))
        self._recalculatebbox()
        return self

    def _recalculatebbox(self) -> None:
        if self.bboxoverride:
            raise ValueError("cannot recalculate bounding box that has been previously overridden")
        elif len(self.d) == 0:
            self._bbox = None
        else:
            # Make sure the d starts with a move
            if not isinstance(self.d[0], Move):
                d = [Move(Vector(0, 0))] + self.d
            else:
                d = self.d
            # Get the starting point of the path
            start = d[0].point
            # Preallocate points
            points = [None] * len(d)
            points[0] = start

            for i, seg in enumerate(d[1:], 1):
                if isinstance(seg, Move):
                    start = seg.point
                    points[i] = start
                elif isinstance(seg, ClosePath):
                    points[i] = start
                else:
                    points[i] = points[i - 1] + seg.point

            minpt = Vector(*(min(d) for d in zip(*points)))
            maxpt = Vector(*(max(d) for d in zip(*points)))
            self._bbox = Rect(*minpt, *(maxpt - minpt))

    def _updatebbox(self, point: Vector) -> None:
        if self._bbox is None:
            self._bbox = Rect(*point, 0, 0)
        else:
            pt1 = self._bbox.position
            pt2 = self._bbox.position + self._bbox.size
            pt1, pt2 = (
                Vector(min(pt1.x, point.x), min(pt1.y, point.y)),
                Vector(max(pt2.x, point.x), max(pt2.y, point.y)),
            )
            self._bbox = Rect(*pt1, *(pt2 - pt1))
