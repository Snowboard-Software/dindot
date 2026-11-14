"""TrueType outline parsing and emission for the italic post-process.

Outlines are read from the exported 8192-unit TTF into the 1024-unit design
space the DINDOT build uses, as rounding.Segment lines and quadratics. Each
contour keeps, per segment, whether its start point was an implied on-curve
point, so the emitter can write the same quadratic splines back.
"""

import sys
from math import atan2, degrees, acos
from pathlib import Path
import numpy as np

# The module sits in the DINDOT project, next to rounding.py.
DINDOT = str(Path(__file__).resolve().parent)
if DINDOT not in sys.path:
    sys.path.insert(0, DINDOT)

from rounding import Segment, sub, dot, cross, norm  # noqa: E402
from fontTools.pens.ttGlyphPen import TTGlyphPen  # noqa: E402
from fontTools.cu2qu.cu2qu import curve_to_quadratic  # noqa: E402

SCALE = 8.0  # 8192 / 1024


class Contour:
    """Closed contour: segments plus the implied-start flag of each segment."""

    def __init__(self, segs, implied=None):
        self.segs = list(segs)
        self.implied = list(implied) if implied is not None else [False] * len(segs)

    def copy(self):
        return Contour(list(self.segs), list(self.implied))


def read_glyph(font, name):
    glyf = font["glyf"]
    g = glyf[name]
    if g.isComposite():
        return None
    if g.numberOfContours <= 0:
        return []
    coords, ends, flags = g.getCoordinates(glyf)
    out = []
    start = 0
    for e in ends:
        pts = [(coords[i][0] / SCALE, coords[i][1] / SCALE) for i in range(start, e + 1)]
        on = [bool(flags[i] & 1) for i in range(start, e + 1)]
        start = e + 1
        out.append(_decode(pts, on))
    return out


def _decode(pts, on):
    n = len(pts)
    # Rotate so that the contour starts with an on-curve point (insert an implied one if none).
    if not any(on):
        mid = lerp2(pts[-1], pts[0])
        pts = [mid] + pts
        on = [True] + on
        implied0 = True
    else:
        k = on.index(True)
        pts = pts[k:] + pts[:k]
        on = on[k:] + on[:k]
        implied0 = False
    n = len(pts)
    segs, implied = [], []
    cur = pts[0]
    cur_implied = implied0
    i = 1
    while i <= n:
        p = pts[i % n]
        o = on[i % n]
        if o:
            if norm(sub(p, cur)) > 1e-9:
                segs.append(Segment((cur, p)))
                implied.append(cur_implied)
            cur, cur_implied = p, False
            i += 1
        else:
            nxt = pts[(i + 1) % n]
            nxt_on = on[(i + 1) % n]
            if nxt_on:
                segs.append(Segment((cur, p, nxt)))
                implied.append(cur_implied)
                cur, cur_implied = nxt, False
                i += 2
            else:
                mid = lerp2(p, nxt)
                segs.append(Segment((cur, p, mid)))
                implied.append(cur_implied)
                cur, cur_implied = mid, True
                i += 1
    return Contour(segs, implied)


def lerp2(a, b, t=0.5):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def emit_glyph(contours, max_err=0.10, implied_tol=0.06):
    """Write contours (lines, quadratics, cubics in 1024 units) to an 8192-unit glyph.

    A shared on-curve point between two quadratics is written implied when it
    lies within implied_tol of the midpoint of their off-curve points and was
    implied in the source (or is a new spline from cu2qu)."""
    pen = TTGlyphPen(None)
    for c in contours:
        segs = []
        flags = []
        for seg, imp in zip(c.segs, c.implied):
            if len(seg.points) == 4:
                q = curve_to_quadratic(seg.points, max_err)
                # q: [p0, off..., p3]; split into quads with implied joins
                offs = q[1:-1]
                if len(offs) == 1:
                    segs.append(Segment((q[0], offs[0], q[-1])))
                    flags.append(imp)
                else:
                    starts = [q[0]] + [lerp2(offs[j], offs[j + 1]) for j in range(len(offs) - 1)]
                    ends_ = starts[1:] + [q[-1]]
                    for j, off in enumerate(offs):
                        segs.append(Segment((tuple(starts[j]), tuple(off), tuple(ends_[j]))))
                        flags.append(imp if j == 0 else True)
            else:
                segs.append(seg)
                flags.append(imp)
        if not segs:
            continue
        start = segs[0].points[0]
        pen.moveTo(_s(start))
        i = 0
        n = len(segs)
        while i < n:
            seg = segs[i]
            if len(seg.points) == 2:
                pen.lineTo(_s(seg.points[1]))
                i += 1
                continue
            offs = [seg.points[1]]
            end = seg.points[2]
            j = i + 1
            while j < n and len(segs[j].points) == 3 and flags[j]:
                mid = lerp2(offs[-1], segs[j].points[1])
                if norm(sub(mid, end)) > implied_tol:
                    break
                offs.append(segs[j].points[1])
                end = segs[j].points[2]
                j += 1
            pen.qCurveTo(*[_s(o) for o in offs], _s(end))
            i = j
        pen.closePath()
    return pen.glyph()


def _s(p):
    return (p[0] * SCALE, p[1] * SCALE)


# ---------------------------------------------------------------- geometry helpers


def sample_contour(contour, per=24):
    pts = []
    for seg in contour.segs:
        for k in range(per):
            pts.append(seg.at(k / per))
    return np.array(pts)


def signed_area(contour, per=24):
    P = sample_contour(contour, per)
    x, y = P[:, 0], P[:, 1]
    return 0.5 * float(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))


def perimeter(contour, per=24):
    P = sample_contour(contour, per)
    return float(np.sum(np.linalg.norm(np.roll(P, -1, 0) - P, axis=1)))


def fit_circle(P):
    """Least squares circle (Kasa, then two Gauss-Newton steps). Returns cx, cy, r, max residual."""
    x, y = P[:, 0], P[:, 1]
    A = np.c_[2 * x, 2 * y, np.ones(len(x))]
    b = x * x + y * y
    try:
        c, *_ = np.linalg.lstsq(A, b, rcond=None)
    except np.linalg.LinAlgError:
        return None
    cx, cy = c[0], c[1]
    r = np.sqrt(max(c[2] + cx * cx + cy * cy, 0))
    for _ in range(4):
        d = np.hypot(x - cx, y - cy)
        d = np.where(d < 1e-9, 1e-9, d)
        J = np.c_[(cx - x) / d, (cy - y) / d, -np.ones(len(x))]
        res = d - r
        try:
            step, *_ = np.linalg.lstsq(J, -res, rcond=None)
        except np.linalg.LinAlgError:
            break
        cx, cy, r = cx + step[0], cy + step[1], r + step[2]
    res = np.abs(np.hypot(x - cx, y - cy) - r)
    return float(cx), float(cy), float(r), float(res.max())


def turn_deg(prev, nxt):
    u, v = prev.tangent(1), nxt.tangent(0)
    return degrees(acos(max(-1, min(1, dot(u, v)))))


def signed_turn(prev, nxt):
    u, v = prev.tangent(1), nxt.tangent(0)
    return degrees(atan2(cross(u, v), dot(u, v)))


def seg_turning(segs, per=16):
    """Total signed turning (degrees) of the tangent along a chain of G1 segments."""
    total = 0.0
    last = None
    for seg in segs:
        for k in range(per + 1):
            t = seg.tangent(k / per)
            if last is not None:
                total += degrees(atan2(cross(last, t), dot(last, t)))
            last = t
    return total
