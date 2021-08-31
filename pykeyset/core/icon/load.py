import pathlib
import xml.etree.ElementTree as et

from .icon import Icon
from .icon_set import IconSet


class IconError(ValueError):
    pass


def load_builtin(name: str) -> IconSet:
    """Load a builtin set of icons by name, returning an IconSet object"""

    raise NotImplementedError


def load_file(path: pathlib.Path) -> IconSet:
    """Load icons from the given path, returning an IconSet object"""

    raise NotImplementedError


def parse_root(name: str, root: et.Element) -> IconSet:
    """Gets the common icon properties from a icon file, returning an empty IconSet object"""

    raise NotImplementedError


def parse_icon(icon: et.Element) -> Icon:
    """Parses a single icon from an ElementTree Element"""

    raise NotImplementedError


def parse_icon_set(name: str, root: et.Element) -> IconSet:
    """Parses a set of icons from an ElementTree Element"""

    raise NotImplementedError
