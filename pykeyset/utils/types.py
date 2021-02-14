# -*- coding: utf-8 -*-

import colorsys
from enum import Enum
from math import atan2, cos, sin, sqrt
from typing import NamedTuple, Union


class VerticalAlign(Enum):
    TOP = 0
    MIDDLE = 0.5
    BOTTOM = 1


class HorizontalAlign(Enum):
    LEFT = 0
    CENTER = 0.5
    RIGHT = 1


class Vector(NamedTuple):
    x: float
    y: float

    @property
    def magnitude(self) -> float:
        return sqrt(self.x * self.x + self.y * self.y)

    @property
    def angle(self) -> float:
        return atan2(self.y, self.x)

    def __neg__(self) -> "Vector":
        return Vector(-self.x, -self.y)

    def __add__(self, other: "Vector") -> "Vector":
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector") -> "Vector":
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, other: Union[float, "Vector"]) -> "Vector":
        if isinstance(other, self.__class__):
            return Vector(self.x * other.x, self.y * other.y)
        else:
            return Vector(self.x * other, self.y * other)

    def __truediv__(self, other: Union[float, "Vector"]) -> "Vector":
        if isinstance(other, self.__class__):
            return Vector(self.x / other.x, self.y / other.y)
        else:
            return Vector(self.x / other, self.y / other)

    def rotate(self, angle: float) -> "Vector":
        c, s = cos(angle), sin(angle)
        return Vector(self.x * c - self.y * s, self.x * s + self.y * c)


class Rect(NamedTuple):
    x: float
    y: float
    w: float
    h: float

    @property
    def width(self) -> float:
        return self.w

    @property
    def height(self) -> float:
        return self.h

    @property
    def position(self) -> Vector:
        return Vector(self.x, self.y)

    @property
    def size(self) -> Vector:
        return Vector(self.w, self.h)

    def scale(self, scale: Union[float, "Vector"]) -> "Rect":
        if isinstance(scale, Vector):
            x1, x2 = sorted([self.x * scale.x, (self.x + self.w) * scale.x])
            y1, y2 = sorted([self.y * scale.y, (self.y + self.h) * scale.y])
        else:
            x1, x2 = sorted([self.x * scale, (self.x + self.w) * scale])
            y1, y2 = sorted([self.y * scale, (self.y + self.h) * scale])
        return Rect(x1, y1, x2 - x1, y2 - y1)


class RoundRect(Rect):
    r: float

    def __new__(cls, x: float, y: float, w: float, h: float, r: float):
        self = super().__new__(cls, x, y, w, h)
        self.r = r
        return self

    @property
    def radius(self) -> float:
        return self.r

    def as_rect(self) -> Rect:
        return Rect(self.x, self.y, self.w, self.h)


class Color(
    # Note: We need to use this call to NamedTuple to make sure Color is a sub-subclass of
    # NamedTuple otherwise it won't let us override __new__ to validate input
    NamedTuple("Color", [("r", float), ("g", float), ("b", float)])
):
    def __new__(cls, r: float, g: float, b: float):

        for key, val in zip("rgb", (r, g, b)):
            if not 0.0 <= val <= 1.0:
                raise ValueError(f"invalid value for '{key}' for Color(): '{val}'")

        return super().__new__(cls, r, g, b)

    @staticmethod
    def from_hex(color: str) -> "Color":
        col = color.lstrip("#")

        try:
            if len(col) == 6:
                rgb = [int(col[i : i + 2], 16) / 255 for i in range(0, len(col), 2)]
            elif len(col) == 3:
                rgb = [int(c, 16) / 15 for c in col]
            else:
                raise ValueError()
        except ValueError:
            raise ValueError(f"invalid literal for Color(): '{color}'") from None

        return Color(*rgb)

    def to_hex(self) -> str:
        return "#" + "".join(f"{int(c * 255 + 0.5):02x}" for c in (self.r, self.g, self.b))

    def lighter(self, val: float = 0.15) -> "Color":
        if not 0.0 <= val <= 1.0:
            raise ValueError(f"invalid value for 'val' in call to Color.lighter(): '{val}'")

        return Color(*(val + (1 - val) * c for c in self))

    def darker(self, val: float = 0.15) -> "Color":
        if not 0.0 <= val <= 1.0:
            raise ValueError(f"invalid value for 'val' in call to Color.lighter(): '{val}'")

        return Color(*((1 - val) * c for c in self))

    def highlight(self, lum: float = 0.15) -> "Color":
        if not 0.0 <= lum <= 0.5:
            raise ValueError(f"invalid value for 'val' in call to Color.lighter(): '{lum}'")

        h, l, s = colorsys.rgb_to_hls(*self)
        l += lum if l < 0.5 else -lum  # flake8 doesn't like the letter l  # noqa: E741
        return Color(*colorsys.hls_to_rgb(h, l, s))
