from xml.etree import ElementTree as et

from ...utils.types import Color, Rect, RoundRect, Vector
from ..kle import Key, KeyType
from .types import GradientType, HomingProperties, ProfileType, TextTypeProperty


class Profile:
    def __init__(
        self,
        name: str,
        type: ProfileType,
        depth: float,
        bottom_rect: RoundRect,
        top_rect: RoundRect,
        text_rect: TextTypeProperty[Rect],
        text_size: TextTypeProperty[float],
        homing: HomingProperties,
    ):
        raise NotImplementedError

    def key(self, key: Key, g: et.Element) -> None:
        raise NotImplementedError

    def legend_rect(self, key: Key, size: int) -> Rect:
        raise NotImplementedError

    def legend_size(self, size: int) -> float:
        raise NotImplementedError

    def draw_key_bottom(self, g: et.Element, size: Vector, color: Color) -> None:
        raise NotImplementedError

    def draw_key_top(self, g: et.Element, keytype: KeyType, size: Vector, color: Color) -> None:
        raise NotImplementedError

    def draw_iso_bottom(self, g: et.Element, color: Color) -> None:
        raise NotImplementedError

    def draw_iso_top(self, g: et.Element, color: Color) -> None:
        raise NotImplementedError

    def draw_step(self, g: et.Element, color: Color) -> None:
        raise NotImplementedError

    def add_gradient(self, gradtype: GradientType, color: Color, depth: float) -> str:
        raise NotImplementedError
