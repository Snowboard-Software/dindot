"""Build DINDOT using optical corner profiles, tangent fillets and circular marks."""

from pathlib import Path
from math import pi, sqrt
from collections import Counter
from copy import deepcopy
import json
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.roundTools import noRound
from fontTools.ttLib.scaleUpem import scale_upem
import skia
from extensions import extend_font
from curve_cleanup import clean_contour
import source_greek
import source_vietnamese
import source_cyrillic
import source_roman
from rounding import (
    Segment,
    contours,
    path_from_contours,
    round_contour,
    circle,
    bounds,
)

ROOT = Path(__file__).resolve().parent
SETTINGS = json.loads((ROOT / "settings.json").read_text())
# Letters DINish lacks, drawn from its own parts on the freshly loaded source,
# in this order, so rounding, spacing, italics and hinting treat them as its own.
SOURCE_SCRIPTS = {
    "Greek": source_greek,
    "Vietnamese": source_vietnamese,
    "Cyrillic": source_cyrillic,
    "Roman numerals": source_roman,
}
# A drawn letter that is neither an NFD composition nor a one-part composite
# names the DINish letter it was made from, for its rounding and spacing.
PROFILE_BASES = {
    name: base
    for module in SOURCE_SCRIPTS.values()
    for name, base in getattr(module, "PROFILE_BASES", {}).items()
}
# Drawn letters whose body is a science.py drawing: rounded, then refit within
# curve_cleanup's budget, as science.py exports the plain letter.
BOUNDED_CURVE_REFIT = {
    name
    for module in SOURCE_SCRIPTS.values()
    for name in getattr(module, "BOUNDED_CURVE_REFIT", ())
}


def load_source(style):
    """DINish as DINDOT starts from it: the source font plus the letters drawn
    from its parts. Returns the font and {glyph name: (script, decision)}."""
    font = TTFont(ROOT / "source" / f"DINish-{style}.woff2", recalcTimestamp=False)
    drawn = {}
    for script, module in SOURCE_SCRIPTS.items():
        for name, decision in module.extend(font, style).items():
            drawn[name] = (script, decision)
    return font, drawn


class SkiaPen(BasePen):
    def __init__(self, glyph_set):
        super().__init__(glyph_set)
        self.path = skia.Path()

    def _moveTo(self, p):
        self.path.moveTo(*p)

    def _lineTo(self, p):
        self.path.lineTo(*p)

    def _qCurveToOne(self, a, b):
        self.path.quadTo(*a, *b)

    def _curveToOne(self, a, b, c):
        self.path.cubicTo(*a, *b, *c)

    def _closePath(self):
        self.path.close()

    def _endPath(self):
        pass


def to_glyph(path):
    pen = TTGlyphPen(None)
    convert = Cu2QuPen(pen, max_err=0.10, reverse_direction=False)
    for verb, points in path:
        pts = [(float(p.x()), float(p.y())) for p in points]
        if verb == skia.Path.kMove_Verb:
            convert.moveTo(pts[0])
        elif verb == skia.Path.kLine_Verb:
            convert.lineTo(pts[-1])
        elif verb == skia.Path.kQuad_Verb:
            convert.qCurveTo(*pts[1:])
        elif verb == skia.Path.kCubic_Verb:
            convert.curveTo(*pts[1:])
        elif verb == skia.Path.kClose_Verb:
            convert.closePath()
        else:
            raise ValueError(f"Unsupported outline verb: {verb}")
    # Keep fractional design coordinates until the final, finer export grid.
    return pen.glyph(round=noRound)


def normalized_outline(font, name):
    """Return outlines in the 1024-unit design space, regardless of export UPM."""
    gs = font.getGlyphSet()
    pen = SkiaPen(gs)
    scale = 1024 / font["head"].unitsPerEm
    gs[name].draw(TransformPen(pen, (scale, 0, 0, scale, 0, 0)))
    return contours(pen.path)


