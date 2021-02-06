# -*- coding: utf-8 -*-

from . import fontgen, save
from .font import Font
from .icon import IconSet
from .kle import KleFile
from .layout import Layout
from .profile import Profile


class Context:
    def __init__(self, name):

        self.name = name
        self.kle = None
        self.font = None
        self.icons = []
        self.profile = None
        self.layout = None


__all__ = ["Context", "Font", "Profile", "KleFile", "Layout", "IconSet", "fontgen", "save"]
