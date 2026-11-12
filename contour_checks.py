"""Outline validity at the exported font's own units.

A contour is checked as the rasteriser sees it: each quadratic flattened in
40 steps at full precision, then tested as a ring that never touches or
crosses itself. Points that double back (a turn sharper than 150 degrees with
a leg under 40 units at 8192 units per em) are counted separately: they are
the grid-sized zigzags that make such loops, and a smooth outline has none.
"""

from math import atan2, degrees, hypot

from shapely.geometry import LinearRing

STEPS = 40
TURN = 150.0
LEG = 40 / 8192  # of the em


def contour_points(glyph, glyf):
    """[(x, y, on_curve)] per contour of a simple glyph."""
    if glyph.isComposite() or glyph.numberOfContours <= 0:
        return []
    coords, ends, flags = glyph.getCoordinates(glyf)
    out, start = [], 0
    for end in ends:
        out.append([(coords[i][0], coords[i][1], flags[i] & 1) for i in range(start, end + 1)])
        start = end + 1
    return out


def flatten(pts, steps=STEPS):
    """The contour as a closed polyline, each quadratic in `steps` pieces."""
    if not any(on for _, _, on in pts):
        pts = [((pts[-1][0] + pts[0][0]) / 2, (pts[-1][1] + pts[0][1]) / 2, 1)] + pts
    k = next(i for i, p in enumerate(pts) if p[2])
    pts = pts[k:] + pts[:k]
    n = len(pts)
    out = []
    cur = pts[0][:2]
    i = 1
    while i <= n:
        p = pts[i % n]
        if p[2]:
            out.append(cur)
            cur = p[:2]
            i += 1
            continue
        q = pts[(i + 1) % n]
        end = q[:2] if q[2] else ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
        for t in range(steps):
            u = t / steps
            out.append(
                (
                    (1 - u) ** 2 * cur[0] + 2 * u * (1 - u) * p[0] + u * u * end[0],
                    (1 - u) ** 2 * cur[1] + 2 * u * (1 - u) * p[1] + u * u * end[1],
                )
            )
        cur = end
        i += 2 if q[2] else 1
    # float noise must not make a repeated point look like a crossing
    ring = []
    for x, y in out:
        p = (round(x, 6), round(y, 6))
        if not ring or p != ring[-1]:
            ring.append(p)
    if len(ring) > 1 and ring[0] == ring[-1]:
        ring.pop()
    return ring


def is_simple(pts):
    ring = flatten(pts)
    return len(ring) >= 3 and LinearRing(ring).is_simple


def doubled_back(pts, upm, turn=TURN, leg=LEG):
    """Indices of points where the point sequence turns back on itself."""
    limit = leg * upm
    bad = []
    n = len(pts)
    for i in range(n):
        a, b, c = pts[i - 1], pts[i], pts[(i + 1) % n]
        u = (b[0] - a[0], b[1] - a[1])
        v = (c[0] - b[0], c[1] - b[1])
        lu, lv = hypot(*u), hypot(*v)
        if lu == 0 or lv == 0:
            continue
        ang = abs(degrees(atan2(u[0] * v[1] - u[1] * v[0], u[0] * v[0] + u[1] * v[1])))
        if ang > turn and min(lu, lv) < limit:
            bad.append(i)
    return bad


def glyph_faults(font, name):
    """{contour index: [faults]} for one glyph; empty when it is valid."""
    glyf = font["glyf"]
    upm = font["head"].unitsPerEm
    faults = {}
    for ci, pts in enumerate(contour_points(glyf[name], glyf)):
        found = []
        if not is_simple(pts):
            found.append("crosses itself")
        back = doubled_back(pts, upm)
        if back:
            found.append(f"doubles back at points {back}")
        if found:
            faults[ci] = found
    return faults


def font_faults(font):
    """{glyph: {contour: [faults]}} over every simple glyph of a font."""
    out = {}
    for name in font.getGlyphOrder():
        found = glyph_faults(font, name)
        if found:
            out[name] = found
    return out


def only_dots_grew(new, old, glyf_new, glyf_old, upm):
    """Since 0.21 each round dot has the area of DINish's square dot. A
    contour that differs from a reference must be a round dot on the same x
    centre, no smaller, keeping its top, its bottom or its centre; every other
    contour is identical. A composite keeps its parts: only its bounding box
    grows with a dot in them."""
    if new.isComposite() or old.isComposite():
        parts = [
            [c.getComponentInfo() + (c.flags,) for c in g.components] if g.isComposite() else None
            for g in (new, old)
        ]
        return parts[0] is not None and parts[0] == parts[1]
    a, b = contour_points(new, glyf_new), contour_points(old, glyf_old)
    if len(a) != len(b):
        return False
    tolerance = upm * 0.002
    for pa, pb in zip(a, b):
        if pa == pb:
            continue
        (ax0, ay0, ax1, ay1), (bx0, by0, bx1, by1) = (
            (min(q[0] for q in p), min(q[1] for q in p), max(q[0] for q in p), max(q[1] for q in p)) for p in (pa, pb)
        )
        round_dots = abs((ax1 - ax0) - (ay1 - ay0)) <= tolerance and abs((bx1 - bx0) - (by1 - by0)) <= tolerance
        kept = min(abs(ay1 - by1), abs(ay0 - by0), abs((ay0 + ay1) - (by0 + by1)) / 2)
        if not (
            round_dots
            and ax1 - ax0 >= bx1 - bx0
            and abs((ax0 + ax1) - (bx0 + bx1)) / 2 <= tolerance
            and kept <= tolerance
        ):
            return False
    return True
