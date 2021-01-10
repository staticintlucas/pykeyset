# -*- coding: utf-8 -*-

from typing import Any, NamedTuple, Optional

from . import Severity, Verbosity

__all__ = ["config", "set_config", "reset_config"]


class _Config(NamedTuple):
    showalign: bool
    dpi: int
    profile: bool
    color: Optional[bool]
    verbosity: Verbosity
    exceptlevel: Severity


_config = None


def config() -> _Config:
    """Returns the global configuration object."""

    global _config

    if _config is None:
        reset_config()  # pragma: no cover

    return _config


def set_config(**kwargs: Any) -> None:
    """Set the global configuration object."""

    global _config

    if _config is None:
        reset_config()  # pragma: no cover

    _config = _Config(
        showalign=kwargs.pop("showalign", _config.showalign),
        dpi=kwargs.pop("dpi", _config.dpi),
        profile=kwargs.pop("profile", _config.profile),
        color=kwargs.pop("color", _config.color),
        verbosity=kwargs.pop("verbosity", _config.verbosity),
        exceptlevel=kwargs.pop("exceptlevel", _config.exceptlevel),
    )

    if len(kwargs) > 0:
        raise ValueError(f"unknown config option {[kwargs.keys()][0]} in call to set_config")


def reset_config() -> None:
    """Reset the global configuration object to it's default values."""

    global _config

    _config = _Config(
        showalign=False,
        dpi=96,
        profile=False,
        color=None,
        verbosity=Verbosity.NONE,
        exceptlevel=Severity.FATAL,
    )
