# coding: utf-8

import re
from math import cos, sin, radians, degrees

from ..error import error
from .arc_to_bezier import arc_to_bezier

class Path:

    def __init__(self, d):

        token = iter(t for t in re.split(r'(-?\d+\.?\d*|[A-Za-z])', d) \
            if len(t) > 0 and not t.isspace() and not t == ',')

        point = [0, 0]
        self.min = [0, 0]
        self.max = [0, 0]
        self.d = []

        for t in token:
            try:
                if t.startswith('m'):
                    x = float(next(token))
                    y = float(next(token))
                    point[0] += x
                    point[1] += y
                    self.d.append(M(tuple(point)))

                elif t.startswith('M'):
                    x = float(next(token))
                    y = float(next(token))
                    point = [x, y]
                    self.d.append(M(tuple(point)))

                elif t.startswith('l'):
                    x = float(next(token))
                    y = float(next(token))
                    self.d.append(l((x, y)))
                    point[0] += x
                    point[1] += y

                elif t.startswith('L'):
                    x = float(next(token))
                    y = float(next(token))
                    self.d.append(l((x - point[0], y - point[1])))
                    point = [x, y]

                elif t.startswith('h'):
                    x = float(next(token))
                    point[0] += x
                    self.d.append(l((x, 0)))

                elif t.startswith('H'):
                    x = float(next(token))
                    self.d.append(l((x - point[0], 0)))
                    point[0] = x

                elif t.startswith('v'):
                    y = float(next(token))
                    point[1] += y
                    self.d.append(l((0, y)))

                elif t.startswith('V'):
                    y = float(next(token))
                    self.d.append(l((0, y - point[1])))
                    point[1] = y

                elif t.lower().startswith('z'):
                    self.d.append(z())

                elif t.startswith('c'):
                    x1 = float(next(token))
                    y1 = float(next(token))
                    x2 = float(next(token))
                    y2 = float(next(token))
                    x = float(next(token))
                    y = float(next(token))

                    self.d.append(c((x1, y1), (x2, y2), (x, y)))

                    point[0] += x
                    point[1] += y

                elif t.startswith('C'):
                    x1 = float(next(token))
                    y1 = float(next(token))
                    x2 = float(next(token))
                    y2 = float(next(token))
                    x = float(next(token))
                    y = float(next(token))

                    self.d.append(c((x1 - point[0], y1 - point[1]),
                        (x2 - point[0], y2 - point[1]), (x - point[0], y - point[1])))

                    point = [x, y]

                elif t.startswith('s'):
                    x2 = float(next(token))
                    y2 = float(next(token))
                    x = float(next(token))
                    y = float(next(token))

                    last = self.d[-1] if len(self.d) > 0 else None
                    if isinstance(last, c):
                        x1 = last.x - last.x2
                        y1 = last.y - last.y2
                        self.d.append(c((x1, y1), (x2, y2), (x, y)))

                    else:
                        self.d.append(q((x2, y2), (x, y)))

                    point[0] += x
                    point[1] += y

                elif t.startswith('S'):
                    x2 = float(next(token))
                    y2 = float(next(token))
                    x = float(next(token))
                    y = float(next(token))

                    last = self.d[-1] if len(self.d) > 0 else None
                    if isinstance(last, c):
                        x1 = last.x - last.x2
                        y1 = last.y - last.y2
                        self.d.append(c((x1, y1), (x2 - point[0], y2 - point[1]),
                            (x - point[0], y - point[1])))

                    else:
                        self.d.append(q((x2 - point[0], y2 - point[1]),
                            (x - point[0], y - point[1])))

                    point = [x, y]

                elif t.startswith('q'):
                    x1 = float(next(token))
                    y1 = float(next(token))
                    x = float(next(token))
                    y = float(next(token))

                    self.d.append(q((x1, y1), (x, y)))

                    point[0] += x
                    point[1] += y

                elif t.startswith('Q'):
                    x1 = float(next(token))
                    y1 = float(next(token))
                    x = float(next(token))
                    y = float(next(token))

                    self.d.append(q((x2 - point[0], y2 - point[1]),
                        (x - point[0], y - point[1])))

                    point = [x, y]

                elif t.startswith('t'):
                    x = float(next(token))
                    y = float(next(token))

                    last = self.d[-1] if len(self.d) > 0 else None
                    if isinstance(last, q):
                        x1 = last.x - last.x1
                        y1 = last.y - last.y1
                        self.d.append(q((x1, y1), (x, y)))

                    else:
                        self.d.append(l((x, y)))

                    point[0] += x
                    point[1] += y

                elif t.startswith('T'):
                    x = float(next(token))
                    y = float(next(token))

                    last = self.d[-1] if len(self.d) > 0 else None
                    if isinstance(last, q):
                        x1 = last.x - last.x1
                        y1 = last.y - last.y1
                        self.d.append(q((x1, y1), (x - point[0], y - point[1])))

                    else:
                        self.d.append(l((x - point[0], y - point[1])))

                    point[0] = x
                    point[1] = y

                elif t.startswith('a'):
                    rx = abs(float(next(token)))
                    ry = abs(float(next(token)))
                    xar = float(next(token))
                    laf = float(next(token)) > 0.5 # Use 0.5 as a threshold between True and False
                    sf = float(next(token)) > 0.5
                    x = float(next(token))
                    y = float(next(token))

                    for d1, d2, d in arc_to_bezier((rx, ry), xar, laf, sf, (x, y)):
                        self.d.append(c(d1, d2, d))

                    point[0] += x
                    point[1] += y

                elif t.startswith('A'):
                    rx = float(next(token))
                    ry = float(next(token))
                    xar = float(next(token))
                    laf = float(next(token)) > 0.5 # Use 0.5 as a threshold between True and False
                    sf = float(next(token)) > 0.5
                    x = float(next(token))
                    y = float(next(token))

                    for d1, d2, d in arc_to_bezier((rx, ry), xar, laf, sf, (x - point[0], y - point[1])):
                        self.d.append(c(d1, d2, d))

                    point[0] = x
                    point[1] = y

                else:
                    error(f"invalid path command '{t}'")

            except (StopIteration, ValueError):
                error("invalid path")

            self.min[0] = min(self.min[0], point[0])
            self.min[1] = min(self.min[1], point[1])

            self.max[0] = max(self.max[0], point[0])
            self.max[1] = max(self.max[1], point[1])


    def __repr__(self):
        return ''.join(str(d) for d in self.d)


