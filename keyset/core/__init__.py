# coding: utf-8

from .. import utils
from .font import Font
from .profile import Profile
from .kle import KleLayout

class Context():

    def __init__(self, name):

        self.name = name
        self.layout = None
        self.font = None
        self.novelty = None
        self.profile = None


__all__ = ['Context', 'Font', 'Profile', 'KleLayout']
