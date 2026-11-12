"""DINDOT: an optically drawn companion for 11-16px data UI.

This changes font outlines and metrics, not CSS tracking. Per-letter profiles
broaden bowls and preserve round marks; every letter
keeps one stem width per weight and DINish's stem-to-bar proportion.
Every exported glyph has an audit decision. The public family contains four proportional weights.
"""

from io import BytesIO
from pathlib import Path
from copy import deepcopy
from math import hypot
import json
import unicodedata
import subprocess
import sys
import skia
from shapely.geometry import LinearRing, Polygon
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
from extensions import canonical, transform
from rounding import Segment, bounds, path_from_contours, contours, round_contour
from font_anchors import move_anchor
from curve_cleanup import clean_contour
from plain_zero import add_plain_zero
from ink_offset import parallel_offset, sweep_offset, smooth_kinks
from rounding import turn, quantization_tolerance
from math import degrees

ROOT = Path(__file__).resolve().parent
STYLES = ["Regular", "Medium", "SemiBold", "Bold"]
DIGITS = [
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
]
CONFIG = {
    "version": "0.12.0",
    "target_pixels": [11, 12, 13, 14, 15, 16],
    # Bold at 3.5 has DINish Bold's stems; at 7 (to 0.20.2) it was 5.5% lighter
    # and its removed ink became space between letters.
    "inset_units": {"Regular": 0, "Medium": 0.6, "SemiBold": 3.2, "Bold": 3.5},
    # DINish stem and bar widths (1024 units; scanlines through H, n, the H bar
    # and the top of o). A stretched letter's stems would grow with its own
    # width factor; text_ink sets every stem and bar to DINish x ink_reference.
    "ink_widths": {
        "Regular": {"capitals": [75.0, 67.5], "lowercase": [69.0, 62.5]},
        "Medium": {"capitals": [95.0, 84.0], "lowercase": [88.0, 79.1]},
        "SemiBold": {"capitals": [115.0, 101.0], "lowercase": [108.0, 95.0]},
        "Bold": {"capitals": [135.0, 117.0], "lowercase": [127.0, 112.5]},
    },
    # 0.19 narrowed the letters (the default width factor went from 1.055 to
    # 1.01) and kept the strokes of 0.17 and 0.18, so the reference stays 1.055.
    "ink_reference": 1.055,
    "ink": "Stems at DINish x 1.055 less twice the inset, whatever the letter's width; bars and curves in DINish proportion to them.",
    "default": {
        "width_factor": 1.01,
        "tracking": 20,
        "reason": "A little more interior space.",
    },
    "profiles": {
        **{
            c: {
                "width_factor": 1.02,
                "tracking": 20,
                "reason": "Broader enclosed bowls; keep counters open.",
            }
            for c in "abdgopq0689"
        },
        **{
            c: {
                "width_factor": 1.03,
                "tracking": 22,
                "reason": "Open forms need more breathing room at UI sizes.",
            }
            for c in "ces"
        },
        **{
            c: {
                "width_factor": 1.0091,
                "tracking": 20,
                "reason": "Keep the capital rhythm while opening the bowl.",
            }
            for c in "CGOS"
        },
        # C and c keep DINish's own terminals. Cutting them back with a vertical
        # line (0.16 to 0.20.0) left a flat on each terminal that read as sliced off.
        "C": {
            "width_factor": 1.0091,
            "tracking": 24,
            "reason": "Keep the capital rhythm; more room on the open side.",
        },
        "c": {
            "width_factor": 1.03,
            "tracking": 24,
            "reason": "A wider bowl and more room on the open side tell c from o.",
        },
        "r": {
            "width_factor": 1.01,
            "tracking": 34,
            "reason": "Extra exit space prevents rn from closing into m.",
        },
        "n": {
            "width_factor": 1.015,
            "tracking": 22,
            "reason": "An open shoulder, paired with r and m.",
        },
        "m": {
            "width_factor": 1.0082,
            "tracking": 22,
            "reason": "Open both shoulder spaces without making the already-wide m excessive.",
        },
        "i": {
            "width_factor": 1.0045,
            "tracking": 24,
            "reason": "Preserve the round tittle; keep the narrow stem well spaced.",
        },
        "l": {
            "width_factor": 1.0055,
            "tracking": 26,
            "reason": "Keep the native foot and give cl/Il more separation.",
        },
        "I": {
            "width_factor": 1.0055,
            "tracking": 24,
            "reason": "A restrained upright; ss03 supplies the barred ID alternate.",
        },
        "1": {
            "width_factor": 1.0082,
            "tracking": 28,
            "reason": "Retain the DIN flag and plain stem; give the tabular cell breathing room.",
        },
        "2": {
            "width_factor": 1.025,
            "tracking": 24,
            "reason": "Separate the curved shoulder from the diagonal and foot.",
        },
        "5": {
            "width_factor": 1.02,
            "tracking": 24,
            "reason": "Retain the square top that distinguishes 5 from S.",
        },
        "8": {
            "width_factor": 1.02,
            "tracking": 24,
            "reason": "Balance the two counters and retain a clear waist.",
        },
        "χ": {
            "width_factor": 1.01,
            "tracking": 24,
            "inset": 0,
            "reason": "Retain the native diagonal crossing fillets; broader spacing provides the optical opening without eroding the narrow join.",
        },
    },
    "tabular_advance": 576,
    "script_advance": 368,
    # Profile tracking is relative: this shifts every proportional glyph, so most
    # letters keep DINish's own spacing and r, i, l and the open forms a little more.
    "tracking_shift": -20,
    # DINish draws every weight on the same widths, so its Bold's heavier stems
    # fill the counters. Bold letters widen 2% between their stems, as most
    # families' Bolds grow from their SemiBold; stems and side bearings stay.
    "growth": {"Bold": 1.02},
    "spacing": "Every glyph keeps its weight's DINish spacing and word space, with its relative profile; Bold letters grow inside, not in their side bearings; tabular figures and the data forms keep one width in every weight.",
    "hinting": "ttfautohint 8-32 ppem, natural stem widths, no x-height snapping",
    # Windows (GDI) clips a glyph at usWinAscent and usWinDescent, and the
    # hinter rounds the cap height up by up to a pixel, with the marks riding
    # on it: Bold's Vietnamese capital stacks rose two pixels past DINish's
    # 1.025 em at 16px. The box covers every hinted glyph at 9 to 32 px with
    # about a pixel to spare (qa/raster.py checks it). Browsers, DirectWrite
    # and macOS space lines by the typo and hhea metrics (USE_TYPO_METRICS),
    # which stay DINish's; GDI applications set lines by this box instead.
    "win_ascent": 1.1,
    "win_descent": 0.3,
    "Greek_ink": "Broaden by Latin archetype; retain distinct Greek strokes; exact aliases inherit their base ink treatment.",
}
# The share of DINish's kerning DINDOT keeps: calmer paragraph kerning.
KERNING_KEPT = 0.76
GREEK_BASE = {
    "Α": "A",
    "Β": "B",
    "Γ": "F",
    "Δ": "A",
    "Ε": "E",
    "Ζ": "Z",
    "Η": "H",
    "Θ": "O",
    "Ι": "I",
    "Κ": "K",
    "Λ": "A",
    "Μ": "M",
    "Ν": "N",
    "Ξ": "E",
    "Ο": "O",
    "Π": "H",
    "Ρ": "P",
    "Σ": "Z",
    "Τ": "T",
    "Υ": "Y",
    "Φ": "O",
    "Χ": "X",
    "Ψ": "U",
    "Ω": "O",
    "α": "a",
    "β": "b",
    "γ": "y",
    "δ": "o",
    "ε": "e",
    "ζ": "s",
    "η": "n",
    "θ": "o",
    "ι": "l",
    "κ": "k",
    "λ": "y",
    "μ": "u",
    "ν": "v",
    "ξ": "s",
    "ο": "o",
    "π": "n",
    "ρ": "p",
    "ς": "s",
    "σ": "o",
    "τ": "t",
    "υ": "u",
    "φ": "o",
    "χ": "x",
    "ψ": "u",
    "ω": "m",
    "ϕ": "o",
    "ϑ": "o",
    "ϵ": "e",
    "Ω": "O",
}


