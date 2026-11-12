"""DINDOT Italic: slant the finished upright faces the way a designer would.

The italic is made from the upright TrueType outlines (8192 units, read in the
1024-unit design space). Every slanted contour goes through:

1. fillet arcs recovered as co-circular runs and replaced by their sharp
   corner, each remembering its radius (the geometric mean of the axes of the
   slightly elliptical fillet the text stage stretched);
2. a stroke correction that keeps every stroke's upright perpendicular
   thickness after the shear: each edge moves by h(n) = t/2 (|M^-T n| - 1),
   in the envelope form h n + h' t that keeps every tangent. t is the width
   of the straight stroke an edge faces, a bowl's own stroke, or the stem;
3. the bowl balance, inside that correction: in every corner a curve's
   outer side takes 2 - cs of it and its inner side cs, with a slight
   contrast (a touch more stroke in the acute corners). The stroke keeps its
   thickness and the bowl turns towards the upright: its sides slide along
   themselves, the acute corners open, the obtuse ones close. cs is searched
   per bowl until its counter's obtuse/acute ratio is `target` times the
   upright's, so every counter gets the same balance. Where two tangent
   pieces end apart (curves with different shares, a curve beside a notch
   leg that keeps its place), the difference is tapered in over one stroke
   width instead of bending the last piece;
4. the shear x += s (y - origin);
5. every recovered corner filleted again as a true circle of its radius;
6. cusp and tangent cleanup: sub-unit pieces the offsets frayed become one
   tangent curve, or their corner, rounded again.

Each contour then has to pass: a valid simple outline in its upright
direction, every join tangent after export, no contour that touches or
crosses itself or turns back on a point at the font's own units, and no more
deviation from the plain shear than its treatment allows. A contour that
fails drops one treatment at a time: full; full with the balance on its
small curves too; full without the tapers; no balance; fillets only; plain
shear. The level each contour got is in the build report.

After export, a quadratic that turns against its neighbours (a dent of the
offsets or of the export grid) is merged with them into one convex curve
when that stays within 6 units (8192 per em) of the outline.

Dots are the upright's own circles, moved: a tittle onto the slanted stem
axis it belongs to, a dot inside a counter (the zero) to that counter's
centre.
"""

import sys
import json
import argparse
import subprocess
from copy import deepcopy
from io import BytesIO
from math import tan, sin, cos, radians, degrees, hypot, sqrt, pi, acos, asin
from pathlib import Path

import numpy as np
from shapely.geometry import Polygon, Point

import ttgeom as T
from contour_checks import glyph_faults
from plain_zero import add_plain_zero
from ttgeom import Contour, read_glyph, emit_glyph
from rounding import Segment, CurveRun, fillet, add, sub, mul, dot, cross, norm, unit
from fontTools.ttLib import TTFont

DINDOT = Path(T.DINDOT)
HERE = Path(__file__).resolve().parent

ANGLE = 12.0
ORIGIN = 264.5  # half the x-height, as DINish Italic

# DINish Italic keeps these 20 upright.
DINISH_UPRIGHT = {
    "plus", "minus", "plusminus", "multiply", "divide", "equal", "less", "greater",
    "logicalnot", "asciitilde", "asciicircum", "bar", "brokenbar", "backslash", "degree",
    "copyright", "registered", "trademark", "dottedcircle", ".notdef",
}
UPRIGHT_FAMILIES = {
    "directional arrows", "double arrows", "bent arrows", "return arrows", "exchange arrows",
    "circular arrows", "mathematics", "geometric symbols", "status symbols",
}
# Superscript and subscript plus, minus and equal follow their full-size signs.
UPRIGHT_EXTRA = {"uni207A", "uni207B", "uni207C", "uni208A", "uni208B", "uni208C"}

# Bowl balance per weight. target: a counter's obtuse/acute corner ratio
# over the upright's (the plain shear gives about 1.85); cs: the inner side's
# share of a curve's stroke correction for an open curve (C, S) and the
# start of each bowl's search; contrast: the stroke's extra weight in the
# acute corners and its lightness in the obtuse ones.
BALANCE = {
    "Regular": {"target": 1.5, "cs": 0.0, "contrast": 0.03},
    "Medium": {"target": 1.5, "cs": 0.0, "contrast": 0.03},
    "SemiBold": {"target": 1.5, "cs": 0.0, "contrast": 0.03},
    "Bold": {"target": 1.5, "cs": 0.0, "contrast": 0.03},
}

# settings.json "italic" holds the same decisions for the project build
_SETTINGS_ITALIC = json.loads((DINDOT / "settings.json").read_text()).get("italic")
if _SETTINGS_ITALIC:
    ANGLE = _SETTINGS_ITALIC["angle"]
    ORIGIN = _SETTINGS_ITALIC["origin"]
    DINISH_UPRIGHT = set(_SETTINGS_ITALIC["upright_glyphs"])
    UPRIGHT_EXTRA = set()
    UPRIGHT_FAMILIES = set(_SETTINGS_ITALIC["upright_families"])
    BALANCE = _SETTINGS_ITALIC["balance"]

LEVELS = (
    # label, fillets, correction, balance, taper
    ("full", True, True, True, True),
    ("full, small curves too", True, True, True, True),
    ("full, untapered", True, True, True, False),
    ("no balance", True, True, False, True),
    ("fillets only", True, False, False, False),
    ("plain shear", False, False, False, False),
)


class P:
    """Parameters for one build."""

    def __init__(self, **kw):
        self.angle = kw.get("angle", ANGLE)
        self.s = tan(radians(self.angle))
        self.origin = kw.get("origin", ORIGIN)
        self.stroke = kw.get("stroke", True)
        self.refillet = kw.get("refillet", True)
        self.dots = kw.get("dots", True)
        self.balance = kw.get("balance", True)
        self.plain = kw.get("plain", False)
        # bowl balance (see BALANCE)
        self.target = kw.get("target", 1.5)
        self.cs = kw.get("cs", 0.0)
        self.contrast = kw.get("contrast", 0.03)
        self.cs_min = kw.get("cs_min", -0.8)
        self.cs_max = kw.get("cs_max", 1.0)

    def copy(self, **kw):
        out = P()
        out.__dict__.update(self.__dict__)
        out.__dict__.update(kw)
        return out


# ------------------------------------------------------------------ segment records


class S:
    """One segment with the metadata of its start point."""

    __slots__ = ("p", "imp", "corner", "sharp", "od", "w", "ol", "f", "cw")

    def __init__(self, p, imp=False, corner=None, sharp=False):
        self.od = None  # direction of a line before the offset
        self.p = tuple(tuple(map(float, q)) for q in p)
        self.imp = imp  # start point was an implied on-curve point
        self.corner = corner  # radius: start point is a recovered fillet corner
        self.sharp = sharp  # start point is a sharp join kept as is
        self.w = None  # stroke width this segment's correction uses
        self.ol = None  # length of a line before the offset
        self.f = 1.0  # share of the curve correction this side takes (bowl balance)
        self.cw = 1.0  # weight of the corner contrast on this curve

    @property
    def seg(self):
        return Segment(self.p)

    def is_line(self):
        return len(self.p) == 2

    def clone(self, p, **kw):
        out = S(p, self.imp, self.corner, self.sharp)
        out.w = self.w
        out.ol = self.ol
        out.f = self.f
        out.cw = self.cw
        for k, v in kw.items():
            setattr(out, k, v)
        return out


def turn_at(a, b):
    """Unsigned turn in degrees between the end of a and the start of b."""
    return T.turn_deg(a.seg, b.seg)


def quant_tol(a, b):
    # tangent direction error from the 1/8-unit export grid at each handle
    la = norm(sub(a.p[-1], a.p[-2]))
    lb = norm(sub(b.p[1], b.p[0]))
    e = 0.125 * sqrt(2)
    return degrees(min(1, e / max(la, 1e-9)) + min(1, e / max(lb, 1e-9)))


def is_g1(a, b, extra=1.0):
    return turn_at(a, b) <= max(1.5, quant_tol(a, b) + extra)


def shear_vec(v, s):
    return (v[0] + s * v[1], v[1])


# ------------------------------------------------------------------ dots


def is_circle(c, tol=0.45):
    P_ = T.sample_contour(c, 16)
    x0, y0 = P_.min(0)
    x1, y1 = P_.max(0)
    w, h = x1 - x0, y1 - y0
    if w < 4 or abs(w - h) > tol:
        return False
    cx, cy, r = (x0 + x1) / 2, (y0 + y1) / 2, (w + h) / 4
    return float(np.abs(np.hypot(P_[:, 0] - cx, P_[:, 1] - cy) - r).max()) < tol


def circle_contour(cx, cy, d, clockwise=True):
    r = d / 2
    k = 4 / 3 * tan(pi / 8)
    segs = []
    for i in range(4):
        a = -i * pi / 2
        b = -(i + 1) * pi / 2
        p0 = (cx + r * cos(a), cy + r * sin(a))
        p3 = (cx + r * cos(b), cy + r * sin(b))
        t0 = (sin(a), -cos(a))
        t1 = (sin(b), -cos(b))
        segs.append(Segment((p0, add(p0, mul(t0, k * r)), sub(p3, mul(t1, k * r)), p3)))
    if not clockwise:
        segs = [Segment(tuple(reversed(s.points))) for s in reversed(segs)]
    return Contour(segs)


def snap(v, grid=0.125):
    return round(v / grid) * grid


# ------------------------------------------------------------------ fillet recovery


def circumcircle(seg):
    a, b, c = seg.at(0), seg.at(0.5), seg.at(1)
    d = 2 * (a[0] * (b[1] - c[1]) + b[0] * (c[1] - a[1]) + c[0] * (a[1] - b[1]))
    if abs(d) < 1e-9:
        return None
    ux = ((a[0] ** 2 + a[1] ** 2) * (b[1] - c[1]) + (b[0] ** 2 + b[1] ** 2) * (c[1] - a[1]) + (c[0] ** 2 + c[1] ** 2) * (a[1] - b[1])) / d
    uy = ((a[0] ** 2 + a[1] ** 2) * (c[0] - b[0]) + (b[0] ** 2 + b[1] ** 2) * (a[0] - c[0]) + (c[0] ** 2 + c[1] ** 2) * (b[0] - a[0])) / d
    return ux, uy, hypot(a[0] - ux, a[1] - uy)


def circular_pieces(arc, tolerance=0.2):
    """A fillet's arc as one cubic, or as two on the same circle when the one
    cubic leaves its circle by more than tolerance: over a half turn it leaves
    it by about 1.8% of the radius (0.5 units at a radius of 30), two by 0.03%.
    Only an arc that needs it is split, because the bowl balance measures the
    corners the fillets make."""
    p0, h0, h1, p3 = arc.points
    cc = circumcircle(arc)
    if cc is None or max(abs(hypot(*sub(arc.at(k / 32), cc[:2])) - cc[2]) for k in range(33)) <= tolerance:
        return [arc.points]
    theta = acos(max(-1.0, min(1.0, dot(unit(sub(h0, p0)), unit(sub(p3, h1))))))
    # The standard handle puts the cubic's midpoint on the circle.
    mid = arc.at(0.5)
    tangent = unit(sub(add(p3, h1), add(h0, p0)))
    handle = 4 / 3 * tan(theta / 8) * cc[2]
    return [
        (p0, add(p0, mul(unit(sub(h0, p0)), handle)), sub(mid, mul(tangent, handle)), mid),
        (mid, add(mid, mul(tangent, handle)), sub(p3, mul(unit(sub(p3, h1)), handle)), p3),
    ]


def fit_ellipse(P_):
    """Least-squares axis-aligned ellipse; returns (cx, cy), (a, b), worst error or None."""
    m = P_.mean(0)
    Q = P_ - m
    A = np.c_[Q[:, 0] ** 2, Q[:, 1] ** 2, Q[:, 0], Q[:, 1]]
    try:
        sol, *_ = np.linalg.lstsq(A, np.ones(len(Q)), rcond=None)
    except np.linalg.LinAlgError:
        return None
    a2, c2, d, e = sol
    if a2 <= 0 or c2 <= 0:
        return None
    cx, cy = -d / (2 * a2), -e / (2 * c2)
    k = 1 + a2 * cx * cx + c2 * cy * cy
    if k <= 0:
        return None
    ra, rb = (k / a2) ** 0.5, (k / c2) ** 0.5
    rho = np.hypot((Q[:, 0] - cx) / ra, (Q[:, 1] - cy) / rb)
    return (cx + m[0], cy + m[1]), (ra, rb), float(np.abs(rho - 1).max() * min(ra, rb))


def fillet_radius(pts, turning, r_circle):
    """The radius a fillet gets again: a circle at sqrt(a b) of the upright's
    slightly elliptical fillet (the text stage stretched it with its letter)."""
    if abs(turning) < 30:
        return r_circle
    fe = fit_ellipse(pts)
    if fe is None or not 0.8 < fe[1][0] / fe[1][1] < 1.25:
        return r_circle
    return sqrt(fe[1][0] * fe[1][1])


def find_arcs(segs, rmax, s=None):
    """Maximal co-circular runs of curve segments that look like fillets.

    Returns (start index, count, (cx, cy, r), turning) with tangent neighbours
    on both sides. A run is a fillet only where its neighbours are straight or
    much flatter than itself (a native small curve, the top of a delta hook,
    continues into similar curvature)."""
    n = len(segs)
    circ = [circumcircle(sg.seg) if not sg.is_line() else None for sg in segs]

    def same(i, j):
        a, b = circ[i], circ[j]
        if a is None or b is None or a[2] > 1.6 * rmax or b[2] > 1.6 * rmax:
            return False
        return is_g1(segs[i], segs[j], 1.5)

    links = [same(i - 1, i) for i in range(n)]
    if all(links):
        return []
    arcs = []
    start = next(i for i in range(n) if not links[i])
    i = start
    visited = 0
    while visited < n:
        if circ[i] is None or segs[i].is_line():
            i = (i + 1) % n
            visited += 1
            continue
        run = [i]
        j = (i + 1) % n
        while links[j] and j != start and len(run) < n:
            run.append(j)
            j = (j + 1) % n
        visited += len(run)
        arcs.append(run)
        i = j
    out = []
    for run in arcs:
        if len(run) >= n:
            continue
        pts = np.array([segs[k].seg.at(t / 12) for k in run for t in range(13)])
        fc = T.fit_circle(pts)
        if fc is None:
            continue
        cx, cy, r, res = fc
        if not 1.5 <= r <= rmax or res > 0.09 * r + 0.3:
            continue
        turning = abs(T.seg_turning([segs[k].seg for k in run]))
        if not 10 <= turning <= 172:
            continue
        prev, first, last, nxt = segs[run[0] - 1], segs[run[0]], segs[run[-1]], segs[(run[-1] + 1) % n]
        if turn_at(prev, first) > 10 or turn_at(last, nxt) > 10:
            continue

        def straightish(sg, factor):
            if sg.is_line():
                return True
            cc = circumcircle(sg.seg)
            return cc is None or cc[2] > factor * r

        if turning > 120:
            # a big turn is a fillet only between straight strokes (an acute
            # tip); between curves it is a native round end (a pill counter)
            if not (straightish(prev, 5) and straightish(nxt, 5)):
                continue
        elif not (straightish(prev, 2.2) or straightish(nxt, 2.2)):
            continue
        out.append((run[0], len(run), (cx, cy, fillet_radius(pts, turning, r)), turning))
    return out


