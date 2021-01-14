# -*- coding: utf-8 -*-

from math import atan2, ceil, cos, isclose, pi, radians, sin, sqrt, tan

from ...utils.types import Vector

TOL = 1e-6


def arc_to_bezier(r, xar, laf, sf, d):

    curves = []

    xar = radians(xar)

    if isclose(d.x, 0) and isclose(d.y, 0):
        return []

    # Rotate the point by -xar. We calculate the result as if xar==0 and then re-rotate the result
    # It's a lot easier this way, I swear
    d = Vector(d.x * cos(xar) + d.y * sin(xar), -d.x * sin(xar) + d.y * cos(xar))

    # Ensure our radii are large enough
    # If either radius is 0 we just return a straight line
    if isclose(r.x, 0, abs_tol=TOL) or isclose(r.y, 0, abs_tol=TOL):
        return [(Vector(d.x / 3, d.y / 3), Vector(2 * d.x / 3, 2 * d.y / 3), Vector(d.x, d.y))]
    else:
        lamb = sqrt((d.x / r.x / 2) ** 2 + (d.y / r.y / 2) ** 2)
        if lamb > 1:
            # Scale the radii to be just the right size, maintaining the ratio
            r = Vector(r.x * lamb, r.y * lamb)

    c = _get_center(r, laf, sf, d)

    phi0 = atan2((0 - c.y) / r.y, (0 - c.x) / r.x)
    dphi = atan2((d.y - c.y) / r.y, (d.x - c.x) / r.x) - phi0

    # Add and subtract 2pi (360 deg) to make sure dphi is the correct angle to sweep
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

    # Double checks the quadrant of dphi
    # TODO remove these? They shouldn't ever fail I think
    if not laf and not sf:
        assert 0 >= dphi >= -pi
    if not laf and sf:
        assert 0 <= dphi <= pi
    if laf and not sf:
        assert -pi >= dphi >= -(2 * pi)
    if laf and sf:
        assert pi <= dphi <= 2 * pi

    segments = ceil(abs(dphi / (pi / 2)) - TOL)  # Subtract TOL so 90.0001 deg doesn't become 2 segs
    dphi /= segments

    for _ in range(segments):
        curves.append(_create_arc(r, phi0, dphi))
        phi0 += dphi

    # Rotate result to match xar
    if xar != 0:
        for curve in curves:
            for i, d in enumerate(curve):
                curve[i] = Vector(d.x * cos(xar) - d.y * sin(xar), d.x * sin(xar) + d.y * cos(xar))

    return curves


def _get_center(r, laf, sf, d):

    # Since we only use half dx/dy in this calculation, pre-halve them
    d = d / 2

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

    d1 = Vector(cos(phi0) * r.x, sin(phi0) * r.y)
    d4 = Vector(cos(phi0 + dphi) * r.x, sin(phi0 + dphi) * r.y)

    d2 = Vector(d1.x - d1.y * a, d1.y + d1.x * a)
    d3 = Vector(d4.x + d4.y * a, d4.y - d4.x * a)

    return [
        d2 - d1,
        d3 - d1,
        d4 - d1,
    ]
