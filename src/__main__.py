#!/usr/bin/env python3
# coding: utf-8

import sys
import traceback
from time import perf_counter

from . import Config
from .utils.error import error, warning, done, KeysetError
from . import cmdlist


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
        conf = Config.from_argv(args)
        result = main(conf)

    # Raised by argparse to exit after printing --help and --version; reraise to exit as expected
    except SystemExit:
        raise

    # If the user interrupts the program
    except KeyboardInterrupt:
        # Print a new line after patrial output and the ^C so we don't get the prompt on the same
        # line because it's kinda ugly
        print()

    # If a fatal error occurs and the program needs to exit. The error will already have been
    # printed when it is raised, so we can just ignore it here
    except KeysetError:
        result = 1

    # Any other exception is an internal error so we print the full traceback
    except:
        # Create a default conf if the error occurred before/as the real conf is created
        if conf is None:
            conf = Config(is_script=True)
        trace = traceback.format_exc()
        error(conf, 'Internal error:\n{:s}'.format(trace), file=sys.stderr, no_raise=True)

    else:
        end = perf_counter()
        done(conf, f'Completed in {end - start:.3f} s')

    sys.exit(result)


def main(conf):
    """The entrypoint for the script. Accepts command line args as a list of strings. Returns 0
    for success and a non-zero value on failure"""

    cmdlists = conf._get_commands()

    if len(cmdlists) == 0:
        warning(conf, 'no commands to execute')

    for name, cmds in cmdlists.items():
        cmdlist.execute(conf, name, cmds)

    return 0


# For compatibility to let this run as a standalone script
if __name__ == '__main__':
    _start()
