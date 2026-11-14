"""One-time, auditable migration of the OFL v0.22.0 release to editable UFOs.

Normal builds do not run this script or require the old binaries. Subsequent
design changes belong in sources/*.ufo. See sources/README.md for provenance.
"""
from argparse import ArgumentParser
from pathlib import Path
from math import tan, radians
import copy
import json
import unicodedata as ud
from io import BytesIO

from extractor.formats.opentype import extractFontFromOpenType
from fontFeatures.ttLib import unparse
from fontFeatures import Attachment, Routine
from fontTools.ttLib import TTFont
from fontTools.ttLib.scaleUpem import scale_upem
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from fontTools.pens.pointPen import ReverseContourPointPen
from fontTools.pens.recordingPen import RecordingPointPen
from ufoLib2 import Font
from ufoLib2.objects import Anchor, Component
from ufo2ft.filters import DecomposeComponentsFilter, RemoveOverlapsFilter

ROOT = Path(__file__).resolve().parents[1]
UPM = 2048
COPYRIGHT = ("Copyright 2021-2024 The DINish Project Authors "
             "(https://github.com/playbeing/dinish); "
             "Copyright 2026 GetDot (DINDOT modifications).")


def cmap(u):
    return {cp: g.name for g in u for cp in g.unicodes}


def alias(u, cp, base):
    g = u.newGlyph(f"uni{cp:04X}")
    g.unicodes = [cp]
    g.width = u[base].width
    g.components.append(Component(base))
    g.note = f"Same letterform as {base}; separate Cyrillic encoding."
    return g


def outline(u, name, base):
    g = u.newGlyph(name)
    g.width = u[base].width
    u[base].draw(g.getPen())
    return g


def add_cyrillic(u, italic):
    """Complete the orthographies already inferred by the GF shaping check.

    Diacritics are canonical composites. New non-decomposing letters use the
    family's own en, ghe, ka, I and AE, with newly drawn hook/stroke details.
    These additions are candidates for native-reader design review.
    """
    cm = cmap(u)
    added = []
    for cp, basecp in [(0x4C0, 0x49), (0x4CF, 0x49),
                       (0x4D4, 0xC6), (0x4D5, 0xE6)]:
        alias(u, cp, cm[basecp])
        added.append(cp)

    for cap in (True, False):
        en = cm[0x41D if cap else 0x43D]
        ge = cm[0x413 if cap else 0x433]
        ka = cm[0x41A if cap else 0x43A]
        x0, _, x1, h = u[ge].getBounds(u)
        # Stem thickness follows this weight's capital I.
        ib = u[cm[0x49]].getBounds(u)
        sh = tan(radians(15)) if italic else 0
        t = ib.xMax - ib.xMin - sh * (ib.yMax - ib.yMin)

        # En-ghe ligature joins the right stem of en to the stem of ghe.
        cp = 0x4A4 if cap else 0x4A5
        g = alias(u, cp, en)
        eb = u[en].getBounds(u)
        shift = eb.xMax - sh * (eb.yMax-eb.yMin) - t - x0
        g.components.append(Component(ge, (1, 0, 0, 1, shift, 0)))
        g.width = round(u[en].width + (x1 - x0 - t))
        g.note = "En-ghe ligature assembled from this face's en and ghe."
        added.append(cp)

        # Ka with a short vertical stroke through its diagonal junction.
        cp = 0x49C if cap else 0x49D
        g = alias(u, cp, ka)
        kb = u[ka].getBounds(u)
        x = kb.xMin + t * 1.6
        p = TransformPen(ReverseContourPen(g.getPen()), (1, 0, sh, 1, 0, 0))
        y0, y1 = h * .22, h * .80
        r = min(t * .20, 12)
        rounded_rect(p, x, y0, x + t * .7, y1, r)
        g.note = "Ka with a new weight-matched short vertical stroke."
        added.append(cp)

        # Ghe with middle hook: keep the native ghe and draw its open bowl.
        cp = 0x494 if cap else 0x495
        g = alias(u, cp, ge)
        g.width = max(g.width, round(x0 + h * .68 + t))
        p = TransformPen(g.getPen(), (1, 0, sh, 1, 0, 0))
        left = x0 + t * .65
        right = x0 + h * .62
        top, bottom = h * .55, -h * .28
        mid = (top + bottom) / 2
        # A single open ring contour merges into the existing left stem.
        p.moveTo((left, top - t))
        p.curveTo((right - t, top + t * .25), (right, top - t), (right, mid))
        p.curveTo((right, bottom), (left + t, bottom - t * .2), (x0, bottom + t))
        p.lineTo((x0 + t * .25, bottom + t * 1.9))
        p.curveTo((left + t, bottom + t * .6), (right - t, bottom + t), (right - t, mid))
        p.curveTo((right - t, top - t * 1.8), (left + t, top - t * 1.8), (left, top - t * 2))
        p.closePath()
        g.note = "Native ghe with a newly drawn open middle hook; review proof."
        added.append(cp)

    # Canonical Cyrillic diacritics, plus auxiliary Latin characters that can
    # be represented without inventing a new base design.
    cps = list(range(0x4D0, 0x4D4)) + [0x4D6, 0x4D7] + list(range(0x4DA, 0x4E0))
    cps += [0x4E4, 0x4E5, 0x4E6, 0x4E7, 0x4EC, 0x4ED,
            0x4F0, 0x4F1, 0x4F2, 0x4F3, 0x4F4, 0x4F5, 0x1FE, 0x1FF]
    for cp in cps:
        if cp in cmap(u):
            continue
        parts = [ord(c) for c in ud.normalize("NFD", chr(cp))]
        cm = cmap(u)
        if len(parts) != 2 or any(c not in cm for c in parts):
            raise ValueError(f"Missing decomposition for U+{cp:04X}: {parts}")
        base, mark = (cm[c] for c in parts)
        g = alias(u, cp, base)
        x0, _, x1, y1 = u[base].getBounds(u)
        # Use the family's existing top attachment where available.
        a = next((a for a in u[base].anchors if a.name == "Anchor-1"), None)
        top = (a.x, a.y) if a else ((x0 + x1) / 2, y1 + 132)
        ma = next(a for a in u[mark].anchors if a.name == "_Anchor-1")
        g.components.append(Component(mark, (1, 0, 0, 1, top[0] - ma.x, top[1] - ma.y)))
        g.note = f"Canonical composition of {base} and {mark}."
        added.append(cp)

    for cp in (0x2028, 0x2029):
        g = u.newGlyph(f"uni{cp:04X}")
        g.unicodes = [cp]
        g.width = 0
        added.append(cp)
    return added


