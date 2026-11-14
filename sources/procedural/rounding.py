"""Tangent-preserving corner fillets, true-circle marks, and outline audit helpers."""

from dataclasses import dataclass
from math import acos, asin, atan2, cos, sin, tan, hypot, pi, degrees
from bisect import bisect_right
from fontTools.misc.bezierTools import calcQuadraticArcLength
import skia

EPS = 1e-8


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def mul(a, s):
    return (a[0] * s, a[1] * s)


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def cross(a, b):
    return a[0] * b[1] - a[1] * b[0]


def norm(a):
    return hypot(*a)


def unit(a):
    n = norm(a)
    return mul(a, 1 / n) if n > EPS else (0, 0)


def lerp(a, b, t):
    return add(mul(a, 1 - t), mul(b, t))


@dataclass
class Segment:
    points: tuple

    def at(self, t):
        p = list(self.points)
        while len(p) > 1:
            p = [lerp(a, b, t) for a, b in zip(p, p[1:])]
        return p[0]

    def derivative(self, t):
        n = len(self.points) - 1
        return Segment(
            tuple(mul(sub(b, a), n) for a, b in zip(self.points, self.points[1:]))
        ).at(t)

    def tangent(self, t):
        d = self.derivative(t)
        if norm(d) > EPS:
            return unit(d)
        return unit(sub(self.at(min(1, t + 1e-4)), self.at(max(0, t - 1e-4))))

    def split(self, t):
        levels = [list(self.points)]
        while len(levels[-1]) > 1:
            levels.append([lerp(a, b, t) for a, b in zip(levels[-1], levels[-1][1:])])
        return Segment(tuple(p[0] for p in levels)), Segment(
            tuple(p[-1] for p in reversed(levels))
        )

    def between(self, a, b):
        left = self.split(b)[0] if b < 1 else self
        return left.split(a / b)[1] if a > 0 and b > 0 else left

    def length(self, t=1):
        if len(self.points) == 2:
            return norm(sub(self.points[1], self.points[0])) * t
        if len(self.points) == 3:
            p0, p1, p2 = self.points
            return calcQuadraticArcLength(p0, lerp(p0, p1, t), self.at(t))
        nodes = [
            0,
            0.5384693101056831,
            -0.5384693101056831,
            0.906179845938664,
            -0.906179845938664,
        ]
        weights = [
            0.5688888888888889,
            0.4786286704993665,
            0.4786286704993665,
            0.2369268850561891,
            0.2369268850561891,
        ]
        return (
            t
            / 2
            * sum(
                w * norm(self.derivative(t / 2 * (x + 1)))
                for x, w in zip(nodes, weights)
            )
        )

    def distance_t(self, d):
        length = self.length()
        if len(self.points) == 2:
            return min(1, max(0, d / length)) if length else 0
        d = min(length, max(0, d))
        a, b, t = 0, 1, d / length
        for _ in range(16):
            error = self.length(t) - d
            if abs(error) < 1e-6:
                return t
            if error < 0:
                a = t
            else:
                b = t
            speed = norm(self.derivative(t))
            candidate = t - error / speed if speed > EPS else -1
            t = candidate if a < candidate < b else (a + b) / 2
        return t


def contours(path):
    result = []
    current = []
    start = None
    end = None
    for verb, points in path:
        p = tuple((float(p.x()), float(p.y())) for p in points)
        if verb == skia.Path.kMove_Verb:
            current = []
            start = end = p[0]
        elif verb in [
            skia.Path.kLine_Verb,
            skia.Path.kQuad_Verb,
            skia.Path.kCubic_Verb,
        ]:
            segment = Segment(p)
            if max(norm(sub(x, p[0])) for x in p) > EPS:
                current.append(segment)
            end = p[-1]
        elif verb == skia.Path.kClose_Verb:
            if end is not None and norm(sub(end, start)) > EPS:
                current.append(Segment((end, start)))
            if current:
                result.append(current)
            current = []
            start = end = None
        else:
            raise ValueError(f"Unsupported path verb {verb}")
    return result


