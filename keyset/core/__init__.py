# coding: utf-8

from .. import utils
from .font import Font
from .profile import Profile

class Context():

    def __init__(self, name):

        self.name = name
        self.kle = None
        self.font = None
        self.novelty = None
        self.profile = None


__all__ = ['Context', 'Font', 'Profile']
