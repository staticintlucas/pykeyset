# -*- coding: utf-8 -*-

from typing import Optional

import typer

from . import Severity
from .config import config


def print_error(message: str, severity: Severity, sourcefile: Optional[str] = None) -> None:

    colormap = {
        Severity.FATAL: typer.colors.RED,
        Severity.WARNING: typer.colors.YELLOW,
        Severity.INFO: typer.colors.BLUE,
        Severity.DEBUG: typer.colors.MAGENTA,
    }
    color = colormap[severity]

    print_message(
        prefix=severity.name.capitalize(),
        message=message,
        color=color,
        filename=sourcefile,
    )


def print_message(prefix: str, message: str, color: str, filename: Optional[str] = None) -> None:

    usecolor = config().color
    prefix = typer.style(f"{prefix.capitalize()}:", fg=color, bold=True)
    message = typer.style(message, bold=True)

    if filename is not None:
        filename = typer.format_filename(filename)
        typer.echo(f"{prefix} {message}\n    In file {filename}", color=usecolor, err=True)
    else:
        typer.echo(f"{prefix} {message}", color=usecolor, err=True)
