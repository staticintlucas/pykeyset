# -*- coding: utf-8 -*-

import pathlib
from numbers import Real
from typing import Tuple

import toml
from toml import TomlDecodeError

from ... import resources
from ...utils.logging import error, format_filename
from ...utils.types import Rect, RoundRect
from .profile import Profile
from .types import (
    HomingBar,
    HomingBump,
    HomingProperties,
    HomingScoop,
    HomingType,
    ProfileType,
    TextTypeProperty,
)


class ProfileError(ValueError):
    pass


def load_builtin(name: str) -> Profile:
    """Load a builtin profile by name, returning a Profile object"""

    if name not in resources.profiles:
        error(ValueError(f"no built in profile called {format_filename(name)}"))

    with resources.profiles[name] as file:
        # Note: no try/except here since we know this path exists and we assume builtin fonts never
        # fail to parse (and we should load each of them with our unit tests)
        root = toml.load(file)

    return parse_profile(name, root)


def load_file(path: pathlib.Path) -> Profile:
    """Load a profile from the given path, returning a Profile object"""

    try:
        root = toml.load(path)

    except IOError as e:
        error(IOError(f"cannot load font from {format_filename(path)}: {e.strerror.lower()}"))

    except TomlDecodeError as e:
        error(ProfileError(f"cannot load font from {format_filename(path)}: {str(e).lower()}"))

    return parse_profile(path.name, root)


def parse_root(name: str, root: dict) -> Tuple[ProfileType, float]:
    """Gets the global properties of the Profile, returning a tuple containing the KeyType and the
    depth"""

    for key, type in (("type", str), ("depth", Real)):
        try:
            if not isinstance(root[key], type):
                error(ProfileError(f"invalid value for '{key}' in profile {format_filename(name)}"))
        except KeyError:
            error(ProfileError(f"no '{key}' key in profile {format_filename(name)}"))

    depth = milliunit(root["depth"])
    type = root["type"]

    try:
        type = ProfileType.from_str(type)
    except ValueError:
        error(ProfileError(f"invalid value for '{key}' in profile {format_filename(name)}"))

    return type, (depth if type != ProfileType.FLAT else 0)


def parse_bottom(bottom: dict) -> RoundRect:
    """Parses the properties of the key's bottom rectangle, returning a RoundRect object"""

    for key in ("width", "height", "radius"):
        try:
            if not isinstance(bottom[key], Real):
                error(ProfileError(f"invalid value for '{key}' in section [bottom]"))
        except KeyError:
            error(ProfileError(f"no '{key}' key in section [bottom]"))

    width = milliunit(bottom["width"])
    height = milliunit(bottom["height"])
    radius = milliunit(bottom["radius"])

    x = 500 - (width / 2)
    y = 500 - (height / 2)

    return RoundRect(x, y, width, height, radius)


def parse_top(top: dict) -> Tuple[RoundRect, float]:
    """Parses the properties of the key's top rectangle, returning a tuple containing RoundRect
    object and a float representing the y-offset"""

    for key in ("width", "height", "radius"):
        try:
            if not isinstance(top[key], Real):
                error(ProfileError(f"invalid value for '{key}' in section [top]"))
        except KeyError:
            error(ProfileError(f"no '{key}' key in section [top]"))

    # Allow a default value of 0 for y-offset
    if not isinstance(top.get("y-offset", 0), Real):
        error(ProfileError("invalid value for 'y-offset' in section [top]"))

    width = milliunit(top["width"])
    height = milliunit(top["height"])
    radius = milliunit(top["radius"])
    offset = milliunit(top.get("y-offset", 0))

    x = 500 - (width / 2)
    y = 500 - (height / 2) + offset

    return RoundRect(x, y, width, height, radius), offset


def parse_legend(
    legend_props: dict, top_offset: float
) -> Tuple[TextTypeProperty[Rect], TextTypeProperty[float]]:
    """Parses the properties of the key's legend alignment rectangles, returning a tuple containing
    TextTypeProperty[Rect] and TextTypeProperty[float] objects containing the rect and size,
    respectively"""

    # Check for default values
    defaults = {}
    for key in ("width", "height", "y-offset"):
        if key in legend_props:
            if not isinstance(legend_props[key], Real):
                error(ProfileError(f"invalid value for '{key}' in section [legend]"))
            else:
                defaults[key] = legend_props[key]

    text_types = TextTypeProperty._fields
    for txt_type in text_types:
        if txt_type not in legend_props or not isinstance(legend_props[txt_type], dict):
            error(ProfileError(f"no {txt_type} section in section [legend]"))

        legend_props[txt_type] = {**defaults, **legend_props[txt_type]}

    text_rects, text_sizes = zip(
        *(parse_legend_type(tt, legend_props[tt], top_offset) for tt in text_types)
    )

    return TextTypeProperty(*text_rects), TextTypeProperty(*text_sizes)


