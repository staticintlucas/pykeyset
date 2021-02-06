# -*- coding: utf-8 -*-

import pathlib
import xml.etree.ElementTree as et

from pykeyset.utils.types import Rect

from ... import resources
from ...utils.logging import error
from ...utils.logging import format_filename as fmt_file
from ...utils.logging import info, warning
from ...utils.path.path import Path
from .icon import Icon
from .icon_set import IconSet


class IconError(ValueError):
    pass


def load_builtin(name: str) -> IconSet:
    """Load a builtin set of icons by name, returning an IconSet object"""

    if name not in resources.icons:
        error(ValueError(f"no built in font called {fmt_file(name)}"))

    with resources.icons[name] as file:
        # Note: no try/except here since we know this path exists and we assume builtin icons never
        # fail to parse (and we should load each of them in CI with our unit tests)
        root = et.parse(file).getroot()

    return parse_icon_set(name, root)


def load_file(path: pathlib.Path) -> IconSet:
    """Load icons from the given path, returning an IconSet object"""

    try:
        root = et.parse(path).getroot()

    except IOError as e:
        error(IOError(f"cannot load icons from {fmt_file(path)}: {e.strerror.lower()}"))

    except et.ParseError as e:
        error(IconError(f"cannot load icons from {fmt_file(path)}: {e.msg.lower()}"))

    return parse_icon_set(path.name, root)


def parse_root(name: str, root: et.Element) -> IconSet:
    """Gets the common icon properties from a icon file, returning an empty IconSet object"""

    if "key-size" not in root.attrib:
        error(IconError(f"no 'key-size' attribute in font {fmt_file(name)}"))
    try:
        key_size = float(root.attrib["key-size"])
    except (TypeError, ValueError):
        error(IconError(f"invalid value for 'key-size' in font {fmt_file(name)}"))

    return IconSet(name, key_size)


def parse_icon(icon: et.Element) -> Icon:
    """Parses a single icon from an ElementTree Element"""

    for key in ("name", "path"):
        if key not in icon.attrib:
            raise IconError(f"no '{key}' attribute for icon")

    name = icon.attrib["name"]

    try:
        path = Path(icon.attrib["path"])
    except ValueError as e:
        raise IconError(f"{e.args[0]} in icon '{name}'")

    if "transform" in icon.attrib:
        try:
            path.transform(icon.attrib["transform"])
        except ValueError as e:
            raise IconError(f"{e.args[0]} in icon '{name}'")

    if "bbox" in icon.attrib:
        try:
            x, y, w, h = (float(i) for i in icon.attrib["bbox"].split(" "))
        except ValueError:
            raise IconError(f"invalid value for 'bbox' for icon '{name}'")

        path.setboundingbox(Rect(x, y, w, h))

    return Icon(name, path)


def parse_icon_set(name: str, root: et.Element) -> IconSet:
    """Parses a set of icons from an ElementTree Element"""

    icon_set = parse_root(name, root)

    for icon_element in root.iterfind("icon"):
        try:
            icon = parse_icon(icon_element)
        except IconError as e:
            warning(IconError(f"{e.args[0]} in font {fmt_file(name)}"), "skipping this icon")
            continue

        icon_set.add_icon(icon)

    info(f"loaded {len(icon_set)} icon from icon set {fmt_file(name)}")

    return icon_set
