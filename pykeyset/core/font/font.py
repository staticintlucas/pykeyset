# -*- coding: utf-8 -*-

from typing import Dict

from ...utils.path import Path
from ...utils.types import Vector
from .glyph import Glyph
from .kerning import Kerning


class Font:
    def __init__(self, name: str, em_size: int, cap_height: int, x_height: int, slope: int):

        self.name = name

        # Font metrics
        self.em_size = em_size
        self.cap_height = cap_height
        self.x_height = x_height
        self.slope = slope
        # self.line_height = line_height  # TODO enable this when I enable multiline legend support

        # Glyph objects
        self._glyphs: Dict[str, Glyph] = {}

        replacement_path = (
            Path()
            .M(Vector(146, 0))
            .a(Vector(73, 73), 0, 0, 1, Vector(-73, -73))
            .l(Vector(0, -580))
            .a(Vector(73, 73), 0, 0, 1, Vector(73, -73))
            .l(Vector(374, 0))
            .a(Vector(73, 73), 0, 0, 1, Vector(73, 73))
            .l(Vector(0, 580))
            .a(Vector(73, 73), 0, 0, 1, Vector(-73, 73))
            .z()
            .M(Vector(283, -110))
            .a(Vector(50, 50), 0, 0, 0, Vector(100, 0))
            .a(Vector(50, 50), 0, 0, 0, Vector(-100, 0))
            .z()
            .M(Vector(293, -236))
            .a(Vector(40, 40), 0, 0, 0, Vector(80, 0))
            .a(Vector(120, 108), 0, 0, 1, Vector(60, -94))
            .a(Vector(200, 180), 0, 0, 0, Vector(100, -156))
            .a(Vector(200, 180), 0, 0, 0, Vector(-400, 0))
            .a(Vector(40, 40), 0, 0, 0, Vector(80, 0))
            .a(Vector(120, 108), 0, 0, 1, Vector(240, 0))
            .a(Vector(120, 108), 0, 0, 1, Vector(-60, 94))
            .a(Vector(200, 180), 0, 0, 0, Vector(-100, 156))
            .z()
        )

        scale = cap_height / replacement_path.boundingbox.height
        self._replacement: Glyph = Glyph(
            name="\ufffd",
            path=replacement_path.scale(scale),
            advance=638 * scale,
        )

        self.kerning = Kerning(cap_height)

    def __len__(self) -> int:
        """Returns the number of glyphs in the font"""
        return len(self._glyphs)

    def glyph(self, char: str, size: float) -> Glyph:
        """Returns a copy of the glyph for the chosen character scaled to the given size, or None
        if the Glyph does not exist in the font"""

        if char not in self._glyphs:
            return None

        scale = size / self.cap_height
        glyph = self._glyphs[char]
        return Glyph(
            name=glyph.name,
            path=glyph.path.copy().scale(scale),
            advance=glyph.advance * scale,
        )

    def add_glyph(self, glyph: Glyph) -> None:
        """Adds a glyph to the font. The glyph should have the same metrics as set when creating
        the Font object"""

        self._glyphs[glyph.name] = glyph

    def replacement(self, size: float) -> Glyph:
        """Returns a copy of this font's replacement character (or the default if none exists)
        scaled to the given size"""

        scale = size / self.cap_height
        return Glyph(
            name=self._replacement.name,
            path=self._replacement.path.copy().scale(scale),
            advance=self._replacement.advance * scale,
        )
