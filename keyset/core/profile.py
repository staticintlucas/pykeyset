# coding: utf-8

import os.path
from enum import Enum
from numbers import Number

from ..utils.types import Rect, RoundRect
from ..utils.error import error, warning
from ..utils import tomlparser
from .. import res

from toml import TomlDecodeError
# TODO why can't pylint find this?
from recordclass import recordclass # pylint: disable=import-error


ProfileType = Enum('ProfileType', ('CYLINDRICAL', 'SPHERICAL', 'FLAT'))
HomingProps = recordclass('HomingProps', ('depth', 'width', 'height','radius','offset'))


class Profile:

    def __init__(self):

        self.file = None

        # Glyph objects
        self.depth = 0
        self.bottom = RoundRect(0, 0, 0, 0, 0)
        self.top = RoundRect(0, 0, 0, 0, 0)
        self.alpharect = Rect(0, 0, 0, 0)
        self.symbolrect = Rect(0, 0, 0, 0)
        self.modrect = Rect(0, 0, 0, 0)
        self.defaulthoming = None
        self.homing = {}


    @classmethod
    def load(cls, ctx, proffile):

        self = cls()
        self.file = proffile

        try:
            if not os.path.isfile(self.file):

                if self.file in res.profiles:
                    file = res.profiles[self.file]

                else:
                    error(f"cannot load profile from '{os.path.abspath(self.file)}'. File not found")

                with file as f:
                    root = tomlparser.load(f)
            else:
                root = tomlparser.load(self.file)

        except IOError as e:
            error(f"cannot load profile from '{self.file}'. {e.strerror}")
        except TomlDecodeError as e:
            error(f"cannot load profile from '{self.file}'. {str(e).capitalize()}")


        try:
            proftype = root.getkey('type', type=str).upper()
            if proftype not in (t.name for t in ProfileType):
                error(f"invalid value '{proftype}' for 'type' in profile '{self.file}'")
            self.type = ProfileType[proftype]

            if self.type != ProfileType.FLAT:
                self.depth = root.getkey('depth', type=Number)
            else:
                self.depth = 0

        except KeyError as e:
            error(f"no key '{e.args[0]}' in profile '{self.file}'")
        except TypeError as e:
            error(f"invalid value for key '{e.args[0]}' in profile '{self.file}'")

        try:
            bottom = root.getsection('bottom')
            top = root.getsection('top')
            legend = root.getsection('legend')
            homing = root.getsection('homing')

        except KeyError as e:
            error(f"no section [{e.args[0]}] in profile '{self.file}'")

        try:
            w = bottom.getkey('width', type=Number) * 1000 / 19.05
            h = bottom.getkey('height', type=Number) * 1000 / 19.05
            r = bottom.getkey('radius', type=Number) * 1000 / 19.05
            self.bottom = RoundRect(500 - (w / 2), 500 - (h / 2), w, h, r)

            w = top.getkey('width', type=Number) * 1000 / 19.05
            h = top.getkey('height', type=Number) * 1000 / 19.05
            r = top.getkey('radius', type=Number) * 1000 / 19.05
            offset = top.getkey('y-offset', type=Number, default=0) * 1000 / 19.05
            self.top = RoundRect(500 - (w / 2), 500 - (h / 2) + offset, w, h, r)

        except KeyError as e:
            error(f"no key '{e.args[0]}' in section [{e.args[1]}] in profile '{self.file}'")
        except ValueError as e:
            error(f"invalid value for key '{e.args[0]}' in section [{e.args[1]}] in profile " \
                f"'{self.file}'")

        try:
            default_w = legend.getkey('width', type=Number, default=None)
            default_h = legend.getkey('height', type=Number, default=None)
            default_offset = legend.getkey('y-offset', type=Number, default=0)

            for rect in ('alpha', 'symbol', 'mod'):
                try:
                    section = legend.getsection(rect)

                except KeyError as e:
                    for key, value in { 'width': default_w, 'height': default_h }.items():
                        if value is None:
                            error(f"no section [{e.args[0]}] and no key '{key}' in [{e.args[1]}] " \
                                f"in profile '{self.file}'")

                    w = default_w
                    h = default_h
                    offset = default_offset

                else:
                    w = section.getkey('width', Number, default_w)
                    h = section.getkey('height', Number, default_h)
                    offset = section.getkey('y-offset', Number, default_offset)

                    for key, value in { 'width': w, 'height': h }.items():
                        if value is None:
                            error(f"no key '{key}' in section [{section.section}] or in section " \
                                f"[{legend.section}] in profile '{self.file}'")

                    setattr(self, f"{rect}rect", Rect(500 - (w / 2), 500 - (h / 2) + offset, w, h))

        except ValueError as e:
            error(f"invalid value for key '{e.args[0]}' in section [{e.args[1]}] in profile " \
                f"'{self.file}'")

        for key, value in homing.items():
            if not isinstance(value, tomlparser.TomlNode):
                continue

            try:
                depth = legend.getkey('depth', type=Number, default=0)
                width = legend.getkey('width', type=Number, default=0)
                height = legend.getkey('height', type=Number, default=0)
                radius = legend.getkey('radius', type=Number, default=0)
                offset = legend.getkey('y-offset', type=Number, default=0)

                self.homing[key] = HomingProps(depth, width, height, radius, offset)

            except ValueError as e:
                error(f"invalid value for key '{e.args[0]}' in section [{e.args[1]}] in profile " \
                    f"'{self.file}'")

        try:
            default = homing.getkey('default', str)

            if default in self.homing:
                self.defaulthoming = default
            else:
                error(f"default homing type '{default}' has no corresponding section " \
                    f"[{homing.section}.{default}] in '{self.file}'")

        except KeyError as e:
            error(f"no key '{e.args[0]}' in section [{e.args[1]}] in profile '{self.file}'")
        except ValueError as e:
            error(f"invalid value for key '{e.args[0]}' in section [{e.args[1]}] in profile " \
                f"'{self.file}'")

        ctx.profile = self
