# -*- coding: utf-8 -*-

from .font import Font
from .profile import Profile
from .kle import KleFile
from .layout import Layout


class Context:
    def __init__(self, name):

        self.name = name
        self.kle = None
        self.font = None
        self.icons = []
        self.profile = None
        self.layout = None


__all__ = ["Context", "Font", "Profile", "KleFile", "Layout"]
