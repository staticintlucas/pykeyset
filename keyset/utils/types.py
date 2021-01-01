# coding: utf-8

from .error import warning

from recordclass import recordclass
from collections import namedtuple
import colorsys

Point = recordclass("Point", ("x", "y"))
Dist = recordclass("Dist", ("x", "y"))
Size = recordclass("Size", ("w", "h"))

Rect = recordclass("Rect", ("x", "y", "w", "h"))
RoundRect = recordclass("Rect", ("x", "y", "w", "h", "r"))

ColorTuple = namedtuple("ColorTuple", ("r", "g", "b"))


class Color(ColorTuple):
    def __new__(cls, *color):
        if len(color) == 3:
            return super().__new__(cls, *color)
        elif len(color) == 1:
            col = color[0].lstrip("#")
            if len(col) == 3:
                return super().__new__(cls, *[int(c, 16) / 15 for c in col])
            elif len(col) == 6:
                return super().__new__(
                    cls, *(int(c, 16) / 255 for c in (col[0:2], col[2:4], col[4:6]))
                )
            else:
                warning(f"invalid color '{color}'. Defaulting to '#000000'")
                return super().__new__(cls, 0, 0, 0)
        else:
            warning(f"invalid color '{color}'. Defaulting to '#000000'")
            return super().__new__(cls, 0, 0, 0)

    def lighter(self, al=0.15):
        return Color(*(al + (1 - al) * c for c in self))

    def darker(self, al=0.15):
        return Color(*((1 - al) * c for c in self))

    def highlight(self, lum=0.15):
        h, l, s = colorsys.rgb_to_hls(*self)
        l += lum if l < 0.5 else -lum
        return Color(*colorsys.hls_to_rgb(h, l, s))

    def __repr__(self):
        return f"#{int(self.r * 256):02x}{int(self.g * 256):02x}{int(self.b * 256):02x}"
