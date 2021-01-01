# coding: utf-8

import re
from math import cos, sin, radians, inf
from copy import deepcopy

from ..error import error
from ..types import Point, Dist, Rect
from .arc_to_bezier import arc_to_bezier


class Path:
    def __init__(self, d=""):

        token = iter(
            t
            for t in re.split(r"(-?\d+\.?\d*|[A-Za-z])", d)
            if len(t) > 0 and not t.isspace() and not t == ","
        )

        self.point = Point(0, 0)
        self.d = []

        for t in token:
            try:
                if t.startswith("m"):
                    d = Point(float(next(token)), float(next(token)))
                    self.m(d)

                elif t.startswith("M"):
                    d = Point(float(next(token)), float(next(token)))
                    self.M(d)

                elif t.startswith("l"):
                    d = Point(float(next(token)), float(next(token)))
                    self.l(d)

                elif t.startswith("L"):
                    d = Point(float(next(token)), float(next(token)))
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
                    d1 = Point(float(next(token)), float(next(token)))
                    d2 = Point(float(next(token)), float(next(token)))
                    d = Point(float(next(token)), float(next(token)))
                    self.c(d1, d2, d)

                elif t.startswith("C"):
                    d1 = Point(float(next(token)), float(next(token)))
                    d2 = Point(float(next(token)), float(next(token)))
                    d = Point(float(next(token)), float(next(token)))
                    self.C(d1, d2, d)

                elif t.startswith("s"):
                    d2 = Point(float(next(token)), float(next(token)))
                    d = Point(float(next(token)), float(next(token)))
                    self.s(d2, d)

                elif t.startswith("S"):
                    d2 = Point(float(next(token)), float(next(token)))
                    d = Point(float(next(token)), float(next(token)))
                    self.s(d2, d)

                elif t.startswith("q"):
                    d1 = Point(float(next(token)), float(next(token)))
                    d = Point(float(next(token)), float(next(token)))
                    self.q(d1, d)

                elif t.startswith("Q"):
                    d1 = Point(float(next(token)), float(next(token)))
                    d = Point(float(next(token)), float(next(token)))
                    self.Q(d1, d)

                elif t.startswith("t"):
                    d = Point(float(next(token)), float(next(token)))
                    self.t(d)

                elif t.startswith("T"):
                    d = Point(float(next(token)), float(next(token)))
                    self.T(d)

                elif t.startswith("a"):
                    r = Dist(abs(float(next(token))), abs(float(next(token))))
                    xar = float(next(token))
                    laf = float(next(token)) > 0.5  # Use 0.5 as a threshold between True and False
                    sf = float(next(token)) > 0.5
                    d = Point(float(next(token)), float(next(token)))
                    self.a(r, xar, laf, sf, d)

                elif t.startswith("A"):
                    r = Dist(abs(float(next(token))), abs(float(next(token))))
                    xar = float(next(token))
                    laf = float(next(token)) > 0.5  # Use 0.5 as a threshold between True and False
                    sf = float(next(token)) > 0.5
                    d = Point(float(next(token)), float(next(token)))
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
        self.d.extend(deepcopy(other.d))
        self.point = Point(*other.point)
        return self

    def copy(self):
        return deepcopy(self)

    def rect(self):
        """Return the bounding box of the path"""
        minpt = Point(inf, inf)
        maxpt = Point(-inf, -inf)

        if len(self.d) == 0:
            return Rect(0, 0, 0, 0)
        else:
            pt = Point(0, 0)
            start = Point(*pt)
            for seg in self.d:
                if isinstance(seg, _M):
                    pt = Point(*seg.d)
                    start = Point(*pt)
                elif isinstance(seg, _z):
                    pt = Point(*start)
                else:
                    pt.x += seg.d.x
                    pt.y += seg.d.y
                minpt = Point(min(minpt.x, pt.x), min(minpt.y, pt.y))
                maxpt = Point(max(maxpt.x, pt.x), max(maxpt.y, pt.y))
        return Rect(minpt.x, minpt.y, maxpt.x - minpt.x, maxpt.y - minpt.y)

    def rel(self, d):
        """Convert an absolute position d to a relative distance"""
        return Point(d.x - self.point.x, d.y - self.point.y)

    def abs(self, d):
        """Convert a relative distance d to an absolute position"""
        return Point(d.x + self.point.x, d.y + self.point.y)

    def m(self, d):
        """SVG m path command"""
        return self.M(self.abs(d))

    def l(self, d):
        """SVG l path command"""
        self.d.append(_l(d))
        self.point.x += d.x
        self.point.y += d.y
        return self

    def h(self, x):
        """SVG h path command"""
        self.d.append(_l(Point(x, 0)))
        self.point.x += x
        return self

    def v(self, y):
        """SVG v path command"""
        self.d.append(_l(Point(0, y)))
        self.point.y += y
        return self

    def c(self, d1, d2, d):
        """SVG c path command"""
        self.d.append(_c(d1, d2, d))
        self.point.x += d.x
        self.point.y += d.y
        return self

    def s(self, d2, d):
        """SVG s path command"""
        last = self.d[-1] if len(self.d) > 0 else None
        if isinstance(last, _c):
            x1 = last.d.x - last.d2.x
            y1 = last.d.y - last.d2.y
            self.d.append(_c(Point(x1, y1), d2, d))
        else:
            self.d.append(_q(d2, d))
        self.point.x += d.x
        self.point.y += d.y
        return self

    def q(self, d1, d):
        """SVG q path command"""
        self.d.append(_q(d1, d))
        self.point.x += d.x
        self.point.y += d.y
        return self

    def t(self, d):
        """SVG t path command"""
        last = self.d[-1] if len(self.d) > 0 else None
        if isinstance(last, _q):
            x1 = last.d.x - last.d1.x
            y1 = last.d.y - last.d1.y
            self.d.append(_q(Point(x1, y1), d))
        else:
            self.d.append(_l(d))
        self.point.x += d.x
        self.point.y += d.y
        return self

    def a(self, r, xar, laf, sf, d):
        """SVG a path command"""
        for d1, d2, d in arc_to_bezier(r, xar, laf, sf, d):
            self.d.append(_c(d1, d2, d))
        self.point.x += d.x
        self.point.y += d.y
        return self

    def z(self):
        """SVG z path command"""
        self.d.append(_z())
        lastm = next((s for s in self.d[::-1] if isinstance(s, _M)), None)
        if lastm is not None:
            self.point = Point(*lastm.d)
        else:
            self.point = Point(0, 0)
        return self

    def M(self, d):
        """SVG M path command"""
        self.d.append(_M(d))
        self.point = Point(*d)
        return self

    def L(self, d):
        """SVG L path command"""
        return self.l(self.rel(d))

    def H(self, x):
        """SVG H path command"""
        return self.h(x - self.point.x)

    def V(self, y):
        """SVG V path command"""
        return self.v(y - self.point.y)

    def C(self, d1, d2, d):
        """SVG C path command"""
        return self.c(self.rel(d1), self.rel(d2), self.rel(d))

    def S(self, d2, d):
        """SVG S path command"""
        return self.s(self.rel(d2), self.rel(d))

    def Q(self, d1, d):
        """SVG Q path command"""
        return self.q(self.rel(d1), self.rel(d))

    def T(self, d):
        """SVG T path command"""
        return self.t(self.rel(d))

    def A(self, r, xar, laf, sf, d):
        """SVG A path command"""
        return self.a(r, xar, laf, sf, self.rel(d))

    def Z(self):
        """SVG Z path command"""
        return self.z()

    def transform(self, trns):
        trns = re.sub(r",\s+", ",", trns).split()[::-1]

        for t in trns:
            try:
                if t.startswith("scale("):
                    val = [float(v) for v in t[6:-1].split(",")]
                    s = Dist(val[0], val[1] if len(val) > 1 else val[0])
                    self.scale(s)

                elif t.startswith("translate("):
                    val = [float(v) for v in t[10:-1].split(",")]
                    d = Dist(val[0], val[1])
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
        self.point.x *= s.x
        self.point.y *= s.y
        return self

    def translate(self, d):
        for seg in self.d:
            seg.translate(d)
        self.point.x += d.x
        self.point.y += d.y
        return self

    def rotate(self, t):
        for seg in self.d:
            seg.rotate(t)
        c, s = cos(radians(t)), sin(radians(t))
        x, y = self.point
        self.point = Point(x * c - y * s, x * s + y * c)
        return self

    def skew_x(self, t):
        for seg in self.d:
            seg.skew_x(t)
        self.point.x -= self.point.y * sin(radians(t))
        return self

    def skew_y(self, t):
        for seg in self.d:
            seg.skew_y(t)
        self.point.y += self.point.x * sin(radians(t))
        return self


