"""Change stroke weight without changing stroke proportions.

Text letters are stretched by their width profile, which thickens vertical
stems by the same 2.5-7.5%, and the heavy weights then lose ink evenly all
round, which thins bars more than stems in proportion. Two exact offsets
replace that:

- `parallel_offset` moves every point the same distance along its normal into
  the ink (a round pen). Lines stay lines, smooth joins stay smooth and every
  curve refits to one cubic with its original end tangents.
- `sweep_offset` erodes or dilates by a horizontal segment. It changes stems
  only; bars, heights and the radius of every corner stay put.

Eroding a curved top by a segment leaves a slight kink where its two sides
meet, and dilating into a rounded notch does the same; `smooth_kinks` aligns
the tangents at only those joins.
"""

from math import ceil, degrees
import skia
from shapely import LineString, MultiLineString, hausdorff_distance
from curve_cleanup import fit_cubic
from extensions import canonical
from rounding import Segment, add, sub, mul, dot, cross, norm, unit, contours, path_from_contours, turn


def _normal(tangent):
    # extensions.canonical writes TrueType winding: the ink lies right of travel.
    return (tangent[1], -tangent[0])


def _shift_end(segments, delta, start):
    # Move an end point and its handle together, which keeps the end tangent.
    seg = segments[0] if start else segments[-1]
    points = list(seg.points)
    ends = (0, 1) if start else (-1, -2)
    for i in ends[: 2 if len(points) > 2 else 1]:
        points[i] = add(points[i], delta)
    segments[0 if start else -1] = Segment(tuple(points))


def _join(pieces, distance):
    out = [list(pieces[0][0])]
    for segments, _, _ in pieces[1:]:
        out.append(list(segments))
    for i in range(len(out)):
        prev, nxt = out[i - 1], out[i]
        a, b = prev[-1].points[-1], nxt[0].points[0]
        if norm(sub(b, a)) < 0.01:
            _shift_end(nxt, sub(a, b), start=True)
            continue
        # A real corner: meet where the two offset tangents cross (a miter).
        ta, tb = pieces[i - 1][2], pieces[i][1]
        det = cross(ta, tb)
        if abs(det) > 1e-6:
            s = cross(sub(b, a), tb) / det
            meet = add(a, mul(ta, s))
            if norm(sub(meet, a)) < 4 * abs(distance) + 1 and norm(sub(meet, b)) < 4 * abs(distance) + 1:
                _shift_end(prev, sub(meet, a), start=False)
                _shift_end(nxt, sub(meet, b), start=True)
                continue
        prev.append(Segment((a, b)))
    return [seg for segments in out for seg in segments]


def _offset_point(seg, t, distance):
    return add(seg.at(t), mul(_normal(seg.tangent(t)), distance))


def _gap(points, curve):
    # Largest distance from the exact offset points to the candidate curve.
    poly = [curve.at(k / 64) for k in range(65)]
    worst = 0
    for p in points:
        best = float("inf")
        for a, b in zip(poly, poly[1:]):
            ab = sub(b, a)
            u = max(0, min(1, dot(sub(p, a), ab) / max(dot(ab, ab), 1e-12)))
            best = min(best, norm(sub(p, add(a, mul(ab, u)))))
        worst = max(worst, best)
    return worst


def _offset_quad(seg, distance, tolerance, depth=0):
    # The offset of a quadratic keeps its end tangents, so its own quadratic
    # has the control point where those tangents meet. Split only if the true
    # offset strays from it.
    t0, t1 = seg.tangent(0), seg.tangent(1)
    q0, q2 = _offset_point(seg, 0, distance), _offset_point(seg, 1, distance)
    det = cross(t0, t1)
    s = cross(sub(q2, q0), t1) / det if abs(det) > 1e-9 else -1
    u = cross(t0, sub(q2, q0)) / det if abs(det) > 1e-9 else -1
    if s > 0 and u > 0:
        curve = Segment((q0, add(q0, mul(t0, s)), q2))
        if _gap([_offset_point(seg, k / 8, distance) for k in range(1, 8)], curve) <= tolerance:
            return [curve]
    if depth == 5:
        return [Segment((q0, q2))] if abs(det) <= 1e-9 else None
    halves = [_offset_quad(h, distance, tolerance, depth + 1) for h in seg.split(0.5)]
    return None if None in halves else halves[0] + halves[1]


def parallel_offset(contour_list, distance, tolerance=0.05):
    """Move every contour `distance` into the ink (negative: outwards).

    Returns None when a curve would fold back on itself, which happens only
    where its radius is smaller than the distance.
    """
    out = []
    for contour in contour_list:
        pieces = []
        for seg in contour:
            if len(seg.points) == 2:
                t = unit(sub(seg.points[1], seg.points[0]))
                shift = mul(_normal(t), distance)
                a, b = add(seg.points[0], shift), add(seg.points[1], shift)
                pieces.append(([Segment((a, b))], t, t))
                continue
            count = max(8, ceil(seg.length() / 6))
            points = [_offset_point(seg, k / count, distance) for k in range(count + 1)]
            tangents = [seg.tangent(k / count) for k in range(count + 1)]
            if any(dot(sub(b, a), t) <= 0 for a, b, t in zip(points, points[1:], tangents)):
                return None
            if len(seg.points) == 3:
                fitted = _offset_quad(seg, distance, tolerance)
                if fitted is None:
                    return None
            else:
                fitted = fit_cubic(points, tangents[0], mul(tangents[-1], -1), tolerance)
            pieces.append((fitted, tangents[0], tangents[-1]))
        out.append(_join(pieces, distance))
    return out


