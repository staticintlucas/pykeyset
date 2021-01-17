# -*- coding: utf-8 -*-

from math import isclose, radians, tan

import pytest

from pykeyset.utils.path.arc_to_bezier import _create_arc, _get_center, arc_to_bezier
from pykeyset.utils.types import Vector

A = 4 / 3 * tan(radians(90) / 4)


@pytest.mark.parametrize(
    "r, xar, laf, sf, d, results",
    [
        (Vector(1, 1), 0, False, False, Vector(1, 1), [Vector(1, 1)]),
        (Vector(1, 1), 0, True, False, Vector(1, 1), [Vector(-1, 1), Vector(1, 1), Vector(1, -1)]),
        (Vector(1, 1), 0, True, True, Vector(1, 1), [Vector(1, -1), Vector(1, 1), Vector(-1, 1)]),
        (Vector(1, 1), 0, True, True, Vector(1, -1), [Vector(-1, -1), Vector(1, -1), Vector(1, 1)]),
        (Vector(1, 2), 0, False, False, Vector(1, 2), [Vector(1, 2)]),
        (Vector(1, 2), 90, False, False, Vector(2, -1), [Vector(2, -1)]),
        (Vector(1, 1), 0, False, False, Vector(0, 0), []),
        (Vector(1.42, 1.42), 0, False, True, Vector(0, -2), [Vector(0, -2)]),
        (Vector(1.42, 1.42), 0, False, False, Vector(0, 2), [Vector(0, 2)]),
        (Vector(1, 1), 0, False, False, Vector(4, 0), [Vector(2, 2), Vector(2, -2)]),
        (Vector(0, 0), 0, False, False, Vector(1, 0), [Vector(1, 0)]),
    ],
)
def test_arc_to_bezier(r, xar, laf, sf, d, results):

    points = [p[-1] for p in arc_to_bezier(r, xar, laf, sf, d)]

    assert len(points) == len(results)

    for pt, res in zip(points, results):
        assert isclose(pt.x, res.x, abs_tol=1e-15)
        assert isclose(pt.y, res.y, abs_tol=1e-15)


@pytest.mark.parametrize(
    "r, laf, sf, d, result",
    [
        (Vector(1, 1), False, False, Vector(1, 1), Vector(1, 0)),
        (Vector(1, 1), True, False, Vector(1, 1), Vector(0, 1)),
        (Vector(1, 1), False, True, Vector(1, 1), Vector(0, 1)),
        (Vector(1, 1), True, True, Vector(1, 1), Vector(1, 0)),
        (Vector(1, 1), False, False, Vector(2, 0), Vector(1, 0)),
    ],
)
def test_get_center(r, laf, sf, d, result):

    point = _get_center(r, laf, sf, d)

    assert isclose(point.x, result.x, abs_tol=1e-15)
    assert isclose(point.y, result.y, abs_tol=1e-15)


@pytest.mark.parametrize(
    "r, phi0, dphi, p1, p2, p",
    [
        (Vector(1, 1), 0, 90, Vector(0, A), Vector(A - 1, 1), Vector(-1, 1)),
        (Vector(1, 1), 90, 90, Vector(-A, 0), Vector(-1, A - 1), Vector(-1, -1)),
        (Vector(1, 1), 180, 90, Vector(0, -A), Vector(1 - A, -1), Vector(1, -1)),
        (Vector(1, 1), -90, 90, Vector(A, 0), Vector(1, 1 - A), Vector(1, 1)),
        (Vector(1, 1), 0, -90, Vector(0, -A), Vector(A - 1, -1), Vector(-1, -1)),
        (Vector(1, 1), 90, -90, Vector(A, 0), Vector(1, A - 1), Vector(1, -1)),
        (Vector(1, 1), 180, -90, Vector(0, A), Vector(1 - A, 1), Vector(1, 1)),
        (Vector(1, 1), -90, -90, Vector(-A, 0), Vector(-1, 1 - A), Vector(-1, 1)),
        (Vector(2, 1), 0, 90, Vector(0, A), Vector(2 * (A - 1), 1), Vector(-2, 1)),
    ],
)
def test_create_arc(r, phi0, dphi, p1, p2, p):

    points = _create_arc(r, radians(phi0), radians(dphi))

    assert len(points) == 3

    assert isclose(points[0].x, p1.x, abs_tol=1e-15)
    assert isclose(points[0].y, p1.y, abs_tol=1e-15)

    assert isclose(points[1].x, p2.x, abs_tol=1e-15)
    assert isclose(points[1].y, p2.y, abs_tol=1e-15)

    assert isclose(points[2].x, p.x, abs_tol=1e-15)
    assert isclose(points[2].y, p.y, abs_tol=1e-15)
