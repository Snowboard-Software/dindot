"""Monotonic Greek: the tonos and dialytika letters, on DINish's own parts.

`extend(font, style)` runs on the freshly loaded DINish font, before any
rounding, so the corners, dots, spacing, italics and hinting treat these
letters like DINish's own accented Latin.

The tonos is DINish's acute stood 14 degrees more upright: the same stroke,
length, thickness, taper and horizontal cuts, on the same bottom line and
around the same middle, so it reaches a little higher. Lowercase letters carry
it where DINish carries the acute on the Latin letter of the same shape;
capitals carry it at the upper left, outside the letter, which moves right
until it has the white H has there. The dialytika letters use DINish's
dieresis; with a tonos the dots stay where the dieresis has them and the tonos
stands between them, as low as it can while it keeps clear of both.

Epsilon, eta, omega and capital Omega are not in DINish: science.py draws them
later, from the rounded masters. Their tonos forms are drawn here from the same
recipes, read from science.py's own builder on the source font, so the accented
letter has the plain letter's body.
"""

from copy import deepcopy
from math import atan2, ceil, degrees, radians, sin, tan, hypot
import skia
from fontTools.pens.basePen import BasePen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.misc.bezierTools import splitCubicAtT, splitQuadraticAtT
from fontTools.misc.roundTools import noRound
from kerning import copy_kerning

TONOS_TURN = 14  # degrees steeper than DINish's acute
# Tonos to dot, as a share of the dieresis's own gap: Noto Sans and Fira Sans
# keep 0.33 to 0.5 of it.
DIALYTIKA_CLEAR = 0.4
# H's capital tonos: its closest approach to the stem, as a share of H's left
# bearing. The white H then has under the tonos, averaged over the tonos's
# height, is every capital's.
TONOS_NEAREST = 0.6
# No capital comes closer to the tonos than this share of H's bearing,
# measured on the letter as build.py rounds it.
TONOS_FLOOR = 0.45
EXTREME_MARGIN = 8  # units; see _x_extremes
CAP = 707
ROUND_XY = 0x0004
USE_MY_METRICS = 0x0200

# Lowercase letters: base glyph, and the DINish acute composite of the same
# shape whose acute position the tonos takes.
LOWER_TONOS = {
    "ά": ("alpha", None),
    "έ": ("ε", None),
    "ή": ("η", "nacute"),
    "ί": ("dotlessi", "iacute"),
    "ό": ("o", "oacute"),
    "ύ": ("u", "uacute"),
    "ώ": ("ω", None),
}
UPPER_TONOS = {
    "Ά": "A",
    "Έ": "E",
    "Ή": "H",
    "Ί": "I",
    "Ό": "O",
    "Ύ": "Y",
    "Ώ": "Ω",
}
# Dialytika letters: base, and DINish's dieresis composite of the same shape.
DIERESIS = {
    "Ϊ": ("I", "Idieresis"),
    "Ϋ": ("Y", "Ydieresis"),
    "ϊ": ("dotlessi", "idieresis"),
    "ϋ": ("u", "udieresis"),
}
DIERESIS_TONOS = {
    "ΐ": ("dotlessi", "idieresis"),
    "ΰ": ("u", "udieresis"),
}
NAMES = {
    "Ά": "Alphatonos",
    "Έ": "Epsilontonos",
    "Ή": "Etatonos",
    "Ί": "Iotatonos",
    "Ό": "Omicrontonos",
    "Ύ": "Upsilontonos",
    "Ώ": "Omegatonos",
    "ά": "alphatonos",
    "έ": "epsilontonos",
    "ή": "etatonos",
    "ί": "iotatonos",
    "ό": "omicrontonos",
    "ύ": "upsilontonos",
    "ώ": "omegatonos",
    "ΐ": "iotadieresistonos",
    "ΰ": "upsilondieresistonos",
    "ϊ": "iotadieresis",
    "ϋ": "upsilondieresis",
    "Ϊ": "Iotadieresis",
    "Ϋ": "Upsilondieresis",
    "\u0384": "tonos",
    "\u0385": "dieresistonos",
    "\u0387": "anoteleia",
    "\u037e": "uni037E",
}
# Latin glyphs whose kerning sides these letters share. A capital's tonos
# changes its left side, so it takes only its base letter's right side.
KERN_BOTH = {
    "Α": "A",  # DINish's own Alpha, the A skeleton, which DINish leaves unkerned
    "ί": "iacute",
    "ό": "oacute",
    "ύ": "uacute",
    "ϊ": "idieresis",
    "ϋ": "udieresis",
    "ΐ": "idieresis",
    "ΰ": "udieresis",
    "Ϊ": "Idieresis",
    "Ϋ": "Ydieresis",
}
KERN_RIGHT = {"Ά": "A", "Έ": "E", "Ή": "H", "Ί": "I", "Ό": "O", "Ύ": "Y"}
# Round on the left as o is, so Τά and Τώ kern as Το, as in Noto Sans and Fira
# Sans; their right sides have no Latin twin. DINish's own α included.
# science.py does the same for ε, σ, ς and ω.
KERN_LEFT = {"α": "o", "ά": "o", "έ": "o", "ώ": "o"}
# Letters whose body is a science.py drawing. science.py exports ε, η, ω and Ω
# rounded and then refit by curve_cleanup; build.py does the same to these
# after rounding them, so each keeps its plain letter's body.
BOUNDED_CURVE_REFIT = {"epsilontonos", "etatonos", "omegatonos", "Omegatonos"}


