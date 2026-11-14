"""Catalogue every encoded character in the shipped DINDOT family."""

from pathlib import Path
import json
import unicodedata
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent


def group(cp, category):
    if category[0] in {"Z", "C"}:
        return "Spacing"
    if category[0] == "M":
        return "Combining marks"
    if 0x2190 <= cp <= 0x21FF:
        return "Arrows"
    if 0x2500 <= cp <= 0x259F or 0x2800 <= cp <= 0x28FF:
        return "Terminal"
    if category == "Sc":
        return "Currency"
    if category == "Sm":
        return "Mathematics"
    if category[0] == "N":
        return "Figures"
    if category[0] == "P":
        return "Punctuation"
    if category[0] == "L":
        if 0x370 <= cp <= 0x3FF or cp == 0x2126:
            return "Greek"
        if 0x400 <= cp <= 0x52F:
            return "Cyrillic"
        return "Latin"
    return "Symbols"


def build_catalog():
    entries, families = {}, []
    for family, prefix in [
        ("DINDOT", "DINDOT"),
    ]:
        font = TTFont(ROOT / f"fonts/{prefix}-Regular.ttf")
        cmap = font.getBestCmap()
        for style in ["Medium", "SemiBold", "Bold"]:
            assert TTFont(ROOT / f"fonts/{prefix}-{style}.ttf").getBestCmap() == cmap
        families.append(
            {
                "name": family,
                "characters": len(cmap),
                "glyphs": len(font.getGlyphOrder()),
            }
        )
        for cp, name in cmap.items():
            char, category = chr(cp), unicodedata.category(chr(cp))
            entry = entries.setdefault(
                cp,
                {
                    "character": char,
                    "codepoint": cp,
                    "code": f"U+{cp:04X}",
                    "name": unicodedata.name(char, "CONTROL CHARACTER"),
                    "category": category,
                    "group": group(cp, category),
                    "families": [],
                    "advances": {},
                },
            )
            entry["families"].append(family)
            entry["advances"][family] = round(
                font["hmtx"][name][0] * 1024 / font["head"].unitsPerEm, 3
            )
    version = json.loads((ROOT / "specimen-release.json").read_text())["version"]
    (ROOT / "glyph-catalog.json").write_text(
        json.dumps(
            {
                "version": version,
                "families": families,
                "characters": [entries[cp] for cp in sorted(entries)],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    )
    print(
        f"Character explorer: {len(entries)} encoded characters catalogued in the DINDOT family."
    )


if __name__ == "__main__":
    build_catalog()