def parse_legend_type(type: str, legend_props: dict, top_offset: float) -> Tuple[Rect, float]:
    """Parses the properties of the key's legend alignment rectangle for a specific key type,
    returning a Rect object"""

    for key in ("width", "height", "size"):
        try:
            if not isinstance(legend_props[key], Real):
                error(ProfileError(f"invalid value for '{key}' in section [legend.{type}]"))
        except KeyError:
            error(ProfileError(f"no '{key}' key in section [legend.{type}]"))

    # Allow a default value of 0 for y-offset
    if not isinstance(legend_props.get("y-offset", 0), Real):
        error(ProfileError(f"invalid value for 'y-offset' in section [legend.{type}]"))

    width = milliunit(legend_props["width"])
    height = milliunit(legend_props["height"])
    size = milliunit(legend_props["size"])
    offset = milliunit(legend_props.get("y-offset", 0)) + top_offset

    x = 500 - (width / 2)
    y = 500 - (height / 2) + offset

    return Rect(x, y, width, height), size


def parse_homing(homing_props: dict) -> HomingProperties:
    """Parses the properties defining the different kinds of homing keys, returning a
    HomingProperties instance"""

    # Determine the default homing type
    try:
        default = HomingType.from_str(homing_props["default"])
    except KeyError:
        error(ProfileError("no 'default' key in section [homing]"))
    except ValueError:
        error(ProfileError("invalid value for 'default' in section [homing]"))

    scoop_props = None
    bar_props = None
    bump_props = None

    try:
        if not isinstance(homing_props["scoop"], dict):
            error(ProfileError("no 'scoop' section in section [homing]"))
        scoop_props = parse_homing_scoop(homing_props["scoop"])
    except KeyError:
        pass  # Allow missing homing types

    try:
        if not isinstance(homing_props["bar"], dict):
            error(ProfileError("no 'bar' section in section [homing]"))
        bar_props = parse_homing_bar(homing_props["bar"])
    except KeyError:
        pass  # Allow missing homing types

    try:
        if not isinstance(homing_props["bump"], dict):
            error(ProfileError("no 'bump' section in section [homing]"))
        bump_props = parse_homing_bump(homing_props["bump"])
    except KeyError:
        pass  # Allow missing homing types

    return HomingProperties(
        default=default,
        scoop=scoop_props,
        bar=bar_props,
        bump=bump_props,
    )


def parse_homing_scoop(scoop_props: dict) -> HomingScoop:
    """Parses the properties for scooped homing keys, returning a HomingScoop object"""

    if "depth" not in scoop_props:
        error(ProfileError("no 'depth' key in section [homing.scoop]"))
    elif not isinstance(scoop_props["depth"], Real):
        error(ProfileError("invalid value for 'depth' in section [homing.scoop]"))

    return HomingScoop(milliunit(scoop_props["depth"]))


def parse_homing_bar(bar_props: dict) -> HomingBar:
    """Parses the properties for barred homing keys, returning a HomingBar object"""

    for key in ("width", "height", "y-offset"):
        try:
            if not isinstance(bar_props[key], Real):
                error(ProfileError(f"invalid value for '{key}' in section [homing.bar]"))
        except KeyError:
            error(ProfileError(f"no '{key}' key in section [homing.bar]"))

    width = milliunit(bar_props["width"])
    height = milliunit(bar_props["height"])
    offset = milliunit(bar_props["y-offset"])

    return HomingBar(width, height, offset)


def parse_homing_bump(bump_props: dict) -> HomingBump:
    """Parses the properties for bumped homing keys, returning a HomingBump object"""

    for key in ("radius", "y-offset"):
        try:
            if not isinstance(bump_props[key], Real):
                error(ProfileError(f"invalid value for '{key}' in section [homing.bump]"))
        except KeyError:
            error(ProfileError(f"no '{key}' key in section [homing.bump]"))

    radius = milliunit(bump_props["radius"])
    offset = milliunit(bump_props["y-offset"])

    return HomingBump(radius, offset)


def parse_profile(name: str, profile_props: dict) -> Profile:
    """Parse a profile from a dict containing its propreties"""

    type, depth = parse_root(name, profile_props)

    for section in ("top", "bottom", "legend", "homing"):
        if section not in profile_props or not isinstance(profile_props[section], dict):
            error(ProfileError(f"no '{section}' section in profile {format_filename(name)}"))

    bottom_rect = parse_bottom(profile_props["bottom"])
    top_rect, top_offset = parse_top(profile_props["top"])
    text_rect, text_size = parse_legend(profile_props["legend"], top_offset)
    homing_props = parse_homing(profile_props["homing"])

    return Profile(
        name=name,
        type=type,
        depth=depth,
        bottom_rect=bottom_rect,
        top_rect=top_rect,
        text_rect=text_rect,
        text_size=text_size,
        homing=homing_props,
    )


def milliunit(millimeter: float) -> float:
    """Converts from millimeter (mm) to milliunit (mu). (Note 1000mu == 1u == 19.05mm == 0.75in)"""

    return millimeter * (1000 / 19.05)
