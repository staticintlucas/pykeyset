# coding: utf-8

import re
from math import cos, sin, radians, degrees, inf

from ..error import error
from ..types import Point, Dist, Rect
from .arc_to_bezier import arc_to_bezier

class Path:

    def __init__(self, d):

        token = iter(t for t in re.split(r'(-?\d+\.?\d*|[A-Za-z])', d) \
            if len(t) > 0 and not t.isspace() and not t == ',')

        point = Point(0, 0)
        self.rect = Rect(0, 0, 0, 0)
        self.d = []

        for t in token:
            try:
                if t.startswith('m'):
                    x = float(next(token))
                    y = float(next(token))
                    point.x += x
                    point.y += y
                    self.d.append(M(point))

                elif t.startswith('M'):
                    x = float(next(token))
                    y = float(next(token))
                    point = Point(x, y)
                    self.d.append(M(point))

                elif t.startswith('l'):
                    x = float(next(token))
                    y = float(next(token))
                    self.d.append(l(Point(x, y)))
                    point.x += x
                    point.y += y

                elif t.startswith('L'):
                    x = float(next(token))
                    y = float(next(token))
                    self.d.append(l(Point(x - point.x, y - point.y)))
                    point = Point(x, y)

                elif t.startswith('h'):
                    x = float(next(token))
                    point.x += x
                    self.d.append(l(Point(x, 0)))

                elif t.startswith('H'):
                    x = float(next(token))
                    self.d.append(l(Point(x - point.x, 0)))
                    point.x = x

                elif t.startswith('v'):
                    y = float(next(token))
                    point.y += y
                    self.d.append(l(Point(0, y)))

                elif t.startswith('V'):
                    y = float(next(token))
                    self.d.append(l(Point(0, y - point.y)))
                    point.y = y

                elif t.lower().startswith('z'):
                    self.d.append(z())

                elif t.startswith('c'):
                    x1 = float(next(token))
                    y1 = float(next(token))
                    x2 = float(next(token))
                    y2 = float(next(token))
                    x = float(next(token))
                    y = float(next(token))

                    self.d.append(c(Point(x1, y1), Point(x2, y2), Point(x, y)))

                    point.x += x
                    point.y += y

                elif t.startswith('C'):
                    x1 = float(next(token))
                    y1 = float(next(token))
                    x2 = float(next(token))
                    y2 = float(next(token))
                    x = float(next(token))
                    y = float(next(token))

                    self.d.append(c(Point(x1 - point.x, y1 - point.y),
                        Point(x2 - point.x, y2 - point.y), Point(x - point.x, y - point.y)))

                    point = Point(x, y)

                elif t.startswith('s'):
                    x2 = float(next(token))
                    y2 = float(next(token))
                    x = float(next(token))
                    y = float(next(token))

                    last = self.d[-1] if len(self.d) > 0 else None
                    if isinstance(last, c):
                        x1 = last.d.x - last.d2.x
                        y1 = last.d.y - last.d2.y
                        self.d.append(c(Point(x1, y1), Point(x2, y2), Point(x, y)))

                    else:
                        self.d.append(q(Point(x2, y2), Point(x, y)))

                    point.x += x
                    point.y += y

                elif t.startswith('S'):
                    x2 = float(next(token))
                    y2 = float(next(token))
                    x = float(next(token))
                    y = float(next(token))

                    last = self.d[-1] if len(self.d) > 0 else None
                    if isinstance(last, c):
                        x1 = last.d.x - last.d2.x
                        y1 = last.d.y - last.d2.y
                        self.d.append(c(Point(x1, y1), Point(x2 - point.x, y2 - point.y),
                            Point(x - point.x, y - point.y)))

                    else:
                        self.d.append(q(Point(x2 - point.x, y2 - point.y),
                            Point(x - point.x, y - point.y)))

                    point = Point(x, y)

                elif t.startswith('q'):
                    x1 = float(next(token))
                    y1 = float(next(token))
                    x = float(next(token))
                    y = float(next(token))

                    self.d.append(q(Point(x1, y1), Point(x, y)))

                    point.x += x
                    point.y += y

                elif t.startswith('Q'):
                    x1 = float(next(token))
                    y1 = float(next(token))
                    x = float(next(token))
                    y = float(next(token))

                    self.d.append(q(Point(x2 - point.x, y2 - point.y),
                        Point(x - point.x, y - point.y)))

                    point = Point(x, y)

                elif t.startswith('t'):
                    x = float(next(token))
                    y = float(next(token))

                    last = self.d[-1] if len(self.d) > 0 else None
                    if isinstance(last, q):
                        x1 = last.d.x - last.d1.x
                        y1 = last.d.y - last.d1.y
                        self.d.append(q(Point(x1, y1), Point(x, y)))

                    else:
                        self.d.append(l(Point(x, y)))

                    point.x += x
                    point.y += y

                elif t.startswith('T'):
                    x = float(next(token))
                    y = float(next(token))

                    last = self.d[-1] if len(self.d) > 0 else None
                    if isinstance(last, q):
                        x1 = last.d.x - last.d1.x
                        y1 = last.d.y - last.d1.y
                        self.d.append(q(Point(x1, y1), Point(x - point.x, y - point.y)))

                    else:
                        self.d.append(l(Point(x - point.x, y - point.y)))

                    point = Point(x, y)

                elif t.startswith('a'):
                    rx = abs(float(next(token)))
                    ry = abs(float(next(token)))
                    xar = float(next(token))
                    laf = float(next(token)) > 0.5 # Use 0.5 as a threshold between True and False
                    sf = float(next(token)) > 0.5
                    x = float(next(token))
                    y = float(next(token))

                    for d1, d2, d in arc_to_bezier(Dist(rx, ry), xar, laf, sf, Point(x, y)):
                        self.d.append(c(d1, d2, d))

                    point.x += x
                    point.y += y

                elif t.startswith('A'):
                    rx = float(next(token))
                    ry = float(next(token))
                    xar = float(next(token))
                    laf = float(next(token)) > 0.5 # Use 0.5 as a threshold between True and False
                    sf = float(next(token)) > 0.5
                    x = float(next(token))
                    y = float(next(token))

                    for d1, d2, d in arc_to_bezier(Dist(rx, ry), xar, laf, sf, Point(x - point.x, y - point.y)):
                        self.d.append(c(d1, d2, d))

                    point = Point(x, y)

                else:
                    error(f"invalid path command '{t}'")

            except (StopIteration, ValueError):
                error("invalid path")

        minpt = Point(*map(min, zip(*(tuple(seg.min()) for seg in self.d))))
        maxpt = Point(*map(max, zip(*(tuple(seg.max()) for seg in self.d))))

        self.rect = Rect(minpt.x, minpt.y, maxpt.x - minpt.x, maxpt.y - minpt.y)


    def __repr__(self):
        return ''.join(str(d) for d in self.d)

    def transform(self, trns):
        trns = re.sub(r",\s+", ",", trns).split()[::-1]

        for t in trns:
            try:
                if t.startswith('scale('):
                    val = [float(v) for v in t[6:-1].split(',')]
                    s = Dist(val[0], val[1] if len(val) > 1 else val[0])
                    self.scale(s)

                elif t.startswith('translate('):
                    val = [float(v) for v in t[10:-1].split(',')]
                    d = Dist(val[0], val[1])
                    self.scale(d)

                elif t.startswith('rotate('):
                    val = float(t[7:-1])
                    self.rotate(val)

                elif t.startswith('skewX('):
                    val = float(t[6:-1])
                    self.skew_x(val)

                elif t.startswith('skewY('):
                    val = float(t[6:-1])
                    self.skew_y(val)

                else:
                    error(f"unsupported transform '{t.split('(')[0]}'")

            except (ValueError, IndexError):
                error("invalid transform")

    def scale(self, s):
        self.rect.x *= s.x
        self.rect.y *= s.y
        self.rect.w *= s.x
        self.rect.h *= s.y
        for seg in self.d:
            seg.scale(s)

    def translate(self, d):
        self.rect.x += d.x
        self.rect.y += d.y
        for seg in self.d:
            seg.translate(d)

    def rotate(self, t):
        for seg in self.d:
            seg.rotate(t)

        minpt = Point(*map(min, zip(*(tuple(seg.min()) for seg in self.d))))
        maxpt = Point(*map(max, zip(*(tuple(seg.max()) for seg in self.d))))

        self.rect(minpt.x, minpt.y, maxpt.x - minpt.x, maxpt.y - minpt.y)

    def skew_x(self, t):
        for seg in self.d:
            seg.skew_x(t)

        minpt = Point(*map(min, zip(*(tuple(seg.min()) for seg in self.d))))
        maxpt = Point(*map(max, zip(*(tuple(seg.max()) for seg in self.d))))

        self.rect(minpt.x, minpt.y, maxpt.x - minpt.x, maxpt.y - minpt.y)

    def skew_y(self, t):
        for seg in self.d:
            seg.skew_y(t)

        minpt = Point(*map(min, zip(*(tuple(seg.min()) for seg in self.d))))
        maxpt = Point(*map(max, zip(*(tuple(seg.max()) for seg in self.d))))

        self.rect(minpt.x, minpt.y, maxpt.x - minpt.x, maxpt.y - minpt.y)


