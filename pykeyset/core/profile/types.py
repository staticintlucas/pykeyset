# -*- coding: utf-8 -*-

import sys
from enum import Enum
from typing import Generic, NamedTuple, Optional, TypeVar


class ProfileType(Enum):
    CYLINDRICAL = 0
    SPHERICAL = 1
    FLAT = 2

    @staticmethod
    def from_str(string: str) -> "ProfileType":
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
    def from_str(string: str) -> "HomingType":
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
    scoop: Optional[HomingScoop]
    bar: Optional[HomingBar]
    bump: Optional[HomingBump]


# Combining NamedTuple with Generic directly is not possible since NamedTuple performs a lot of
# trickery under the hood, removing __class_getitem__ which makes generics work. Unless we want a
# bunch of 'type is not subscriptable' errors for every type hint we need to create a NamedTuple
# subclass and then use that as the base class for our type.
#
# Also, in Python 3.6 this solution fails due to a metaclass conflict between NamedTuple and
# Generic, while on Python >= 3.7 Generic has no metaclass. So we handle 3.6 separately.
#
# TODO change this when we drop support for 3.6. NamedTuple works more nicely in >= 3.7 with a
# `from __future__ import annotations`. Unfortunately we can't use that until we drop 3.6 support
# since we can't conditionally import it and it doesn't exist in 3.6.

T = TypeVar("T")


class TextTypePropertyBase(NamedTuple):
    alpha: T
    symbol: T
    mod: T


if sys.version_info >= (3, 7):  # pragma: no cover

    class TextTypeProperty(TextTypePropertyBase, Generic[T]):
        pass


else:  # pragma: no cover
    from typing import GenericMeta

    class TextTypePropertyMeta(GenericMeta):
        pass

    class TextTypeProperty(TextTypePropertyBase, Generic[T], metaclass=TextTypePropertyMeta):
        pass
