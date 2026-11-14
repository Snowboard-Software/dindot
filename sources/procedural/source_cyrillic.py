"""Cyrillic for Kazakh, Uzbek, Tajik, Azerbaijani, Tatar and Bashkir, drawn
from DINish's own parts.

extend(font, style) adds the letters DINish lacks to a DINish master that was
just loaded, before DINDOT rounds it, so rounding, spacing, italics and hinting
treat them like DINish's own glyphs. Every measure is read from the master
itself, so each weight gets its own strokes. It returns {glyph name: decision}.

- Қ Ң Ҳ Җ Ҷ and their lowercase: the letter and DINish's own Ц (or ц) corner
  as one square-cornered outline: the foot run out past the right stem and
  the descender below it, with Ц's width and depth. On a vertical stem the
  corner stands where it stands on Ц. A diagonal leg (К, Х, Ж) has no stem
  edge, so the corner stands on the middle of the leg's outer edge within
  the foot's height, with Ц's own reach past it.
- Ҙ Ҫ ҙ ҫ: a short upright tail centred below the bowl, as PT Sans draws it,
  as wide as DINish's cedilla where it meets the bowl and as deep as Ц's
  descender. (Noto Sans draws a cedilla here; the brief chose PT Sans.)
- Ғ ғ: Г with the bar DINish puts across the stem of Đ, standing out left
  of the stem as far as Ħ's (Đ's longer stub moved Г right and left a hole
  before it), г with the bar of ħ; Ұ: Ү with the upper bar of ¥, its top at
  the fork; ұ: the same bar across ү's descender just below the baseline, as
  Noto Sans and PT Sans draw it (ү forks so low that a bar at the fork stood
  on the baseline). Every bar has the weight of DINish's crossbar (H for
  capitals, н for lowercase).
- Һ: Ч turned 180 degrees, which is the h shape at cap height with capital
  stems; һ is the Latin h (a composite).
- Ә ә: ә is DINish's e turned 180 degrees; Ә is the capital e that DINish's
  own parts give (Є below its bar, O above it, the bar run out to the right
  side as e runs it), turned the same way. DINish has no Latin Ə ə to reuse.
- Ҹ ҹ: Ч with an upright stroke across its bar, as wide as the stroke of $
  (it grows with the weight; ¢'s does not) but no more than STROKE_SHARE of
  the counter, half the letter's height long and centred on the bar, as Noto
  Sans and PT Sans cover 44 to 61% of it.
- Ҡ ҡ (Bashkir, beyond the requested list: Башҡортостан needs it): К with
  the arm of Ъ. Т and Г end their bars almost where the arm of Ҡ and Ъ
  begins, so those pairs kern apart (KERN_APART).
- Ӣ ӣ Ӯ ӯ: DINish's macron over и and у, where DINish puts its marks on them.

PROFILE_BASES names, for each new letter, the DINish letter whose rounding
and spacing profile it should follow; build.py and build_text.py find those
only through NFD and single-component composites, which these letters are
not (see its comment).
"""

from copy import deepcopy
from math import ceil

import skia
from fontTools.misc.roundTools import noRound, otRound
from fontTools.pens.basePen import BasePen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from shapely.geometry import Polygon

from kerning import add_pair_lookup, copy_kerning

# The DINish letter each new letter is made from, for the rounding profile
# (build.py profile(), settings.json glyph_profile_aliases) and the optical
# spacing profile (build_text.py glyph_info()). Without it the letters take
# the defaults: radius 1 where К rounds at 0.8, Х and Ж at 0.75, Ч and Ү as Y,
# С and с at 0.9, е at 0.85; spacing 1.01 and 20 where С, с, О and е have
# their own. Ӣ ӣ Ӯ ӯ and һ find theirs already (NFD, a one-part composite).
PROFILE_BASES = {
    "Kadescendercyrillic": "Kacyr",
    "kadescendercyrillic": "kacyr",
    "Endescendercyrillic": "Encyr",
    "endescendercyrillic": "encyr",
    "Hadescendercyrillic": "Hacyr",
    "hadescendercyrillic": "hacyr",
    "Chedescendercyrillic": "Checyr",
    "chedescendercyrillic": "checyr",
    "Zhedescendercyrillic": "Zhecyr",
    "zhedescendercyrillic": "zhecyr",
    "Zedescendercyrillic": "Zecyr",
    "zedescendercyrillic": "zecyr",
    "Esdescendercyrillic": "Escyr",
    "esdescendercyrillic": "escyr",
    "Ghestrokecyrillic": "Gecyr",
    "ghestrokecyrillic": "gecyr",
    "Ustraightstrokecyrillic": "Ustraightcyrillic",
    "ustraightstrokecyrillic": "ustraightcyrillic",
    "Shhacyrillic": "Checyr",
    "Schwacyrillic": "Ocyr",
    "schwacyrillic": "iecyr",
    "Cheverticalstrokecyrillic": "Checyr",
    "cheverticalstrokecyrillic": "checyr",
    "Kabashkircyrillic": "Kacyr",
    "kabashkircyrillic": "kacyr",
}
# A new letter whose shape is its source letter's on both sides takes that
# letter's kerning. DINish kerns no Cyrillic letter, so only һ (the Latin h)
# has classes to join.
KERN_AS = {"shhacyrillic": "h"}
# Letters whose top bar ends at the right, and letters whose arm starts at the
# left on the same line: as set, ТҠ and ТЪ met in one bar (тҡ, the Bashkir
# ятҡан, тотҡан). Each pair kerns apart until BAR_GAP of white stands between
# them, as in Noto Sans (28 to 33 thousandths) and PT Sans (23 to 30).
KERN_APART = (("ТГҐҒ", "ҠЪ"), ("тгґғ", "ҡъ"))
BAR_GAP = 0.028
# The stroke of Ҹ ҹ takes at most this share of the counter between Ч's arm
# and stem, as in Noto Sans Bold (0.40) and PT Sans Bold (0.41): $'s stroke
# left Bold ч too little white beside it for the bar's fillets.
STROKE_SHARE = 0.4