def defillet(segs, rmax, records, s):
    """Replace each fillet arc by its sharp corner.

    The corner is where the neighbours' tangents meet: a straight neighbour is
    extended to it, a curved one gets a straight leg along its end tangent.
    An arc stays as drawn where its corner would be ill-conditioned after the
    shear: an acute tip whose sheared fillet needs much more or much less
    tangent length than the upright leg (a slot end between near-parallel
    sides), or a corner on a curve that the re-fillet would flatten."""
    arcs = find_arcs(segs, rmax)
    if not arcs:
        return segs
    n = len(segs)
    in_arc = {}
    new_end = {}
    new_start = {}
    corner_at = {}
    legs_before = {}
    legs_after = {}
    for start, count, (cx, cy, r), turning in arcs:
        ip, inx = (start - 1) % n, (start + count) % n
        idx = [(start + k) % n for k in range(count)]
        if ip in idx or inx in idx or any(k in in_arc for k in idx) or ip in in_arc or inx in in_arc:
            continue
        prev, nxt = segs[ip], segs[inx]
        A, B = segs[idx[0]].p[0], segs[idx[-1]].p[-1]
        tA, tB = prev.seg.tangent(1), nxt.seg.tangent(0)
        det = cross(tA, tB)
        if abs(det) < 1e-4:
            continue
        lam = cross(sub(B, A), tB) / det
        mu = cross(tA, sub(B, A)) / det
        if lam <= 0 or mu <= 0 or lam > 12 * r or mu > 12 * r:
            continue
        # conditioning after the shear
        sa, sb = unit(shear_vec(tA, s)), unit(shear_vec(tB, s))
        turn_sh = degrees(acos(max(-1, min(1, dot(sa, sb)))))
        need_sh = r * tan(radians(min(turn_sh, 176)) / 2)
        leg = min(lam, mu)
        if turn_sh > 150 or turning > 150:
            continue
        if need_sh > 1.6 * leg + 1.0:
            continue
        curved = (not prev.is_line()) or (not nxt.is_line())
        if curved and need_sh < 0.75 * leg - 1.0:
            continue
        Pc = add(A, mul(tA, lam))
        for k in idx:
            in_arc[k] = True
        if prev.is_line():
            new_end[ip] = Pc
        else:
            legs_after[ip] = S((A, Pc))
        if nxt.is_line():
            new_start[inx] = Pc
            corner_at[inx] = r
        else:
            legs_before[inx] = S((Pc, B), corner=r)
        records.append({"r": round(r, 3), "turning": round(turning, 2), "inner": det > 0, "corner": Pc})
    out = []
    for i in range(n):
        if i in in_arc:
            continue
        if i in legs_before:
            out.append(legs_before[i])
        sg = segs[i]
        if i in new_start or i in new_end:
            p = list(sg.p)
            if i in new_start:
                p[0] = new_start[i]
            if i in new_end:
                p[-1] = new_end[i]
            sg = sg.clone(tuple(p))
            if i in corner_at:
                sg.corner = corner_at[i]
                sg.imp = False
        out.append(sg)
        if i in legs_after:
            out.append(legs_after[i])
    # a leg that continues a straight neighbour is one edge with it
    merged = []
    for sg in out:
        if merged and sg.is_line() and merged[-1].is_line() and sg.corner is None and turn_at(merged[-1], sg) < 0.05:
            merged[-1] = merged[-1].clone((merged[-1].p[0], sg.p[1]))
            continue
        merged.append(sg)
    return merged


# ------------------------------------------------------------------ stroke widths


def facing_width(sg, lines, stem):
    """Width of the straight stroke this edge belongs to: the distance to the
    nearest antiparallel edge across the ink, if one overlaps it enough."""
    p0, p1 = sg.p
    d = unit(sub(p1, p0))
    n_in = (d[1], -d[0])  # TrueType winding: ink on the right of travel
    length = norm(sub(p1, p0))
    best = None
    for q0, q1 in lines:
        e = unit(sub(q1, q0))
        # the two sides of a tapered diagonal (k, K, X) converge a little
        if dot(d, e) > -0.985:
            continue
        mid = mul(add(q0, q1), 0.5)
        w = dot(sub(mid, p0), n_in)
        if not 0.2 * stem < w < 2.0 * stem:
            continue
        a, b = sorted((dot(sub(q0, p0), d), dot(sub(q1, p0), d)))
        overlap = min(length, b) - max(0, a)
        if overlap < 0.25 * min(length, b - a):
            continue
        if best is None or w < best:
            best = w
    return best


def white_gap(sg, lines, limit):
    """Distance across the white to the nearest antiparallel edge, if under limit."""
    p0, p1 = sg.p
    d = unit(sub(p1, p0))
    n_out = (-d[1], d[0])
    length = norm(sub(p1, p0))
    best = None
    for q0, q1 in lines:
        e = unit(sub(q1, q0))
        if dot(d, e) > -0.99:
            continue
        mid = mul(add(q0, q1), 0.5)
        w = dot(sub(mid, p0), n_out)
        if not 0 < w < limit:
            continue
        a, b = sorted((dot(sub(q0, p0), d), dot(sub(q1, p0), d)))
        if min(length, b) - max(0, a) < 0.25 * min(length, b - a):
            continue
        if best is None or w < best:
            best = w
    return best


# ------------------------------------------------------------------ stroke correction


def outward(t):
    # TrueType winding: the ink lies right of travel, so outwards is left.
    return (-t[1], t[0])


def h_of(n, s):
    return sqrt(n[0] ** 2 + (n[1] - s * n[0]) ** 2) - 1


def STEM_BASE(s):
    """h_of at the stem direction: the correction a vertical stem edge takes."""
    return sqrt(1 + s * s) - 1


def corner_contrast(n):
    """sin 2 psi of an edge's upright normal: +1 in the middle of the corners
    the slant makes acute (top right, bottom left), -1 in the obtuse ones, 0
    at the stem and bar directions."""
    return 2 * n[0] * n[1]


def concave(sg):
    """A curve that turns left: the inside of a bowl or an arc (TrueType
    winding puts the ink on the right of travel)."""
    g = sg.seg
    return cross(g.tangent(0), g.tangent(1)) > 0 or cross(sub(g.points[1], g.points[0]), sub(g.points[-1], g.points[-2])) > 0


def make_delta(thickness, s, contrast=0.0, share=1.0):
    """Displacement of an outline point with outward normal n.

    h(n) = t/2 (|M^-T n| - 1) restores the upright perpendicular thickness of a
    stroke after the shear M. Moving each point by h(n) n alone would turn the
    tangent wherever h changes along a curve, and break G1 at every curve-line
    join; the envelope form h n + h'(phi) t keeps every tangent direction.

    In a bowl's corners the two sides of a stroke take different parts of
    that: share (cs on the counter side, 2 - cs outside), less what it would
    give a straight side, so a curve still meets its straight side exactly; and
    contrast, a touch more stroke in the acute corners and less in the
    obtuse ones, split evenly."""

    def h(n):
        base = h_of(n, s)
        out = thickness / 2 * base
        if share != 1.0:
            # zero at the stem and bar directions, where straight sides keep
            # the plain correction, so a curve meets them exactly
            out += thickness / 2 * (share - 1) * (base - STEM_BASE(s) * n[0] * n[0])
        if contrast:
            out += thickness / 2 * contrast * corner_contrast(n) * (base + 1)
        return out

    def disp(n, eps=1e-5):
        c, sn = cos(eps), sin(eps)
        a = (n[0] * c - n[1] * sn, n[0] * sn + n[1] * c)
        b = (n[0] * c + n[1] * sn, -n[0] * sn + n[1] * c)
        hp = (h(a) - h(b)) / (2 * eps)
        return (h(n) * n[0] - hp * n[1], h(n) * n[1] + hp * n[0])

    return disp


def _off_point(seg, t, disp):
    n = outward(seg.tangent(t))
    return add(seg.at(t), disp(n))


def _poly_gap(points, curve, count=24):
    poly = np.array([curve.at(k / count) for k in range(count + 1)])
    a, b = poly[:-1], poly[1:]
    ab = b - a
    L2 = np.maximum((ab * ab).sum(1), 1e-12)
    worst = 0.0
    for p in points:
        u = np.clip(((p - a) * ab).sum(1) / L2, 0, 1)
        d = np.hypot(*(a + ab * u[:, None] - p).T).min()
        worst = max(worst, float(d))
    return worst


def offset_quad(seg, delta, tol=0.06, depth=0):
    """Offset a quadratic by a direction-dependent distance; the result keeps its end tangents."""
    t0, t1 = seg.tangent(0), seg.tangent(1)
    q0, q2 = _off_point(seg, 0, delta), _off_point(seg, 1, delta)
    det = cross(t0, t1)
    curve = None
    if abs(det) > 1e-7:
        s_ = cross(sub(q2, q0), t1) / det
        u_ = cross(t0, sub(q2, q0)) / det
        if s_ > 0 and u_ > 0:
            curve = Segment((q0, add(q0, mul(t0, s_)), q2))
    if curve is None and (abs(det) <= 1e-7 or depth >= 3):
        n = outward(unit(add(t0, t1)))
        curve = Segment((q0, add(seg.points[1], delta(n)), q2))
    if curve is not None:
        exact = np.array([_off_point(seg, k / 8, delta) for k in range(1, 8)])
        if depth >= 3 or _poly_gap(exact, curve) <= tol:
            return [curve]
    a, b = seg.split(0.5)
    return offset_quad(a, delta, tol, depth + 1) + offset_quad(b, delta, tol, depth + 1)


def offset_curve(seg, delta):
    """Offset one curve. A curve tighter than the direction-dependent offset
    (a small native arc, where h + h'' exceeds its radius) would fold into a
    swallowtail; it moves each end with its handle instead, as a cubic, which
    keeps both end points and tangents of the envelope."""
    count = 16
    pts = [_off_point(seg, k / count, delta) for k in range(count + 1)]
    tans = [seg.tangent(k / count) for k in range(count + 1)]
    if all(dot(sub(b, a), t) > 0 for a, b, t in zip(pts, pts[1:], tans)):
        return offset_quad(seg, delta)
    p = seg.points
    if len(p) == 3:
        q0, c, q2 = p
        p = (q0, add(q0, mul(sub(c, q0), 2 / 3)), add(q2, mul(sub(c, q2), 2 / 3)), q2)
    s0, s1 = sub(pts[0], p[0]), sub(pts[-1], p[-1])
    return [Segment((add(p[0], s0), add(p[1], s0), add(p[2], s1), add(p[3], s1)))]


def _shift(sobj, delta_pt, start):
    """Move one end of a segment. A curve keeps both its end tangents: a
    quadratic's control point moves to where the tangents meet again (its one
    handle serves both ends), or the quadratic becomes a cubic."""
    p = list(sobj.p)
    if norm(delta_pt) < 1e-12:
        return
    if len(p) == 3:
        q0, c, q2 = p
        t0, t1 = unit(sub(c, q0)), unit(sub(q2, c))
        a0, a1 = norm(sub(c, q0)), norm(sub(q2, c))
        if start:
            q0 = add(q0, delta_pt)
        else:
            q2 = add(q2, delta_pt)
        m = _meet(q0, t0, q2, t1)
        if m is not None and 0 < m[0] < 3 * a0 + 1 and 0 < m[1] < 3 * a1 + 1:
            sobj.p = (q0, add(q0, mul(t0, m[0])), q2)
            return
        q0, c, q2 = p
        p = [q0, add(q0, mul(sub(c, q0), 2 / 3)), add(q2, mul(sub(c, q2), 2 / 3)), q2]
    if start:
        p[0] = add(p[0], delta_pt)
        if len(p) > 2:
            p[1] = add(p[1], delta_pt)
    else:
        p[-1] = add(p[-1], delta_pt)
        if len(p) > 2:
            p[-2] = add(p[-2], delta_pt)
    sobj.p = tuple(p)


def _as_cubic(p):
    if len(p) == 3:
        q0, c, q2 = p
        return [q0, add(q0, mul(sub(c, q0), 2 / 3)), add(q2, mul(sub(c, q2), 2 / 3)), q2]
    return list(p)


def _ramp(chain, gap, length, toward_end):
    """Spread a displacement over the last (toward_end) or first stretch of
    `length` along a chain of tangent curves: gap times a smoothstep of the
    arc length, zero with zero slope where the ramp starts, the whole gap
    with zero slope at the join. Each curve takes the ramp exactly, as a
    cubic, so its joins stay tangent and a convex stretch stays convex as
    long as the ramp is gentler than the curve."""
    if norm(gap) < 1e-9 or not chain:
        return
    lens = [sg.seg.length() for sg in chain]
    total = sum(lens)
    T = min(length, total)
    if T <= 1e-6:
        return

    def e(d):
        # d: distance from the join; 1 at the join, 0 from T on
        x = max(0.0, 1.0 - d / T)
        return x * x * (3 - 2 * x), (-6 * x * (1 - x) / T) if d < T else 0.0

    order = list(range(len(chain)))
    if toward_end:
        order.reverse()
    dist = 0.0
    for k in order:
        sg, L = chain[k], lens[k]
        near, far = dist, dist + L  # distances of this piece's join-side and far ends
        dist = far
        if near >= T:
            break
        en, dn = e(near)
        ef, df = e(far)
        # local parameter runs from the far end to the near end (toward_end)
        if toward_end:
            ea, da, eb, db = ef, -df * L, en, -dn * L
        else:
            ea, da, eb, db = en, dn * L, ef, df * L
        coef = (ea, ea + da / 3, eb - db / 3, eb)
        p = _as_cubic(sg.p)
        sg.p = tuple(add(q, mul(gap, c)) for q, c in zip(p, coef))


def min_radius(seg, count=6):
    """Smallest radius of curvature along a curve segment."""
    P_ = np.asarray(seg.points, float)
    if len(P_) == 2:
        return float("inf")
    best = float("inf")
    for k in range(count + 1):
        t = k / count
        if len(P_) == 3:
            d = 2 * ((1 - t) * (P_[1] - P_[0]) + t * (P_[2] - P_[1]))
            dd = 2 * (P_[2] - 2 * P_[1] + P_[0])
        else:
            d = 3 * ((1 - t) ** 2 * (P_[1] - P_[0]) + 2 * t * (1 - t) * (P_[2] - P_[1]) + t * t * (P_[3] - P_[2]))
            dd = 6 * ((1 - t) * (P_[2] - 2 * P_[1] + P_[0]) + t * (P_[3] - 2 * P_[2] + P_[1]))
        c = abs(d[0] * dd[1] - d[1] * dd[0])
        sp = float(np.hypot(*d))
        if c > 1e-12 and sp > 1e-9:
            best = min(best, sp**3 / c)
    return best


def normal_only(thickness, s):
    def disp(n):
        h = thickness / 2 * h_of(n, s)
        return (h * n[0], h * n[1])

    return disp


def folds(seg, delta, count=16):
    pts = [_off_point(seg, k / count, delta) for k in range(count + 1)]
    tans = [seg.tangent(k / count) for k in range(count + 1)]
    return any(dot(sub(b, a), t) <= 0 for a, b, t in zip(pts, pts[1:], tans))


def tight_runs(segs, limit_for, delta_for):
    """Runs of G1 curve segments tighter than the offset's own curvature
    (h + h'' reaches about 0.19 t): a small native arc, a slot end. A run
    starts where the envelope offset actually folds and takes in its tight
    neighbours, so it covers the whole small arc."""
    n = len(segs)
    seed = [(not sg.is_line()) and folds(sg.seg, delta_for(sg)) for sg in segs]
    if not any(seed):
        return []
    small = [(not sg.is_line()) and min_radius(sg.seg) < limit_for(sg) for sg in segs]
    tight = list(seed)
    for _ in range(n):
        grown = False
        for i in range(n):
            if tight[i] or not small[i]:
                continue
            if (tight[i - 1] and is_g1(segs[i - 1], segs[i], 1.5)) or (tight[(i + 1) % n] and is_g1(segs[i], segs[(i + 1) % n], 1.5)):
                tight[i] = True
                grown = True
        if not grown:
            break
    if all(tight):
        return []
    runs = []
    start = next(i for i in range(n) if not tight[i])
    i = (start + 1) % n
    cur = []
    for _ in range(n):
        if tight[i] and (not cur or is_g1(segs[cur[-1]], segs[i], 1.5)):
            cur.append(i)
        else:
            if cur:
                runs.append(cur)
            cur = [i] if tight[i] else []
        i = (i + 1) % n
    if cur:
        runs.append(cur)
    return runs


