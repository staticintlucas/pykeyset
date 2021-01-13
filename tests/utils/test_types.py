# -*- coding: utf-8 -*-

from math import isclose, radians

import pytest

from pykeyset.utils.types import Color, Rect, RoundRect, Vector


def test_vector():

    vec = Vector(3, 4)
    assert isclose(vec.magnitude, 5)

    vec = Vector(1, 1)
    assert isclose(vec.angle, radians(45))


def test_rect():

    rect = Rect(1, 1, 2, 3)

    assert isclose(rect.x, 1)
    assert isclose(rect.y, 1)
    assert isclose(rect.w, 2)
    assert isclose(rect.h, 3)

    assert rect.width == rect.w
    assert rect.height == rect.h

    assert rect.position.x == rect.x
    assert rect.position.y == rect.y
    assert rect.size.x == rect.w
    assert rect.size.y == rect.h


def test_round_rect():

    round_rect = RoundRect(1, 2, 3, 4, 1)

    assert isclose(round_rect.x, 1)
    assert isclose(round_rect.y, 2)
    assert isclose(round_rect.w, 3)
    assert isclose(round_rect.h, 4)
    assert isclose(round_rect.r, 1)

    assert round_rect.radius == round_rect.r

    rect = round_rect.as_rect()

    assert rect.x == round_rect.x
    assert rect.y == round_rect.y
    assert rect.w == round_rect.w
    assert rect.h == round_rect.h


def test_rgb_to_hex():

    assert Color(0, 0.2, 0.4).to_hex() == "#003366"


def test_hex_to_rgb():

    color = Color.from_hex("#99ccff")

    assert isclose(color.r, 0.6)
    assert isclose(color.g, 0.8)
    assert isclose(color.b, 1.0)


def test_invalid():

    with pytest.raises(ValueError):
        Color(2, 3, 5)

    with pytest.raises(ValueError):
        Color(-1, True, "string lol")


def test_invalid_hex():

    with pytest.raises(ValueError):
        _ = Color.from_hex("#hexlol")

    with pytest.raises(ValueError):
        _ = Color.from_hex("#12345")


def test_3_digit_hex():

    color1 = Color.from_hex("#336699")
    color2 = Color.from_hex("#369")

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


def test_hightlight():

    color = Color(0.6, 0.6, 0.6).highlight(0.2)

    assert isclose(color.r, 0.4)
    assert isclose(color.g, 0.4)
    assert isclose(color.b, 0.4)

    color = Color(0.4, 0.4, 0.4).highlight(0.2)

    assert isclose(color.r, 0.6)
    assert isclose(color.g, 0.6)
    assert isclose(color.b, 0.6)


def test_invalid_amount():

    with pytest.raises(ValueError):
        _ = Color(0.8, 0.6, 0.2).lighter(2)

    with pytest.raises(ValueError):
        _ = Color(0.8, 0.6, 0.2).darker(-0.5)

    with pytest.raises(ValueError):
        _ = Color(0.8, 0.6, 0.2).highlight(0.8)

    with pytest.raises(TypeError):
        _ = Color(0.8, 0.6, 0.2).lighter("spaghetti")