# ---------------------------------------------------------------- outlines


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
        raise ValueError("cubic in a DINish outline")

    def _closePath(self):
        self.path.close()

    def _endPath(self):
        pass


def _outline(font, name):
    glyph_set = font.getGlyphSet()
    pen = _SkiaPen(glyph_set)
    glyph_set[name].draw(pen)
    return pen.path


def _rect(x0, y0, x1, y1):
    p = skia.Path()
    p.addRect(skia.Rect.MakeLTRB(x0, y0, x1, y1))
    return p


def _op(a, b, op):
    out = skia.Op(a, b, op)
    assert out is not None, "path operation failed"
    return out


def _union(*paths):
    out = skia.Path()
    for p in paths:
        out = _op(out, p, skia.PathOp.kUnion_PathOp)
    return out


def _clip(path, x0, y0, x1, y1):
    return _op(path, _rect(x0, y0, x1, y1), skia.PathOp.kIntersect_PathOp)


def _move(path, dx):
    out = skia.Path(path)
    out.transform(skia.Matrix.MakeAll(1, 0, dx, 0, 1, 0, 0, 0, 1))
    return out


def _turn(path, cx2, cy2):
    """The path turned 180 degrees about (cx2 / 2, cy2 / 2)."""
    out = skia.Path(path)
    out.transform(skia.Matrix.MakeAll(-1, 0, cx2, 0, -1, cy2, 0, 0, 1))
    return out


def _bounds(path):
    b = path.computeTightBounds()
    return b.left(), b.top(), b.right(), b.bottom()


def _runs(path, y, x0=-300, x1=1400):
    """Horizontal ink runs of a path at height y, to the unit."""
    runs = []
    for x in range(x0, x1):
        if path.contains(x + 0.5, y):
            if runs and runs[-1][1] == x:
                runs[-1][1] = x + 1
            else:
                runs.append([x, x + 1])
    return runs


def _column(path, x, y0=-400, y1=1200):
    """Vertical ink runs of a path at x, to the unit."""
    runs = []
    for y in range(y0, y1):
        if path.contains(x, y + 0.5):
            if runs and runs[-1][1] == y:
                runs[-1][1] = y + 1
            else:
                runs.append([y, y + 1])
    return runs


def _contours(path):
    """Closed contours of a skia path as [("M"|"L"|"Q", points)]."""
    out, cur = [], None
    it = skia.Path.Iter(path, True)
    while True:
        verb, pts = it.next()
        if verb == skia.Path.kDone_Verb:
            break
        if verb == skia.Path.kMove_Verb:
            cur = [("M", [(pts[0].x(), pts[0].y())])]
            out.append(cur)
        elif verb == skia.Path.kLine_Verb:
            cur.append(("L", [(pts[1].x(), pts[1].y())]))
        elif verb == skia.Path.kQuad_Verb:
            cur.append(("Q", [(pts[1].x(), pts[1].y()), (pts[2].x(), pts[2].y())]))
        elif verb == skia.Path.kConic_Verb:
            quads = skia.Path.ConvertConicToQuads(
                pts[0], pts[1], pts[2], it.conicWeight(), 3
            )
            for i in range(1, len(quads), 2):
                cur.append(
                    (
                        "Q",
                        [
                            (quads[i].x(), quads[i].y()),
                            (quads[i + 1].x(), quads[i + 1].y()),
                        ],
                    )
                )
        elif verb == skia.Path.kCubic_Verb:
            raise ValueError("cubic in a Cyrillic outline")
    return [c for c in out if len(c) > 2]


