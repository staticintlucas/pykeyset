# coding: utf-8

from os import path
from math import radians
from xml.etree import ElementTree as et

from .. import fonts
from ..utils.error import error, warning
from .glyph import Glyph


class Kern:

    def __init__(self):
        self.dict = {}

    def add(self, char1, char2, value):

        for c1 in char2:
            for c2 in char2:
                self.dict[f'{c1}{c2}'] = value

    def get(self, c1, c2):

        return self.dict.get(f'{c1}{c2}', 0)


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

        if not path.isfile(self.file):

            if not any(c in self.file for c in './\\'):
                filename = path.join(fonts.FONT_DIR, f'{self.file}.svg')

                if not path.isfile(filename):
                    error(ctx.conf, f"cannot load font '{self.file}'. No such font")

                else:
                    self.file = filename

            else:
                error(ctx.conf, f"cannot load font from '{path.abspath(self.file)}'. File not found")

        try:
            tree = et.parse(self.file)

        except IOError as e:
            error(ctx.conf, f"cannot load font from '{self.file}'. {e.strerror}")

        except et.ParseError as e:
            error(ctx.conf, f"cannot load font from '{self.file}'. {e.msg.capitalize()}")

        except:
            raise

        defs = tree.getroot().findall('defs')
        if len(defs) == 0:
            error(ctx.conf, f"cannot load font from '{self.file}'. No 'defs' element in SVG root")
        elif len(defs) > 1:
            warning(ctx.conf, f"multiple 'defs' elements in font '{self.file}'. "
                'Using only the last one found')
        defs = defs[-1]

        metrics = defs.findall('metrics')
        if len(metrics) == 0:
            warning(ctx.conf, f"no 'metrics' element found in 'defs' in font '{self.file}'. " \
                'Using default (probably incorrect) values')
            metrics = [et.Element('metrics')]
        elif len(metrics) > 1:
            warning(ctx.conf, f"multiple 'metrics' elements found in 'defs' in font '{self.file}'" \
                'Using only the last one found')
        metrics = metrics[-1]

        self.emsize = float(self._get_metrics_attr(ctx, metrics, 'em-size', 1000))
        self.capheight = float(self._get_metrics_attr(ctx, metrics, 'cap-height', 0.8 * self.emsize))
        self.xheight = float(self._get_metrics_attr(ctx, metrics, 'x-height', 0.5 * self.emsize))
        self.slope = radians(self._get_metrics_attr(ctx, metrics, 'slope', 0.0))
        self.lineheight = float(self._get_metrics_attr(ctx, metrics, 'line-height', self.emsize))

        default_advance = float(self._get_metrics_attr(ctx, metrics, 'horiz-adv-x', 0.6 * self.emsize))
        global_transform = metrics.get('transform', '')

        for kern in defs.findall('kern'):
            c1 = self._get_kern_attr(ctx, kern, 'c1')
            c2 = self._get_kern_attr(ctx, kern, 'c2')
            k = self._get_kern_attr(ctx, kern, 'k')

            self.kerning.add(c1, c2, k)

        glyphs = defs.findall('glyph')

        for g in glyphs:
            unicode = g.attrib.pop('unicode', None)
            if unicode is not None:
                pass

        if len(glyphs) == 0:
            warning(ctx.conf, f"no glyphs found in font '{self.file}'. No glyphs will be rendered")

        ctx.font = self




    def _get_metrics_attr(self, ctx, metrics, name, default):

        if name in metrics.attrib:
            return metrics.get(name)
        else:
            warning(ctx.conf, f"no '{name}' attribute in font metrics '{self.file}'. " \
                f'Using default value ({default})')
            return default


    def _get_kern_attr(self, ctx, kerning, name):

        if name in kerning.attrib:
            return kerning.get(name)
        else:
            error(ctx.conf, f"no '{name}' attribute in font kerning in '{self.file}'.")
