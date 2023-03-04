from __future__ import annotations

from enum import Enum
from typing import Generic, NamedTuple, TypeVar


class ProfileType(Enum):
    CYLINDRICAL = 0
    SPHERICAL = 1
    FLAT = 2

    @staticmethod
    def from_str(string: str) -> ProfileType:
        try:
            return ProfileType[string.upper()]
        except KeyError:
            raise ValueError(f"String '{string}' does not represent a valid enum variant")


class GradientType(Enum):
    KEY = 0
    SCOOP = 1
    SPACE = 2


class HomingType(Enum):
    SCOOP = 0
    BAR = 1
    BUMP = 2

    @staticmethod
    def from_str(string: str) -> HomingType:
        try:
            return HomingType[string.upper()]
        except KeyError:
            raise ValueError(f"String '{string}' does not represent a valid enum variant")


class HomingScoop(NamedTuple):
    depth: float


class HomingBar(NamedTuple):
    width: float
    height: float
    offset: float


class HomingBump(NamedTuple):
    radius: float
    offset: float


class HomingProperties(NamedTuple):
    default: HomingType
    scoop: HomingScoop | None
    bar: HomingBar | None
    bump: HomingBump | None


T = TypeVar("T")


class TextTypeProperty(NamedTuple, Generic[T]):
    alpha: T
    symbol: T
    mod: T
