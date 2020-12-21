# coding: utf-8

import sys
from os import path
from argparse import ArgumentParser, ArgumentError

from .. import __version__
from .output import error

NAME = 'keyset.py'
PROG = 'keyset'
DESCRIPTION = "This script can process a individual commands (with the -c option) or a cmdlist \
file containing a sequence of commands. A cmdlist can also set most options with the set command. \
A cmdlist option will override a command line option if both are present."
VERSION_STR = '''{:s} version {:s}
Copyright (c) 2020 Lucas Jansen'''.format(NAME, __version__)


def printandexit(string):
    print(string, file=sys.stderr)
    sys.exit(0)


class Config():

    def __init__(self, args):

        parser = ArgumentParser(
            prog=PROG, description=DESCRIPTION, allow_abbrev=False, add_help=False)

        # Add all arguments to the parser instance
        parser.add_argument('-h', '--help',
            action='store_true', help='show this help message and exit')
        parser.add_argument('-V', '--version',
            action='store_true', help='show version information')
        parser.add_argument('-v', '--verbose',
            action='store_true', help='display verbose output')
        parser.add_argument('--color',
            action='store_true', dest='color', default=None, help='enable colored output')
        parser.add_argument('--no-color',
            action='store_false', dest='color', default=None, help='disable colored output')
        # parser.add_argument('--profile',
        #     action='store_true', help='print profiling information')
        parser.add_argument('-d', '--dpi',
            type=int, metavar='<dpi>', help='the DPI for the output (default: 96 [i.e. 1u = 72])')
        parser.add_argument('-c',
            type=str, metavar='"<command>"', action='append', dest='commands', help='execute a command')
        parser.add_argument('cmdlist',
            type=str, nargs='*', metavar='<cmdlist>', help='command list file')

        # Parse the args
        self.args = {k: v for k, v in vars(parser.parse_args(args)).items() if v is not None}

        if self.args.get('help', False):
            # Import only as needed to avoid circular dependencies
            from .. import commands

            parser.print_help(sys.stderr)
            print(file=sys.stderr)
            print(commands.help(), file=sys.stderr)

            sys.exit(0)

        elif self.args.get('version', False):
            print(VERSION_STR, file=sys.stderr)

            sys.exit(0)

        commands = self.args.get('commands', [])
        cmdlists = self.args.get('cmdlist', [])

        self.verbose = self.args.get('verbose', False)
        self.color = self.args.get('color', None)
        self.profile = self.args.get('profile', False)
        self.dpi = self.args.get('dpi', 96)
        self.commands = []

        if len(cmdlists) > 0:
            if len(commands) > 0:
                error(self, 'cannot read a cmdlist and execute commands with -c at the same time')
                sys.exit(1)

            for cl in cmdlists:
                with open(cl) as f:
                    for line in f:
                        # Strip out comments
                        line = line.split(';', 1)[0].strip()

                        if len(line) == 0:
                            continue # Ignore empty lines

                        self.commands.append(line)

                # Add a reset between cmdlists so the goings on in one doesn't affect the next
                self.commands.append(['reset'])

        else:
            for cmd in commands:
                self.commands.append(cmd)


    def is_set(self, attribute):

        return attribute in self.args and attribute in vars(self)
