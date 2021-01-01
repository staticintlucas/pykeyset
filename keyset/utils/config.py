# coding: utf-8

import sys
from os import path
from argparse import ArgumentParser, ArgumentError

from .. import __version__
from .error import Verbosity, error, warning


__all__ = ["config"]


NAME = "keyset.py"
PROG = "keyset"
DESCRIPTION = "This script can process a individual commands (with the -c option) or a cmdlist \
file containing a sequence of commands. A cmdlist can also set most options with the set command. \
A cmdlist option will override a command line option if both are present."
VERSION_STR = f"""{NAME} version {__version__}
Copyright (c) 2020 Lucas Jansen"""


class Config:
    def __init__(self, **configuration):
        """Construct a Config object from a dict"""

        clone = configuration.pop("clone", None)
        if clone is not None:
            configuration = dict(vars(clone), **configuration)

        self.color = configuration.pop("color", None)
        self.profile = configuration.pop("profile", False)
        self.dpi = configuration.pop("dpi", 96)
        self.is_script = configuration.pop("is_script", False)
        self.verbosity = configuration.pop(
            "verbosity", Verbosity.NORMAL if self.is_script else Verbosity.QUIET
        )
        self.showalignment = configuration.pop("showalignment", False)

        # This stores the cmdlists and commands to execute if instantiated from argv, otherwise
        # Config does not need to store that information
        self._cmdlists = []
        self._commands = []
        configuration.pop("_cmdlists", None)
        configuration.pop("_commands", None)

        for key in configuration:
            warning(self, f"ignoring unknown key '{key}' when constructing Config object")

    def _get_commands(self):
        """Gets the cmdlists parsed from argv"""

        result = {}

        if len(self._commands) > 0:
            result["-c ..."] = self._commands

        for cmdlist in self._cmdlists:
            commands = []

            with open(cmdlist) as f:
                for line in f:
                    # Strip out comments
                    line = line.split(";", 1)[0].strip()

                    if len(line) == 0:
                        continue  # Ignore empty lines

                    commands.append(line)

            if len(commands) > 0:
                result[cmdlist] = commands

            else:
                warning(self, f"ignoring empty cmdlist '{cmdlist}'")

        return result

    @classmethod
    def from_argv(cls, argv):
        """Constructs a Config object from command line arguments"""

        parser = ArgumentParser(
            prog=PROG, description=DESCRIPTION, allow_abbrev=False, add_help=False
        )

        # Add all arguments to the parser instance
        parser.add_argument(
            "-h", "--help", action="store_true", help="show this help message and exit"
        )
        parser.add_argument("--version", action="store_true", help="show version information")
        parser.add_argument("-v", "--verbose", action="store_true", help="display verbose output")
        parser.add_argument("-q", "--quiet", action="store_true", help="display only errors")
        parser.add_argument(
            "--color",
            action="store_true",
            dest="color",
            default=None,
            help="enable colored text output",
        )
        parser.add_argument(
            "--no-color",
            action="store_false",
            dest="color",
            default=None,
            help="disable colored text output",
        )
        # parser.add_argument('--profile',
        #     action='store_true', help='print profiling information')
        parser.add_argument(
            "-d",
            "--dpi",
            type=int,
            metavar="<dpi>",
            help="the DPI for the output (default: 96 [i.e. 1u = 72])",
        )
        parser.add_argument(
            "--show-alignment",
            action="store_true",
            dest="showalignment",
            help="draw rectangles to which text is aligned",
        )
        parser.add_argument(
            "-c",
            type=str,
            metavar='"<command>"',
            action="append",
            dest="commands",
            help="execute a command",
        )
        parser.add_argument(
            "cmdlist", type=str, nargs="*", metavar="<cmdlist>", help="command list file"
        )

        # Parse the args
        args = {k: v for k, v in vars(parser.parse_args(argv)).items() if v is not None}

        if args.get("help", False):

            parser.print_help(sys.stderr)
            print(file=sys.stderr)

            from .. import cmdlist

            print(cmdlist.help_msg(), file=sys.stderr)

            sys.exit(0)

        elif args.get("version", False):
            print(VERSION_STR, file=sys.stderr)

            sys.exit(0)

        self = cls(is_script=True)

        # Override default config only if set
        self._commands = args.get("commands", self._commands)
        self._cmdlists = args.get("cmdlist", self._cmdlists)

        if args.get("verbose", False):
            self.verbosity = Verbosity.VERBOSE
        elif args.get("quiet", False):
            self.verbosity = Verbosity.QUIET
        self.color = args.get("color", self.color)
        self.profile = args.get("profile", self.profile)
        self.dpi = args.get("dpi", self.dpi)
        self.showalignment = args.get("showalignment", self.showalignment)

        return self


class GlobalConfigMeta(type):
    def load_argv(cls, argv):
        cls._private = Config.from_argv(argv)

    def __getattr__(cls, attr):
        return getattr(cls._private, attr)


class config(metaclass=GlobalConfigMeta):
    _private = Config()
