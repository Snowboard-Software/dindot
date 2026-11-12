"""Review every glyph against the source for new outline/topology problems."""

from pathlib import Path
import json
from math import hypot
from fontTools.ttLib import TTFont
from shapely.geometry import Polygon, GeometryCollection
from shapely.validation import explain_validity
from build import load_source, normalized_outline
from rounding import contours, sub, cross, norm

ROOT = Path(__file__).resolve().parent
SETTINGS = json.loads((ROOT / "settings.json").read_text())


def flatten(seg):
    p = seg.points
    if len(p) == 2:
        return [p[0], p[-1]]
    chord = sub(p[-1], p[0])
    length = norm(chord)
    flat = max(
        abs(cross(chord, sub(x, p[0]))) / length if length else norm(sub(x, p[0]))
        for x in p[1:-1]
    )
    if flat < 0.25:
        return [p[0], p[-1]]
    left, right = seg.split(0.5)
    return flatten(left)[:-1] + flatten(right)


def polygon_data(font, name):
    polys = []
    invalid = []
    for i, c in enumerate(normalized_outline(font, name)):
        points = []
        for seg in c:
            points.extend(flatten(seg)[:-1])
        if len(points) < 3:
            continue
        area = sum(cross(a, b) for a, b in zip(points, points[1:] + points[:1])) / 2
        if abs(area) < 0.5:
            continue
        poly = Polygon(points)
        if not poly.is_valid:
            invalid.append({"contour": i, "reason": explain_validity(poly)})
        polys.append((area, poly))
    return polys, invalid


def region(polys):
    if not polys:
        return GeometryCollection()
    polys = sorted(polys, key=lambda a: abs(a[0]), reverse=True)
    sign = -1 if polys[0][0] < 0 else 1
    out = GeometryCollection()
    for area, poly in polys:
        # Only diagnostic topology uses repaired source contours; no generated font is repaired this way.
        if not poly.is_valid:
            poly = poly.buffer(0)
        out = out.union(poly) if area * sign > 0 else out.difference(poly)
    return out


def counts(region):
    if region.is_empty:
        return 0, 0
    polygons = (
        [region]
        if region.geom_type == "Polygon"
        else [p for p in region.geoms if p.geom_type == "Polygon"]
    )
    return len(polygons), sum(len(p.interiors) for p in polygons)


def audit():
    reports = {}
    issues = []
    DECISIONS = json.loads((ROOT / "audit/glyph-decisions.json").read_text())
    for style in SETTINGS["radii"]:
        # The letters drawn from DINish's parts are source glyphs too: their
        # square-cornered drawing is what the rounding must keep the topology of.
        source, _ = load_source(style)
        target = TTFont(ROOT / "masters" / f"DINDOT-{style}.ttf")
        rows = {}
        for name in target.getGlyphOrder():
            added = name not in source.getGlyphOrder()
            decision = DECISIONS[style].get(name, {})
            data_alternate = decision.get("kind") == "data-alternate"
            before, source_invalid = (
                polygon_data(target, decision["reference"])
                if data_alternate
                else ([], []) if added else polygon_data(source, name)
            )
            after, new_invalid = polygon_data(target, name)
            a, b = region(before), region(after)
            ca, ha = counts(a)
            cb, hb = counts(b)
            expected_extra = (
                1 if not data_alternate and not added and name.startswith("zero") else 0
            )
            if added and not data_alternate:
                expected = DECISIONS[style][name]["expected_topology"]
                ca, ha = expected["components"], expected["counters"]
            problems = []
            if new_invalid and not source_invalid:
                problems.append("new-self-intersection")
            if cb != ca + expected_extra:
                problems.append(
                    f"ink-components {ca}->{cb}; expected {ca+expected_extra}"
                )
            if hb != ha:
                problems.append(f"counters {ha}->{hb}")
            delta = (b.area / a.area - 1) * 100 if a.area else 0
            rows[name] = {
                "source_components": ca,
                "components": cb,
                "source_counters": ha,
                "counters": hb,
                "source_invalid": source_invalid,
                "outline_issues": new_invalid,
                "area_delta_percent": round(delta, 2),
                "problems": problems,
            }
            if problems:
                issues.append(
                    {
                        "style": style,
                        "glyph": name,
                        "problems": problems,
                        "detail": new_invalid,
                    }
                )
        reports[style] = rows
    (ROOT / "audit" / "geometry.json").write_text(json.dumps(reports, indent=2) + "\n")
    (ROOT / "audit" / "geometry-issues.json").write_text(
        json.dumps(issues, indent=2) + "\n"
    )
    print(
        json.dumps(
            {
                "glyphs_reviewed": sum(len(r) for r in reports.values()),
                "issues": issues,
            },
            indent=2,
        )
    )

    if issues:
        raise SystemExit(
            "Outline geometry audit failed; see audit/geometry-issues.json"
        )
    # The italics have no DINish source of their own: they are drawn from the
    # upright outlines, so their topology is audited against the uprights.
    print(
        "Italics not reviewed here: audit_text.py checks each italic glyph's "
        "topology against its upright, and validate.py its contours at export precision."
    )


if __name__ == "__main__":
    audit()
