# -*- coding: utf-8 -*-

import os.path
from pathlib import Path

from ... import resources
from .font import Font
from .glyph import Glyph
from .kerning import Kerning
from .load import load_builtin, load_file

__all__ = ["Font", "Glyph", "Kerning", "load_builtin", "load_file"]


# TODO this function is used by the cmdlist parser. Move it somewhere more appropriate?
def load(ctx, file):
    """load a built in font or an XML font file"""

    if not os.path.isfile(file) and file in resources.fonts:
        ctx.font = load_builtin(file)
    else:
        ctx.font = load_file(Path(file))
