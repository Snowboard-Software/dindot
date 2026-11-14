"""Vietnamese for DINDOT, drawn from DINish's own parts.

extend(font, style) adds the Vietnamese letters DINish lacks to a DINish master
that was just loaded, before DINDOT rounds it, so rounding, spacing, italics and
hinting treat them like DINish's own glyphs. Every measure is read from the
master itself, so each weight gets its own strokes. It returns
{glyph name: decision}.

- hookabovecomb (U+0309): DINish's question mark without its dot, scaled to
  mark size and grown back to the breve's stroke, its stem cut away level.
  Vietnamese guidance asks for a hook smaller than the question mark with its
  stem truncated.
- Ơ ơ Ư ư: the letter and its horn as one square-cornered outline. The horn
  turns up through DINish's own o quarter (outer and inner curves), at the
  weight of the f's arm, and ends in a flat cut leaning 12 degrees, like DIN's
  terminals. U and u carry it from the top of the right stem, O and o from the
  shoulder; all four horn tops stand the same height above the letter, as the
  guidance asks for ươ. horncomb (U+031B) is the lowercase horn on its own.
- the precomposed letters of U+1EA0 to U+1EF9 that DINish lacks, as composites
  of DINish's own marks at DINish's own positions. On a circumflex every tone
  mark sits to the right, the grave too: Vietnamese guidance recommends tone
  marks consistently on the right for reading, and a grave on the left would
  run into the ascender before it (đầu, lần, những, Hồ), while a tone on the
  right only meets the x-height letters that end a syllable. The tilde sits on
  top of the circumflex, and every tone on top of the breve.
- DINish has no capital marks, and its capital stacks would rise above the
  ascent, so capital stacks use DINish's circumflex and breve cut shorter
  (circumflexcmb.case, brevecmb.case), the hook with its tail cut shorter
  (hookabovecomb.case) and tighter gaps. Everything stays inside usWinAscent
  and the hhea ascender.
- the single-storey (ss02) forms of the new a letters, so the italic, which
  draws every a single-storey, draws these too; mark anchors for the new bases
  and marks (a horn lookup of its own; DINish has no mkmk, so stacked marks
  come from the precomposed letters, which shapers compose to); and the base
  letters' kerning classes, for these letters and for DINish's own Vietnamese
  letters that had none (Ă Ạ Ẹ Ị Ọ Ụ Ỳ ...), on the right side only where no
  horn changes it.
- each composite stands its base letter where DINish's own composite of the
  same base and first mark does, with that composite's advance: DINish sets
  its accented E narrower than E in the heavier weights, and its I further
  right in a wider box.
"""

import unicodedata
from copy import deepcopy
from math import hypot, radians, tan

import skia
from fontTools.misc.roundTools import noRound, otRound
from fontTools.pens.basePen import BasePen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib.tables import otTables as ot
from shapely.geometry import Polygon

from kerning import copy_kerning

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
        self.path.cubicTo(*a, *b, *c)

    def _closePath(self):
        self.path.close()

    def _endPath(self):
        pass


def _outline(font, name):
    pen = _SkiaPen(font.getGlyphSet())
    font["glyf"][name].draw(pen, font["glyf"])
    return pen.path


def _contours(path):
    """Split a skia path into closed contours of (verb, points) in quads and lines."""
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
            raise ValueError("cubic in a Vietnamese outline")
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


def _glyph(path):
    """A TrueType glyph from a skia path, outer contours clockwise. Points keep
    their fractions, as build.py keeps its own until the finer export grid
    rounds them: a curve that a union split keeps its tangent, where rounding a
    short piece's control point to the unit would leave a kink."""
    cs = _contours(skia.Simplify(path))
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
        # TrueType: ink contours run clockwise (negative area), counters the other way.
        clockwise = depth % 2 == 0
        if (_area(_polygon(c, 4)) < 0) != clockwise:
            c = _reverse(c)
        c = _tidy(c)
        pen.moveTo(c[0][1][0])
        for verb, p in c[1:]:
            if verb == "L":
                pen.lineTo(p[0])
            else:
                pen.qCurveTo(*p)
        pen.closePath()
    return pen.glyph(round=noRound)


def _tidy(contour, shortest=1.0):
    """Merge segments shorter than a unit (a cut through a curve can leave
    one) into their neighbours, and make a curve whose control point sits on
    an end a line."""
    prev = contour[0][1][0]
    out = [contour[0]]
    for verb, p in contour[1:]:
        end = p[-1]
        if hypot(end[0] - prev[0], end[1] - prev[1]) < shortest:
            continue
        if (
            verb == "Q"
            and min(hypot(p[0][0] - q[0], p[0][1] - q[1]) for q in (prev, end)) < 1e-6
        ):
            verb, p = "L", [end]
        out.append((verb, p))
        prev = end
    return out


def _reverse(contour):
    """Reverse a closed contour of (verb, points)."""
    nodes = [contour[0][1][0]]
    segs = []
    for verb, p in contour[1:]:
        segs.append((verb, nodes[-1], p))
        nodes.append(p[-1])
    out = [("M", [nodes[-1]])]
    for verb, start, p in reversed(segs):
        if verb == "L":
            out.append(("L", [start]))
        else:
            out.append(("Q", [p[0], start]))
    return out


