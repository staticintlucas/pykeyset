from collections import namedtuple
import itertools
import pytest
import re
import sys
import tomllib

import pykeyset

# Fixtures to read the expected version from Cargo.toml

@pytest.fixture(scope="module")
def exp_version_str():
    with open("Cargo.toml", "rb") as f:
        return tomllib.load(f)["package"]["version"]

@pytest.fixture(scope="module")
def exp_version_tuple(exp_version_str):
    regex = re.compile(r"(\d+)\.(\d+)\.(\d+)(?:-(\w+)\.?(\d+))?", flags=re.ASCII)
    [major, minor, patch, level, serial] = regex.fullmatch(exp_version_str).groups()
    major = int(major)
    minor = int(minor)
    patch = int(patch)
    level = "final" if level is None else level
    serial = 0 if serial is None else int(serial)

    return (major, minor, patch, level, serial)

# Tests for version values

def test_version_info(exp_version_tuple):
    (major, minor, patch, level, serial) = exp_version_tuple

    assert pykeyset.version_info.major == int(major)
    assert pykeyset.version_info.minor == int(minor)
    assert pykeyset.version_info.patch == int(patch)
    assert pykeyset.version_info.releaselevel == level
    assert pykeyset.version_info.serial == int(serial)

def test_version(exp_version_str):
    assert pykeyset.version == exp_version_str
    assert pykeyset.__version__ == exp_version_str

# Tests for version_info type

def test_version_info_type():
    assert type(pykeyset.version_info).__name__ == "version_info"
    assert type(pykeyset.version_info).__module__ == "pykeyset"

@pytest.mark.parametrize("tuple", [
    (1, 2, 3, "alpha", 1),
    (1, 2, 3, "beta", 2),
    (1, 2, 3, "candidate", 3),
    (1, 2, 3, "final", 0),
])
def test_version_info_new(tuple):
    (major, minor, patch, level, serial) = tuple

    version = type(pykeyset.version_info)(*tuple)

    assert version.major == int(major)
    assert version.minor == int(minor)
    assert version.patch == int(patch)
    assert version.releaselevel == level
    assert version.serial == int(serial)

@pytest.mark.parametrize("tuple, error", [
    ((-1, 2, 3, "final", 0), OverflowError),
    ((1, 2, 3, "bleh", 1), ValueError),
    (("1", 2, 3, "bleh", 1), TypeError),
])
def test_version_info_new_error(tuple, error):
    with pytest.raises(error):
        type(pykeyset.version_info)(*tuple)

@pytest.mark.parametrize("tuple, x", [
    ((1, 2, 3, "final", 0), 1),
    ((1, 2, 3, "final", 0), 2),
    ((1, 2, 3, "final", 0), "final"),
    ((1, 2, 3, "final", 0), "alpha"),
    ((0, 1, 1, "candidate", 1), 1),
])
def test_version_info_count(tuple, x):
    version = type(pykeyset.version_info)(*tuple)

    assert version.count(x) == tuple.count(x)

@pytest.mark.parametrize("tuple, params", [
    ((1, 2, 3, "final", 0), (1,)),
    ((1, 2, 3, "final", 0), (2,)),
    ((1, 2, 3, "final", 0), ("final",)),
    ((0, 2, 3, "final", 0), (0, 1)),
    ((0, 2, 3, "final", 0), (0, -4)),
    ((0, 1, 1, "candidate", 1), (1,)),
    ((0, 1, 1, "candidate", 1), (1, 3)),
    ((0, 1, 1, "candidate", 1), (1, -2)),
    ((0, 1, 1, "candidate", 1), (1, 1, 3)),
    ((0, 1, 1, "candidate", 1), (1, -4, 3)),
    ((0, 1, 1, "candidate", 1), (1, 1, -2)),
    ((0, 1, 1, "candidate", 1), (1, -4, -2)),
])
def test_version_info_index(tuple, params):
    version = type(pykeyset.version_info)(*tuple)

    assert version.index(*params) == tuple.index(*params)

