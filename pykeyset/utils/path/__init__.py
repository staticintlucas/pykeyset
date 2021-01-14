# -*- coding: utf-8 -*-

import re
from copy import deepcopy
from math import cos, inf, radians, sin, tan

from ..error import error
from ..types import Rect, Vector
from .arc_to_bezier import arc_to_bezier


class Path:
    def __init__(self, d=""):

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
                    error(f"invalid path command '{t}'")

            except (StopIteration, ValueError):
                error("invalid path")

    def __repr__(self):
        return "".join(str(d) for d in self.d)

    def append(self, other):
        if not other.d:
            return self

        if other._bbox is None:
            other._recalculatebbox()
            if other._bbox is None:
                error(
                    "bounding box of path is None even though path is not empty. This should not "
                    "happen"
                )  # pragma: no cover
        self._updatebbox(other._bbox.position)
        self._updatebbox(other._bbox.position + other._bbox.size)
        self.d.extend(deepcopy(other.d))
        self.point = other.point
        return self

    def setboundingbox(self, bbox):
        self._bbox = bbox
        self.bboxoverride = True

    def copy(self):
        return deepcopy(self)

    @property
    def boundingbox(self):
        """Return the bounding box of the path"""
        return self._bbox if self._bbox is not None else Rect(0, 0, 0, 0)

    def _rel(self, d):
        """Convert an absolute position d to a relative distance"""
        return d - self.point

    def _abs(self, d):
        """Convert a relative distance d to an absolute position"""
        return d + self.point

    def m(self, d):
        """SVG m path command"""
        return self.M(self._abs(d))

    # flake8 doesn't like the lowercase l, even though the rest are fine, so disable E741 & E743
    def l(self, d):  # noqa: E741, E743
        """SVG l path command"""
        self.d.append(_l(d))
        self.point = self.point + d
        self._updatebbox(self.point)
        return self

    def h(self, x):
        """SVG h path command"""
        return self.l(Vector(x, 0))

    def v(self, y):
        """SVG v path command"""
        return self.l(Vector(0, y))

    def c(self, d1, d2, d):
        """SVG c path command"""
        self.d.append(_c(d1, d2, d))
        self.point = self.point + d
        self._updatebbox(self.point)
        return self

    def s(self, d2, d):
        """SVG s path command"""
        last = self.d[-1] if len(self.d) > 0 else None
        if isinstance(last, _c):
            d1 = last.d - last.d2
            self.d.append(_c(d1, d2, d))
        else:
            self.d.append(_q(d2, d))
        self.point = self.point + d
        self._updatebbox(self.point)
        return self

    def q(self, d1, d):
        """SVG q path command"""
        self.d.append(_q(d1, d))
        self.point = self.point + d
        self._updatebbox(self.point)
        return self

    def t(self, d):
        """SVG t path command"""
        last = self.d[-1] if len(self.d) > 0 else None
        if isinstance(last, _q):
            d1 = last.d - last.d1
            self.d.append(_q(d1, d))
        else:
            self.d.append(_l(d))
        self.point = self.point + d
        self._updatebbox(self.point)
        return self

    def a(self, r, xar, laf, sf, d):
        """SVG a path command"""
        for d1, d2, d in arc_to_bezier(r, xar, laf, sf, d):
            self.c(d1, d2, d)
        return self

    def z(self):
        """SVG z path command"""
        self.d.append(_z())
        lastm = next((s for s in self.d[::-1] if isinstance(s, _M)), None)
        if lastm is not None:
            self.point = lastm.d
        else:
            self.point = Vector(0, 0)
        self._updatebbox(self.point)
        return self

    def M(self, d):
        """SVG M path command"""
        self.d.append(_M(d))
        self.point = d
        self._updatebbox(self.point)
        return self

    def L(self, d):
        """SVG L path command"""
        return self.l(self._rel(d))

    def H(self, x):
        """SVG H path command"""
        return self.h(x - self.point.x)

    def V(self, y):
        """SVG V path command"""
        return self.v(y - self.point.y)

    def C(self, d1, d2, d):
        """SVG C path command"""
        return self.c(self._rel(d1), self._rel(d2), self._rel(d))

    def S(self, d2, d):
        """SVG S path command"""
        return self.s(self._rel(d2), self._rel(d))

    def Q(self, d1, d):
        """SVG Q path command"""
        return self.q(self._rel(d1), self._rel(d))

    def T(self, d):
        """SVG T path command"""
        return self.t(self._rel(d))

    def A(self, r, xar, laf, sf, d):
        """SVG A path command"""
        return self.a(r, xar, laf, sf, self._rel(d))

    def Z(self):
        """SVG Z path command"""
        return self.z()

    def transform(self, trns):
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
                    error(f"unsupported transform '{t.split('(')[0]}'")

            except (ValueError, IndexError):
                error("invalid transform")

    def scale(self, s):
        for seg in self.d:
            seg.scale(s)
        self.point = Vector(self.point.x * s.x, self.point.y * s.y)
        if self._bbox is not None:
            self._bbox = Rect(
                self._bbox.x * s.x,
                self._bbox.y * s.y,
                self._bbox.w * s.x,
                self._bbox.h * s.y,
            )
            if self._bbox.w < 0:
                self._bbox = self._bbox._replace(
                    x=self._bbox.x + self._bbox.w,
                    w=-self._bbox.w,
                )
            if self._bbox.h < 0:
                self._bbox = self._bbox._replace(
                    y=self._bbox.y + self._bbox.h,
                    h=-self._bbox.h,
                )
        return self

    def translate(self, d):
        for seg in self.d:
            seg.translate(d)
        self.point = self.point + d
        if self._bbox is not None:
            self._bbox = self._bbox._replace(x=self._bbox.x + d.x, y=self._bbox.y + d.y)
        return self

    def rotate(self, t):
        for seg in self.d:
            seg.rotate(t)
        c, s = cos(radians(t)), sin(radians(t))
        x, y = self.point
        self.point = Vector(x * c - y * s, x * s + y * c)
        self._recalculatebbox()
        return self

    def skew_x(self, t):
        for seg in self.d:
            seg.skew_x(t)
        self.point = self.point._replace(x=self.point.x - self.point.y * tan(radians(t)))
        self._recalculatebbox()
        return self

    def skew_y(self, t):
        for seg in self.d:
            seg.skew_y(t)
        self.point = self.point._replace(y=self.point.y + self.point.x * tan(radians(t)))
        self._recalculatebbox()
        return self

    def _recalculatebbox(self):
        if self.bboxoverride:
            raise ValueError("cannot recalculate bounding box that has been previously overridden")
        elif len(self.d) == 0:
            self._bbox = None
        else:
            minpt = Vector(inf, inf)
            maxpt = Vector(-inf, -inf)

            pt = Vector(0, 0)
            start = pt
            for seg in self.d:
                if isinstance(seg, _M):
                    pt = seg.d
                    start = pt
                elif isinstance(seg, _z):
                    pt = start
                else:
                    pt = pt + seg.d
                minpt = Vector(min(minpt.x, pt.x), min(minpt.y, pt.y))
                maxpt = Vector(max(maxpt.x, pt.x), max(maxpt.y, pt.y))
            self._bbox = Rect(*minpt, *(maxpt - minpt))

    def _updatebbox(self, point):
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