def _sign_changes(chain):
    """Curvature sign changes along a chain of curves, from each piece's
    control polygon (a convex polygon makes a convex curve)."""
    turns = []
    for sg in chain:
        turns += [t for t in _control_turns(sg.p) if abs(t) > 0.05]
    return sum(1 for a, b in zip(turns, turns[1:]) if a * b < 0)


def _ramp_or_not(chain, gap, length, toward_end):
    """Ramp the gap in along the chain unless that adds curvature sign
    changes; True when it did."""
    if not chain:
        return False
    before = [sg.p for sg in chain]
    count = _sign_changes(chain)
    _ramp(chain, gap, length, toward_end)
    if _sign_changes(chain) > count:
        for sg, p in zip(chain, before):
            sg.p = p
        return False
    return True


def _ramp_length(sg):
    return max(8.0, sg.w or 0.0)


def _curve_chain(pieces, segs, k, forward):
    """The fitted curve pieces of segment k and of the tangent curves beyond
    it, away from the join at k's start (forward) or end, in contour order."""
    n = len(pieces)
    chain = []
    for step in range(n):
        idx = (k + step) % n if forward else (k - step) % n
        if segs[idx].is_line():
            break
        if step and not is_g1(segs[idx - 1] if forward else segs[idx], segs[idx] if forward else segs[(idx + 1) % n], 1.5):
            break
        part = pieces[idx][0]
        chain = chain + part if forward else part + chain
    return chain


def offset_contour(segs, delta_for, thickness_for=None, s=None, taper=True):
    """delta_for(segment) gives that segment's displacement function.

    A tight run would fold under the envelope offset; it moves as a whole
    instead, each piece's ends with their handles, from the displacement its
    neighbour needs at one end to the other's at the far end. Beside a line
    that is the normal offset only (the line slides along itself)."""
    special = {}
    if thickness_for is not None:
        runs = tight_runs(segs, lambda sg: 0.21 * thickness_for(sg) + 1.0, delta_for)
        n = len(segs)
        for run in runs:
            first, last = segs[run[0]], segs[run[-1]]
            before, after = segs[run[0] - 1], segs[(run[-1] + 1) % n]
            nA = outward(first.seg.tangent(0))
            nB = outward(last.seg.tangent(1))
            w = thickness_for(first)
            dA = (normal_only(w, s) if before.is_line() else delta_for(first))(nA)
            dB = (normal_only(w, s) if after.is_line() else delta_for(last))(nB)
            lengths = [segs[k].seg.length() for k in run]
            total = sum(lengths) or 1.0
            acc = 0.0
            for k, L in zip(run, lengths):
                g0, g1 = acc / total, (acc + L) / total
                acc += L
                p = segs[k].p
                if len(p) == 3:
                    q0, c, q2 = p
                    p = (q0, add(q0, mul(sub(c, q0), 2 / 3)), add(q2, mul(sub(c, q2), 2 / 3)), q2)
                D0 = add(dA, mul(sub(dB, dA), g0))
                D1 = add(dA, mul(sub(dB, dA), g1))
                special[k] = (add(p[0], D0), add(p[1], D0), add(p[2], D1), add(p[3], D1))
    pieces = []
    for idx, sg in enumerate(segs):
        g = sg.seg
        delta = delta_for(sg)
        if idx in special:
            o = sg.clone(special[idx])
            o.od = unit(sub(g.points[-1], g.points[0]))
            pieces.append(([o], g.tangent(0), g.tangent(1)))
            continue
        if sg.is_line():
            t = g.tangent(0)
            dv = delta(outward(t))
            a, b = add(sg.p[0], dv), add(sg.p[1], dv)
            line = sg.clone((a, b))
            line.od = t
            line.ol = g.length()
            pieces.append(([line], t, t))
        else:
            fitted = offset_curve(g, delta)
            out = [sg.clone(fitted[0].points)]
            for f in fitted[1:]:
                o = S(f.points, imp=True)
                o.w = sg.w
                out.append(o)
            od = unit(sub(g.points[-1], g.points[0]))
            for o in out:
                o.od = od
            pieces.append((out, g.tangent(0), g.tangent(1)))
    n = len(pieces)
    for i in range(n):
        prev, nxt = pieces[i - 1][0], pieces[i][0]
        a, b = prev[-1].p[-1], nxt[0].p[0]
        gap = sub(b, a)
        if norm(gap) < 1e-9:
            continue
        ta, tb = pieces[i - 1][2], pieces[i][1]
        g1 = dot(ta, tb) > cos(radians(3.0)) or (is_g1(segs[i - 1], segs[i], 1.5) and not segs[i].sharp and segs[i].corner is None)
        if not g1:
            det = cross(ta, tb)
            if abs(det) > 1e-6:
                s_ = cross(gap, tb) / det
                meet = add(a, mul(ta, s_))
                if norm(sub(meet, a)) < 40 and norm(sub(meet, b)) < 40:
                    _shift(prev[-1], sub(meet, a), start=False)
                    _shift(nxt[0], sub(meet, b), start=True)
                    continue
            nxt.insert(0, S((a, b), sharp=True))
            continue
        # a smooth join between pieces of different widths: a line keeps its
        # direction and the curve follows it, so the join stays tangent
        # Beside a notch leg, which keeps its place, the curve's own offset
        # differs from the line's, and two curves with different bowl shares
        # end apart: the difference is ramped in along the curves over one
        # stroke width, as a smooth taper, instead of bending their ends.
        pl, nl = prev[-1].is_line(), nxt[0].is_line()
        if pl and not nl:
            target = add(a, mul(ta, dot(gap, ta)))
            if not (taper and _ramp_or_not(_curve_chain(pieces, segs, i, forward=True), sub(target, b), _ramp_length(segs[i]), toward_end=False)):
                _shift(nxt[0], sub(target, b), start=True)
            _shift(prev[-1], sub(target, a), start=False)
        elif nl and not pl:
            target = sub(b, mul(tb, dot(gap, tb)))
            if not (taper and _ramp_or_not(_curve_chain(pieces, segs, i - 1, forward=False), sub(target, a), _ramp_length(segs[i - 1]), toward_end=True)):
                _shift(prev[-1], sub(target, a), start=False)
            _shift(nxt[0], sub(target, b), start=True)
        else:
            mid = mul(add(a, b), 0.5)
            if pl or not taper or not _ramp_or_not(_curve_chain(pieces, segs, i - 1, forward=False), sub(mid, a), _ramp_length(segs[i - 1]), toward_end=True):
                _shift(prev[-1], sub(mid, a), start=False)
            if nl or not taper or not _ramp_or_not(_curve_chain(pieces, segs, i, forward=True), sub(mid, b), _ramp_length(segs[i]), toward_end=False):
                _shift(nxt[0], sub(mid, b), start=True)
    for k, (sg, piece) in enumerate(zip(segs, pieces)):
        if sg.is_line():
            continue
        refit_folded(sg, piece[0])
    return drop_reversed([s for piece in pieces for s in piece[0]])


def abs_turning(seg_list, per=12):
    total = 0.0
    last = None
    for g in seg_list:
        for k in range(per + 1):
            t = g.tangent(k / per)
            if last is not None:
                total += abs(degrees(atan2_c(cross(last, t), dot(last, t))))
            last = t
    return total


def atan2_c(y, x):
    from math import atan2

    return atan2(y, x)


def refit_folded(orig, out):
    """An offset curve whose joins moved its ends far enough to fold it (its
    tangent turns much more than the upright's) becomes one cubic between its
    new ends with the upright's end tangents."""
    g = orig.seg
    if abs_turning([o.seg for o in out]) <= abs_turning([g]) + 12:
        return
    S0, E = out[0].p[0], out[-1].p[-1]
    t0, t1 = g.tangent(0), g.tangent(1)
    chord = norm(sub(E, S0))
    if chord < 1e-6:
        out[1:] = []
        out[0].p = (S0, E)
        return
    m = _meet(S0, t0, E, t1)
    L0 = L1 = chord / 3
    if m is not None and 0 < m[0] < 2 * chord and 0 < m[1] < 2 * chord:
        L0, L1 = 2 / 3 * m[0], 2 / 3 * m[1]
    out[1:] = []
    out[0].p = (S0, add(S0, mul(t0, L0)), sub(E, mul(t1, L1)), E)


def _meet(p, u, q, v):
    """(a, b) with p + a u = q - b v, or None."""
    det = cross(u, v)
    if abs(det) < 1e-9:
        return None
    w = sub(q, p)
    return cross(w, v) / det, cross(u, w) / det


def drop_reversed(out):
    """A short leg next to a corner can be consumed by its neighbours' different
    offsets. Remove it and join its neighbours where their tangents meet."""
    changed = True
    while changed and len(out) > 3:
        changed = False
        n = len(out)
        for i, sg in enumerate(out):
            if sg.od is None:
                continue
            if dot(sub(sg.p[-1], sg.p[0]), sg.od) > 0.02 and sg.seg.length() > 0.05:
                continue
            a, b = out[i - 1], out[(i + 1) % n]
            ta, tb = a.seg.tangent(1), b.seg.tangent(0)
            pa, pb = a.p[-1], b.p[0]
            meet = mul(add(pa, pb), 0.5)
            det = cross(ta, tb)
            if abs(det) > 1e-6:
                s_ = cross(sub(pb, pa), tb) / det
                cand = add(pa, mul(ta, s_))
                if norm(sub(cand, pa)) < 15 and norm(sub(cand, pb)) < 15:
                    meet = cand
            if keep_notch(a, sg, b, meet):
                changed = True
                break
            _shift(a, sub(meet, pa), start=False)
            _shift(b, sub(meet, pb), start=True)
            if sg.corner is not None and b.corner is None:
                b.corner = sg.corner
            del out[i]
            changed = True
            break
    return out


def keep_notch(a, flat, b, meet):
    """A flat between two corners (the notch where a bowl meets a stem) that
    the offsets turned inside out keeps a short length in its own direction,
    between its two straight neighbours, so both of its corners survive."""
    if not (flat.is_line() and a.is_line() and b.is_line() and flat.ol and flat.ol >= 1.0):
        return False
    if flat.corner is None or b.corner is None or flat.od is None:
        return False
    ta, tb, od = a.seg.tangent(1), b.seg.tangent(0), flat.od
    ca, cb = cross(ta, od), cross(tb, od)
    if abs(cb) < 1e-6:
        return False
    beta_per_alpha = -ca / cb
    if beta_per_alpha <= 0:
        return False
    v = add(mul(tb, beta_per_alpha), ta)
    if dot(v, od) <= 0:
        return False
    length = max(0.6, 0.3 * flat.ol)
    alpha = length / norm(v)
    beta = alpha * beta_per_alpha
    P0, P1 = sub(meet, mul(ta, alpha)), add(meet, mul(tb, beta))
    if norm(sub(P0, a.p[0])) < alpha + 0.5 or norm(sub(b.p[1], P1)) < beta + 0.5:
        return False
    if dot(sub(P0, a.p[0]), ta) <= 0 or dot(sub(b.p[1], P1), tb) <= 0:
        return False
    a.p = (a.p[0], P0)
    flat.p = (P0, P1)
    b.p = (P1, b.p[1])
    return True


# ------------------------------------------------------------------ shear


def shear_pt(p, prm):
    return (p[0] + prm.s * (p[1] - prm.origin), p[1])


def shear_segs(segs, prm):
    for sg in segs:
        sg.p = tuple(shear_pt(q, prm) for q in sg.p)
    return segs


# ------------------------------------------------------------------ bowl balance


def _bezier_pts(P, t):
    """Points, first and second derivatives of one Bezier (2 to 4 points) at the parameters t."""
    P = np.asarray(P, float)
    t = np.asarray(t, float)[:, None]
    u = 1 - t
    if len(P) == 2:
        d = np.repeat((P[1] - P[0])[None], len(t), 0)
        return P[0] * u + P[1] * t, d, np.zeros_like(d)
    if len(P) == 3:
        pt = P[0] * u * u + 2 * P[1] * u * t + P[2] * t * t
        d = 2 * (u * (P[1] - P[0]) + t * (P[2] - P[1]))
        dd = np.repeat((2 * (P[2] - 2 * P[1] + P[0]))[None], len(t), 0)
        return pt, d, dd
    pt = P[0] * u**3 + 3 * P[1] * u * u * t + 3 * P[2] * u * t * t + P[3] * t**3
    d = 3 * (u * u * (P[1] - P[0]) + 2 * u * t * (P[2] - P[1]) + t * t * (P[3] - P[2]))
    dd = 6 * (u * (P[2] - 2 * P[1] + P[0]) + t * (P[3] - 2 * P[2] + P[1]))
    return pt, d, dd


# ------------------------------------------------------------------ fillets again


def refillet_contour(segs, log):
    """A true circular fillet at every recovered corner. Two fillets on a flat
    too short for both (the notch where a bowl meets a stem foot) share the
    flat in proportion and both shrink, so the upright's small step survives."""
    n = len(segs)
    bounds_ = []
    for i in range(n):
        a, b = segs[i - 1], segs[i]
        if b.corner is not None or b.sharp or not is_g1(a, b, 1.5):
            bounds_.append(i)
    if not any(segs[i].corner is not None for i in bounds_):
        return segs
    runs = []
    for j, st in enumerate(bounds_):
        en = bounds_[(j + 1) % len(bounds_)]
        idx = list(range(st, en)) if en > st else list(range(st, n)) + list(range(0, en))
        runs.append([segs[k] for k in idx])
    m = len(runs)
    need = []
    for j in range(m):
        r = runs[j][0].corner
        if r is None:
            need.append(0.0)
            continue
        ang = radians(T.turn_deg(runs[j - 1][-1].seg, runs[j][0].seg))
        need.append(r * tan(min(ang, radians(176)) / 2))
    budgets = []
    for j in range(m):
        L = sum(sg.seg.length() for sg in runs[j])
        avail = 0.94 * L
        a, b = need[j], need[(j + 1) % m]
        if a + b <= avail:
            slack = avail - a - b
            la = a + (slack / 2 if a else 0) + (slack / 2 if not b else 0)
            lb = b + (slack / 2 if b else 0) + (slack / 2 if not a else 0)
        else:
            la, lb = avail * a / (a + b), avail * b / (a + b)
        budgets.append((la, lb))
    curve_runs = []
    meta = []
    for run in runs:
        seg_objs = [sg.seg for sg in run]
        curve_runs.append(CurveRun(seg_objs))
        meta.append({id(o): sg for o, sg in zip(seg_objs, run)})
    changes = []
    for j in range(m):
        r = runs[j][0].corner
        if r is None:
            changes.append(None)
            continue
        cut, status = fillet(
            curve_runs[j - 1],
            curve_runs[j],
            r,
            1.0,
            1.0,
            limit_prev=budgets[j - 1][1],
            limit_next=budgets[j][0],
        )
        if cut is None:
            log.append({"status": status, "radius": r})
            changes.append(None)
            continue
        cc = circumcircle(cut[2])
        geo = {"centre": [round(cc[0], 3), round(cc[1], 3)], "start": [round(v, 3) for v in cut[2].points[0]], "end": [round(v, 3) for v in cut[2].points[-1]]} if cc else {}
        if cut[3] < r - 0.01:
            log.append({"status": "radius-limited", "radius": round(r, 3), "used": round(cut[3], 3), "turn": round(T.turn_deg(runs[j - 1][-1].seg, runs[j][0].seg), 1), **geo})
        else:
            log.append({"status": "rounded", "radius": round(r, 3), "used": round(cut[3], 3), **geo})
        changes.append(cut)
    out = []
    for j in range(m):
        begin = changes[j][1] if changes[j] else 0.0
        end = changes[(j + 1) % m][0] if changes[(j + 1) % m] else 1.0
        if begin >= end:
            log.append({"status": "overlap"})
            begin, end = 0.0, 1.0
        kept = curve_runs[j].between(begin, end) if (begin > 0 or end < 1) else list(curve_runs[j].segments)
        for sgm in kept:
            src = meta[j].get(id(sgm))
            if src is not None:
                out.append(src.clone(sgm.points, corner=None))
            else:
                out.append(S(sgm.points))
        nxt = changes[(j + 1) % m]
        if nxt is not None:
            out.extend(S(points) for points in circular_pieces(nxt[2]))
    return out