# Absolute move
class M:
    def __init__(self, to):
        self.x, self.y = to

    def __repr__(self):
        return 'M{0:s}'.format(_format(self.x, self.y))

    def scale(self, s):
        self.x *= s[0]
        self.y *= s[1]

    def translate(self, d):
        self.x += d[0]
        self.y += d[1]

    def rotate(self, t):
        t = radians(t)
        x, y = self.x, self.y
        self.x, self.y = x * cos(t) - y * sin(t), x * sin(t) + y * cos(t)

    def skew_x(self, t):
        t = radians(t)
        self.x -= self.y * sin(t)

    def skew_y(self, t):
        t = radians(t)
        self.y += self.x * sin(t)

# Relative line
class l:
    def __init__(self, d):
        self.x, self.y = d

    def __repr__(self):
        return 'l{0:s}'.format(_format(self.x, self.y))

    def scale(self, s):
        self.x *= s[0]
        self.y *= s[1]

    def translate(self, d):
        pass # Do nothing since this is a relative distance

    def rotate(self, t):
        t = radians(t)
        x, y = self.x, self.y
        self.x, self.y = x * cos(t) - y * sin(t), x * sin(t) + y * cos(t)

    def skew_x(self, t):
        t = radians(t)
        self.x -= self.y * sin(t)

    def skew_y(self, t):
        t = radians(t)
        self.y += self.x * sin(t)

# Relative cubic Bézier
class c:
    def __init__(self, d1, d2, d):
        self.x1, self.y1 = d1
        self.x2, self.y2 = d2
        self.x, self.y = d

    def __repr__(self):
        return 'c{0:s}'.format(_format(self.x1, self.y1, self.x2, self.y2, self.x, self.y))

    def scale(self, s):
        self.x1 *= s[0]
        self.y1 *= s[1]
        self.x2 *= s[0]
        self.y2 *= s[1]
        self.x *= s[0]
        self.y *= s[1]

    def translate(self, d):
        pass # Do nothing since this is a relative distance

    def rotate(self, t):
        t = radians(t)
        x1, y1, x2, y2, x, y = self.x1, self.y1, self.x2, self.y2, self.x, self.y
        self.x1, self.y1 = x1 * cos(t) - y1 * sin(t), x1 * sin(t) + y1 * cos(t)
        self.x2, self.y2 = x2 * cos(t) - y2 * sin(t), x2 * sin(t) + y2 * cos(t)
        self.x, self.y = x * cos(t) - y * sin(t), x * sin(t) + y * cos(t)

    def skew_x(self, t):
        t = radians(t)
        self.x1 -= self.y1 * sin(t)
        self.x2 -= self.y2 * sin(t)
        self.x -= self.y * sin(t)

    def skew_y(self, t):
        t = radians(t)
        self.y1 += self.x1 * sin(t)
        self.y2 += self.x2 * sin(t)
        self.y += self.x * sin(t)

# Relative quadratic Bézier
class q:
    def __init__(self, d1, d):
        self.x1, self.y1 = d1
        self.x, self.y = d

    def __repr__(self):
        return 'q{0:s}'.format(_format(self.x1, self.y1, self.x, self.y))

    def scale(self, s):
        self.x1 *= s[0]
        self.y1 *= s[1]
        self.x *= s[0]
        self.y *= s[1]

    def translate(self, d):
        pass # Do nothing since this is a relative distance

    def rotate(self, t):
        t = radians(t)
        x1, y1, x, y = self.x1, self.y1, self.x, self.y
        self.x1, self.y1 = x1 * cos(t) - y1 * sin(t), x1 * sin(t) + y1 * cos(t)
        self.x, self.y = x * cos(t) - y * sin(t), x * sin(t) + y * cos(t)

    def skew_x(self, t):
        t = radians(t)
        self.x1 -= self.y1 * sin(t)
        self.x -= self.y * sin(t)

    def skew_y(self, t):
        t = radians(t)
        self.y1 += self.x1 * sin(t)
        self.y += self.x * sin(t)

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

# Format a list of coords as efficiently as possible
def _format(*args):
    return ''.join(f'{float(n): .3f}'.rstrip('0').rstrip('.') for n in args).lstrip()
