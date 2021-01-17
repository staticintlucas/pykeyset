#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cProfile
import os.path
import pstats
import sys
from time import perf_counter
from typing import Any, List, Optional

import click.core
import typer

from . import __version__, cmdlist, res
from .utils import Verbosity
from .utils.config import set_config
from .utils.error import error

profiler = None
PROFILE_FILE = "pykeyset_profile.txt"

starttime = None


def print_version(value: bool) -> None:
    if value:
        typer.echo(
            f"{os.path.basename(sys.argv[0])} version {__version__}\n"
            "Copyright (c) 2021 Lucas Jansen",
            err=True,
        )
        raise typer.Exit()


def callback(
    showalign: Optional[bool] = typer.Option(
        False,
        "--show-alignment",
        show_default=False,
        help="Show alignment boundaries in output graphics.",
    ),
    dpi: int = typer.Option(
        96,
        "-d",
        "--dpi",
        metavar="<number>",
        help="Set the DPI used when generating output graphics.",
    ),
    profile: Optional[bool] = typer.Option(
        False,
        "--profexec",
        show_default=False,
        help=f"Profile program execution. Saved to {PROFILE_FILE}.",
    ),
    color: Optional[bool] = typer.Option(
        None,
        "--color/--no-color",
        show_default=False,
        help="Enable / disable colored text output.  [default: auto]",
    ),
    verbose: Optional[bool] = typer.Option(
        False,
        "-v",
        "--verbose",
        show_default=False,
        help="Show all debug and information output messages.",
    ),
    quiet: Optional[bool] = typer.Option(
        False,
        "-q",
        "--quiet",
        show_default=False,
        help="Show only fatal error messages in program output.",
    ),
    version: Optional[bool] = typer.Option(
        False,
        "--version",
        show_default=False,
        callback=print_version,
        is_eager=True,
        help="Show version message and exit.",
    ),
) -> None:
    global starttime
    starttime = perf_counter()

    if profile:
        global profiler
        profiler = cProfile.Profile()

    if verbose:
        verbosity = Verbosity.VERBOSE
    elif quiet:
        verbosity = Verbosity.QUIET
    else:
        verbosity = Verbosity.NORMAL

    set_config(
        showalign=showalign,
        dpi=dpi,
        profile=profile,
        color=color,
        verbosity=verbosity,
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
        res.format_options(ctx, formatter)


@app.command(options_metavar="[options]", no_args_is_help=True, cls=RunCommand)
def run(
    cmdlists: List[str] = typer.Argument(
        None,
        metavar="<cmdlist> ...",
        show_default=False,
        help="Command list files to execute. Each is executed in its own context.",
    ),
) -> int:
    """Run one or more command list (.cmdlist) files."""

    if cmdlists is None or len(cmdlists) == 0:
        error("No commands to run")

    cmd_dict = {}

    for cl in cmdlists:
        commands = []

        try:
            with open(cl) as f:
                commands = f.readlines()
            cmd_dict[cl] = commands

        except IOError as e:
            error(f"cannot load command list '{e.filename}'. {e.strerror}")

    for name, cmds in cmd_dict.items():
        cmdlist.run(name, cmds)

    return 0


# For compatibility to let this run as a standalone script
if __name__ == "__main__":
    app()
