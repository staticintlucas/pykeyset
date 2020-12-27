# coding: utf-8

# TODO why can't pylint find this?
from recordclass import recordclass # pylint: disable=import-error

Point = recordclass('Point', ('x', 'y'))
Dist = recordclass('Dist', ('x', 'y'))
Size = recordclass('Size', ('w', 'h'))

Rect = recordclass('Rect', ('x', 'y', 'w', 'h'))
RoundRect = recordclass('Rect', ('x', 'y', 'w', 'h', 'r'))
