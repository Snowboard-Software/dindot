"""Small, opt-in data improvements; the existing display outlines stay intact."""

from copy import deepcopy
from fontTools.ttLib.tables import otTables as ot
from fontTools.otlLib.builder import buildLookup, buildSingleSubstSubtable
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
from extensions import rect, combine, canonical
from rounding import contours, path_from_contours, round_contour

# The largest native advance in the four weights, in the 1024-unit design space.
# Keeping each symbol's own width avoids turning ordinary numbers into code.
from pathlib import Path
import json

NUMERIC_WIDTHS = json.loads(
    (Path(__file__).with_name("numeric-widths.json")).read_text()
)


def register_feature(font, tag):
    """Make an explicitly supported feature available in every script/language.

    Some native features were only registered under DFLT. A shaping engine
    selecting latn (or its PLK language) then could not activate them at all.
    This changes opt-in availability, never default feature activation.
    """
    gsub = font["GSUB"].table
    index = next(
        i for i, r in enumerate(gsub.FeatureList.FeatureRecord) if r.FeatureTag == tag
    )
    for script in gsub.ScriptList.ScriptRecord:
        systems = [script.Script.DefaultLangSys] + [
            r.LangSys for r in script.Script.LangSysRecord
        ]
        for system in systems:
            if system is not None and index not in system.FeatureIndex:
                system.FeatureIndex = sorted([*system.FeatureIndex, index])
                system.FeatureCount = len(system.FeatureIndex)


def add_feature(font, tag, mapping, label=None):
    """Append a lookup without recompiling or replacing the upstream layout."""
    gsub = font["GSUB"].table
    lookup = buildLookup([buildSingleSubstSubtable(mapping)])
    index = len(gsub.LookupList.Lookup)
    gsub.LookupList.Lookup.append(lookup)
    gsub.LookupList.LookupCount += 1
    records = gsub.FeatureList.FeatureRecord
    existing = next((r for r in records if r.FeatureTag == tag), None)
    if existing:
        existing.Feature.LookupListIndex.append(index)
        existing.Feature.LookupCount += 1
        register_feature(font, tag)
        return
    record = ot.FeatureRecord()
    record.FeatureTag = tag
    record.Feature = ot.Feature()
    record.Feature.FeatureParams = None
    if label:
        params = ot.FeatureParamsStylisticSet()
        params.Version = 0
        params.UINameID = font["name"].addName(label)
        record.Feature.FeatureParams = params
    record.Feature.LookupListIndex = [index]
    record.Feature.LookupCount = 1
    old = list(records)
    records.append(record)
    records.sort(key=lambda r: r.FeatureTag)
    remap = {i: records.index(r) for i, r in enumerate(old)}
    new_index = records.index(record)
    for script in gsub.ScriptList.ScriptRecord:
        systems = [script.Script.DefaultLangSys] + [
            r.LangSys for r in script.Script.LangSysRecord
        ]
        for system in systems:
            if system is None:
                continue
            system.FeatureIndex = sorted(
                [remap[i] for i in system.FeatureIndex] + [new_index]
            )
            system.FeatureCount = len(system.FeatureIndex)
            if system.ReqFeatureIndex != 0xFFFF:
                system.ReqFeatureIndex = remap[system.ReqFeatureIndex]
    gsub.FeatureList.FeatureCount = len(records)


def readable_i(font, radius, to_glyph):
    """A restrained barred I; rounded with the same system as the letters."""
    upm = font["head"].unitsPerEm
    scale = upm / 1024
    g = font["glyf"]["I"]
    g.recalcBounds(font["glyf"])
    stem = (g.xMax - g.xMin) / scale
    top = g.yMax / scale
    bar = stem * 0.72
    p = combine(
        rect(190 - stem / 2, 0, 190 + stem / 2, top),
        rect(30, 0, 350, bar),
        rect(30, top - bar, 350, top),
    )
    rounded = [round_contour(c, radius, 0.55, 0.65)[0] for c in contours(canonical(p))]
    glyph = to_glyph(path_from_contours(rounded))
    pen = TTGlyphPen(font.getGlyphSet())
    glyph.draw(TransformPen(pen, (scale, 0, 0, scale, 0, 0)), font["glyf"])
    return pen.glyph()


def optimize_report_font(font, radius, to_glyph):
    scale = font["head"].unitsPerEm / 1024
    order = list(font.getGlyphOrder())
    mapping, records = {}, {}
    for source, width in NUMERIC_WIDTHS.items():
        assert source in order, source
        name = source + ".data"
        assert name not in order
        advance = round(width * scale)
        old_width = font["hmtx"][source][0]
        dx = round((advance - old_width) / 2)
        pen = TTGlyphPen(font.getGlyphSet())
        pen.addComponent(source, (1, 0, 0, 1, dx, 0))
        font["glyf"][name] = pen.glyph()
        font["glyf"][name].recalcBounds(font["glyf"])
        font["hmtx"][name] = advance, getattr(font["glyf"][name], "xMin", 0)
        order.append(name)
        mapping[source] = name
        records[name] = {
            "kind": "data-alternate",
            "reference": source,
            "feature": "tnum",
            "advance": width,
            "decision": "Native outline, centered in a weight-stable numeric advance.",
        }
    name = "I.ss03"
    font["glyf"][name] = readable_i(font, radius, to_glyph)
    font["glyf"][name].recalcBounds(font["glyf"])
    font["hmtx"][name] = round(380 * scale), font["glyf"][name].xMin
    order.append(name)
    records[name] = {
        "kind": "data-alternate",
        "reference": "I",
        "feature": "ss03",
        "decision": "Optional barred capital I; the display I remains unchanged.",
    }
    font.setGlyphOrder(order)
    for name in records:
        font["GDEF"].table.GlyphClassDef.classDefs[name] = 1
    add_feature(font, "tnum", mapping)
    add_feature(font, "ss03", {"I": "I.ss03"}, "Readable capital I")
    return records


def without_data_features(font):
    """Reassemble the source layout using the actual preserved lookup prefix.

    Only features/scripts added by DINDOT are stripped. The returned lookup
    bytes still come from the exported font, making the regression meaningful.
    """
    from build import load_source

    style = font["name"].getDebugName(17)
    source, _ = load_source(style)
    table = deepcopy(font["GSUB"])
    original = source["GSUB"].table
    count = original.LookupList.LookupCount
    table.table.LookupList.Lookup = table.table.LookupList.Lookup[:count]
    table.table.LookupList.LookupCount = count
    table.table.FeatureList = deepcopy(original.FeatureList)
    table.table.ScriptList = deepcopy(original.ScriptList)
    return table
