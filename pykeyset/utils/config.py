# -*- coding: utf-8 -*-

import sys
from logging import NOTSET
from typing import NamedTuple, Optional

__all__ = ["set_config", "config"]


def set_config(
    showalign: Optional[bool] = False,
    dpi: Optional[int] = 96,
    profile: Optional[bool] = False,
    color: Optional[bool] = sys.stderr.isatty(),
    verbosity: Optional[int] = NOTSET,
):
    """Set the global configuration object."""

    class Config(NamedTuple):
        showalign: bool
        dpi: int
        profile: bool
        color: bool
        verbosity: int

    global config

    config = Config(
        showalign=showalign,
        dpi=dpi,
        profile=profile,
        color=color,
        verbosity=verbosity,
    )


config = None

set_config()  # No args to set default values