# Absolute move
class _M:
    def __init__(self, d):
        self.d = d

    def __repr__(self):
        return f"M{format_coords(self.d)}"

    def scale(self, s):
        self.d = Vector(self.d.x * s.x, self.d.y * s.y)

    def translate(self, d):
        self.d = self.d + d

    def rotate(self, t):
        t = radians(t)
        x, y = self.d
        self.d = Vector(x * cos(t) - y * sin(t), x * sin(t) + y * cos(t))

    def skew_x(self, t):
        t = radians(t)
        self.d = self.d._replace(x=self.d.x - self.d.y * tan(t))

    def skew_y(self, t):
        t = radians(t)
        self.d = self.d._replace(y=self.d.y + self.d.x * tan(t))


# Relative line
class _l:
    def __init__(self, d):
        self.d = d

    def __repr__(self):
        return f"l{format_coords(self.d)}"

    def scale(self, s):
        self.d = Vector(self.d.x * s.x, self.d.y * s.y)

    def translate(self, d):
        pass  # Do nothing since this is a relative distance

    def rotate(self, t):
        t = radians(t)
        x, y = self.d.x, self.d.y
        self.d = Vector(x * cos(t) - y * sin(t), x * sin(t) + y * cos(t))

    def skew_x(self, t):
        t = radians(t)
        self.d = self.d._replace(x=self.d.x - self.d.y * tan(t))

    def skew_y(self, t):
        t = radians(t)
        self.d = self.d._replace(y=self.d.y + self.d.x * tan(t))


