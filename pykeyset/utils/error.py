# -*- coding: utf-8 -*-

import io
from abc import ABC, abstractproperty
from typing import Any, Optional, Type

from . import Severity, Verbosity, logging
from .config import config


class BaseKeysetError(ABC):
    def __init__(self) -> None:
        self.sourcefile = None  # pragma: no cover

    @abstractproperty
    def message(self) -> str:
        pass  # pragma: no cover


# TODO legacy error type. Replace this with specific exceptions for all error types
class KeysetError(Exception, BaseKeysetError):
    def __init__(self, message: str) -> None:
        self._message = message
        self.sourcefile = None

    @property
    def message(self) -> str:
        return self._message


class KeysetIOError(IOError, BaseKeysetError):
    def __init__(self, sourcefile: Optional[str] = None, source: Optional[IOError] = None) -> None:

        cause = source if source is not None else self.__cause__
        assert cause is not None

        winerror = getattr(cause, "winerror", 0)  # winerror attribute only exists on Windows

        IOError.__init__(
            self, cause.errno, cause.strerror, cause.filename, winerror, cause.filename2
        )
        self.sourcefile = sourcefile

    @property
    def message(self) -> str:
        return f"could not open file {self.filename}, {self.strerror}"


class KeysetTypeError(TypeError, BaseKeysetError):
    def __init__(
        self,
        value: Any,
        expected: Type,
        value_for: str,
        sourcefile: Optional[str] = None,
        source: Optional[TypeError] = None,
    ) -> None:

        cause = source if source is not None else self.__cause__
        assert cause is not None

        TypeError.__init__(cause)
        self.value = value
        self.expected = expected
        self.value_for = value_for
        self.sourcefile = sourcefile

    @property
    def message(self) -> str:
        return f"invalid value '{self.value}' for '{self.value_for}', expected {self.expected}"


class KeysetValueError(ValueError, BaseKeysetError):
    def __init__(
        self,
        value: Any,
        expected: str,
        value_for: str,
        sourcefile: Optional[str] = None,
        source: Optional[ValueError] = None,
    ) -> None:

        cause = source if source is not None else self.__cause__
        assert cause is not None

        ValueError.__init__(cause)
        self.value = value
        self.expected = expected
        self.value_for = value_for
        self.sourcefile = sourcefile

    @property
    def message(self) -> str:
        return f"invalid value '{self.value}' for '{self.value_for}', expected {self.expected}"


def io_error(sourcefile: Optional[str] = None, source: Optional[IOError] = None) -> None:
    raise_or_print(KeysetIOError(sourcefile, source), Severity.FATAL)


def type_error(
    value: Any,
    expected: Type,
    value_for: str,
    sourcefile: Optional[str] = None,
    source: Optional[TypeError] = None,
) -> None:
    raise_or_print(KeysetTypeError(value, expected, value_for, sourcefile, source), Severity.FATAL)


def value_error(
    value: Any,
    expected: str,
    value_for: str,
    sourcefile: Optional[str] = None,
    source: Optional[ValueError] = None,
) -> None:
    raise_or_print(KeysetValueError(value, expected, value_for, sourcefile, source), Severity.FATAL)


def raise_or_print(error: BaseKeysetError, severity: Severity) -> None:

    verbositymap = {
        Severity.FATAL: Verbosity.QUIET,
        Severity.WARNING: Verbosity.NORMAL,
        Severity.INFO: Verbosity.VERBOSE,
        Severity.DEBUG: Verbosity.DEBUG,
    }
    minverbosity = verbositymap.get(severity, Verbosity.DEBUG)

    conf = config()

    if severity >= conf.exceptlevel:  # Raise as an exception if severity is high enough
        raise error

    elif conf.verbosity >= minverbosity:  # Else print the error if verbosity is high enough
        logging.print_error(error.message, severity, error.sourcefile)


# Legacy error/warning/info functions; TODO remove these altogether


def error(*args, **kwargs):
    msg = as_string(
        *args, **{k: v for k, v in kwargs.items() if k not in ("color", "file", "wrap")}
    )

    raise_or_print(KeysetError(msg), Severity.FATAL)


def warning(*args, **kwargs):
    msg = as_string(
        *args, **{k: v for k, v in kwargs.items() if k not in ("color", "file", "wrap")}
    )

    raise_or_print(KeysetError(msg), Severity.WARNING)


def info(*args, **kwargs):
    msg = as_string(
        *args, **{k: v for k, v in kwargs.items() if k not in ("color", "file", "wrap")}
    )

    raise_or_print(KeysetError(msg), Severity.INFO)


def as_string(*args, **kwargs):
    """Returns the result of a print() call as a string"""

    kwargs["end"] = ""

    with io.StringIO() as f:
        print(*args, file=f, **kwargs)
        return f.getvalue()
