# -*- coding: utf-8 -*-

from numbers import Real


class Kerning:
    def __init__(self, cap_height):
        self.kern_dict = {}
        self.cap_height = cap_height

    def get(self, lhs: str, rhs: str, size: Real) -> int:
        """Returns the kerning between the given pair of glyph names if set, otherwise returns the
        default value of 0"""

        kerning = 0

        if lhs in self.kern_dict:
            lhs_dict = self.kern_dict[lhs]
            if rhs in lhs_dict:
                kerning = lhs_dict[rhs]

        return kerning * size / self.cap_height

    def set(self, lhs: str, rhs: str, kerning: int) -> None:
        """Sets the kerning between the given pair of glyph names"""

        if lhs not in self.kern_dict:
            self.kern_dict[lhs] = {}

        self.kern_dict[lhs][rhs] = kerning

    def delete(self, lhs: str, rhs: str) -> None:
        """Resets the kerning between the given pair of glyph names. This will not modify the
        anything if the kerning between these characters has not been previously set"""

        if lhs in self.kern_dict and rhs in self.kern_dict[lhs]:
            del self.kern_dict[lhs][rhs]

            if len(self.kern_dict[lhs]) == 0:
                del self.kern_dict[lhs]

    def __len__(self) -> int:
        """Returns the number of kerning pair explicitly set"""

        return sum(len(lhs) for lhs in self.kern_dict.values())
