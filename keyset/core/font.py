# coding: utf-8

import os.path
from xml.etree import ElementTree as et

# from .. import fonts
from ..utils.error import error, warning
from ..utils import path
from .. import res
from .glyph import Glyph, Kern


class Font:

    def __init__(self):

        self.file = None

        # Glyph objects
        self.glyphs = []
        self.replacement = None

        # Font metrics
        self.emsize = 1000
        self.capheight = 800
        self.xheight = 500
        self.slope = 0
        self.lineheight = 1
        self.kerning = Kern()


    @classmethod
    def load(cls, ctx, fontfile):

        self = cls()
        self.file = fontfile
        self.glyphs = {}

        try:
            if not os.path.isfile(self.file):

                if self.file in res.fonts:
                    file = res.fonts[self.file]

                else:
                    error(f"cannot load font from '{os.path.abspath(self.file)}'. File not found")

                with file as f:
                    root = et.parse(f).getroot()
            else:
                root = et.parse(self.file).getroot()

        except IOError as e:
            error(f"cannot load font from '{self.file}'. {e.strerror}")
        except et.ParseError as e:
            error(f"cannot load font from '{self.file}'. {e.msg.capitalize()}")


        for a in ('em-size', 'cap-height', 'x-height'):
            if not a in root.attrib:
                error(f"no global '{a}' attribute for font '{self.file}'")

        self.emsize = float(root.get('em-size'))
        self.capheight = float(root.get('cap-height'))
        self.xheight = float(root.get('x-height'))

        if not 'slope' in root.attrib:
            warning(f"no global 'slope' attribute for font '{self.file}'. " \
                'Using default value (0)')
        self.slope = float(root.get('slope', 0))
        if not 'line-height' in root.attrib:
            warning(f"no global 'line-height' attribute for font '{self.file}'. " \
                'Using default value (equal to em-size)')
        self.lineheight = float(root.get('line-height', self.emsize))

        if not 'horiz-adv-x' in root.attrib:
            warning(f"no global 'horiz-adv-x' attribute for font '{self.file}'. " \
                'this attribute must for each individual glyph instead')
            def_advance = None
        else:
            def_advance = float(root.get('horiz-adv-x'))
        global_xform = root.get('transform', None)


        for glyph in root.findall('glyph'):
            for a in ('char', 'path'):
                if not a in glyph.attrib:
                    warning(f"no '{a}' attribute for 'glyph' in '{self.file}'. Ignoring " \
                        'this glyph')
                    continue

            char = glyph.get('char')
            gp = path.Path(glyph.get('path'))

            if 'transform' in glyph.attrib:
                gp.transform(glyph.get('transform'))

            if global_xform is not None:
                gp.transform(global_xform)

            if 'horiz-adv-x' in glyph.attrib:
                advance = glyph.get('horiz-adv-x')
            elif def_advance is not None:
                advance = def_advance
            else:
                warning(f"no 'horiz-adv-x' attribute for 'glyph' and not default value " \
                    f"set in '{self.file}'. Ignoring this glyph")
                continue

            self.glyphs[char] = Glyph(gp, advance)

        if len(self.glyphs) == 0:
            error(f"no valid glyphs found in font '{self.file}'")

        for kern in root.findall('kern'):
            for a in ('u', 'k'):
                if not a in kern.attrib:
                    warning(f"no '{a}' attribute for 'kern' in '{self.file}'. Ignoring " \
                        'this kerning value')
                    continue

            u = kern.get('u')
            if len(u) != 2:
                warning(f"invalid 'u' attribute for 'kern' in '{self.file}'. Ignoring " \
                    'this kerning value')
                continue

            try:
                k = float(kern.get('k'))
            except ValueError:
                warning(f"invalid 'k' attribute for 'kern' in '{self.file}'. Ignoring " \
                    'this kerning value')
                continue

            self.kerning.add(u[0], u[1], k)

        ctx.font = self