def glyph_info(font):
    inverse = {}
    for cp, name in font.getBestCmap().items():
        inverse.setdefault(name, chr(cp))
    out = {}
    for name in font.getGlyphOrder():
        raw = name.removesuffix(".data")
        # OpenType alternates have the same language/letter anatomy as their
        # encoded base. Losing that information made a.ss02, localized Polish
        # accents and Bulgarian letters follow the symbol profile instead.
        semantic_name = raw if raw in inverse else raw.split(".")[0]
        char = inverse.get(semantic_name, "")
        if raw == "t_t":
            char = "t"
        if not char:
            for digit, word in enumerate(DIGITS):
                if raw.startswith(word):
                    char = str(digit)
                    break
        base = unicodedata.normalize("NFD", char)[:1] if char else ""
        base = GREEK_BASE.get(base, base)
        if not base and raw.split(".")[0] in CONFIG["profiles"]:
            base = raw.split(".")[0]
        category = unicodedata.category(char) if char else ""
        if (
            name in font["GDEF"].table.GlyphClassDef.classDefs
            and font["GDEF"].table.GlyphClassDef.classDefs[name] == 3
        ):
            category = "Mn"
        # Roman numerals (Nl) are letters in form: they stretch, take their
        # stems, keep their height and grow in Bold as the letters do.
        numeric = any(raw.startswith(word) for word in DIGITS) or category in {
            "Nd",
            "No",
            "Nl",
        }
        is_script = (
            raw.endswith((".dnom", ".numr"))
            or raw.endswith("superior")
            or char
            and (0x2070 <= ord(char) <= 0x209F or char in "¹²³ᵢⱼᵣᵤᵥ")
        )
        if category.startswith("L") or numeric:
            rule = dict(
                CONFIG["profiles"].get(
                    char, CONFIG["profiles"].get(base, CONFIG["default"])
                )
            )
        else:
            rule = {
                "width_factor": 1,
                "tracking": 16 if category not in {"Mn", "Me", "Cf", "Zs"} else 0,
                "reason": "Keep mathematical axes, mark geometry and symbol proportions.",
            }
        out[name] = {
            **rule,
            "base": base,
            "character": char,
            "category": category,
            "numeric": numeric,
            "script": bool(is_script),
            "accented": bool(char and len(unicodedata.normalize("NFD", char)) > 1),
            "semantic_source": semantic_name,
        }
    # Follow letter anatomy through native composite aliases and accents too.
    # Cyrillic o/c and their accented forms need the same optical profiles as
    # the identical Latin skeletons, including the opened c terminal.
    relatives = {"dotlessi": "i", "dotlessj": "j"}
    # A letter drawn from DINish's parts that NFD and one-part composites do
    # not lead back to (Ҫ is С with a tail) follows the letter it was made from.
    from build import PROFILE_BASES

    relatives.update({n: b for n, b in PROFILE_BASES.items() if n in out and b in out})
    for name, rule in out.items():
        if not rule["category"].startswith("L"):
            continue
        raw = name.removesuffix(".data")
        if rule["semantic_source"] != raw and rule["semantic_source"] in out:
            relatives[name] = rule["semantic_source"]
        char = rule["character"]
        decomposed = unicodedata.normalize("NFD", char)
        if len(decomposed) > 1:
            base = font.getBestCmap().get(ord(decomposed[0]))
            if base and base != name:
                relatives[name] = base
        glyph = font["glyf"][name]
        if glyph.isComposite() and len(glyph.components) == 1:
            base, matrix = glyph.components[0].getComponentInfo()
            if matrix == (1, 0, 0, 1, 0, 0) and out[base]["category"].startswith("L"):
                relatives[name] = base
    # Exact Unicode skeleton aliases must inherit all optical decisions, not
    # just the ink inset. Iota/dotless-i and Phi/Cyrillic Ef otherwise drifted.
    drawings = json.loads((ROOT / "audit/glyph-decisions.json").read_text())["Regular"]
    for name, drawing in drawings.items():
        bases = drawing.get("native_components", [])
        if drawing.get("family") == "Greek" and len(bases) == 1:
            relatives[name] = bases[0]
            out[name]["skeleton_alias"] = bases[0]
    fields = ("width_factor", "tracking", "inset", "reason")
    done = set()

    def inherit(name, chain=()):
        if name in done:
            return
        assert name not in chain, ("optical profile cycle", chain, name)
        base = relatives.get(name)
        if base:
            inherit(base, (*chain, name))
            for key in fields:
                out[name].pop(key, None)
                if key in out[base]:
                    out[name][key] = out[base][key]
            out[name]["profile_source"] = base
        done.add(name)

    for name in out:
        inherit(name)
    return out


