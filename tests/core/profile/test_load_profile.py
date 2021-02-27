# -*- coding: utf-8 -*-

import pathlib
from math import isclose

import pytest

from pykeyset import resources
from pykeyset.core.profile.load import (
    ProfileError,
    load_builtin,
    load_file,
    parse_bottom,
    parse_homing,
    parse_homing_bar,
    parse_homing_bump,
    parse_homing_scoop,
    parse_legend,
    parse_legend_type,
    parse_profile,
    parse_root,
    parse_top,
)
from pykeyset.core.profile.types import (
    HomingBar,
    HomingBump,
    HomingProperties,
    HomingScoop,
    HomingType,
    ProfileType,
    TextTypeProperty,
)
from pykeyset.utils import types

LEGEND = {
    "alpha": {
        "size": 5,
        "width": 12.5,
        "height": 12.5,
        "y-offset": 0,
    },
    "symbol": {
        "size": 3.5,
        "width": 12,
        "height": 12,
        "y-offset": 0.5,
    },
    "mod": {
        "size": 2.5,
        "width": 10,
        "height": 11,
        "y-offset": -0.5,
    },
}

LEGEND_DEFAULTS = {
    "width": 10,
    "height": 10,
    "alpha": {
        "size": 5,
    },
    "symbol": {
        "size": 3.5,
    },
    "mod": {
        "size": 2.5,
    },
}

ROOT = {
    "type": "cylindrical",
    "depth": 0.5,
    "bottom": {
        "width": 18.29,
        "height": 18.29,
        "radius": 0.38,
    },
    "top": {
        "width": 11.81,
        "height": 13.91,
        "radius": 1.52,
        "y-offset": -1.62,
    },
    "legend": LEGEND,
    "homing": {
        "default": "scoop",
        "scoop": {
            "depth": 1.5,
        },
        "bar": {
            "width": 3.85,
            "height": 0.4,
            "y-offset": 5.05,
        },
        "bump": {
            "radius": 0.2,
            "y-offset": -0.2,
        },
    },
}


@pytest.mark.parametrize(
    "dict, type, depth",
    [
        ({"type": "cylindrical", "depth": 2}, ProfileType.CYLINDRICAL, (2 / 19.05 * 1000)),
        ({"type": "spherical", "depth": 1.5}, ProfileType.SPHERICAL, (1.5 / 19.05 * 1000)),
        ({"type": "flat", "depth": 5}, ProfileType.FLAT, 0),
    ],
)
def test_parse_root(dict, type, depth):

    profile_type, profile_depth = parse_root("test", dict)

    assert profile_type == type
    assert isclose(profile_depth, depth)


@pytest.mark.parametrize(
    "dict",
    [
        {},
        {"type": "cylindrical", "depth": "2"},
        {"type": 5, "depth": 2},
        {"type": "invalid", "depth": 2},
    ],
)
def test_invalid_root(dict):

    with pytest.raises(ProfileError):
        _ = parse_root("test", dict)


def test_parse_bottom():

    bottom = parse_bottom({"width": 12, "height": 12, "radius": 1})

    assert isclose(bottom.x, 3525 / 19.05)
    assert isclose(bottom.y, 3525 / 19.05)
    assert isclose(bottom.w, 12000 / 19.05)
    assert isclose(bottom.h, 12000 / 19.05)
    assert isclose(bottom.r, 1000 / 19.05)


@pytest.mark.parametrize(
    "dict",
    [
        {},
        {"width": "12", "height": "12", "radius": "1"},
    ],
)
def test_invalid_bottom(dict):

    with pytest.raises(ProfileError):
        _ = parse_bottom(dict)


@pytest.mark.parametrize(
    "dict, result",
    [
        (
            {"width": 12, "height": 12, "radius": 1},
            types.RoundRect(3525 / 19.05, 3525 / 19.05, 12000 / 19.05, 12000 / 19.05, 1000 / 19.05),
        ),
        (
            {"width": 12, "height": 12, "radius": 1, "y-offset": -1},
            types.RoundRect(3525 / 19.05, 2525 / 19.05, 12000 / 19.05, 12000 / 19.05, 1000 / 19.05),
        ),
    ],
)
def test_parse_top(dict, result):

    top, offset = parse_top(dict)

    assert isclose(top.x, result.x)
    assert isclose(top.y, result.y)
    assert isclose(top.w, result.w)
    assert isclose(top.h, result.h)
    assert isclose(top.r, result.r)

    assert isclose(offset, dict.get("y-offset", 0) * 1000 / 19.05)


@pytest.mark.parametrize(
    "dict",
    [
        {},
        {"width": "12", "height": "12", "radius": "1"},
        {"width": 12, "height": 12, "radius": 1, "y-offset": "-1"},
    ],
)
def test_invalid_top(dict):

    with pytest.raises(ProfileError):
        _ = parse_top(dict)


@pytest.mark.parametrize(
    "dict, rects, sizes",
    [
        (
            LEGEND_DEFAULTS,
            TextTypeProperty(*([types.Rect(4525, 4525, 10000, 10000).scale(1 / 19.05)] * 3)),
            TextTypeProperty(5000 / 19.05, 3500 / 19.05, 2500 / 19.05),
        ),
        (
            LEGEND,
            TextTypeProperty(
                types.Rect(3275, 3275, 12500, 12500).scale(1 / 19.05),
                types.Rect(3525, 4025, 12000, 12000).scale(1 / 19.05),
                types.Rect(4525, 3525, 10000, 11000).scale(1 / 19.05),
            ),
            TextTypeProperty(5000 / 19.05, 3500 / 19.05, 2500 / 19.05),
        ),
    ],
)
def test_parse_legend(dict, rects, sizes):

    r, s = parse_legend(dict, 0)

    for result, expected in zip(r, rects):
        for res_size, exp_size in zip(result, expected):
            assert isclose(res_size, exp_size)

    for result, expected in zip(s, sizes):
        assert isclose(result, expected)


