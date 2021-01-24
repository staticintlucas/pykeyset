# -*- coding: utf-8 -*-

from math import isclose, radians, tan
from typing import NamedTuple, Union

from ..types import Vector

# Note: I tried (and failed) to make a common abstract base class for all these segment types. The
# issue was that NamedTuple does a lot of internal trickery to make it work the way it's supposed
# to. As a result it didn't work quite correctly in Python <= 3.8 and straight up raised an error
# in Python 3.9. For now this is about the best way to do this if we want immutability (we do) and
# a namedtuple-like interface


class Move(NamedTuple):
    """Absolute move (M) NamedTuple"""

    point: Vector

    def __repr__(self) -> str:
        return f"M{format_coords(self.point)}"

    def scale(self, scale: Union[float, "Vector"]) -> "Move":
        return Move(self.point * scale)

    def translate(self, dist: Vector) -> "Move":
        return Move(self.point + dist)

    def rotate(self, degrees: float) -> "Move":
        return Move(self.point.rotate(radians(degrees)))

    def skew_x(self, degrees: float) -> "Move":
        return Move(self.point - Vector(self.point.y * tan(radians(degrees)), 0))

    def skew_y(self, degrees: float) -> "Move":
        return Move(self.point + Vector(0, self.point.x * tan(radians(degrees))))


class Line(NamedTuple):
    """Relative line (l) NamedTuple"""

    point: Vector

    def __repr__(self) -> str:
        if isclose(self.point.y, 0, abs_tol=5e-4):
            return f"h{float(self.point.x):.3f}".rstrip("0").rstrip(".")
        elif isclose(self.point.x, 0, abs_tol=5e-4):
            return f"v{float(self.point.y):.3f}".rstrip("0").rstrip(".")
        else:
            return f"l{format_coords(self.point)}"

    def scale(self, scale: Union[float, "Vector"]) -> "Line":
        return Line(self.point * scale)

    def translate(self, dist: Vector) -> "Line":
        return self  # Do nothing since this is a relative distance

    def rotate(self, degrees: float) -> "Line":
        return Line(self.point.rotate(radians(degrees)))

    def skew_x(self, degrees: float) -> "Line":
        return Line(self.point._replace(x=self.point.x - self.point.y * tan(radians(degrees))))

    def skew_y(self, degrees: float) -> "Line":
        return Line(self.point._replace(y=self.point.y + self.point.x * tan(radians(degrees))))


class CubicBezier(NamedTuple):
    """Relative cubic Bézier (c) NamedTuple"""

    ctrl1: Vector
    ctrl2: Vector
    point: Vector

    def __repr__(self) -> str:
        return f"c{format_coords(self.ctrl1, self.ctrl2, self.point)}"

    def scale(self, scale: Union[float, "Vector"]) -> "CubicBezier":
        return CubicBezier(self.ctrl1 * scale, self.ctrl2 * scale, self.point * scale)

    def translate(self, dist: Vector) -> "CubicBezier":
        return self  # Do nothing since this is a relative distance

    def rotate(self, degrees: float) -> "CubicBezier":
        t = radians(degrees)
        return CubicBezier(self.ctrl1.rotate(t), self.ctrl2.rotate(t), self.point.rotate(t))

    def skew_x(self, degrees: float) -> "CubicBezier":
        t = radians(degrees)
        return CubicBezier(
            self.ctrl1._replace(x=self.ctrl1.x - self.ctrl1.y * tan(t)),
            self.ctrl2._replace(x=self.ctrl2.x - self.ctrl2.y * tan(t)),
            self.point._replace(x=self.point.x - self.point.y * tan(t)),
        )

    def skew_y(self, degrees: float) -> "CubicBezier":
        t = radians(degrees)
        return CubicBezier(
            self.ctrl1._replace(y=self.ctrl1.y + self.ctrl1.x * tan(t)),
            self.ctrl2._replace(y=self.ctrl2.y + self.ctrl2.x * tan(t)),
            self.point._replace(y=self.point.y + self.point.x * tan(t)),
        )


class QuadraticBezier(NamedTuple):
    """Relative quadratic Bézier (q) NamedTuple"""

    ctrl: Vector
    point: Vector

    def __repr__(self) -> str:
        return f"q{format_coords(self.ctrl, self.point)}"

    def scale(self, scale: Union[float, "Vector"]) -> "QuadraticBezier":
        return QuadraticBezier(self.ctrl * scale, self.point * scale)

    def translate(self, dist: Vector) -> "QuadraticBezier":
        return self  # Do nothing since this is a relative distance

    def rotate(self, degrees: float) -> "QuadraticBezier":
        t = radians(degrees)
        return QuadraticBezier(self.ctrl.rotate(t), self.point.rotate(t))

    def skew_x(self, degrees: float) -> "QuadraticBezier":
        t = radians(degrees)
        return QuadraticBezier(
            self.ctrl._replace(x=self.ctrl.x - self.ctrl.y * tan(t)),
            self.point._replace(x=self.point.x - self.point.y * tan(t)),
        )

    def skew_y(self, degrees: float) -> "QuadraticBezier":
        t = radians(degrees)
        return QuadraticBezier(
            self.ctrl._replace(y=self.ctrl.y + self.ctrl.x * tan(t)),
            self.point._replace(y=self.point.y + self.point.x * tan(t)),
        )


class ClosePath(NamedTuple):
    """Close path (z) NamedTuple"""

    def __repr__(self) -> str:
        return "z"

    def scale(self, scale: Union[float, "Vector"]) -> "ClosePath":
        return self

    def translate(self, dist: Vector) -> "ClosePath":
        return self

    def rotate(self, degrees: float) -> "ClosePath":
        return self

    def skew_x(self, degrees: float) -> "ClosePath":
        return self

    def skew_y(self, degrees: float) -> "ClosePath":
        return self


def format_coords(*args: Vector):
    """Format a list of coords as efficiently as possible"""
    coords = [a for arg in args for a in arg]
    return "".join(f"{float(c): .3f}".rstrip("0").rstrip(".") for c in coords).lstrip()