def path_from_contours(contour_list):
    path = skia.Path()
    for contour in contour_list:
        if not contour:
            continue
        path.moveTo(*contour[0].points[0])
        for seg in contour:
            if len(seg.points) == 2:
                path.lineTo(*seg.points[1])
            elif len(seg.points) == 3:
                path.quadTo(*seg.points[1], *seg.points[2])
            elif len(seg.points) == 4:
                path.cubicTo(*seg.points[1], *seg.points[2], *seg.points[3])
        path.close()
    return path


def bounds(contour):
    # Skia's tight bounds include Bezier extrema rather than control-point extrema.
    rect = path_from_contours([contour]).computeTightBounds()
    return rect.left(), rect.top(), rect.right(), rect.bottom()


def circle(cx, cy, diameter):
    """Four cubic circular quadrants, clockwise, with integral center and diameter."""
    cx, cy = round(cx), round(cy)
    d = max(2, 2 * round(diameter / 2))
    r = d / 2
    k = 4 / 3 * tan(pi / 8)
    result = []
    for i in range(4):
        a = -i * pi / 2
        b = -(i + 1) * pi / 2
        p0 = (cx + r * cos(a), cy + r * sin(a))
        p3 = (cx + r * cos(b), cy + r * sin(b))
        tangent0 = (sin(a), -cos(a))
        tangent1 = (sin(b), -cos(b))
        result.append(
            Segment(
                (p0, add(p0, mul(tangent0, k * r)), sub(p3, mul(tangent1, k * r)), p3)
            )
        )
    return result


@dataclass
class CurveRun:
    """A continuous outline run, independent of the source's segment boundaries."""

    segments: list

    def __post_init__(self):
        self.lengths = [s.length() for s in self.segments]
        self.ends = []
        length = 0
        for d in self.lengths:
            length += d
            self.ends.append(length)
        self.total = length

    def locate(self, distance):
        distance = max(0, min(self.total, distance))
        index = min(bisect_right(self.ends, distance), len(self.segments) - 1)
        start = self.ends[index - 1] if index else 0
        return index, self.segments[index].distance_t(distance - start)

    def length(self, t=1):
        return self.total * t

    def at(self, t):
        i, u = self.locate(t * self.total)
        return self.segments[i].at(u)

    def tangent(self, t):
        i, u = self.locate(t * self.total)
        return self.segments[i].tangent(u)

    def distance_t(self, distance):
        return distance / self.total

    def between(self, a, b):
        i, u = self.locate(a * self.total)
        j, v = self.locate(b * self.total)
        if i == j:
            return [self.segments[i].between(u, v)]
        result = [self.segments[i].between(u, 1)]
        result.extend(self.segments[i + 1 : j])
        if v > EPS:
            result.append(self.segments[j].between(0, v))
        return result


def turn(prev, nxt):
    u, v = prev.tangent(1), nxt.tangent(0)
    return acos(max(-1, min(1, dot(u, v)))), cross(u, v)


