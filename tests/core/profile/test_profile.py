# -*- coding: utf-8 -*-

from math import isclose
from xml.etree import ElementTree as et

import pytest

from pykeyset.core.kle import Key, KeyType
from pykeyset.core.profile.profile import Profile
from pykeyset.core.profile.types import (
    HomingBar,
    HomingBump,
    HomingProperties,
    HomingScoop,
    HomingType,
    ProfileType,
    TextTypeProperty,
)
from pykeyset.utils.types import Color, Rect, RoundRect, Vector

BTM_RECT = RoundRect(0, 0, 1000, 1000, 20)
TOP_RECT = RoundRect(200, 200, 600, 600, 100)
TXT_RECT = TextTypeProperty(
    Rect(200, 200, 600, 600),
    Rect(250, 250, 500, 500),
    Rect(300, 300, 400, 400),
)
TXT_SIZE = TextTypeProperty(100, 80, 60)
HOMING = HomingProperties(
    default=HomingType.BAR,
    scoop=HomingScoop(30),
    bar=HomingBar(200, 40, 200),
    bump=HomingBump(50, 0),
)


@pytest.fixture
def profile():
    return Profile(
        name="test",
        type=ProfileType.SPHERICAL,
        depth=10,
        bottom_rect=BTM_RECT,
        top_rect=TOP_RECT,
        text_rect=TXT_RECT,
        text_size=TXT_SIZE,
        homing=HOMING,
    )


def test_init(profile):
    assert profile.name == "test"
    assert profile.type == ProfileType.SPHERICAL
    assert profile.depth == 10
    assert profile.bottom == BTM_RECT
    assert profile.top == TOP_RECT
    assert profile.text_rect == TXT_RECT
    assert profile.text_size == TXT_SIZE
    assert profile.homing == HOMING
    assert profile.defs is None
    assert profile.gradients == []


@pytest.mark.parametrize(
    "key_type, key_size, result_type",
    [
        (KeyType.NORM, Vector(1, 1), ("rect", "path")),
        (KeyType.NORM, "iso", ("path", "path")),
        (KeyType.NORM, "step", ("rect", "path", "path")),
        (KeyType.NONE, Vector(1, 1), ()),
    ],
)
def test_key(profile, key_type, key_size, result_type):

    key = Key(
        pos=Vector(0, 0),
        size=key_size,
        type=key_type,
        legend=[""] * 9,
        legsize=[4] * 9,
        bgcol=Color(0.8, 0.2, 0.2),
        fgcol=Color(0.2, 0.2, 0.8),
    )

    g = et.Element("g")
    profile.key(key, g)

    assert len(g) == len(result_type)
    for el, type in zip(g, result_type):
        assert el.tag == type


@pytest.mark.parametrize(
    "text_size, key_size, key_type, rect",
    [
        (5, Vector(1, 1), KeyType.NORM, TXT_RECT.alpha),
        (4, Vector(1, 1), KeyType.NORM, TXT_RECT.symbol),
        (3, Vector(1, 1), KeyType.NORM, TXT_RECT.mod),
        (4, Vector(2, 1), KeyType.NORM, TXT_RECT.symbol._replace(w=TXT_RECT.symbol.w + 1000)),
        (4, "step", KeyType.NORM, TXT_RECT.symbol._replace(w=TXT_RECT.symbol.w + 250)),
        (
            4,
            "iso",
            KeyType.NORM,
            TXT_RECT.symbol._replace(
                x=TXT_RECT.symbol.x + 250,
                w=TXT_RECT.symbol.w + 250,
                h=TXT_RECT.symbol.h + 1000,
            ),
        ),
        (4, Vector(1, 1), KeyType.NONE, BTM_RECT),
    ],
)
def test_legend_rect(profile, text_size, key_size, key_type, rect):

    key = Key(
        pos=Vector(0, 0),
        size=key_size,
        type=key_type,
        legend=[""] * 9,
        legsize=[text_size] * 9,
        bgcol=Color(0.8, 0.2, 0.2),
        fgcol=Color(0.2, 0.2, 0.8),
    )

    assert profile.legend_rect(key, text_size) == rect


@pytest.mark.parametrize(
    "text_size, result",
    [
        (3, TXT_SIZE.mod),
        (4, TXT_SIZE.symbol),
        (5, TXT_SIZE.alpha),
        (1, TXT_SIZE.mod / 3),
        (9, TXT_SIZE.alpha * 1.8),
    ],
)
def test_legend_size(profile, text_size, result):

    assert isclose(profile.legend_size(text_size), result)


def test_draw_key_bottom(profile):

    g = et.Element("g")
    profile.draw_key_bottom(g, Vector(1, 1), Color(0.8, 0.2, 0.2))

    assert g.find("rect") is not None


@pytest.mark.parametrize(
    "key_type, profile_type, element_type",
    [
        (KeyType.NORM, ProfileType.CYLINDRICAL, "path"),
        (KeyType.SCOOP, ProfileType.CYLINDRICAL, "path"),
        (KeyType.SPACE, ProfileType.CYLINDRICAL, "path"),
        (KeyType.NORM, ProfileType.SPHERICAL, "path"),
        (KeyType.NORM, ProfileType.FLAT, "rect"),
    ],
)
def test_draw_key_top(profile, key_type, profile_type, element_type):

    profile.type = profile_type

    g = et.Element("g")
    profile.draw_key_top(g, key_type, Vector(1, 1), Color(0.8, 0.2, 0.2))

    assert g.find(element_type) is not None


def test_draw_iso_bottom(profile):

    g = et.Element("g")
    profile.draw_iso_bottom(g, Color(0.8, 0.2, 0.2))

    assert g.find("path") is not None


@pytest.mark.parametrize(
    "profile_type",
    [
        ProfileType.CYLINDRICAL,
        ProfileType.SPHERICAL,
        ProfileType.FLAT,
    ],
)
def test_draw_iso_top(profile, profile_type):

    profile.type = profile_type

    g = et.Element("g")
    profile.draw_iso_top(g, Color(0.8, 0.2, 0.2))

    assert g.find("path") is not None


def test_draw_step(profile):

    g = et.Element("g")
    profile.draw_step(g, Color(0.8, 0.2, 0.2))

    assert g.find("path") is not None
