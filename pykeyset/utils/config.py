# -*- coding: utf-8 -*-

from typing import Any, NamedTuple, Optional

from . import Verbosity

__all__ = ["config", "set_config", "reset_config"]


class _Config(NamedTuple):
    show_align: bool
    dpi: int
    profile: bool
    color: Optional[bool]
    verbosity: Verbosity
    raise_warnings: bool
    is_script: bool


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
        show_align=kwargs.pop("show_align", _config.show_align),
        dpi=kwargs.pop("dpi", _config.dpi),
        profile=kwargs.pop("profile", _config.profile),
        color=kwargs.pop("color", _config.color),
        verbosity=kwargs.pop("verbosity", _config.verbosity),
        raise_warnings=kwargs.pop("raise_warnings", _config.raise_warnings),
        is_script=kwargs.pop("is_script", _config.is_script),
    )

    if len(kwargs) > 0:
        raise ValueError(f"unknown config option {[kwargs.keys()][0]} in call to set_config")


def reset_config() -> None:
    """Reset the global configuration object to it's default values."""

    global _config

    _config = _Config(
        show_align=False,
        dpi=96,
        profile=False,
        color=None,
        verbosity=Verbosity.NONE,
        raise_warnings=False,
        is_script=False,
    )
