# -*- coding: utf-8 -*-

from math import ceil, cos, isclose, pi, radians, sin, sqrt, tan
from typing import List, Tuple

from ...utils.types import Vector

TOL = 1e-6


def arc_to_bezier(
    r: Vector, xar: float, laf: bool, sf: bool, d: Vector
) -> List[Tuple[Vector, Vector, Vector]]:

    curves = []

    xar = radians(xar)

    if isclose(d.x, 0, abs_tol=TOL) and isclose(d.y, 0, abs_tol=TOL):
        return []

    # Ensure our radii are large enough
    # If either radius is 0 we just return a straight line
    if isclose(r.x, 0, abs_tol=TOL) or isclose(r.y, 0, abs_tol=TOL):
        return [(d / 3, d * (2 / 3), d)]

    # Rotate the point by -xar. We calculate the result as if xar==0 and then re-rotate the result
    # It's a lot easier this way, I swear
    d = d.rotate(-xar)

    lamb = (d / (r * 2)).magnitude
    if lamb > 1:
        # Scale the radii to be just the right size, maintaining the ratio
        r = r * lamb

    c = _get_center(r, laf, sf, d)

    phi0 = (-c / r).angle
    dphi = ((d - c) / r).angle - phi0

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
    # TODO remove these? They shouldn't ever fail I think aside from the odd tolerance issue
    # if not laf and not sf:
    #     assert 0 >= dphi >= -pi
    # if not laf and sf:
    #     assert 0 <= dphi <= pi
    # if laf and not sf:
    #     assert -pi >= dphi >= -(2 * pi)
    # if laf and sf:
    #     assert pi <= dphi <= 2 * pi

    segments = ceil(abs(dphi / (pi / 2)) - TOL)  # Subtract TOL so 90.0001 deg doesn't become 2 segs
    dphi /= segments

    for _ in range(segments):
        curves.append(_create_arc(r, phi0, dphi))
        phi0 += dphi

    # Rotate result to match xar
    if xar != 0:
        for i, curve in enumerate(curves):
            curves[i] = tuple(d.rotate(xar) for d in curve)

    return curves


def _get_center(r: Vector, laf: bool, sf: bool, d: Vector) -> Vector:

    # Since we only use half dx/dy in this calculation, pre-halve them
    d = d / 2

    sign = 1 if laf == sf else -1

    expr = (r.x * d.y) ** 2 + (r.y * d.x) ** 2
    v = ((r.x * r.y) ** 2 - expr) / expr

    if isclose(v, 0, abs_tol=TOL):
        co = 0
    else:
        co = sign * sqrt(v)

    c = Vector(r.x * d.y / r.y, -r.y * d.x / r.x) * co + d

    return c


def _create_arc(r: Vector, phi0: float, dphi: float) -> Tuple[Vector, Vector, Vector]:

    a = 4 / 3 * tan(dphi / 4)

    d1 = Vector(cos(phi0), sin(phi0))
    d4 = Vector(cos(phi0 + dphi), sin(phi0 + dphi))

    d2 = Vector(d1.x - d1.y * a, d1.y + d1.x * a)
    d3 = Vector(d4.x + d4.y * a, d4.y - d4.x * a)

    return (
        r * (d2 - d1),
        r * (d3 - d1),
        r * (d4 - d1),
    )
