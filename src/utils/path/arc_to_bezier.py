# coding: utf-8

from math import radians, cos, sin, tan, atan2, pi
from math import sqrt, ceil, isclose


TOL = 1e-6


def arc_to_bezier(r, xar, laf, sf, d):

    curves = []

    rx, ry = r
    dx, dy = d
    xar = radians(xar)

    if isclose(dx, 0) and isclose(dy, 0):
        return []

    dx, dy = dx * cos(xar) + dy * sin(xar), -dx * sin(xar) + dy * cos(xar)

    # Ensure our radii are large enough
    lamb = sqrt((dx / rx / 2) ** 2 + (dy / ry / 2) ** 2)
    if lamb > 1:
        rx *= lamb
        ry *= lamb

    cx, cy = _get_center((rx, ry), laf, sf, (dx, dy))

    phi0 = atan2(0 - cy, 0 - cx)
    dphi = atan2(dy - cy, dx - cx) - phi0

    if laf:
        dphi += (2 * pi) if dphi < 0 else (-2 * pi)

    if not laf and not sf: assert(0 <= dphi <= pi)
    if not laf and sf: assert(0 >= dphi >= -pi)
    if laf and not sf: assert(pi <= dphi <= 2 * pi)
    if laf and sf: assert(-pi >= dphi >= -2 * pi)

    segments = ceil(abs(dphi / (pi / 2)) - TOL)
    dphi /= segments

    for _ in range(segments):
        curves.append(_create_arc((rx, ry), phi0, dphi))
        phi0 += dphi

    return curves


def _get_center(r, laf, sf, d):

    (rx, ry), (dx, dy) = r, d

    # Since we only use half dx/dy in this calculation, pre-halve them
    dx = dx / 2
    dy = dy / 2

    sign = -1 if laf == sf else 1

    v = ((rx * ry) ** 2 - (rx * dy) ** 2 - (ry * dx) ** 2) / ((rx * dy) ** 2 + (ry * dx) ** 2)

    if isclose(v, 0):
        co = 0
    else:
        co = sign * sqrt(v)

    cx, cy = rx * dy / ry * co, -ry * dx / rx * co

    return cx + dx, cy + dy


def _create_arc(r, phi0, dphi):

    rx, ry = r
    a = 4 / 3 * tan(dphi / 4)

    x1, y1 = cos(phi0) * rx, sin(phi0) * ry
    x4, y4 = cos(phi0 + dphi) * rx, sin(phi0 + dphi) * ry

    x2, y2 = x1 - y1 * a, y1 + x1 * a
    x3, y3 = x4 + y4 * a, y4 - x4 * a

    return [
        (x2 - x1, y2 - y1),
        (x3 - x1, y3 - y1),
        (x4 - x1, y4 - y1),
    ]
