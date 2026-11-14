"""Kerning shared by the letters drawn from DINish's parts.

A letter's left side is where it stands second in a pair (ClassDef2, a
PairValueRecord's SecondGlyph); its right side is where it stands first
(Coverage, ClassDef1, its own PairSet).
"""

from copy import deepcopy

from fontTools.otlLib.builder import buildLookup, buildPairPosGlyphsSubtable, buildValue


def _pair_subtables(font):
    for lookup in font["GPOS"].table.LookupList.Lookup:
        if lookup.LookupType == 2:
            yield from lookup.SubTable


def copy_kerning(font, name, model, left=True, right=True):
    """Give `name` the kerning of `model` on its left side, its right side or
    both, wherever `name` has no kerning of its own."""
    gid = font.getGlyphID
    for sub in _pair_subtables(font):
        cover = sub.Coverage.glyphs
        if sub.Format == 1:
            if right and model in cover and name not in cover:
                sets = dict(zip(cover, sub.PairSet))
                sets[name] = deepcopy(sets[model])
                cover[:] = sorted(sets, key=gid)
                sub.PairSet = [sets[g] for g in cover]
                sub.PairSetCount = len(sub.PairSet)
            if left:
                for pair_set in sub.PairSet:
                    records = pair_set.PairValueRecord
                    seconds = {r.SecondGlyph for r in records}
                    if model in seconds and name not in seconds:
                        new = deepcopy(next(r for r in records if r.SecondGlyph == model))
                        new.SecondGlyph = name
                        records.append(new)
                        records.sort(key=lambda r: gid(r.SecondGlyph))
                        pair_set.PairValueCount = len(records)
        else:
            if right and model in cover and name not in cover:
                first = sub.ClassDef1.classDefs
                if model in first:
                    first[name] = first[model]
                cover.append(name)
                cover.sort(key=gid)
            if left:
                second = sub.ClassDef2.classDefs
                if model in second and name not in second:
                    second[name] = second[model]


def add_pair_lookup(font, pairs):
    """Append one glyph-pair lookup, {(first, second): x advance}, to the kern
    feature, after DINish's own: its values add to theirs."""
    if not pairs:
        return
    gpos = font["GPOS"].table
    kern = [r for r in gpos.FeatureList.FeatureRecord if r.FeatureTag == "kern"]
    flag = gpos.LookupList.Lookup[kern[0].Feature.LookupListIndex[0]].LookupFlag
    subtable = buildPairPosGlyphsSubtable(
        {k: (buildValue({"XAdvance": v}), None) for k, v in sorted(pairs.items())},
        font.getReverseGlyphMap(),
    )
    gpos.LookupList.Lookup.append(buildLookup([subtable], flags=flag))
    gpos.LookupList.LookupCount = len(gpos.LookupList.Lookup)
    for record in kern:
        record.Feature.LookupListIndex.append(gpos.LookupList.LookupCount - 1)
        record.Feature.LookupCount = len(record.Feature.LookupListIndex)
