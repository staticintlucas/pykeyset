# -*- coding: utf-8 -*-

import os.path
from xml.etree import ElementTree as et
from collections import namedtuple

# from .. import fonts
from ..utils.error import error, warning
from ..utils.types import Dist
from ..utils import path
from .. import res


Icon = namedtuple("Icon", ("name", "path", "width", "height"))


class Icons:
    def __init__(self):

        self.file = None

        # Glyph objects
        self.icons = {}

        # Size of a 1u key
        self.unitsize = 1000

    @classmethod
    def load(cls, ctx, iconfile):

        self = cls()
        self.file = iconfile

        try:
            if not os.path.isfile(self.file):

                if self.file in res.icons:
                    file = res.icons[self.file]

                else:
                    error(f"cannot load icons from '{os.path.abspath(self.file)}'. File not found")

                with file as f:
                    root = et.parse(f).getroot()
            else:
                root = et.parse(self.file).getroot()

        except IOError as e:
            error(f"cannot load icons from '{self.file}'. {e.strerror}")
        except et.ParseError as e:
            error(f"cannot load icons from '{self.file}'. {e.msg.capitalize()}")

        if "key-size" not in root.attrib:
            error(f"no global 'key-size' attribute for icons '{self.file}'")

        self.unitsize = float(root.get("key-size"))
        global_xform = root.get("transform", None)

        for icon in root.findall("icon"):
            for a in ("name", "path"):
                if a not in icon.attrib:
                    warning(f"no '{a}' attribute for 'icon' in '{self.file}'. Ignoring this icon")
                    continue

            name = icon.get("name")
            gp = path.Path(icon.get("path"))

            if "transform" in icon.attrib:
                gp.transform(icon.get("transform"))

            if global_xform is not None:
                gp.transform(global_xform)

            width = float(icon.get("width", 0))
            height = float(icon.get("height", 0))

            self.icons[name] = Icon(name, gp, width, height)

        if len(self.icons) == 0:
            error(f"no valid icons found in '{self.file}'")

        ctx.icons.append(self)

    def geticon(self, ctx, name, size, valign):

        scale = 1 / self.unitsize

        if name not in self.icons:
            return None, 0

        icon = self.icons[name]
        path = icon.path.copy()

        path.scale(Dist(scale, scale))
        width, height = icon.width / self.unitsize, icon.height / self.unitsize

        path.translate(Dist(0, (height - size) * (1 - valign / 2) - height))

        return path, width
