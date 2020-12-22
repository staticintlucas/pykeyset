# coding: utf-8

from .. import utils
from .font import Font

class Context():

    def __init__(self, conf, name):

        self.conf = utils.config.Config(clone=conf)
        self.name = name
        self.kle = None
        self.font = None
        self.novelty = None
        self.profile = None


__all__ = ['Context', 'Font']
