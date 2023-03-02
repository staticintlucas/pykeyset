from enum import IntEnum


class Verbosity(IntEnum):
    NONE = 0
    QUIET = 1
    NORMAL = 2
    VERBOSE = 3
    DEBUG = 4


class Severity(IntEnum):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
