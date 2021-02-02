# -*- coding: utf-8 -*-

import pathlib
import xml.etree.ElementTree as et
from typing import Optional, Tuple

from ... import resources
from ...utils.logging import error
from ...utils.logging import format_filename as fmt_file
from ...utils.logging import info, warning
from ...utils.path import Path
from .font import Font
from .glyph import Glyph


class FontError(ValueError):
    pass


def load_builtin(name: str) -> Font:
    """Load a builtin font by name, returning a Font object"""

    if name not in resources.fonts:
        error(ValueError(f"no built in font called {fmt_file(name)}"))

    with resources.fonts[name] as file:
        # Note: no try/except here since we know this path exists and we assume builtin fonts never
        # fail to parse (and we should load each of them with our unit tests)
        root = et.parse(file).getroot()

    return parse_font(name, root)


def load_file(path: pathlib.Path) -> Font:
    """Load a font from the given path, returning a Font object"""

    try:
        root = et.parse(path).getroot()

    except IOError as e:
        error(IOError(f"cannot load font from {fmt_file(path)}: {e.strerror.lower()}"))

    except et.ParseError as e:
        error(FontError(f"cannot load font from {fmt_file(path)}: {e.msg.lower()}"))

    return parse_font(path.name, root)


def parse_root(name: str, root: et.Element) -> Tuple[Font, Optional[float]]:
    """Gets the global font properties from a font, returning a tuple containing an empty Font
    object and the advance (if set, otherwise None)"""

    for key in ("em-size", "cap-height", "x-height"):
        if key not in root.attrib:
            error(FontError(f"no '{key}' attribute in font {fmt_file(name)}"))
        try:
            float(root.attrib[key])
        except (TypeError, ValueError):
            error(FontError(f"invalid value for '{key}' in font {fmt_file(name)}"))
    else:
        em_size = float(root.attrib["em-size"])
        cap_height = float(root.attrib["cap-height"])
        x_height = float(root.attrib["x-height"])

    for key, message in (
        ("slope", "Using default value (0)"),
        ("horiz-adv-x", "Value must be set per glyph"),
        # TODO enable this when multiline legend support lands
        # ("line-height", "Using em-size as a default"),
    ):
        if key not in root.attrib:
            info(f"no '{key}' attribute in font {fmt_file(name)}. {message}")
        else:
            try:
                float(root.attrib[key])
            except (TypeError, ValueError):
                error(FontError(f"invalid value for '{key}' in font {fmt_file(name)}"))
    else:
        slope = float(root.get("slope", 0))
        advance = float(root.get("horiz-adv-x")) if "horiz-adv-x" in root.attrib else None
        # line_height = float(root.get("line-height", em_size))

    return Font(name, em_size, cap_height, x_height, slope), advance


def parse_glyph(glyph: et.Element, default_advance: Optional[float] = None) -> Glyph:
    """Parses a single glyph from an ElementTree Element"""

    for key in ("char", "path"):
        if key not in glyph.attrib:
            raise FontError(f"no '{key}' attribute for glyph")
    else:
        char = glyph.attrib["char"]

        try:
            path = Path(glyph.attrib["path"])
        except ValueError as e:
            raise FontError(f"{e.args[0]} in glyph '{char}'")

    if "transform" in glyph.attrib:
        try:
            path.transform(glyph.attrib["transform"])
        except ValueError as e:
            raise FontError(f"{e.args[0]} in glyph '{char}'")

    if "horiz-adv-x" in glyph.attrib:
        try:
            advance = float(glyph.attrib["horiz-adv-x"])
        except (TypeError, ValueError):
            raise FontError(f"invalid value for 'horiz-adv-x' for glyph '{char}'")
    elif default_advance is not None:
        advance = default_advance
    else:
        raise FontError(f"no 'horiz-adv-x' attribute for glyph '{char}' and no default value set")

    return Glyph(char, path, advance)


def parse_kerning(kern: et.Element) -> Tuple[str, str, float]:
    """Parses a kerning value from an ElementTree Element"""

    for key in ("u", "k"):
        if key not in kern.attrib:
            raise FontError(f"no '{key}' attribute for kern element")

    if len(kern.attrib["u"]) != 2:
        raise FontError("invalid value for 'u' for kern element")
    else:
        lhs, rhs = list(kern.attrib["u"])

    try:
        value = float(kern.attrib["k"])
    except (TypeError, ValueError):
        raise FontError(f"invalid value for 'k' for kern element for '{lhs}{rhs}'")

    return lhs, rhs, value


def parse_font(name: str, root: et.Element) -> Font:
    """Parses a font from an ElementTree Element"""

    font, default_advance = parse_root(name, root)

    for g in root.iterfind("glyph"):
        try:
            glyph = parse_glyph(g, default_advance)
        except FontError as e:
            warning(FontError(f"{e.args[0]} in font {fmt_file(name)}"), "skipping this glyph")
            continue

        font.add_glyph(glyph)

    info(f"loaded {len(font)} glyphs from font {fmt_file(name)}")

    for k in root.iterfind("kern"):
        try:
            lhs, rhs, value = parse_kerning(k)
            font.kerning.set(lhs, rhs, value)
        except FontError as e:
            warning(
                FontError(f"{e.args[0]} in kern element in font {fmt_file(name)}"),
                "skipping this element",
            )

    return font