# Absolute move
class M:
    def __init__(self, d):
        self.d = d

    def __repr__(self):
        return 'M{0:s}'.format(_format(self.d.x, self.d.y))

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

    def min(self):
        return self.d

    def max(self):
        return self.d

# Relative line
class l:
    def __init__(self, d):
        self.d = d

    def __repr__(self):
        return 'l{0:s}'.format(_format(self.d.x, self.d.y))

    def scale(self, s):
        self.d.x *= s.x
        self.d.y *= s.y

    def translate(self, d):
        pass # Do nothing since this is a relative distance

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

    def min(self):
        return self.d

    def max(self):
        return self.d

# Relative cubic Bézier
class c:
    def __init__(self, d1, d2, d):
        self.d1 = d1
        self.d2 = d2
        self.d = d

    def __repr__(self):
        return 'c{0:s}'.format(_format(self.d1.x, self.d1.y, self.d2.x, self.d2.y, self.d.x, self.d.y))

    def scale(self, s):
        self.d1.x *= s.x
        self.d1.y *= s.y
        self.d2.x *= s.x
        self.d2.y *= s.y
        self.d.x *= s.x
        self.d.y *= s.y

    def translate(self, d):
        pass # Do nothing since this is a relative distance

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

    def min(self):
        return min(self.d1.x, self.d2.x, self.d.x), min(self.d1.y, self.d2.y, self.d.y)

    def max(self):
        return max(self.d1.x, self.d2.x, self.d.x), max(self.d1.y, self.d2.y, self.d.y)

# Relative quadratic Bézier
class q:
    def __init__(self, d1, d):
        self.d1 = d1
        self.d = d

    def __repr__(self):
        return 'q{0:s}'.format(_format(self.d1.x, self.d1.y, self.d.x, self.d.y))

    def scale(self, s):
        self.d1.x *= s.x
        self.d1.y *= s.y
        self.d.x *= s.x
        self.d.y *= s.y

    def translate(self, d):
        pass # Do nothing since this is a relative distance

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

    def min(self):
        return min(self.d1.x, self.d.x), min(self.d1.y, self.d.y)

    def max(self):
        return max(self.d1.x, self.d.x), max(self.d1.y, self.d.y)

# z
class z:
    def __init__(self):
        pass

    def __repr__(self):
        return 'z'

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

    def min(self):
        return inf, inf

    def max(self):
        return -inf, -inf

# Format a list of coords as efficiently as possible
def _format(*args):
    return ''.join(f'{float(n): .3f}'.rstrip('0').rstrip('.') for n in args).lstrip()
