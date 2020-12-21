# coding: utf-8

import sys
from inspect import signature

from ..utils import error, info

from colorama import Style

COMMANDS = {
    'load kle': dict(args='(<file>|<url>)', fun=lambda *_: None,
        desc='load a keyboard layout editor layout'),
    'load font': dict(args='(<name>|<file>)', fun=lambda *_: None,
        desc='load an SVG font file (use name for built in fonts)'),
    'load novelty': dict(args='<file>', fun=lambda *_: None,
        desc='load an SVG novelty file'),
    'load profile': dict(args='(<name>|<file>)', fun=lambda *_: None,
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
    'set': dict(args='<option> [<value>]', fun=lambda *_: None,
        desc='set an option (overrides command line options)'),
    'reset': dict(args='[<arg>]', fun=lambda *_: None,
        desc='reset the given option (default: reset all options)'),
}

WIDTH = 24


def execute(conf, command):

    for cmd, val in COMMANDS.items():

        if command.startswith(cmd):

            if conf.verbose:
                info(conf, f"executing command '{command}'")

            fun = val['fun']
            args = command[len(cmd):].split()

            fun(args)
            break

    else:
        error(conf, f"unknown command '{command.split()[0]}'")
        sys.exit(1)


def help():

    message = ['commands:']

    for cmd, val in COMMANDS.items():

        msg = f'  {cmd} {val["args"]}'

        if len(msg) > WIDTH - 2:
            msg = f'{msg}\n{" " * WIDTH}{val["desc"]}'
        else:
            msg = f'{msg.ljust(WIDTH)}{val["desc"]}'

        message.append(msg)

    return '\n'.join(message)
