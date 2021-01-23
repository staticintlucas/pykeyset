# -*- coding: utf-8 -*-

import os.path
from collections import namedtuple
from xml.etree import ElementTree as et

from .. import resources
from ..utils import path
from ..utils.logging import error, format_filename, warning
from ..utils.types import Rect, Vector

Icon = namedtuple("Icon", ("name", "path"))


class Icons:
    def __init__(self):

        self.file = None

        # Glyph objects
        self.icons = {}

        # Size of a 1u key
        self.unitsize = 1000

    @classmethod
    def load(cls, ctx, file):
        """load built in icons or an XML icon/novelty file"""

        self = cls()
        self.file = file

        try:
            if not os.path.isfile(self.file) and self.file in resources.icons:
                file = resources.icons[self.file]

                with file as f:
                    root = et.parse(f).getroot()
            else:
                root = et.parse(self.file).getroot()

        except IOError as e:
            error(
                ValueError(
                    f"cannot load icons from {format_filename(self.file)}: {e.strerror.lower()}"
                )
            )
        except et.ParseError as e:
            error(
                ValueError(f"cannot load icons from {format_filename(self.file)}: {e.msg.lower()}")
            )

        if "key-size" not in root.attrib:
            error(ValueError("no global 'key-size' attribute for icon file"), file=self.file)

        self.unitsize = float(root.get("key-size"))
        global_xform = root.get("transform", None)

        for icon in root.findall("icon"):

            skip = False
            for a in ("name", "path"):
                if a not in icon.attrib:
                    warning(
                        ValueError(f"no '{a}' attribute for 'icon' element."),
                        "Skipping this icon",
                        file=self.file,
                    )
                    skip = True
            if skip:
                continue

            name = icon.get("name")
            gp = path.Path(icon.get("path"))

            if "transform" in icon.attrib:
                gp.transform(icon.get("transform"))

            if global_xform is not None:
                gp.transform(global_xform)

            if "bbox" in icon.attrib:
                try:
                    x, y, w, h = (float(i) for i in icon.attrib["bbox"].split(" "))
                except ValueError:
                    warning(
                        ValueError(
                            f"invalid 'bbox' attribute for 'icon' element with name='{name}'"
                        ),
                        "Skipping this icon",
                        file=self.file,
                    )
                    continue
                gp.setboundingbox(Rect(x, y, w, h))

            self.icons[name] = Icon(name, gp)

        if len(self.icons) == 0:
            error(ValueError("no valid icons found in file"), file=self.file)

        ctx.icons.append(self)

    def geticon(self, ctx, name, size, valign):

        scale = 1 / self.unitsize

        if name not in self.icons:
            return None, 0

        icon = self.icons[name]
        path = icon.path.copy()

        path.scale(Vector(scale, scale))
        bbox = path.boundingbox

        path.translate(Vector(-bbox.x, -bbox.y - size))
        path.translate(Vector(0, (size - bbox.h) * (valign / 2)))

        return path, bbox.w
