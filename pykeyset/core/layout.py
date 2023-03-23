from __future__ import annotations

import json
from urllib import request
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse

# from . import Context
from .._impl.drawing import Drawing
from .._impl.layout import Layout
from ..utils.logging import error, format_filename


def layout(ctx):
    """generate a layout diagram from the loaded resources"""

    if ctx.layout is None:
        error(ValueError("no layout is loaded"))
    elif ctx.font is None:
        error(ValueError("no font is loaded"))
    elif ctx.profile is None:
        error(ValueError("no profile is loaded"))

    ctx.drawing = Drawing(ctx.layout, ctx.profile, ctx.font).to_svg()


def load(ctx, file: str):
    """load a KLE Gist URL or local JSON file"""

    if urlparse(file).scheme in ("http", "https"):
        data = _load_url(file)
    else:
        data = _load_file(file)

    try:
        ctx.layout = Layout.from_kle(data)

    except ValueError as e:
        error(ValueError(f"cannot decode KLE JSON file: {str(e).lower()}"), file=file)


def _load_url(url: str) -> str:
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
    except HTTPError as e:
        error(OSError(f"cannot load KLE data: request returned {e} for URL {gisturl}"), file=url)
    except URLError as e:
        error(OSError(f"cannot load KLE data: {e.reason} for URL {gisturl}"), file=url)
    except json.JSONDecodeError as e:
        error(ValueError(f"invalid JSON response for URL {gisturl}: {str(e).lower()}"), file=url)

    if "files" not in gist:
        error(ValueError("no files found in KLE gist"), file=url)

    file = [f for f in gist.get("files", []) if f.endswith(".kbd.json")]

    if len(file) == 0:
        error(ValueError("no valid KLE files found in KLE gist"), file=url)
    file = file[0]

    if "content" not in gist["files"][file]:
        error(ValueError("no content in file in KLE gist"), file=url)

    return gist["files"][file]["content"]


def _load_file(path: str) -> str:
    try:
        with open(path) as f:
            return f.read()

    except OSError as e:
        error(
            OSError(f"cannot load KLE layout from {format_filename(path)}: {e.strerror}"),
            file=path,
        )
