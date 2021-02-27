# -*- coding: utf-8 -*-

import pytest

from pykeyset.core.profile.types import HomingType, ProfileType


@pytest.mark.parametrize(
    "name, result",
    [
        ("cylindrical", ProfileType.CYLINDRICAL),
        ("spherical", ProfileType.SPHERICAL),
        ("flat", ProfileType.FLAT),
    ],
)
def test_profile_type(name, result):

    assert ProfileType.from_str(name) == result


def test_invalid_profile_type():

    with pytest.raises(ValueError):
        ProfileType.from_str("invalid")


@pytest.mark.parametrize(
    "name, result",
    [
        ("scoop", HomingType.SCOOP),
        ("bar", HomingType.BAR),
        ("bump", HomingType.BUMP),
    ],
)
def test_homing_type(name, result):

    assert HomingType.from_str(name) == result


def test_invalid_homing_type():

    with pytest.raises(ValueError):
        HomingType.from_str("invalid")