# ------------------------------------------------------------------ cleanup


def cleanup(segs):
    out = []
    pending = None
    for sg in segs:
        if sg.seg.length() < 0.02:
            if out:
                _shift(out[-1], sub(sg.p[-1], out[-1].p[-1]), start=False)
            if sg.corner is not None:
                pending = sg.corner
            continue
        if pending is not None and sg.corner is None:
            sg.corner = pending
        pending = None
        out.append(sg)
    if out and norm(sub(out[-1].p[-1], out[0].p[0])) > 1e-9:
        _shift(out[-1], sub(out[0].p[0], out[-1].p[-1]), start=False)
    changed = True
    while changed and len(out) > 2:
        changed = False
        for i in range(len(out)):
            a, b = out[i - 1], out[i]
            if a.is_line() and b.is_line() and turn_at(a, b) < 0.08 and b.corner is None:
                merged = a.clone((a.p[0], b.p[1]))
                if i == 0:
                    out = [merged] + out[1:-1]
                else:
                    out[i - 1 : i + 1] = [merged]
                changed = True
                break
    return out


def remove_cusps(segs, max_len=1.0):
    """Delete any segment under max_len that reverses direction (a cusp of a
    sub-unit scrap the offsets or warps folded) and join its neighbours."""
    changed = True
    while changed and len(segs) > 3:
        changed = False
        n = len(segs)
        for i in range(n):
            sg = segs[i]
            L = sg.seg.length()
            if L >= max_len:
                continue
            a, b = segs[i - 1], segs[(i + 1) % n]
            if max(turn_at(a, sg), turn_at(sg, b)) < 60 and L > 0.05:
                continue
            pa, pb = a.p[-1], b.p[0]
            ta, tb = a.seg.tangent(1), b.seg.tangent(0)
            meet = mul(add(pa, pb), 0.5)
            det = cross(ta, tb)
            if abs(det) > 1e-6:
                s_ = cross(sub(pb, pa), tb) / det
                cand = add(pa, mul(ta, s_))
                if norm(sub(cand, pa)) < 2 * max_len and norm(sub(cand, pb)) < 2 * max_len:
                    meet = cand
            _shift(a, sub(meet, pa), start=False)
            _shift(b, sub(meet, pb), start=True)
            if sg.corner is not None and b.corner is None:
                b.corner = sg.corner
            del segs[i]
            changed = True
            break
    return segs


def _rotate_handle(sg, start, direction):
    """Turn the handle at one end of a curve to the given unit direction (leaving that end)."""
    p = list(sg.p)
    if len(p) == 3:
        # a quadratic's one handle serves both ends; as a cubic each end turns alone
        q0, c, q2 = p
        p = [q0, add(q0, mul(sub(c, q0), 2 / 3)), add(q2, mul(sub(c, q2), 2 / 3)), q2]
    if start:
        L = norm(sub(p[1], p[0]))
        p[1] = add(p[0], mul(direction, L))
    else:
        L = norm(sub(p[-1], p[-2]))
        p[-2] = sub(p[-1], mul(direction, L))
    sg.p = tuple(p)


def enforce_g1(segs, limit=25.0):
    """Make every join under `limit` degrees exactly tangent. Every join of the
    upright is smooth, so a small kink here is a warp or offset artefact; a
    line keeps its direction and the curve beside it follows."""
    n = len(segs)
    fixed = 0
    for i in range(n):
        a, b = segs[i - 1], segs[i]
        ang = turn_at(a, b)
        if ang < 0.3 or ang > limit:
            continue
        ta, tb = a.seg.tangent(1), b.seg.tangent(0)
        if a.is_line() and b.is_line():
            continue
        if len(a.p) == 3 and len(b.p) == 3:
            # two quadratics: move the join onto the line between their handles
            ca, J, cb = a.p[1], a.p[2], b.p[1]
            la, lb = norm(sub(J, ca)), norm(sub(cb, J))
            if la + lb > 1e-9:
                Jn = add(ca, mul(sub(cb, ca), la / (la + lb)))
                a.p = (a.p[0], ca, Jn)
                b.p = (Jn, cb, b.p[2])
                fixed += 1
                continue
        if a.is_line() and len(b.p) == 3:
            J, c, e = b.p
            m = _meet(J, ta, e, unit(sub(e, c)))
            if m is not None and m[0] > 0 and m[1] > 0 and m[0] < 3 * norm(sub(c, J)) + 1:
                b.p = (J, add(J, mul(ta, m[0])), e)
                fixed += 1
                continue
        if b.is_line() and len(a.p) == 3:
            s0, c, J = a.p
            m = _meet(s0, unit(sub(c, s0)), J, tb)
            if m is not None and m[0] > 0 and m[1] > 0 and m[1] < 3 * norm(sub(J, c)) + 1:
                a.p = (s0, add(s0, mul(unit(sub(c, s0)), m[0])), J)
                fixed += 1
                continue
        if a.is_line():
            _rotate_handle(b, True, ta)
        elif b.is_line():
            _rotate_handle(a, False, tb)
        else:
            la = norm(sub(a.p[-1], a.p[-2]))
            lb = norm(sub(b.p[1], b.p[0]))
            d = unit(add(mul(ta, la), mul(tb, lb)))
            _rotate_handle(a, False, d)
            _rotate_handle(b, True, d)
        fixed += 1
    return fixed


def _control_turns(pts):
    """Signed turns (degrees) between the consecutive legs of a control polygon."""
    out = []
    for k in range(1, len(pts) - 1):
        u, v = sub(pts[k], pts[k - 1]), sub(pts[k + 1], pts[k])
        if norm(u) < 1e-9 or norm(v) < 1e-9:
            continue
        out.append(degrees(atan2_c(cross(u, v), dot(u, v))))
    return out


def is_wobble(sg, max_chord=1.5):
    """A sub-unit piece whose control polygon doubles back or snakes: an
    offset folded it, and the export grid would turn it into a loop."""
    if sg.is_line():
        return False
    chord = norm(sub(sg.p[-1], sg.p[0]))
    if chord >= max_chord:
        return False
    if chord < 0.3:
        # under the export grid's reach: its off-curve points would land
        # behind its ends
        return True
    turns = _control_turns(sg.p)
    if any(abs(t) > 100 for t in turns):
        return True
    return any(t > 5 for t in turns) and any(t < -5 for t in turns)


def smooth_wobbles(segs, max_chord=1.5):
    """Replace every run of wobbles. Where the tangents on either side meet
    ahead, by one quadratic tangent to both; where they do not, the run was
    a corner the offsets frayed: its neighbours meet at that corner, which
    is marked for a micro fillet. A run spans under a few units, so the
    outline moves by a fraction of a unit. Returns (segs, runs, corners)."""
    n = len(segs)
    if n < 4:
        return segs, 0, 0
    flags = [is_wobble(sg, max_chord) for sg in segs]
    if not any(flags) or all(flags):
        return segs, 0, 0
    # rotate so the list starts outside a run
    k0 = flags.index(False)
    segs = segs[k0:] + segs[:k0]
    flags = flags[k0:] + flags[:k0]
    out, i, runs, corners = [], 0, 0, 0
    while i < n:
        if not flags[i]:
            out.append(segs[i])
            i += 1
            continue
        j = i
        while j + 1 < n and flags[j + 1]:
            j += 1
        prev, nxt = out[-1], segs[(j + 1) % n]
        p0, p1 = segs[i].p[0], segs[j].p[-1]
        t0, t1 = prev.seg.tangent(1), nxt.seg.tangent(0)
        chord = norm(sub(p1, p0))
        m = _meet(p0, t0, p1, t1)
        run_corner = next((sg.corner for sg in segs[i : j + 1] if sg.corner is not None), None)
        runs += 1
        i = j + 1
        if m is not None and 0 < m[0] < 4 * chord + 0.5 and 0 < m[1] < 4 * chord + 0.5:
            piece = segs[i - 1].clone((p0, add(p0, mul(t0, m[0])), p1))
            piece.corner = run_corner
            out.append(piece)
            continue
        if m is not None and abs(m[0]) < 3 and abs(m[1]) < 3 and turn_at(prev, nxt) > 5:
            # a frayed corner: the neighbours meet at it, and it is rounded again
            q = add(p0, mul(t0, m[0]))
            _shift(prev, sub(q, prev.p[-1]), start=False)
            _shift(nxt, sub(q, nxt.p[0]), start=True)
            nxt.corner = max(1.0, run_corner or 0.0)
            corners += 1
            continue
        piece = segs[i - 1].clone((p0, p1))
        piece.corner = run_corner
        out.append(piece)
    return out, runs, corners


def round_line_kinks(segs, log):
    """Two straight edges meeting at a small kink (a grid scrap of the upright
    the slant turned further) get a micro fillet, as every join must be round."""
    kinks = False
    for i in range(len(segs)):
        a, b = segs[i - 1], segs[i]
        if a.is_line() and b.is_line() and b.corner is None and max(1.0, join_limit(a, b)) < turn_at(a, b) <= 25:
            b.corner = 1.0
            kinks = True
    if not kinks:
        return segs
    return remove_cusps(cleanup(refillet_contour(segs, log)))


def sanitize(segs):
    """Degenerate quadratics (an off-curve point on its on-curve neighbour, from
    integer export) become lines; sub-unit scraps are absorbed."""
    out = []
    head = []
    for sg in segs:
        if len(sg.p) == 3:
            p0, c, p2 = sg.p
            chord = sub(p2, p0)
            L = norm(chord)
            flat = abs(cross(chord, sub(c, p0))) / L if L > 1e-9 else 0
            if norm(sub(c, p0)) < 0.06 or norm(sub(c, p2)) < 0.06 or flat < 0.01:
                sg = sg.clone((p0, p2))
        if sg.seg.length() < 1.0:
            if out:
                _shift(out[-1], sub(sg.p[-1], out[-1].p[-1]), start=False)
            else:
                head.append(sg.p[0])
            continue
        if head and len(out) == 0:
            _shift(sg, sub(head[0], sg.p[0]), start=True)
            head.clear()
        out.append(sg)
    if out and norm(sub(out[-1].p[-1], out[0].p[0])) > 1e-9:
        _shift(out[-1], sub(out[0].p[0], out[-1].p[-1]), start=False)
    i = 0
    while len(out) > 3 and i < len(out):
        a, b = out[i - 1], out[i]
        if a.is_line() and b.is_line() and turn_at(a, b) < 0.15:
            merged = a.clone((a.p[0], b.p[1]))
            if i == 0:
                out = [merged] + out[1:-1]
            else:
                out[i - 1 : i + 1] = [merged]
            continue
        i += 1
    return out


# ------------------------------------------------------------------ checks


def sample_segs(segs, per=10):
    pts = []
    for sg in segs:
        g = sg.seg
        for k in range(per):
            pts.append(g.at(k / per))
    return np.array(pts)


def dense(segs, step=4.0):
    pts = []
    for sg in segs:
        g = sg.seg
        k = max(2, int(g.length() / step) + 1)
        for j in range(k):
            pts.append(g.at(j / k))
    return np.array(pts)


def hausdorff(A, B):
    """Discrete Hausdorff distance between two closed point chains (GEOS)."""
    from shapely.geometry import LineString

    return float(LineString(np.vstack([A, A[:1]])).hausdorff_distance(LineString(np.vstack([B, B[:1]]))))


def join_limit(a, b):
    # the Text audit's limit for an exported join, less a margin for the export
    la = norm(sub(a.p[-1], a.p[-2]))
    lb = norm(sub(b.p[1], b.p[0]))
    unit_ = 1024 / 8192
    qt = degrees(asin(min(1, 2**0.5 * unit_ / max(la, 1e-9))) + asin(min(1, 2**0.5 * unit_ / max(lb, 1e-9))))
    return max(5, 2 * qt + 2) - 1.5


def contour_ok(segs, up_area_sign):
    if len(segs) < 2:
        return "degenerate"
    for i in range(len(segs)):
        a, b = segs[i - 1], segs[i]
        ang = turn_at(a, b)
        if ang > max(1.0, join_limit(a, b)):
            return f"join {ang:.1f} at {tuple(round(v, 1) for v in b.p[0])}"
        if segs[i].seg.length() < 0.05:
            return "scrap"
    P_ = sample_segs(segs, 10)
    poly = Polygon(P_)
    if not poly.is_valid or poly.area <= 0:
        return "invalid"
    x, y = P_[:, 0], P_[:, 1]
    area = 0.5 * float(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))
    if area * up_area_sign <= 0:
        return "direction"
    return None


# ------------------------------------------------------------------ one contour


def _dbg(ctx, stage, segs):
    if ctx.get("debug"):
        ctx["debug"](stage, segs)


def bowl_shares(segs, ctx, small=False):
    """Each curve's share f of its stroke correction: cs on the inside of a
    bowl or an arc (a curve that turns left), 2 - cs outside.

    Where a run of same-turning curves meets an inflection or a slanted
    straight edge, the two sides' shares differ at the join, so f, and the
    corner contrast with it (cw), ramp in over one stroke width of the run.
    At a corner, and at a stem or bar side (where neither adds anything),
    they apply in full. A run under half the stroke (a joint, a kept fillet)
    is no bowl corner and takes neither, unless `small`: then it takes its
    split, and every curve the whole contrast (the cascade's second level,
    for a notch the first cannot draw)."""
    n = len(segs)
    if n < 2:
        return
    cs_of = ctx["faces"] if ctx.get("faces") else (lambda sg: ctx["cs"])
    turn = [None if sg.is_line() else concave(sg) for sg in segs]
    # a scrap of a curve (under a twentieth of the stroke) inside a run of the
    # other turning is a grid artefact of the upright, not an inflection
    for i, sg in enumerate(segs):
        if turn[i] is None or norm(sub(sg.p[-1], sg.p[0])) >= 0.05 * max(sg.w or 0.0, 1.0):
            continue
        a, b = turn[i - 1], turn[(i + 1) % n]
        if a is not None and a == b != turn[i] and is_g1(segs[i - 1], sg, 1.5) and is_g1(sg, segs[(i + 1) % n], 1.5):
            turn[i] = a

    def axis_line(sg):
        d = unit(sub(sg.p[1], sg.p[0]))
        return abs(d[0]) < 0.02 or abs(d[1]) < 0.02

    def free_end(i, j):
        """Is the join between segs[i] (inside the run) and its neighbour segs[j] free?"""
        a, b = (segs[j], segs[i]) if j == (i - 1) % n else (segs[i], segs[j])
        if not is_g1(a, b, 1.5) or b.corner is not None or b.sharp:
            return True
        nb = segs[j]
        return nb.is_line() and axis_line(nb)

    start = next((i for i in range(n) if turn[i] is None or turn[i - 1] is None or turn[i] != turn[i - 1] or not is_g1(segs[i - 1], segs[i], 1.5)), None)
    if start is None:
        start = 0
    runs, cur = [], []
    for k in range(n):
        i = (start + k) % n
        if turn[i] is None:
            if cur:
                runs.append(cur)
            cur = []
            continue
        if cur and (turn[i] != turn[cur[-1]] or not is_g1(segs[cur[-1]], segs[i], 1.5)):
            runs.append(cur)
            cur = []
        cur.append(i)
    if cur:
        runs.append(cur)
    for run in runs:
        lengths = [segs[k].seg.length() for k in run]
        total = sum(lengths)
        ramp0 = not free_end(run[0], (run[0] - 1) % n)
        ramp1 = not free_end(run[-1], (run[-1] + 1) % n)
        acc = 0.0
        for k, L in zip(run, lengths):
            sg = segs[k]
            mid = acc + L / 2
            acc += L
            r = max(sg.w or 0.0, 1.0)
            wt = 1.0 if (small or total >= 0.5 * r) else 0.0
            if ramp0:
                wt *= min(1.0, mid / r)
            if ramp1:
                wt *= min(1.0, (total - mid) / r)
            cs = cs_of(sg)
            sg.f = 1 + ((cs if turn[k] else 2 - cs) - 1) * wt
            sg.cw = 1.0 if small else wt


