# coding: utf-8

from .load_font import load_font

from copy import deepcopy

class Context():

    def __init__(self, conf, name):

        self.conf = deepcopy(conf)
        self.name = name
        self.kle = None
        self.font = None
        self.novelty = None
        self.profile = None

__all__ = ['Context', 'load_font']
