"""DINDOT's drawn symbol repertoire, in the same 1024-unit design space.

No borrowed symbol font: stroke widths come from I/minus; letters and digits
come from the already-rounded DINDOT outlines. New Unicode glyphs append after
all upstream glyph IDs, preserving the existing OpenType substitutions.
"""

from collections import Counter
import json
from pathlib import Path
from math import sin, cos, pi, sqrt
import unicodedata
import skia
from shapely.geometry import Polygon
from fontTools.pens.basePen import BasePen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from rounding import Segment, contours, path_from_contours, round_contour, circle

TITTLES = json.loads((Path(__file__).resolve().parent / "settings.json").read_text())["zero_dot_diameters"]


def cubic_path(commands):
    p = skia.Path()
    for command in commands:
        op, *v = command
        getattr(
            p,
            {"M": "moveTo", "L": "lineTo", "C": "cubicTo", "Q": "quadTo", "Z": "close"}[
                op
            ],
        )(*v)
    return p


def normalize_conics(path):
    out = skia.Path()
    iterator = skia.Path.RawIter(path)
    for verb, pts in iterator:
        if verb == skia.Path.kMove_Verb:
            out.moveTo(pts[0])
        elif verb == skia.Path.kLine_Verb:
            out.lineTo(pts[-1])
        elif verb == skia.Path.kQuad_Verb:
            out.quadTo(*pts[1:])
        elif verb == skia.Path.kCubic_Verb:
            out.cubicTo(*pts[1:])
        elif verb == skia.Path.kConic_Verb:
            q = skia.Path.ConvertConicToQuads(*pts, iterator.conicWeight(), 4)
            for i in range(1, len(q), 2):
                out.quadTo(q[i], q[i + 1])
        elif verb == skia.Path.kClose_Verb:
            out.close()
    return out


def signed_area(contour):
    points = [seg.at(k / 8) for seg in contour for k in range(8)]
    return (
        sum(a[0] * b[1] - a[1] * b[0] for a, b in zip(points, points[1:] + points[:1]))
        / 2
    )


def canonical(path, simplify=True):
    if path.isEmpty():
        return skia.Path()
    cs = contours(normalize_conics(skia.Simplify(path) if simplify else path))
    # PathOps returns even-odd contours with arbitrary directions. Classify each
    # contour by nesting depth, including separate outer islands and ink inside
    # counters, then write the clockwise/counterclockwise TrueType winding.
    polygons = [Polygon([seg.at(k / 12) for seg in c for k in range(12)]) for c in cs]
    out = []
    for i, c in enumerate(cs):
        p = polygons[i]
        if p.is_empty or p.area < 1e-5:
            continue
        point = p.representative_point()
        depth = sum(
            q.area > p.area and q.contains(p) for j, q in enumerate(polygons) if j != i
        )
        want_negative = depth % 2 == 0
        if (signed_area(c) < 0) != want_negative:
            c = [Segment(tuple(reversed(seg.points))) for seg in reversed(c)]
        out.append(c)
    return path_from_contours(out)


def append_paths(*paths):
    p = skia.Path()
    for path in paths:
        p.addPath(path)
    return p


def combine(*paths):
    out = skia.Path()
    for p in paths:
        if not p.isEmpty():
            out = skia.Op(out, p, skia.PathOp.kUnion_PathOp)
    return canonical(out)


def subtract(a, b):
    return canonical(skia.Op(a, b, skia.PathOp.kDifference_PathOp))


def transform(path, a=1, b=0, c=0, d=1, x=0, y=0):
    out = skia.Path(path)
    out.transform(skia.Matrix.MakeAll(a, c, x, b, d, y, 0, 0, 1))
    return out


def rotate(path, angle, cx=0, cy=0):
    a, b = cos(angle), sin(angle)
    return transform(path, a, b, -b, a, cx - a * cx + b * cy, cy - b * cx - a * cy)


def stroke(points, width):
    if isinstance(points, skia.Path):
        line = points
    else:
        line = skia.Path()
        line.moveTo(*points[0])
        for p in points[1:]:
            line.lineTo(*p)
    out = skia.Path()
    paint = skia.Paint(
        Style=skia.Paint.kStroke_Style,
        StrokeWidth=width,
        StrokeCap=skia.Paint.kButt_Cap,
        StrokeJoin=skia.Paint.kMiter_Join,
        StrokeMiter=4,
    )
    paint.getFillPath(line, out, resScale=8)
    return canonical(out)


def rect(x0, y0, x1, y1):
    p = skia.Path()
    p.addRect(skia.Rect.MakeLTRB(x0, y0, x1, y1))
    return canonical(p)


def disk(cx, cy, diameter):
    return path_from_contours([circle(cx, cy, diameter)])


def ellipse(cx, cy, rx, ry):
    return transform(disk(0, 0, 2 * rx), d=ry / rx, x=cx, y=cy)


def polygon(points):
    p = skia.Path()
    p.moveTo(*points[0])
    for q in points[1:]:
        p.lineTo(*q)
    p.close()
    return canonical(p)


class OutlinePen(BasePen):
    def __init__(self, gs):
        super().__init__(gs)
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


