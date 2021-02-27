# -*- coding: utf-8 -*-

import os.path
from pathlib import Path

from ... import resources
from .load import load_builtin, load_file
from .profile import Profile

__all__ = [Profile, load_builtin, load_file]


# TODO this function is used by the cmdlist parser. Move it somewhere more appropriate?
def load(ctx, file):
    """load a built in profile or a profile config file"""

    if not os.path.isfile(file) and file in resources.profiles:
        ctx.profile = load_builtin(file)
    else:
        ctx.profile = load_file(Path(file))