def is_circle(c):
    x0, y0, x1, y1 = bounds(c)
    w = x1 - x0
    h = y1 - y0
    if abs(w - h) > 0.3 or w < 1:
        return False
    cx = (x0 + x1) / 2
    cy = (y0 + y1) / 2
    r = (w + h) / 4
    return (
        max(
            abs(hypot(*((p[0] - cx, p[1] - cy))) - r)
            for seg in c
            for p in [seg.at(k / 8) for k in range(9)]
        )
        < 0.3
    )


def groups(cs):
    polys = [Polygon([seg.at(k / 12) for seg in c for k in range(12)]) for c in cs]
    parents = []
    for i, p in enumerate(polys):
        candidates = [
            j for j, q in enumerate(polys) if q.area > p.area + 1e-5 and q.contains(p)
        ]
        parents.append(
            min(candidates, key=lambda j: polys[j].area) if candidates else None
        )

    def depth(i):
        return 0 if parents[i] is None else depth(parents[i]) + 1

    return [
        [c] + [cs[j] for j in range(len(cs)) if parents[j] == i]
        for i, c in enumerate(cs)
        if depth(i) % 2 == 0
    ]


def is_apart(group, rule):
    """A round dot or an accent: moved with its letter, never stretched."""
    x0, y0, x1, y1 = bounds(group[0])
    return is_circle(group[0]) or (rule["accented"] and y1 - y0 < 250 and (y0 > 430 or y1 < 100))