def _shift(path, dx=0, dy=0, sx=1, sy=1):
    out = skia.Path(path)
    out.transform(skia.Matrix.MakeAll(sx, 0, dx, 0, sy, dy, 0, 0, 1))
    return out


def _union(*paths):
    out = skia.Path()
    for p in paths:
        out = skia.Op(out, p, skia.PathOp.kUnion_PathOp)
    return out


def _rect(x0, y0, x1, y1):
    p = skia.Path()
    p.addRect(skia.Rect.MakeLTRB(x0, y0, x1, y1))
    return p


def _bounds(path):
    b = path.computeTightBounds()
    return b.left(), b.top(), b.right(), b.bottom()


def _run(path, y, x0=-400, x1=1400):
    """Horizontal ink runs of a path at height y, to the unit."""
    runs = []
    for x in range(x0, x1):
        if path.contains(x + 0.5, y):
            if runs and runs[-1][1] == x:
                runs[-1][1] = x + 1
            else:
                runs.append([x, x + 1])
    return runs


def _column(path, x, y0=-400, y1=1400):
    runs = []
    for y in range(y0, y1):
        if path.contains(x, y + 0.5):
            if runs and runs[-1][1] == y:
                runs[-1][1] = y + 1
            else:
                runs.append([y, y + 1])
    return runs


def _largest(path):
    """The contour with the largest area, as a path."""
    best = None
    for c in _contours(path):
        area = abs(_area(_polygon(c)))
        if best is None or area > best[0]:
            best = (area, c)
    return _path(best[1])


def _path(contour):
    p = skia.Path()
    p.moveTo(*contour[0][1][0])
    for verb, pts in contour[1:]:
        if verb == "L":
            p.lineTo(*pts[0])
        else:
            p.quadTo(*pts[0], *pts[1])
    p.close()
    return p


def _shapely(path):
    polys = [Polygon(_polygon(c, 6)).buffer(0) for c in _contours(skia.Simplify(path))]
    out = polys[0]
    for p in polys[1:]:
        out = out.symmetric_difference(p)
    return out


def _distance(a, b):
    return _shapely(a).distance(_shapely(b))


def _lowest_dy(lower, upper, dx, gap, start, stop):
    """The lowest whole-unit lift of `upper` (moved by dx) that keeps `gap` from `lower`."""
    low, high = start, stop
    assert _distance(lower, _shift(upper, dx, high)) >= gap
    while high - low > 1:
        mid = (low + high) // 2
        if _distance(lower, _shift(upper, dx, mid)) >= gap:
            high = mid
        else:
            low = mid
    return high


# ---------------------------------------------------------------- measures


def _quarter(font, name, contour_index):
    """DINish's own lower-right bowl quarter of `name`, normalized: the
    off-curve points between the lowest point and the right side (one or two,
    as the weight draws it), as fractions of the quarter's box."""
    glyph = font["glyf"][name]
    coords, ends, flags = glyph.getCoordinates(font["glyf"])
    start = 0 if contour_index == 0 else ends[contour_index - 1] + 1
    pts = [
        (coords[i][0], coords[i][1], flags[i] & 1)
        for i in range(start, ends[contour_index] + 1)
    ]
    n = len(pts)
    bottom = min(
        (i for i in range(n) if pts[i][2]), key=lambda i: (pts[i][1], -pts[i][0])
    )
    # Walk from the bottom towards the right side: the neighbour with the larger x.
    step = 1 if pts[(bottom + 1) % n][0] > pts[(bottom - 1) % n][0] else -1
    offs, i = [], (bottom + step) % n
    while not pts[i][2]:
        offs.append(pts[i])
        i = (i + step) % n
    end = pts[i]
    x0, y0 = pts[bottom][0], pts[bottom][1]
    w, h = end[0] - x0, end[1] - y0
    assert offs and w > 0 and h > 0, (name, offs)
    return tuple(((p[0] - x0) / w, (p[1] - y0) / h) for p in offs)


