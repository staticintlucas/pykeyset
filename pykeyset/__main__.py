#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cProfile
import os.path
import pstats
import sys
from pathlib import Path
from time import perf_counter
from typing import Any, List

import click.core
import rich.traceback
import typer
from typer import Option

from . import __version__, cmdlist, resources
from .utils import Verbosity
from .utils.config import set_config

profiler = None
PROFILE_FILE = "pykeyset_profile.txt"

HELP = {
    "align": "Show alignment boundaries in output graphics.",
    "dpi": "Set the DPI used when generating output graphics.",
    "profile": f"Profile program execution. Saved to {PROFILE_FILE}.",
    "color": "Enable / disable colored text output.  [default: auto]",
    "debug": "Show extra debug information messages.",
    "verbose": "Show all information output messages.",
    "quiet": "Show only fatal error messages in program output.",
}

starttime = None


def print_version(value: bool) -> None:
    """Show version message and exit."""

    if value:
        typer.echo(
            f"{os.path.basename(sys.argv[0])} version {__version__}\n"
            "Copyright (c) 2021 Lucas Jansen",
            err=True,
        )
        raise typer.Exit()


def callback(
    show_align: bool = Option(False, "--show-align", show_default=False, help=HELP["align"]),
    dpi: int = Option(96, "-d", "--dpi", metavar="<number>", help=HELP["dpi"]),
    profile: bool = Option(False, "--profexec", show_default=False, help=HELP["profile"]),
    color: bool = Option(None, "--color/--no-color", show_default=False, help=HELP["color"]),
    debug: bool = Option(False, "--debug", show_default=False, help=HELP["debug"]),
    verbose: bool = Option(False, "-v", "--verbose", show_default=False, help=HELP["verbose"]),
    quiet: bool = Option(False, "-q", "--quiet", show_default=False, help=HELP["quiet"]),
    version: bool = Option(
        False,
        "--version",
        show_default=False,
        callback=print_version,
        is_eager=True,
        help=print_version.__doc__,
    ),
) -> None:

    rich.traceback.install()

    global starttime
    starttime = perf_counter()

    if profile:
        global profiler
        profiler = cProfile.Profile()
        profiler.enable()

    if debug:
        verbosity = Verbosity.DEBUG
        rich.traceback.install(show_locals=True)
    elif verbose:
        verbosity = Verbosity.VERBOSE
    elif quiet:
        verbosity = Verbosity.QUIET
    else:
        verbosity = Verbosity.NORMAL

    set_config(
        show_align=show_align,
        dpi=dpi,
        profile=profile,
        color=color,
        verbosity=verbosity,
        raise_warnings=False,
        is_script=True,
    )


def result_callback(exit_code: int, **kwargs: Any) -> None:

    global profiler
    if profiler is not None:
        profiler.disable()

        if exit_code == 0:
            with open(PROFILE_FILE, "w") as f:
                stats = pstats.Stats(profiler, stream=f)
                stats.strip_dirs().sort_stats("tottime").print_stats()

    if exit_code == 0:
        endtime = perf_counter()
        typer.secho(f"Completed in {endtime - starttime:.3f} s", fg=typer.colors.GREEN, bold=True)


app = typer.Typer(
    context_settings={"max_content_width": 800},  # So that is doesn't auto wrap at 80
    add_completion=False,
    options_metavar="[options]",
    subcommand_metavar="<command> [args ...]",
    callback=callback,
    result_callback=result_callback,
)


class RunCommand(typer.core.TyperCommand):
    def format_options(self, ctx: typer.Context, formatter: click.HelpFormatter) -> None:
        super().format_options(ctx, formatter)
        cmdlist.format_options(ctx, formatter)
        resources.format_options(ctx, formatter)


@app.command(options_metavar="[options]", no_args_is_help=True, cls=RunCommand)
def run(
    cmdlists: List[Path] = typer.Argument(
        None,
        metavar="<cmdlist> ...",
        show_default=False,
        help="Command list files to execute. Each is executed in its own context.",
    ),
) -> int:
    """Run one or more command list (.cmdlist) files."""

    for cl in cmdlists:
        cmdlist.run(cl)

    return 0


# For compatibility to let this run as a standalone script
if __name__ == "__main__":
    app()
