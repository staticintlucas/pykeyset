# -*- coding: utf-8 -*-

from math import radians, tan

import pytest

from pykeyset.utils.path import Path
from pykeyset.utils.types import Rect

A = 4 / 3 * tan(radians(90) / 4)


@pytest.mark.parametrize(
    "string, expected",
    [
        ("M 0 0", "M0 0"),
        ("m,0,0", "M0 0"),
        ("l 10 10", "l10 10"),
        ("L 10 10", "l10 10"),
        ("h10,", "l10 0"),
        ("H,10", "l10 0"),
        ("v,   10", "l0 10"),
        ("V 10.0", "l0 10"),
        ("c 5 0 10 5 10 10", "c5 0 10 5 10 10"),
        ("C -5 0 -10 5 -10 10", "c-5 0-10 5-10 10"),
        ("s 10 0 10 10", "q10 0 10 10"),
        ("c 5 0 10 5 10 10 S 15 20 20 20", "c5 0 10 5 10 10c0 5 5 10 10 10"),
        ("q 10 0 10 -10", "q10 0 10-10"),
        ("Q 0 10 10 10", "q0 10 10 10"),
        ("t 10 10", "l10 10"),
        ("q 10 0 10 10 T 20 20", "q10 0 10 10q0 10 10 10"),
        ("a 10 10 0 0 0 10 10", f"c0 {10 * A:.3f} {10 - 10 * A:.3f} 10 10 10"),
        ("A 1 1 0 0 0 2 0", f"c0 {A:.3f} {1 - A:.3f} 1 1 1c{A:.3f} 0 1-{1 - A:.3f} 1-1"),
        ("z", "z"),
        ("M0 0Z", "M0 0z"),
    ],
)
def test_string(string, expected):

    path = Path(string)

    assert str(path) == expected


@pytest.mark.parametrize(
    "string",
    [
        ("M 0 0 0"),
        ("p 0 5"),
        ("AAAAAAAAAAaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaagggggghhhhhhhhhhhh"),
    ],
)
def test_invalid(string):

    with pytest.raises(ValueError):
        _ = Path(string)


pathwithnobbox = Path("l 10 10")
pathwithnobbox._bbox = None


@pytest.mark.parametrize(
    "first, second, expected",
    [
        (Path("M0, 0"), Path("l 10 10"), "M0 0l10 10"),
        (Path("M0, 0"), Path(), "M0 0"),
        (Path("M0, 0"), pathwithnobbox, "M0 0l10 10"),
    ],
)
def test_append(first, second, expected):

    first.append(second)

    assert str(first) == expected


def test_setbbox():

    path = Path("M 0 0 l 10 10z")
    assert tuple(path.boundingbox) == (0, 0, 10, 10)

    path._recalculatebbox()
    assert tuple(path.boundingbox) == (0, 0, 10, 10)

    path.setboundingbox(Rect(-5, -5, 20, 20))
    assert tuple(path.boundingbox) == (-5, -5, 20, 20)

    with pytest.raises(ValueError):
        path._recalculatebbox()
    assert tuple(path.boundingbox) == (-5, -5, 20, 20)

    path = Path()
    path._recalculatebbox()
    assert path._bbox is None
    assert tuple(path.boundingbox) == (0, 0, 0, 0)


def test_copy():

    path1 = Path("M 0 0 l 10 10")
    path2 = path1.copy()

    path1.append(Path("M 0 0 l -10 -10"))

    assert tuple(path1.boundingbox) == (-10, -10, 20, 20)
    assert tuple(path2.boundingbox) == (0, 0, 10, 10)


@pytest.mark.parametrize(
    "transform, bbox",
    [
        ("", (0, 0, 40, 10)),
        ("scale(0.5)", (0, 0, 20, 5)),
        ("scale(-1, -2)", (-40, -20, 40, 20)),
        ("translate(20, 10)", (20, 10, 40, 10)),
        ("rotate(90)", (-10, 0, 10, 40)),
        ("skewX(-45)", (0, 0, 50, 10)),
        ("skewY(45)", (0, 0, 40, 50)),
    ],
)
def test_transform(transform, bbox):

    path = Path("M0 0l10 10c5 5 15 5 20 0q5 -5 10 0z")
    path.transform(transform)

    assert tuple(path.boundingbox) == bbox


@pytest.mark.parametrize(
    "transform",
    [
        ("flurp(20)"),
        ("translate(p)"),
        ("rotate(10, 20)"),
        ("I sense something; a presence I've not felt since— "),
    ],
)
def test_invalid_transform(transform):

    path = Path("M0 0l10 10c5 5 15 5 20 0q5 -5 10 0z")

    with pytest.raises(ValueError):
        path.transform(transform)
