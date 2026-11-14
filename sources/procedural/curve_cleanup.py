"""Bounded cubic refitting for tiny segments produced by Skia stroke offsets.

Offsetting a cubic can create hundreds of nearly degenerate quadratic pieces.
They survive visually at design scale, but integer export makes their handles
collapse into tiny stair steps. Refit only newly drawn/optical outlines, never
the preserved Display alphabet. The fit has a 0.18/1024 em error budget.
"""

from math import hypot
from rounding import Segment, add, sub, mul, dot, unit, norm


def samples(segment, tolerance=0.04):
    chord = sub(segment.points[-1], segment.points[0])
    length = norm(chord)
    flat = max(
        (
            (
                abs(
                    chord[0] * (p[1] - segment.points[0][1])
                    - chord[1] * (p[0] - segment.points[0][0])
                )
                / length
                if length
                else norm(sub(p, segment.points[0]))
            )
            for p in segment.points[1:-1]
        ),
        default=0,
    )
    if len(segment.points) == 2 or flat < tolerance:
        # Avoid a sparse long straight run next to a short transition.
        count = max(1, round(segment.length() / 12))
        return [segment.at(i / count) for i in range(count + 1)]
    a, b = segment.split(0.5)
    return samples(a, tolerance)[:-1] + samples(b, tolerance)


def fit_cubic(points, left, right, error=0.18):
    if len(points) == 2:
        d = norm(sub(points[1], points[0])) / 3
        return [
            Segment(
                (
                    points[0],
                    add(points[0], mul(left, d)),
                    add(points[-1], mul(right, d)),
                    points[-1],
                )
            )
        ]
    distances = [0]
    for a, b in zip(points, points[1:]):
        distances.append(distances[-1] + norm(sub(b, a)))
    if distances[-1] < 1e-6:
        return []
    params = [d / distances[-1] for d in distances]
    c00 = c01 = c11 = x0 = x1 = 0
    for p, u in zip(points, params):
        v = 1 - u
        b0 = v**3
        b1 = 3 * u * v * v
        b2 = 3 * u * u * v
        b3 = u**3
        a = mul(left, b1)
        b = mul(right, b2)
        residual = sub(p, add(mul(points[0], b0 + b1), mul(points[-1], b2 + b3)))
        c00 += dot(a, a)
        c01 += dot(a, b)
        c11 += dot(b, b)
        x0 += dot(a, residual)
        x1 += dot(b, residual)
    det = c00 * c11 - c01 * c01
    al = (x0 * c11 - x1 * c01) / det if abs(det) > 1e-12 else 0
    ar = (c00 * x1 - c01 * x0) / det if abs(det) > 1e-12 else 0
    chord = norm(sub(points[-1], points[0]))
    if min(al, ar) < 1e-6 * chord or max(al, ar) > distances[-1] * 2:
        al = ar = chord / 3
    curve = Segment(
        (
            points[0],
            add(points[0], mul(left, al)),
            add(points[-1], mul(right, ar)),
            points[-1],
        )
    )
    errors = [norm(sub(p, curve.at(u))) for p, u in zip(points, params)]
    worst = max(range(1, len(points) - 1), key=lambda i: errors[i])
    if errors[worst] <= error:
        return [curve]
    tangent = unit(sub(points[worst - 1], points[worst + 1]))
    if norm(tangent) < 0.1:
        tangent = unit(sub(points[worst - 1], points[worst]))
    return fit_cubic(points[: worst + 1], left, tangent, error) + fit_cubic(
        points[worst:], mul(tangent, -1), right, error
    )


def clean_contour(contour, error=0.18):
    if not contour:
        return []
    # Split the closed contour into four long spans, keeping exact tangents at
    # the shared boundaries. A single closed cubic has zero chord length.
    points = []
    for segment in contour:
        points.extend(samples(segment)[:-1])
    filtered = []
    for p in points:
        if not filtered or norm(sub(p, filtered[-1])) > 0.01:
            filtered.append(p)
    points = filtered
    if len(points) < 4:
        return contour
    indices = [round(len(points) * i / 4) for i in range(4)]
    output = []
    for k, start in enumerate(indices):
        end = indices[(k + 1) % 4]
        span = (
            points[start : end + 1]
            if end > start
            else points[start:] + points[: end + 1]
        )
        left = unit(sub(points[(start + 1) % len(points)], points[start - 1]))
        right = unit(sub(points[end - 1], points[(end + 1) % len(points)]))
        output.extend(fit_cubic(span, left, right, error))
    return output
