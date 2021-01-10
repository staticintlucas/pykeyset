# -*- coding: utf-8 -*-

import pytest

from pykeyset.utils.config import config, set_config
from pykeyset.utils.error import Verbosity


@pytest.mark.parametrize(
    "key, val",
    [
        ("color", None),
        ("profile", False),
        ("dpi", 96),
        ("verbosity", Verbosity.NONE),
        ("showalign", False),
    ],
)
def test_default(reset_config_fixture, key, val):
    assert getattr(config(), key) == val


@pytest.mark.parametrize(
    "key, val",
    [
        ("color", True),
        ("profile", True),
        ("dpi", 192),
        ("verbosity", Verbosity.NORMAL),
        ("showalign", True),
    ],
)
def test_set_config(reset_config_fixture, key, val):

    set_config(**{key: val})

    assert getattr(config(), key) == val


def test_set_unknown_config(reset_config_fixture):

    with pytest.raises(ValueError):
        set_config(unknown="value")