def growth(name, rule, style):
    """How much wider a letter grows between its stems in this weight.

    Only letters and proportional figures whose stems text_ink sets grow; the
    tabular and data forms keep one width in every weight."""
    raw = name.removesuffix(".data")
    if (
        rule["width_factor"] == 1
        or "inset" in rule
        or rule["script"]
        or not (rule["category"].startswith("L") or rule["numeric"])
        or raw != name
        or raw.endswith((".tlf", ".tosf"))
        or raw == "uni2007"
    ):
        return 1
    return CONFIG["growth"].get(style, 1)


def offset_ink(path, inset):
    if not inset:
        return path
    border = skia.Path()
    skia.Paint(
        Style=skia.Paint.kStroke_Style,
        StrokeWidth=abs(inset) * 2,
        StrokeJoin=skia.Paint.kRound_Join,
        StrokeCap=skia.Paint.kRound_Cap,
    ).getFillPath(path, border, resScale=8)
    return canonical(
        skia.Op(
            path,
            border,
            skia.PathOp.kDifference_PathOp if inset > 0 else skia.PathOp.kUnion_PathOp,
        )
    )


def text_ink(body, rule, style, inset, upm):
    """Return the body's ink after the weight's offsets, and a record of them.

    Stretching a letter by its width factor thickens its stems by the same
    factor, and an even inset then thins bars more than stems in proportion.
    For stretched letters, a horizontal sweep sets every stem to DINish x
    ink_reference and an even offset gives bars and curves the same multiple
    of DINish, so corners keep their radius. Other glyphs keep the even inset.
    """
    if rule["width_factor"] != 1 and "inset" not in rule:
        case = "lowercase" if rule["character"].islower() else "capitals"
        stem, bar = CONFIG["ink_widths"][style][case]
        reference = CONFIG["ink_reference"]
        # Per side: across a vertical stem, and across a horizontal bar.
        across_stem = (rule["width_factor"] - reference) * stem / 2 + inset
        across_bar = inset * bar / stem - (reference - 1) * bar / 2
        even, sweep = across_bar, across_stem - across_bar
    else:
        even, sweep = inset, 0
    if not even and not sweep:
        return path_from_contours(body), {}
    record = {"even_offset": round(even, 3), "stem_offset": round(sweep, 3)}
    shapes, sources = [], []
    # Offset each separate shape on its own, so a near gap (the bar inside Θ)
    # cannot close at the first step before the second opens it again.
    for group in groups(body):
        sources.append(group)
        shapes.append(parts := [])
        joins = [(c[i - 1], s) for c in group for i, s in enumerate(c)]
        # A join over 5 degrees, even a grid-sized one, cannot be offset point
        # by point; one past the Text audit's limit is also refitted below.
        bent = any(degrees(turn(a, b)[0]) > 5 for a, b in joins)
        sharp = any(
            degrees(turn(a, b)[0]) > max(5, 2 * quantization_tolerance(a, b, upm) + 2)
            for a, b in joins
        )
        shifted = None if bent else parallel_offset(group, even) if even else group
        stem = sweep
        if shifted is not None:
            drawn = canonical(path_from_contours(shifted))
        elif sweep:
            # A fillet tighter than the even offset would fold, or the junction
            # pass left a bent join: keep this letter's bars and put the whole
            # stem change into the sweep.
            drawn, stem = canonical(path_from_contours(group)), sweep + even
            record["ink_fallback"] = "sweep only"
        else:
            # A symbol inset evenly, as before: the round pen resolves folds.
            drawn = offset_ink(path_from_contours(group), even)
            record["ink_fallback"] = "round pen"
        # Sharp joins and round-pen curves are refitted after the offsets.
        if sharp or record.get("ink_fallback") == "round pen":
            record["ink_refit"] = True
        swept = sweep_offset(drawn, stem) if stem else drawn
        if swept is None:
            record["sweep_rejected"] = True
            parts.extend(contours(drawn))
        else:
            parts.extend(smooth_kinks(contours(swept)) if stem else contours(swept))
    shapes, kept = keep_gaps(shapes, sources)
    if kept:
        record["gaps_kept"] = kept
    return canonical(path_from_contours([c for shape in shapes for c in shape])), record


