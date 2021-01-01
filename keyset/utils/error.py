# coding: utf-8

import sys
import io
from shutil import get_terminal_size

from colorama import colorama_text, Fore, Style
from ansiwrap import fill


class Verbosity:
    QUIET = 0
    NORMAL = 1
    VERBOSE = 2


class KeysetError(Exception):
    pass


def error(*args, **kwargs):
    """Print an error message when running as a script, or raise an exception"""

    from .config import config as conf

    print_errors = conf.is_script or conf.verbosity >= Verbosity.VERBOSE
    no_raise = kwargs.pop("no_raise", False)

    if print_errors:
        msg = as_string(
            *args, **{k: v for k, v in kwargs.items() if k not in ("color", "file", "wrap")}
        )

        if "color" not in kwargs:
            kwargs["color"] = conf.color

        print_color(f"{Style.BRIGHT}{Fore.RED}Error: {Style.RESET_ALL}{msg}", **kwargs)

    if not no_raise:
        raise KeysetError(msg)


def warning(*args, **kwargs):
    """Print a warning message if the verbosity setting is high enough"""

    from .config import config as conf

    print_warnings = (
        conf.is_script and conf.verbosity >= Verbosity.NORMAL
    ) or conf.verbosity >= Verbosity.VERBOSE

    if print_warnings:
        msg = as_string(
            *args, **{k: v for k, v in kwargs.items() if k not in ("color", "file", "wrap")}
        )

        if "color" not in kwargs:
            kwargs["color"] = conf.color

        print_color(f"{Style.BRIGHT}{Fore.YELLOW}Warning: {Style.RESET_ALL}{msg}", **kwargs)


def info(*args, **kwargs):
    """Print an info message if the verbosity setting is high enough"""

    from .config import config as conf

    print_info = conf.verbosity >= Verbosity.VERBOSE

    if print_info:
        msg = as_string(
            *args, **{k: v for k, v in kwargs.items() if k not in ("color", "file", "wrap")}
        )

        if "color" not in kwargs:
            kwargs["color"] = conf.color

        print_color(f"{Style.BRIGHT}{Fore.BLUE}Info: {Style.RESET_ALL}{msg}", **kwargs)


def done(*args, **kwargs):
    """Print a done message if the verbosity setting is high enough"""

    from .config import config as conf

    print_done = conf.is_script and conf.verbosity >= Verbosity.NORMAL

    if print_done:
        msg = as_string(
            *args, **{k: v for k, v in kwargs.items() if k not in ("color", "file", "wrap")}
        )

        if "color" not in kwargs:
            kwargs["color"] = conf.color

        print_color(f"{Style.BRIGHT}{Fore.GREEN}{msg}{Style.RESET_ALL}", **kwargs)


def as_string(*args, **kwargs):
    """Returns the result of a print() call as a string"""

    kwargs["end"] = ""

    with io.StringIO() as f:
        print(*args, file=f, **kwargs)
        return f.getvalue()


def print_color(*args, **kwargs):
    """Wraps print using colorama for coloured output"""

    file = kwargs.pop("file", sys.stderr)
    color = kwargs.pop("color", None)
    color = color if color is not None else file.isatty()

    # Use word wrapping if we can get the terminal size
    if kwargs.pop("wrap", True):
        width, _ = get_terminal_size((99999, 0))
        msg = fill(as_string(*args, **kwargs), width)
    else:
        msg = as_string(*args, **kwargs)

    # Auto convert to WinAPI calls on Windows if we want color, else don't convert anything
    convert = None if color else False
    # Auto strip escape sequences on Windows, else strip everything so we get no color
    strip = None if color else True

    with colorama_text(convert=convert, strip=strip):
        print(msg, file=file, **kwargs)
