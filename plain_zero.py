"""The plain zero: every dotted zero without its dot, behind ss04.

The dotted zero stays the default. ss04 swaps each glyph that carries the
zero dot for a copy without it: same advance, same outline, one contour
fewer. It runs on the unhinted faces, uprights and italics alike, so the
autohinter treats the plain zeros like every other glyph, and its lookup
comes last, so tabular, old-style, fraction and script zeros switch too.
"""

from copy import deepcopy

from fontTools.ttLib.tables import ttProgram
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates

from data_features import add_feature


def contour_boxes(glyph):
    coords, ends, _ = glyph.getCoordinates(None)
    starts = [0] + [e + 1 for e in ends[:-1]]
    boxes = []
    for s, e in zip(starts, ends):
        xs = [p[0] for p in coords[s : e + 1]]
        ys = [p[1] for p in coords[s : e + 1]]
        boxes.append((min(xs), min(ys), max(xs), max(ys)))
    return boxes


def nested_circles(glyph):
    """[(index, diameter)] of near-circular contours inside two other
    contours: a dot in a counter, such as the zero's."""
    boxes = contour_boxes(glyph)
    found = []
    for i, (x0, y0, x1, y1) in enumerate(boxes):
        w, h = x1 - x0, y1 - y0
        if w <= 0 or abs(w - h) > 0.06 * max(w, h):
            continue
        around = [
            j
            for j, (a0, b0, a1, b1) in enumerate(boxes)
            if j != i and a0 < x0 and a1 > x1 and b0 < y0 and b1 > y1
        ]
        if len(around) >= 2:
            found.append((i, max(w, h)))
    return found


def without_contour(glyph, index):
    """A copy of a simple glyph with one contour removed, every other point
    untouched."""
    coords, ends, flags = glyph.getCoordinates(None)
    start = 0 if index == 0 else ends[index - 1] + 1
    stop = ends[index] + 1
    out = Glyph()
    out.numberOfContours = glyph.numberOfContours - 1
    out.coordinates = GlyphCoordinates(list(coords[:start]) + list(coords[stop:]))
    out.flags = bytearray(list(flags[:start]) + list(flags[stop:]))
    out.endPtsOfContours = list(ends[:index]) + [e - (stop - start) for e in ends[index + 1 :]]
    out.program = ttProgram.Program()
    out.program.fromBytecode(b"")
    return out


def clone_positioning(font, mapping):
    """Give each new glyph its source's kerning and mark attachment. New glyphs
    have the highest glyph ids, so appending keeps every coverage sorted."""
    rank = {g: i for i, g in enumerate(font.getGlyphOrder())}
    added = sorted(mapping.items(), key=lambda item: rank[item[1]])
    for lookup in font["GPOS"].table.LookupList.Lookup:
        assert lookup.LookupType in (2, 4), ("unexpected GPOS lookup type", lookup.LookupType)
        for st in lookup.SubTable:
            if lookup.LookupType == 2 and st.Format == 1:
                for pairset in st.PairSet:
                    seconds = {r.SecondGlyph: r for r in pairset.PairValueRecord}
                    for source, name in added:
                        if source in seconds:
                            clone = deepcopy(seconds[source])
                            clone.SecondGlyph = name
                            pairset.PairValueRecord.append(clone)
                    pairset.PairValueCount = len(pairset.PairValueRecord)
                firsts = list(st.Coverage.glyphs)
                for source, name in added:
                    if source in firsts:
                        st.Coverage.glyphs.append(name)
                        st.PairSet.append(deepcopy(st.PairSet[firsts.index(source)]))
                st.PairSetCount = len(st.PairSet)
            elif lookup.LookupType == 2:
                for source, name in added:
                    if source in st.Coverage.glyphs:
                        st.Coverage.glyphs.append(name)
                    for classdef in (st.ClassDef1, st.ClassDef2):
                        if source in classdef.classDefs:
                            classdef.classDefs[name] = classdef.classDefs[source]
            else:
                bases = list(st.BaseCoverage.glyphs)
                for source, name in added:
                    if source in bases:
                        st.BaseCoverage.glyphs.append(name)
                        st.BaseArray.BaseRecord.append(deepcopy(st.BaseArray.BaseRecord[bases.index(source)]))
                st.BaseArray.BaseCount = len(st.BaseArray.BaseRecord)


def add_plain_zero(font, settings):
    """Append `<name>.ss04` for every dotted zero in settings["glyphs"] and the
    ss04 lookup that selects them. Returns {dotted: plain}."""
    glyf, hmtx = font["glyf"], font["hmtx"]
    mapping = {}
    for name in settings["glyphs"]:
        glyph = glyf[name]
        assert not glyph.isComposite(), (name, "a dotted zero is a decomposed outline")
        assert not (glyph.program and glyph.program.getBytecode()), (name, "add plain zeros before hinting")
        dots = nested_circles(glyph)
        assert len(dots) == 1, (name, "exactly one zero dot", dots)
        plain = without_contour(glyph, dots[0][0])
        plain.recalcBounds(glyf)
        mapping[name] = f"{name}.{settings['feature']}"
        glyf.glyphs[mapping[name]] = plain
        hmtx[mapping[name]] = (hmtx[name][0], plain.xMin)
    font.setGlyphOrder(font.getGlyphOrder() + list(mapping.values()))
    glyf.glyphOrder = font.getGlyphOrder()
    classes = font["GDEF"].table.GlyphClassDef.classDefs
    for source, name in mapping.items():
        if source in classes:
            classes[name] = classes[source]
    clone_positioning(font, mapping)
    add_feature(font, settings["feature"], mapping, settings["label"])
    font["maxp"].numGlyphs = len(font.getGlyphOrder())
    font["OS/2"].recalcAvgCharWidth(font)
    return mapping
