# -*- coding: utf-8 -*-

import html
import json
from enum import Enum
from math import isclose
from urllib import request
from urllib.parse import urlparse

from recordclass import recordclass

from ..utils.logging import error, format_filename, info, warning
from ..utils.types import Color, Vector

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


def _is_stepped_caps(props):
    return props.l and all(
        map(
            lambda n: isclose(*n),
            [
                (props.w, 1.25),
                (props.h, 1),
                (props.x2, 0),
                (props.y2, 0),
                (props.w2, 1.75),
                (props.h2, 1),
            ],
        )
    )


def _is_iso_enter(props):
    return not props.l and (
        all(
            map(
                lambda n: isclose(*n),
                [
                    (props.w, 1.25),
                    (props.h, 2),
                    (props.x2, -0.25),
                    (props.y2, 0),
                    (props.w2, 1.5),
                    (props.h2, 1),
                ],
            )
        )
        or all(
            map(
                lambda n: isclose(*n),
                [
                    (props.w, 1.5),
                    (props.h, 1),
                    (props.x2, 0.25),
                    (props.y2, 0),
                    (props.w2, 1.25),
                    (props.h2, 2),
                ],
            )
        )
    )


class KleFile:
    def __init__(self):

        self.keys = []
        self.size = Vector(0, 0)

    @staticmethod
    def _load_url(ctx, url):

        urlparts = urlparse(url)

        if (
            urlparts is None
            or not urlparts.netloc.endswith("keyboard-layout-editor.com")
            or not urlparts.fragment.startswith("/gists/")
        ):
            error(ValueError(f"URL is not a valid KLE link: {url}"))

        gisturl = "https://api.github.com" + urlparts.fragment

        try:
            with request.urlopen(gisturl) as response:
                gist = json.load(response)
        except request.HTTPError as e:
            error(
                IOError(f"cannot load KLE data: request returned {e} for URL {gisturl}"), file=url
            )
        except request.URLError as e:
            error(IOError(f"cannot load KLE data: {e.reason} for URL {gisturl}"), file=url)
        except json.JSONDecodeError as e:
            error(
                ValueError(f"invalid JSON response for URL {gisturl}: {str(e).lower()}"), file=url
            )

        if "files" not in gist:
            error(ValueError("no files found in KLE gist"), file=url)

        file = [f for f in gist.get("files", []) if f.endswith(".kbd.json")]

        if len(file) == 0:
            error(ValueError("no valid KLE files found in KLE gist"), file=url)
        file = file[0]

        if "content" not in gist["files"][file]:
            error(ValueError("no content in file in KLE gist"), file=url)

        return gist["files"][file]["content"]

    @staticmethod
    def _load_file(ctx, path):

        try:
            with open(path) as f:
                return f.read()

        except IOError as e:
            error(
                IOError(f"cannot load KLE layout from {format_filename(path)}: {e.strerror}"),
                file=path,
            )

    @classmethod
    def load(cls, ctx, file):
        """load a KLE Gist URL or local JSON file"""

        self = cls()

        if urlparse(file).scheme in ("http", "https"):
            data = self._load_url(ctx, file)
        else:
            data = self._load_file(ctx, file)

        self.file = file

        try:
            data = json.loads(data)
        except json.JSONDecodeError as e:
            error(ValueError(f"cannot decode KLE JSON file: {str(e).lower()}"), file=self.file)

        props = _Props(self.file)

        for row in data:
            # skip metadata
            if isinstance(row, dict):
                continue

            for key in row:
                if isinstance(key, str):
                    pos, size, type, legend, legsize, bgcol, fgcol = self._parsekey(key, props)

                    self.keys.append(
                        Key(
                            pos=pos,
                            size=size,
                            type=type,
                            legend=legend,
                            legsize=legsize,
                            bgcol=bgcol,
                            fgcol=fgcol,
                        )
                    )

                    props.nextkey()

                elif isinstance(key, dict):
                    props.parse(key)

            props.newline()

        self.size = Vector(props.maxw, props.maxh)

        ctx.kle = self

    def _parsekey(self, string, props):
        legend = [html.unescape(leg) for leg in kle_to_ord(string.split("\n"), props.a)]

        pos = Vector(props.x, props.y)
        size = Vector(props.w, props.h)

        if _is_stepped_caps(props):
            size = "step"
        elif _is_iso_enter(props):
            size = "iso"
            if props.x2 < 0:
                pos = pos._replace(x=pos.x + props.x2)
        else:
            for p in ("l", "x2", "y2", "w2", "h2"):
                if not isclose(getattr(props, p), props.defaults[p]):
                    warning(
                        ValueError(f"unsupported property '{p}' in KLE data"),
                        "Ignoring this property",
                        file=self.file,
                    )
                    info(
                        "stepped caps lock and ISO enter use unsupported properties but are "
                        "supported as special cases. This warning is about another key that is "
                        f"using the '{p}' property"
                    )

        type = KeyType.NORM
        if any(p in props.p for p in ["deep", "dish", "scoop"]):
            type = KeyType.SCOOP
        elif any(p in props.p for p in ["bar", "line"]):
            type = KeyType.BAR
        elif any(p in props.p for p in ["bump", "dot", "nub", "nipple"]):
            type = KeyType.BUMP
        elif "space" in props.p:
            type = KeyType.SPACE
        elif props.n:
            type = KeyType.DEFHOME
        elif props.d:
            type = KeyType.NONE

        bgcol = Color.from_hex(props.c)
        if "\n" in props.t:
            colors = props.t.split("\n")
            if colors[0]:
                defaultcolor = Color.from_hex(colors[0])
            else:
                defaultcolor = Color(0, 0, 0)
            fgcol = kle_to_ord(props.t.split("\n"), props.a)
            fgcol = [Color.from_hex(fg) if fg else defaultcolor for fg in fgcol]
        else:
            fgcol = 12 * [Color.from_hex(props.t)]

        legsize = [props.f] * 9

        return (pos, size, type, legend, legsize, bgcol, fgcol)