class _SkiaPen(BasePen):
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


def _outline(font, name):
    pen = _SkiaPen(font.getGlyphSet())
    font["glyf"][name].draw(pen, font["glyf"])
    return pen.path


def _x_extremes(points):
    """Where a curve turns horizontally, away from its ends.

    A turn within EXTREME_MARGIN units of an end is left alone: the end is
    already nearly the extreme, and a sliver of curve would kink on the grid.
    """
    v = [p[0] for p in points]
    ts = []
    if len(v) == 3:
        d = v[0] - 2 * v[1] + v[2]
        if abs(d) > 1e-9:
            ts = [(v[0] - v[1]) / d]
    else:
        a = v[3] - 3 * v[2] + 3 * v[1] - v[0]
        b = 2 * (v[2] - 2 * v[1] + v[0])
        c = v[1] - v[0]
        if abs(a) < 1e-9:
            ts = [-c / b] if abs(b) > 1e-9 else []
        elif b * b - 4 * a * c >= 0:
            root = (b * b - 4 * a * c) ** 0.5
            ts = [(-b + root) / (2 * a), (-b - root) / (2 * a)]
    out = []
    for t in sorted(round(t, 9) for t in ts if 0 < t < 1):
        at = _point_at(points, t)
        if (
            min(hypot(at[0] - e[0], at[1] - e[1]) for e in (points[0], points[-1]))
            > EXTREME_MARGIN
        ):
            out.append(t)
    return out


