# coding: utf-8

class Glyph:

    def __init__(self):

        self.path = []
        self.xpos = 0
        self.ypos = 0
        self.width = 0
        self.height = 0
        self.advance = 0

    @classmethod
    def from_element(cls, tree):

        self = cls()

        return self
