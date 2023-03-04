from __future__ import annotations

import pathlib
import xml.etree.ElementTree as et

from .font import Font
from .glyph import Glyph


class FontError(ValueError):
    pass


def load_builtin(name: str) -> Font:
    """Load a builtin font by name, returning a Font object"""

    raise NotImplementedError


def load_file(path: pathlib.Path) -> Font:
    """Load a font from the given path, returning a Font object"""

    raise NotImplementedError


def parse_root(name: str, root: et.Element) -> tuple[Font, float | None]:
    """Gets the global font properties from a font, returning a tuple containing an empty Font
    object and the advance (if set, otherwise None)"""

    raise NotImplementedError


def parse_glyph(glyph: et.Element, default_advance: float | None = None) -> Glyph:
    """Parses a single glyph from an ElementTree Element"""

    raise NotImplementedError


def parse_kerning(kern: et.Element) -> tuple[str, str, float]:
    """Parses a kerning value from an ElementTree Element"""

    raise NotImplementedError


def parse_font(name: str, root: et.Element) -> Font:
    """Parses a font from an ElementTree Element"""

    raise NotImplementedError
