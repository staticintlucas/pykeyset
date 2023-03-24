from __future__ import annotations

import os.path
from pathlib import Path

from .. import resources
from .._impl.profile import Profile
from ..utils.logging import error, format_filename

__all__ = ["Profile", "load_builtin", "load_file"]


class ProfileError(ValueError):
    pass


# TODO this function is used by the cmdlist parser. Move it somewhere more appropriate?
def load(ctx, file):
    """load a built in profile or a profile config file"""

    if not os.path.isfile(file) and file in resources.profiles:
        ctx.profile = load_builtin(file)
    else:
        ctx.profile = load_file(Path(file))


def load_builtin(name: str) -> Profile:
    """Load a builtin profile by name, returning a Profile object"""

    if name not in resources.profiles:
        error(ValueError(f"no built in profile called {format_filename(name)}"))

    # Note: no try/except here since we know this path exists and we assume builtin fonts never
    # fail to parse (and we should load each of them with our unit tests)
    return Profile(resources.profiles[name].read_text())


def load_file(path: Path) -> Profile:
    """Load a profile from the given path, returning a Profile object"""

    try:
        return Profile(path.read_text())

    except OSError as e:
        error(OSError(f"cannot load font from {format_filename(path)}: {e.strerror.lower()}"))

    except ValueError as e:
        error(ProfileError(f"cannot load font from {format_filename(path)}: {str(e).lower()}"))
