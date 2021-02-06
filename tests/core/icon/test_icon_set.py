# -*- coding: utf-8 -*-

from math import isclose

from pykeyset.core.icon.icon import Icon
from pykeyset.core.icon.icon_set import IconSet
from pykeyset.utils.path import Path
from pykeyset.utils.types import VerticalAlign


def test_init():

    icon_set = IconSet("test", 1000)

    assert icon_set.name == "test"
    assert icon_set.icon_size == 1000
    assert icon_set._icons == {}


def test_add_get_icon():

    font = IconSet("test", 1000)
    assert len(font) == 0

    glyph = Icon("A", Path("h20"))
    font.add_icon(glyph)
    assert len(font) == 1

    glyph = Icon("B", Path("h30"))
    font.add_icon(glyph)
    assert len(font) == 2

    glyph = Icon("C", Path("h40"))
    font.add_icon(glyph)
    assert len(font) == 3

    assert isclose(font.icon("A", 1000, 100, VerticalAlign.TOP).path.boundingbox.width, 20)
    assert isclose(font.icon("B", 1000, 100, VerticalAlign.MIDDLE).path.boundingbox.width, 30)
    assert isclose(font.icon("C", 1000, 100, VerticalAlign.BOTTOM).path.boundingbox.width, 40)

    assert font.icon("D", 1000, 100, VerticalAlign.TOP) is None
