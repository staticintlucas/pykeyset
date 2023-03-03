from typing import Optional

from ...utils.types import VerticalAlign
from .icon import Icon


class IconSet:
    def __init__(self, name: str, icon_size: float):
        raise NotImplementedError

    def __len__(self) -> int:
        """Returns the number of icons in the set"""

        raise NotImplementedError

    def icon(
        self, name: str, icon_size: float, font_size: float, valign: VerticalAlign
    ) -> Optional[Icon]:
        """Returns a copy of the icon for the chosen name scaled to the given size, or None
        if the icon does not exist"""

        raise NotImplementedError

    def add_icon(self, icon: Icon) -> None:
        """Adds a icon to the set"""

        raise NotImplementedError
