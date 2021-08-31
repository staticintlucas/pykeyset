from enum import Enum

from recordclass import recordclass

Key = recordclass("Key", ("pos", "size", "type", "legend", "legsize", "bgcol", "fgcol"))
KeyType = Enum("KeyType", ["NONE", "NORM", "DEFHOME", "SCOOP", "BAR", "BUMP", "SPACE"])


KLE_TO_ORD_MAP = (
    (0, 6, 2, 8, 9, 11, 3, 5, 1, 4, 7, 10),  # 0 = no centering
    (1, 7, 0, 2, 9, 11, 4, 3, 5, 6, 8, 10),  # 1 = center x
    (3, 0, 5, 1, 9, 11, 2, 6, 4, 7, 8, 10),  # 2 = center y
    (4, 0, 1, 2, 9, 11, 3, 5, 6, 7, 8, 10),  # 3 = center x & y
    (0, 6, 2, 8, 10, 9, 3, 5, 1, 4, 7, 11),  # 4 = center front (default)
    (1, 7, 0, 2, 10, 3, 4, 5, 6, 8, 9, 11),  # 5 = center front & x
    (3, 0, 5, 1, 10, 2, 6, 7, 4, 8, 9, 11),  # 6 = center front & y
    (4, 0, 1, 2, 10, 3, 5, 6, 7, 8, 9, 11),  # 7 = center front & x & y
)


def kle_to_ord(legends, index):
    legends = legends[:] + [""] * max(0, len(KLE_TO_ORD_MAP[index]) - len(legends))
    return [l for _, l in sorted(zip(KLE_TO_ORD_MAP[index], legends))]


class KleFile:
    def __init__(self):

        raise NotImplementedError

    @staticmethod
    def _load_url(ctx, url):

        raise NotImplementedError

    @staticmethod
    def _load_file(ctx, path):

        raise NotImplementedError

    @classmethod
    def load(cls, ctx, file):
        """load a KLE Gist URL or local JSON file"""

        raise NotImplementedError

    def _parsekey(self, string, props):

        raise NotImplementedError
