#!/usr/bin/env python3
# coding: utf-8

import sys
import traceback
from time import perf_counter

from .utils import Config, error, warning, done
from . import commands


def _start():
    """Wraps the main function in a try/except block to pretty print any exceptions that
    propagate"""

    # Default return code if an error occurs
    result = 1
    conf = None
    start = perf_counter()

    try:
        args = sys.argv[1:]
        if len(args) == 0:
            args = ['--help']
        conf = Config(args)
        result = main(conf)

    # Raised by argparse to exit after printing --help and --version; reraise to exit as expected
    except SystemExit:
        raise

    # If the user interrupts the program
    except KeyboardInterrupt:
        # Print a new line after patrial output and the ^C so we don't get the prompt on the same
        # line because it's kinda ugly
        print()

    # Any other exception is an internal error so we print the full traceback
    except:
        # Pass in a dummy conf in case the error occurred before the conf is created
        if conf is None:
            conf = lambda: None
            conf.color = None
        error(conf, 'Internal error:\n{:s}'.format(traceback.format_exc()), file=sys.stderr)

    else:
        end = perf_counter()
        done(conf, f'Completed in {end - start:.3f} s')

    sys.exit(result)


def main(conf):
    """The entrypoint for the script. Accepts command line args as a list of strings. Returns 0
    for success and a non-zero value on failure"""

    if len(conf.commands) == 0:
        warning(conf, 'no commands to execute')

    for cmd in conf.commands:
        commands.execute(conf, cmd)

    return 0


# For compatibility to let this run as a standalone script
if __name__ == '__main__':
    _start()