def fillet(
    prev,
    nxt,
    radius,
    inner_scale=0.55,
    acute_scale=0.65,
    minimum_angle=pi / 180,
    minimum_trim=0.02,
    limit_prev=None,
    limit_next=None,
):
    """Solve a true circular fillet tangent to both continuous outline runs."""
    angle, signed_turn = turn(prev, nxt)
    if angle < minimum_angle:
        return None, "smooth"
    if angle > pi * 0.999:
        return None, "protected-cusp"
    sign = 1 if signed_turn > 0 else -1
    desired = radius * (inner_scale if sign > 0 else 1)
    if angle > pi * 2 / 3:
        desired *= acute_scale
    pa = 0.42 * prev.length() if limit_prev is None else limit_prev
    pb = 0.42 * nxt.length() if limit_next is None else limit_next
    half_tangent = tan(angle / 2)
    working = min(desired, pa / half_tangent, pb / half_tangent)

    def evaluate(a, b, r):
        ta = prev.distance_t(prev.length() - a)
        tb = nxt.distance_t(b)
        p, q = prev.at(ta), nxt.at(tb)
        u, v = prev.tangent(ta), nxt.tangent(tb)
        cp = add(p, mul((-u[1], u[0]), sign * r))
        cq = add(q, mul((-v[1], v[0]), sign * r))
        return sub(cp, cq), (ta, tb, p, q, u, v)

    for attempt in range(12):
        distance = working * half_tangent
        seeds = [
            (min(distance, pa), min(distance, pb)),
            (min(distance * 1.5, pa), min(distance, pb)),
            (min(distance, pa), min(distance * 1.5, pb)),
            (min(distance * 1.5, pa), min(distance * 1.5, pb)),
        ]
        for a, b in seeds:
            for _ in range(14):
                error, data = evaluate(a, b, working)
                if norm(error) < 1e-5:
                    ta, tb, p, q, u, v = data
                    theta = acos(max(-1, min(1, dot(u, v))))
                    if cross(u, v) * sign <= 0 or theta < pi / 360:
                        break
                    handle = 4 / 3 * tan(theta / 4) * working
                    arc = Segment(
                        (p, add(p, mul(u, handle)), sub(q, mul(v, handle)), q)
                    )
                    return (ta, tb, arc, working, desired), "rounded"
                delta = max(0.001, working * 0.002)
                da = delta if a + delta <= pa else -delta
                db = delta if b + delta <= pb else -delta
                ea, _ = evaluate(a + da, b, working)
                eb, _ = evaluate(a, b + db, working)
                ja, jb = mul(sub(ea, error), 1 / da), mul(sub(eb, error), 1 / db)
                det = cross(ja, jb)
                if abs(det) < 1e-10:
                    break
                step_a, step_b = (
                    cross(mul(error, -1), jb) / det,
                    cross(ja, mul(error, -1)) / det,
                )
                improved = False
                for fraction in [1, 0.5, 0.25, 0.125, 0.0625]:
                    na, nb = a + step_a * fraction, b + step_b * fraction
                    if not (minimum_trim < na <= pa and minimum_trim < nb <= pb):
                        continue
                    e, _ = evaluate(na, nb, working)
                    if norm(e) < norm(error):
                        a, b, improved = na, nb, True
                        break
                if not improved:
                    break
        working *= 0.8
        if working * half_tangent < minimum_trim:
            break
    return None, "unresolved-corner"


def insert_cuts(segments, changes, runs=False):
    result = []
    for i, seg in enumerate(segments):
        begin = changes[i][1] if changes[i] else 0
        end = (
            changes[(i + 1) % len(segments)][0]
            if changes[(i + 1) % len(segments)]
            else 1
        )
        assert begin < end, (begin, end)
        clipped = seg.between(begin, end)
        result.extend(clipped if runs else [clipped])
        following = changes[(i + 1) % len(segments)]
        if following:
            result.append(following[2])
    return result