def slant_contour(base, level, ctx):
    """One contour at one cascade level; base is the sanitized upright list of S."""
    label, use_fillets, use_corr, use_bal, taper = LEVELS[level]
    prm = ctx["prm"]
    fillet_log = []
    segs = [sg.clone(sg.p) for sg in base]
    for i in range(len(segs)):
        segs[i].sharp = not is_g1(segs[i - 1], segs[i], 1.5)
    records = []
    if use_fillets and ctx.get("defillet", True):
        segs = defillet(segs, ctx["rmax"], records, prm.s)
        # a join the upright turned through sub-unit scraps (absorbed by
        # sanitize) is a corner; it gets a micro fillet like any other
        for i in range(len(segs)):
            a, b = segs[i - 1], segs[i]
            if b.corner is None and turn_at(a, b) > 25:
                b.corner = 1.0
    if level == len(LEVELS) - 1:
        # the plain slant keeps the upright's joins; the grid's sub-unit
        # scraps it turns further are straightened as everywhere else
        segs = remove_cusps(cleanup(shear_segs(segs, prm)))
        enforce_g1(segs)
        segs = round_line_kinks(segs, fillet_log)
        return segs, records, fillet_log
    if use_corr and ctx["correct"]:
        lines = ctx["lines"]
        stem = ctx["stem"]
        for sg in segs:
            w = None
            if sg.is_line() and sg.seg.length() > 8:
                w = facing_width(sg, lines, stem)
            sg.w = w if w is not None else ctx["t_curve"]
        # a notch (a short flat between two corners, where a bowl meets a
        # stem) and its short legs keep their place: corrected, the leg's
        # corner would slide along the flat by h / sin(angle) and eat it
        n_ = len(segs)
        for i, sg in enumerate(segs):
            nxt = segs[(i + 1) % n_]
            if sg.is_line() and sg.corner is not None and nxt.corner is not None and sg.seg.length() < 30:
                sg.w = 0.0
                for nb in (segs[i - 1], nxt):
                    if nb.is_line() and nb.seg.length() < 8:
                        nb.w = 0.0
        balanced = use_bal and prm.balance
        if balanced:
            bowl_shares(segs, ctx, small=level == 1)
        cache = {}

        def delta_for(sg):
            w = sg.w
            if not sg.is_line():
                key = (round(w, 3), round(sg.f, 4), round(sg.cw, 4)) if balanced else round(w, 3)
                if key not in cache:
                    cache[key] = make_delta(w, prm.s, prm.contrast * sg.cw, sg.f) if balanced else make_delta(w, prm.s)
                return cache[key]
            if sg.seg.length() > 8:
                # a narrow white slot cannot take the whole correction
                hmax = abs(w / 2 * h_of(outward(sg.seg.tangent(0)), prm.s))
                if hmax > 0.05:
                    gap = white_gap(sg, lines, 1.5 * 2 * hmax + 0.5)
                    if gap is not None:
                        w *= max(0.0, min(1.0, gap / (1.5 * 2 * hmax + 0.5)))
            key = round(w, 3)
            if key not in cache:
                cache[key] = make_delta(w, prm.s)
            return cache[key]

        segs = offset_contour(segs, delta_for, lambda sg: sg.w, prm.s, taper=taper)
        _dbg(ctx, "offset", segs)
    shear_segs(segs, prm)
    _dbg(ctx, "shear", segs)
    segs = cleanup(segs)
    segs = remove_cusps(segs)
    if use_fillets:
        segs = refillet_contour(segs, fillet_log)
        _dbg(ctx, "refillet", segs)
    segs = cleanup(segs)
    segs = remove_cusps(segs)
    segs, _, corners = smooth_wobbles(segs)
    if corners:
        segs = remove_cusps(cleanup(refillet_contour(segs, fillet_log)))
    enforce_g1(segs)
    segs = round_line_kinks(segs, fillet_log)
    return segs, records, fillet_log


# ------------------------------------------------------------------ bowl thickness


def _normals_and_points(segs, per=16):
    P_, N_ = [], []
    for sg in segs:
        g = sg.seg
        for k in range(per):
            t = k / per
            P_.append(g.at(t))
            N_.append(outward(g.tangent(t)))
    return np.array(P_), np.array(N_)


def stroke_sections(counter, host):
    """(normal angle, thickness) of the bowl's real cross-sections: each counter
    point to its nearest outer point, kept only where the two tangents are
    parallel (not at a junction, a waist or an arm)."""
    P_, N_ = _normals_and_points(counter)
    H_, HN = _normals_and_points(host, 24)
    psi, d = [], []
    for p, n in zip(P_, N_):
        dist = np.hypot(*(H_ - p).T)
        j = int(dist.argmin())
        if abs(n[0] * HN[j, 1] - n[1] * HN[j, 0]) > sin(radians(15)) or n[0] * HN[j, 0] + n[1] * HN[j, 1] > 0:
            continue
        psi.append(atan2_c(n[1], n[0]))
        d.append(dist[j])
    return np.array(psi), np.array(d)


def quadrant_radii(segs, s=0.0, smooth=7.5, step=0.75):
    """Tightest radius of curvature in each quadrant of a contour (TL, TR, BR,
    BL), smoothed over `smooth` units of arc, in the frame deslanted by s."""
    P_, K = [], []
    for sg in segs:
        g = sg.seg
        if g.points[0] == g.points[-1]:
            continue
        L = max(g.length(), 1e-6)
        n = max(2, int(L / step))
        t = np.arange(n) / n
        pt, d, dd = _bezier_pts(g.points, t)
        sp = np.hypot(d[:, 0], d[:, 1])
        k = np.where(sp > 1e-9, (d[:, 0] * dd[:, 1] - d[:, 1] * dd[:, 0]) / np.maximum(sp, 1e-9) ** 3, 0.0)
        if len(g.points) == 2:
            k = np.zeros(n)
        P_.append(pt)
        K.append(k)
    if not P_:
        return None
    P_, K = np.vstack(P_), np.concatenate(K)
    w = max(1, int(smooth / step))
    ker = np.ones(2 * w + 1) / (2 * w + 1)
    Ks = np.abs(np.convolve(np.concatenate([K[-w:], K, K[:w]]), ker, mode="valid"))
    cy = (P_[:, 1].min() + P_[:, 1].max()) / 2
    X = P_[:, 0] - s * (P_[:, 1] - cy)
    cx = (X.min() + X.max()) / 2
    out = []
    for mx, my in ((-1, 1), (1, 1), (1, -1), (-1, -1)):
        m = ((X - cx) * mx > 0) & ((P_[:, 1] - cy) * my > 0)
        if not m.any() or Ks[m].max() <= 0:
            return None
        out.append(1 / Ks[m].max())
    return out


def balance_ratio(segs, s=0.0):
    """Obtuse over acute corners: (TL + BR) / (TR + BL) of the tightest radii."""
    q = quadrant_radii(segs, s)
    return None if q is None else (q[0] + q[2]) / (q[1] + q[3])


# ------------------------------------------------------------------ one glyph


def stem_lines(segs):
    return [sg.p for sg in segs if sg.is_line() and sg.seg.length() > 8]


def tittle_x(out_contours, dot_c, prm):
    """x of the slanted stem axis at the dot's height, for a dot that sits over
    or under a straight stem: the midline of the stem's two long edges."""
    cx, cy = dot_c
    best_dist, best_axis = None, None
    for segs in out_contours:
        for i, a in enumerate(segs):
            if not a.is_line():
                continue
            ya = sorted((a.p[0][1], a.p[1][1]))
            if ya[1] - ya[0] < 60:
                continue
            da = unit(sub(a.p[1], a.p[0]))
            for b in segs:
                if b is a or not b.is_line():
                    continue
                db = unit(sub(b.p[1], b.p[0]))
                if dot(da, db) > -0.9995:
                    continue
                yb = sorted((b.p[0][1], b.p[1][1]))
                if yb[1] - yb[0] < 60:
                    continue
                lo, hi = max(ya[0], yb[0]), min(ya[1], yb[1])
                if hi - lo < 40:
                    continue

                def x_at(seg, y):
                    (x0, y0), (x1, y1) = seg.p
                    return x0 + (x1 - x0) * (y - y0) / (y1 - y0)

                ym = (lo + hi) / 2
                width = abs(x_at(a, ym) - x_at(b, ym))
                if not 20 < width < 260:
                    continue
                # the axis, extended to the dot's height
                xa, xb = x_at(a, cy), x_at(b, cy)
                axis = (xa + xb) / 2
                dist = min(abs(cy - lo), abs(cy - hi))
                # only a dot that already sits on this stem (i, j, !): a
                # dieresis over a bowl stays at its own sheared centre
                expected = cx + prm.s * (cy - prm.origin)
                if abs(axis - expected) > max(3.0, 0.08 * width):
                    continue
                if best_dist is None or dist < best_dist:
                    best_dist, best_axis = dist, axis
    return best_axis


def tune_bowls(hosts, bases, ctxs, results, run, prm):
    """Give every bowl the same balance. The share cs of the curves' stroke
    correction a counter takes (the outer curves facing it take 2 - cs) is
    searched per counter until the counter's obtuse/acute corner ratio is
    prm.target times the upright counter's; a counter that cannot reach it
    keeps the nearest end of [prm.cs_min, prm.cs_max]. An outer curve takes
    the share of the counter it faces."""
    for i, js in hosts.items():
        ups = {j: balance_ratio(bases[j]) for j in js}
        js = [j for j in js if ups[j]]
        if not js:
            continue
        share = {j: prm.cs for j in js}
        if len(js) > 1:
            from shapely.geometry import LineString

            rings = {j: LineString(np.vstack([T.sample_contour(Contour([sg.seg for sg in bases[j]]), 6)] * 1)) for j in js}

            def faces(sg, rings=rings, share=share):
                p = Point(*sg.seg.at(0.5))
                return share[min(rings, key=lambda j: rings[j].distance(p))]

            ctxs[i]["faces"] = faces
        for _ in range(2 if len(js) > 1 else 1):
            for j in js:

                def miss(cs, j=j):
                    share[j] = cs
                    ctxs[j]["cs"] = cs
                    if len(js) == 1:
                        ctxs[i]["cs"] = cs
                    results.clear()
                    segs = run(j)[0]
                    r = balance_ratio(segs, prm.s) if segs else None
                    return None if r is None else r / ups[j] - prm.target

                a, b = share[j], share[j] - 0.4
                fa, fb = miss(a), miss(b)
                best = (abs(fa), a) if fa is not None else (9, a)
                for _ in range(6):
                    if fa is None or fb is None or abs(fb - fa) < 1e-6:
                        break
                    if abs(fb) < best[0]:
                        best = (abs(fb), b)
                    if abs(fb) < 0.005:
                        break
                    c = max(prm.cs_min, min(prm.cs_max, b - fb * (b - a) / (fb - fa)))
                    a, fa, b = b, fb, c
                    fb = miss(b)
                if fb is not None and abs(fb) < best[0]:
                    best = (abs(fb), b)
                miss(best[1])
        results.clear()