# Absolute move
class _M:
    def __init__(self, d):
        self.d = Point(*d)

    def __repr__(self):
        return "M{0:s}".format(_format(self.d.x, self.d.y))

    def scale(self, s):
        self.d.x *= s.x
        self.d.y *= s.y

    def translate(self, d):
        self.d.x += d.x
        self.d.y += d.y

    def rotate(self, t):
        t = radians(t)
        x, y = self.d.x, self.d.y
        self.d = Point(x * cos(t) - y * sin(t), x * sin(t) + y * cos(t))

    def skew_x(self, t):
        t = radians(t)
        self.d.x -= self.d.y * sin(t)

    def skew_y(self, t):
        t = radians(t)
        self.d.y += self.d.x * sin(t)


# Relative line
class _l:
    def __init__(self, d):
        self.d = Point(*d)

    def __repr__(self):
        return "l{0:s}".format(_format(self.d.x, self.d.y))

    def scale(self, s):
        self.d.x *= s.x
        self.d.y *= s.y

    def translate(self, d):
        pass  # Do nothing since this is a relative distance

    def rotate(self, t):
        t = radians(t)
        x, y = self.d.x, self.d.y
        self.d = Point(x * cos(t) - y * sin(t), x * sin(t) + y * cos(t))

    def skew_x(self, t):
        t = radians(t)
        self.d.x -= self.d.y * sin(t)

    def skew_y(self, t):
        t = radians(t)
        self.d.y += self.d.x * sin(t)