def _measure(font):
    """Per-weight strokes and positions, all read from this DINish master."""
    m = {"xh": font["OS/2"].sxHeight, "cap": font["OS/2"].sCapHeight}
    o, O, f = _outline(font, "o"), _outline(font, "O"), _outline(font, "f")
    ob, Ob = _bounds(o), _bounds(O)

    def side(path, b):
        run = _run(path, int((b[1] + b[3]) / 2))[-1]
        return run[1] - run[0]

    def top(path, b):
        run = _column(path, (b[0] + b[2]) / 2)[-1]
        return run[1] - run[0]

    m["o_side"], m["o_top"] = side(o, ob), top(o, ob)
    m["O_side"], m["O_top"] = side(O, Ob), top(O, Ob)
    fb = _bounds(f)
    arm = _column(f, fb[2] - 8)[-1]
    m["f_arm"] = arm[1] - arm[0]
    breve = _outline(font, "brevecmb")
    bb = _bounds(breve)
    arm = _run(breve, int(bb[3]) - 6)[0]
    m["mark_stroke"] = arm[1] - arm[0]
    m["outer_quarter"] = _quarter(font, "o", 0)
    m["inner_quarter"] = _quarter(font, "o", 1)
    # Where each bowl's shoulder turns through 45 degrees: the horn leaves it there.
    for key, path, b in (("o_shoulder", o, ob), ("O_shoulder", O, Ob)):
        best = None
        for y in range(int((b[1] + b[3]) / 2), int(b[3])):
            right = _run(path, y)[-1][1]
            below = _run(path, y - 4)[-1][1]
            if best is None or abs((below - right) - 4) < best[0]:
                best = (abs((below - right) - 4), (right, y))
        m[key] = best[1]
    m["right"] = {
        name: _bounds(_outline(font, name))[2] for name in ("o", "O", "u", "U")
    }
    runs = _run(o, int((ob[1] + ob[3]) / 2))
    m["o_counter"] = (runs[-1][0] - runs[0][1]) / 2
    m["mark_zone"] = _bounds(_outline(font, "acutecomb"))[3] - m["xh"]
    return m


# ---------------------------------------------------------------- new parts

# The hook above is as wide as this share of the circumflex, and this much
# taller than it. Vietnamese guidance asks for a hook smaller than the question
# mark it resembles, with its stem cut away.
HOOK_WIDTH = 0.6
HOOK_HEIGHT = 1.12
# The horn: its inner curve as a share of the o's counter (so it tightens in
# the heavier weights, as DINish's own counters do), how high its flat end
# rises above the letter as a share of the height the acute stands above the
# x-height, and how far its end leans right of upright, in degrees.
HORN_INNER = 0.25
HORN_RISE = 0.4
HORN_LEAN = 12
# The horn's curve starts this share of its stroke inside the letter (the top
# of the U's stem, the O's shoulder), so the letter flows into it rather than
# carrying a level shelf.
HORN_INSET = 0.35


def _hook(font, m, height=HOOK_HEIGHT):
    """DINish's question mark without its dot, at mark size and the breve's
    stroke: the outline is scaled, then grown evenly so every part keeps the
    question mark's own proportion of stroke to curve, and its stem is cut
    away level, as DIN cuts its terminals, where the hook is `height`
    circumflex heights tall."""
    q = _largest(_outline(font, "question"))
    x0, y0, x1, y1 = _bounds(q)
    widest = max(range(int(y0) + 1, int(y1), 2), key=lambda y: (_run(q, y)[-1][1], -y))
    side = _run(q, widest)[-1]
    side = side[1] - side[0]
    circ = _bounds(_outline(font, "circumflexcmb"))
    stroke = m["mark_stroke"]
    k = (HOOK_WIDTH * (circ[2] - circ[0]) - stroke) / ((x1 - x0) - side)
    grow = (stroke - side * k) / 2
    paint = skia.Paint(
        Style=skia.Paint.kStrokeAndFill_Style,
        StrokeWidth=2 * grow,
        StrokeJoin=skia.Paint.kMiter_Join,
        StrokeMiter=8,
    )
    grown = skia.Path()
    paint.getFillPath(_shift(q, sx=k, sy=k), grown)
    grown = skia.Simplify(grown)
    top = y1 * k + grow
    cut = top - height * (circ[3] - circ[1])
    hook = skia.Op(grown, _rect(-4000, cut, 4000, 4000), skia.PathOp.kIntersect_PathOp)
    hx0, hy0, hx1, _ = _bounds(hook)
    acute = _bounds(_outline(font, "acutecomb"))
    return _shift(hook, -round((hx0 + hx1) / 2), round(acute[1] - hy0))


def _quad_chain(start, end, offs, flip=False):
    """Absolute quadratic points for a quarter from `start` to `end` whose
    normalized off-curve points are `offs` (x along the box from start)."""
    (x0, y0), (x1, y1) = start, end
    pts = [(x0 + (x1 - x0) * a, y0 + (y1 - y0) * b) for a, b in offs]
    return list(reversed(pts)) if flip else pts


def _horn_piece(m, case, stub):
    """The horn in its own frame: where it leaves the letter at x 0, the top
    of its stroke at y 0. It leaves level, turns up through DINish's own o
    quarter (outer and inner curves, as this weight draws them) and ends in a
    short upright, leaned HORN_LEAN degrees and cut flat at `stub` above y 0.
    Its level part has the weight of the f's arm, its upright that weight in
    the o's own ratio of side to top; capitals scale both as O's side to o's."""
    scale = 1 if case == "lc" else m["O_side"] / m["o_side"]
    t_h = m["f_arm"] * scale
    t_v = m["f_arm"] * m["o_side"] / m["o_top"] * scale
    reach = t_v + HORN_INNER * m["o_counter"] * scale
    turn = reach - t_h
    root = 2 * t_v
    p = skia.Path()
    p.moveTo(-root, -t_h)
    p.lineTo(0, -t_h)
    offs = _quad_chain((0, -t_h), (reach, turn), m["outer_quarter"])
    _qcurve(p, offs, (reach, turn))
    p.lineTo(reach, stub)
    p.lineTo(reach - t_v, stub)
    p.lineTo(reach - t_v, turn)
    offs = _quad_chain((0, 0), (reach - t_v, turn), m["inner_quarter"], flip=True)
    _qcurve(p, offs, (0, 0))
    p.lineTo(-root, 0)
    p.close()
    # Lean the end: a shear keeps the level root and the flat cut level.
    lean = tan(radians(HORN_LEAN))
    p.transform(skia.Matrix.MakeAll(1, lean, 0, 0, 1, 0, 0, 0, 1))
    return p, {"reach": reach + lean * stub, "turn": turn, "t_h": t_h, "t_v": t_v}


