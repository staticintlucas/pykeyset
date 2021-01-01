# coding: utf-8

from math import radians, cos, sin, tan, atan2, pi
from math import sqrt, ceil, isclose, copysign

from ...utils.types import Dist, Point


TOL = 1e-6


def arc_to_bezier(r, xar, laf, sf, d):

    curves = []

    r = Dist(*r)
    d = Point(*d)
    xar = radians(xar)

    if isclose(d.x, 0) and isclose(d.y, 0):
        return []

    d = Point(d.x * cos(xar) + d.y * sin(xar), -d.x * sin(xar) + d.y * cos(xar))

    # Ensure our radii are large enough
    lamb = sqrt((d.x / r.x / 2) ** 2 + (d.y / r.y / 2) ** 2)
    if lamb > 1:
        r.x *= lamb
        r.y *= lamb

    c = _get_center(r, laf, sf, d)

    phi0 = atan2((0 - c.y) / r.y, (0 - c.x) / r.x)
    dphi = atan2((d.y - c.y) / r.y, (d.x - c.x) / r.x) - phi0

    if laf:
        if sf:
            if dphi < pi:
                dphi += 2 * pi
        else:
            if dphi > -pi:
                dphi -= 2 * pi
    else:
        if sf:
            if dphi < 0:
                dphi += 2 * pi
        else:
            if dphi > 0:
                dphi -= 2 * pi

    if not laf and not sf:
        assert 0 >= dphi >= -pi
    if not laf and sf:
        assert 0 <= dphi <= pi
    if laf and not sf:
        assert -pi >= dphi >= -(2 * pi)
    if laf and sf:
        assert pi <= dphi <= 2 * pi

    segments = ceil(abs(dphi / (pi / 2)) - TOL)
    dphi /= segments

    for _ in range(segments):
        curves.append(_create_arc(r, phi0, dphi))
        phi0 += dphi

    return curves


def _get_center(r, laf, sf, d):

    r = Dist(*r)
    d = Point(*d)

    # Since we only use half dx/dy in this calculation, pre-halve them
    d.x = d.x / 2
    d.y = d.y / 2

    sign = 1 if laf == sf else -1

    v = ((r.x * r.y) ** 2 - (r.x * d.y) ** 2 - (r.y * d.x) ** 2) / (
        (r.x * d.y) ** 2 + (r.y * d.x) ** 2
    )

    if isclose(v, 0):
        co = 0
    else:
        co = sign * sqrt(v)

    c = Point(r.x * d.y / r.y * co + d.x, -r.y * d.x / r.x * co + d.y)

    return c


def _create_arc(r, phi0, dphi):

    a = 4 / 3 * tan(dphi / 4)

    x1, y1 = cos(phi0) * r.x, sin(phi0) * r.y
    x4, y4 = cos(phi0 + dphi) * r.x, sin(phi0 + dphi) * r.y

    x2, y2 = x1 - y1 * a, y1 + x1 * a
    x3, y3 = x4 + y4 * a, y4 - x4 * a

    return [
        Point(x2 - x1, y2 - y1),
        Point(x3 - x1, y3 - y1),
        Point(x4 - x1, y4 - y1),
    ]