def _split_y_extrema(seg):
    p = [q[1] for q in seg.points]
    if len(p) == 2:
        return [seg]
    if len(p) == 3:
        den = p[0] - 2 * p[1] + p[2]
        roots = [(p[0] - p[1]) / den] if abs(den) > 1e-12 else []
    else:
        a = p[1] - p[0]
        b = p[2] - p[1]
        c = p[3] - p[2]
        qa, qb, qc = a - 2 * b + c, 2 * (b - a), a
        if abs(qa) < 1e-12:
            roots = [-qc / qb] if abs(qb) > 1e-12 else []
        else:
            disc = qb * qb - 4 * qa * qc
            roots = [] if disc < 0 else [(-qb + s * disc**0.5) / (2 * qa) for s in (-1, 1)]
    pieces, rest, done = [], seg, 0
    for r in sorted(r for r in roots if 1e-6 < r < 1 - 1e-6):
        left, rest = rest.split((r - done) / (1 - done))
        pieces.append(left)
        done = r
    return pieces + [rest]


def _swept(piece, w):
    # A y-monotone piece swept from -w to +w is bounded by its two copies and
    # the horizontal lines joining their ends.
    left = Segment(tuple((x - w, y) for x, y in piece.points))
    right = Segment(tuple((x + w, y) for x, y in reversed(piece.points)))
    region = [left, Segment((left.points[-1], right.points[0])), right, Segment((right.points[-1], left.points[0]))]
    if piece.points[-1][1] > piece.points[0][1]:
        # Upward pieces trace clockwise; reverse so every region winds alike.
        region = [Segment(tuple(reversed(s.points))) for s in reversed(region)]
    return region


def sweep_offset(path, half):
    """Erode (half > 0) or dilate (half < 0) a filled path by a horizontal
    segment of half-length |half|: S minus, or plus, its boundary swept.

    Under half a unit the two copies of an edge sit so close that the path
    operations can leave a seam, so such a sweep is skipped. A sweep that
    changes the number of contours returns None."""
    if abs(half) < 0.5:
        return path
    regions = []
    for contour in contours(path):
        for seg in contour:
            for piece in _split_y_extrema(seg):
                if abs(piece.points[-1][1] - piece.points[0][1]) > 1e-9:
                    regions.append(_swept(piece, abs(half)))
    op = skia.PathOp.kDifference_PathOp if half > 0 else skia.PathOp.kUnion_PathOp
    kept = _kept(skia.Op(path, skia.Simplify(path_from_contours(regions)), op))
    if len(kept) != len(contours(path)):
        # Under about 1.2 units, neighbouring regions share edges so closely that
        # simplifying them together can split or fill a contour (24 SemiBold
        # letters in 0.19). Applying them one at a time gives the same ink
        # wherever the joint operation works, and holds where it fails.
        swept = path
        for region in regions:
            swept = skia.Op(swept, path_from_contours([region]), op)
        kept = _kept(swept)
    if len(kept) != len(contours(path)):
        return None
    swept = canonical(path_from_contours(kept))
    # The sweep moves every edge at most |half| sideways. On edges this close the
    # path operations can instead join two points of a curve with a chord, up to
    # 20 units inside it (B, D, ß and 11 more SemiBold letters in 0.19, at a
    # half of 0.58): a sweep that strays further than that is refused. Correct
    # sweeps stay within 0.01 of |half|, the faulty ones went at least 3.2 past it.
    if hausdorff_distance(_boundary(path), _boundary(swept), densify=0.25) > abs(half) + 1:
        return None
    return swept


def _boundary(path, step=2.0):
    lines = []
    for contour in contours(path):
        points = []
        for seg in contour:
            count = max(2, ceil(seg.length() / step))
            points.extend(seg.at(k / count) for k in range(count))
        lines.append(LineString(points + points[:1]))
    return MultiLineString(lines)


def _kept(path):
    # Edges the sweep shares with the outline can leave zero-width slivers.
    kept = []
    for c in contours(canonical(path)):
        box = path_from_contours([c]).computeTightBounds()
        if min(box.width(), box.height()) > 0.05:
            kept.append(c)
    return kept


def _cubic(seg):
    if len(seg.points) == 4:
        return list(seg.points)
    p, q, r = seg.points
    return [p, add(p, mul(sub(q, p), 2 / 3)), add(r, mul(sub(q, r), 2 / 3)), r]


def smooth_kinks(contour_list, low=0.5, high=45):
    """Align the tangents at each join that turns between low and high degrees.

    As round_contour does for minor joins: a line keeps its direction and the
    curve beside it turns its end handle to match; two curves both take their
    average direction. Handle lengths stay the same.
    """
    out = []
    for contour in contour_list:
        c = list(contour)
        for i in range(len(c)):
            prev, nxt = c[i - 1], c[i]
            if not low < degrees(turn(prev, nxt)[0]) < high:
                continue
            if len(prev.points) == 2 and len(nxt.points) == 2:
                continue
            incoming, outgoing = prev.tangent(1), nxt.tangent(0)
            if len(prev.points) == 2:
                tangent = incoming
            elif len(nxt.points) == 2:
                tangent = outgoing
            else:
                tangent = unit(add(incoming, outgoing))
            if len(prev.points) > 2:
                points = _cubic(prev)
                points[-2] = sub(points[-1], mul(tangent, norm(sub(points[-1], points[-2]))))
                c[i - 1] = Segment(tuple(points))
            if len(nxt.points) > 2:
                points = _cubic(nxt)
                points[1] = add(points[0], mul(tangent, norm(sub(points[1], points[0]))))
                c[i] = Segment(tuple(points))
        out.append(c)
    return out