@pytest.mark.parametrize("tuple, params", [
    ((1, 2, 3, "final", 0), (4,)),
    ((1, 2, 3, "final", 0), ("alpha",)),
    ((1, 2, 3, "final", 0), (1, 1)),
    ((1, 2, 3, "final", 0), (0, 0, 4)),
    ((1, 2, 3, "final", 0), (1, "bleh")),
    ((1, 2, 3, "final", 0), (1, 0, "bleh")),
])
def test_version_info_index_error(tuple, params):
    version = type(pykeyset.version_info)(*tuple)

    with pytest.raises(Exception) as e:
        tuple.index(*params)

    with pytest.raises(e.type):
        version.index(*params)

@pytest.mark.parametrize("tuple", [
    (1, 2, 3, "alpha", 1),
    (2, 3, 4, "beta", 2),
    (4, 6, 8, "candidate", 3),
    (27, 4, 69, "final", 0),
])
def test_version_info_str(tuple):
    version = type(pykeyset.version_info)(*tuple)

    (major, minor, patch, level, serial) = tuple
    if level == "final":
        exp = f"{major}.{minor}.{patch}"
    else:
        exp = f"{major}.{minor}.{patch}-{level}{serial}"

    assert str(version) == exp

@pytest.mark.parametrize("tuple", [
    (1, 2, 3, "alpha", 1),
    (2, 3, 4, "beta", 2),
    (4, 6, 8, "candidate", 3),
    (27, 4, 69, "final", 0),
])
def test_version_info_repr(tuple):
    version = type(pykeyset.version_info)(*tuple)

    Exp = namedtuple("version_info", ["major", "minor", "patch", "releaselevel", "serial"])
    exp = Exp(*tuple)
    exp_repr = repr(exp)
    # namedtuple doesn't include the module, while most other reprs including sys.version_info do
    exp_repr = f"pykeyset.{exp_repr}"

    assert repr(version) == exp_repr

@pytest.mark.parametrize("major", range(0, 3))
@pytest.mark.parametrize("minor", range(1, 4))
@pytest.mark.parametrize("patch", range(2, 5))
@pytest.mark.parametrize("level", ["alpha", "beta", "candidate", "final"])
@pytest.mark.parametrize("serial", range(0, 3))
def test_version_info_rich_cmp(major, minor, patch, level, serial):
    tuple1 = (1, 2, 3, "beta", 1)
    version1 = type(pykeyset.version_info)(*tuple1)

    tuple2 = (major, minor, patch, level, serial)
    version2 = type(pykeyset.version_info)(*tuple2)

    assert (version1 < version2) == (tuple1 < tuple2)
    assert (version1 <= version2) == (tuple1 <= tuple2)
    assert (version1 > version2) == (tuple1 > tuple2)
    assert (version1 >= version2) == (tuple1 >= tuple2)
    assert (version1 == version2) == (tuple1 == tuple2)
    assert (version1 != version2) == (tuple1 != tuple2)

    assert (version1 < tuple2) == (tuple1 < tuple2)
    assert (version1 <= tuple2) == (tuple1 <= tuple2)
    assert (version1 > tuple2) == (tuple1 > tuple2)
    assert (version1 >= tuple2) == (tuple1 >= tuple2)
    assert (version1 == tuple2) == (tuple1 == tuple2)
    assert (version1 != tuple2) == (tuple1 != tuple2)

    assert (tuple1 < version2) == (tuple1 < tuple2)
    assert (tuple1 <= version2) == (tuple1 <= tuple2)
    assert (tuple1 > version2) == (tuple1 > tuple2)
    assert (tuple1 >= version2) == (tuple1 >= tuple2)
    assert (tuple1 == version2) == (tuple1 == tuple2)
    assert (tuple1 != version2) == (tuple1 != tuple2)

def test_version_info_len(exp_version_tuple):
    assert len(pykeyset.version_info) == len(exp_version_tuple)