def keep_gaps(shapes, sources):
    """Give way where two separate shapes overlap after the offsets.

    Since 0.19 the strokes of narrower letters grow by up to 2 units a side,
    which closed the 1.4-unit gap between the bar of Θ and its ring in
    Regular. The smaller shape is cut back by the larger one grown by the gap
    the source drew between them, so the gap keeps its width."""
    if len(shapes) < 2:
        return shapes, 0
    paths = [path_from_contours(shape) for shape in shapes]
    area = [p.computeTightBounds().width() * p.computeTightBounds().height() for p in paths]
    cut = set()

    def rings(group):
        return [LinearRing([s.at(k / 12) for s in c for k in range(12)]) for c in group]

    for i, j in ((i, j) for i in range(len(paths)) for j in range(len(paths)) if area[i] < area[j]):
        overlap = skia.Op(paths[i], paths[j], skia.PathOp.kIntersect_PathOp)
        if overlap.isEmpty() or min(overlap.computeTightBounds().width(), overlap.computeTightBounds().height()) < 1e-3:
            continue
        gap = min(a.distance(b) for a in rings(sources[i]) for b in rings(sources[j]))
        grown = skia.Path()
        skia.Paint(Style=skia.Paint.kStroke_Style, StrokeWidth=2 * gap, StrokeJoin=skia.Paint.kRound_Join).getFillPath(paths[j], grown)
        paths[i] = skia.Op(paths[i], skia.Op(paths[j], grown, skia.PathOp.kUnion_PathOp), skia.PathOp.kDifference_PathOp)
        cut.add(i)
    return [contours(canonical(paths[i])) if i in cut else shape for i, shape in enumerate(shapes)], len(cut)


def transform_marks(font, matrices):
    for lookup in font["GPOS"].table.LookupList.Lookup:
        if lookup.LookupType == 4:
            for sub in lookup.SubTable:
                for name, rec in zip(sub.MarkCoverage.glyphs, sub.MarkArray.MarkRecord):
                    move_anchor(rec.MarkAnchor, matrices[name])
                for name, rec in zip(sub.BaseCoverage.glyphs, sub.BaseArray.BaseRecord):
                    for anchor in rec.BaseAnchor:
                        move_anchor(anchor, matrices[name])
        elif lookup.LookupType == 2:
            # Calmer paragraph kerning. Data presets turn it off completely.
            for sub in lookup.SubTable:
                records = (
                    [v for ps in sub.PairSet for v in ps.PairValueRecord]
                    if sub.Format == 1
                    else [v for row in sub.Class1Record for v in row.Class2Record]
                )
                for record in records:
                    for field in ["Value1", "Value2"]:
                        value = getattr(record, field, None)
                        if value is not None and hasattr(value, "XAdvance"):
                            value.XAdvance = round(value.XAdvance * KERNING_KEPT)


