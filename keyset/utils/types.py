# coding: utf-8

from recordclass import recordclass

Point = recordclass('Point', ('x', 'y'))
Dist = recordclass('Dist', ('x', 'y'))
Size = recordclass('Size', ('w', 'h'))

Rect = recordclass('Rect', ('x', 'y', 'w', 'h'))
RoundRect = recordclass('Rect', ('x', 'y', 'w', 'h', 'r'))
