# -*- coding: utf-8 -*-

from typing import Dict

from ...utils.types import Vector, VerticalAlign
from .icon import Icon


class IconSet:
    def __init__(self, name: str, icon_size: float):

        self.name = name
        self.icon_size = icon_size

        # Icon objects
        self._icons: Dict[str, Icon] = {}

    def __len__(self) -> int:
        """Returns the number of icons in the set"""
        return len(self._icons)

    def icon(self, name: str, icon_size: float, font_size: float, valign: VerticalAlign) -> Icon:
        """Returns a copy of the icon for the chosen name scaled to the given size, or None
        if the icon does not exist"""

        if name not in self._icons:
            return None

        icon = self._icons[name]
        path = icon.path.copy()
        path.scale(icon_size / self.icon_size)

        bbox = path.boundingbox
        offset = (bbox.height - font_size) * (1 - valign.value)
        path.translate(Vector(-bbox.x, -(bbox.y + bbox.height) + offset))

        return Icon(name=icon.name, path=path)

    def add_icon(self, icon: Icon) -> None:
        """Adds a icon to the set"""

        self._icons[icon.name] = icon
