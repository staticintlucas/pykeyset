# -*- coding: utf-8 -*-

import pytest

from pykeyset.utils import Severity
from pykeyset.utils.config import set_config
from pykeyset.utils.error import (
    KeysetIOError,
    KeysetTypeError,
    KeysetValueError,
    io_error,
    type_error,
    value_error,
)


@pytest.fixture
def set_config_fixture():
    # Set the global configuration for each test
    set_config(exceptlevel=Severity.DEBUG)


@pytest.mark.parametrize(
    "func, args, error",
    [
        (io_error, ("test", IOError()), KeysetIOError),
        (type_error, (1, str, "test", "test", TypeError()), KeysetTypeError),
        (value_error, (1, "something", "test", "test", ValueError()), KeysetValueError),
    ],
)
def test_error(set_config_fixture, func, args, error):

    with pytest.raises(error) as exc_info:
        func(*args)

    assert exc_info.value.message is not None