def rename(font, style):
    version = SETTINGS["version"]
    family = "DINDOT"
    names = {
        1: family if style in ("Regular", "Bold") else f"{family} {style}",
        2: "Bold" if style == "Bold" else "Regular",
        3: f"DINDOT-{version}-{style}",
        4: f"DINDOT {style}",
        5: f"Version {version}",
        6: f"DINDOT-{style}",
        8: "GetDot",
        9: "Bert Driehuis, Rick Radewagen",
        10: "DINDOT: a DINish derivative with rounded contours, circular marks, a dotted zero, native script forms and weight-matched arrows, mathematics, currencies and typographic symbols.",
        11: "https://getdot.ai",
        16: family,
        17: style,
        0: font["name"].getDebugName(0)
        + "\nCopyright 2026 GetDot (DINDOT modifications).",
    }
    for key, value in names.items():
        font["name"].removeNames(nameID=key)
        font["name"].setName(value, key, 3, 1, 0x409)
        font["name"].setName(value, key, 1, 0, 0)
    font["head"].fontRevision = float(version)


def profile(name, glyf):
    if name in PROFILE_BASES:
        # The letter it was made from; a one-part composite (Encyr is H)
        # rounds as the outline it holds.
        name = PROFILE_BASES[name]
        while glyf[name].isComposite() and len(glyf[name].components) == 1:
            name = glyf[name].components[0].glyphName
    lookup = SETTINGS["glyph_profile_aliases"].get(name, name.split(".")[0])
    return SETTINGS["letter_profiles"].get(
        lookup,
        {
            "radius_multiplier": 1,
            "reason": "Apply the shared outer/inner/acute corner system; preserve smooth native curves.",
        },
    )


def equal_area(w, h):
    """The diameter of the circle with the area of DINish's w by h dot, so a
    round dot carries the ink of the square one it replaces."""
    return sqrt(4 * w * h / pi)


def circle_for(name, contour, tittle_diameter, source_contours):
    x0, y0, x1, y1 = bounds(contour)
    w, h = x1 - x0, y1 - y0
    if name not in SETTINGS["circular_glyphs"]:
        return None
    if name in ("i", "j", "ij", "fi"):
        if y0 < 550 or h > 190:
            return None
        diameter = tittle_diameter
    else:
        # In these glyphs only the dot is round, not the stroke above it.
        if name in ("exclam", "exclamdown", "question", "questiondown", "semicolon", "divide") and (
            h > 190 or not 0.65 < w / h < 1.6
        ):
            return None
        diameter = equal_area(w, h)
    cy = (y0 + y1) / 2
    diameter = 2 * round(diameter / 2)
    if name in ("i", "j", "ij", "fi"):
        cy = 707 - diameter / 2
    if name in ("period", "colon", "exclam", "question") and abs(y0) < 1:
        cy = diameter / 2
    cx = (x0 + x1) / 2
    if name in ("i", "j", "ij", "fi"):
        edges = sorted(
            {
                p[0]
                for c in source_contours
                for seg in c
                if len(seg.points) == 2
                and abs(seg.points[0][0] - seg.points[1][0]) < 0.01
                and min(seg.points[0][1], seg.points[1][1])
                < 450
                < max(seg.points[0][1], seg.points[1][1])
                for p in [seg.points[0]]
            }
        )
        centers = [(a + b) / 2 for a, b in zip(edges, edges[1:]) if 35 < b - a < 180]
        if centers:
            cx = min(centers, key=lambda c: abs(c - cx))
    return circle(cx, cy, diameter)


