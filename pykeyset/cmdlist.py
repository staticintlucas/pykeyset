# -*- coding: utf-8 -*-

import inspect
import shlex
from inspect import signature
from pathlib import Path
from typing import Callable, Dict

import click
from typer import Context

from . import core
from .utils.logging import error, format_filename, info

__all__ = ["run", "format_options"]


COMMANDS: Dict[str, Callable] = {
    "load kle": core.KleFile.load,
    "load font": core.font.load,
    "load icons": core.icon.load,
    "load profile": core.profile.load,
    "generate layout": core.Layout.layout,
    # "generate texture": # TODO generate a texture file (for renders, etc.)
    "save svg": core.save.as_svg,
    "save png": core.save.as_png,
    "save pdf": core.save.as_pdf,
    "save ai": core.save.as_ai,
    "newfont": core.fontgen.fontgen,
}


def run(filepath: Path) -> None:

    context = core.Context(filepath)

    try:
        with filepath.open() as file:
            for line in file:
                run_line(context, line)
    except IOError as e:
        error(IOError(f"cannot open command list {format_filename(filepath)}: {e.strerror}"))


def run_line(context: core.Context, string: str) -> None:

    line = shlex.split(string, comments=True)

    if len(line) == 0:
        return

    for cmd, fn in COMMANDS.items():
        cmd = cmd.split()
        if len(line) >= len(cmd) and line[: len(cmd)] == cmd:
            command = cmd
            func = fn
            break
    else:
        raise ValueError(f"invalid command '{line[0]}'")

    info(f"executing command '{command}'", file=context.name)

    num_args = len(signature(func).parameters) - 1  # Subtract one for the context
    args = line[len(command) :]

    if len(args) < num_args:
        raise ValueError(f"not enough arguments for command '{command}'")
    elif len(args) > num_args:
        raise ValueError(f"too many arguments for command '{command}'")
    else:
        func(context, *args)


def format_options(ctx: Context, formatter: click.HelpFormatter) -> None:

    items = []
    for cmd, fun in COMMANDS.items():

        empty = inspect.Parameter.empty
        args = [
            f"<{p.name}>" if p.default is empty else f"[{p.name}]"
            for p in list(signature(fun).parameters.values())[1:]
        ]
        cmd = f"{cmd} {' '.join(args)}"

        items.append((cmd, inspect.cleandoc(fun.__doc__ if fun.__doc__ is not None else "")))

    with formatter.section("Commands"):
        formatter.write_dl(items)
