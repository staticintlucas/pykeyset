#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import traceback
from time import perf_counter
import cProfile
import pstats

from .utils.config import config
from .utils.error import error, warning, done, KeysetError
from . import cmdlist


def _start():
    """Wraps the main function in a try/except block to pretty print any exceptions that
    propagate"""

    # Default return code if an error occurs
    result = 1
    start = perf_counter()

    try:
        args = sys.argv[1:]
        if len(args) == 0:
            args = ["--help"]
        config.load_argv(args)

        if config.profile:
            # Profile the execution of the main function
            with cProfile.Profile() as p:
                result = main()

            # Write out statistics
            with open("pykeyset_profile.txt", "w") as f:
                stats = pstats.Stats(p, stream=f)
                stats.strip_dirs().sort_stats("tottime").print_stats()

        else:
            result = main()

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
        pass

    # Any other exception is an internal error so we print the full traceback
    except Exception:
        trace = traceback.format_exc()
        error("Internal error:\n{:s}".format(trace), no_raise=True, wrap=False)

    else:
        end = perf_counter()
        done(f"Completed in {end - start:.3f} s")

    sys.exit(result)


def main():
    """The entrypoint for the script. Accepts command line args as a list of strings. Returns 0
    for success and a non-zero value on failure"""

    cmdlists = config._private._get_commands()

    if len(cmdlists) == 0:
        warning("no commands to execute")

    for name, cmds in cmdlists.items():
        cmdlist.execute(name, cmds)

    return 0


# For compatibility to let this run as a standalone script
if __name__ == "__main__":
    _start()
