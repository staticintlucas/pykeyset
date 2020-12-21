# coding: utf-8

import sys
from inspect import signature

from .utils.error import error, info
from . import command

from colorama import Style


COMMANDS = {
    'load kle': dict(args='{<file>|<url>}', fun=lambda *_: None,
        desc='load a keyboard layout editor layout'),
    'load font': dict(args='{<name>|<file>}', fun=command.load_font,
        desc='load an SVG font file (use name for built in fonts)'),
    'load novelty': dict(args='<file>', fun=lambda *_: None,
        desc='load an SVG novelty file'),
    'load profile': dict(args='{<name>|<file>}', fun=lambda *_: None,
        desc='load an keycap profile configuration file'),
    'generate layout': dict(args='', fun=lambda *_: None,
        desc='generate a layout diagram'),
    'generate texture': dict(args='', fun=lambda *_: None,
        desc='generate a texture file (for renders, etc.)'),
    'save svg': dict(args='[<file>]', fun=lambda *_: None,
        desc='export the generated graphic as an SVG file'),
    'save png': dict(args='[<file>]', fun=lambda *_: None,
        desc='export the generated graphic as a PNG image'),
    'save ai': dict(args='[<file>]', fun=lambda *_: None,
        desc='export the generated graphic as an Illustrator file'),
    'set': dict(args='<option> <value>', fun=lambda *_: None,
        desc='set an option (overrides command line options)'),
    'reset': dict(args='[<option>]', fun=lambda *_: None,
        desc='reset the given option (default: reset all options)'),
}

FMT_HELP_WIDTH = 24


def execute(conf, name, commands):

    context = command.Context(conf, name)

    for line in commands:

        cmd = next((c for c, _ in COMMANDS.items() if line.startswith(c)), None)

        if cmd is None:
            error(conf, f"invalid command '{line}'")

        info(conf, f"executing command '{line}'")

        fun = COMMANDS[cmd]['fun']

        args = line[len(cmd):].split()

        fun(context, *args)


def help_msg():

    message = ['commands:']

    for cmd, val in COMMANDS.items():

        msg = f'  {cmd} {val["args"]}'

        if len(msg) > FMT_HELP_WIDTH - 2:
            msg = f'{msg}\n{" " * FMT_HELP_WIDTH}{val["desc"]}'
        else:
            msg = f'{msg.ljust(FMT_HELP_WIDTH)}{val["desc"]}'

        message.append(msg)

    return '\n'.join(message)

__all__ = ['execute', 'help_msg']