def _qcurve(path, offs, end):
    """TrueType qCurveTo onto a skia path: implied on-curve points between offs."""
    for i, c in enumerate(offs):
        nxt = (
            end
            if i == len(offs) - 1
            else ((c[0] + offs[i + 1][0]) / 2, (c[1] + offs[i + 1][1]) / 2)
        )
        path.quadTo(*c, *nxt)


def _horned(font, m, base):
    """Ơ ơ Ư ư: the base letter and its horn as one outline, in DINish's square
    corners. U and u carry it from the top of the right stem; O and o from
    where the shoulder turns through 45 degrees. All four horn tops stand the
    same height above the letter."""
    case = "uc" if base.isupper() else "lc"
    top = m["cap"] if case == "uc" else m["xh"]
    rise = HORN_RISE * m["mark_zone"]
    letter = _outline(font, base)
    scale = 1 if case == "lc" else m["O_side"] / m["o_side"]
    inset = HORN_INSET * m["f_arm"] * m["o_side"] / m["o_top"] * scale
    if base in "Uu":
        x, y = m["right"][base] - inset, top
    else:
        x, y = m["O_shoulder" if case == "uc" else "o_shoulder"]
        x -= inset
    piece, info = _horn_piece(m, case, top + rise - y)
    piece = _shift(piece, x, y)
    # Only the part outside the letter: a root that reached into a counter, or
    # into the opening of a U, would fill it.
    filled = _largest(letter) if base in "Oo" else _rect(*_bounds(letter))
    piece = skia.Op(piece, filled, skia.PathOp.kDifference_PathOp)
    return _union(letter, piece), {
        **info,
        "x": x,
        "y": y,
        "rise": rise,
        "tip": x + info["reach"],
    }


# ---------------------------------------------------------------- letters

MARKS = {
    0x0300: "grave",
    0x0301: "acute",
    0x0302: "circumflex",
    0x0303: "tilde",
    0x0306: "breve",
    0x0309: "hookabove",
    0x031B: "horn",
    0x0323: "dotbelow",
}
TONES = ("grave", "acute", "hookabove", "tilde")
HORNED = {0x01A0: "Ohorn", 0x01A1: "ohorn", 0x01AF: "Uhorn", 0x01B0: "uhorn"}
# The Vietnamese letters with a mark: each vowel, plain or with its
# circumflex, breve or horn, with each tone or none.
VIETNAMESE = {
    unicodedata.normalize("NFC", vowel + tone)
    for vowel in "aăâeêioôơuưyAĂÂEÊIOÔƠUƯY"
    for tone in ("", "\u0300", "\u0301", "\u0309", "\u0303", "\u0323")
} - set("aeiouyAEIOUY")
# Stacked marks keep this share of DINish's own gap between a letter and its mark.
STACK_GAP = 0.75
# A tone mark to the right of a circumflex stands with its foot (the middle of
# its lowest edge) this far across the bottom of the circumflex's right leg:
# 0 at its inner corner, 1 at its outer one. Over the outer end, the tone can
# drop beside the leg, as in Noto Sans, Barlow and Be Vietnam Pro; nearer the
# inner corner (0.25 in 0.21.0) the leg's outer edge stood almost as high as
# the apex there, so the tone had to stand on top of the whole circumflex.
RIGHT_FOOT = 1.0
# Capital stacks must fit under the font's ascent, and DINish has no capital
# marks: they keep this share of the gap, cut this share off the circumflex's
# legs and the breve's arms, and cut the hook's tail until it is this many
# circumflex heights tall; every cut level, as DINish cuts its marks. Cutting
# keeps each mark's stroke and curve; a hook scaled down instead closed its
# counter in the heavier weights.
CAPITAL_GAP = 0.5
CAPITAL_CUT = 0.3
CAPITAL_HOOK_HEIGHT = 0.95


def _decompose(char):
    nfd = unicodedata.normalize("NFD", char)
    return nfd[0], [MARKS[ord(c)] for c in nfd[1:]]


def _name(base, marks):
    order = ["horn", "circumflex", "breve", *TONES, "dotbelow"]
    return base + "".join(sorted(marks, key=order.index))


