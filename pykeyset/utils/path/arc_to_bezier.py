# -*- coding: utf-8 -*-

from math import atan2, ceil, cos, isclose, pi, radians, sin, sqrt, tan

from ...utils.types import Vector

TOL = 1e-6


def arc_to_bezier(r, xar, laf, sf, d):

    curves = []

    xar = radians(xar)

    if isclose(d.x, 0) and isclose(d.y, 0):
        return []

    d = Vector(d.x * cos(xar) + d.y * sin(xar), -d.x * sin(xar) + d.y * cos(xar))

    # Ensure our radii are large enough
    if isclose(r.x, 0, abs_tol=TOL) or isclose(r.y, 0, abs_tol=TOL):
        return [(Vector(d.x / 3, d.y / 3), Vector(2 * d.x / 3, 2 * d.y / 3), Vector(d.x, d.y))]
    else:
        lamb = sqrt((d.x / r.x / 2) ** 2 + (d.y / r.y / 2) ** 2)
        if lamb > 1:
            r = Vector(r.x * lamb, r.y * lamb)

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

    if xar != 0:
        for curve in curves:
            for i, d in enumerate(curve):
                curve[i] = Vector(d.x * cos(xar) - d.y * sin(xar), d.x * sin(xar) + d.y * cos(xar))

    return curves


def _get_center(r, laf, sf, d):

    # Since we only use half dx/dy in this calculation, pre-halve them
    d = Vector(d.x / 2, d.y / 2)

    sign = 1 if laf == sf else -1

    v = ((r.x * r.y) ** 2 - (r.x * d.y) ** 2 - (r.y * d.x) ** 2) / (
        (r.x * d.y) ** 2 + (r.y * d.x) ** 2
    )

    if isclose(v, 0):
        co = 0
    else:
        co = sign * sqrt(v)

    c = Vector(r.x * d.y / r.y * co + d.x, -r.y * d.x / r.x * co + d.y)

    return c


def _create_arc(r, phi0, dphi):

    a = 4 / 3 * tan(dphi / 4)

    x1, y1 = cos(phi0) * r.x, sin(phi0) * r.y
    x4, y4 = cos(phi0 + dphi) * r.x, sin(phi0 + dphi) * r.y

    x2, y2 = x1 - y1 * a, y1 + x1 * a
    x3, y3 = x4 + y4 * a, y4 - x4 * a

    return [
        Vector(x2 - x1, y2 - y1),
        Vector(x3 - x1, y3 - y1),
        Vector(x4 - x1, y4 - y1),
    ]
