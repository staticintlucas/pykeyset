# -*- coding: utf-8 -*-


class Glyph:
    def __init__(self, path, advance):

        self.path = path
        self.advance = advance


class Kern:
    def __init__(self):
        self.dict = {}

    def add(self, char1, char2, value):

        for c1 in char2:
            for c2 in char2:
                self.dict[f"{c1}{c2}"] = value

    def get(self, c1, c2):

        return self.dict.get(f"{c1}{c2}", 0)
