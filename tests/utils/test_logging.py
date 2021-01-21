# -*- coding: utf-8 -*-

import pytest
import typer

from pykeyset.utils import Severity, Verbosity
from pykeyset.utils.config import set_config
from pykeyset.utils.logging import (
    debug,
    error,
    format_error,
    info,
    print_message,
    warning,
)


def test_error(capsys):

    set_config(verbosity=Verbosity.QUIET, is_script=True)
    with pytest.raises(typer.Exit):
        error(ValueError("test"), "file")
    stderr = capsys.readouterr().err
    assert stderr.startswith("Error")

    set_config(verbosity=Verbosity.NONE)
    with pytest.raises(typer.Exit):
        error(ValueError("test"), "file")
    stderr = capsys.readouterr().err
    assert len(stderr) == 0

    set_config(is_script=False)
    with pytest.raises(ValueError) as e:
        error(ValueError("test"), "file")
    assert e.value.__cause__ is None

    prev_except = IOError("prev")
    with pytest.raises(ValueError) as e:
        error(ValueError("test"), "file", prev_except)
    assert e.value.__cause__ is prev_except


def test_warning(capsys):

    set_config(verbosity=Verbosity.QUIET, is_script=True)
    warning(ValueError("test"), "ignoring", "file")
    stderr = capsys.readouterr().err
    assert len(stderr) == 0

    set_config(verbosity=Verbosity.NORMAL)
    warning(ValueError("test"), "ignoring", "file")
    stderr = capsys.readouterr().err
    assert stderr.startswith("Warning")
    assert "ignoring" in stderr

    set_config(raise_warnings=True)
    with pytest.raises(typer.Exit):
        warning(ValueError("test"), "ignoring", "file")
    stderr = capsys.readouterr().err
    assert stderr.startswith("Warning")
    assert "ignoring" not in stderr

    set_config(is_script=False)
    with pytest.raises(ValueError):
        warning(ValueError("test"), "ignoring", "file")
    stderr = capsys.readouterr().err


def test_info(capsys):

    set_config(verbosity=Verbosity.NORMAL)
    info("test", "file")
    stderr = capsys.readouterr().err
    assert len(stderr) == 0

    set_config(verbosity=Verbosity.VERBOSE)
    info("test", "file")
    stderr = capsys.readouterr().err
    assert stderr.startswith("Info")


def test_debug(capsys):

    set_config(verbosity=Verbosity.VERBOSE)
    debug("test", "file")
    stderr = capsys.readouterr().err
    assert len(stderr) == 0

    set_config(verbosity=Verbosity.DEBUG)
    debug("test", "file")
    stderr = capsys.readouterr().err
    assert stderr.startswith("Debug")


@pytest.mark.parametrize(
    "error, string",
    [
        (ValueError("error"), "error"),
        (
            IOError(1, "file not found", "filename"),
            "cannot open file [bold magenta]filename[/bold magenta]: file not found",
        ),
        (IOError(1, "strerror"), "strerror"),
        (IOError("Just a message"), "just a message"),
    ],
)
def test_format_error(error, string):

    assert format_error(error) == string


@pytest.mark.parametrize(
    "message, severity, file, code",
    [
        ("test", Severity.ERROR, "test", "\x1b[1;31m"),
        ("test", Severity.WARNING, None, "\x1b[1;33m"),
        ("test", Severity.INFO, "test", "\x1b[1;34m"),
        ("test", Severity.DEBUG, None, "\x1b[1;2m"),
    ],
)
def test_color(capsys, message, severity, file, code):

    set_config(color=True)

    print_message(message, severity, file)
    stderr = capsys.readouterr().err

    assert code in stderr


@pytest.mark.parametrize(
    "message, severity, file",
    [
        ("test", Severity.ERROR, "test"),
        ("test", Severity.WARNING, None),
        ("test", Severity.INFO, "test"),
        ("test", Severity.DEBUG, None),
    ],
)
def test_no_color(capsys, message, severity, file):

    set_config(color=False)

    print_message(message, severity, file)
    stderr = capsys.readouterr().err

    assert "\x1b" not in stderr
