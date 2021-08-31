from typing import Tuple

import pykeyset_rust


def version() -> Tuple[int, int, int]:
    return pykeyset_rust.version()


__version__ = "{}.{}.{}".format(*version())
