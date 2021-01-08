# -*- coding: utf-8 -*-

from math import isclose, radians, tan

import pytest

from pykeyset.utils.path.arc_to_bezier import _create_arc, _get_center, arc_to_bezier
from pykeyset.utils.types import Dist, Point

A = 4 / 3 * tan(radians(90) / 4)


@pytest.mark.parametrize(
    "r, xar, laf, sf, d, results",
    [
        (Dist(1, 1), 0, False, False, Point(1, 1), [Point(1, 1)]),
        (Dist(1, 1), 0, True, False, Point(1, 1), [Point(-1, 1), Point(1, 1), Point(1, -1)]),
        (Dist(1, 1), 0, True, True, Point(1, 1), [Point(1, -1), Point(1, 1), Point(-1, 1)]),
        (Dist(1, 2), 0, False, False, Point(1, 2), [Point(1, 2)]),
        (Dist(1, 2), 90, False, False, Point(2, -1), [Point(2, -1)]),
        (Dist(1, 1), 0, False, False, Point(0, 0), []),
        (Dist(1.42, 1.42), 0, False, True, Point(0, -2), [Point(0, -2)]),
        (Dist(1.42, 1.42), 0, False, False, Point(0, 2), [Point(0, 2)]),
        (Dist(1, 1), 0, False, False, Point(4, 0), [Point(2, 2), Point(2, -2)]),
        (Dist(0, 0), 0, False, False, Point(1, 0), [Point(1, 0)]),
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
        (Dist(1, 1), False, False, Point(1, 1), Point(1, 0)),
        (Dist(1, 1), True, False, Point(1, 1), Point(0, 1)),
        (Dist(1, 1), False, True, Point(1, 1), Point(0, 1)),
        (Dist(1, 1), True, True, Point(1, 1), Point(1, 0)),
        (Dist(1, 1), False, False, Point(2, 0), Point(1, 0)),
    ],
)
def test_get_center(r, laf, sf, d, result):

    point = _get_center(r, laf, sf, d)

    assert isclose(point.x, result.x, abs_tol=1e-15)
    assert isclose(point.y, result.y, abs_tol=1e-15)


@pytest.mark.parametrize(
    "phi0, dphi, p1, p2, p",
    [
        (0, 90, Point(0, A), Point(A - 1, 1), Point(-1, 1)),
        (90, 90, Point(-A, 0), Point(-1, A - 1), Point(-1, -1)),
        (180, 90, Point(0, -A), Point(1 - A, -1), Point(1, -1)),
        (-90, 90, Point(A, 0), Point(1, 1 - A), Point(1, 1)),
        (0, -90, Point(0, -A), Point(A - 1, -1), Point(-1, -1)),
        (90, -90, Point(A, 0), Point(1, A - 1), Point(1, -1)),
        (180, -90, Point(0, A), Point(1 - A, 1), Point(1, 1)),
        (-90, -90, Point(-A, 0), Point(-1, 1 - A), Point(-1, 1)),
    ],
)
def test_create_arc(phi0, dphi, p1, p2, p):

    points = _create_arc(Dist(1, 1), radians(phi0), radians(dphi))

    assert len(points) == 3

    assert isclose(points[0].x, p1.x, abs_tol=1e-15)
    assert isclose(points[0].y, p1.y, abs_tol=1e-15)

    assert isclose(points[1].x, p2.x, abs_tol=1e-15)
    assert isclose(points[1].y, p2.y, abs_tol=1e-15)

    assert isclose(points[2].x, p.x, abs_tol=1e-15)
    assert isclose(points[2].y, p.y, abs_tol=1e-15)