def round_contour(
    contour,
    radius,
    inner_scale=0.55,
    acute_scale=0.65,
    profile_multiplier=1,
    audit=None,
):
    """Round minor joins, then real corners across whole tangent-continuous runs.

    Common convex terminals use the family radius. Letter-specific optical
    reductions apply to concave/acute joins, rather than weakening every terminal.
    """
    statuses = []
    contour = list(contour)
    minor = [None] * len(contour)
    for i in range(len(contour)):
        prev, nxt = contour[i - 1], contour[i]
        angle, signed = turn(prev, nxt)
        if not pi / 180 < angle < pi * 25 / 180:
            continue
        incoming, outgoing = prev.tangent(1), nxt.tangent(0)
        if len(prev.points) == 2 and len(nxt.points) == 2:
            # A shallow kink needs a generous transition, not a subpixel arc.
            cut, status = fillet(
                prev, nxt, max(radius, 8 / angle), inner_scale, acute_scale
            )
            minor[i] = cut
            statuses.append(status)
            continue
        tangent = (
            incoming
            if len(prev.points) == 2
            else outgoing if len(nxt.points) == 2 else unit(add(incoming, outgoing))
        )

        def cubic(seg):
            if len(seg.points) == 4:
                return list(seg.points)
            p, q, r = seg.points
            return [p, lerp(p, q, 2 / 3), lerp(r, q, 2 / 3), r]

        # Cubic handles are independent at each end, so repairing this join
        # does not introduce another kink at the neighboring native join.
        if len(prev.points) > 2:
            points = cubic(prev)
            points[-2] = sub(
                points[-1], mul(tangent, norm(sub(points[-1], points[-2])))
            )
            contour[i - 1] = Segment(tuple(points))
        if len(nxt.points) > 2:
            points = cubic(nxt)
            points[1] = add(points[0], mul(tangent, norm(sub(points[1], points[0]))))
            contour[i] = Segment(tuple(points))
        statuses.append("minor-join-smoothed")
    contour = insert_cuts(contour, minor)
    boundaries = [
        i for i, s in enumerate(contour) if turn(contour[i - 1], s)[0] > pi / 36
    ]
    if not boundaries:
        return contour, statuses + ["smooth"] * len(contour)
    runs = []
    for j, start in enumerate(boundaries):
        end = boundaries[(j + 1) % len(boundaries)]
        parts = contour[start:end] if end > start else contour[start:] + contour[:end]
        runs.append(CurveRun(parts))
    # Share each run's space between its two ends. A short crossbar need not
    # shrink its outer cap when the smaller inner fillet already leaves room.
    # Acute inner joins retain a conservative share to protect the aperture.
    node_rules = []
    for i, nxt in enumerate(runs):
        angle, signed = turn(runs[i - 1], nxt)
        optical = profile_multiplier if signed > 0 or angle > pi * 110 / 180 else 1
        desired = radius * optical * (inner_scale if signed > 0 else 1)
        if angle > pi * 2 / 3:
            desired *= acute_scale
        node_rules.append((angle, signed, optical, desired * tan(angle / 2)))
    budgets = []
    for i, run in enumerate(runs):
        start, end = node_rules[i], node_rules[(i + 1) % len(runs)]
        available = 0.90 * run.length()
        if (start[1] > 0) != (end[1] > 0):
            if start[1] > 0:
                a = min(start[3], 0.42 * run.length())
                b = available - a
            else:
                b = min(end[3], 0.42 * run.length())
                a = available - b
        else:
            a = b = available / 2
        budgets.append((a, b))
    changes = []
    for i, nxt in enumerate(runs):
        prev = runs[i - 1]
        angle, signed, optical, _ = node_rules[i]
        cut, status = fillet(
            prev,
            nxt,
            radius * optical,
            inner_scale,
            acute_scale,
            limit_prev=budgets[i - 1][1],
            limit_next=budgets[i][0],
        )
        changes.append(cut)
        statuses.append(status)
        if audit is not None:
            audit.append(
                {
                    "point": list(nxt.at(0)),
                    "turn_degrees": round(angle * 180 / pi, 3),
                    "class": (
                        "inner"
                        if signed > 0
                        else "acute" if angle > pi * 110 / 180 else "outer"
                    ),
                    "status": status,
                    "radius": round(cut[3], 4) if cut else None,
                    "target_radius": round(cut[4], 4) if cut else None,
                    "arc_start": list(cut[2].points[0]) if cut else None,
                    "arc_end": list(cut[2].points[-1]) if cut else None,
                    "arc_center": (
                        list(
                            add(
                                cut[2].points[0],
                                mul(
                                    (-cut[2].tangent(0)[1], cut[2].tangent(0)[0]),
                                    (1 if signed > 0 else -1) * cut[3],
                                ),
                            )
                        )
                        if cut
                        else None
                    ),
                    "limit_reason": (
                        "available span or local curve clearance"
                        if cut and cut[3] < cut[4] - 0.001
                        else None
                    ),
                    "continuous_segments_before": len(prev.segments),
                    "continuous_segments_after": len(nxt.segments),
                }
            )
    return insert_cuts(runs, changes, runs=True), statuses


def quantization_tolerance(prev, nxt, upm):
    # Two independent integer-grid roundings affect each tangent vector.
    unit = 1024 / upm
    a = hypot(
        prev.points[-1][0] - prev.points[-2][0], prev.points[-1][1] - prev.points[-2][1]
    )
    b = hypot(nxt.points[1][0] - nxt.points[0][0], nxt.points[1][1] - nxt.points[0][1])
    return degrees(
        asin(min(1, 2**0.5 * unit / max(a, 1e-9)))
        + asin(min(1, 2**0.5 * unit / max(b, 1e-9)))
    )
