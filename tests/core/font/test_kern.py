# -*- coding: utf-8 -*-

from pykeyset.core.font.kerning import Kerning

KERNINGS = {
    ("a", "b"): 2,
    ("c", "d"): 3,
    ("e", "f"): 4,
    ("a", "f"): 6,
}


def test_kerning():

    kerning = Kerning(1)

    assert len(kerning) == 0
    assert kerning.get("x", "y", 1) == 0

    for (lhs, rhs), value in KERNINGS.items():
        kerning.set(lhs, rhs, value)

    assert len(kerning) == len(KERNINGS)

    kerning.delete("e", "f")
    assert len(kerning) == len(KERNINGS) - 1
    assert kerning.get("e", "f", 1) == 0
