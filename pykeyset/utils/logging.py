# -*- coding: utf-8 -*-

import inspect
import sys
from pathlib import Path
from types import TracebackType
from typing import NoReturn, Optional, Union

import rich.console
import typer

from . import Severity, Verbosity
from .config import config

__all__ = ["error", "warning", "info", "debug"]


COLOR_MAP = {
    Severity.ERROR: "red",
    Severity.WARNING: "yellow",
    Severity.INFO: "blue",
    Severity.DEBUG: "dim",
}

VERBOSITY_MAP = {
    Severity.ERROR: Verbosity.QUIET,
    Severity.WARNING: Verbosity.NORMAL,
    Severity.INFO: Verbosity.VERBOSE,
    Severity.DEBUG: Verbosity.DEBUG,
}


def error(
    error: Exception, file: Optional[str] = None, prev_except: Optional[Exception] = None
) -> NoReturn:
    """Handle an error in pykeyset code.

    Depending on the current configuration, this function can raise the error as an exception,
    print the error to the terminal, and/or exit the script."""

    # Try to remove this call from the traceback. This will make it look like the exception was
    # raised where this function was called, not inside. Note: this is not guaranteed to work on
    # version < 3.7 or implementation != CPython, in which case we just pass None to raise_or_print
    frame = inspect.currentframe()
    if frame is not None:
        frame = frame.f_back

    conf = config()

    if conf.verbosity >= Verbosity.QUIET:
        message = format_error(error)
        print_message(message, Severity.ERROR, file)

    if conf.is_script:
        raise typer.Exit(1)

    else:
        # Create a traceback from frame (Python >= 3.7 only)
        if frame is not None and sys.version_info >= (3, 7):
            tb = TracebackType(
                tb_next=None, tb_frame=frame, tb_lasti=frame.f_lasti, tb_lineno=frame.f_lineno
            )
            raise error.with_traceback(tb) from prev_except
        else:
            raise error from prev_except  # pragma: no cover


def warning(
    error: Exception,
    resolution: str,
    file: Optional[str] = None,
    prev_except: Optional[Exception] = None,
) -> None:
    """Handle an warning in pykeyset code.

    Depending on the current configuration, this function can raise the warning as an exception or
    print the warning to the terminal, or silently ignore it."""

    # See comment in error() for details. Warnings can also end up raising an exception (if
    # raise_warnings is set in the config).
    frame = inspect.currentframe()
    if frame is not None:
        frame = frame.f_back

    conf = config()

    if conf.verbosity >= Verbosity.NORMAL:
        # Only format the resolution if this warning will not be raised. Otherwise the resolution
        # doesn't resolve anything
        if conf.raise_warnings:
            message = format_error(error)
        else:
            message = format_error(error, resolution)
        print_message(message, Severity.WARNING, file)

    if conf.raise_warnings:
        if conf.is_script:
            raise typer.Exit(1)

        else:
            # Create a traceback from frame (Python >= 3.7 only)
            if frame is not None and sys.version_info >= (3, 7):
                tb = TracebackType(
                    tb_next=None, tb_frame=frame, tb_lasti=frame.f_lasti, tb_lineno=frame.f_lineno
                )
                raise error.with_traceback(tb) from prev_except
            else:
                raise error from prev_except  # pragma: no cover


def info(message: str, file: Optional[str] = None):
    if config().verbosity >= Verbosity.VERBOSE:
        print_message(message, Severity.INFO, file)


def debug(message: str, file: Optional[str] = None):
    if config().verbosity >= Verbosity.DEBUG:
        print_message(message, Severity.DEBUG, file)


def format_error(error: Exception, resolution: Optional[str] = None) -> str:
    if isinstance(error, OSError):
        if error.filename is not None:
            filename = Path(error.filename).name
            result = f"cannot open file {format_filename(filename)}: {error.strerror.lower()}"
        elif error.strerror is not None:
            result = error.strerror.lower()
        else:
            result = str(error).lower()
    else:
        result = f"{error}"

    if resolution is not None:
        result = f"{result}. {resolution}"

    return result


def format_filename(filename: Union[str, Path]) -> str:
    return f"[bold magenta]{filename}[/bold magenta]"


def print_message(message: str, severity: Severity, filename: Optional[Path] = None) -> None:

    color = COLOR_MAP.get(severity, "magenta")
    prefix = severity.name.capitalize()

    console = rich.console.Console(force_terminal=config().color, stderr=True)
    console.print(f"[{color} bold]{prefix}:[/{color} bold] {message}")
    if filename is not None:
        console.print(f"    In file {format_filename(filename)}")