def rounded_rect(p, x0, y0, x1, y1, r):
    k = .5522847498
    p.moveTo((x0 + r, y0))
    p.lineTo((x1 - r, y0))
    p.curveTo((x1-r+k*r,y0),(x1,y0+r-k*r),(x1,y0+r))
    p.lineTo((x1,y1-r))
    p.curveTo((x1,y1-r+k*r),(x1-r+k*r,y1),(x1-r,y1))
    p.lineTo((x0+r,y1))
    p.curveTo((x0+r-k*r,y1),(x0,y1-r+k*r),(x0,y1-r))
    p.lineTo((x0,y0+r))
    p.curveTo((x0,y0+r-k*r),(x0+r-k*r,y0),(x0+r,y0))
    p.closePath()


def fix_attachments(u, ff):
    rules = [r.routine.rules[0] for r in ff.features["mark"]]
    below, above, horn = rules
    for rule in rules:
        rule.font = None
    # The mark's intended anchor is at the circle's upper right, not its center.
    b = u["dottedcircle"].getBounds(u)
    horn.bases["dottedcircle"] = (round(b.xMax - 60), round(b.yMax))
    for g in u:
        if g.name != "idotaccent" and (not g.unicodes or not any(ud.category(chr(c)).startswith("L") for c in g.unicodes)):
            continue
        b = g.getBounds(u)
        if b is None:
            continue
        if g.name not in above.bases:
            above.bases[g.name] = (round((b.xMin + b.xMax)/2), round(b.yMax + 132))
        if g.name not in below.bases:
            below.bases[g.name] = (round((b.xMin + b.xMax)/2), min(0, round(b.yMin)) - 172)
        ff.glyphclasses[g.name] = "base"
    # Above marks can themselves receive another accent (Lithuanian dot + acute).
    tops = {}
    for name in above.marks:
        b = u[name].getBounds(u)
        tops[name] = (round((b.xMin+b.xMax)/2), round(b.yMax + 100))
    ff.addFeature("mkmk", [Routine("DindotMarkStacking", rules=[Attachment(
        "DindotStackTop", "DindotStackMark", bases=tops,
        marks=copy.deepcopy(above.marks), force_markmark=True)])])
    # Publish the attachment locations as editable UFO anchors as well as FEA.
    # The checked-in FEA is authoritative; normal builds do not regenerate it.
    for rule in rules:
        for name, xy in rule.bases.items():
            anchor_name = {above.base_name:"top",below.base_name:"bottom",horn.base_name:"horn"}[rule.base_name]
            u[name].anchors.append(Anchor(xy[0], xy[1], anchor_name))
    for name, xy in tops.items():
        u[name].anchors.append(Anchor(xy[0], xy[1], "stack_top"))