def italic_glyph(cs, prm, info, name=None, checker=None):
    """cs: upright contours (ttgeom.Contour, 1024 units). Returns contours and levels."""
    dots, body, slots = [], [], []
    for c in cs:
        if prm.dots and is_circle(c):
            slots.append(("dot", len(dots)))
            dots.append(c)
        else:
            slots.append(("body", len(body)))
            body.append(c)
    info["dots"] = len(dots)
    stem = info["stem"]
    rmax = info["rmax"]
    polys = [Polygon(T.sample_contour(c, 8)).buffer(0) for c in body]
    islands = set()
    for i, pi_ in enumerate(polys):
        depth = sum(1 for j, pj in enumerate(polys) if j != i and pj.area > pi_.area and pj.contains(pi_.representative_point()))
        if depth >= 2:
            islands.add(i)
    bases = [sanitize([S(x.points, imp) for x, imp in zip(c.segs, c.implied)]) for c in body]
    smooth = set()
    for i, c in enumerate(body):
        if T.signed_area(c) <= 0:
            continue
        sg = bases[i]
        # a counter without corners: every small arc it has is its own round
        # end (a small zero), not a fillet, when it spans its width
        width = float(np.ptp(T.sample_contour(c, 8)[:, 0]))
        if all(is_g1(sg[k - 1], sg[k], 1.5) for k in range(len(sg))) and all(a[2][2] >= 0.25 * width for a in find_arcs(sg, rmax)):
            smooth.add(i)
    # every counter belongs to the smallest outer contour around it: a bowl
    hosts = {}
    for j, pj in enumerate(polys):
        if T.signed_area(body[j]) <= 0 or j in islands:
            continue
        around = [i for i, pi_ in enumerate(polys) if i != j and T.signed_area(body[i]) < 0 and pi_.contains(pj.representative_point())]
        if around:
            hosts.setdefault(min(around, key=lambda i: polys[i].area), []).append(j)
    # Curves take the stem, or a thinner part's own stroke (a mark, a small
    # figure), estimated per outer contour with its counters as 2 area /
    # perimeter, so an accent never changes the letter under it.
    def t_of(group):
        area = abs(sum(T.signed_area(body[k]) for k in group))
        perim = sum(T.perimeter(body[k]) for k in group)
        t_est = 2 * area / perim if perim else stem
        return stem if t_est >= 0.7 * stem else max(0.3 * stem, t_est)

    t_curve = {}
    for i in range(len(body)):
        if T.signed_area(body[i]) < 0 or not any(i in js for js in hosts.values()):
            group = [i] + hosts.get(i, [])
            for k in group:
                t_curve[k] = t_of(group)
    info["t_curve"] = round(min(t_curve.values() or [stem]), 2)
    # a bowl's curves are corrected with its own stroke: the median upright
    # cross-section between its counter and outer contour
    bowl_t = {}
    for i, js in hosts.items():
        for j in js:
            _, d = stroke_sections(bases[j], bases[i])
            if len(d) >= 16:
                bowl_t[j] = float(np.median(d))
        ts = [bowl_t[j] for j in js if j in bowl_t]
        if ts:
            bowl_t[i] = float(np.mean(ts))

    # stem lines of the defilleted upright, for the per-edge widths
    lines = []
    for b in bases:
        tmp = [sg.clone(sg.p) for sg in b]
        lines += stem_lines(defillet(tmp, rmax, [], prm.s))
    plains = [dense(shear_segs([sg.clone(sg.p) for sg in b], prm)) for b in bases]
    signs = [1 if T.signed_area(c) > 0 else -1 for c in body]
    ctxs = [
        {
            "prm": prm, "rmax": rmax, "stem": stem, "t_curve": bowl_t.get(ci, t_curve.get(ci, stem)), "lines": lines,
            "correct": ci not in islands, "defillet": ci not in smooth, "cs": prm.cs,
        }
        for ci in range(len(body))
    ]
    # allowed deviation from the plain shear: the correction and balance, and
    # the fillets' change of corner angle
    lim = 2.2 * (3.0 + 0.12 * stem + 0.25 * rmax)
    levels = [0] * len(body)
    results = {}
    groups = [[i] + js for i, js in hosts.items()]

    def run(ci):
        key = (ci, levels[ci])
        if key not in results:
            try:
                segs, rec, flog = slant_contour(bases[ci], levels[ci], ctxs[ci])
                why = contour_ok(segs, signs[ci]) if levels[ci] < len(LEVELS) - 1 else None
                dev = hausdorff(dense(segs), plains[ci]) if segs else 1e9
                if why is None and levels[ci] < len(LEVELS) - 1 and dev > lim:
                    why = f"deviation {dev:.1f} > {lim:.1f}"
            except Exception as exc:  # reported; the cascade continues
                segs, rec, why, dev, flog = None, [], f"error {exc!r}", 0, []
            results[key] = (segs, rec, why, dev, flog)
        return results[key]

    if prm.balance and prm.target:
        tune_bowls(hosts, bases, ctxs, results, run, prm)
        info["bowl_cs"] = {str(j): round(ctxs[j]["cs"], 3) for js in hosts.values() for j in js}

    def align_bowls():
        # both sides of a bowl share one balance: a contour that lost it takes
        # its whole bowl with it, so the stroke stays at its thickness
        nob = next(i for i, lv in enumerate(LEVELS) if lv[0] == "no balance")
        for g in groups:
            if max(levels[k] for k in g) >= nob:
                for k in g:
                    levels[k] = max(levels[k], nob)

    reasons = {}
    for _ in range(8):
        for ci in range(len(body)):
            while True:
                segs, rec, why, dev, _ = run(ci)
                if why is None or levels[ci] == len(LEVELS) - 1:
                    break
                reasons.setdefault(ci, []).append((LEVELS[levels[ci]][0], why))
                levels[ci] += 1
        align_bowls()
        outs = [run(ci)[0] for ci in range(len(body))]
        if checker is None:
            break
        provisional = [circle_contour(*shear_pt(dot_centre(c), prm), 2 * dot_radius(c), T.signed_area(c) < 0) for c in dots]
        drawn = [Contour([sg.seg for sg in s], [sg.imp for sg in s]) for s in outs]
        ordered = [drawn[i] if kind == "body" else provisional[i] for kind, i in slots]
        body_at = [k for k, (kind, _) in enumerate(slots) if kind == "body"]
        bad_pos = checker(ordered, body_at)
        bad = [body_at.index(k) for k in bad_pos]
        bad = [ci for ci in bad if levels[ci] < len(LEVELS) - 1]
        if not bad:
            break
        for ci in bad:
            reasons.setdefault(ci, []).append((LEVELS[levels[ci]][0], "export"))
            levels[ci] += 1
        align_bowls()
    outs = [run(ci)[0] for ci in range(len(body))]
    info["levels"] = [LEVELS[lv][0] for lv in levels]
    if reasons:
        info["fallbacks"] = {str(k): v for k, v in reasons.items()}
    info["recovered_corners"] = sum(len(run(ci)[1]) for ci in range(len(body)))
    info["fillets"] = [f for ci in range(len(body)) for f in run(ci)[4]]
    info["deviation"] = round(max([run(ci)[3] for ci in range(len(body))] or [0]), 2)
    out = [Contour([sg.seg for sg in s], [sg.imp for sg in s]) for s in outs]
    # dots: true circles; a tittle on its stem axis, a dot in a counter at its centre
    upright_polys = body
    info["dot_placement"] = []
    dot_out = []
    for c in dots:
        P_ = T.sample_contour(c, 16)
        x0, y0 = P_.min(0)
        x1, y1 = P_.max(0)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        host, host_area = -1, float("inf")
        for k, uc in enumerate(upright_polys):
            if T.signed_area(uc) > 0:
                poly = Polygon(T.sample_contour(uc, 8))
                if poly.is_valid and poly.contains(Point(cx, cy)) and poly.area < host_area:
                    host, host_area = k, poly.area
        how = "sheared centre"
        if host >= 0:
            Q = T.sample_contour(out[host], 32)
            ncx, ncy = (Q[:, 0].min() + Q[:, 0].max()) / 2, (Q[:, 1].min() + Q[:, 1].max()) / 2
            how = "counter centre"
        else:
            ncx, ncy = shear_pt((cx, cy), prm)
            ax = tittle_x(outs, (cx, cy), prm)
            if ax is not None:
                ncx = ax
                how = "stem axis"
        info["dot_placement"].append(how)
        # the upright's own circle, moved by a step on the export grid: its
        # diameter and roundness are the upright's exactly
        dx, dy = snap(ncx - cx), snap(ncy - cy)
        dot_out.append(Contour([Segment(tuple((q[0] + dx, q[1] + dy) for q in g.points)) for g in c.segs], list(c.implied)))
    # the upright's contour order
    return [out[i] if kind == "body" else dot_out[i] for kind, i in slots]


def dot_centre(c):
    P_ = T.sample_contour(c, 16)
    return tuple((P_.min(0) + P_.max(0)) / 2)


def dot_radius(c):
    P_ = T.sample_contour(c, 16)
    return float((np.ptp(P_[:, 0]) + np.ptp(P_[:, 1])) / 4)


def plain_glyph(cs, prm):
    out = []
    for c in cs:
        out.append(Contour([Segment(tuple(shear_pt(q, prm) for q in sg.points)) for sg in c.segs], list(c.implied)))
    return out


# ------------------------------------------------------------------ font level


def slant_class(name, decisions):
    base = name.split(".")[0]
    if name in DINISH_UPRIGHT or base in DINISH_UPRIGHT or base in UPRIGHT_EXTRA:
        return "upright"
    for key in (name, base, name.removesuffix(".data")):
        fam = decisions.get(key, {}).get("family")
        if fam in UPRIGHT_FAMILIES:
            return "upright"
    return "slant"


def measure_stems(font):
    """Upright stems (1024 units): H left stem, n left stem, at mid height."""
    out = {}
    for name, y in (("H", 200), ("n", 250)):
        cs = read_glyph(font, name)
        xs = []
        for c in cs:
            for g in c.segs:
                a, b = g.points[0], g.points[-1]
                if len(g.points) == 2 and (a[1] - y) * (b[1] - y) < 0:
                    xs.append(a[0] + (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]))
        xs.sort()
        out[name] = xs[1] - xs[0] if len(xs) >= 2 else 80
    return out


def a_family(font):
    gsub = font["GSUB"].table
    for fr in gsub.FeatureList.FeatureRecord:
        if fr.FeatureTag == "ss02":
            for li in fr.Feature.LookupListIndex:
                for st in gsub.LookupList.Lookup[li].SubTable:
                    if hasattr(st, "mapping"):
                        return dict(st.mapping)
    return {}


def fix_kerning(font, family):
    """The single-storey a (and a.ss02) takes o's left-side kerning; a.ss02 takes a's right side."""
    gpos = font["GPOS"].table
    singles = set(family) | set(family.values())
    changed = 0
    order = {g: i for i, g in enumerate(font.getGlyphOrder())}
    for lookup in gpos.LookupList.Lookup:
        if lookup.LookupType != 2:
            continue
        for st in lookup.SubTable:
            if st.Format == 2:
                c2 = st.ClassDef2.classDefs
                oc = c2.get("o", 0)
                if oc:
                    for g in singles:
                        if c2.get(g, 0) != oc:
                            c2[g] = oc
                            changed += 1
                cov = list(st.Coverage.glyphs)
                c1 = st.ClassDef1.classDefs
                for a, alt in family.items():
                    if a in cov and alt not in cov:
                        cov.append(alt)
                        if c1.get(a, 0):
                            c1[alt] = c1[a]
                        changed += 1
                st.Coverage.glyphs = sorted(cov, key=order.get)
            else:
                for first, ps in zip(st.Coverage.glyphs, st.PairSet):
                    recs = {r.SecondGlyph: r for r in ps.PairValueRecord}
                    if "o" not in recs:
                        continue
                    proto = recs["o"]
                    for g in sorted(singles):
                        r = deepcopy(proto)
                        r.SecondGlyph = g
                        recs[g] = r
                        changed += 1
                    ps.PairValueRecord = sorted(recs.values(), key=lambda r: order[r.SecondGlyph])
                    ps.PairValueCount = len(ps.PairValueRecord)
    return changed


# Pairs whose ink gap the slant can close (a descender under a hook, a
# bracket's corner over j, f's terminal against a raised letter).
KERN_PAIR_TEXTS = sorted(
    set(
        [a + b for a in "abcdefghijklmnopqrstuvwxyz" for b in "abcdefghijklmnopqrstuvwxyz"]
        + [a + b for a in "TVWYFPLKRAD" for b in "aeoyrj.,"]
        + [a + b for a in "abcdefghijklmnopqrstuvwxyz" for b in ")]}'\"?!.,:;"]
        + [a + b for a in "([{'\"¿¡/" for b in "abcdefghijklmnopqrstuvwxyzAJT"]
        + ["fä", "fö", "fü", "f)", "f]", "f}", "f'", "f\"", "f?", "f!", "f*", "7/", "/7", "/A", "ß'", "1'", "y)", "j)", "T,", "r,", "V)", "Y)"]
    )
)


