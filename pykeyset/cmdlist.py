# -*- coding: utf-8 -*-

from inspect import signature

from . import core
from .utils.error import error, info

COMMANDS = {
    "load kle": dict(
        args="{<file>|<url>}",
        fun=core.KleFile.load,
        desc="load a Keyboard Layout Editor URL or JSON file",
    ),
    "load font": dict(
        args="{<name>|<file>}",
        fun=core.Font.load,
        desc="load an XML font file",
    ),
    "load icons": dict(
        args="<file>",
        fun=core.Icons.load,
        desc="load an XML icon or novelty file (use name for built in icons)",
    ),
    "load profile": dict(
        args="{<name>|<file>}",
        fun=core.Profile.load,
        desc="load an keycap profile configuration file",
    ),
    "generate layout": dict(
        args="",
        fun=core.Layout.layout,
        desc="generate a layout diagram from the loaded assets",
    ),
    # "generate texture": dict(
    #     args="",
    #     fun=lambda *_: None,
    #     desc="generate a texture file (for renders, etc.)",
    # ),
    "save svg": dict(
        args="[<file>]",
        fun=core.save.as_svg,
        desc="export the generated graphic as an SVG file",
    ),
    # "save png": dict(
    #     args="[<file>]",
    #     fun=lambda *_: None,
    #     desc="export the generated graphic as a PNG image",
    # ),
    # "save ai": dict(
    #     args="[<file>]",
    #     fun=lambda *_: None,
    #     desc="export the generated graphic as an Illustrator file",
    # ),
    "newfont": dict(
        args="<file> <src>",
        fun=lambda ctx, outp, inp: core.fontgen.fontgen(outp, inp),
        desc="create a new XML font file from a source font",
    ),
}

FMT_HELP_WIDTH = 24


def execute(name, commands):

    context = core.Context(name)

    for line in commands:

        line = " ".join(line.split()) + " "
        cmd = next((c for c in COMMANDS if line.startswith(c + " ")), None)

        if cmd is None:
            error(f"invalid command '{line}'")

        info(f"executing command '{line}'")

        fun = COMMANDS[cmd]["fun"]
        num_args = len(signature(fun).parameters) - 1  # Subtract one for the context

        args = line[len(cmd) :].split()

        if len(args) < num_args:
            error(f"not enough arguments for command '{cmd}' in '{name}'")
        elif len(args) > num_args:
            error(f"too many arguments for command '{cmd}' in '{name}'")
        else:
            fun(context, *args)


def help_msg():

    message = ["commands:"]

    for cmd, val in COMMANDS.items():

        msg = f'  {cmd} {val["args"]}'

        if len(msg) > FMT_HELP_WIDTH - 2:
            msg = f'{msg}\n{" " * FMT_HELP_WIDTH}{val["desc"]}'
        else:
            msg = f'{msg.ljust(FMT_HELP_WIDTH)}{val["desc"]}'

        message.append(msg)

    return "\n".join(message)


__all__ = ["execute", "help_msg"]
