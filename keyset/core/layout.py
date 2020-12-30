# coding: utf-8

from enum import Enum
from xml.etree import ElementTree as et

from ..utils.types import Point, Dist, Size, Color
from ..utils.error import error, warning
from ..utils.path import Path
from ..utils import config
from .profile import ProfileType
from .kle import KeyType



GradientType = Enum('GradientType', ('KEY', 'SCOOP', 'SPACE'))


UNIT = 1000 # 1u = 1000 svg units
DPK = 0.75 * config.config.dpi # dpk = dots per key = 0.75 * dpi


class Layout:

    def __init__(self):

        self.root = et.Element('svg')

        # Keep track of which keytop gradients have already been generated
        self.gradients = []

    @classmethod
    def layout(cls, ctx):

        if ctx.kle is None:
            error(f"no KLE layout is loaded")
        elif ctx.font is None:
            error(f"no font is loaded")
        elif ctx.profile is None:
            error(f"no profile is loaded")

        self = cls()

        self.root.attrib.update({
            'width': _format(ctx.kle.size.w * DPK), # 1u = 0.75in
            'height': _format(ctx.kle.size.h * DPK),
            'viewBox': f'0 0 {_format(ctx.kle.size.w * UNIT)} {_format(ctx.kle.size.h * UNIT)}',
            'xmlns': 'http://www.w3.org/2000/svg',
            'stroke-linecap': 'round',
            'stroke-linejoin': 'round',
        })

        for key in ctx.kle.keys:
            x = _format(key.pos.x * UNIT)
            y = _format(key.pos.y * UNIT)
            g = et.SubElement(self.root, 'g', {
                'transform': f'translate({x},{y})'
            })

            if key.type == KeyType.DEFHOME:
                if ctx.profile.defaulthoming == 'scoop':
                    key.type = KeyType.SCOOP
                elif ctx.profile.defaulthoming == 'bump':
                    key.type = KeyType.BUMP
                else:
                    key.type = KeyType.BAR

            self.drawkey(ctx, key, g)


    def drawkey(self, ctx, key, g):

        if key.type == KeyType.NONE:
            pass # do nothing

        elif key.size == 'iso':
            self.drawisobottom(ctx, g, key.bgcol)
            self.drawisotop(ctx, g, key.bgcol)

        elif key.size == 'step':
            self.drawkeybottom(ctx, g, Size(1.75, 1), key.bgcol)
            self.drawkeytop(ctx, g, key.type, Size(1.25, 1), key.bgcol)

        else:
            self.drawkeybottom(ctx, g, key.size, key.bgcol)
            self.drawkeytop(ctx, g, key.type,key.size, key.bgcol)

    def drawkeybottom(self, ctx, g, size, color):
        rect = ctx.profile.bottom
        et.SubElement(g, 'rect', {
            'fill': color,
            'stroke': color.highlight(),
            'stroke-width': '10',
            'x': _format(rect.x * UNIT),
            'y': _format(rect.y * UNIT),
            'width': _format((rect.w + size.w - 1) * UNIT),
            'height': _format((rect.h + size.h - 1) * UNIT),
            'rx': _format(rect.r * UNIT),
            'ry': _format(rect.r * UNIT),
        })

    def drawkeytop(self, ctx, g, keytype, size, color):

        rect = ctx.profile.top

        w = rect.w + size.w - 1 - 2 * rect.r
        h = rect.h + size.h - 1 - 2 * rect.r

        if keytype == KeyType.SCOOP:
            try:
                depth = ctx.profile.homing['scoop']['depth']
            except KeyError:
                error(f"no scooped homing keys for profile '{ctx.profile.name}'")
        else:
            depth = ctx.profile.depth

        if ctx.profile.type == ProfileType.FLAT:
            et.SubElement(g, 'rect', {
                'fill': color,
                'stroke': color.highlight(),
                'stroke-width': '10',
                'x': _format(rect.x * UNIT),
                'y': _format(rect.y * UNIT),
                'width': _format((rect.w + size.w - 1) * UNIT),
                'height': _format((rect.h + size.h - 1) * UNIT),
                'rx': _format(rect.r * UNIT),
                'ry': _format(rect.r * UNIT),
            })

        else:

            curve = depth / 100
            gradtype = GradientType.SCOOP if keytype == KeyType.SCOOP else GradientType.KEY

            # Calculate the radius of the arc for horizontal and vertical (for spherical) curved keytop
            # edges using standard formula for segments of an arc using w/h as the widths and curve as
            # the height
            hr = (curve**2 + (w ** 2 / 4)) / (2 * curve)
            vr = (curve**2 + (h ** 2 / 4)) / (2 * curve)

            if keytype == KeyType.SPACE:
                path = (Path()
                    .M(Point(rect.x, rect.y + rect.r))
                    .a(Size(rect.r, rect.r), 0, False, True, Dist(rect.r, -rect.r))
                    .h(w)
                    .a(Size(rect.r, rect.r), 0, False, True, Dist(rect.r, rect.r))
                    .a(Size(vr, vr), 0, False, False, Dist(0, h))
                    .a(Size(rect.r, rect.r), 0, False, True, Dist(-rect.r, rect.r))
                    .h(-w)
                    .a(Size(rect.r, rect.r), 0, False, True, Dist(-rect.r, -rect.r))
                    .a(Size(vr, vr), 0, False, False, Dist(0, -h))
                    .z()
                    .scale(Dist(UNIT, UNIT)))
                gradtype = GradientType.SPACE

            elif ctx.profile.type == ProfileType.CYLINDRICAL:
                path = (Path()
                    .M(Point(rect.x, rect.y + rect.r))
                    .a(Size(rect.r, rect.r), 0, False, True, Dist(rect.r, -rect.r))
                    .h(w)
                    .a(Size(rect.r, rect.r), 0, False, True, Dist(rect.r, rect.r))
                    .v(h)
                    .a(Size(rect.r, rect.r), 0, False, True, Dist(-rect.r, rect.r))
                    .a(Size(hr, hr), 0, False, True, Dist(-w, 0))
                    .a(Size(rect.r, rect.r), 0, False, True, Dist(-rect.r, -rect.r))
                    .z()
                    .scale(Dist(UNIT, UNIT)))

            else: # ProfileType.SPHERICAL
                path = (Path()
                    .M(Point(rect.x, rect.y + rect.r))
                    .a(Size(rect.r, rect.r), 0, False, True, Dist(rect.r, -rect.r))
                    .a(Size(hr, hr), 0, False, True, Dist(w, 0))
                    .a(Size(rect.r, rect.r), 0, False, True, Dist(rect.r, rect.r))
                    .a(Size(vr, vr), 0, False, True, Dist(0, h))
                    .a(Size(rect.r, rect.r), 0, False, True, Dist(-rect.r, rect.r))
                    .a(Size(hr, hr), 0, False, True, Dist(-w, 0))
                    .a(Size(rect.r, rect.r), 0, False, True, Dist(-rect.r, -rect.r))
                    .a(Size(vr, vr), 0, False, True, Dist(0, -h))
                    .z()
                    .scale(Dist(UNIT, UNIT)))

            et.SubElement(g, 'path', {
                'fill': self.addgradient(ctx, gradtype, color, depth),
                'stroke': color.highlight(),
                'stroke-width': '10',
                'd': str(path),
            })

    def drawisobottom(self, ctx, g, color):
        rect = ctx.profile.bottom
        et.SubElement(g, 'path', {
            'fill': color,
            'stroke': color.highlight(),
            'stroke-width': '10',
            'd': str(Path()
                .M(Point(rect.x, rect.y + rect.r))
                .a(Size(rect.r, rect.r), 0, False, True, Dist(rect.r, -rect.r))
                .h(0.5 + rect.w - 2 * rect.r)
                .a(Size(rect.r, rect.r), 0, False, True, Dist(rect.r, rect.r))
                .v(1 + rect.h - 2 * rect.r)
                .a(Size(rect.r, rect.r), 0, False, True, Dist(-rect.r, rect.r))
                .h(-(0.25 + rect.w - 2 * rect.r))
                .a(Size(rect.r, rect.r), 0, False, True, Dist(-rect.r, -rect.r))
                .v(-(1 - 2 * rect.r))
                .a(Size(rect.r, rect.r), 0, False, False, Dist(-rect.r, -rect.r))
                .h(-(0.25 - 2 * rect.r))
                .a(Size(rect.r, rect.r), 0, False, True, Dist(-rect.r, -rect.r))
                .v(-(rect.h - 2 * rect.r))
                .z()
                .scale(Dist(UNIT, UNIT))),
        })

    def drawisotop(self, ctx, g, color):
        rect = ctx.profile.top
        curve = ctx.profile.depth / 100

        w_top = rect.w + 1.5 - 1 - 2 * rect.r
        w_btm = rect.w + 1.25 - 1 - 2 * rect.r
        h_lefttop = rect.h - 2 * rect.r
        h_leftbtm = 1 - curve / 3 - 2 * rect.r
        h_right = rect.h + 2 - 1 - 2 * rect.r

        if ctx.profile.type == ProfileType.FLAT:
            path = (Path()
                .M(Point(rect.x, rect.y + rect.r))
                .a(Size(rect.r, rect.r), 0, False, True, Dist(rect.r, -rect.r))
                .h(w_top)
                .a(Size(rect.r, rect.r), 0, False, True, Dist(rect.r, rect.r))
                .v(h_right)
                .a(Size(rect.r, rect.r), 0, False, True, Dist(-rect.r, rect.r))
                .h(-w_btm)
                .a(Size(rect.r, rect.r), 0, False, True, Dist(-rect.r, -rect.r))
                .v(-(1 - 2 * rect.r))
                .a(Size(rect.r, rect.r), 0, False, False, Dist(-rect.r, -rect.r))
                .h(-(0.25 - 2 * rect.r))
                .a(Size(rect.r, rect.r), 0, False, True, Dist(-rect.r, -rect.r))
                .v(-h_lefttop)
                .z()
                .scale(Dist(UNIT, UNIT)))

        else:

            # Calculate the radius of the arc for horizontal and vertical (for spherical) curved keytop
            # edges using standard formula for segments of an arc using w/h as the widths and curve as
            # the height
            top_r, btm_r, lefttop_r, leftbtm_r, right_r = \
                ((curve**2 + (d ** 2 / 4)) / (2 * curve) for d in (w_top, w_btm, h_lefttop, h_leftbtm, h_right))

            if ctx.profile.type == ProfileType.CYLINDRICAL:
                path = (Path()
                    .M(Point(rect.x, rect.y + rect.r))
                    .a(Size(rect.r, rect.r), 0, False, True, Dist(rect.r, -rect.r))
                    .h(w_top)
                    .a(Size(rect.r, rect.r), 0, False, True, Dist(rect.r, rect.r))
                    .v(h_right)
                    .a(Size(rect.r, rect.r), 0, False, True, Dist(-rect.r, rect.r))
                    .a(Size(btm_r, btm_r), 0, False, True, Dist(-w_btm, 0))
                    .a(Size(rect.r, rect.r), 0, False, True, Dist(-rect.r, -rect.r))
                    .v(-(h_leftbtm))
                    .a(Size(rect.r, rect.r), 0, False, False, Dist(-rect.r, -rect.r))
                    .l(Dist(-(0.25 - 2 * rect.r), -curve / 3))
                    .a(Size(rect.r, rect.r), 0, False, True, Dist(-rect.r, -rect.r))
                    .v(-(h_lefttop))
                    .z()
                    .scale(Dist(UNIT, UNIT)))

            else: # ProfileType.SPHERICAL
                path = (Path()
                    .M(Point(rect.x, rect.y + rect.r))
                    .a(Size(rect.r, rect.r), 0, False, True, Dist(rect.r, -rect.r))
                    .a(Size(top_r, top_r), 0, False, True, Dist(w_top, 0))
                    .a(Size(rect.r, rect.r), 0, False, True, Dist(rect.r, rect.r))
                    .a(Size(right_r, right_r), 0, False, True, Dist(0, h_right))
                    .a(Size(rect.r, rect.r), 0, False, True, Dist(-rect.r, rect.r))
                    .a(Size(btm_r, btm_r), 0, False, True, Dist(-w_btm, 0))
                    .a(Size(rect.r, rect.r), 0, False, True, Dist(-rect.r, -rect.r))
                    .a(Size(leftbtm_r, leftbtm_r), 0, False, True, Dist(0, -h_leftbtm))
                    .a(Size(rect.r, rect.r), 0, False, False, Dist(-rect.r, -rect.r))
                    .l(Dist(-(0.25 - 2 * rect.r), -curve / 3))
                    .a(Size(rect.r, rect.r), 0, False, True, Dist(-rect.r, -rect.r))
                    .a(Size(lefttop_r, lefttop_r), 0, False, True, Dist(0, -h_lefttop))
                    .z()
                    .scale(Dist(UNIT, UNIT)))

        et.SubElement(g, 'path', {
            'fill': self.addgradient(ctx, GradientType.KEY, color, ctx.profile.depth),
            'stroke': color.highlight(),
            'stroke-width': '10',
            'd': str(path),
        })


    def addgradient(self, ctx, gradtype, color, depth):

        if ctx.profile.type == ProfileType.FLAT:
            # Flat has not gradients so we just return the flat colour
            return f"{color}"

        defs = self.root.find('defs')
        if defs is None:
            defs = et.Element('defs')
            self.root.insert(0, defs)

        else:
            id = f"{gradtype.name.lower()}-{str(color).lstrip('#')}"
            url = f"url(#{id})"

        if id not in self.gradients:

            if gradtype in (GradientType.KEY, GradientType.SCOOP):

                if ctx.profile.type == ProfileType.CYLINDRICAL:
                    gradient = et.SubElement(defs, 'linearGradient', {
                        'id': id,
                        'x1': '100%',
                        'y1': '0%',
                        'x2': '0%',
                        'y2': '0%',
                    })
                else: # if ProfileType.SPHERICAL
                    gradient = et.SubElement(defs, 'radialGradient', {
                        'id': id,
                        'cx': '100%',
                        'cy': '100%',
                        'fx': '100%',
                        'fy': '100%',
                        'fr': '0%',
                        'r': '141%',
                        'spreadMethod': 'repeat',
                    })
            else: # if GradientType.SPACE
                gradient = et.SubElement(defs, 'linearGradient', {
                    'id': id,
                    'x1': '0%',
                    'y1': '0%',
                    'x2': '0%',
                    'y2': '100%',
                })

            stopcolors = [color.lighter(min(1, depth / 10)), color, color.darker(min(1, depth / 10))]
            stopdists = [0, 50, 100]

            for col, dist in zip(stopcolors, stopdists):
                et.SubElement(gradient, 'stop', {
                    'offset': f'{_format(dist)}%',
                    'stop-color': f'{col}',
                })

            self.gradients.append(id)

        return url


# Format a number as efficiently as possible
def _format(num):
    return f'{float(num):.3f}'.rstrip('0').rstrip('.')