def _letters(cmap):
    """Every Vietnamese letter of U+1EA0 to U+1EF9 that DINish lacks."""
    out = []
    for cp in range(0x1EA0, 0x1EFA):
        if cp in cmap:
            continue
        base, marks = _decompose(chr(cp))
        if "horn" in marks:
            base = {"O": "Ohorn", "o": "ohorn", "U": "Uhorn", "u": "uhorn"}[base]
            marks = [k for k in marks if k != "horn"]
        out.append((cp, _name(base, marks), base, marks))
    return out


class _Placer:
    """Where DINish puts each mark on each letter, read from its own composites,
    and where the stacks put their second mark."""

    def __init__(self, font, m):
        self.font = font
        self.m = m
        cmap = font.getBestCmap()
        self.glyph = {k: cmap[cp] for cp, k in MARKS.items() if cp in cmap}
        self.composites = {}
        # Each composite's frame: where it puts its base letter, and its advance.
        self.frames = {}
        glyf = font["glyf"]
        for name in font.getGlyphOrder():
            g = glyf[name]
            if g.isComposite() and len(g.components) == 2:
                base, mark = g.components
                self.composites[(base.glyphName, mark.glyphName)] = (mark.x, mark.y)
                self.frames[(base.glyphName, mark.glyphName)] = (
                    (base.x, base.y),
                    font["hmtx"][name][0],
                )
        anchors = {}
        for lookup in font["GPOS"].table.LookupList.Lookup:
            if lookup.LookupType != 4:
                continue
            for sub in lookup.SubTable:
                if "acutecomb" in sub.MarkCoverage.glyphs:
                    for name, rec in zip(
                        sub.BaseCoverage.glyphs, sub.BaseArray.BaseRecord
                    ):
                        anchors[name] = rec.BaseAnchor[0].XCoordinate
        self.anchors = anchors
        circ = _bounds(_outline(font, self.glyph["circumflex"]))
        self.gap = round(STACK_GAP * (circ[1] - m["xh"]))
        self.capital_gap = round(CAPITAL_GAP * (circ[1] - m["xh"]))
        self.shapes = {k: _outline(font, g) for k, g in self.glyph.items()}
        self.cache = {}

    def offset(self, base, kind, capital):
        """DINish's own position of a single mark on `base`: from its
        composite with that mark, else centred where its circumflex sits."""
        mark = self.glyph.get(kind, "hookabovecomb")
        if (base, mark) in self.composites:
            return self.composites[(base, mark)]
        centre = self.composites.get((base, self.glyph["circumflex"]))
        a = "A" if capital else "a"
        if kind in ("acute", "grave", "tilde", "dotbelow") and centre is not None:
            ref = self.composites[(a, self.glyph[kind])]
            aref = self.composites[(a, self.glyph["circumflex"])]
            x = centre[0] + ref[0] - aref[0]
            return (x, ref[1] if kind != "dotbelow" else 0)
        if centre is not None:
            # The hook above is a centred mark, like the circumflex; it lifts
            # onto capitals as the acute does.
            lift = self.composites[(a, self.glyph["acute"])][1]
            return (centre[0], lift)
        x = self.anchors[base]
        lift = self.composites[(a, self.glyph["acute"])][1]
        return (x, lift if kind != "dotbelow" else 0)

    def frame(self, base, kind):
        """The frame of the DINish composite offset() reads the position of
        `kind` on `base` from, or None where it reads an anchor."""
        mark = self.glyph.get(kind, "hookabovecomb")
        return self.frames.get((base, mark)) or self.frames.get(
            (base, self.glyph["circumflex"])
        )

    def tone_from(self, lower, tone, capital):
        """Where a tone mark sits from the circumflex or breve under it, in
        whole units: to the right of a circumflex, its foot over the end of the
        right leg (RIGHT_FOOT); on top of a breve, or of a circumflex for the
        tilde, where DINish centres it. Either way as low as the stack gap
        allows, and the same for every letter of a case."""
        key = (lower, tone, capital)
        if key in self.cache:
            return self.cache[key]
        shapes = self.capital_shapes if capital else self.shapes
        gap = self.capital_gap if capital else self.gap
        low, top = shapes[lower], shapes[tone]
        lb, tb = _bounds(low), _bounds(top)
        a = "A" if capital else "a"
        if lower == "circumflex" and tone != "tilde":
            # Measured on DINish's full marks: the capital stack's circumflex and
            # hook are the same marks cut shorter, so the tone stands where it
            # would on the full circumflex, only lower.
            full = self.shapes[lower]
            legs = _run(full, int(_bounds(full)[1]) + 1)
            leg = legs[-1][0] + RIGHT_FOOT * (legs[-1][1] - legs[-1][0])
            full = self.shapes[tone]
            feet = _run(full, int(_bounds(full)[1]) + 1)
            foot = (feet[0][0] + feet[-1][1]) / 2
            dx = round(leg - foot)
            start = round(lb[1] - tb[1])
            dy = _lowest_dy(low, top, dx, gap, start, round(lb[3] - tb[1]) + gap + 1)
        else:
            dx = 0
            if tone != "hookabove":
                dx = (
                    self.composites[(a, self.glyph[tone])][0]
                    - self.composites[(a, self.glyph[lower])][0]
                )
            start = round(lb[1] - tb[1])
            dy = _lowest_dy(low, top, dx, gap, start, round(lb[3] - tb[1]) + gap + 1)
        self.cache[key] = (dx, dy)
        return dx, dy

    def components(self, base, marks):
        """[(glyph, x, y)] for `base` with Vietnamese `marks`, and the advance.

        The base letter stands where DINish's own composite that gives the
        first mark its place stands it, with that composite's advance: the
        marks' positions are read in its frame, and DINish's heavier weights
        set E's accented letters narrower than E (Bold: 544 against 569) and
        I's further right in a wider box (Bold: Í at 7 in 267, I 254)."""
        capital = base[0].isupper()
        source = {
            "Ohorn": "O",
            "ohorn": "o",
            "Uhorn": "U",
            "uhorn": "u",
            "i": "dotlessi",
        }.get(base, base)
        glyph = {"i": "dotlessi"}.get(base, base)
        if base == "i" and marks == ["dotbelow"]:
            glyph = "i"
        tones = [k for k in marks if k in TONES]
        lower = [k for k in marks if k in ("circumflex", "breve")]
        first = (lower or tones or ["dotbelow"])[0]
        frame = None
        if glyph == source:  # not a horned letter, whose horn changes its width
            frame = self.frame(source, first)
        (bx, by), advance = frame or ((0, 0), self.font["hmtx"][glyph][0])
        out = [(glyph, bx, by)]
        if lower:
            x, y = self.offset(source, lower[0], capital)
            name = self.glyph[lower[0]]
            if capital and tones:
                # The capital stack's circumflex or breve, a stack gap above the capital.
                name = self.capital_glyph[lower[0]]
                y = round(
                    self.m["cap"]
                    + self.capital_gap
                    - _bounds(self.capital_shapes[lower[0]])[1]
                )
            out.append((name, x, y))
            if tones:
                dx, dy = self.tone_from(lower[0], tones[0], capital)
                names = self.capital_glyph if capital else self.glyph
                out.append((names[tones[0]], x + dx, y + dy))
        elif tones:
            x, y = self.offset(source, tones[0], capital)
            out.append((self.glyph[tones[0]], x, y))
        if "dotbelow" in marks:
            x, y = self.offset(
                source if source != "dotlessi" else "i", "dotbelow", capital
            )
            out.append((self.glyph["dotbelow"], x, y))
        return out, advance

    def add_capital_marks(self, capital_marks):
        """The capital stack's own marks, {kind: (glyph, outline)}; the others
        are DINish's."""
        self.capital_glyph = dict(self.glyph)
        self.capital_shapes = dict(self.shapes)
        for kind, (name, path) in capital_marks.items():
            self.capital_glyph[kind] = name
            self.capital_shapes[kind] = path


