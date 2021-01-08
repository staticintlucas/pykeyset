# -*- coding: utf-8 -*-

import pytest

from pykeyset.utils import config
from pykeyset.utils.error import Verbosity


@pytest.fixture
def reset_config():
    # Reset the global configuration for each test
    config.config._private = config.Config()


@pytest.mark.parametrize(
    "key, val",
    [
        ("color", None),
        ("profile", False),
        ("dpi", 96),
        ("is_script", False),
        ("verbosity", Verbosity.QUIET),
        ("showalignment", False),
        ("_cmdlists", []),
        ("_commands", []),
    ],
)
def test_default(reset_config, key, val):
    assert getattr(config.config, key) == val


@pytest.mark.parametrize(
    "arg, key, val",
    [
        (["--color"], "color", True),
        (["--no-color"], "color", False),
        (["--profile"], "profile", True),
        (["--dpi=192"], "dpi", 192),
        ([""], "is_script", True),
        ([""], "verbosity", Verbosity.NORMAL),
        (["-q"], "verbosity", Verbosity.QUIET),
        (["-v"], "verbosity", Verbosity.VERBOSE),
        (["--show-alignment"], "showalignment", True),
        (["example.cmdlist"], "_cmdlists", ["example.cmdlist"]),
        (["-c", "load font cherry"], "_commands", ["load font cherry"]),
    ],
)
def test_argv(reset_config, arg, key, val):

    config.config.load_argv(arg)

    assert getattr(config.config, key) == val


def test_clone():

    tmpconf = config.Config(color=True, unknown=5)
    conf = config.Config(clone=tmpconf)

    assert conf.color

    with pytest.raises(AttributeError):
        _ = conf.unknown


def test_help_version(reset_config):

    with pytest.raises(SystemExit):
        config.config.load_argv(["--help"])

    with pytest.raises(SystemExit):
        config.config.load_argv(["--version"])


def test_get_commands(reset_config, tmp_path):

    cmdlist1 = "test1.cmdlist"
    cmdlist2 = "test2.cmdlist"

    d = tmp_path / "pykeyset_test"
    d.mkdir()

    f1 = d / cmdlist1
    f1.write_text(
        """
        load font gorton
        ; comment
        generate layout
        """
    )

    f2 = d / cmdlist2
    f2.write_text("")  # Empty file should be ignored

    config.config.load_argv(["-c", "load font cherry", "-c", "load profile kat", str(f1), str(f2)])

    expected = {
        "-c ...": ["load font cherry", "load profile kat"],
        str(f1): ["load font gorton", "generate layout"],
    }

    assert config.config._private._get_commands() == expected