# Relative cubic Bézier
class _c:
    def __init__(self, d1, d2, d):
        self.d1 = d1
        self.d2 = d2
        self.d = d

    def __repr__(self):
        return f"c{format_coords(self.d1, self.d2, self.d)}"

    def scale(self, s):
        self.d1 = Vector(self.d1.x * s.x, self.d1.y * s.y)
        self.d2 = Vector(self.d2.x * s.x, self.d2.y * s.y)
        self.d = Vector(self.d.x * s.x, self.d.y * s.y)

    def translate(self, d):
        pass  # Do nothing since this is a relative distance

    def rotate(self, t):
        t = radians(t)
        x1, y1, x2, y2, x, y = self.d1.x, self.d1.y, self.d2.x, self.d2.y, self.d.x, self.d.y
        self.d1 = Vector(x1 * cos(t) - y1 * sin(t), x1 * sin(t) + y1 * cos(t))
        self.d2 = Vector(x2 * cos(t) - y2 * sin(t), x2 * sin(t) + y2 * cos(t))
        self.d = Vector(x * cos(t) - y * sin(t), x * sin(t) + y * cos(t))

    def skew_x(self, t):
        t = radians(t)
        self.d1 = self.d1._replace(x=self.d1.x - self.d1.y * tan(t))
        self.d2 = self.d2._replace(x=self.d2.x - self.d2.y * tan(t))
        self.d = self.d._replace(x=self.d.x - self.d.y * tan(t))

    def skew_y(self, t):
        t = radians(t)
        self.d1 = self.d1._replace(y=self.d1.y + self.d1.x * tan(t))
        self.d2 = self.d2._replace(y=self.d2.y + self.d2.x * tan(t))
        self.d = self.d._replace(y=self.d.y + self.d.x * tan(t))


# Relative quadratic Bézier
class _q:
    def __init__(self, d1, d):
        self.d1 = d1
        self.d = d

    def __repr__(self):
        return f"q{format_coords(self.d1, self.d)}"

    def scale(self, s):
        self.d1 = Vector(self.d1.x * s.x, self.d1.y * s.y)
        self.d = Vector(self.d.x * s.x, self.d.y * s.y)

    def translate(self, d):
        pass  # Do nothing since this is a relative distance

    def rotate(self, t):
        t = radians(t)
        x1, y1, x, y = self.d1.x, self.d1.y, self.d.x, self.d.y
        self.d1 = Vector(x1 * cos(t) - y1 * sin(t), x1 * sin(t) + y1 * cos(t))
        self.d = Vector(x * cos(t) - y * sin(t), x * sin(t) + y * cos(t))

    def skew_x(self, t):
        t = radians(t)
        self.d1 = self.d1._replace(x=self.d1.x - self.d1.y * tan(t))
        self.d = self.d._replace(x=self.d.x - self.d.y * tan(t))

    def skew_y(self, t):
        t = radians(t)
        self.d1 = self.d1._replace(y=self.d1.y + self.d1.x * tan(t))
        self.d = self.d._replace(y=self.d.y + self.d.x * tan(t))


# z
class _z:
    def __init__(self):
        pass

    def __repr__(self):
        return "z"

    def scale(self, s):
        pass

    def translate(self, d):
        pass

    def rotate(self, t):
        pass

    def skew_x(self, t):
        pass

    def skew_y(self, t):
        pass


# Format a list of coords as efficiently as possible
def format_coords(*args):
    coords = [a for arg in args for a in arg]
    return "".join(f"{float(c): .3f}".rstrip("0").rstrip(".") for c in coords).lstrip()
