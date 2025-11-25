from math import isclose
import pytest

import pykeyset

@pytest.mark.parametrize("input, expected", [
    ((0.2, 0.4, 0.6), (0.2, 0.4, 0.6)),
    ([0.2, 0.4, 0.6], (0.2, 0.4, 0.6)),
    ({ "r": 0.2, "g": 0.4, "b": 0.6 }, (0.2, 0.4, 0.6)),
    ("336699", (0.2, 0.4, 0.6)),
    ("#336699", (0.2, 0.4, 0.6)),
    ("rgb(51, 102, 153)", (0.2, 0.4, 0.6)),
    ("hsl(210, 50%, 40%)", (0.2, 0.4, 0.6)),
])
def test_color(input, expected):
    output = pykeyset.test.color_identity(input)
    for o, e in zip(output, expected):
        assert isclose(o, e, rel_tol=0, abs_tol=1e-6)

class Dummy:
    pass

@pytest.mark.parametrize("input, error", [
    (Dummy, TypeError),
    (2, TypeError),
    ("bad string", ValueError),
    ((2.2, 0.5, 0.5), ValueError),
    ((0.5, -0.1, 0.5), ValueError),
])
def test_color_error(input, error):
    with pytest.raises(error):
        pykeyset.test.color_identity(input)

@pytest.mark.parametrize("input, expected", [
    ((0.2, 0.4, 0.6), (0.2, 0.4, 0.6)),
    ([0.2, 0.4, 0.6], (0.2, 0.4, 0.6)),
    ({ "r": 0.2, "g": 0.4, "b": 0.6 }, (0.2, 0.4, 0.6)),
    ("336699", (0.2, 0.4, 0.6)),
    ("#336699", (0.2, 0.4, 0.6)),
    ("rgb(51, 102, 153)", (0.2, 0.4, 0.6)),
    ("hsl(210, 50%, 40%)", (0.2, 0.4, 0.6)),
])
def test_color_rust_round_trip(input, expected):
    output = pykeyset.test.color_round_trip(input)
    for o, e in zip(output, expected):
        assert isclose(o, e, rel_tol=0, abs_tol=1e-6)
