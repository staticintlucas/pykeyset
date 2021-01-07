# -*- coding: utf-8 -*-

import contextlib
import os
import pathlib

import pytest

from pykeyset.__main__ import main
from pykeyset.utils.config import config


@contextlib.contextmanager
def cwd(path):
    old_cwd = pathlib.Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_cwd)


@pytest.mark.slow
def test_cmdlist(tmp_path):

    cmdlist = "test.cmdlist"
    contents = """
        load kle http://www.keyboard-layout-editor.com/#/gists/102f1fb614275f50e39d970d691e1030
        load profile cherry
        load font cherry
        generate layout
        save svg test.svg
        """

    d = tmp_path / "pykeyset_test"
    d.mkdir()

    f = d / cmdlist
    f.write_text(contents)

    with cwd(d):
        config.load_argv([cmdlist])
        main()
