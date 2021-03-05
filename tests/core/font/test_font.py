# -*- coding: utf-8 -*-

from math import isclose

from pykeyset.core.font.font import Font
from pykeyset.core.font.glyph import Glyph
from pykeyset.core.font.kerning import Kerning
from pykeyset.utils.path import Path


def test_init():

    font = Font("test", 1000, 600, 400, 1200, 0, 0)

    assert font.name == "test"
    assert font.em_size == 1000
    assert font.cap_height == 600
    assert font.x_height == 400
    assert font.line_height == 1200
    assert font.slope == 0
    assert font.char_spacing == 0
    assert font._glyphs == {}

    assert isinstance(font._replacement, Glyph)
    assert font._replacement.name == "�"
    assert isclose(font._replacement.path.boundingbox.x, 73 * (600 / 726))
    assert isclose(font._replacement.path.boundingbox.y, -726 * (600 / 726))
    assert isclose(font._replacement.path.boundingbox.w, 520 * (600 / 726))
    assert isclose(font._replacement.path.boundingbox.h, 726 * (600 / 726))
    assert isclose(font._replacement.advance, 638 * (600 / 726))

    assert isinstance(font.kerning, Kerning)
    assert len(font.kerning) == 0


def test_add_get_glyph():

    font = Font("test", 1000, 600, 400, 1200, 0, 0)
    assert len(font) == 0

    glyph = Glyph("A", Path(), 200)
    font.add_glyph(glyph)
    assert len(font) == 1

    glyph = Glyph("B", Path(), 300)
    font.add_glyph(glyph)
    assert len(font) == 2

    glyph = Glyph("C", Path(), 400)
    font.add_glyph(glyph)
    assert len(font) == 3

    assert isclose(font.glyph("A", 600).advance, 200)
    assert isclose(font.glyph("B", 600).advance, 300)
    assert isclose(font.glyph("C", 600).advance, 400)

    assert font.glyph("D", 600) is None

    assert isclose(font.replacement(726).advance, 638)


def test_line_spacing():

    font = Font("test", 1000, 600, 400, 1200, 0, 0)

    assert isclose(font.line_spacing(10), 20)