@pytest.mark.parametrize(
    "dict",
    [
        {"width": None},
        {"invalid": 12},
    ],
)
def test_invalid_legend(dict):

    with pytest.raises(ProfileError):
        _ = parse_legend(dict, 0)


def test_parse_legend_type():

    rect, size = parse_legend_type(
        "test",
        {"width": 10, "height": 10, "size": 4, "y-offset": -0.5},
        -500 / 19.05,
    )

    assert isclose(rect.x, 4525 / 19.05)
    assert isclose(rect.y, 3525 / 19.05)
    assert isclose(rect.w, 10000 / 19.05)
    assert isclose(rect.h, 10000 / 19.05)

    assert isclose(size, 4000 / 19.05)


@pytest.mark.parametrize(
    "dict",
    [
        {},
        {"width": "10", "height": "10", "size": "4"},
        {"width": 10, "height": 10, "size": 4, "y-offset": "-1"},
    ],
)
def test_invalid_legend_type(dict):

    with pytest.raises(ProfileError):
        _ = parse_legend_type("test", dict, 0)


@pytest.mark.parametrize(
    "dict, expected",
    [
        (
            {
                "default": "bar",
            },
            HomingProperties(HomingType.BAR, None, None, None),
        ),
        (
            {
                "default": "scoop",
                "scoop": {"depth": 0.5},
                "bar": {"width": 3, "height": 1, "y-offset": 4},
                "bump": {"radius": 0.5, "y-offset": 0.1},
            },
            HomingProperties(
                HomingType.SCOOP,
                HomingScoop(500 / 19.05),
                HomingBar(3000 / 19.05, 1000 / 19.05, 4000 / 19.05),
                HomingBump(500 / 19.05, 100 / 19.05),
            ),
        ),
    ],
)
def test_parse_homing(dict, expected):

    result = parse_homing(dict)

    assert expected.default == result.default

    for p in ("scoop", "bar", "bump"):
        if getattr(expected, p) is None:
            assert getattr(result, p) is None
        else:
            for exp, res in zip(getattr(expected, p), getattr(result, p)):
                assert isclose(exp, res)


@pytest.mark.parametrize(
    "dict",
    [
        {},
        {"default": "invalid"},
        {"default": "bar", "scoop": 2},
        {"default": "bar", "bar": None},
        {"default": "bar", "bump": "string"},
    ],
)
def test_invalid_homing(dict):

    with pytest.raises(ProfileError):
        _ = parse_homing(dict)


def test_parse_homing_scoop():

    result = parse_homing_scoop({"depth": 0.5})

    assert isclose(result.depth, 500 / 19.05)


@pytest.mark.parametrize(
    "dict",
    [
        {"depth": "2"},
        {"invalid": 1},
    ],
)
def test_invalid_homing_scoop(dict):

    with pytest.raises(ProfileError):
        _ = parse_homing_scoop(dict)


def test_parse_homing_bar():

    result = parse_homing_bar({"width": 3, "height": 1, "y-offset": 5})

    assert isclose(result.width, 3000 / 19.05)
    assert isclose(result.height, 1000 / 19.05)
    assert isclose(result.offset, 5000 / 19.05)


@pytest.mark.parametrize(
    "dict",
    [
        {"width": "3", "height": "1", "y-offset": "5"},
        {"invalid": 1},
    ],
)
def test_invalid_homing_bar(dict):

    with pytest.raises(ProfileError):
        _ = parse_homing_bar(dict)


def test_parse_homing_bump():

    result = parse_homing_bump({"radius": 0.5, "y-offset": 0.1})

    assert isclose(result.radius, 500 / 19.05)
    assert isclose(result.offset, 100 / 19.05)


@pytest.mark.parametrize(
    "dict",
    [
        {"radius": "0.5", "y-offset": "0.1"},
        {"invalid": 1},
    ],
)
def test_invalid_homing_bump(dict):

    with pytest.raises(ProfileError):
        _ = parse_homing_bump(dict)


def test_parse_profile():

    result = parse_profile("test", ROOT)

    assert result.name == "test"
    assert result.type == ProfileType.CYLINDRICAL
    assert isclose(result.depth, 500 / 19.05)

    # Only test 1 dimension as the rect parsing is tested separately anyway
    assert isclose(result.bottom.width, 18290 / 19.05)
    assert isclose(result.top.height, 13910 / 19.05)
    assert isclose(result.text_rect.symbol.y, 2405 / 19.05)
    assert isclose(result.text_size.alpha, 5000 / 19.05)
    assert result.homing.default == HomingType.SCOOP


def test_invalid_profile():

    with pytest.raises(ProfileError):
        _ = parse_profile("test", {"type": "cylindrical", "depth": 0.5})


def test_load_file():

    profile_root = pathlib.Path(resources.__file__).parent / "profiles"

    path = profile_root / "cherry.toml"
    _ = load_file(path)

    path = profile_root / "notfound.toml"
    with pytest.raises(IOError):
        _ = load_file(path)

    path = profile_root.parent / "fonts" / "cherry.xml"  # A file that does not parse as TOML
    with pytest.raises(ProfileError):
        _ = load_file(path)


def test_load_builtin():

    _ = load_builtin("cherry")

    with pytest.raises(ValueError):
        _ = load_builtin("notfound")
