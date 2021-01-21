# -*- coding: utf-8 -*-

import pytest

from pykeyset.utils import Verbosity
from pykeyset.utils.config import config, set_config


@pytest.mark.parametrize(
    "key, val",
    [
        ("color", None),
        ("profile", False),
        ("dpi", 96),
        ("verbosity", Verbosity.NONE),
        ("show_align", False),
    ],
)
def test_default(key, val):
    assert getattr(config(), key) == val


@pytest.mark.parametrize(
    "key, val",
    [
        ("color", True),
        ("profile", True),
        ("dpi", 192),
        ("verbosity", Verbosity.NORMAL),
        ("show_align", True),
    ],
)
def test_set_config(key, val):

    set_config(**{key: val})

    assert getattr(config(), key) == val


def test_set_unknown_config():

    with pytest.raises(ValueError):
        set_config(unknown="value")