def build_text(hint=True, italic=True):
    """Write the four upright faces, then (with `italic`) their italics, which
    are drawn from this run's unhinted upright outlines by italic.py."""
    from build import normalized_outline, to_glyph

    source = {
        s: TTFont(ROOT / f"masters/DINDOT-{s}.ttf", recalcTimestamp=False)
        for s in STYLES
    }
    info = glyph_info(source["Regular"])
    drawings = json.loads((ROOT / "audit/glyph-decisions.json").read_text())["Regular"]

    def ink_inset(name, style):
        rule = info[name]
        drawing = drawings.get(name, {})
        if drawing.get("family") == "circular arrows":
            # These contours already have an optical weight-specific master.
            # A second stroke offset pinches the tiny head/arc transition.
            return 0
        if "inset" in rule:
            return rule["inset"]
        if rule.get("profile_source"):
            return ink_inset(rule["profile_source"], style)
        if drawing.get("family") == "Greek":
            bases = drawing.get("native_components", [])
            if len(bases) == 1:
                return ink_inset(bases[0], style)
            return 0
        if rule["character"] and 0x391 <= ord(rule["character"]) <= 0x3F5:
            return 0
        return CONFIG["inset_units"][style]

    upm = source["Regular"]["head"].unitsPerEm
    scale = upm / 1024
    widths = {style: {} for style in STYLES}
    for name, rule in info.items():
        own = {style: f["hmtx"][name][0] for style, f in source.items()}
        old = max(own.values())
        raw = name.removesuffix(".data")
        # Every glyph keeps its own weight's DINish advance. The data forms take
        # the widest weight's, so a tabular value keeps its width in any weight.
        data = ".data" in name
        for style in STYLES:
            if old == 0:
                width = 0
            elif raw.endswith((".tlf", ".tosf")) or raw == "uni2007":
                width = CONFIG["tabular_advance"] * scale
            elif rule["script"] and (rule["numeric"] or raw.startswith("uni208")):
                width = CONFIG["script_advance"] * scale
            elif rule["category"] in {"Zs", "Cf"}:
                width = old
            else:
                tracking = max(0, rule["tracking"] + CONFIG["tracking_shift"])
                width = (old if data else own[style]) * rule["width_factor"] + tracking * scale
            widths[style][name] = round(width)
    reports = {}
    unhinted = {}
    for style, font in source.items():
        original = deepcopy(font)
        matrices = {}
        decisions = {}
        for name in font.getGlyphOrder():
            rule = info[name]
            sx = rule["width_factor"]
            advance = original["hmtx"][name][0]
            target = widths[style][name]
            dx = (target - advance * sx) / 2 / scale if advance else 0
            matrices[name] = (sx, 1, dx * scale, 0)
            cs = normalized_outline(original, name)
            # Merge intentional source overlaps before insetting. A barred
            # letter's crossing strokes are one ink shape, not nested holes.
            if cs:
                cs = contours(canonical(path_from_contours(cs)))
                junctions = []
                for c in cs:
                    real_join = any(
                        degrees(turn(c[i - 1], s)[0])
                        > max(10, 2 * quantization_tolerance(c[i - 1], s, upm) + 2)
                        for i, s in enumerate(c)
                    )
                    if real_join:
                        c, status = round_contour(
                            c,
                            {"Regular": 20, "Medium": 22, "SemiBold": 24, "Bold": 25}[
                                style
                            ],
                            0.55,
                            0.65,
                        )
                        if "unresolved-corner" in status or "protected-cusp" in status:
                            raise ValueError(
                                (style, name, "component intersection", status)
                            )
                    junctions.append(c)
                cs = junctions
            grow = growth(name, rule, style)
            ungrown = None
            if cs and grow != 1:
                # Widen the letter's body, not its dots and accents; the sweep
                # in text_ink takes the wider stems back to the weight's, so the
                # side bearings stay and only the counters gain.
                spans = [bounds(g[0]) for g in groups(cs) if not is_apart(g, rule)]
                left, right = min(b[0] for b in spans), max(b[2] for b in spans)
                case = "lowercase" if rule["character"].islower() else "capitals"
                stem = CONFIG["ink_widths"][style][case][0]
                pivot, room = left + stem / 2, (grow - 1) * sx * (right - left - stem)
                ungrown = (sx, dx, pivot, room)
                target += round(room * scale)
                dx -= (grow - 1) * sx * pivot
                sx *= grow
                matrices[name] = (sx, 1, dx * scale, 0)
                rule = {**rule, "width_factor": sx, "growth": grow}
            if not cs:
                font["hmtx"][name] = (target, 0)
                decisions[name] = {
                    **rule,
                    "inset": 0,
                    "advance": target / scale,
                    "reason": "Intentional spacing/control glyph; no outline.",
                }
                continue
            ink = {}
            if rule["category"] in {"Mn", "Me", "Cf"}:
                # Keep native mark drawings; the base anchors move with letters.
                transformed = cs
                matrices[name] = (1, 1, 0, 0)
                dot_count = 0
                inset = 0
            else:
                body = []
                marks = []
                dot_count = 0
                for group in groups(cs):
                    x0, _, x1, _ = bounds(group[0])
                    circle = is_circle(group[0])
                    if is_apart(group, rule):
                        cx = (x0 + x1) / 2
                        shift = cx * (sx - 1) + dx
                        if ungrown:
                            # A dot or accent follows the counter it sits over
                            # and no further: the stems do not move apart, so
                            # ï's dots and a capital's tonos keep their place.
                            base_sx, base_dx, pivot, room = ungrown
                            lift = (grow - 1) * base_sx * (cx - pivot)
                            shift = cx * (base_sx - 1) + base_dx + min(max(lift, 0), room)
                        moved = [
                            [
                                Segment(
                                    tuple(
                                        (p[0] + shift, p[1])
                                        for p in seg.points
                                    )
                                )
                                for seg in c
                            ]
                            for c in group
                        ]
                        marks.extend(moved)
                        dot_count += int(circle)
                    else:
                        body.extend(
                            [
                                [
                                    Segment(
                                        tuple(
                                            (p[0] * sx + dx, p[1]) for p in seg.points
                                        )
                                    )
                                    for seg in c
                                ]
                                for c in group
                            ]
                        )
                inset = ink_inset(name, style)
                if rule["script"]:
                    inset *= 0.62
                if body:
                    before = path_from_contours(body)
                    bb = before.computeTightBounds()
                    drawn, ink = text_ink(body, rule, style, inset, upm)
                    # Body height and baseline stay put; counters gain interior space.
                    if rule["category"].startswith("L") or rule["numeric"]:
                        after = drawn.computeTightBounds()
                        sy = bb.height() / after.height()
                        drawn = transform(drawn, d=sy, y=bb.top() - after.top() * sy)
                    # The offsets keep the reviewed tangent fillets smooth. Refit
                    # only a round-pen fallback.
                    transformed = [
                        clean_contour(c) if ink.get("ink_refit") else c
                        for c in contours(drawn)
                    ] + marks
                else:
                    transformed = marks
            glyph = to_glyph(canonical(path_from_contours(transformed)))
            pen = TTGlyphPen(None)
            glyph.draw(TransformPen(pen, (scale, 0, 0, scale, 0, 0)), font["glyf"])
            out = pen.glyph()
            out.recalcBounds(font["glyf"])
            font["glyf"][name] = out
            font["hmtx"][name] = (target, getattr(out, "xMin", 0))
            from audit_geometry import polygon_data

            invalid = None
            for repair in range(4):
                _, invalid = polygon_data(font, name)
                if not invalid:
                    break
                # Integer export can collapse an offset's tiny loop. Resolve
                # the actual exported outline, then check it again; never
                # repair diagnostic polygons and pass them off as the font.
                glyph = to_glyph(
                    canonical(path_from_contours(normalized_outline(font, name)))
                )
                pen = TTGlyphPen(None)
                glyph.draw(TransformPen(pen, (scale, 0, 0, scale, 0, 0)), font["glyf"])
                out = pen.glyph()
                out.recalcBounds(font["glyf"])
                font["glyf"][name] = out
                font["hmtx"][name] = (target, getattr(out, "xMin", 0))
            else:
                raise ValueError(
                    (style, name, "invalid exported Text outline", invalid)
                )
            # The offsets can fold a fillet smaller than themselves into a point,
            # sometimes only once the outline is on the font's grid: since 0.19
            # the strokes of narrower letters grow by up to 2 units a side. Round
            # such joins again, as the junction pass does, and export once more.
            exported = normalized_outline(font, name)
            folded = folded_contours(exported, upm)
            if folded:
                radius = {"Regular": 20, "Medium": 22, "SemiBold": 24, "Bold": 25}[style]
                fixed = []
                for i, c in enumerate(exported):
                    if i in folded:
                        c = drop_short_segments(clean_contour(c))
                        c, status = round_contour(c, radius, 0.55, 0.65)
                        if "unresolved-corner" in status or "protected-cusp" in status:
                            raise ValueError((style, name, "folded join", status))
                    fixed.append(c)
                glyph = to_glyph(canonical(path_from_contours(fixed)))
                pen = TTGlyphPen(None)
                glyph.draw(TransformPen(pen, (scale, 0, 0, scale, 0, 0)), font["glyf"])
                out = pen.glyph()
                out.recalcBounds(font["glyf"])
                font["glyf"][name] = out
                font["hmtx"][name] = (target, getattr(out, "xMin", 0))
                _, invalid = polygon_data(font, name)
                still = folded_contours(normalized_outline(font, name), upm)
                if invalid or still:
                    raise ValueError((style, name, "folded join after rounding", invalid, still))
                ink["folded_joins_rounded"] = len(folded)
            decisions[name] = {
                **rule,
                "inset": inset,
                "advance": target / scale,
                "preserved_circular_components": dot_count,
                **ink,
                "export_cleanup_passes": repair,
            }
        transform_marks(font, matrices)
        version = json.loads((ROOT / "settings.json").read_text())["version"]
        family = "DINDOT"
        values = {
            1: family if style in {"Regular", "Bold"} else f"{family} {style}",
            2: "Bold" if style == "Bold" else "Regular",
            3: f"DINDOT-{version}-{style}",
            4: f"{family} {style}",
            6: f"DINDOT-{style}",
            16: family,
            17: style,
        }
        for key, value in values.items():
            font["name"].removeNames(nameID=key)
            font["name"].setName(value, key, 3, 1, 0x409)
            font["name"].setName(value, key, 1, 0, 0)
        font["OS/2"].recalcAvgCharWidth(font)
        font["OS/2"].usWinAscent = round(CONFIG["win_ascent"] * upm)
        font["OS/2"].usWinDescent = round(CONFIG["win_descent"] * upm)
        font.flavor = None
        # The italics are drawn from the upright before its plain zeros exist;
        # italic.py adds its own the same way.
        buffer = BytesIO()
        font.save(buffer)
        unhinted[style] = buffer.getvalue()
        plain_zero = json.loads((ROOT / "settings.json").read_text())["plain_zero"]
        for dotted, plain in add_plain_zero(font, plain_zero).items():
            decisions[plain] = {
                **decisions[dotted],
                "plain_zero_of": dotted,
                "reason": f"{dotted} without the zero dot, selected by {plain_zero['feature']}.",
            }
        target = ROOT / f"fonts/DINDOT-{style}.ttf"
        font.save(target)
        if hint:
            hinted = target.with_suffix(".hinted.ttf")
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "ttfautohint",
                    "--hinting-range-min=8",
                    "--hinting-range-max=32",
                    "--hinting-limit=32",
                    "--stem-width-mode=nnn",
                    "--increase-x-height=0",
                    "--no-info",
                    "--default-script=latn",
                    str(target),
                    str(hinted),
                ],
                check=True,
            )
            hinted.replace(target)
        web = TTFont(target, recalcTimestamp=False)
        # The autohinter assigns scripts by Unicode. Exact skeleton aliases
        # must also share instructions: mu/micro otherwise rasterized
        # differently at 12px despite identical contours and metrics.
        for name, rule in info.items():
            base = rule.get("skeleton_alias")
            if base:
                web["glyf"][name] = deepcopy(web["glyf"][base])
                web["hmtx"][name] = web["hmtx"][base]
                decisions[name]["hint_source"] = base
        # ttfautohint stamps the current time. Keep the source timestamp so a
        # clean rebuild produces identical installation and web files.
        web["head"].modified = original["head"].modified
        web.save(target)
        web.flavor = "woff2"
        web.save(target.with_suffix(".woff2"))
        reports[style] = {
            "family": family,
            "glyphs": len(web.getGlyphOrder()),
            "unicode_characters": len(web.getBestCmap()),
            "hinted": hint,
            "glyphs_reviewed": decisions,
        }
        print(
            f"DINDOT {style}: {len(decisions)} optical profiles; hinted={hint}.",
            flush=True,
        )
    (ROOT / "text/settings.json").write_text(json.dumps(CONFIG, indent=2) + "\n")
    (ROOT / "text/build-report.json").write_text(
        json.dumps(reports, indent=2, ensure_ascii=False) + "\n"
    )
    if italic:
        from italic import build_italics, summarize_report

        aliases = {
            name: rule["skeleton_alias"]
            for name, rule in info.items()
            if rule.get("skeleton_alias")
        }
        italics = build_italics(
            unhinted,
            json.loads((ROOT / "settings.json").read_text()),
            json.loads((ROOT / "audit/glyph-decisions.json").read_text()),
            aliases,
            ROOT / "fonts",
            hint,
        )
        (ROOT / "text/build-report-italic.json").write_text(
            json.dumps(
                {k: summarize_report(v) for k, v in italics.items()},
                separators=(",", ":"),
            )
            + "\n"
        )
        for name, rep in italics.items():
            print(f"DINDOT {name}: contour treatments {rep['contour_levels']}.", flush=True)


