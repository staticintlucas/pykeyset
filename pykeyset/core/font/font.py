# -*- coding: utf-8 -*-

from typing import Dict, Optional

from ...utils.path import Path
from ...utils.types import Vector
from .glyph import Glyph
from .kerning import Kerning


class Font:
    def __init__(
        self,
        name: str,
        em_size: float,
        cap_height: float,
        x_height: float,
        line_height: float,
        slope: float,
        char_spacing: float,
    ):

        self.name = name

        # Font metrics
        self.em_size = em_size
        self.cap_height = cap_height
        self.x_height = x_height
        self.slope = slope
        self.line_height = line_height
        self.char_spacing = char_spacing

        # Glyph objects
        self._glyphs: Dict[str, Glyph] = {}

        replacement_path = (
            Path()
            .M(Vector(146, 0))
            .a(Vector(73, 73), 0, False, True, Vector(-73, -73))
            .l(Vector(0, -580))
            .a(Vector(73, 73), 0, False, True, Vector(73, -73))
            .l(Vector(374, 0))
            .a(Vector(73, 73), 0, False, True, Vector(73, 73))
            .l(Vector(0, 580))
            .a(Vector(73, 73), 0, False, True, Vector(-73, 73))
            .z()
            .M(Vector(283, -110))
            .a(Vector(50, 50), 0, False, False, Vector(100, 0))
            .a(Vector(50, 50), 0, False, False, Vector(-100, 0))
            .z()
            .M(Vector(293, -236))
            .a(Vector(40, 40), 0, False, False, Vector(80, 0))
            .a(Vector(120, 108), 0, False, True, Vector(60, -94))
            .a(Vector(200, 180), 0, False, False, Vector(100, -156))
            .a(Vector(200, 180), 0, False, False, Vector(-400, 0))
            .a(Vector(40, 40), 0, False, False, Vector(80, 0))
            .a(Vector(120, 108), 0, False, True, Vector(240, 0))
            .a(Vector(120, 108), 0, False, True, Vector(-60, 94))
            .a(Vector(200, 180), 0, False, False, Vector(-100, 156))
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

    def glyph(self, char: str, size: float) -> Optional[Glyph]:
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

    def line_spacing(self, size: float) -> float:
        return self.line_height * size / self.cap_height

    def add_glyph(self, glyph: Glyph) -> None:
        """Adds a glyph to the font. The glyph should have the same metrics as set when creating
        the Font object"""

        glyph = glyph._replace(advance=glyph.advance + self.char_spacing)
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
