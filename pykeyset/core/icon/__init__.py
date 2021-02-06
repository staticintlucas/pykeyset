# -*- coding: utf-8 -*-

import os.path
from pathlib import Path

from ... import resources
from .icon import Icon
from .icon_set import IconSet
from .load import load_builtin, load_file

__all__ = ["IconSet", "Icon", "load_builtin", "load_file"]


# TODO this function is used by the cmdlist parser. Move it somewhere more appropriate?
def load(ctx, file):
    """load built in icons or an XML icon/novelty file"""

    if ctx.icons is None:
        ctx.icons = []

    if not os.path.isfile(file) and file in resources.fonts:
        ctx.icons.append(load_builtin(file))
    else:
        ctx.icons.append(load_file(Path(file)))