# Relative cubic Bézier
class _c:
    def __init__(self, d1, d2, d):
        self.d1 = Point(*d1)
        self.d2 = Point(*d2)
        self.d = Point(*d)

    def __repr__(self):
        return "c{0:s}".format(
            _format(self.d1.x, self.d1.y, self.d2.x, self.d2.y, self.d.x, self.d.y)
        )

    def scale(self, s):
        self.d1.x *= s.x
        self.d1.y *= s.y
        self.d2.x *= s.x
        self.d2.y *= s.y
        self.d.x *= s.x
        self.d.y *= s.y

    def translate(self, d):
        pass  # Do nothing since this is a relative distance

    def rotate(self, t):
        t = radians(t)
        x1, y1, x2, y2, x, y = self.d1.x, self.d1.y, self.d2.x, self.d2.y, self.d.x, self.d.y
        self.d1 = Point(x1 * cos(t) - y1 * sin(t), x1 * sin(t) + y1 * cos(t))
        self.d2 = Point(x2 * cos(t) - y2 * sin(t), x2 * sin(t) + y2 * cos(t))
        self.d = Point(x * cos(t) - y * sin(t), x * sin(t) + y * cos(t))

    def skew_x(self, t):
        t = radians(t)
        self.d1.x -= self.d1.y * sin(t)
        self.d2.x -= self.d2.y * sin(t)
        self.d.x -= self.d.y * sin(t)

    def skew_y(self, t):
        t = radians(t)
        self.d1.y += self.d1.x * sin(t)
        self.d2.y += self.d2.x * sin(t)
        self.d.y += self.d.x * sin(t)


# Relative quadratic Bézier
class _q:
    def __init__(self, d1, d):
        self.d1 = Point(*d1)
        self.d = Point(*d)

    def __repr__(self):
        return "q{0:s}".format(_format(self.d1.x, self.d1.y, self.d.x, self.d.y))

    def scale(self, s):
        self.d1.x *= s.x
        self.d1.y *= s.y
        self.d.x *= s.x
        self.d.y *= s.y

    def translate(self, d):
        pass  # Do nothing since this is a relative distance

    def rotate(self, t):
        t = radians(t)
        x1, y1, x, y = self.d1.x, self.d1.y, self.d.x, self.d.y
        self.d1 = Point(x1 * cos(t) - y1 * sin(t), x1 * sin(t) + y1 * cos(t))
        self.d = Point(x * cos(t) - y * sin(t), x * sin(t) + y * cos(t))

    def skew_x(self, t):
        t = radians(t)
        self.d1.x -= self.d1.y * sin(t)
        self.d.x -= self.d.y * sin(t)

    def skew_y(self, t):
        t = radians(t)
        self.d1.y += self.d1.x * sin(t)
        self.d.y += self.d.x * sin(t)


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
def _format(*args):
    return "".join(f"{float(n): .3f}".rstrip("0").rstrip(".") for n in args).lstrip()
