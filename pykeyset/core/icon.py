from __future__ import annotations

import os.path
from pathlib import Path

from .. import resources
from ..utils.logging import error

__all__ = ["IconSet", "Icon", "load_builtin", "load_file"]


class Icon:
    def __init__(self) -> None:
        error(NotImplementedError())


class IconSet:
    def __init__(self) -> None:
        error(NotImplementedError())


def load(ctx, file):
    """load built in icons or an XML icon/novelty file"""

    if ctx.icons is None:
        ctx.icons = []

    if not os.path.isfile(file) and file in resources.fonts:
        ctx.icons.append(load_builtin(file))
    else:
        ctx.icons.append(load_file(Path(file)))


def load_builtin(name: str) -> IconSet:
    """Load a builtin set of icons by name, returning an IconSet object"""

    error(NotImplementedError())


def load_file(path: Path) -> IconSet:
    """Load icons from the given path, returning an IconSet object"""

    error(NotImplementedError())
