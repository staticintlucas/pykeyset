# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from math import isclose, radians, tan
from numbers import Number
from typing import NamedTuple, NamedTupleMeta, Union

from ..types import Vector


class NamedTupleABCMeta(ABCMeta, NamedTupleMeta):
    pass


class Segment(metaclass=NamedTupleABCMeta):
    @abstractmethod
    def __repr__(self) -> str:
        pass  # pragma: no cover

    @abstractmethod
    def scale(self, scale: Union[Number, Vector]) -> "Segment":
        pass  # pragma: no cover

    @abstractmethod
    def translate(self, dist: Vector) -> "Segment":
        pass  # pragma: no cover

    @abstractmethod
    def rotate(self, degrees: Number) -> "Segment":
        pass  # pragma: no cover

    @abstractmethod
    def skew_x(self, degrees: Number) -> "Segment":
        pass  # pragma: no cover

    @abstractmethod
    def skew_y(self, degrees: Number) -> "Segment":
        pass  # pragma: no cover


class Move(NamedTuple, Segment):
    """Absolute move (M) segment"""

    point: Vector

    def __repr__(self) -> str:
        return f"M{format_coords(self.point)}"

    def scale(self, scale: Vector) -> "Move":
        return Move(self.point * scale)

    def translate(self, dist: Vector) -> "Move":
        return Move(self.point + dist)

    def rotate(self, degrees: Number) -> "Move":
        return Move(self.point.rotate(radians(degrees)))

    def skew_x(self, degrees: Number) -> "Move":
        return Move(self.point - Vector(self.point.y * tan(radians(degrees)), 0))

    def skew_y(self, degrees: Number) -> "Move":
        return Move(self.point + Vector(0, self.point.x * tan(radians(degrees))))


class Line(NamedTuple, Segment):
    """Relative line (l) segment"""

    point: Vector

    def __repr__(self) -> str:
        if isclose(self.point.y, 0, abs_tol=5e-4):
            return f"h{float(self.point.x):.3f}".rstrip("0").rstrip(".")
        elif isclose(self.point.x, 0, abs_tol=5e-4):
            return f"v{float(self.point.y):.3f}".rstrip("0").rstrip(".")
        else:
            return f"l{format_coords(self.point)}"

    def scale(self, scale: Vector) -> "Line":
        return Line(self.point * scale)

    def translate(self, dist: Vector) -> "Line":
        return self  # Do nothing since this is a relative distance

    def rotate(self, degrees: Number) -> "Line":
        return Line(self.point.rotate(radians(degrees)))

    def skew_x(self, degrees: Number) -> "Line":
        return Line(self.point._replace(x=self.point.x - self.point.y * tan(radians(degrees))))

    def skew_y(self, degrees: Number) -> "Line":
        return Line(self.point._replace(y=self.point.y + self.point.x * tan(radians(degrees))))


class CubicBezier(NamedTuple, Segment):
    """Relative cubic Bézier (c) segment"""

    ctrl1: Vector
    ctrl2: Vector
    point: Vector

    def __repr__(self) -> str:
        return f"c{format_coords(self.ctrl1, self.ctrl2, self.point)}"

    def scale(self, scale: Vector) -> "CubicBezier":
        return CubicBezier(self.ctrl1 * scale, self.ctrl2 * scale, self.point * scale)

    def translate(self, dist: Vector) -> "CubicBezier":
        return self  # Do nothing since this is a relative distance

    def rotate(self, degrees: Number) -> "CubicBezier":
        t = radians(degrees)
        return CubicBezier(self.ctrl1.rotate(t), self.ctrl2.rotate(t), self.point.rotate(t))

    def skew_x(self, degrees: Number) -> "CubicBezier":
        t = radians(degrees)
        return CubicBezier(
            self.ctrl1._replace(x=self.ctrl1.x - self.ctrl1.y * tan(t)),
            self.ctrl2._replace(x=self.ctrl2.x - self.ctrl2.y * tan(t)),
            self.point._replace(x=self.point.x - self.point.y * tan(t)),
        )

    def skew_y(self, degrees: Number) -> "CubicBezier":
        t = radians(degrees)
        return CubicBezier(
            self.ctrl1._replace(y=self.ctrl1.y + self.ctrl1.x * tan(t)),
            self.ctrl2._replace(y=self.ctrl2.y + self.ctrl2.x * tan(t)),
            self.point._replace(y=self.point.y + self.point.x * tan(t)),
        )


class QuadraticBezier(NamedTuple, Segment):
    """Relative quadratic Bézier (q) segment"""

    ctrl: Vector
    point: Vector

    def __repr__(self) -> str:
        return f"q{format_coords(self.ctrl, self.point)}"

    def scale(self, scale: Vector) -> "QuadraticBezier":
        return QuadraticBezier(self.ctrl * scale, self.point * scale)

    def translate(self, dist: Vector) -> "QuadraticBezier":
        return self  # Do nothing since this is a relative distance

    def rotate(self, degrees: Number) -> "QuadraticBezier":
        t = radians(degrees)
        return QuadraticBezier(self.ctrl.rotate(t), self.point.rotate(t))

    def skew_x(self, degrees: Number) -> "QuadraticBezier":
        t = radians(degrees)
        return QuadraticBezier(
            self.ctrl._replace(x=self.ctrl.x - self.ctrl.y * tan(t)),
            self.point._replace(x=self.point.x - self.point.y * tan(t)),
        )

    def skew_y(self, degrees: Number) -> "QuadraticBezier":
        t = radians(degrees)
        return QuadraticBezier(
            self.ctrl._replace(y=self.ctrl.y + self.ctrl.x * tan(t)),
            self.point._replace(y=self.point.y + self.point.x * tan(t)),
        )


class ClosePath(NamedTuple, Segment):
    """Close path (z) segment"""

    def __repr__(self) -> str:
        return "z"

    def scale(self, scale: Vector) -> "ClosePath":
        return self

    def translate(self, dist: Vector) -> "ClosePath":
        return self

    def rotate(self, degrees: Number) -> "ClosePath":
        return self

    def skew_x(self, degrees: Number) -> "ClosePath":
        return self

    def skew_y(self, degrees: Number) -> "ClosePath":
        return self


def format_coords(*args: Vector):
    """Format a list of coords as efficiently as possible"""
    coords = [a for arg in args for a in arg]
    return "".join(f"{float(c): .3f}".rstrip("0").rstrip(".") for c in coords).lstrip()
