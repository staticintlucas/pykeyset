from __future__ import annotations

import pathlib
from typing import Any, MutableMapping

from ...utils.types import Rect, RoundRect
from .profile import Profile
from .types import (
    HomingBar,
    HomingBump,
    HomingProperties,
    HomingScoop,
    ProfileType,
    TextTypeProperty,
)


class ProfileError(ValueError):
    pass


def load_builtin(name: str) -> Profile:
    """Load a builtin profile by name, returning a Profile object"""

    raise NotImplementedError


def load_file(path: pathlib.Path) -> Profile:
    """Load a profile from the given path, returning a Profile object"""

    raise NotImplementedError


def parse_root(name: str, root: MutableMapping[str, Any]) -> tuple[ProfileType, float]:
    """Gets the global properties of the Profile, returning a tuple containing the KeyType and the
    depth"""

    raise NotImplementedError


def parse_bottom(bottom: MutableMapping[str, Any]) -> RoundRect:
    """Parses the properties of the key's bottom rectangle, returning a RoundRect object"""

    raise NotImplementedError


def parse_top(top: MutableMapping[str, Any]) -> tuple[RoundRect, float]:
    """Parses the properties of the key's top rectangle, returning a tuple containing RoundRect
    object and a float representing the y-offset"""

    raise NotImplementedError


def parse_legend(
    legend_props: MutableMapping[str, Any], top_offset: float
) -> tuple[TextTypeProperty[Rect], TextTypeProperty[float]]:
    """Parses the properties of the key's legend alignment rectangles, returning a tuple containing
    TextTypeProperty[Rect] and TextTypeProperty[float] objects containing the rect and size,
    respectively"""

    raise NotImplementedError


def parse_legend_type(
    type: str, legend_props: MutableMapping[str, Any], top_offset: float
) -> tuple[Rect, float]:
    """Parses the properties of the key's legend alignment rectangle for a specific key type,
    returning a Rect object"""

    raise NotImplementedError


def parse_homing(homing_props: MutableMapping[str, Any], top_offset: float) -> HomingProperties:
    """Parses the properties defining the different kinds of homing keys, returning a
    HomingProperties instance"""

    raise NotImplementedError


def parse_homing_scoop(scoop_props: MutableMapping[str, Any], _top_offset: float) -> HomingScoop:
    """Parses the properties for scooped homing keys, returning a HomingScoop object"""

    raise NotImplementedError


def parse_homing_bar(bar_props: MutableMapping[str, Any], top_offset: float) -> HomingBar:
    """Parses the properties for barred homing keys, returning a HomingBar object"""

    raise NotImplementedError


def parse_homing_bump(bump_props: MutableMapping[str, Any], top_offset: float) -> HomingBump:
    """Parses the properties for bumped homing keys, returning a HomingBump object"""

    raise NotImplementedError


def parse_profile(name: str, profile_props: MutableMapping[str, Any]) -> Profile:
    """Parse a profile from a MutableMapping[str, Any] containing its propreties"""

    raise NotImplementedError
