from __future__ import annotations

import os
from pathlib import Path

from .. import resources
from .._impl.font import Font
from ..utils.logging import error
from ..utils.logging import format_filename as fmt_file

__all__ = ["Font", "load_builtin", "load_file"]


class FontError(ValueError):
    pass


def load(ctx, file):
    """load a built in font or an XML font file"""

    if not os.path.isfile(file) and file in resources.fonts:
        ctx.font = load_builtin(file)
    else:
        ctx.font = load_file(Path(file))


def load_builtin(name: str) -> Font:
    """Load a builtin font by name, returning a Font object"""

    if name not in resources.fonts:
        error(ValueError(f"no built in font called {fmt_file(name)}"))

    # Note: no try/except here since we know this path exists and we assume builtin fonts never
    # fail to parse (and we should load each of them with our unit tests)
    return Font(resources.fonts[name].read_bytes())


def load_file(path: Path) -> Font:
    """Load a font from the given path, returning a Font object"""

    try:
        return Font(path.read_bytes())

    except OSError as e:
        error(OSError(f"cannot load font from {fmt_file(path)}: {e.strerror.lower()}"))

    except ValueError as e:
        error(FontError(f"cannot load font from {fmt_file(path)}: {str(e).lower()}"))
