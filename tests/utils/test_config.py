# -*- coding: utf-8 -*-

import sys

import pytest

from pykeyset.utils.config import config, set_config
from pykeyset.utils.error import Verbosity


@pytest.fixture
def reset_config():
    # Reset the global configuration for each test
    set_config()


@pytest.mark.parametrize(
    "key, val",
    [
        ("color", sys.stderr.isatty()),
        ("profile", False),
        ("dpi", 96),
        ("verbosity", Verbosity.QUIET),
        ("showalign", False),
    ],
)
def test_default(reset_config, key, val):
    assert getattr(config, key) == val
