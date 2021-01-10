# -*- coding: utf-8 -*-

import pytest

from pykeyset.utils import Severity
from pykeyset.utils.config import set_config
from pykeyset.utils.logging import print_error


@pytest.mark.parametrize(
    "message, severity, file, code",
    [
        ("test", Severity.FATAL, "test", "\x1b[31m"),
        ("test", Severity.WARNING, None, "\x1b[33m"),
        ("test", Severity.INFO, "test", "\x1b[34m"),
        ("test", Severity.DEBUG, None, "\x1b[35m"),
    ],
)
def test_color(capsys, message, severity, file, code):

    set_config(color=True)

    print_error(message, severity, file)
    stderr = capsys.readouterr().err

    assert code in stderr


@pytest.mark.parametrize(
    "message, severity, file",
    [
        ("test", Severity.FATAL, "test"),
        ("test", Severity.WARNING, None),
        ("test", Severity.INFO, "test"),
        ("test", Severity.DEBUG, None),
    ],
)
def test_no_color(capsys, message, severity, file):

    set_config(color=False)

    print_error(message, severity, file)
    stderr = capsys.readouterr().err

    assert "\x1b" not in stderr