class ExtensionBuilder:
    def __init__(self, font, style, radius, to_glyph):
        self.font = font
        self.style = style
        self.radius = radius
        self.to_glyph = to_glyph
        self.records = {}
        self.mappings = {}
        self.order = list(font.getGlyphOrder())
        self.gs = font.getGlyphSet()
        self.axis = 282.5
        box = self.outline("I").computeTightBounds()
        self.stem = box.width()
        self.math_stroke = self.outline("minus").computeTightBounds().height()
        self.math_advance = font["hmtx"]["plus"][0]

    def outline(self, name):
        # Recreate the glyph set after each addition, so compositions see new glyphs.
        p = OutlinePen(self.font.getGlyphSet())
        self.font["glyf"][name].draw(p, self.font["glyf"])
        return p.path

    def fit(self, path, width, height=None, bottom=None):
        b = path.computeTightBounds()
        sx = width / b.width()
        sy = sx if height is None else height / b.height()
        return transform(
            path,
            a=sx,
            d=sy,
            x=-b.left() * sx,
            y=(0 if bottom is None else bottom) - b.top() * sy,
        )

    def add(
        self,
        char,
        path=None,
        advance=None,
        family="symbols",
        reason="",
        rounded=True,
        **metadata,
    ):
        cp = ord(char)
        if cp in self.font.getBestCmap() or cp in self.mappings:
            raise ValueError(f"Duplicate character {char!r}")
        name = f"uni{cp:04X}"
        advance = advance if advance is not None else self.math_advance
        cs = contours(canonical(path, simplify=False)) if path is not None else []
        reference = contours(canonical(path)) if path is not None else []
        expected = {
            "components": sum(signed_area(c) < -0.5 for c in reference),
            "counters": sum(signed_area(c) > 0.5 for c in reference),
        }
        details = []
        statuses = Counter()
        out = []
        for c in cs:
            if rounded:
                c, status = round_contour(c, self.radius, 0.55, 0.65, audit=details)
                statuses.update(status)
            if family == "circular arrows" and rounded:
                from curve_cleanup import clean_contour

                c = clean_contour(c)
                metadata["bounded_curve_refit"] = 0.18
            out.append(c)
        if statuses.get("unresolved-corner") or statuses.get("protected-cusp"):
            raise ValueError(
                (
                    self.style,
                    char,
                    "unresolved extension corner",
                    dict(statuses),
                    [d for d in details if d["status"] != "rounded"],
                )
            )
        glyph = self.to_glyph(path_from_contours(out))
        self.font["glyf"][name] = glyph
        glyph.recalcBounds(self.font["glyf"])
        lsb = getattr(glyph, "xMin", 0)
        self.font["hmtx"][name] = (advance, lsb)
        self.order.append(name)
        self.font.setGlyphOrder(list(self.order))
        self.mappings[cp] = name
        self.records[name] = {
            "kind": "extension",
            "character": char,
            "unicode": f"U+{cp:04X}",
            "unicode_name": unicodedata.name(char, "UNNAMED"),
            "family": family,
            "radius": self.radius,
            "corners": dict(statuses),
            "corner_details": details,
            "decision": reason,
            "expected_topology": expected,
            "advance": advance,
            "stem_width": self.stem,
            "math_stroke": self.math_stroke,
            **metadata,
        }
        return name

    def compose(self, char, components, advance, family, reason):
        paths = [transform(self.outline(name), *matrix) for name, matrix in components]
        name = self.add(
            char,
            append_paths(*paths),
            advance,
            family,
            reason,
            rounded=False,
            native_components=[n for n, _ in components],
        )
        pen = TTGlyphPen(self.font.getGlyphSet())
        for base, matrix in components:
            pen.addComponent(base, matrix)
        glyph = pen.glyph()
        glyph.components[0].flags |= 0x400
        self.font["glyf"][name] = glyph
        glyph.recalcBounds(self.font["glyf"])
        self.font["hmtx"][name] = (advance, glyph.xMin)
        return name

    def alias(
        self,
        char,
        source,
        family="typographic punctuation",
        reason="Unicode alias of an existing DINDOT form.",
    ):
        # A dedicated glyph keeps the extension inventory explicit and auditable.
        return self.add(
            char,
            self.outline(source),
            self.font["hmtx"][source][0],
            family,
            reason,
            rounded=False,
        )

    def centered(self, path, advance, cy=None):
        b = path.computeTightBounds()
        return transform(
            path,
            x=advance / 2 - (b.left() + b.right()) / 2,
            y=(self.axis if cy is None else cy) - (b.top() + b.bottom()) / 2,
        )

    def arrow(self, angle=0, both=False, double=False):
        t = self.stem
        shaft = 540
        head = 190
        thin = t * 0.62 if double else t
        parts = []
        if double:
            gap = t * 0.82
            for y in [-gap, gap]:
                parts.append(
                    stroke(
                        [(-shaft / 2 + (gap if both else 0), y), (shaft / 2 - gap, y)],
                        thin,
                    )
                )
        else:
            parts.append(stroke([(-shaft / 2, 0), (shaft / 2, 0)], t))
        parts.append(
            stroke(
                [(shaft / 2 - head, head), (shaft / 2, 0), (shaft / 2 - head, -head)],
                thin,
            )
        )
        if both:
            parts.append(
                stroke(
                    [
                        (-shaft / 2 + head, head),
                        (-shaft / 2, 0),
                        (-shaft / 2 + head, -head),
                    ],
                    thin,
                )
            )
        path = rotate(combine(*parts), angle)
        return self.centered(path, 768)

    def arrows(self):
        directions = {
            "→": 0,
            "↗": pi / 4,
            "↑": pi / 2,
            "↖": 3 * pi / 4,
            "←": pi,
            "↙": 5 * pi / 4,
            "↓": 3 * pi / 2,
            "↘": 7 * pi / 4,
        }
        for char, angle in directions.items():
            self.add(
                char,
                self.arrow(angle),
                768,
                "directional arrows",
                "One master arrow, rotated; shaft matches I, terminals use the weight’s reference radius.",
                master_rotation_degrees=round(angle * 180 / pi),
                reference_stroke=self.stem,
            )
        for char, angle in [("↔", 0), ("↕", pi / 2)]:
            self.add(
                char,
                self.arrow(angle, both=True),
                768,
                "directional arrows",
                "Shared shaft and two matching heads.",
                reference_stroke=self.stem,
            )
        for char, angle in [
            ("⇒", 0),
            ("⇑", pi / 2),
            ("⇐", pi),
            ("⇓", 3 * pi / 2),
            ("⇔", 0),
            ("⇕", pi / 2),
        ]:
            self.add(
                char,
                self.arrow(angle, both=char in "⇔⇕", double=True),
                768,
                "double arrows",
                "Parallel shafts retain clearance at every weight; arrowhead proportions follow the single arrows.",
            )
        # Square return/bend arrows use a curve with tangent continuity at the elbow.
        t = self.stem
        head = 150
        for char, mirror, up in [
            ("↰", False, True),
            ("↱", True, True),
            ("↲", False, False),
            ("↳", True, False),
        ]:
            line = cubic_path(
                [
                    ("M", 150, -240),
                    ("L", 150, 60),
                    ("C", 150, 150, 100, 195, 10, 195),
                    ("L", -190, 195),
                ]
            )
            p = combine(
                stroke(line, t), stroke([(-40, 345), (-190, 195), (-40, 45)], t)
            )
            if mirror:
                p = transform(p, a=-1)
            if not up:
                p = transform(p, d=-1)
            self.add(
                char,
                self.centered(p, 768),
                768,
                "bent arrows",
                "Tangent rounded elbow; head and shaft follow the same weight system.",
            )
        for char, mirror in [("↩", False), ("↪", True)]:
            line = cubic_path(
                [
                    ("M", 140, 200),
                    ("L", 140, 20),
                    ("C", 140, -70, 85, -125, -5, -125),
                    ("L", -220, -125),
                ]
            )
            p = combine(
                stroke(line, t), stroke([(-65, 30), (-220, -125), (-65, -280)], t)
            )
            if mirror:
                p = transform(p, a=-1)
            self.add(
                char,
                self.centered(p, 768),
                768,
                "return arrows",
                "Return arrow with a genuinely curved elbow and the shared head construction.",
            )
        for char, angle in [("⇄", 0), ("⇅", pi / 2)]:
            # Each arrow is thinner than a single arrow, keeping two clear lanes.
            small = transform(
                self.arrow(), a=0.78, d=0.65, x=-384 * 0.78, y=-self.axis * 0.65
            )
            p = combine(transform(small, y=125), transform(rotate(small, pi), y=-125))
            self.add(
                char,
                self.centered(rotate(p, angle), 900),
                900,
                "exchange arrows",
                "Two optically balanced, separate lanes.",
            )
        for char, mirror in [("↻", False), ("↺", True)]:
            if mirror:
                # Mirror the final rounded/refitted outline, not a second
                # approximation of the construction. Every exported point agrees.
                self.add(
                    char,
                    transform(self.outline("uni21BB"), a=-1, x=768),
                    768,
                    "circular arrows",
                    "Exact reflection of the final clockwise master.",
                    rounded=False,
                    bounded_curve_refit=0.18,
                )
                continue
            r = 250
            start, end, steps = 7 * pi / 4, 55 * pi / 180, 6
            arc = skia.Path()
            arc.moveTo(r * cos(start), r * sin(start))
            for i in range(steps):
                a = start + (end - start) * i / steps
                b = start + (end - start) * (i + 1) / steps
                k = 4 / 3 * __import__("math").tan((b - a) / 4)
                arc.cubicTo(
                    r * (cos(a) - k * sin(a)),
                    r * (sin(a) + k * cos(a)),
                    r * (cos(b) + k * sin(b)),
                    r * (sin(b) - k * cos(b)),
                    r * cos(b),
                    r * sin(b),
                )
            base = (r * cos(end), r * sin(end))
            tangent, normal = (sin(end), -cos(end)), (cos(end), sin(end))
            length = 185 + (self.stem - 75) * 0.40
            half = 120 + (self.stem - 75) * 0.25
            tip = tuple(base[j] + tangent[j] * length * 0.75 for j in [0, 1])
            wings = [
                tuple(
                    tip[j] - tangent[j] * length + sign * normal[j] * half
                    for j in [0, 1]
                )
                for sign in [-1, 1]
            ]
            head = cubic_path([("M", *tip), ("L", *wings[0]), ("L", *wings[1]), ("Z",)])
            p = combine(stroke(arc, self.stem * 0.82), head)
            if mirror:
                p = transform(p, a=-1)
            self.add(
                char,
                self.centered(p, 768),
                768,
                "circular arrows",
                "Circular arc with a distinct filled triangular head, optically sized per weight. Counterclockwise is an exact mirror.",
            )

    def maths(self):
        t = self.math_stroke
        w = self.math_advance
        cx = w / 2
        axis = self.axis
        left = 55
        right = w - 55
        h = lambda y: stroke([(left, y), (right, y)], t)
        line = lambda pts: stroke(pts, t)
        eq = self.outline("equal")
        less = self.outline("less")
        greater = self.outline("greater")
        self.add(
            "≠",
            combine(eq, line([(cx - 140, 20), (cx + 140, 550)])),
            w,
            "mathematics",
            "Existing equals plus a weight-matched slash.",
        )
        for ch, base in [("≤", less), ("≥", greater)]:
            b = base.computeTightBounds()
            height = 340
            upper = transform(
                base, d=height / b.height(), y=150 - b.top() * height / b.height()
            )
            self.add(
                ch,
                combine(upper, h(35)),
                w,
                "mathematics",
                "Existing comparison form with a separate equality bar.",
            )
        self.add(
            "≡",
            combine(h(axis - 155), h(axis), h(axis + 155)),
            w,
            "mathematics",
            "Three equal strokes on the math axis.",
        )
        tilde = self.outline("asciitilde")
        b = tilde.computeTightBounds()
        tilde = self.centered(tilde, w)
        self.add(
            "≈",
            combine(transform(tilde, y=102), transform(tilde, y=-102)),
            w,
            "mathematics",
            "Two native tilde curves, vertically balanced.",
        )
        self.add(
            "≃",
            combine(transform(tilde, y=110), h(axis - 115)),
            w,
            "mathematics",
            "Native tilde over an equal-weight straight bar.",
        )
        self.add(
            "≅",
            combine(transform(tilde, y=200), transform(eq, y=-115)),
            w,
            "mathematics",
            "Native tilde and equals retain separate bands.",
        )
        self.add(
            "∓",
            combine(transform(self.outline("plus"), y=-90), h(540)),
            w,
            "mathematics",
            "Companion to the native plus-minus.",
        )
        self.add(
            "∥",
            combine(
                line([(cx - 100, 30), (cx - 100, 535)]),
                line([(cx + 100, 30), (cx + 100, 535)]),
            ),
            w,
            "mathematics",
            "Two weight-matched upright stems.",
        )
        self.add(
            "⊥",
            combine(h(70), line([(cx, 70), (cx, 550)])),
            w,
            "mathematics",
            "Shared upright and bar geometry.",
        )
        self.add(
            "∠",
            line([(right, 530), (left, 70), (right, 70)]),
            w,
            "mathematics",
            "Open angle with a softened vertex.",
        )
        for ch, points in [
            ("∧", [(left, 80), (cx, 500), (right, 80)]),
            ("∨", [(left, 500), (cx, 80), (right, 500)]),
        ]:
            self.add(ch, line(points), w, "mathematics", "Matching logical chevrons.")
        cup = cubic_path(
            [
                ("M", left, 530),
                ("L", left, 245),
                ("C", left, 30, right, 30, right, 245),
                ("L", right, 530),
            ]
        )
        self.add(
            "∪",
            stroke(cup, t),
            w,
            "mathematics",
            "Open union curve, aligned on the math axis.",
        )
        self.add(
            "∩",
            self.centered(transform(stroke(cup, t), d=-1), w),
            w,
            "mathematics",
            "Exact inverted companion of union.",
        )
        subset = rotate(stroke(cup, t), -pi / 2, cx, axis)
        subset = self.centered(subset, w)
        for ch, shape in [("⊂", subset), ("⊃", transform(subset, a=-1, x=w))]:
            self.add(
                ch, shape, w, "mathematics", "Matching subset and superset curves."
            )
        for ch, shape in [("⊆", subset), ("⊇", transform(subset, a=-1, x=w))]:
            b = shape.computeTightBounds()
            p = transform(shape, d=0.70, y=175 - b.top() * 0.70)
            self.add(
                ch,
                combine(p, h(35)),
                w,
                "mathematics",
                "Subset form plus a clear equality band.",
            )
        for ch, shape, negated in [
            ("∈", subset, False),
            ("∉", subset, True),
            ("∋", transform(subset, a=-1, x=w), False),
        ]:
            p = combine(shape, h(axis))
            if negated:
                p = combine(p, line([(cx - 145, 0), (cx + 145, 565)]))
            self.add(
                ch,
                p,
                w,
                "mathematics",
                "Set membership uses the shared curve and math bar.",
            )
        for ch, rotate_triangle in [("∆", False), ("∇", True)]:
            p = stroke(
                cubic_path([("M", 55, 20), ("L", cx, 600), ("L", w - 55, 20), ("Z",)]),
                t,
            )
            if rotate_triangle:
                p = rotate(p, pi, cx, 310)
            self.add(
                ch,
                p,
                w,
                "mathematics",
                "Open triangular counter with the diagonal corner profile.",
            )
        self.add(
            "∅",
            combine(
                subtract(disk(cx, axis, 440), disk(cx, axis, 440 - 2 * t)),
                line([(cx - 195, axis - 260), (cx + 195, axis + 260)]),
            ),
            w,
            "mathematics",
            "True circular ring plus the shared diagonal stroke.",
        )
        self.add(
            "√",
            line([(30, 250), (115, 310), (220, 30), (360, 610), (w + 20, 610)]),
            w + 75,
            "mathematics",
            "Open radical with a flat, extended top bar.",
        )
        self.add(
            "∑",
            line([(w - 45, 650), (55, 650), (cx + 30, 315), (55, -30), (w - 45, -30)]),
            w + 15,
            "mathematics",
            "Summation with a clear internal zigzag.",
        )
        self.add(
            "∏",
            combine(
                line([(55, -30), (55, 640), (w - 50, 640), (w - 50, -30)]),
                line([(15, 640), (w - 10, 640)]),
            ),
            w + 5,
            "mathematics",
            "Product stems and overshooting top bar.",
        )
        integral = cubic_path(
            [
                ("M", w - 50, 690),
                ("C", w - 180, 750, cx + 29.4, 650, cx + 15, 470),
                ("L", cx - 15, 95),
                ("C", cx - 28.6, -75, 120, -125, 45, -75),
            ]
        )
        self.add(
            "∫",
            stroke(integral, t),
            w,
            "mathematics",
            "A smooth integral with separate open ends.",
        )
        iw = 720
        ic = iw / 2
        infinity = cubic_path(
            [
                ("M", ic, axis),
                ("C", ic - 125, axis + 210, 40, axis + 205, 40, axis),
                ("C", 40, axis - 205, ic - 125, axis - 210, ic, axis),
                ("C", ic + 125, axis + 210, iw - 40, axis + 205, iw - 40, axis),
                ("C", iw - 40, axis - 205, ic + 125, axis - 210, ic, axis),
                ("Z",),
            ]
        )
        infinity_ink = stroke(infinity, t * 0.92)
        self.add(
            "∞",
            infinity_ink,
            iw,
            "mathematics",
            "Generous twin bowls preserve counter clearance in the heaviest weight.",
        )
        bowl = stroke(ellipse(cx - 20, 180, 180, 160), t)
        tail = cubic_path(
            [
                ("M", 75, 585),
                ("C", cx, 760, w - 40, 650, w - 40, 440),
                ("C", w - 40, 330, cx + 160, 335, cx + 160, 180),
            ]
        )
        self.add(
            "∂",
            combine(bowl, stroke(tail, t)),
            w,
            "mathematics",
            "Smooth oval bowl and a tangent upper extension.",
        )
        proportional = cubic_path(
            [
                ("M", 650, axis - 155),
                ("C", 550, axis - 210, ic + 125, axis - 210, ic, axis),
                ("C", ic - 125, axis + 210, 40, axis + 205, 40, axis),
                ("C", 40, axis - 205, ic - 125, axis - 210, ic, axis),
                ("C", ic + 125, axis + 210, 550, axis + 210, 650, axis + 155),
            ]
        )
        self.add(
            "∝",
            stroke(proportional, t * 0.92),
            iw,
            "mathematics",
            "Open proportional curves share the infinity bowl without clipping its terminals.",
        )
        self.add(
            "∀",
            combine(
                line([(50, 590), (cx, 0), (w - 50, 590)]),
                line([(cx - 135, 360), (cx + 135, 360)]),
            ),
            w,
            "mathematics",
            "Inverted A with a readable crossbar.",
        )
        exists = combine(line([(70, 580), (w - 60, 580), (w - 60, 0), (70, 0)]), h(290))
        self.add(
            "∃",
            exists,
            w,
            "mathematics",
            "Reversed E construction on the shared math widths.",
        )
        slash = self.outline("slash")
        box = slash.computeTightBounds()
        factor = 1.12
        self.compose(
            "∄",
            [
                ("uni2203", (1, 0, 0, 1, 0, 0)),
                (
                    "slash",
                    (
                        factor,
                        0,
                        0,
                        factor,
                        cx - (box.left() + box.right()) / 2 * factor,
                        axis - (box.top() + box.bottom()) / 2 * factor,
                    ),
                ),
            ],
            w,
            "mathematics",
            "Rounded exists and native slash components keep their continuous curves.",
        )
        diameter = TITTLES[self.style]
        for ch in ["⋅", "∙"]:
            self.add(
                ch,
                disk(cx, axis, diameter),
                w,
                "mathematics",
                "Circular multiplication dot, matching the i tittle.",
                rounded=False,
            )
        for ch, inverted in [("∴", False), ("∵", True)]:
            points = [(cx, axis + 170), (cx - 160, axis - 125), (cx + 160, axis - 125)]
            if inverted:
                points = [(x, 2 * axis - y) for x, y in points]
            self.add(
                ch,
                combine(*(disk(x, y, diameter) for x, y in points)),
                w,
                "mathematics",
                "Three matching circular points.",
                rounded=False,
            )

    def currencies(self):
        t = self.math_stroke
        stem = self.stem
        for ch, base, crosses in [
            ("₽", "P", [170]),
            ("₩", "W", [250, 415]),
            ("₦", "N", [260, 415]),
            ("฿", "B", []),
            ("₿", "B", []),
            ("₱", "P", [420, 545]),
        ]:
            p = self.outline(base)
            b = p.computeTightBounds()
            advance = self.font["hmtx"][base][0]
            if ch == "₿":
                # Bitcoin's two stem extensions are exposed above and below
                # the B, without forcing an extra line through its counters.
                xs = [b.left() + b.width() * fraction for fraction in [0.22, 0.46]]
                parts = [p]
                for x in xs:
                    parts.extend(
                        [
                            stroke([(x, -68), (x, stem * 0.65)], t * 0.56),
                            stroke([(x, 707 - stem * 0.65), (x, 775)], t * 0.56),
                        ]
                    )
                p = combine(*parts)
            elif ch == "฿":
                x = b.left() + b.width() * 0.46
                p = combine(p, stroke([(x, -60), (x, 767)], t * 0.48))
            else:
                if ch == "₱":
                    holes = [c for c in contours(canonical(p)) if signed_area(c) > 0]
                    counter = path_from_contours(
                        [max(holes, key=lambda c: abs(signed_area(c)))]
                    ).computeTightBounds()
                    crosses = [
                        counter.top() + counter.height() * f for f in [0.32, 0.72]
                    ]
                parts = [p] + [
                    stroke(
                        [(max(25, b.left() - 25), y), (b.right() + 20, y)],
                        t * (0.38 if ch == "₱" else 0.46),
                    )
                    for y in crosses
                ]
                p = combine(*parts)
            p = self.centered(p, advance, 353.5)
            self.add(
                ch,
                p,
                advance,
                "currencies",
                "Native DINDOT letter structure with optically lighter currency crossbars.",
            )
        # A continuous shoulder and diagonal avoid cap bumps and overlapping joins.
        w = self.font["hmtx"]["R"][0]
        bar, body, leg, outer = stem * 0.76, stem * 0.94, stem * 0.96, 515
        shoulder = cubic_path(
            [
                ("M", 190, 707),
                ("C", 415, 707, outer, 636, outer, 535),
                ("C", outer, 422, 421, 342, 235, 330),
                ("L", w - 45, 0),
                ("L", w - 45 - leg * 1.48, 0),
                ("L", 65, 344),
                ("L", 65, 401),
                ("L", 150, 401),
                ("C", 347, 401, outer - body, 450, outer - body, 535),
                ("C", outer - body, 610, 386, 707 - bar, 190, 707 - bar),
                ("Z",),
            ]
        )
        self.add(
            "₹",
            combine(
                shoulder,
                rect(65, 707 - bar, w - 50, 707),
                rect(65, 490 - bar / 2, w - 50, 490 + bar / 2),
            ),
            w,
            "currencies",
            "Continuous rupee shoulder and leg; equal aligned bands, flat top and baseline.",
        )
        lira = cubic_path(
            [("M", 160, 707), ("L", 160, 80), ("C", 350, 50, 470, 120, 480, 320)]
        )
        self.add(
            "₺",
            combine(
                stroke(lira, stem),
                stroke([(65, 380), (350, 505)], t * 0.75),
                stroke([(65, 235), (350, 360)], t * 0.75),
            ),
            560,
            "currencies",
            "Lira with parallel angled crossbars and a rounded lower hook.",
        )
        dong = self.outline("dcroat")
        w = self.font["hmtx"]["dcroat"][0]
        self.add(
            "₫",
            combine(dong, stroke([(60, -125), (w - 50, -125)], t * 0.7)),
            w,
            "currencies",
            "Native crossed d with the lower currency bar.",
        )

    def punctuation_and_spaces(self):
        for ch, source in [
            ("‑", "hyphentwo"),
            ("‒", "minus"),
            ("―", "emdash"),
            ("‧", "periodcentered"),
            ("‛", "quoteleft"),
            ("‟", "quotedblleft"),
            ("\u00ad", "hyphen"),
        ]:
            self.alias(ch, source)
        d = self.outline("period")
        advance = self.font["hmtx"]["period"][0]
        self.add(
            "‥",
            combine(d, transform(d, x=advance)),
            2 * advance,
            "typographic punctuation",
            "Two native round periods.",
            rounded=False,
        )
        prime = self.outline("minute")
        adv = self.font["hmtx"]["minute"][0] - 50
        self.add(
            "‴",
            combine(prime, transform(prime, x=adv), transform(prime, x=2 * adv)),
            3 * adv + 50,
            "typographic punctuation",
            "Three native prime marks with consistent spacing.",
            rounded=False,
        )
        for ch, source in [("‵", "minute"), ("‶", "second")]:
            p = self.outline(source)
            w = self.font["hmtx"][source][0]
            self.add(
                ch,
                transform(p, a=-1, x=w),
                w,
                "typographic punctuation",
                "Mirrored native prime mark.",
                rounded=False,
            )
        for ch, source in [("⟨", "less"), ("⟩", "greater")]:
            p = self.outline(source)
            b = p.computeTightBounds()
            p = transform(
                p,
                a=0.70,
                d=1.8,
                x=25 - b.left() * 0.70,
                y=282.5 - (b.top() + b.bottom()) * 0.9,
            )
            self.add(
                ch,
                p,
                380,
                "typographic punctuation",
                "Distinct tall angle bracket with the native comparison rhythm.",
                rounded=False,
            )
        widths = {
            0x2000: 512,
            0x2001: 1024,
            0x2002: 512,
            0x2003: 1024,
            0x2004: 1024 / 3,
            0x2005: 256,
            0x2006: 1024 / 6,
            0x2007: self.font["hmtx"]["zero"][0],
            0x2008: advance,
            0x2009: 1024 / 5,
            0x200A: 1024 / 10,
            0x202F: 1024 / 5,
            0x205F: 1024 * 4 / 18,
            0x200B: 0,
            0x200C: 0,
            0x200D: 0,
            0x2060: 0,
            0xFEFF: 0,
        }
        for cp, width in widths.items():
            self.add(
                chr(cp),
                None,
                width,
                "spacing",
                "Intentional Unicode space width; breaking/joining behavior remains the layout engine’s responsibility.",
            )

    def small_forms(self):
        names = [
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
        for digit, name in enumerate(names):
            source = f"{name}.dnom"
            p = transform(self.outline(source), y=-165)
            self.add(
                chr(0x2080 + digit),
                p,
                self.font["hmtx"][source][0],
                "subscripts",
                "Native denominator form, positioned consistently below the baseline.",
                rounded=False,
            )
        for ch, base in [
            ("⁺", "plus"),
            ("⁻", "minus"),
            ("⁼", "equal"),
            ("⁽", "parenleft"),
            ("⁾", "parenright"),
            ("₊", "plus"),
            ("₋", "minus"),
            ("₌", "equal"),
            ("₍", "parenleft"),
            ("₎", "parenright"),
        ]:
            p = self.outline(base)
            b = p.computeTightBounds()
            factor = 0.60
            if base.startswith("paren"):
                factor = 0.55
            cy = 640 if ord(ch) < 0x2080 else 60
            p = transform(p, a=factor, d=factor)
            advance = round(self.font["hmtx"][base][0] * factor)
            p = self.centered(p, advance, cy)
            self.add(
                ch,
                p,
                advance,
                "superscript operators" if ord(ch) < 0x2080 else "subscripts",
                "Scaled native operator; optical stroke follows existing superior figures.",
                rounded=False,
            )
        for ch, base in [("ⁿ", "n"), ("ⁱ", "i")]:
            factor = 0.63
            self.compose(
                ch,
                [(base, (factor, 0, 0, factor, 0, 437))],
                round(self.font["hmtx"][base][0] * factor),
                "superior letters",
                "Native lowercase component at superior scale; shared curves avoid a second quantization.",
            )
        fractions = {
            "⅐": ("1", "7"),
            "⅑": ("1", "9"),
            "⅒": ("1", "10"),
            "⅓": ("1", "3"),
            "⅔": ("2", "3"),
            "⅕": ("1", "5"),
            "⅖": ("2", "5"),
            "⅗": ("3", "5"),
            "⅘": ("4", "5"),
            "⅙": ("1", "6"),
            "⅚": ("5", "6"),
            "⅛": ("1", "8"),
            "⅜": ("3", "8"),
            "⅝": ("5", "8"),
            "⅞": ("7", "8"),
        }
        for ch, (numerator, denominator) in fractions.items():
            num_name = names[int(numerator)] + ".dnom"
            num = self.outline(num_name)
            num_width = self.font["hmtx"][num_name][0]
            parts = [transform(num, x=8, y=287)]
            slash_x = num_width + 10
            parts.append(transform(self.outline("fraction"), x=slash_x))
            dx = slash_x + 210
            for digit in denominator:
                name = names[int(digit)] + ".dnom"
                parts.append(transform(self.outline(name), x=dx))
                dx += self.font["hmtx"][name][0]
            self.add(
                ch,
                append_paths(*parts),
                dx + 8,
                "fractions",
                "Uses the native numerator shift, denominator outlines and fraction slash.",
                rounded=False,
            )

    def shapes(self):
        t = self.math_stroke
        w = 720
        cx = w / 2
        cy = self.axis
        square = rect(80, cy - 280, 640, cy + 280)
        circle_out = disk(cx, cy, 560)
        tri = polygon([(cx, cy + 310), (65, cy - 245), (655, cy - 245)])
        diamond = polygon([(cx, cy + 310), (665, cy), (cx, cy - 310), (55, cy)])
        for char, shape, hollow in [
            ("■", square, False),
            ("□", square, True),
            ("●", circle_out, False),
            ("○", circle_out, True),
            ("▲", tri, False),
            ("△", tri, True),
            ("▼", rotate(tri, pi, cx, cy), False),
            ("▽", rotate(tri, pi, cx, cy), True),
            ("◆", diamond, False),
            ("◇", diamond, True),
            ("◊", diamond, True),
        ]:
            if hollow:
                if char == "○":
                    inner = disk(cx, cy, 560 - 2 * t)
                elif char == "□":
                    inner = rect(80 + t, cy - 280 + t, 640 - t, cy + 280 - t)
                elif char in "△▽":
                    scale = max(0.35, 1 - t / 145)
                    inner = transform(
                        shape, a=scale, d=scale, x=cx * (1 - scale), y=cy * (1 - scale)
                    )
                else:
                    scale = 1 - t / 215
                    inner = transform(
                        shape, a=scale, d=scale, x=cx * (1 - scale), y=cy * (1 - scale)
                    )
                shape = subtract(shape, inner)
            self.add(
                char,
                shape,
                w,
                "geometric symbols",
                "Shared visual size; outlined and filled sister shapes use weight-matched stems.",
                rounded=char not in "●○",
            )
        check = stroke([(90, cy - 15), (255, cy - 180), (625, cy + 230)], self.stem)
        cross = combine(
            stroke([(130, cy - 230), (590, cy + 230)], self.stem),
            stroke([(130, cy + 230), (590, cy - 230)], self.stem),
        )
        for ch, p in [
            ("✓", check),
            (
                "✔",
                stroke(
                    [(90, cy - 15), (255, cy - 180), (625, cy + 230)], self.stem * 1.25
                ),
            ),
            ("✕", cross),
            (
                "✖",
                combine(
                    stroke([(130, cy - 230), (590, cy + 230)], self.stem * 1.25),
                    stroke([(130, cy + 230), (590, cy - 230)], self.stem * 1.25),
                ),
            ),
        ]:
            self.add(
                ch,
                p,
                w,
                "status symbols",
                "Check and cross drawn on the same geometric grid.",
            )
        box = subtract(
            rect(45, cy - 305, 675, cy + 305),
            rect(
                45 + t * 0.65, cy - 305 + t * 0.65, 675 - t * 0.65, cy + 305 - t * 0.65
            ),
        )
        for ch, p in [
            ("☐", box),
            (
                "☑",
                combine(
                    box, transform(check, a=0.65, d=0.65, x=cx * 0.35, y=cy * 0.35)
                ),
            ),
            (
                "☒",
                combine(
                    box, transform(cross, a=0.65, d=0.65, x=cx * 0.35, y=cy * 0.35)
                ),
            ),
        ]:
            self.add(
                ch,
                p,
                w,
                "status symbols",
                "Ballot boxes keep generous internal clearance.",
            )

    def letterlike(self):
        t = self.math_stroke
        w = 846
        cx = w / 2
        cy = 350
        ring = subtract(disk(cx, cy, 710), disk(cx, cy, 710 - 2 * t * 0.65))
        self.add(
            "◯",
            ring,
            w,
            "geometric symbols",
            "Large circular enclosure, also used by the phonogram sign.",
            rounded=False,
        )
        p = self.outline("P")
        box = p.computeTightBounds()
        factor = 0.55
        px = cx - (box.left() + box.right()) / 2 * factor
        py = cy - (box.top() + box.bottom()) / 2 * factor
        self.compose(
            "℗",
            [("uni25EF", (1, 0, 0, 1, 0, 0)), ("P", (factor, 0, 0, factor, px, py))],
            w,
            "letterlike symbols",
            "Circular enclosure and native P component preserve smoothness at every weight.",
        )
        small = []
        x = 35
        factor = 0.56
        for name in ["S", "M"]:
            small.append((name, (factor, 0, 0, factor, x, 311)))
            x += self.font["hmtx"][name][0] * factor
        self.compose(
            "℠",
            small,
            round(x + 35),
            "letterlike symbols",
            "Native S and M components at trademark height.",
        )
        n = self.outline("N")
        nw = self.font["hmtx"]["N"][0]
        o = self.outline("o")
        ob = o.computeTightBounds()
        small_o = transform(o, a=0.52, d=0.52, x=nw - 5, y=430 - ob.top() * 0.52)
        underline = stroke([(nw + 20, 365), (nw + 225, 365)], t * 0.65)
        self.add(
            "№",
            combine(n, small_o, underline),
            nw + 280,
            "letterlike symbols",
            "Native N plus a raised o and its underline.",
        )
        c = self.outline("c")
        o = self.outline("o")
        cw = self.font["hmtx"]["c"][0] * 0.6
        self.add(
            "℅",
            combine(
                transform(c, a=0.6, d=0.6, x=20, y=400),
                transform(self.outline("fraction"), x=cw + 50),
                transform(o, a=0.6, d=0.6, x=cw + 250, y=0),
            ),
            round(cw + 590),
            "letterlike symbols",
            "Native c/o in the fraction rhythm.",
            rounded=False,
        )

    def build(self):
        self.arrows()
        self.maths()
        self.currencies()
        self.punctuation_and_spaces()
        self.small_forms()
        self.shapes()
        self.letterlike()
        for table in self.font["cmap"].tables:
            if table.isUnicode():
                table.cmap.update(self.mappings)
        gdef = self.font["GDEF"].table.GlyphClassDef.classDefs
        for cp, name in self.mappings.items():
            if self.records[name]["family"] != "spacing":
                gdef[name] = 1
        self.font["OS/2"].recalcUnicodeRanges(self.font)
        self.font["OS/2"].recalcAvgCharWidth(self.font)
        return self.records


def extend_font(font, style, radius, to_glyph):
    return ExtensionBuilder(font, style, radius, to_glyph).build()
