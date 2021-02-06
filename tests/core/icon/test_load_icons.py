# -*- coding: utf-8 -*-

import pathlib
from math import isclose
from xml.etree import ElementTree as et

import pytest

from pykeyset import resources
from pykeyset.core.icon.load import (
    IconError,
    load_builtin,
    load_file,
    parse_icon,
    parse_icon_set,
    parse_root,
)
from pykeyset.utils.path.path import Path

ROOT = et.Element("test_root", {"key-size": "1000"})
GLYPH = et.Element(
    "icon",
    {
        "name": "A",
        "transform": "scale(0.5, -0.5)",
        "path": "m50 0h400v400h-400z",
    },
)


def test_parse_root():

    icon_set = parse_root("test", ROOT)

    assert isclose(icon_set.icon_size, 1000)


def test_invalid_root():

    root = et.Element(ROOT.tag, ROOT.attrib)

    root.attrib["key-size"] = "a lot"
    with pytest.raises(IconError):
        parse_root("test", root)

    del root.attrib["key-size"]
    with pytest.raises(IconError):
        _ = parse_root("test", root)


def test_parse_glyph():

    element = et.Element(GLYPH.tag, GLYPH.attrib)
    icon = parse_icon(element)

    assert icon.name == "A"
    assert isinstance(icon.path, Path)
    assert isclose(icon.path.boundingbox.x, 25)
    assert isclose(icon.path.boundingbox.y, -200)
    assert isclose(icon.path.boundingbox.w, 200)
    assert isclose(icon.path.boundingbox.h, 200)

    del element.attrib["transform"]
    icon = parse_icon(element)
    assert isclose(icon.path.boundingbox.x, 50)
    assert isclose(icon.path.boundingbox.y, 0)
    assert isclose(icon.path.boundingbox.w, 400)
    assert isclose(icon.path.boundingbox.h, 400)

    element.attrib["bbox"] = "0 10 20 40"
    icon = parse_icon(element)
    assert isclose(icon.path.boundingbox.x, 0)
    assert isclose(icon.path.boundingbox.y, 10)
    assert isclose(icon.path.boundingbox.w, 20)
    assert isclose(icon.path.boundingbox.h, 40)


def test_invalid_glyph():

    element = et.Element(GLYPH.tag, GLYPH.attrib)

    element.set("bbox", "invalid")
    with pytest.raises(IconError):
        _ = parse_icon(element)

    del element.attrib["bbox"]
    element.set("transform", "spin(20)")
    with pytest.raises(IconError):
        _ = parse_icon(element)

    del element.attrib["transform"]
    element.set("path", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaggggggggggggghhhhhhhh")
    with pytest.raises(IconError):
        _ = parse_icon(element)

    element.set("path", "m10 10")
    del element.attrib["name"]
    with pytest.raises(IconError):
        _ = parse_icon(element)


def test_parse_font():

    root = et.Element(ROOT.tag, ROOT.attrib)
    glyph = et.Element(GLYPH.tag, GLYPH.attrib)
    root.append(glyph)

    font = parse_icon_set("test", root)
    assert font.name == "test"
    assert len(font._icons) == 1

    glyph.set("path", "twenty")
    # Assert that this does not raise for invalid kerning, just skips it
    _ = parse_icon_set("test", root)

    glyph.set("transform", "invalid")
    # Assert that this does not raise for invalid glyph, just skips it
    _ = parse_icon_set("in font test", root)


def test_load_file():

    font_root = pathlib.Path(resources.__file__).parent / "icons"

    path = font_root / "cherry.xml"
    _ = load_file(path)

    path = font_root / "notfound.xml"
    with pytest.raises(IOError):
        _ = load_file(path)

    path = font_root / "__init__.py"  # A file that does not parse as XML
    with pytest.raises(IconError):
        _ = load_file(path)


def test_load_builtin():

    _ = load_builtin("cherry")

    with pytest.raises(ValueError):
        _ = load_builtin("notfound")
