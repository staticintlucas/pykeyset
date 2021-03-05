# -*- coding: utf-8 -*-

import re
from pathlib import Path
from textwrap import dedent

import click.core
import pytest
import typer

from pykeyset import cmdlist, core


@pytest.fixture
def dont_call(monkeypatch):

    monkeypatch.setitem(cmdlist.COMMANDS, "load kle", lambda ctx, file: print("kle", file))
    monkeypatch.setitem(cmdlist.COMMANDS, "load font", lambda ctx, file: print("font", file))
    monkeypatch.setitem(cmdlist.COMMANDS, "load icons", lambda ctx, file: print("icon", file))
    monkeypatch.setitem(cmdlist.COMMANDS, "load profile", lambda ctx, file: print("profile", file))
    monkeypatch.setitem(cmdlist.COMMANDS, "generate layout", lambda ctx: print("layout"))
    monkeypatch.setitem(cmdlist.COMMANDS, "save svg", lambda ctx, file: print("svg", file))
    monkeypatch.setitem(cmdlist.COMMANDS, "fontgen", lambda ctx, o, i: print("fontgen", o, i))


@pytest.mark.parametrize(
    "cmd, result",
    [
        ("load kle kleurl", "kle kleurl"),
        ("load font name", "font name"),
        ("load icons novelty", "icon novelty"),
        ("load profile meow", "profile meow"),
        ("generate layout", "layout"),
        ("save svg output", "svg output"),
        ("fontgen dest.xml src.ttf", "fontgen dest.xml src.ttf"),
        ("#comment", ""),
        ("load kle url #comment", "kle url"),
        ("load kle 'url #comment'", "kle url #comment"),
    ],
)
def test_cmdlist_line(capsys, dont_call, cmd, result):

    ctx = core.Context("test")

    cmdlist.run_line(ctx, cmd)
    stdout = capsys.readouterr().out

    assert stdout.strip() == result


def test_cmdlist(capsys, dont_call, tmp_path):

    d = tmp_path / "pykeyset_test"
    d.mkdir()

    text = dedent(
        """\
        load kle kleurl
        load font name
        load icons novelty
        load profile meow
        generate layout
        save svg output
        fontgen dest.xml src.ttf
        #comment
        load kle url #comment
        load kle 'url #comment'"""
    )

    result = dedent(
        """\
        kle kleurl
        font name
        icon novelty
        profile meow
        layout
        svg output
        fontgen dest.xml src.ttf
        kle url
        kle url #comment"""
    )

    f = d / "test.cmdlist"
    f.write_text(text)

    cmdlist.run(f)
    stdout = capsys.readouterr().out

    assert stdout.strip() == result

    with pytest.raises(IOError):
        cmdlist.run(Path("notfound.cmdlist"))


@pytest.mark.parametrize(
    "cmd",
    [
        "laod font name",
        "load font",
        "load font too many args",
        "load font #comment name",
    ],
)
def test_invalid_cmdlist(dont_call, cmd):

    ctx = core.Context("test")

    with pytest.raises(ValueError):
        cmdlist.run_line(ctx, cmd)


def test_format_options():

    expected = re.sub(
        r"\s+",
        " ",
        """Commands:
        load kle <file>           load a KLE Gist URL or local JSON file
        load font <file>          load a built in font or an XML font file
        load icons <file>         load built in icons or an XML icon/novelty file
        load profile <file>       load a built in profile or a profile config file
        generate layout           generate a layout diagram from the loaded resources
        save svg <filename>       export the generated graphic as an SVG file
        save png <filename>       export the generated graphic as a PNG file
        save ai <filename>        export the generated graphic as an AI file (experimental)
        newfont <output> <input>  create a new XML font file from a source font
        """,
    )

    cmdclass = click.Command("test")
    ctx = typer.Context(cmdclass)
    fmt = click.HelpFormatter()

    cmdlist.format_options(ctx, fmt)

    assert re.sub(r"\s+", " ", fmt.getvalue()) == expected