# ---------------------------------------------------------------- the font


def _composite(font, parts, metrics=True):
    pen = TTGlyphPen(font.getGlyphSet())
    for name, x, y in parts:
        pen.addComponent(name, (1, 0, 0, 1, x, y))
    glyph = pen.glyph()
    for i, component in enumerate(glyph.components):
        # As DINish's own composites: the base letter gives the metrics,
        # unless the composite moves it or has an advance of its own.
        component.flags = 0x204 if i == 0 and metrics else 0x4
    return glyph


class _Builder:
    def __init__(self, font, style):
        self.font = font
        self.style = style
        self.order = list(font.getGlyphOrder())
        self.decisions = {}
        self.unicodes = {}

    def add(self, name, glyph, advance, decision, cp=None):
        assert name not in self.font["glyf"], name
        self.order.append(name)
        self.font.setGlyphOrder(list(self.order))
        self.font["glyf"][name] = glyph
        glyph.recalcBounds(self.font["glyf"])
        self.font["hmtx"][name] = (int(advance), otRound(getattr(glyph, "xMin", 0)))
        if cp is not None:
            self.unicodes[cp] = name
        self.decisions[name] = decision

    def finish(self, classes):
        font = self.font
        for table in font["cmap"].tables:
            if table.isUnicode():
                for cp, name in sorted(self.unicodes.items()):
                    if table.format != 4 or cp <= 0xFFFF:
                        table.cmap[cp] = name
        if "GDEF" in font and font["GDEF"].table.GlyphClassDef:
            defs = font["GDEF"].table.GlyphClassDef.classDefs
            for name, cls in classes.items():
                if cls:
                    defs[name] = cls
        font["OS/2"].recalcUnicodeRanges(font)