def latin_core_unencoded(u, ff):
    """Include Latin Core's unencoded Catalan dots and dotted-i form."""
    dot = u["periodcentered"]
    b = dot.getBounds(u)
    for name, letter in [("periodcentered.loclCAT", "l"),
                         ("periodcentered.loclCAT.case", "L")]:
        g = u.newGlyph(name)
        g.width = dot.width
        height = u[letter].getBounds(u).yMax
        # The lowercase l is an ascender; center its dot on x-height instead.
        if letter == "l":
            height = u.info.xHeight
        g.components.append(Component("periodcentered", (1,0,0,1,0,round(height/2-(b.yMin+b.yMax)/2))))
        ff.glyphclasses[name] = "base"
    g = u.newGlyph("idotaccent")
    g.width = u["i"].width
    g.components.append(Component("i"))
    ff.glyphclasses[g.name] = "base"


def soft_dotted_forms(u, ff):
    """Remove a soft tittle before an above mark, preserving explicit dots."""
    cm = cmap(u)
    pairs = []
    # Soft_Dotted characters present in this family's repertoire (Unicode
    # PropList.txt). Preserve each base's own outline origin and advance.
    for cp in (0x69,0x6A,0x12F,0x249,0x268,0x29D,0x2B2,0x3F3,0x456,0x458,
               0x1D62,0x1D96,0x1DA4,0x1DA8,0x1ECB,0x2071,0x2148,0x2149,0x2C7C):
        if cp not in cm:
            continue
        base = cm[cp]
        target = base + ".dotless"
        g = u[base].copy(name=target)
        g.unicodes = []
        u.addGlyph(g)
        DecomposeComponentsFilter(include=[target])(u)
        # A soft dot is the highest separate contour, above the stem.
        bounds = [(i,c.getBounds()) for i,c in enumerate(g.contours)]
        index, box = max(bounds, key=lambda pair: pair[1].yMax)
        assert box.yMax-box.yMin < u.info.unitsPerEm * .25, (base,"tittle not isolated")
        del g.contours[index]
        g.note = "Soft-dotted form without its tittle, selected before above marks."
        # Give the unencoded form the normal top/bottom mark attachments.
        for ref in ff.features["mark"][:2]:
            rule=ref.routine.rules[0]
            if base in rule.bases:
                rule.bases[target]=rule.bases[base]
        ff.glyphclasses[target]="base"
        pairs.append((base,target))
    return pairs


