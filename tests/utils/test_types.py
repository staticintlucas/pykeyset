# -*- coding: utf-8 -*-

from math import isclose

import pytest

from pykeyset.utils.types import Color


def test_invalid():

    with pytest.raises(ValueError):
        Color(0, 0.2)

    with pytest.raises(ValueError):
        Color(2, 3, 5)

    with pytest.raises(ValueError):
        Color("string lol")


def test_rgb_to_hex():

    assert str(Color(0, 0.2, 0.4)) == "#003366"


def test_hex_to_rgb():

    color = Color("#99ccff")

    assert isclose(color.r, 0.6)
    assert isclose(color.g, 0.8)
    assert isclose(color.b, 1.0)


def test_3_digit_hex():

    color1 = Color("#336699")
    color2 = Color("#369")

    assert isclose(color1.r, color2.r)
    assert isclose(color1.g, color2.g)
    assert isclose(color1.b, color2.b)


def test_lighter():

    color = Color(0.8, 0.6, 0.2).lighter(0.2)

    assert isclose(color.r, 0.84)
    assert isclose(color.g, 0.68)
    assert isclose(color.b, 0.36)


def test_darker():

    color = Color(0.8, 0.6, 0.2).darker(0.2)

    assert isclose(color.r, 0.64)
    assert isclose(color.g, 0.48)
    assert isclose(color.b, 0.16)