def extend(font, style):
    """Add DINDOT's Vietnamese to a freshly loaded DINish master; return
    {glyph name: decision}."""
    builder = _Builder(font, style)
    m = _measure(font)
    cmap = font.getBestCmap()
    classes = {}

    # The two new marks.
    if 0x0309 not in cmap:
        hook = _hook(font, m)
        builder.add(
            "hookabovecomb",
            _glyph(hook),
            0,
            "DINish's question mark without its dot, scaled to mark size and grown back to the breve's stroke, its stem cut away level.",
            0x0309,
        )
        classes["hookabovecomb"] = 3
    horns = {}
    for cp, name in HORNED.items():
        base = name[0]
        path, info = _horned(font, m, base)
        horns[name] = info
        if cp in cmap:
            continue
        advance = max(font["hmtx"][base][0], round(info["tip"]))
        builder.add(
            name,
            _glyph(path),
            advance,
            f"{base} and a horn in one square-cornered outline, its curve DINish's o quarter and its flat end level with the other horns; {base}'s advance"
            + (
                f", widened to the horn's tip ({advance} units)."
                if advance > font["hmtx"][base][0]
                else "."
            ),
            cp,
        )
        classes[name] = 1
    if 0x031B not in cmap:
        info = horns["uhorn"]
        piece, _ = _horn_piece(m, "lc", info["rise"])
        piece = _shift(piece, 0, m["xh"])
        piece = skia.Op(
            piece, _rect(-2000, -2000, 0, m["xh"]), skia.PathOp.kDifference_PathOp
        )
        builder.add(
            "horncomb",
            _glyph(piece),
            0,
            "The lowercase horn on its own, as u carries it, attached by its own mark anchor to O, o, U and u.",
            0x031B,
        )
        classes["horncomb"] = 3

    # The precomposed letters.
    placer = _Placer(font, m)
    placer.glyph["hookabove"] = cmap.get(0x0309, "hookabovecomb")
    placer.shapes["hookabove"] = _outline(font, placer.glyph["hookabove"])
    capital = {}
    for kind, keep, why in (
        (
            "circumflex",
            "legs",
            "DINish's circumflex with its legs cut shorter, level, for capital stacks.",
        ),
        (
            "breve",
            "arms",
            "DINish's breve with its arms cut shorter, level, for capital stacks.",
        ),
    ):
        mark = placer.glyph[kind]
        path = placer.shapes[kind]
        x0, y0, x1, y1 = _bounds(path)
        cut = CAPITAL_CUT * (y1 - y0)
        band = (
            _rect(x0 - 10, y0 + cut, x1 + 10, y1 + 10)
            if keep == "legs"
            else _rect(x0 - 10, y0 - 10, x1 + 10, y1 - cut)
        )
        path = skia.Op(path, band, skia.PathOp.kIntersect_PathOp)
        builder.add(mark + ".case", _glyph(path), 0, why)
        classes[mark + ".case"] = 3
        capital[kind] = (mark + ".case", _outline(font, mark + ".case"))
    builder.add(
        "hookabovecomb.case",
        _glyph(_hook(font, m, CAPITAL_HOOK_HEIGHT)),
        0,
        "The hook above with its tail cut shorter, level, for capital stacks.",
    )
    classes["hookabovecomb.case"] = 3
    capital["hookabove"] = ("hookabovecomb.case", _outline(font, "hookabovecomb.case"))
    placer.add_capital_marks(capital)
    letters = _letters(cmap)
    for cp, name, base, marks in letters:
        parts, advance = placer.components(base, marks)
        glyph, bx, by = parts[0]
        metrics = (bx, by) == (0, 0) and advance == font["hmtx"][glyph][0]
        builder.add(
            name,
            _composite(font, parts, metrics),
            advance,
            _describe(base, marks),
            cp,
        )
        classes[name] = 1
    # The single-storey a: the same marks, where DINish's own a.ss02 forms
    # keep them, so the italic draws every a the same way.
    ss02 = {}
    for cp, name, base, marks in letters:
        if base != "a":
            continue
        parts = [("a.ss02", 0, 0)] + placer.components(base, marks)[0][1:]
        alt = name + ".ss02"
        builder.add(
            alt,
            _composite(font, parts),
            font["hmtx"]["a.ss02"][0],
            f"The single-storey form of {name}, for ss02 and the italic.",
        )
        classes[alt] = font["GDEF"].table.GlyphClassDef.classDefs.get(
            "acircumflex.ss02", 0
        )
        ss02[name] = alt
    builder.finish(classes)
    _alternates(font, ss02)
    _anchors(font, m, horns)
    _kerning(font)
    return builder.decisions


def _describe(base, marks):
    """One sentence for the decision record of a precomposed letter."""
    shown = {"hookabove": "hook above", "dotbelow": "dot below"}
    tones = [shown.get(k, k) for k in marks if k in TONES]
    lower = [k for k in marks if k in ("circumflex", "breve")]
    below = " and DINish's dot below" if "dotbelow" in marks else ""
    if lower and tones:
        capital = base[0].isupper()
        mark = (
            f"the capital stack's {lower[0]} (DINish's, cut shorter)"
            if capital
            else f"DINish's {lower[0]}"
        )
        if lower[0] == "circumflex" and tones[0] != "tilde":
            where = "to its right, foot over the end of its right leg"
        else:
            where = "centred on top"
        return f"{base} with {mark} and the {tones[0]} {where}, as low as the stack gap allows{below}; a composite."
    if lower:
        return (
            f"{base} with DINish's {lower[0]} where DINish sets it{below}; a composite."
        )
    if tones:
        tone = (
            "the new hook above" if tones[0] == "hook above" else f"DINish's {tones[0]}"
        )
        return f"{base} with {tone} where DINish centres its marks on {base.replace('horn', '')}{below}; a composite."
    return f"{base} with DINish's dot below where DINish sets it; a composite."