def migrate(release):
    report = {}
    for path in sorted((release / "fonts").glob("*.ttf")):
        f = TTFont(path, recalcTimestamp=False)
        # Hint programs cannot be rescaled. The new build autohints from sources.
        for g in f["glyf"].glyphs.values():
            g.removeHinting()
        for tag in ("fpgm", "prep", "cvt ", "hdmx", "LTSH", "VDMX", "DSIG", "gasp"):
            if tag in f:
                del f[tag]
        scale_upem(f, UPM)
        u = Font()
        buffer = BytesIO()
        f.save(buffer)
        buffer.seek(0)
        extractFontFromOpenType(buffer, u, doInstructions=False)
        ff = unparse(f, do_gdef=True)
        style = path.stem.removeprefix("DINDOT-")
        added = add_cyrillic(u, "Italic" in style)
        # Resolve only the newly drawn joins. Existing release outlines retain
        # their geometry; they are not subjected to a global Boolean cleanup.
        joined = [f"uni{cp:04X}" for cp in (0x494,0x495,0x49C,0x49D,0x4A4,0x4A5)]
        DecomposeComponentsFilter(include=joined)(u)
        RemoveOverlapsFilter(include=joined, backend="pathops")(u)
        latin_core_unencoded(u, ff)
        fix_attachments(u, ff)
        soft_dotted = soft_dotted_forms(u, ff)
        above = next(ref.routine.rules[0].marks for ref in ff.features["mark"]
                     if "acutecomb" in ref.routine.rules[0].marks)
        # Catalan must inherit the full default Latin feature set, in addition
        # to its newly added dot positioning. Keep this in the source model.
        for routine in ff.routines:
            if ("latn", "dflt") in routine.languages:
                routine.languages.append(("latn", "CAT "))
        fea = ff.asFea()
        fea += """
feature locl {
    script latn;
    language CAT;
    sub l periodcentered' l by periodcentered.loclCAT;
    sub L periodcentered' L by periodcentered.loclCAT.case;
} locl;
feature ccmp {
    sub dotlessi dotaccentcmb by idotaccent;
} ccmp;
"""
        fea += "\n@DindotAboveMarks = ["+" ".join(above)+"];\nfeature ccmp {\n"
        for base, target in soft_dotted:
            fea += f"  sub {base}' @DindotAboveMarks by {target};\n"
        fea += "} ccmp;\n"
        # Retain caret locations for the real text ligatures.
        fea += "\ntable GDEF {\n"
        for lig in ("fi", "fl", "t_t"):
            fea += f"  LigatureCaretByPos {lig} {round(u[lig].width/2)};\n"
        for lig in ("onequarter", "onehalf", "threequarters"):
            fea += f"  LigatureCaretByPos {lig} {round(u[lig].width/3)} {round(u[lig].width*2/3)};\n"
        fea += "} GDEF;\n"
        # fontFeatures does not preserve stylistic-set UI labels.
        for tag, label in [("ss01", "Language specific stylistic alternates"),
                           ("ss02", "Cursive style in upright"),
                           ("ss03", "Readable capital I"), ("ss04", "Plain zero")]:
            fea += f'\nfeature {tag} {{ featureNames {{ name "{label}"; }}; }} {tag};\n'
        u.features.text = fea
        u.info.versionMajor, u.info.versionMinor = 1, 0
        u.info.openTypeOS2Selection = [7, 8]
        u.info.copyright = COPYRIGHT
        u.info.openTypeNameRecords = [r for r in u.info.openTypeNameRecords if r.nameID not in {0,1,2,3,4,5,6,16,17,256,257,258,259}]
        u.info.openTypeNameUniqueID = f"1.000;GETD;{path.stem}"
        u.info.openTypeNameVersion = "Version 1.000"
        u.info.openTypeNamePreferredFamilyName = "DINDOT"
        # RIBBI faces need no redundant typographic name records.
        if style in {"Regular", "Italic", "Bold", "BoldItalic"}:
            u.info.openTypeNamePreferredFamilyName = None
            u.info.openTypeNamePreferredSubfamilyName = None
        u.lib.pop("public.truetype.instructions", None)
        u.lib["public.openTypeMeta"] = {"dlng":["Latn", "Grek", "Cyrl"], "slng":["Latn", "Grek", "Cyrl"]}
        u.lib["public.glyphOrder"] = list(f.getGlyphOrder()) + [g.name for g in u if g.name not in f.getGlyphOrder()]
        for g in u:
            g.lib.pop("public.truetype.instructions", None)
            # Extractor keeps TrueType winding. UFO sources use the opposite
            # convention; fontmake reverses it again for TrueType output.
            if g.name in joined:
                # pathops union already returns the UFO winding convention.
                continue
            record = RecordingPointPen()
            reverse = ReverseContourPointPen(record)
            for contour in g.contours:
                contour.drawPoints(reverse)
            g.clearContours()
            record.replay(g.getPointPen())
        u.save(ROOT / "sources" / f"{path.stem}.ufo", overwrite=True)
        report[path.stem] = {"source_release": "v0.22.0", "upm_before":8192,
                             "upm_after":UPM, "added_codepoints":[f"U+{c:04X}" for c in added]}
        print(path.stem, len(u), "glyphs", len(added), "added codepoints")
    (ROOT / "documentation" / "google-fonts" / "source-migration.json").write_text(json.dumps(report,indent=2)+"\n")


if __name__ == "__main__":
    p = ArgumentParser(description=__doc__)
    p.add_argument("release_dir", type=Path, help="Unpacked, original v0.22.0 release")
    migrate(p.parse_args().release_dir)