def build():
    (ROOT / "masters").mkdir(exist_ok=True)
    (ROOT / "fonts").mkdir(exist_ok=True)
    reports = []
    all_audits = {}
    for style, radius in SETTINGS["radii"].items():
        font, drawn = load_source(style)
        glyph_set = font.getGlyphSet()
        originals = {}
        audits = {}
        # Capture every source outline before any base glyph is modified. In particular,
        # percent rings must not inherit the dot added to numeric zero.dnom.
        for name in font.getGlyphOrder():
            glyph = font["glyf"][name]
            if glyph.isComposite():
                for component in glyph.components:
                    if hasattr(component, "firstPt"):
                        raise ValueError(f"Point attachment needs remapping: {name}")
                audits[name] = {
                    "kind": "composite",
                    "components": [c.glyphName for c in glyph.components],
                    "decision": "Inherit the reviewed base outlines; keep source placement.",
                }
            if glyph.numberOfContours > 0 or name in SETTINGS["decompose_before_zero"]:
                pen = SkiaPen(glyph_set)
                glyph_set[name].draw(pen)
                originals[name] = contours(pen.path)
        ibox = bounds(max(originals["i"], key=lambda c: bounds(c)[1]))
        tittle_diameter = 2 * round(equal_area(ibox[2] - ibox[0], ibox[3] - ibox[1]) / 2)
        assert tittle_diameter == SETTINGS["zero_dot_diameters"][style], (
            style,
            "zero/i dot mismatch",
        )
        base_counter = min(
            [bounds(c) for c in originals["zero"]],
            key=lambda b: (b[2] - b[0]) * (b[3] - b[1]),
        )
        for name, source_contours in originals.items():
            rule = profile(name, font["glyf"])
            target = []
            decisions = Counter()
            circular = 0
            marks = []
            corner_details = []
            zero_scale = 1
            zero_extra_width = 0
            if name in SETTINGS["zero_bases"]:
                counter = min(
                    [bounds(c) for c in source_contours],
                    key=lambda b: (b[2] - b[0]) * (b[3] - b[1]),
                )
                x0, y0, x1, y1 = counter
                zero_scale = min(
                    (x1 - x0) / (base_counter[2] - base_counter[0]),
                    (y1 - y0) / (base_counter[3] - base_counter[1]),
                )
                if name in SETTINGS["zero_full_size_dot_bases"]:
                    # Old-style figures have the same stroke weight as lining figures.
                    # Their shorter height does not make the dot a smaller optical size.
                    zero_scale = 1
                zero_extra_width = SETTINGS["zero_extra_widths"][style] * zero_scale
                # Widen each contour affinely, keeping every native curve tangent.
                # The counter opens more than the outside: compensate for the larger
                # dot's ink and retain space between repeated tabular zeros.
                widened = []
                counter_index = min(
                    range(len(source_contours)),
                    key=lambda i: (
                        bounds(source_contours[i])[2] - bounds(source_contours[i])[0]
                    )
                    * (bounds(source_contours[i])[3] - bounds(source_contours[i])[1]),
                )
                for ci, contour in enumerate(source_contours):
                    a, _, b, _ = bounds(contour)
                    cx = (a + b) / 2
                    extra = (
                        zero_extra_width
                        if ci == counter_index
                        else SETTINGS["zero_outer_extra_widths"][style] * zero_scale
                    )
                    factor = (b - a + extra) / (b - a)
                    widened.append(
                        [
                            Segment(
                                tuple(
                                    (cx + (p[0] - cx) * factor, p[1])
                                    for p in seg.points
                                )
                            )
                            for seg in contour
                        ]
                    )
                source_contours = widened
            for contour in source_contours:
                dot = circle_for(name, contour, tittle_diameter, source_contours)
                if dot is not None:
                    marks.append(
                        {
                            "contour": len(target),
                            "kind": "circular-mark",
                            "bounds": bounds(dot),
                        }
                    )
                    target.append(dot)
                    circular += 1
                    continue
                rounded, statuses = round_contour(
                    contour,
                    radius,
                    SETTINGS["inner_radius_ratio"],
                    SETTINGS["acute_radius_ratio"],
                    profile_multiplier=rule["radius_multiplier"],
                    audit=corner_details,
                )
                if name in BOUNDED_CURVE_REFIT:
                    rounded = clean_contour(rounded)
                target.append(rounded)
                decisions.update(statuses)
            dotted = False
            if name in SETTINGS["zero_bases"]:
                # The smaller contour is the white counter; center the dot in its actual bounds.
                boxes = [bounds(c) for c in source_contours]
                x0, y0, x1, y1 = min(boxes, key=lambda b: (b[2] - b[0]) * (b[3] - b[1]))
                diameter = SETTINGS["zero_dot_diameters"][style] * zero_scale
                zero_dot = circle((x0 + x1) / 2, (y0 + y1) / 2, diameter)
                marks.append(
                    {
                        "contour": len(target),
                        "kind": "zero-dot",
                        "bounds": bounds(zero_dot),
                    }
                )
                target.append(zero_dot)
                dotted = True
            font["glyf"][name] = to_glyph(path_from_contours(target))
            audits[name] = {
                "kind": "outline",
                "radius": radius,
                "inner_acute_profile_multiplier": rule["radius_multiplier"],
                "profile": rule["reason"],
                "corners": dict(decisions),
                "corner_details": corner_details,
                "circular_marks": circular,
                "dotted_zero": dotted,
                "percent_isolated": name in SETTINGS["decompose_before_zero"],
                "marks": marks,
                "zero_extra_width": round(zero_extra_width, 2),
            }
            if name in BOUNDED_CURVE_REFIT:
                audits[name]["bounded_curve_refit"] = 0.18
        unresolved = [
            name
            for name, details in audits.items()
            if details.get("corners", {}).get("unresolved-corner")
            or details.get("corners", {}).get("protected-cusp")
        ]
        if unresolved:
            raise ValueError(f"Unresolved rounding in {style}: {unresolved}")
        # The drawn letters keep their rounding record and say how they were made.
        for name, (script, decision) in drawn.items():
            audits[name].update({"drawn_for": script, "decision": decision})
        # Keep the original glyph order/IDs; append the drawn Unicode extensions.
        audits.update(extend_font(font, style, radius, to_glyph))
        from science import extend_science

        audits.update(extend_science(font, style, radius, to_glyph))
        # An 8x coordinate grid keeps small fillets smooth after integer export.
        # Scale the entire font, including anchors and positioning, in one pass.
        scale_upem(font, SETTINGS["units_per_em"])
        # A small Roman numeral sets its letters as text does. A letter whose
        # rounding moved its leftmost point (i's round dot, v's rounded tips)
        # keeps DINish's side bearing, and renderers set its outline at that
        # bearing; a component is drawn at its own coordinates, so it moves too.
        for name in source_roman.SET_AS_TEXT:
            glyph = font["glyf"][name]
            for component in glyph.components:
                letter = font["glyf"][component.glyphName]
                letter.recalcBounds(font["glyf"])
                component.x += font["hmtx"][component.glyphName][1] - letter.xMin
            glyph.recalcBounds(font["glyf"])
        from data_features import optimize_report_font

        audits.update(optimize_report_font(font, radius, to_glyph))
        # Zero advances remain unchanged in ems, including tabular figures. Update the
        # sidebearings to reflect the deliberately widened heavier outlines.
        for name in font.getGlyphOrder():
            if (
                name.startswith("zero")
                or audits.get(name, {}).get("kind") == "extension"
            ):
                glyph = font["glyf"][name]
                glyph.recalcBounds(font["glyf"])
                advance, _ = font["hmtx"][name]
                drawing = audits.get(name, {})
                bases = drawing.get("native_components", [])
                if drawing.get("family") == "Greek" and len(bases) == 1:
                    # A TrueType left sidebearing contributes to the drawing
                    # origin. Share it as well as the alias's coordinates.
                    font["hmtx"][name] = font["hmtx"][bases[0]]
                    # Copy the base drawing as well: nested component drawing
                    # applies a different left-bearing origin in outline tools.
                    # Literal shared contours also rasterize identically.
                    font["glyf"][name] = deepcopy(font["glyf"][bases[0]])
                else:
                    font["hmtx"][name] = advance, getattr(glyph, "xMin", 0)
        for glyph in font["glyf"].glyphs.values():
            glyph.removeHinting()
        for tag in ["fpgm", "prep", "cvt ", "hdmx", "LTSH", "VDMX", "DSIG"]:
            if tag in font:
                del font[tag]
        rename(font, style)
        font.flavor = None
        ttf = ROOT / "masters" / f"DINDOT-{style}.ttf"
        font.save(ttf)
        font.flavor = "woff2"
        font.save(ttf.with_suffix(".woff2"))
        all_audits[style] = audits
        reports.append(
            {
                "style": style,
                "units_per_em": font["head"].unitsPerEm,
                "radius": radius,
                "glyphs": len(font.getGlyphOrder()),
                "unicode_characters": len(font.getBestCmap()),
                "outlines_processed": len(originals),
                "corners_rounded": sum(
                    a.get("corners", {}).get("rounded", 0) for a in audits.values()
                ),
                "circular_marks": sum(
                    a.get("circular_marks", 0) for a in audits.values()
                ),
                "dotted_zero_bases": SETTINGS["zero_bases"],
            }
        )
    (ROOT / "build-report.json").write_text(json.dumps(reports, indent=2) + "\n")
    (ROOT / "audit" / "glyph-decisions.json").write_text(
        json.dumps(all_audits, indent=2) + "\n"
    )
    print(json.dumps(reports, indent=2))
    from build_text import build_text

    build_text()
    from build_catalog import build_catalog

    build_catalog()


if __name__ == "__main__":
    build()