class _Props:
    def __init__(self, file):
        # Next-key modifiers
        self.x = self.defaults["x"]
        self.y = self.defaults["y"]
        self.w = self.defaults["w"]
        self.h = self.defaults["h"]
        self.x2 = self.defaults["x2"]
        self.y2 = self.defaults["y2"]
        self.w2 = self.defaults["w2"]
        self.h2 = self.defaults["h2"]
        self.l = self.defaults["l"]  # stepped  # noqa: E741
        self.n = self.defaults["n"]  # homing
        self.d = self.defaults["d"]  # invisible
        # Persistent modifiers
        self.c = self.defaults["c"]  # bg colour
        self.t = self.defaults["t"]  # fg colour
        self.a = self.defaults["a"]  # alignment
        self.p = self.defaults["p"]  # profile info
        self.f = self.defaults["f"]  # font size

        self.maxw = 0
        self.maxh = 0

        self.file = file

    @property
    def defaults(self):
        return {
            "x": 0,
            "y": 0,
            "w": 1,
            "h": 1,
            "x2": 0,
            "y2": 0,
            "w2": self.w if hasattr(self, "w") else 0,
            "h2": self.h if hasattr(self, "h") else 0,
            "l": False,
            "n": False,
            "d": False,
            "c": "#cccccc",
            "t": "#000000",
            "a": 4,
            "p": "",
            "f": 3,
        }

    def parse(self, props):
        self.x += props.get("x", 0)
        self.y += props.get("y", 0)
        self.w = props.get("w", 1)
        self.h = props.get("h", 1)
        self.x2 = props.get("x2", 0)
        self.y2 = props.get("y2", 0)
        self.w2 = props.get("w2", self.w)
        self.h2 = props.get("h2", self.h)
        self.l = props.get("l", False)  # noqa: E741
        self.n = props.get("n", False)
        self.d = props.get("d", False)

        self.c = props.get("c", self.c)
        self.t = props.get("t", self.t)
        self.a = props.get("a", self.a)
        self.p = props.get("p", self.p)
        self.f = props.get("f", self.f)

        for p in props:
            if p not in self.defaults.keys():
                warning(
                    ValueError(f"unsupported property '{p}' in KLE data"),
                    "Ignoring this property",
                    file=self.file,
                )

    def newline(self):
        self.x = 0
        self.y += 1

    def nextkey(self):

        self.maxw = max(self.maxw, self.x + self.w)
        self.maxh = max(self.maxh, self.y + self.h)

        # Reset variables
        self.x += self.w
        # self.y += 0
        self.w = 1
        self.h = 1
        self.x2 = 0
        self.y2 = 0
        self.w2 = self.w
        self.h2 = self.h
        self.l = False  # noqa: E741
        self.n = False
        self.d = False
