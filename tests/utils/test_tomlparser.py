# -*- coding: utf-8 -*-

import pytest

from pykeyset.utils import tomlparser
from pykeyset.utils.tomlparser import TomlNode


@pytest.fixture
def toml_str():
    return """
        [section]
        key = "value"
        """


@pytest.fixture
def toml_node():
    return TomlNode({"section": {"key": "value"}})


def test_load(tmp_path, toml_str, toml_node):
    d = tmp_path / "pykeyset_test"
    d.mkdir()
    f = d / "test.toml"
    f.write_text(toml_str)

    toml = tomlparser.load(f)

    assert toml == toml_node


def test_loads(toml_str, toml_node):
    toml = tomlparser.loads(toml_str)

    assert toml == toml_node


def test_set_get_del(toml_node):

    assert toml_node["section"].get("key", "default") == "value"

    toml_node["section"]["key"] = "another value"
    assert toml_node["section"].get("key", "default") == "another value"

    assert toml_node["section"].get("unknown", "default") == "default"

    toml_node["section"]["unknown"] = "now known"
    assert toml_node["section"].get("unknown", "default") == "now known"

    del toml_node["section"]["unknown"]
    with pytest.raises(KeyError):
        toml_node["section"]["unknown"]

    with pytest.raises(KeyError):
        del toml_node["section"]["unknown"]


def test_iter_len(toml_node):

    keys = []
    values = []

    for k, v in toml_node["section"].items():
        keys.append(k)
        values.append(v)

    assert len(keys) == len(toml_node)
    assert len(values) == len(toml_node)

    assert keys == ["key"]
    assert values == ["value"]


def test_getsection(toml_node):

    section = toml_node.getsection("section")

    with pytest.raises(KeyError):
        _ = toml_node.getsection("doesn't exist")

    with pytest.raises(KeyError):
        _ = section.getsection("key")


def test_getkey(toml_node):

    section = toml_node["section"]

    assert section.getkey("key") == "value"

    assert section.getkey("not found", default="hi") == "hi"

    with pytest.raises(KeyError):
        _ = toml_node.getkey("section")

    with pytest.raises(KeyError):
        _ = section.getkey("404")

    with pytest.raises(ValueError):
        _ = section.getkey("key", int)


def test_contains(toml_node):

    assert "section" in toml_node

    assert "other key" not in toml_node