def _alternates(font, ss02):
    """Put the new single-storey forms in DINish's own ss02 substitution."""
    gsub = font["GSUB"].table
    for record in gsub.FeatureList.FeatureRecord:
        if record.FeatureTag != "ss02":
            continue
        for index in record.Feature.LookupListIndex:
            for sub in gsub.LookupList.Lookup[index].SubTable:
                if hasattr(sub, "mapping") and "a" in sub.mapping:
                    sub.mapping.update(ss02)


def _anchor(x, y):
    a = ot.Anchor()
    a.Format = 1
    a.XCoordinate, a.YCoordinate = int(x), int(y)
    return a


def _insert(coverage, records, name, record, gid):
    """Insert into a coverage and its parallel record list, in glyph order."""
    glyphs = coverage.glyphs
    at = next((i for i, g in enumerate(glyphs) if gid[g] > gid[name]), len(glyphs))
    glyphs.insert(at, name)
    records.insert(at, record)


def _anchors(font, m, horns):
    """Mark positioning for decomposed text: the new letters take their base
    letter's anchors, the hook above attaches like the acute, and the horn has
    its own anchor at the point each horned letter carries it from."""
    gpos = font["GPOS"].table
    gid = {g: i for i, g in enumerate(font.getGlyphOrder())}
    for lookup in gpos.LookupList.Lookup:
        if lookup.LookupType != 4:
            continue
        for sub in lookup.SubTable:
            marks = sub.MarkCoverage.glyphs
            if (
                "acutecomb" in marks
                and "hookabovecomb" in gid
                and "hookabovecomb" not in marks
            ):
                proto = sub.MarkArray.MarkRecord[marks.index("acutecomb")]
                _insert(
                    sub.MarkCoverage,
                    sub.MarkArray.MarkRecord,
                    "hookabovecomb",
                    deepcopy(proto),
                    gid,
                )
                sub.MarkArray.MarkCount = len(sub.MarkArray.MarkRecord)
            bases = sub.BaseCoverage.glyphs
            for name in HORNED.values():
                base = name[0]
                if name in gid and base in bases and name not in bases:
                    proto = sub.BaseArray.BaseRecord[bases.index(base)]
                    _insert(
                        sub.BaseCoverage,
                        sub.BaseArray.BaseRecord,
                        name,
                        deepcopy(proto),
                        gid,
                    )
            sub.BaseArray.BaseCount = len(sub.BaseArray.BaseRecord)
    if "horncomb" not in gid:
        return
    sub = ot.MarkBasePos()
    sub.Format = 1
    sub.ClassCount = 1
    sub.MarkCoverage = ot.Coverage()
    sub.MarkCoverage.glyphs = ["horncomb"]
    record = ot.MarkRecord()
    record.Class = 0
    record.MarkAnchor = _anchor(0, m["xh"])
    sub.MarkArray = ot.MarkArray()
    sub.MarkArray.MarkRecord = [record]
    sub.MarkArray.MarkCount = 1
    sub.BaseCoverage = ot.Coverage()
    sub.BaseCoverage.glyphs = sorted("OUou", key=gid.get)
    sub.BaseArray = ot.BaseArray()
    sub.BaseArray.BaseRecord = []
    for base in sub.BaseCoverage.glyphs:
        info = horns[base + "horn"]
        rec = ot.BaseRecord()
        rec.BaseAnchor = [_anchor(round(info["x"]), round(info["y"]))]
        sub.BaseArray.BaseRecord.append(rec)
    sub.BaseArray.BaseCount = len(sub.BaseArray.BaseRecord)
    lookup = ot.Lookup()
    lookup.LookupType = 4
    lookup.LookupFlag = 0
    lookup.SubTable = [sub]
    lookup.SubTableCount = 1
    gpos.LookupList.Lookup.append(lookup)
    gpos.LookupList.LookupCount = len(gpos.LookupList.Lookup)
    for record in gpos.FeatureList.FeatureRecord:
        if record.FeatureTag == "mark":
            record.Feature.LookupListIndex.append(len(gpos.LookupList.Lookup) - 1)
            record.Feature.LookupCount = len(record.Feature.LookupListIndex)


def _kerning(font):
    """Every precomposed Vietnamese letter, DINish's own (Ă Ạ Ẹ Ị Ọ Ụ Ỳ ...) as
    well as the new ones, kerns as its base letter wherever it has no kerning
    of its own: on its left side always, and on its right side unless a horn
    changes it. Marks above or below the letter leave both sides to the body,
    as DINish kerns its own á and â as a."""
    cmap = font.getBestCmap()
    for char in sorted(VIETNAMESE):
        name = cmap.get(ord(char))
        decomposed = unicodedata.normalize("NFD", char)
        model = cmap.get(ord(decomposed[0]))
        if name is None or model is None or model == name:
            continue
        copy_kerning(font, name, model, right="\u031b" not in decomposed)