def _polygon(contour, steps=12):
    pts = [contour[0][1][0]]
    for verb, p in contour[1:]:
        if verb == "L":
            pts.append(p[0])
        else:
            a, (c, e) = pts[-1], p
            for k in range(1, steps + 1):
                t = k / steps
                pts.append(
                    (
                        (1 - t) ** 2 * a[0] + 2 * (1 - t) * t * c[0] + t * t * e[0],
                        (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * c[1] + t * t * e[1],
                    )
                )
    return pts


def _area(pts):
    return sum(a[0] * b[1] - a[1] * b[0] for a, b in zip(pts, pts[1:] + pts[:1])) / 2


def _snap(p):
    """Float noise off a coordinate that is meant to be whole: skia computes in
    single precision, and DINish's own points are all whole units."""
    return tuple(float(round(v)) if abs(v - round(v)) < 2e-3 else v for v in p)


def _reverse(contour):
    nodes = [contour[0][1][0]]
    segs = []
    for verb, p in contour[1:]:
        segs.append((verb, nodes[-1], p))
        nodes.append(p[-1])
    out = [("M", [nodes[-1]])]
    for verb, start, p in reversed(segs):
        out.append(("L", [start]) if verb == "L" else ("Q", [p[0], start]))
    return out


def _straight(a, b, c):
    """b lies on the line from a to c, between them."""
    cross = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    ahead = (b[0] - a[0]) * (c[0] - b[0]) + (b[1] - a[1]) * (c[1] - b[1])
    return (
        abs(cross) < 1e-3 * max(1.0, abs(c[0] - a[0]) + abs(c[1] - a[1])) and ahead > 0
    )


def _tidy(contour):
    """Snap float noise, drop segments shorter than a unit, make a curve whose
    control point lies on its chord a line, and merge lines that run straight
    on, so rounding sees DINish's own kind of outline: no point that is not a
    corner or a curve's end."""
    start = _snap(contour[0][1][0])
    segs = []  # cyclic: (kind, control, end); the last one ends at start
    for verb, p in contour[1:]:
        p = [_snap(q) for q in p]
        segs.append(("L", None, p[0]) if verb == "L" else ("Q", p[0], p[1]))
    if segs[-1][2] != start:
        segs.append(("L", None, start))
    out = []
    prev = start
    for kind, ctrl, end in segs:
        if abs(end[0] - prev[0]) + abs(end[1] - prev[1]) < 1.0 and end != start:
            continue
        if kind == "Q" and _straight(prev, ctrl, end):
            kind, ctrl = "L", None
        out.append((kind, ctrl, end))
        prev = end
    changed = True
    while changed and len(out) > 3:
        changed = False
        n = len(out)
        for i in range(n):
            a = out[i - 1][2]
            here, after = out[i], out[(i + 1) % n]
            if here[0] == "L" and after[0] == "L" and _straight(a, here[2], after[2]):
                del out[i]
                changed = True
                break
    # start the contour on its first remaining node
    first = out[-1][2]
    result = [("M", [first])]
    for kind, ctrl, end in out:
        result.append(("L", [end]) if kind == "L" else ("Q", [ctrl, end]))
    # the final segment returns to `first`, which TrueType closes implicitly
    if result[-1][0] == "L":
        result.pop()
    return result


def _glyph(path):
    """A TrueType glyph from a skia path: overlaps removed, outer contours
    clockwise, coordinates kept to the fraction (build.py keeps its own until
    the finer export grid rounds them)."""
    cs = [_tidy(c) for c in _contours(skia.Simplify(path))]
    polys = [Polygon(_polygon(c)) for c in cs]
    pen = TTGlyphPen(None)
    for i, c in enumerate(cs):
        p = polys[i]
        if p.is_empty or p.area < 1:
            continue
        depth = sum(
            q.area > p.area and q.contains(p.representative_point())
            for j, q in enumerate(polys)
            if j != i
        )
        clockwise = depth % 2 == 0
        if (_area(_polygon(c, 4)) < 0) != clockwise:
            c = _reverse(c)
        pen.moveTo(c[0][1][0])
        for verb, p in c[1:]:
            if verb == "L":
                pen.lineTo(p[0])
            else:
                pen.qCurveTo(*p)
        pen.closePath()
    return pen.glyph(round=noRound)


def _composite(font, parts, metrics=0):
    """A composite of DINish glyphs; the first part gives the metrics, as in
    DINish's own composites."""
    pen = TTGlyphPen(font.getGlyphSet())
    for name, x, y in parts:
        pen.addComponent(name, (1, 0, 0, 1, x, y))
    glyph = pen.glyph()
    for i, component in enumerate(glyph.components):
        component.flags = 0x204 if i == metrics else 0x4
    return glyph


def _turned_glyph(font, name, cx2, cy2):
    """DINish's own outline turned 180 degrees, point for point (a turn keeps
    every point whole and every contour's direction)."""
    glyph = deepcopy(font["glyf"][name])
    assert not glyph.isComposite()
    coords = glyph.coordinates
    for i in range(len(coords)):
        x, y = coords[i]
        coords[i] = (cx2 - x, cy2 - y)
    return glyph


# ---------------------------------------------------------------- measures


def _stems(path, y):
    """The ink runs at height y, as (left, right) pairs."""
    return [tuple(r) for r in _runs(path, y)]


def _nearest(runs, middle):
    """The run whose middle lies nearest `middle`."""
    return min(runs, key=lambda r: (abs((r[0] + r[1]) / 2 - middle), r[0]))


def _edge_top(path, x, y):
    """The top of the outline's vertical edge at x that passes height y."""
    best = None
    for contour in _contours(path):
        prev = contour[0][1][0]
        for verb, pts in contour[1:] + [("L", [contour[0][1][0]])]:
            end = pts[-1]
            if (
                verb == "L"
                and abs(prev[0] - x) < 0.01
                and abs(end[0] - x) < 0.01
                and min(prev[1], end[1]) <= y <= max(prev[1], end[1])
            ):
                best = max(prev[1], end[1])
            prev = end
    assert best is not None, (x, y)
    return best


class _Parts:
    """Per-weight parts and measures, read from this DINish master."""

    def __init__(self, font):
        self.font = font
        self.cap = font["OS/2"].sCapHeight
        self.top = {"uc": self.cap, "lc": font["glyf"]["encyr"].yMax}
        self.corner = {
            "uc": self._corner("Tsecyr", "uc"),
            "lc": self._corner("tsecyr", "lc"),
        }
        self.crossbar = {
            "uc": self._crossbar("H", "uc"),
            "lc": self._crossbar("encyr", "lc"),
        }

    def _corner(self, name, case):
        """Ц's corner: the bottom of its right stem, its foot run out past the
        stem and the descender, cut off at the top of the foot."""
        path = _outline(self.font, name)
        top = self.top[case]
        stems = _stems(path, top * 0.85)
        left, right = stems[-1]
        foot = _column(path, (stems[0][1] + left) / 2)[0][1]
        depth = _bounds(path)[1]
        desc = _stems(path, depth / 2)[-1]
        return {
            "path": _clip(path, left, depth - 1, 4000, foot),
            "stem": (left, right),
            "foot": foot,
            "depth": depth,
            "descender": desc,
            "width": desc[1] - desc[0],
            "reach": desc[1] - right,
            "bearing": self.font["hmtx"][name][0] - desc[1],
        }

    def _crossbar(self, name, case):
        """(bottom, top) of the crossbar of H or н."""
        path = _outline(self.font, name)
        b = _bounds(path)
        top = self.top[case]
        runs = [r for r in _column(path, (b[0] + b[2]) / 2) if 0 < r[0] and r[1] < top]
        return tuple(_nearest(runs, top / 2))

    def stem(self, path, case, index, at=0.85):
        """A vertical stem of the path: the index-th run at `at` of the
        letter's height (high, above any crossbar, unless told otherwise)."""
        return _stems(path, self.top[case] * at)[index]


# ---------------------------------------------------------------- letters


def _descender_letter(font, parts, base, case, diagonal):
    """The base letter and Ц's corner as one outline. On a vertical stem the
    corner stands as it stands on Ц, its stem on the base's right stem. A
    diagonal leg has no stem edge to stand on: within the height of Ц's foot
    its outer edge runs from the toe in towards the letter, and the corner
    stands on that edge's middle, with Ц's own reach past it. (Ц's reach from
    the toe itself spread the letters; this lands between PT Sans and Noto
    Sans in every weight.) The foot never starts left of the toe."""
    c = parts.corner[case]
    path = _outline(font, base)
    piece = c["path"]
    if diagonal:
        toe = _stems(path, 0.5)[-1]
        leg = _stems(path, c["foot"] - 0.5)[-1]
        dx = (toe[1] + leg[1]) / 2 - c["stem"][1]
        piece = _clip(_move(piece, dx), toe[0], c["depth"] - 1, 4000, c["foot"])
        assert toe[0] <= leg[1], (base, "the foot must reach into the leg")
    else:
        stem = parts.stem(path, case, -1)
        assert abs((stem[1] - stem[0]) - (c["stem"][1] - c["stem"][0])) <= 2, (
            base,
            stem,
        )
        dx = stem[0] - c["stem"][0]
        piece = _move(piece, dx)
    out = _union(path, piece)
    advance = max(font["hmtx"][base][0], otRound(c["descender"][1] + dx + c["bearing"]))
    return out, advance


def _centred_descender(font, parts, base, case):
    """The bowl and a short upright tail centred on its lowest point, rising
    into the middle of its bottom stroke: as wide as DINish's cedilla where
    it meets the bowl (DINish's own tail under a bowl, about three quarters
    of a stem, as PT Sans draws this tail), as deep as Ц's descender."""
    c = parts.corner[case]
    path = _outline(font, base)
    glyph = font["glyf"][base]
    coords, _, flags = glyph.getCoordinates(font["glyf"])
    middle = (glyph.xMin + glyph.xMax) / 2
    low = min(
        (coords[i] for i in range(len(coords)) if flags[i] & 1),
        key=lambda p: (p[1], abs(p[0] - middle)),
    )
    cx = low[0]
    stroke = _column(path, cx)[0]
    cedilla = _outline(font, "cedillacmb")
    top = _stems(cedilla, _bounds(cedilla)[3] - 1)[0]
    w = top[1] - top[0]
    tail = _rect(cx - w / 2, c["depth"], cx + w / 2, (stroke[0] + stroke[1]) / 2)
    return _union(path, tail), font["hmtx"][base][0]


def _stem_bar(font, parts, name, case):
    """Where DINish's barred letter `name` (Đ, ħ) crosses its left stem: the
    bar's bottom and top, its overhang left of the stem, its reach right of
    it and its left side bearing."""
    path = _outline(font, name)
    stem = parts.stem(path, case, 0, at=0.25)
    # the bar is the only ink just left of the stem
    (y0, y1) = _column(path, stem[0] - 1)[0]
    row = _stems(path, (y0 + y1) / 2)[0]
    return {
        "bar": (y0, y1),
        "over": stem[0] - row[0],
        "reach": row[1] - stem[1],
        "bearing": row[0],
    }


def _fork(path, stem, y):
    """The top of a Y's plain stem: the higher of the two points where the
    arms leave its sides."""
    return max(_edge_top(path, stem[0], y), _edge_top(path, stem[1], y))


def _yen_overhang(font):
    """How far the upper bar of DINish's ¥ reaches out past its stem. Rows
    from the foot up are the plain stem or one run wider than it (a bar, and
    above the upper bar the arms' junction, until the arms part); the upper
    bar is the foot of the last such band."""
    yen = _outline(font, "yen")
    stem = _stems(yen, 1)[0]
    foot = None
    y = 1
    while True:
        runs = _stems(yen, y + 0.5)
        if len(runs) != 1:
            break
        if runs[0] != stem and _stems(yen, y - 0.5)[0] == stem:
            foot = runs[0]
        y += 1
    return stem[0] - foot[0]


def _bar_letter(font, base, bar, shift=0):
    """The base letter moved right by `shift` and a crossbar (x0, y0, x1, y1)."""
    path = _move(_outline(font, base), shift)
    return _union(path, _rect(*bar)), font["hmtx"][base][0] + shift


def _letters(font):
    """[(codepoint, name, glyph, advance, decision, anchor source)] for every
    letter, in the order they are added. The anchor source is the DINish
    glyph whose mark anchors the letter takes, how ("move" by an x shift, or
    "turn" in a box of that width) and by how much; None for no anchors."""
    parts = _Parts(font)
    gl = font["glyf"]
    hm = font["hmtx"]
    out = []

    # -- Қ Ң Ҳ Ҷ Җ: Ц's corner on the right foot
    for cp, name, base, case, diagonal in (
        (0x049A, "Kadescendercyrillic", "Kacyr", "uc", True),
        (0x049B, "kadescendercyrillic", "kacyr", "lc", True),
        (0x04A2, "Endescendercyrillic", "Encyr", "uc", False),
        (0x04A3, "endescendercyrillic", "encyr", "lc", False),
        (0x04B2, "Hadescendercyrillic", "Hacyr", "uc", True),
        (0x04B3, "hadescendercyrillic", "hacyr", "lc", True),
        (0x04B6, "Chedescendercyrillic", "Checyr", "uc", False),
        (0x04B7, "chedescendercyrillic", "checyr", "lc", False),
        (0x0496, "Zhedescendercyrillic", "Zhecyr", "uc", True),
        (0x0497, "zhedescendercyrillic", "zhecyr", "lc", True),
    ):
        path, adv = _descender_letter(font, parts, base, case, diagonal)
        tse = "Ц" if case == "uc" else "ц"
        where = (
            f"standing on the middle of the right leg's outer edge within the foot's height, with {tse}'s reach past it"
            if diagonal
            else f"on the right stem, where {tse} carries it"
        )
        out.append(
            (
                cp,
                name,
                _glyph(path),
                adv,
                f"{base} and {tse}'s foot and descender as one outline, {where}.",
                (base, "move", 0),
            )
        )

    # -- Ҙ Ҫ: a short descender centred below the bowl
    for cp, name, base, case in (
        (0x0498, "Zedescendercyrillic", "Zecyr", "uc"),
        (0x0499, "zedescendercyrillic", "zecyr", "lc"),
        (0x04AA, "Esdescendercyrillic", "Escyr", "uc"),
        (0x04AB, "esdescendercyrillic", "escyr", "lc"),
    ):
        path, adv = _centred_descender(font, parts, base, case)
        tse = "Ц" if case == "uc" else "ц"
        out.append(
            (
                cp,
                name,
                _glyph(path),
                adv,
                f"{base} and a short descender centred below the bowl, as PT Sans draws it: the weight of DINish's cedilla where it meets the bowl, stood upright under the bowl's lowest point, to {tse}'s depth.",
                (base, "move", 0),
            )
        )

    # -- Ғ ғ: Г with the bar of Đ and the stub of Ħ, г with the bar of ħ
    for cp, name, base, barred, stub, case in (
        (0x0492, "Ghestrokecyrillic", "Gecyr", "Eth", "Hbar", "uc"),
        (0x0493, "ghestrokecyrillic", "gecyr", "hbar", "hbar", "lc"),
    ):
        b = _stem_bar(font, parts, barred, case)
        left = _stem_bar(font, parts, stub, case)
        stem = parts.stem(_outline(font, base), case, 0, at=0.25)
        shift = max(0, left["bearing"] - (stem[0] - left["over"]))
        y0, y1 = parts.crossbar[case]
        mid = (b["bar"][0] + b["bar"][1]) / 2 if case == "uc" else (y0 + y1) / 2
        h = y1 - y0
        bar = (
            stem[0] + shift - left["over"],
            mid - h / 2,
            stem[1] + shift + b["reach"],
            mid + h / 2,
        )
        path, adv = _bar_letter(font, base, bar, shift)
        mark = "Đ (its reach right of the stem), with Ħ's overhang and side bearing left of it" if case == "uc" else "ħ (its overhang, reach and side bearing)"
        hn = "H" if case == "uc" else "н"
        height = "at Đ's height" if case == "uc" else "at н's crossbar height"
        out.append(
            (
                cp,
                name,
                _glyph(path),
                adv,
                f"{base} with the bar DINish puts across the stem of {mark}, {height}, as thick as {hn}'s crossbar.",
                (base, "move", shift),
            )
        )

    # -- Ұ ұ: Ү with the upper bar of ¥, at the fork
    y_over = _yen_overhang(font)
    spans = {}
    for case, base in (("uc", "Ustraightcyrillic"), ("lc", "ustraightcyrillic")):
        p = _outline(font, base)
        top = _bounds(p)[3]
        r = _stems(p, top - 0.5)
        spans[case] = r[-1][1] - r[0][0]
    for cp, name, base, case in (
        (0x04B0, "Ustraightstrokecyrillic", "Ustraightcyrillic", "uc"),
        (0x04B1, "ustraightstrokecyrillic", "ustraightcyrillic", "lc"),
    ):
        p = _outline(font, base)
        low = _bounds(p)[1]
        stem = _stems(p, low + 1)[0]
        fork = _fork(p, stem, low + 1)
        y0, y1 = parts.crossbar[case]
        over = y_over * spans[case] / spans["uc"]
        top = fork if case == "uc" else 0
        bar = (stem[0] - over, top - (y1 - y0), stem[1] + over, top)
        path, adv = _bar_letter(font, base, bar)
        letter = "Ү" if case == "uc" else "ү"
        hn = "H" if case == "uc" else "н"
        where = (
            "its top at the fork"
            if case == "uc"
            else "across the descender, its top on the baseline, its overhang in ү's proportion to Ү"
        )
        out.append(
            (
                cp,
                name,
                _glyph(path),
                adv,
                f"{letter} with the upper bar of DINish's ¥: {where}, as thick as {hn}'s crossbar.",
                (base, "move", 0),
            )
        )

    # -- Һ һ
    adv = hm["Checyr"][0]
    out.append(
        (
            0x04BA,
            "Shhacyrillic",
            _turned_glyph(font, "Checyr", adv, parts.cap),
            adv,
            "Ч turned 180 degrees in its own advance: the h shape at cap height, with Ч's capital stems, bowl and width.",
            None,
        )
    )
    out.append(
        (
            0x04BB,
            "shhacyrillic",
            _composite(font, [("h", 0, 0)]),
            hm["h"][0],
            "The Latin h, as a composite, as DINish makes н and х of H and x; it takes h's kerning.",
            ("h", "move", 0),
        )
    )

    # -- Ә ә
    e = gl["e"]
    out.append(
        (
            0x04D9,
            "schwacyrillic",
            _turned_glyph(font, "e", e.xMin + e.xMax, e.yMin + e.yMax),
            hm["e"][0],
            "DINish's e turned 180 degrees in its own box.",
            ("e", "turn", e.xMin + e.xMax),
        )
    )
    ukr = _outline(font, "Eukrcyr")
    o = _outline(font, "O")
    ub = _bounds(ukr)
    bar = _nearest(
        [
            r
            for r in _column(ukr, ub[0] + 0.3 * (ub[2] - ub[0]))
            if 0 < r[0] and r[1] < parts.cap
        ],
        parts.cap / 2,
    )
    split = (bar[0] + bar[1]) / 2
    sides = _stems(o, split)
    capital_e = _union(
        _clip(ukr, -4000, -4000, 4000, split),
        _clip(o, -4000, split, 4000, 4000),
        _rect((sides[0][0] + sides[0][1]) / 2, bar[0], sides[-1][1], bar[1]),
    )
    ob = gl["O"]
    out.append(
        (
            0x04D8,
            "Schwacyrillic",
            _glyph(_turn(capital_e, ob.xMin + ob.xMax, ob.yMin + ob.yMax)),
            hm["O"][0],
            "A capital e of DINish's parts turned 180 degrees in O's box: Є below its bar, O above it, the bar run out to the right side as e runs it.",
            ("Ocyr", "turn", ob.xMin + ob.xMax),
        )
    )

    # -- Ҹ ҹ: an upright stroke across Ч's bar: the stroke of $
    dollar = _outline(font, "dollar")
    run = _stems(dollar, _bounds(dollar)[3] - 1)[0]
    for cp, name, base, case in (
        (0x04B8, "Cheverticalstrokecyrillic", "Checyr", "uc"),
        (0x04B9, "cheverticalstrokecyrillic", "checyr", "lc"),
    ):
        path = _outline(font, base)
        arm, stem = parts.stem(path, case, 0), parts.stem(path, case, -1)
        cx = (arm[1] + stem[0]) / 2
        width = min(run[1] - run[0], STROKE_SHARE * (stem[0] - arm[1]))
        bar = _column(path, cx)[0]
        cy, half = (bar[0] + bar[1]) / 2, parts.top[case] / 4
        stroke = _rect(cx - width / 2, cy - half, cx + width / 2, cy + half)
        letter = "Ч" if case == "uc" else "ч"
        out.append(
            (
                cp,
                name,
                _glyph(_union(path, stroke)),
                hm[base][0],
                f"{letter} with an upright stroke across its bar, in the middle of the counter: as wide as the stroke of DINish's $ (at most {STROKE_SHARE:.0%} of the counter), half {letter}'s height long and centred on the bar.",
                (base, "move", 0),
            )
        )

    # -- Ҡ ҡ: К with the arm of Ъ
    for cp, name, base, hard, case in (
        (0x04A0, "Kabashkircyrillic", "Kacyr", "Hardcyr", "uc"),
        (0x04A1, "kabashkircyrillic", "kacyr", "hardcyr", "lc"),
    ):
        top = parts.top[case]
        hp = _outline(font, hard)
        hst = _stems(hp, top * 0.75)[0]
        arm = _clip(hp, -4000, top * 0.75, hst[1], 4000)
        kp = _outline(font, base)
        shift = hst[0] - parts.stem(kp, case, 0)[0]
        path = _union(_move(kp, shift), arm)
        letter, sign = ("К", "Ъ") if case == "uc" else ("к", "ъ")
        out.append(
            (
                cp,
                name,
                _glyph(path),
                hm[base][0] + shift,
                f"{letter} with the arm of {sign}, moved right by the arm's length as {sign}'s stem stands.",
                (base, "move", shift),
            )
        )

    # -- Ӣ ӣ Ӯ ӯ: the macron where DINish centres its other marks on и and у
    macron_y = gl["Amacron"].components[1].y
    for cp, name, short, y in (
        (0x04E2, "Imacroncyrillic", "Ishortcyr", macron_y),
        (0x04E3, "imacroncyrillic", "ishortcyr", 0),
        (0x04EE, "Umacroncyrillic", "Ushortcyr", macron_y),
        (0x04EF, "umacroncyrillic", "ushortcyr", 0),
    ):
        base, mark = gl[short].components
        out.append(
            (
                cp,
                name,
                _composite(font, [(base.glyphName, 0, 0), ("macroncmb", mark.x, y)]),
                hm[base.glyphName][0],
                f"{base.glyphName} and DINish's macron, centred where DINish centres the breve of {short}, as high as DINish's other macrons.",
                None,
            )
        )
    return out


def _anchors(font, letters):
    """Mark anchors for the new letters, in DINish's own mark lookups, where
    the letter they are made from has one: moved with it, or mirrored with a
    turned letter. DINish's anchors on Ж and ж disagree between its weights
    (x 416 and 872 on Ж, 778 and 647 on ж), so Җ and җ take none; a letter
    that already carries a mark takes none, as in DINish, and a letter with a
    new descender takes no anchor for marks below."""
    gpos = font["GPOS"].table
    gid = {g: i for i, g in enumerate(font.getGlyphOrder())}
    for lookup in gpos.LookupList.Lookup:
        if lookup.LookupType != 4:
            continue
        for sub in lookup.SubTable:
            bases = dict(zip(sub.BaseCoverage.glyphs, sub.BaseArray.BaseRecord))
            below = all(r.MarkAnchor.YCoordinate <= 0 for r in sub.MarkArray.MarkRecord)
            added = []
            for cp, name, glyph, advance, decision, source in letters:
                if (
                    source is None
                    or source[0] not in bases
                    or source[0] in ("Zhecyr", "zhecyr")
                ):
                    continue
                if below and "descender" in name:
                    continue  # the new descender is where a mark below would go
                src, kind, value = source
                record = deepcopy(bases[src])
                for anchor in record.BaseAnchor:
                    if anchor is None:
                        continue
                    anchor.Format = 1
                    for attr in ("XDeviceTable", "YDeviceTable", "AnchorPoint"):
                        if hasattr(anchor, attr):
                            delattr(anchor, attr)
                    x = anchor.XCoordinate
                    anchor.XCoordinate = x + value if kind == "move" else value - x
                added.append((gid[name], name, record))
            for _, name, record in sorted(added):
                sub.BaseCoverage.glyphs.append(name)
                sub.BaseArray.BaseRecord.append(record)
            sub.BaseArray.BaseCount = len(sub.BaseArray.BaseRecord)


def _kerning(font, letters):
    """A new letter whose shape is its source letter's on both sides (һ, the
    Latin h) takes that letter's kerning classes and pairs. DINish kerns no
    Cyrillic letter, so the others have no class to join. The KERN_APART
    pairs get a lookup of their own, sized on this master to BAR_GAP of white
    once build_text keeps its share of every kern."""
    from build_text import KERNING_KEPT

    names = {r[1] for r in letters}
    for name, base in KERN_AS.items():
        if name in names:
            copy_kerning(font, name, base)
    cmap = font.getBestCmap()
    glyf, hmtx = font["glyf"], font["hmtx"]
    target = BAR_GAP * font["head"].unitsPerEm
    pairs = {}
    for lefts, rights in KERN_APART:
        for a in lefts:
            for b in rights:
                first, second = cmap[ord(a)], cmap[ord(b)]
                glyf[first].recalcBounds(glyf)
                glyf[second].recalcBounds(glyf)
                gap = hmtx[first][0] - glyf[first].xMax + glyf[second].xMin
                kern = ceil((target - gap) / KERNING_KEPT)
                if kern > 0:
                    pairs[(first, second)] = kern
    add_pair_lookup(font, pairs)
    return pairs


def extend(font, style):
    """Add the letters to a freshly loaded DINish master; return
    {glyph name: decision}."""
    cmap = font.getBestCmap()
    letters = [r for r in _letters(font) if r[0] not in cmap]
    order = list(font.getGlyphOrder())
    decisions = {}
    for cp, name, glyph, advance, decision, _ in letters:
        assert name not in font["glyf"].glyphs, name
        order.append(name)
        font.setGlyphOrder(list(order))
        font["glyf"][name] = glyph
        glyph.recalcBounds(font["glyf"])
        font["hmtx"][name] = (int(advance), otRound(getattr(glyph, "xMin", 0)))
        decisions[name] = decision
    for table in font["cmap"].tables:
        if table.isUnicode():
            for cp, name, *_ in letters:
                table.cmap[cp] = name
    if "GDEF" in font and font["GDEF"].table.GlyphClassDef:
        defs = font["GDEF"].table.GlyphClassDef.classDefs
        for cp, name, *_ in letters:
            defs[name] = 1
    _anchors(font, letters)
    for (first, second), kern in _kerning(font, letters).items():
        if second in decisions:
            decisions[second] += f" Kerns {kern} units apart after {first}."
    font["OS/2"].recalcUnicodeRanges(font)
    return decisions
