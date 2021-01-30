# -*- coding: utf-8 -*-

import pathlib
from math import isclose
from xml.etree import ElementTree as et

import pytest

from pykeyset import resources
from pykeyset.core.font.load import (
    FontError,
    load_builtin,
    load_file,
    parse_font,
    parse_glyph,
    parse_kerning,
    parse_root,
)
from pykeyset.utils.path.path import Path

ROOT = et.Element(
    "test_root",
    {
        "horiz-adv-x": "500",
        "em-size": "1000",
        "x-height": "400",
        "cap-height": "600",
        "ascent": "600",
        "descent": "-100",
        "slope": "10",
    },
)

GLYPH = et.Element(
    "glyph",
    {
        "char": "A",
        "horiz-adv-x": "500",
        "transform": "scale(0.5, -0.5)",
        "path": "m50 0h400v400h-400z",
    },
)

KERNING = et.Element(
    "kern",
    {
        "u": "AB",
        "k": "20",
    },
)


def test_parse_root():

    font, advance = parse_root("test", ROOT)

    assert isclose(font.em_size, 1000)
    assert isclose(font.x_height, 400)
    assert isclose(font.cap_height, 600)
    assert isclose(font.slope, 10)

    assert isclose(advance, 500)


def test_invalid_root():

    root = et.Element(ROOT.tag, ROOT.attrib)

    root.attrib["horiz-adv-x"] = "a lot"
    with pytest.raises(FontError):
        parse_root("test", root)

    del root.attrib["horiz-adv-x"]
    _, advance = parse_root("test", root)
    assert advance is None

    root.attrib["x-height"] = "invalid"
    with pytest.raises(FontError):
        parse_root("test", root)

    del root.attrib["x-height"]
    with pytest.raises(FontError):
        parse_root("test", root)


def test_parse_glyph():

    element = et.Element(GLYPH.tag, GLYPH.attrib)
    glyph = parse_glyph(element, None)

    assert glyph.name == "A"
    assert isclose(glyph.advance, 500)
    assert isinstance(glyph.path, Path)
    assert isclose(glyph.path.boundingbox.x, 25)
    assert isclose(glyph.path.boundingbox.y, -200)
    assert isclose(glyph.path.boundingbox.w, 200)
    assert isclose(glyph.path.boundingbox.h, 200)

    del element.attrib["horiz-adv-x"]
    glyph = parse_glyph(element, 10)
    assert isclose(glyph.advance, 10)

    del element.attrib["transform"]
    glyph = parse_glyph(element, 10)


def test_invalid_glyph():

    element = et.Element(GLYPH.tag, GLYPH.attrib)

    element.set("horiz-adv-x", "invalid")
    with pytest.raises(FontError):
        _ = parse_glyph(element, None)

    del element.attrib["horiz-adv-x"]
    with pytest.raises(FontError):
        _ = parse_glyph(element, None)

    element.set("transform", "spin(20)")
    with pytest.raises(FontError):
        _ = parse_glyph(element, 10)

    del element.attrib["transform"]
    element.set("path", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaggggggggggggghhhhhhhh")
    with pytest.raises(FontError):
        _ = parse_glyph(element, 10)

    element.set("path", "m10 10")
    del element.attrib["char"]
    with pytest.raises(FontError):
        _ = parse_glyph(element, 10)


def test_parse_kerning():

    element = et.Element(KERNING.tag, KERNING.attrib)

    lhs, rhs, value = parse_kerning(element)

    assert lhs == "A"
    assert rhs == "B"
    assert isclose(value, 20)


def test_invalid_kerning():

    element = et.Element(KERNING.tag, KERNING.attrib)

    element.set("k", "twenty")
    with pytest.raises(FontError):
        _ = parse_kerning(element)

    element.set("u", "ABC")
    with pytest.raises(FontError):
        _ = parse_kerning(element)

    del element.attrib["u"]
    with pytest.raises(FontError):
        _ = parse_kerning(element)


def test_parse_font():

    root = et.Element(ROOT.tag, ROOT.attrib)
    glyph = et.Element(GLYPH.tag, GLYPH.attrib)
    kerning = et.Element(KERNING.tag, KERNING.attrib)
    root.extend([glyph, kerning])

    font = parse_font("test", root)
    assert font.name == "test"
    assert len(font._glyphs) == 1
    assert len(font.kerning) == 1

    kerning.set("k", "twenty")
    # Assert that this does not raise for invalid kerning, just skips it
    _ = parse_font("test", root)

    glyph.set("transform", "invalid")
    # Assert that this does not raise for invalid glyph, just skips it
    _ = parse_font("in font test", root)


def test_load_file():

    font_root = pathlib.Path(resources.__file__).parent / "fonts"

    path = font_root / "cherry.xml"
    _ = load_file(path)

    path = font_root / "notfound.xml"
    with pytest.raises(IOError):
        _ = load_file(path)

    path = font_root / "__init__.py"  # A file that does not parse as XML
    with pytest.raises(FontError):
        _ = load_file(path)


def test_load_builtin():

    _ = load_builtin("cherry")

    with pytest.raises(ValueError):
        _ = load_builtin("notfound")