def drop_short_segments(contour, shortest=1.0):
    """Merge segments under `shortest` units into the next one.

    A fold the offsets leave can be a spike a fraction of a unit long. Smoothing
    keeps it as a wiggle that the font's grid turns back into a spike; removing
    it leaves one real corner for round_contour to fillet."""
    c = list(contour)
    while len(c) > 3:
        short = next(
            (i for i, s in enumerate(c) if hypot(s.points[-1][0] - s.points[0][0], s.points[-1][1] - s.points[0][1]) < shortest),
            None,
        )
        if short is None:
            break
        start = c[short].points[0]
        following = (short + 1) % len(c)
        points = list(c[following].points)
        shift = (start[0] - points[0][0], start[1] - points[0][1])
        points[0] = start
        if len(points) > 2:
            points[1] = (points[1][0] + shift[0], points[1][1] + shift[1])
        c[following] = Segment(tuple(points))
        del c[short]
    return c


def folded_contours(outline, upm):
    """Indices of the contours with a join sharper than audit_text allows."""
    return {
        n
        for n, c in enumerate(outline)
        if any(
            degrees(turn(c[i - 1], s)[0]) > max(5, 2 * quantization_tolerance(c[i - 1], s, upm) + 2)
            for i, s in enumerate(c)
        )
    }


if __name__ == "__main__":
    build_text()
