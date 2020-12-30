# coding: utf-8

import os.path
from enum import Enum
from numbers import Number

from ..utils.types import Rect, RoundRect
from ..utils.error import error, warning
from ..utils import tomlparser
from .. import res

from toml import TomlDecodeError
from recordclass import recordclass


ProfileType = Enum('ProfileType', ('CYLINDRICAL', 'SPHERICAL', 'FLAT'))


class Profile:

    def __init__(self):

        self.name = None

        self.type = ProfileType.CYLINDRICAL
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
        self.name = proffile

        try:
            if not os.path.isfile(self.name):

                if self.name in res.profiles:
                    file = res.profiles[self.name]

                else:
                    error(f"cannot load profile from '{os.path.abspath(self.name)}'. File not found")

                with file as f:
                    root = tomlparser.load(f)
            else:
                root = tomlparser.load(self.name)

        except IOError as e:
            error(f"cannot load profile from '{self.name}'. {e.strerror}")
        except TomlDecodeError as e:
            error(f"cannot load profile from '{self.name}'. {str(e).capitalize()}")


        try:
            proftype = root.getkey('type', type=str).upper()
            if proftype not in (t.name for t in ProfileType):
                error(f"invalid value '{proftype}' for 'type' in profile '{self.name}'")
            self.type = ProfileType[proftype]

            if self.type != ProfileType.FLAT:
                self.depth = root.getkey('depth', type=Number)
            else:
                self.depth = 0

        except KeyError as e:
            error(f"no key '{e.args[0]}' in profile '{self.name}'")
        except TypeError as e:
            error(f"invalid value for key '{e.args[0]}' in profile '{self.name}'")

        try:
            bottom = root.getsection('bottom')
            top = root.getsection('top')
            legend = root.getsection('legend')
            homing = root.getsection('homing')

        except KeyError as e:
            error(f"no section [{e.args[0]}] in profile '{self.name}'")

        try:
            w = bottom.getkey('width', type=Number) / 19.05
            h = bottom.getkey('height', type=Number) / 19.05
            r = bottom.getkey('radius', type=Number) / 19.05
            self.bottom = RoundRect(0.5 - (w / 2), 0.5 - (h / 2), w, h, r)

            w = top.getkey('width', type=Number) / 19.05
            h = top.getkey('height', type=Number) / 19.05
            r = top.getkey('radius', type=Number) / 19.05
            offset = top.getkey('y-offset', type=Number, default=0) / 19.05
            self.top = RoundRect(0.5 - (w / 2), 0.5 - (h / 2) + offset, w, h, r)

        except KeyError as e:
            error(f"no key '{e.args[0]}' in section [{e.args[1]}] in profile '{self.name}'")
        except ValueError as e:
            error(f"invalid value for key '{e.args[0]}' in section [{e.args[1]}] in profile " \
                f"'{self.name}'")

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
                                f"in profile '{self.name}'")

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
                                f"[{legend.section}] in profile '{self.name}'")

                    setattr(self, f"{rect}rect", Rect(500 - (w / 2), 500 - (h / 2) + offset, w, h))

        except ValueError as e:
            error(f"invalid value for key '{e.args[0]}' in section [{e.args[1]}] in profile " \
                f"'{self.name}'")

        try:
            if 'scoop' in homing and isinstance(homing['scoop'], tomlparser.TomlNode):
                depth = homing['scoop'].getkey('depth', type=Number)

                self.homing['scoop'] = { 'depth': depth }

            if 'bar' in homing and isinstance(homing['bar'], tomlparser.TomlNode):
                width = homing['bar'].getkey('width', type=Number, default=0)
                height = homing['bar'].getkey('height', type=Number, default=0)
                offset = homing['bar'].getkey('y-offset', type=Number, default=0)

                self.homing['bar'] = { 'width': width, 'height': height, 'offset': offset }

            if 'bump' in homing and isinstance(homing['bump'], tomlparser.TomlNode):
                radius = homing['bump'].getkey('radius', type=Number, default=0)
                offset = homing['bump'].getkey('y-offset', type=Number, default=0)

                self.homing['bump'] = { 'radius': radius, 'offset': offset }

        except KeyError as e:
            error(f"no key '{e.args[0]}' in section [{e.args[1]}] in profile '{self.name}'")
        except ValueError as e:
            error(f"invalid value for key '{e.args[0]}' in section [{e.args[1]}] in profile " \
                f"'{self.name}'")

        try:
            default = homing.getkey('default', str)

            if default not in ('scoop', 'bar', 'bump'):
                error(f"unknown default homing type '{default}' in section [{homing.section}] in " \
                    f"file '{self.name}'")
            elif default not in self.homing:
                error(f"default homing type '{default}' has no corresponding section " \
                    f"[{homing.section}.{default}] in '{self.name}'")
            else:
                self.defaulthoming = default

        except KeyError as e:
            error(f"no key '{e.args[0]}' in section [{e.args[1]}] in profile '{self.name}'")
        except ValueError as e:
            error(f"invalid value for key '{e.args[0]}' in section [{e.args[1]}] in profile " \
                f"'{self.name}'")

        ctx.profile = self
