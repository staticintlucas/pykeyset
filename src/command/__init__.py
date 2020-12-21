# coding: utf-8

from .. import utils
from .load_font import load_font

class Context():

    def __init__(self, conf, name):

        self.conf = utils.config.Config(clone=conf)
        self.name = name
        self.kle = None
        self.font = None
        self.novelty = None
        self.profile = None


__all__ = ['Context', 'load_font']
