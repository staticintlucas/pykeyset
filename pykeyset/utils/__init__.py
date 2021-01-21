# -*- coding: utf-8 -*-

from enum_tools import OrderedEnum


class Verbosity(OrderedEnum):
    NONE = 0
    QUIET = 1
    NORMAL = 2
    VERBOSE = 3
    DEBUG = 4


class Severity(OrderedEnum):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
