# -*- coding: utf-8 -*-

import tempfile
from xml.etree import ElementTree as et

from ..utils.logging import error, format_filename, info, warning


def fontgen(ctx, output, input):
    """create a new XML font file from a source font"""

    try:
        import fontforge
    except ModuleNotFoundError as e:
        from rich import inspect

        inspect(e)
        error(
            ImportError(
                "cannot import Python FontForge module. Make sure it is installed on your system",
                name=e.name,
                path=e.path,
            )
        )

    if not output.endswith(".xml"):
        output = output + ".xml"

    info("opening font with FontForge", file=input)
    try:
        font = fontforge.open(input, 0x10)  # 0x10 = hidewindow
    except Exception as e:
        error(IOError(f"FontForge could not load the font {format_filename(input)}: {e}"))

    with tempfile.NamedTemporaryFile(suffix=".svg") as tmp:

        font.generate(tmp.name)
        tmp.seek(0)

        info("reading FontForge output", file=input)

        try:
            root = et.parse(tmp).getroot()
            namespace = {"default": "http://www.w3.org/2000/svg"}
        except et.ParseError as e:
            error(ValueError(f"cannot parse FontForge output: {e.msg.capitalize()}"), file=input)

        defs = _et_get_child(root, "defs")
        font = _et_get_child(defs, "font")

        ksfont = et.Element("keyset-font")

        if "horiz-adv-x" in font.attrib:
            ksfont.set("horiz-adv-x", font.get("horiz-adv-x"))
        else:
            warning(
                AttributeError(
                    f"no 'horiz-adv-x' attribute found for '{font.tag}' in FontForge SVG output"
                ),
                "All glyphs must have their 'horiz-adv-x' set individually.",
                file=input,
            )

        fontface = _et_get_child(font, "font-face")

        ksfont.set("em-size", _et_get_attr(fontface, "units-per-em"))
        ksfont.set("x-height", _et_get_attr(fontface, "x-height"))
        ksfont.set("cap-height", _et_get_attr(fontface, "cap-height"))
        ksfont.set("ascent", _et_get_attr(fontface, "ascent"))
        ksfont.set("descent", _et_get_attr(fontface, "descent"))
        ksfont.set("slope", _et_get_attr(fontface, "slope", "0"))

        info("parsing replacement glyph", file=input)

        missing = (
            font.findall("default:missing-glyph", namespace)[::-1]
            + font.findall("default:glyph[@glyph-name='.notdef']", namespace)[::-1]
            + font.findall("default:glyph[@glyph-name='\uFFFD']", namespace)[::-1]
        )
        missing = [g for g in missing if "d" in g.attrib]

        if len(missing) != 0:
            missing = missing[-1]
            attrib = {
                "d": missing.get("d"),
                "transform": "scale(1, -1)",
            }
            if "horiz-adv-x" in missing.attrib:
                attrib["horiz-adv-x"] = missing.get("horiz-adv-x")
            ksfont.append(et.Element("missing", attrib))
        else:
            warning(
                "no replacement glyph found in font",
                "If any glyphs are missing a default character will be drawn",
                file=input,
            )

        info("parsing glyphs", file=input)

        for glyph in font.findall("default:glyph", namespace):
            if not all(a in glyph.attrib for a in ("unicode", "d")):
                continue

            attrib = {}
            attrib["char"] = glyph.get("unicode")
            if "horiz-adv-x" in glyph.attrib:
                attrib["horiz-adv-x"] = glyph.get("horiz-adv-x")
            attrib["transform"] = "scale(1, -1)"
            # Add path last so that recent versions or etree that preserve ordering add it last
            attrib["path"] = glyph.get("d")

            ksfont.append(et.Element("glyph", attrib))

        info("parsing kerning information", file=input)

        for kern in font.findall("default:hkern", namespace):
            u1attr = kern.get("u1", kern.get("g1", None))
            u2attr = kern.get("u2", kern.get("g1", None))
            k = kern.get("k", None)

            if u1attr is None or u2attr is None or k is None:
                continue

            # Using a bit of a hack to split these lists of characters, since ',' is the delimiter
            # for multi-char sequences, but a comma is also a valid character in those sequences
            # when written as '&#x2c;'. Since the XML parser naturally decodes XML escape sequences
            # we can't tell the difference between the delimiter and the characters it's meant to be
            # delimiting. So if we end up with empty value when splitting, we were probably meant to
            # have a comma in the sequence, so we remove the empty entries, add back in a comma, and
            # hope nothing breaks.
            u1list = u1attr.split(",")
            if any(len(u1) == 0 for u1 in u1list):
                u1list = [u1 for u1 in u1list if len(u1) > 0]
                u1list.append(",")
            u2list = u2attr.split(",")
            if any(len(u2) == 0 for u2 in u2list):
                u2list = [u2 for u2 in u2list if len(u2) > 0]
                u2list.append(",")

            for u1 in u1list:
                for u2 in u2list:
                    attrib = {
                        "u": f"{u1}{u2}",
                        "k": k,
                    }
                    ksfont.append(et.Element("kern", attrib))

        for el in ksfont.iter():
            el.tail = "\n"
            if len(el) > 0:
                el.text = "\n"

        info("generating output", file=input)

        try:
            et.ElementTree(ksfont).write(output)
        except IOError as e:
            error(IOError(0, f"cannot write font to file. {e.strerror}", 0, output), file=input)


_unset = lambda: None  # noqa: E731


def _et_get_child(node, name, default=_unset):

    res = node.findall(f"default:{name}", {"default": "http://www.w3.org/2000/svg"})

    if len(res) == 0:
        error(ValueError(f"no '{name}' node found in '{node.tag}' in FontForge SVG output"))
    elif len(res) > 1:
        warning(
            ValueError(f"multiple '{name}' nodes found in '{node.tag}' in FontForge SVG output"),
            "Using last node found",
        )

    return res[-1]


def _et_get_attr(node, name, default=_unset):

    tag = node.tag
    if tag.startswith("{"):
        tag = tag[tag.find("}") + 1 :]

    if name in node.attrib:
        return node.get(name)
    elif default is _unset:
        error(ValueError(f"no '{name}' attribute found for '{tag}' in FontForge SVG output"))
    else:
        warning(
            ValueError(f"no '{name}' attribute found for '{tag}' in FontForge SVG output"),
            f"Using default value ({default})",
        )
        return default