def ink_gaps(font, texts, kern=True):
    """Ink gap between the two glyphs of each pair as shaped (font units)."""
    import uharfbuzz as hb
    from shapely.ops import unary_union
    from shapely import affinity
    from fontTools.pens.basePen import BasePen

    class _Flat(BasePen):
        def __init__(self, gs):
            super().__init__(gs)
            self.cs, self.cur = [], []

        def _moveTo(self, p):
            self.cur = [p]

        def _lineTo(self, p):
            self.cur.append(p)

        def _qCurveToOne(self, b, c):
            a = self.cur[-1]
            for k in range(1, 9):
                t = k / 8
                self.cur.append(((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * b[0] + t * t * c[0], (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * b[1] + t * t * c[1]))

        def _closePath(self):
            self.cs.append(self.cur)
            self.cur = []

        _endPath = _closePath

    buf_ = BytesIO()
    font.save(buf_)
    hbf = hb.Font(hb.Face(buf_.getvalue()))
    gs = font.getGlyphSet()
    order = font.getGlyphOrder()
    cache = {}

    def poly(n):
        if n not in cache:
            p = _Flat(gs)
            gs[n].draw(p)
            ps = [Polygon(c).buffer(0) for c in p.cs if len(c) > 2]
            cache[n] = unary_union(ps) if ps else None
        return cache[n]

    out = {}
    for text in texts:
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(hbf, buf, {"kern": kern})
        if len(buf.glyph_infos) != 2:
            continue
        x, geoms, names = 0, [], []
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            names.append(order[info.codepoint])
            g = poly(order[info.codepoint])
            geoms.append(None if g is None else affinity.translate(g, x + pos.x_offset, pos.y_offset))
            x += pos.x_advance
        if None in geoms or geoms[0].is_empty or geoms[1].is_empty:
            continue
        out[text] = (tuple(names), float(geoms[0].distance(geoms[1])))
    return out


def italic_pair_kerning(font, upright, keep=0.7, target=0.8):
    """Kern apart the pairs whose ink gap the slant closed below `keep` of the
    upright's, to `target` of it: an extra pair lookup in the kern feature."""
    from fontTools.otlLib.builder import buildPairPosGlyphsSubtable, buildValue, buildLookup

    gu, gi = ink_gaps(upright, KERN_PAIR_TEXTS), ink_gaps(font, KERN_PAIR_TEXTS)
    pairs = {}
    rows = []
    for text, (names, a) in gu.items():
        if text not in gi or a <= 0:
            continue
        b = gi[text][1]
        if b < keep * a:
            value = int(round(target * a - b))
            if value > 0 and names not in pairs:
                pairs[names] = value
                rows.append([text, round(a), round(b), value])
    if not pairs:
        return rows
    gpos = font["GPOS"].table
    kern_lookups = [li for fr in gpos.FeatureList.FeatureRecord if fr.FeatureTag == "kern" for li in fr.Feature.LookupListIndex]
    flag = gpos.LookupList.Lookup[kern_lookups[0]].LookupFlag if kern_lookups else 0
    subtable = buildPairPosGlyphsSubtable({k: (buildValue({"XAdvance": v}), None) for k, v in sorted(pairs.items())}, font.getReverseGlyphMap())
    lookup = buildLookup([subtable], flags=flag)
    gpos.LookupList.Lookup.append(lookup)
    gpos.LookupList.LookupCount = len(gpos.LookupList.Lookup)
    index = gpos.LookupList.LookupCount - 1
    for fr in gpos.FeatureList.FeatureRecord:
        if fr.FeatureTag == "kern":
            fr.Feature.LookupListIndex.append(index)
            fr.Feature.LookupCount = len(fr.Feature.LookupListIndex)
    return rows


def shear_anchors(font, slanted, prm):
    upm = font["head"].unitsPerEm
    k = upm / 1024
    origin = prm.origin * k

    def mv(anchor, name):
        if anchor is None or name not in slanted:
            return
        anchor.XCoordinate = round(anchor.XCoordinate + prm.s * (anchor.YCoordinate - origin))

    for lookup in font["GPOS"].table.LookupList.Lookup:
        if lookup.LookupType != 4:
            continue
        for sub_ in lookup.SubTable:
            for name, rec in zip(sub_.MarkCoverage.glyphs, sub_.MarkArray.MarkRecord):
                mv(rec.MarkAnchor, name)
            for name, rec in zip(sub_.BaseCoverage.glyphs, sub_.BaseArray.BaseRecord):
                for a in rec.BaseAnchor:
                    mv(a, name)


def single_storey_anchors(font, upright, family):
    """A base anchor of the a family follows its new drawing. It moves with
    the bounding-box centre of X.ss02 against X, and by how much further the
    precomposed single-storey forms (aacute.ss02 and the rest, which the
    italic draws) set their marks from the base than the double-storey ones,
    measured apart for marks above and below. A combining mark on the
    italic a then sits where the precomposed letter has it."""
    upm = upright["head"].unitsPerEm
    xh = upright["OS/2"].sxHeight

    def centre(name):
        g = upright["glyf"][name]
        g.recalcBounds(upright["glyf"])
        return (g.xMin + g.xMax) / 2

    def mark_offsets(name):
        """x of the marks above and below minus the x of the base's centre."""
        g = upright["glyf"][name]
        cs = read_glyph(upright, name) if not g.isComposite() else None
        if cs is None:
            from fontTools.pens.recordingPen import DecomposingRecordingPen
            from fontTools.pens.ttGlyphPen import TTGlyphPen

            rec = DecomposingRecordingPen(upright.getGlyphSet())
            upright.getGlyphSet()[name].draw(rec)
            pen = TTGlyphPen(None)
            rec.replay(pen)
            tmp = deepcopy(upright)
            tmp["glyf"][name] = pen.glyph()
            cs = read_glyph(tmp, name)
        unit = upm / 1024
        pts = [T.sample_contour(c, 8) * unit for c in cs]
        above = [p for p in pts if p[:, 1].min() > xh + 20 * unit]
        below = [p for p in pts if p[:, 1].max() < -20 * unit]
        body = [p for p in pts if not any(p is q for q in above + below)]
        if not body:
            return {}
        B = np.vstack(body)
        bx = (B[:, 0].min() + B[:, 0].max()) / 2
        out = {}
        for key, ms in (("above", above), ("below", below)):
            if ms:
                M_ = np.vstack(ms)
                out[key] = (M_[:, 0].min() + M_[:, 0].max()) / 2 - bx
        return out

    shift = {"above": [], "below": []}
    for name, alt in family.items():
        if name in ("a",) or name not in upright["glyf"].keys() or alt not in upright["glyf"].keys():
            continue
        d1, d2 = mark_offsets(name), mark_offsets(alt)
        for key in shift:
            if key in d1 and key in d2:
                shift[key].append(d2[key] - d1[key])
    extra = {k: (float(np.median(v)) if v else 0.0) for k, v in shift.items()}
    moved = 0
    for lookup in font["GPOS"].table.LookupList.Lookup:
        if lookup.LookupType != 4:
            continue
        for sub_ in lookup.SubTable:
            for name, rec in zip(sub_.BaseCoverage.glyphs, sub_.BaseArray.BaseRecord):
                alt = family.get(name)
                if not alt:
                    continue
                dx = centre(alt) - centre(name)
                for a in rec.BaseAnchor:
                    if a is not None:
                        a.XCoordinate += round(dx + extra["above" if a.YCoordinate > xh / 2 else "below"])
                        moved += 1
    return {"anchors": moved, "mark_shift": {k: round(v / (upm / 1024), 2) for k, v in extra.items()}}


STYLE_NAMES = {
    # style: (subfamily label, file and PostScript suffix, name ID 1)
    "Regular": ("Italic", "Italic", "DINDOT"),
    "Medium": ("Medium Italic", "MediumItalic", "DINDOT Medium"),
    "SemiBold": ("SemiBold Italic", "SemiBoldItalic", "DINDOT SemiBold"),
    "Bold": ("Bold Italic", "BoldItalic", "DINDOT"),
}


def file_style(style):
    return STYLE_NAMES[style][1]


def italic_metadata(font, style, prm):
    """Names 1/2/3/4/6/16/17, fsSelection, macStyle, caret and italic angle."""
    label, suffix, fam1 = STYLE_NAMES[style]
    version = font["name"].getDebugName(5).replace("Version ", "")
    vals = {
        1: fam1,
        2: "Bold Italic" if style == "Bold" else "Italic",
        3: f"DINDOT-{version}-{suffix}",
        4: f"DINDOT {label}",
        6: f"DINDOT-{suffix}",
        16: "DINDOT",
        17: label,
    }
    for key, value in vals.items():
        font["name"].removeNames(nameID=key)
        font["name"].setName(value, key, 3, 1, 0x409)
        font["name"].setName(value, key, 1, 0, 0)
    upm = font["head"].unitsPerEm
    font["post"].italicAngle = -prm.angle
    font["hhea"].caretSlopeRise = upm
    font["hhea"].caretSlopeRun = round(upm * prm.s)
    font["hhea"].caretOffset = -round(prm.s * prm.origin * upm / 1024)
    # PANOSE letterform: the oblique counterpart of the upright's (2-8 -> 9-15)
    # superscripts and subscripts sit on the slant: shifted along it
    os2 = font["OS/2"]
    os2.ySuperscriptXOffset = round(prm.s * os2.ySuperscriptYOffset)
    os2.ySubscriptXOffset = -round(prm.s * os2.ySubscriptYOffset)
    pan = font["OS/2"].panose
    if 2 <= pan.bLetterForm <= 8:
        pan.bLetterForm += 7
    bold = style == "Bold"
    font["OS/2"].fsSelection = (font["OS/2"].fsSelection & ~0b1100001) | 1 | (0x20 if bold else 0)
    font["OS/2"].fsSelection &= ~0x40  # not REGULAR
    font["head"].macStyle = 2 | (1 if bold else 0)


def make_checker(font, name, upright_font, source_name=None):
    """Per-contour check after export: every join within the Text audit limit,
    and the glyph's region topology equal to the upright's."""
    from build import normalized_outline
    from rounding import turn as r_turn, quantization_tolerance
    from audit_geometry import polygon_data, region, counts

    upm = font["head"].unitsPerEm
    up_counts = counts(region(polygon_data(upright_font, source_name or name)[0]))

    def check(contours, body_at):
        """Positions (in contour order) of slanted contours that fail."""
        glyph = emit_glyph(contours)
        font["glyf"][name] = glyph
        outline = normalized_outline(font, name)
        if len(outline) != len(contours):
            return list(body_at)
        bad = []
        for ci in body_at:
            c = outline[ci]
            for i, seg in enumerate(c):
                prev = c[i - 1]
                ang = degrees(r_turn(prev, seg)[0])
                lim = max(5, 2 * quantization_tolerance(prev, seg, upm) + 2)
                if ang > lim - 0.5:
                    bad.append(ci)
                    break
        if bad:
            return bad
        # flattened at the font's own units, no contour may touch or cross
        # itself, nor turn back on itself at a grid-sized point
        faults = glyph_faults(font, name)
        bad = [ci for ci in body_at if ci in faults]
        if bad:
            return bad
        polys, invalid = polygon_data(font, name)
        if invalid:
            return sorted({iv["contour"] for iv in invalid if iv["contour"] in body_at}) or list(body_at)
        if counts(region(polys)) != up_counts:
            return list(body_at)
        return []

    return check


def join_failures(font, name, glyph):
    """Joins of this glyph over the Text audit's limit, after export."""
    from build import normalized_outline
    from rounding import turn as r_turn, quantization_tolerance

    font["glyf"][name] = glyph
    upm = font["head"].unitsPerEm
    bad = 0
    for c in normalized_outline(font, name):
        for i, seg in enumerate(c):
            prev = c[i - 1]
            if degrees(r_turn(prev, seg)[0]) > max(5, 2 * quantization_tolerance(prev, seg, upm) + 2):
                bad += 1
    return bad


def italic_font(upright, style, prm, settings, decisions, aliases, only=None, report=None, log=print):
    """Return the unhinted italic TTFont built from an unhinted upright TTFont."""
    font = deepcopy(upright)
    radius = settings["radii"][style]
    stems = measure_stems(upright)
    glyf = font["glyf"]
    for g in glyf.glyphs.values():
        g.removeHinting()
    for tag in ["fpgm", "prep", "cvt ", "hdmx", "LTSH", "VDMX", "gasp"]:
        if tag in font and tag != "gasp":
            del font[tag]
    family = a_family(font)
    order = font.getGlyphOrder()
    rep = {"style": style, "stems": stems, "params": {k: v for k, v in vars(prm).items()}, "glyphs": {}}
    slanted = set()
    for name in order:
        if slant_class(name, decisions) == "slant":
            slanted.add(name)
    for name in order:
        cls = "slant" if name in slanted else "upright"
        if only and name not in only:
            continue
        if name in aliases:
            continue
        g = upright["glyf"][name]
        if g.isComposite() or g.numberOfContours <= 0 or cls == "upright":
            if g.isComposite() and cls == "slant":
                for comp in glyf[name].components:
                    comp.x = round(comp.x + prm.s * comp.y)
            rep["glyphs"][name] = {"class": cls if g.numberOfContours else "empty"}
            continue
        source_name = family.get(name, name)
        cs = read_glyph(upright, source_name)
        info = {
            "stem": stems["n"] if (name[:1].islower() and name[:1].isalpha()) else stems["H"],
            "rmax": 1.25 * radius + 6,
        }
        if prm.plain:
            outc = plain_glyph(cs, prm)
            info["levels"] = ["plain shear"] * len(cs)
        else:
            checker = make_checker(font, name, upright, source_name)
            outc = italic_glyph(cs, prm, info, name, checker)
        newg = emit_glyph(outc)
        # an on-curve point repeated changes nothing; the rest may hold a tangent
        dup = tidy_glyph(newg, duplicates_only=True)
        raw = deepcopy(newg)
        info["tidied_points"] = tidy_glyph(newg)
        if info["tidied_points"] and join_failures(font, name, newg) > join_failures(font, name, raw):
            # a point the grid made look redundant was holding a tangent
            newg, info["tidied_points"] = raw, 0
        info["tidied_points"] += dup
        tidied = deepcopy(newg)
        info["straightened"] = straighten_flips(newg)
        if info["straightened"]:
            # a straightened piece can land on its neighbour's point
            info["tidied_points"] += tidy_glyph(newg, duplicates_only=True)
            if join_failures(font, name, newg) > join_failures(font, name, tidied):
                newg, info["straightened"] = tidied, 0
        if not prm.plain:
            base_joins = join_failures(font, name, deepcopy(newg))

            def accept(g, base_joins=base_joins):
                # join_failures puts the trial glyph in the font for glyph_faults
                return join_failures(font, name, deepcopy(g)) <= base_joins and not glyph_faults(font, name)

            keep = []
            for f in info.get("fillets", []):
                if f.get("status") in ("rounded", "radius-limited") and f.get("centre"):
                    cx, cy = f["centre"]
                    a0 = atan2_c(f["start"][1] - cy, f["start"][0] - cx)
                    a1 = atan2_c(f["end"][1] - cy, f["end"][0] - cx)
                    da = (a1 - a0 + pi) % (2 * pi) - pi
                    keep += [(T.SCALE * (cx + f["used"] * cos(a0 + da * t / 16)), T.SCALE * (cy + f["used"] * sin(a0 + da * t / 16))) for t in range(17)]
            info["unflipped"] = unflip_glyph(newg, accept, keep=keep)
            if info["unflipped"]:
                # a merged run's new end can land on its neighbour's point
                info["tidied_points"] += tidy_glyph(newg, duplicates_only=True)
        glyf[name] = newg
        newg.recalcBounds(glyf)
        info["class"] = "slant"
        info["points"] = [len(upright["glyf"][name].coordinates), len(newg.coordinates)]
        rep["glyphs"][name] = info
    for name, base in aliases.items():
        if only and name not in only:
            continue
        glyf[name] = deepcopy(glyf[base])
        rep["glyphs"][name] = {"class": "alias", "of": base}
    for name in order:
        g = glyf[name]
        g.recalcBounds(glyf)
        font["hmtx"][name] = (upright["hmtx"][name][0], getattr(g, "xMin", 0) if g.numberOfContours else 0)
    rep["kerning_records_changed"] = fix_kerning(font, family)
    if not only and not prm.plain:
        rep["italic_pair_kerning"] = italic_pair_kerning(font, upright)
    rep["a_family_anchors_moved"] = single_storey_anchors(font, upright, family)
    shear_anchors(font, slanted, prm)
    italic_metadata(font, style, prm)
    font["OS/2"].recalcAvgCharWidth(font)
    font["head"].checkSumAdjustment = 0
    levels = {}
    for info in rep["glyphs"].values():
        for lv in info.get("levels", []):
            levels[lv] = levels.get(lv, 0) + 1
    rep["contour_levels"] = levels
    if report is not None:
        report.update(rep)
    return font


def hint_and_save(font, target, aliases, modified, hint=True):
    """ttfautohint with the upright's flags; aliases share their base's program."""
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    font.flavor = None
    font.save(target)
    if hint:
        hinted = target.with_suffix(".hinted.ttf")
        subprocess.run(
            [
                sys.executable, "-m", "ttfautohint",
                "--hinting-range-min=8", "--hinting-range-max=32", "--hinting-limit=32",
                "--stem-width-mode=nnn", "--increase-x-height=0", "--no-info",
                "--default-script=latn", str(target), str(hinted),
            ],
            check=True,
        )
        hinted.replace(target)
    web = TTFont(target, recalcTimestamp=False)
    for name, base in aliases.items():
        web["glyf"][name] = deepcopy(web["glyf"][base])
        web["hmtx"][name] = web["hmtx"][base]
    web["head"].modified = modified
    web.save(target)
    web = TTFont(target, recalcTimestamp=False)
    web.flavor = "woff2"
    web.save(target.with_suffix(".woff2"))
    return target


def tidy_glyph(glyph, duplicates_only=False):
    """Remove points the export grid made redundant: consecutive duplicates,
    on-curve points in the middle of a straight line (within half a unit),
    and the off-curve point of a quadratic that lies on its chord (within one
    unit), which is a straight piece."""
    if glyph.isComposite() or glyph.numberOfContours <= 0:
        return 0
    coords = list(glyph.coordinates)
    flags = list(glyph.flags)
    ends = list(glyph.endPtsOfContours)
    out_c, out_f, out_e = [], [], []
    removed = 0
    start = 0
    for e in ends:
        pts = [(tuple(coords[i]), flags[i] & 1) for i in range(start, e + 1)]
        start = e + 1
        changed = True
        while changed and len(pts) > 3:
            changed = False
            n = len(pts)
            for i in range(n):
                (p, on), (q, onq) = pts[i], pts[(i + 1) % n]
                # only two equal on-curve points are an exact duplicate: an
                # off-curve point can take an implied point with it
                if p == q and not (duplicates_only and not (on and onq)):
                    if not on and not onq:
                        pts[i] = (p, 1)
                        drop = (i + 1) % n
                    else:
                        drop = (i + 1) % n if on else i
                    del pts[drop]
                    removed += 1
                    changed = True
                    break
                if duplicates_only:
                    continue
                prv = pts[i - 1]
                if not on and onq and prv[1]:
                    a, b = prv[0], q
                    L = hypot(b[0] - a[0], b[1] - a[1])
                    if L > 0:
                        cr = abs((p[0] - a[0]) * (b[1] - a[1]) - (p[1] - a[1]) * (b[0] - a[0])) / L
                        dp = (p[0] - a[0]) * (b[0] - a[0]) + (p[1] - a[1]) * (b[1] - a[1])
                        if cr <= 1.0 and 0 < dp < L * L:
                            del pts[i]
                            removed += 1
                            changed = True
                            break
                if on and onq and prv[1]:
                    a, b = prv[0], q
                    L = hypot(b[0] - a[0], b[1] - a[1])
                    if L > 0:
                        cr = abs((p[0] - a[0]) * (b[1] - a[1]) - (p[1] - a[1]) * (b[0] - a[0])) / L
                        dp = (p[0] - a[0]) * (b[0] - a[0]) + (p[1] - a[1]) * (b[1] - a[1])
                        if cr < 0.5 and 0 < dp < L * L:
                            del pts[i]
                            removed += 1
                            changed = True
                            break
        out_c.extend(p for p, _ in pts)
        out_f.extend(1 if on else 0 for _, on in pts)
        out_e.append(len(out_c) - 1)
    if removed:
        from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates

        glyph.coordinates = GlyphCoordinates(out_c)
        glyph.flags = bytearray(out_f)
        glyph.endPtsOfContours = out_e
    return removed


def straighten_flips(glyph, max_kink=2.0):
    """A quadratic that turns against both of its curved neighbours by a
    grid-sized amount is a wobble of the offsets, not a drawn inflection:
    it becomes straight (its off-curve point moves onto its chord) when the
    joins it then makes stay within max_kink degrees. Returns the count."""
    if glyph.isComposite() or glyph.numberOfContours <= 0:
        return 0
    from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates

    coords = [tuple(c) for c in glyph.coordinates]
    flags = list(glyph.flags)
    fixed = 0
    start = 0
    for end in glyph.endPtsOfContours:
        idx = list(range(start, end + 1))
        start = end + 1
        n = len(idx)
        if n < 4:
            continue

        def on(k):
            return flags[idx[k % n]] & 1

        def pt(k):
            return coords[idx[k % n]]

        def ends(k):
            """On-curve (or implied) ends of the quadratic whose off-curve point is k."""
            a = pt(k - 1) if on(k - 1) else mul(add(pt(k - 1), pt(k)), 0.5)
            b = pt(k + 1) if on(k + 1) else mul(add(pt(k), pt(k + 1)), 0.5)
            return a, b

        def turning(k):
            a, b = ends(k)
            return cross(sub(pt(k), a), sub(b, pt(k)))

        offs = [k for k in range(n) if not on(k)]
        for j, k in enumerate(offs):
            t = turning(k)
            if t == 0:
                continue
            prev_k, next_k = offs[j - 1], offs[(j + 1) % len(offs)]
            tp, tn = turning(prev_k), turning(next_k)
            if not (tp * t < 0 and tn * t < 0):
                continue
            # only neighbours that touch it (no straight edge between)
            if (k - prev_k) % n > 2 or (next_k - k) % n > 2:
                continue
            a, b = ends(k)
            L = norm(sub(b, a))
            if L < 1e-9:
                continue
            sag = abs(cross(sub(pt(k), a), sub(b, a))) / L
            if sag > 1.5:
                continue
            q = add(a, mul(sub(b, a), dot(sub(pt(k), a), sub(b, a)) / (L * L)))
            # the joins it makes when straight
            chord = unit(sub(b, a))
            ta = unit(sub(a, pt(prev_k))) if (k - prev_k) % n <= 2 else chord
            tb = unit(sub(pt(next_k), b)) if (next_k - k) % n <= 2 else chord
            if degrees(acos(max(-1, min(1, dot(ta, chord))))) > max_kink or degrees(acos(max(-1, min(1, dot(chord, tb))))) > max_kink:
                continue
            coords[idx[k]] = (round(q[0]), round(q[1]))
            fixed += 1
        start = end + 1
    if fixed:
        glyph.coordinates = GlyphCoordinates(coords)
    return fixed


# ------------------------------------------------------------------ fairing


# how far (8192 units) a merge may move a re-rounded fillet: within the
# exported-radius audit's 0.35 of 1024 with a margin for the grid
FILLET_KEEP = 2.4


def _tt_pieces(pts):
    """One exported contour as explicit pieces, from an on-curve point:
    (p0, c, p2, owned) for a quadratic, (p0, None, p1, owned) for a line;
    owned are the indices of the points the piece adds (its off-curve point,
    and its end when that is an on-curve point)."""
    n = len(pts)
    k = next(i for i, p in enumerate(pts) if p[2])
    order = [(i + k) % n for i in range(n)]
    P = [pts[i] for i in order]
    out, cur, i = [], P[0][:2], 1
    while i <= n:
        p = P[i % n]
        if p[2]:
            out.append((cur, None, p[:2], (order[i % n],)))
            cur = p[:2]
            i += 1
            continue
        q = P[(i + 1) % n]
        end = q[:2] if q[2] else ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
        out.append((cur, p[:2], end, (order[i % n],) + ((order[(i + 1) % n],) if q[2] else ())))
        cur = end
        i += 2 if q[2] else 1
    return out


def _q_turn(q):
    p0, c, p2, _ = q
    return cross(sub(c, p0), sub(p2, c))


def _q_at(q, t):
    p0, c, p2, _ = q
    return add(add(mul(p0, (1 - t) ** 2), mul(c, 2 * t * (1 - t))), mul(p2, t * t))


def _fit_cubic(P0, t0, P3, t1, samples):
    """Least-squares handle lengths of the cubic from P0 (leaving along t0)
    to P3 (arriving along t1) through samples, chord-length parametrised."""
    d = [0.0]
    for a, b in zip(samples, samples[1:]):
        d.append(d[-1] + norm(sub(b, a)))
    if d[-1] <= 1e-9:
        return None
    A = np.zeros((2, 2))
    r = np.zeros(2)
    for p, dist in zip(samples, d):
        t = dist / d[-1]
        b1, b2 = 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t
        base = add(mul(P0, (1 - t) ** 3 + b1), mul(P3, b2 + t**3))
        u, v = mul(t0, b1), mul(t1, -b2)
        e = sub(p, base)
        A += np.array([[dot(u, u), dot(u, v)], [dot(u, v), dot(v, v)]])
        r += np.array([dot(u, e), dot(v, e)])
    try:
        al, be = np.linalg.solve(A, r)
    except np.linalg.LinAlgError:
        return None
    if al <= 0 or be <= 0:
        return None
    return (P0, add(P0, mul(t0, float(al))), sub(P3, mul(t1, float(be))), P3)


def _spline_at(pts, k=12):
    """Points along a TrueType quadratic spline [on, off..., on]."""
    offs = pts[1:-1]
    out = []
    cur = pts[0]
    for j, c in enumerate(offs):
        end = pts[-1] if j == len(offs) - 1 else mul(add(c, offs[j + 1]), 0.5)
        q = (cur, c, end, ())
        out += [_q_at(q, m / k) for m in range(k + 1)]
        cur = end
    return out


def _flip_merge(qs, i, tol, reach=4, kink=12.0, keep=()):
    """When qs[i] turns against a curved neighbour, the smallest run of
    quadratics around it (up to `reach` on either side, joined within `kink`
    degrees) that one convex curve with the run's outer ends and tangents
    replaces within tol units: a quadratic, or a cubic without an
    inflection as quadratics. Returns (first, last, [P0, off..., P3])."""
    from fontTools.cu2qu import curve_to_quadratic

    n = len(qs)
    B = qs[i]
    if B[1] is None or n < 4:
        return None
    tb = _q_turn(B)
    nbrs = [q for q in (qs[i - 1], qs[(i + 1) % n]) if q[1] is not None]
    if not any(_q_turn(q) * tb < 0 for q in nbrs):
        return None

    def ang(u, v):
        return degrees(acos(max(-1.0, min(1.0, dot(unit(u), unit(v))))))

    def within(spline, idx):
        ref = _spline_at(spline, 24)
        if not all(min(norm(sub(_q_at(qs[j], k / 16), r_)) for r_ in ref) <= tol for j in idx for k in range(1, 16)):
            return False
        # a re-rounded fillet the run carries stays a circle of its radius
        old = [_q_at(qs[j], k / 16) for j in idx for k in range(17)]
        for p in keep:
            if min(norm(sub(p, o)) for o in old) < 3 and min(norm(sub(p, r_)) for r_ in ref) > FILLET_KEEP:
                return False
        return True

    for size in range(2, 2 * reach + 2):
        for a in range(0, size):
            b = size - 1 - a
            if a > reach or b > reach:
                continue
            idx = [(i + k) % n for k in range(-a, b + 1)]
            if len(set(idx)) < len(idx) or any(qs[k][1] is None for k in idx):
                continue
            if any(ang(sub(qs[p][2], qs[p][1]), sub(qs[q][1], qs[q][0])) > kink for p, q in zip(idx, idx[1:])):
                continue
            first, last = qs[idx[0]], qs[idx[-1]]
            P0, P3 = first[0], last[2]
            own0, own1 = unit(sub(first[1], P0)), unit(sub(P3, last[1]))
            # a small kink into the run (a dent often hides one) goes too
            # when it can: the run leaves and enters along its neighbours
            before, after = qs[(idx[0] - 1) % n], qs[(idx[-1] + 1) % n]
            nb0 = unit(sub(before[2], before[1] if before[1] is not None else before[0]))
            nb1 = unit(sub(after[1] if after[1] is not None else after[2], after[0]))
            options = [(nb0 if ang(nb0, own0) <= kink else own0, nb1 if ang(own1, nb1) <= kink else own1), (own0, own1)]
            for t0, t1 in dict.fromkeys(options):
                m = _meet(P0, t0, P3, t1)
                if m is not None and m[0] > 0 and m[1] > 0:
                    spline = [P0, add(P0, mul(t0, m[0])), P3]
                    if within(spline, idx):
                        return idx[0], idx[-1], spline
                samples = [_q_at(qs[j], k / 16) for j in idx for k in range(16)] + [P3]
                cub = _fit_cubic(P0, t0, P3, t1, samples)
                if cub is None:
                    continue
                # no inflection: every control-polygon turn has one sign
                turns = _control_turns(cub)
                if len(turns) == 2 and turns[0] * turns[1] < 0:
                    continue
                spline = [tuple(p) for p in curve_to_quadratic(cub, 0.5)]
                legs = [sub(b_, a_) for a_, b_ in zip(spline, spline[1:])]
                if any(cross(u, v) * (turns[0] if turns else 1) < 0 for u, v in zip(legs, legs[1:])):
                    continue
                if len(spline) > 2 and within(spline, idx):
                    return idx[0], idx[-1], spline
    return None


def _contour_flips(pts, flat=25000.0):
    """Curvature sign changes along one exported contour, sampled nine
    times per quadratic; curvature under 1/flat (a radius of about three ems
    at 8192 units) counts as straight and is skipped."""
    signs = []
    for p0, c, p2, _ in _tt_pieces(pts):
        if c is None:
            continue
        acc = mul(add(sub(p0, mul(c, 2)), p2), 2)
        for k in range(9):
            t = k / 8
            d = add(mul(sub(c, p0), 2 * (1 - t)), mul(sub(p2, c), 2 * t))
            v = norm(d)
            if v < 1e-9:
                continue
            kappa = cross(d, acc) / v**3
            if abs(kappa) > 1 / flat:
                signs.append(kappa)
    return sum(1 for k in range(len(signs)) if signs[k] * signs[k - 1] < 0)


def unflip_glyph(glyph, accept, tol=6.0, keep=()):
    """A quadratic that turns against both of its tangent neighbours, which
    turn the same way, is a dent the offsets or the export grid left: the
    three become one quadratic with the outer ends and tangents, when it
    stays within tol units (8192 per em) of them and accept(glyph) holds.
    Returns the number merged."""
    if glyph.isComposite() or glyph.numberOfContours <= 0:
        return 0
    from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates

    merged = 0
    for _ in range(64):
        coords = [tuple(c) for c in glyph.coordinates]
        flags = [f & 1 for f in glyph.flags]
        ends = list(glyph.endPtsOfContours)
        contours, start = [], 0
        for e in ends:
            contours.append([(coords[j][0], coords[j][1], flags[j]) for j in range(start, e + 1)])
            start = e + 1
        done = False
        for ci, pts in enumerate(contours):
            if len(pts) < 6:
                continue
            qs = _tt_pieces([(x, y, f) for x, y, f in pts])
            for i in range(len(qs)):
                found = _flip_merge(qs, i, tol, keep=keep)
                if found is None:
                    continue
                n = len(qs)
                lo, hi, new = found
                run = set()
                j = lo
                while True:
                    run.add(j)
                    if j == hi:
                        break
                    j = (j + 1) % n
                pts_out = []
                for k in range(n):
                    j = (lo + k) % n
                    if j in run:
                        if j == lo:
                            prev_q = qs[(lo - 1) % n]
                            if not pts[prev_q[3][-1]][2]:
                                pts_out.append((round(new[0][0]), round(new[0][1]), 1))
                            pts_out += [(round(c[0]), round(c[1]), 0) for c in new[1:-1]]
                            pts_out.append((round(new[-1][0]), round(new[-1][1]), 1))
                        continue
                    pts_out.extend(pts[o] for o in qs[j][3])
                if _contour_flips(pts_out) >= _contour_flips(pts):
                    continue
                trial = contours[:ci] + [pts_out] + contours[ci + 1 :]
                old = (glyph.coordinates, glyph.flags, glyph.endPtsOfContours)
                glyph.coordinates = GlyphCoordinates([(x, y) for c in trial for x, y, _ in c])
                glyph.flags = bytearray(f for c in trial for _, _, f in c)
                ends2, tot = [], 0
                for c in trial:
                    tot += len(c)
                    ends2.append(tot - 1)
                glyph.endPtsOfContours = ends2
                if accept(glyph):
                    merged += 1
                    done = True
                    break
                glyph.coordinates, glyph.flags, glyph.endPtsOfContours = old
            if done:
                break
        if not done:
            break
    return merged


def _build_one(job):
    """One italic face in a worker process: (style, unhinted upright bytes,
    settings, decisions, aliases, fonts dir, hint). Returns its report."""
    style, data, settings, decisions, aliases, fonts_dir, hint = job
    upright = TTFont(BytesIO(data), recalcTimestamp=False)
    report = {}
    font = italic_font(upright, style, prm_for(style), settings, decisions, aliases, report=report)
    add_plain_zero(font, settings["plain_zero"])
    target = Path(fonts_dir) / f"DINDOT-{file_style(style)}.ttf"
    hint_and_save(font, target, aliases, upright["head"].modified, hint=hint)
    return style, report


def build_italics(unhinted, settings, decisions, aliases, fonts_dir, hint=True):
    """The four italic faces from this build's unhinted uprights, in parallel.

    unhinted: {style: TrueType bytes}. Writes fonts/DINDOT-<Style>Italic.ttf
    and .woff2 and returns {file style: report}."""
    from concurrent.futures import ProcessPoolExecutor
    import multiprocessing

    jobs = [(st, data, settings, decisions[st], aliases, str(fonts_dir), hint) for st, data in unhinted.items()]
    with ProcessPoolExecutor(max_workers=min(4, len(jobs)), mp_context=multiprocessing.get_context("spawn")) as pool:
        results = dict(pool.map(_build_one, jobs))
    return {file_style(st): results[st] for st in unhinted}


def summarize_report(rep):
    """A compact build report: per glyph its levels, fallbacks, dots and fillets."""
    glyphs = {}
    for name, g in rep["glyphs"].items():
        if g.get("class") != "slant":
            glyphs[name] = {"class": g.get("class"), **({"of": g["of"]} if "of" in g else {})}
            continue
        row = {"levels": g.get("levels")}
        for key in ("fallbacks", "dot_placement", "t_curve", "deviation", "points", "bowl_cs", "unflipped"):
            if g.get(key):
                row[key] = g[key]
        row["fillets"] = [
            [f.get("status"), f.get("radius"), f.get("used"), f.get("centre"), f.get("start"), f.get("end")]
            for f in g.get("fillets", [])
        ]
        glyphs[name] = row
    return {
        "style": rep["style"],
        "angle": ANGLE,
        "origin": ORIGIN,
        "balance": BALANCE.get(rep["style"]),
        "contour_levels": rep.get("contour_levels"),
        "kerning_records_changed": rep.get("kerning_records_changed"),
        "italic_pair_kerning": rep.get("italic_pair_kerning"),
        "a_family_anchors_moved": rep.get("a_family_anchors_moved"),
        "glyphs": glyphs,
    }


def prm_for(style, plain=False, **kw):
    if plain:
        return P(stroke=False, refillet=False, balance=False, dots=False, plain=True, **kw)
    return P(**{**BALANCE[style], **kw})


def build(style, out_dir, prm, hint=True, only=None, report_path=None, upright_path=None):
    src = Path(upright_path) if upright_path else DINDOT / "fonts" / f"DINDOT-{style}.ttf"
    upright = TTFont(src, recalcTimestamp=False)
    settings = json.loads((DINDOT / "settings.json").read_text())
    decisions = json.loads((DINDOT / "audit/glyph-decisions.json").read_text())[style]
    text_report = json.loads((DINDOT / "text/build-report.json").read_text())[style]["glyphs_reviewed"]
    aliases = {n: d["hint_source"] for n, d in text_report.items() if d.get("hint_source")}
    report = {}
    font = italic_font(upright, style, prm, settings, decisions, aliases, only=only, report=report)
    if f"zero.{settings['plain_zero']['feature']}" not in font.getGlyphOrder():
        add_plain_zero(font, settings["plain_zero"])
    target = Path(out_dir) / f"DINDOT-{file_style(style)}.ttf"
    hint_and_save(font, target, aliases, upright["head"].modified, hint=hint)
    if report_path:
        Path(report_path).write_text(json.dumps(report, indent=1, default=str) + "\n")
    return target, report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("styles", nargs="*", default=["Regular", "Bold"])
    ap.add_argument("--out", default=str(HERE / "fonts"))
    ap.add_argument("--no-hint", action="store_true")
    ap.add_argument("--only", default="")
    ap.add_argument("--plain", action="store_true", help="plain shear, for comparison")
    ap.add_argument("--set", default="", help="override balance params, k=v,k=v")
    args = ap.parse_args()
    only = set(args.only.split(",")) if args.only else None
    over = {}
    for kv in filter(None, args.set.split(",")):
        k, v = kv.split("=")
        over[k] = float(v)
    for style in args.styles:
        prm = prm_for(style, plain=args.plain, **over)
        target, rep = build(style, Path(args.out), prm, hint=not args.no_hint, only=only, report_path=Path(args.out) / f"report-{style}.json")
        print(style, "->", target, "levels:", rep.get("contour_levels"), flush=True)


if __name__ == "__main__":
    main()
