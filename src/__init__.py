# coding: utf-8

from . import version
__version__ = version.get_versions()['version']

from .utils.config import Config
