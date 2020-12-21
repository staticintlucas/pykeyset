# coding: utf-8

from .version import get_versions
__version__ = get_versions()['version']
del get_versions

from .__main__ import main

__all__ = ['main', '__version__']
