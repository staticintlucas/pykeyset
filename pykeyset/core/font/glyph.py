# -*- coding: utf-8 -*-

from typing import NamedTuple

from ...utils.path import Path


class Glyph(NamedTuple):
    name: str
    path: Path
    advance: float
