from __future__ import annotations

from .glyph import Glyph


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
        raise NotImplementedError

    def __len__(self) -> int:
        """Returns the number of glyphs in the font"""

        raise NotImplementedError

    def glyph(self, char: str, size: float) -> Glyph | None:
        """Returns a copy of the glyph for the chosen character scaled to the given size, or None
        if the Glyph does not exist in the font"""

        raise NotImplementedError

    def line_spacing(self, size: float) -> float:
        raise NotImplementedError

    def add_glyph(self, glyph: Glyph) -> None:
        """Adds a glyph to the font. The glyph should have the same metrics as set when creating
        the Font object"""

        raise NotImplementedError

    def replacement(self, size: float) -> Glyph:
        """Returns a copy of this font's replacement character (or the default if none exists)
        scaled to the given size"""

        raise NotImplementedError