def _point_at(points, t):
    pts = list(points)
    while len(pts) > 1:
        pts = [
            (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
            for a, b in zip(pts, pts[1:])
        ]
    return pts[0]


def _simple(path):
    """A TrueType glyph from a skia path, kept in design units.

    Curves are split at their horizontal extremes first, as a drawn source
    glyph has them: the leftmost point is then an on-curve point, so the left
    side bearing stays the outline's own through the rounding.
    """
    pen = TTGlyphPen(None)
    convert = Cu2QuPen(pen, max_err=0.1, reverse_direction=False)
    for verb, pts in path:
        # Skia gives each segment with its start point first.
        pts = [(float(p.x()), float(p.y())) for p in pts]
        if verb == skia.Path.kMove_Verb:
            convert.moveTo(pts[0])
        elif verb == skia.Path.kLine_Verb:
            convert.lineTo(pts[-1])
        elif verb in (skia.Path.kQuad_Verb, skia.Path.kCubic_Verb):
            split = splitQuadraticAtT if len(pts) == 3 else splitCubicAtT
            for piece in split(*pts, *_x_extremes(pts)):
                if len(piece) == 3:
                    convert.qCurveTo(*piece[1:])
                else:
                    convert.curveTo(*piece[1:])
        elif verb == skia.Path.kClose_Verb:
            convert.closePath()
        else:
            raise ValueError(f"Unsupported outline verb: {verb}")
    return pen.glyph(round=noRound)


def _polygon(points):
    path = skia.Path()
    path.moveTo(*points[0])
    for p in points[1:]:
        path.lineTo(*p)
    path.close()
    return path


def _offset(path, dx, dy=0):
    out = skia.Path(path)
    out.offset(dx, dy)
    return out


def _left_at(path, y, x0, x1):
    """The leftmost ink of `path` on the line y, or None."""
    x = x0
    while x <= x1 and not path.contains(x, y):
        x += 2
    if x > x1:
        return None
    lo, hi = x - 2, x
    for _ in range(12):
        mid = (lo + hi) / 2
        if path.contains(mid, y):
            hi = mid
        else:
            lo = mid
    return hi


def _science_recipes(font, style):
    """Epsilon, eta, omega and Omega as science.py draws them, on this font."""
    from science import ScienceBuilder

    class Recipes(ScienceBuilder):
        def __init__(self):
            super().__init__(font, style, 0, None)
            self.drawn = {}

        def letter(self, ch, path, width=600):
            if ord(ch) in self.font.getBestCmap():
                return self.font.getBestCmap()[ord(ch)]
            self.drawn[ch] = (path, width)
            self.mappings[ord(ch)] = f"uni{ord(ch):04X}"
            return self.mappings[ord(ch)]

        def alias_letter(self, ch, base, advance=None):
            return base

    recipes = Recipes()
    recipes.greek()
    return {ch: recipes.drawn[ch] for ch in "εηωΩ"}


def _tonos_points(font):
    """DINish's acute stood up by TONOS_TURN degrees.

    The stroke keeps its length, its thickness across the stroke, its taper,
    its horizontal cuts, its bottom height and the x of its middle; only the
    angle changes, so it rises a little higher than the acute.
    """
    coords, ends, _ = font["glyf"]["acutecomb"].getCoordinates(font["glyf"])
    assert list(ends) == [3], "acutecomb is one quadrilateral"
    pts = [tuple(p) for p in coords]
    y0 = min(p[1] for p in pts)
    y1 = max(p[1] for p in pts)
    bottom = sorted(p[0] for p in pts if p[1] == y0)
    top = sorted(p[0] for p in pts if p[1] == y1)
    assert len(bottom) == 2 and len(top) == 2
    bc, tc = sum(bottom) / 2, sum(top) / 2
    wb, wt = bottom[1] - bottom[0], top[1] - top[0]
    acute = atan2(y1 - y0, tc - bc)
    turned = acute + radians(TONOS_TURN)
    length = hypot(tc - bc, y1 - y0)
    keep = sin(acute) / sin(turned)  # the same thickness across the stroke
    mx = (bc + tc) / 2
    h = round(length * sin(turned))
    run = h / 2 / tan(turned)
    bc, tc = mx - run, mx + run
    wb, wt = wb * keep, wt * keep
    points = [
        (bc - wb / 2, y0),
        (tc - wt / 2, y0 + h),
        (tc + wt / 2, y0 + h),
        (bc + wb / 2, y0),
    ]
    return [(round(x), y) for x, y in points], degrees(acute), degrees(turned)


def _dieresis_dots(font):
    """Each DINish dieresis dot as DINDOT draws it: (cx, cy, diameter)."""
    from build import equal_area

    coords, ends, _ = font["glyf"]["dieresiscmb"].getCoordinates(font["glyf"])
    assert list(ends) == [3, 7], "dieresiscmb is two square dots"
    dots = []
    for a, b in ((0, 4), (4, 8)):
        xs = [p[0] for p in coords[a:b]]
        ys = [p[1] for p in coords[a:b]]
        w, h = max(xs) - min(xs), max(ys) - min(ys)
        # build.circle_for: a dieresis dot becomes a circle of the square's area.
        dots.append(
            (
                (min(xs) + max(xs)) / 2,
                (min(ys) + max(ys)) / 2,
                2 * round(equal_area(w, h) / 2),
            )
        )
    return dots[0], dots[1]


def _distance_to_polygon(point, polygon):
    best = None
    for a, b in zip(polygon, polygon[1:] + polygon[:1]):
        ax, ay = a
        dx, dy = b[0] - ax, b[1] - ay
        t = max(
            0,
            min(1, ((point[0] - ax) * dx + (point[1] - ay) * dy) / (dx * dx + dy * dy)),
        )
        d = hypot(point[0] - ax - t * dx, point[1] - ay - t * dy)
        best = d if best is None else min(best, d)
    return best


def _anchor_lookups(font):
    out = []
    for lookup in font["GPOS"].table.LookupList.Lookup:
        if lookup.LookupType == 4:
            out.extend(lookup.SubTable)
    return out


def extend(font, style):
    from build import SETTINGS, profile
    from rounding import circle, contours, path_from_contours, round_contour

    cmap = font.getBestCmap()
    glyf = font["glyf"]
    hmtx = font["hmtx"]
    order = list(font.getGlyphOrder())
    decisions = {}
    added = []

    def component(glyph, index):
        c = glyph.components[index]
        return c.glyphName, c.x, c.y

    def make(name, glyph, advance, reason, char=None, mark=False):
        assert name not in glyf.glyphs, name
        glyf[name] = glyph
        glyph.recalcBounds(glyf)
        hmtx[name] = (round(advance), getattr(glyph, "xMin", 0))
        order.append(name)
        font.setGlyphOrder(list(order))
        added.append((name, char, mark))
        decisions[name] = reason
        return name

    def composite(parts, flags_first=ROUND_XY):
        pen = TTGlyphPen(font.getGlyphSet())
        for base, x, y in parts:
            pen.addComponent(base, (1, 0, 0, 1, round(x), round(y)))
        glyph = pen.glyph()
        for i, c in enumerate(glyph.components):
            c.flags = (flags_first if i == 0 else ROUND_XY) | (c.flags & ~0x0207)
        return glyph

    wanted = [ch for ch in NAMES if ord(ch) not in cmap]

    # The marks.
    tonos, acute_angle, tonos_angle = _tonos_points(font)
    ty0, ty1 = tonos[0][1], tonos[1][1]
    tonos_path = _polygon(tonos)
    make(
        "tonoscomb",
        _simple(tonos_path),
        0,
        f"DINish's acute stood up from {acute_angle:.1f} to {tonos_angle:.1f} degrees,"
        " keeping its length, thickness, taper, horizontal cuts, bottom and middle.",
        mark=True,
    )
    left, right = _dieresis_dots(font)
    gap = right[0] - left[0] - (left[2] + right[2]) / 2
    # The dots stay where the dieresis has them, so ΐ and ΰ are as wide as ï
    # and ü. The tonos stands with its foot (the middle of its lowest edge) on
    # their centre line, raised in whole units until it keeps DIALYTIKA_CLEAR
    # of the dieresis's own gap from both. Spreading the dots instead put
    # them over the next letter's ascender (Αΐδα).
    clear = gap * DIALYTIKA_CLEAR
    foot = (tonos[0][0] + tonos[3][0]) / 2
    middle = (left[0] + right[0]) / 2

    def placed(lift):
        return [(x - foot + middle, y - ty0 + left[1] + lift) for x, y in tonos]

    def keeps_clear(lift):
        return all(
            _distance_to_polygon(dot[:2], placed(lift)) - dot[2] / 2 >= clear
            for dot in (left, right)
        )

    lift = 0
    while not keeps_clear(lift):
        lift += 1
    dots = [circle(*left), circle(*right)]
    dt_path = skia.Path(path_from_contours(dots))
    dt_path.addPath(_polygon(placed(lift)))
    make(
        "dieresistonoscomb",
        _simple(dt_path),
        0,
        "DINish's dieresis dots, drawn as DINDOT's circles where the dieresis has"
        f" them; the tonos between them, its foot on their centre line, raised {lift}"
        f" units to keep {clear:.0f} units clear of either.",
        mark=True,
    )

    recipes = _science_recipes(font, style)
    o_box = _outline(font, "o").computeTightBounds()
    o_center = (o_box.left() + o_box.right()) / 2
    o_shift = component(glyf["oacute"], 1)[1] - o_center

    def lower_offset(base, model, body=None):
        if model:
            name, x, y = component(glyf[model], 1)
            assert name == "acutecomb" and y == 0, (model, name)
            return x
        if base == "alpha":
            # Over the bowl: the counter's centre, related to the tonos as o's.
            coords, ends, _ = glyf["alpha"].getCoordinates(glyf)
            counter = coords[ends[0] + 1 : ends[1] + 1]
            xs = [p[0] for p in counter]
            return (min(xs) + max(xs)) / 2 + o_shift
        box = body.computeTightBounds()
        return (box.left() + box.right()) / 2 + o_shift

    for ch, (base, model) in LOWER_TONOS.items():
        if ch not in wanted:
            continue
        x = lower_offset(base, model, recipes[base][0] if base in recipes else None)
        if base in recipes:
            body, width = recipes[base]
            path = skia.Path(body)
            path.addPath(_offset(tonos_path, round(x)))
            make(
                NAMES[ch],
                _simple(path),
                width,
                f"science.py's {base} drawn on the source font, with the tonos"
                f" centred at {round(x)} as the acute sits on o.",
                ch,
            )
        else:
            make(
                NAMES[ch],
                composite(
                    [(base, 0, 0), ("tonoscomb", x, 0)], ROUND_XY | USE_MY_METRICS
                ),
                hmtx[base][0],
                f"{base} with the tonos where DINish puts the acute"
                + (f" ({model})." if model else ", over the bowl as on o."),
                ch,
            )

    # Capitals: the tonos at the upper left, its top on the cap height and its
    # left side bearing that of DINish's apostrophe. The letter moves right
    # until the space between is wide enough (below), and its foot never
    # reaches in under the tonos.
    quote = glyf["quoteright"]
    quote.recalcBounds(glyf)
    tonos_lsb = hmtx["quoteright"][1]
    stem_bearing = hmtx["H"][1]
    tx = tonos_lsb - min(p[0] for p in tonos)
    dy = CAP - ty1
    x_br, x_tr = tonos[3][0] + tx, tonos[2][0] + tx

    def whites(body):
        """The white from the tonos's right edge to the letter, on each line
        of the tonos's height where the letter has ink."""
        box = body.computeTightBounds()
        out = []
        for y in range(ty0 + dy, ty1 + dy + 1):
            edge = _left_at(body, y, box.left() - 2, box.right() + 2)
            if edge is not None:
                out.append(edge - x_br - (x_tr - x_br) * (y - ty0 - dy) / (ty1 - ty0))
        return out

    def rounded(body, name):
        """The body as build.py rounds the glyph `name`."""
        rule = profile(name, glyf)
        return path_from_contours(
            [
                round_contour(
                    c,
                    SETTINGS["radii"][style],
                    SETTINGS["inner_radius_ratio"],
                    SETTINGS["acute_radius_ratio"],
                    profile_multiplier=rule["radius_multiplier"],
                )[0]
                for c in contours(body)
            ]
        )

    # Every capital gets the white H has under the tonos, averaged over the
    # tonos's height, where H's stem comes TONOS_NEAREST of its bearing from
    # the tonos's top. (A rule per letter's nearest point set Ύ loose and Ό
    # and Ώ tight, since the tonos leans away from a stem and not from a
    # bowl.) No letter, as rounded, comes closer than TONOS_FLOOR of the
    # bearing: Y's square arm end, which the rounding takes away, does not
    # hold Ύ off.
    h_white = whites(_outline(font, "H"))
    target = sum(h_white) / len(h_white) + ceil(
        TONOS_NEAREST * stem_bearing - min(h_white)
    )
    shifts = {}
    for ch, base in UPPER_TONOS.items():
        if ch not in wanted:
            continue
        if base in recipes:
            body, width = recipes[base]
        else:
            body, width = _outline(font, base), hmtx[base][0]
        white = whites(body)
        near = whites(rounded(body, NAMES[ch] if base in recipes else base))
        shift = max(
            ceil(target - sum(white) / len(white)),
            ceil(TONOS_FLOOR * stem_bearing - min(near)),
            ceil(x_br - body.computeTightBounds().left()),
        )
        shifts[ch] = shift
        if base in recipes:
            path = _offset(body, shift)
            path.addPath(_offset(tonos_path, tx, dy))
            make(
                NAMES[ch],
                _simple(path),
                width + shift,
                f"science.py's {base} drawn on the source font and moved {shift}"
                " right for the capital tonos at the upper left.",
                ch,
            )
        else:
            make(
                NAMES[ch],
                composite([(base, shift, 0), ("tonoscomb", tx, dy)]),
                width + shift,
                f"{base} moved {shift} right; the tonos at the upper left, top on"
                f" the cap height, left bearing {tonos_lsb} as DINish's apostrophe.",
                ch,
            )

    for ch, (base, model) in DIERESIS.items():
        if ch not in wanted:
            continue
        parts = [component(glyf[model], i) for i in range(2)]
        assert parts[0][0] == base and parts[1][0] == "dieresiscmb", parts
        make(
            NAMES[ch],
            composite(parts, ROUND_XY | USE_MY_METRICS),
            hmtx[model][0],
            f"{base} with DINish's dieresis placed exactly as in {model}.",
            ch,
        )
    for ch, (base, model) in DIERESIS_TONOS.items():
        if ch not in wanted:
            continue
        first, (_, x, y) = component(glyf[model], 0), component(glyf[model], 1)
        assert first[0] == base, (model, first)
        make(
            NAMES[ch],
            composite(
                [first, ("dieresistonoscomb", x, y)],
                ROUND_XY | USE_MY_METRICS,
            ),
            hmtx[model][0],
            f"{base} with the dialytika tonos centred where {model} centres its dieresis.",
            ch,
        )

    # Spacing marks: the drawing between DINish's apostrophe side bearings.
    qa, ql = hmtx["quoteright"]
    qr = qa - ql - (quote.xMax - quote.xMin)
    for ch, mark in (("\u0384", "tonoscomb"), ("\u0385", "dieresistonoscomb")):
        if ch not in wanted:
            continue
        mark_glyph = glyf[mark]
        mark_glyph.recalcBounds(glyf)
        x = ql - mark_glyph.xMin
        make(
            NAMES[ch],
            composite([(mark, x, 0)]),
            ql + (mark_glyph.xMax - mark_glyph.xMin) + qr,
            f"The {mark} drawing, spaced like DINish's apostrophe.",
            ch,
        )
    if "\u0387" in wanted:
        # DINDOT draws the period as a circle of its square's area on the
        # baseline; raise it so its top meets the top of o.
        from build import equal_area

        period = glyf["period"]
        period.recalcBounds(glyf)
        d = 2 * round(equal_area(period.xMax - period.xMin, period.yMax - period.yMin) / 2)
        o = glyf["o"]
        o.recalcBounds(glyf)
        make(
            NAMES["\u0387"],
            composite([("period", 0, o.yMax - d)], ROUND_XY | USE_MY_METRICS),
            hmtx["period"][0],
            "DINish's period, raised so DINDOT's round dot tops out with o.",
            "\u0387",
        )
    if "\u037e" in wanted:
        make(
            NAMES["\u037e"],
            composite([("semicolon", 0, 0)], ROUND_XY | USE_MY_METRICS),
            hmtx["semicolon"][0],
            "The semicolon, its canonical equivalent.",
            "\u037e",
        )

    # Unicode mappings and glyph classes.
    for table in font["cmap"].tables:
        if table.isUnicode():
            for name, char, _ in added:
                if char:
                    table.cmap[ord(char)] = name
    if "GDEF" in font and font["GDEF"].table.GlyphClassDef:
        classes = font["GDEF"].table.GlyphClassDef.classDefs
        for name, char, mark in added:
            classes[name] = 3 if mark else 1

    # Top mark anchors: DINish gives a precomposed letter its base's anchor.
    # A base science.py draws later gets the anchor science.py will give it.
    anchored = {}
    for sub in _anchor_lookups(font):
        bases = sub.BaseCoverage.glyphs
        for name, char, mark in added:
            if not char or mark:
                continue
            model, dx = None, 0
            if char in UPPER_TONOS:
                model, dx = UPPER_TONOS[char], shifts[char]
                if model in recipes:
                    width = recipes[model][1]
                    model, dx = "O", shifts[char] + (width - hmtx["O"][0]) / 2
            elif char in LOWER_TONOS:
                model = LOWER_TONOS[char][0]
                if model in recipes:
                    model, dx = "o", (hmtx[name][0] - hmtx["o"][0]) / 2
            elif char in DIERESIS or char in DIERESIS_TONOS:
                model = (DIERESIS.get(char) or DIERESIS_TONOS[char])[1]
            if model not in bases:
                continue
            record = deepcopy(sub.BaseArray.BaseRecord[bases.index(model)])
            for anchor in record.BaseAnchor:
                if anchor is not None:
                    anchor.XCoordinate = round(anchor.XCoordinate + dx)
            bases.append(name)
            sub.BaseArray.BaseRecord.append(record)
            anchored[name] = model
        sub.BaseArray.BaseCount = len(sub.BaseArray.BaseRecord)
    for name, model in anchored.items():
        decisions[name] += f" Mark anchors from {model}."

    # Kerning: share the Latin classes where the side is the same shape.
    names = {char: name for name, char, _ in added if char}
    sides = [(KERN_BOTH, True, True), (KERN_RIGHT, False, True), (KERN_LEFT, True, False)]
    pairs = [
        (names.get(c) or cmap[ord(c)], m, left, right)
        for table, left, right in sides
        for c, m in table.items()
        if c in names or ord(c) in cmap
    ]
    for name, model, left, right in pairs:
        copy_kerning(font, name, model, left=left, right=right)
        if name in decisions:
            side = "" if left and right else " on its right side" if right else " on its left side"
            decisions[name] += f" Kerns as {model}{side}."
    return decisions