@pytest.mark.parametrize("tuple", [
    (1, 2, 3, "final", 0),
    (0, 1, 1, "candidate", 1)
])
@pytest.mark.parametrize("x", [
    *range(-5, 5),
    *(slice(a, b) for a, b in itertools.product(range(-5, 5), range(-5, 5))),
    *(slice(a, b, c) for a, b, c in itertools.product(range(-5, 5), range(-5, 5), [*range(-5, 0), *range(1, 5)])),
])
def test_version_info_getitem(tuple, x):
    version = type(pykeyset.version_info)(*tuple)

    assert version[x] == tuple[x]

@pytest.mark.parametrize("tuple", [
    (1, 2, 3, "final", 0),
    (0, 1, 1, "candidate", 1)
])
@pytest.mark.parametrize("x", [
    -6,
    5,
    "bleh",
    None,
    slice("bleh", 3, 1),
    slice(1, 3, 0),
])
def test_version_info_getitem_error(tuple, x):
    version = type(pykeyset.version_info)(*tuple)

    with pytest.raises(Exception) as e:
        tuple[x]

    with pytest.raises(e.type):
        version[x]

@pytest.mark.parametrize("tuple", [
    (1, 2, 3, "final", 0),
    (0, 1, 1, "candidate", 1)
])
@pytest.mark.parametrize("x", [
    (-6,),
    (5,),
    ("bleh",),
    (None,),
    ("bleh", 3, 1),
    (1, 3, 0),
])
def test_version_info_concat(tuple, x):
    version = type(pykeyset.version_info)(*tuple)

    assert version + x == tuple + x


@pytest.mark.parametrize("tuple, el, exp", [
    ((1, 2, 3, "final", 0), 1, True),
    ((1, 2, 3, "final", 0), 2, True),
    ((1, 2, 3, "final", 0), "final", True),
    ((0, 2, 3, "final", 0), 0, True),
    ((0, 2, 3, "final", 0), 0, True),
    ((1, 2, 3, "final", 0), 4, False),
    ((1, 2, 3, "final", 0), "alpha", False),
])
def test_version_info_contains(tuple, el, exp):
    version = type(pykeyset.version_info)(*tuple)

    assert (el in version) == exp

def test_version_info_match_args():
    Exp = namedtuple("version_info", ["major", "minor", "patch", "releaselevel", "serial"])

    assert pykeyset.version_info.__match_args__ == Exp.__match_args__

@pytest.mark.parametrize("tuple, x", [
    ((1, 2, 3, "final", 0), 0),
    ((1, 2, 3, "final", 0), 1),
    ((1, 2, 3, "final", 0), 2),
    ((1, 2, 3, "final", 0), 50),
])
def test_version_info_repeat(tuple, x):
    version = type(pykeyset.version_info)(*tuple)

    assert version * x == tuple * x

@pytest.mark.parametrize("tuple", [
    (1, 2, 3, "final", 0),
])
def test_version_info_iter(tuple):
    version = type(pykeyset.version_info)(*tuple)

    for v, t in zip(version, tuple):
        assert v == t

def test_build_info(exp_version_str):
    exp = [
        rf"pykeyset {re.escape(exp_version_str)} \(.*\)",
        r"python:",
        rf"  target: {re.escape(sys.implementation.name)} .*",
        rf"  using: {re.escape(sys.version)}",
        r"rust:",
        r"  compiler: rustc 1\.\d+\.\d+.*",
        r"  host: .*",
        r"  target: .*",
        r"build:",
        r"  profile: .*",
        r"  opt_level: .*",
        r"  debug: .*",
        r"dependencies:",
        r"  keyset-rs: \d+\.\d+\.\d+",
        r"  pyo3: \d+\.\d+\.\d+",
    ]

    assert len(pykeyset.build_info().splitlines()) == len(exp)

    for line, pat in zip(pykeyset.build_info().splitlines(), exp):
        print(line, pat)
        assert re.fullmatch(pat, line) is not None
