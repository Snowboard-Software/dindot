"""Check source migration, shaping regressions, and repeatable output bytes."""
from argparse import ArgumentParser
from collections import Counter
from hashlib import sha256
from pathlib import Path
import json
import math
import random
from functools import lru_cache

from fontTools.ttLib import TTFont
from fontTools.agl import toUnicode
from fontTools.pens.basePen import BasePen
from shapely.geometry import MultiLineString
import uharfbuzz as hb

ROOT = Path(__file__).resolve().parents[1]


class FlattenPen(BasePen):
    """Sample outlines at 16 points per Bezier segment, in 2048-unit space."""
    def __init__(self, gs, scale=1):
        super().__init__(gs)
        self.scale = scale
        self.contours = []

    def put(self, p):
        self.contours[-1].append((p[0]*self.scale, p[1]*self.scale))

    def _moveTo(self, p):
        self.contours.append([])
        self.put(p)

    def _lineTo(self, p):
        self.put(p)

    def _qCurveToOne(self, p1, p2):
        p0 = self._getCurrentPoint()
        for i in range(1,17):
            t=i/16; s=1-t
            self.put(tuple(s*s*a+2*s*t*b+t*t*c for a,b,c in zip(p0,p1,p2)))

    def _curveToOne(self,p1,p2,p3):
        p0=self._getCurrentPoint()
        for i in range(1,17):
            t=i/16;s=1-t
            self.put(tuple(s**3*a+3*s*s*t*b+3*s*t*t*c+t**3*d for a,b,c,d in zip(p0,p1,p2,p3)))

    def _closePath(self):
        self.contours[-1].append(self.contours[-1][0])

    def _endPath(self):
        pass

    def geometry(self):
        return MultiLineString([c for c in self.contours if len(c)>1])


@lru_cache(maxsize=32)
def font_objects(path):
    f=TTFont(path)
    hf=hb.Font(hb.Face(path.read_bytes()))
    hf.scale=(8192,8192)
    return f,hf


def shape(path, text, features=None, language=None):
    f,hf=font_objects(path)
    b=hb.Buffer();b.add_str(text);b.guess_segment_properties()
    if language:b.language=language
    hb.shape(hf,b,features or {})
    return [(f.getGlyphName(i.codepoint),p.x_advance,p.y_advance,p.x_offset,p.y_offset)
            for i,p in zip(b.glyph_infos,b.glyph_positions)]


def latin_core(f):
    aliases={"nbspace":0xA0,"euro":0x20AC,"guillemetleft":0xAB,"guillemetright":0xBB,
             "idotless":0x131,"jdotless":0x237,"Idotaccent":0x130,
             "commaaccentcomb":0x326,"Germandbls":0x1E9E}
    unencoded={".notdef":".notdef", "periodcentered.loclCAT":"periodcentered.loclCAT",
               "periodcentered.loclCAT.case":"periodcentered.loclCAT.case",
               "caroncomb.alt":"caroncmb.alt", "idotaccent":"idotaccent"}
    missing=[]
    for name in (ROOT/"documentation/google-fonts/GF_Latin_Core.txt").read_text().splitlines():
        if not name or name.startswith("#"):continue
        if name in unencoded:
            present=unencoded[name] in f.getGlyphOrder()
        else:
            cps=toUnicode(name)
            cp=aliases.get(name,ord(cps) if len(cps)==1 else None)
            # Nice-name combining suffixes differ from Adobe Glyph List names.
            if cp is None and name.endswith("comb"):
                fallback={"circumflex":0x302,"macron":0x304,"breve":0x306,
                          "dotaccent":0x307,"dieresis":0x308,"ring":0x30A,
                          "hungarumlaut":0x30B,"caron":0x30C,"cedilla":0x327,"ogonek":0x328}
                cp=fallback.get(name[:-4])
            present=cp in f.getBestCmap()
        if not present:missing.append(name)
    assert not missing, f"Latin Core missing: {missing}"


def validate(reference, fonts, repeat=None):
    reports={}
    maintenance=json.loads((ROOT/"documentation/google-fonts/warning-cleanup-changes.json").read_text())
    rng=random.Random(22)
    alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,:;%+-/€()"
    sample=" ".join("".join(rng.choices(alphabet,k=12)) for _ in range(70))
    for path in sorted((fonts/"ttf").glob("*.ttf")):
        before=reference/"fonts"/path.name
        old,new=TTFont(before),TTFont(path)
        assert set(old.getBestCmap())-set(new.getBestCmap())==set(maintenance["removed_codepoints"]),path.name
        assert new["head"].unitsPerEm==2048
        assert new["name"].getDebugName(5)=="Version 1.001"
        assert new["OS/2"].fsSelection & 128
        latin_core(new)
        assert set(r.FeatureTag for r in old["GSUB"].table.FeatureList.FeatureRecord) <= set(r.FeatureTag for r in new["GSUB"].table.FeatureList.FeatureRecord)
        # Compare every original glyph geometrically, independent of contour
        # starting point, direction, decomposition and hint bytecode.
        og,ng=old.getGlyphSet(),new.getGlyphSet()
        worst_distance=0;worst_name=None;worst_width=0
        style_changes=maintenance["styles"][path.stem]
        not_exported=set(maintenance["non_exporting_glyphs"]+maintenance["removed_glyphs"])
        redesigned=set(style_changes["carons"])|{"uni221D"}
        compared=0
        for name in old.getGlyphOrder():
            if name in not_exported:
                assert name not in new.getGlyphOrder(),(path.name,name,"unused glyph exported")
                continue
            if name in redesigned:continue
            a=FlattenPen(og,.25);og[name].draw(a)
            b=FlattenPen(ng);ng[name].draw(b)
            ga,gb=a.geometry(),b.geometry()
            assert ga.is_empty==gb.is_empty, (path.name,name,"empty outline changed")
            if not ga.is_empty:
                dist=ga.hausdorff_distance(gb)
                if dist>worst_distance:worst_distance,worst_name=dist,name
                limit=2.5 if name in style_changes["outline_cleanup"] else 1.5
                assert dist<=limit,(path.name,name,"outline distance",dist,limit)
            delta=abs(old["hmtx"][name][0]/4-new["hmtx"][name][0])
            worst_width=max(worst_width,delta)
            assert delta<=.5,(path.name,name,"advance changed",delta)
            compared+=1
        # Intentional revisions have stricter structural/metric tests instead
        # of pretending that their old appearance and advances are unchanged.
        for name,change in style_changes["carons"].items():
            glyph=new["glyf"][name]
            assert glyph.isComposite() and len(glyph.components)==2,(path.name,name)
            assert [c.glyphName for c in glyph.components]==[change["base"],change["mark"]]
            assert new["hmtx"][name][0]==change["new_advance"]
            assert [glyph.components[1].x,glyph.components[1].y]==change["mark_offset"]
        assert new["hmtx"]["uni221D"][0]==new["hmtx"]["plus"][0]
        prop=new["glyf"]["uni221D"];prop.recalcBounds(new["glyf"])
        assert prop.xMin>=0 and prop.xMax<=new["hmtx"]["uni221D"][0],path.name
        stat=new["STAT"].table
        assert [a.AxisTag for a in stat.DesignAxisRecord.Axis]==["wght","ital"]
        assert stat.AxisValueArray.AxisValue[0].Value==new["OS/2"].usWeightClass
        assert stat.AxisValueArray.AxisValue[1].Value==int(bool(new["OS/2"].fsSelection&1))
        cases=0;max_position_delta=0
        texts=[sample,"AVATAR To We fi fl tt 0123456789 1/2 3/4 €12.40",
               "Ελληνικά ΑΒΓΔ ΖΗΘ ΙΚΛΜΝ ΞΟΠΡΣ ΤΥΦΧΨΩ",
               "Кириллица АБВГД ЕЖЗ ИЙКЛМНО ПРСТУФ ХЦЧШЩ ЪЫЬЭЮЯ"]
        features=[{}, {"tnum":True},{"pnum":True},{"onum":True},{"lnum":True},
                  {"ss03":True},{"ss04":True},{"frac":True}, {"sups":True},
                  {"subs":True},{"dnom":True},{"numr":True},{"liga":False},{"dlig":True}]
        for text in texts:
            for feat in features:
                a,b=shape(before,text,feat),shape(path,text,feat)
                assert [r[0] for r in a]==[r[0] for r in b],(path.name,"substitutions",feat)
                delta=max((abs(x-y) for r,s in zip(a,b) for x,y in zip(r[1:],s[1:])),default=0)
                max_position_delta=max(max_position_delta,delta)
                assert delta<=8,(path.name,"positioning",feat,delta)
                cases+=1
        for language in ["ca", "pl", "nl", "ro", "bg"]:
            for feat in features:
                a,b=shape(before,texts[1],feat,language),shape(path,texts[1],feat,language)
                assert [r[0] for r in a]==[r[0] for r in b],(path.name,"language features",language,feat)
                delta=max((abs(x-y) for r,s in zip(a,b) for x,y in zip(r[1:],s[1:])),default=0)
                assert delta<=8,(path.name,"language positioning",language,feat,delta)
                cases+=1
        # Corrected sequences must resolve to non-missing glyphs and must use
        # nonzero mark placement, including the original dotted-circle failure.
        for text in ["◌̛","Ą́","į̇́","є́","ї́","ё́","і́","j̀","ị́"]:
            result=shape(path,text)
            assert all(r[0]!=".notdef" for r in result),(path.name,text)
            assert any(r[3] or r[4] for r in result),(path.name,"unattached mark",text,result)
            old_result=shape(before,text)
            assert abs(sum(r[1] for r in old_result)-sum(r[1] for r in result))<=8,(path.name,"accented text width changed",text)
        catalan=shape(path,"l·l L·L",language="ca")
        assert {"periodcentered.loclCAT","periodcentered.loclCAT.case"} <= {r[0] for r in catalan}
        assert sum(r[1] for r in shape(path,"co\u00adoperate"))==sum(r[1] for r in shape(path,"cooperate"))
        if repeat:
            for folder,suffix in [("ttf",".ttf"),("webfonts",".woff2")]:
                filename=path.stem+suffix
                assert (fonts/folder/filename).read_bytes()==(repeat/folder/filename).read_bytes(),f"Non-reproducible {filename}"
        # WOFF2 must preserve every semantic table, ignoring its transform's
        # permitted loca/glyf encoding changes and head checksum adjustment.
        web=TTFont(fonts/"webfonts"/(path.stem+".woff2"))
        assert new.getBestCmap()==web.getBestCmap()
        for tag in ["GSUB","GPOS","GDEF","hmtx","OS/2","name","STAT","meta"]:
            assert new[tag].compile(new)==web[tag].compile(web),(path.name,tag,"webfont mismatch")
        reports[path.stem]={"original_glyphs_compared":compared,
            "codepoints_before":len(old.getBestCmap()),"codepoints_after":len(new.getBestCmap()),
            "max_outline_distance_2048_units":worst_distance,"worst_outline_glyph":worst_name,
            "max_advance_delta_2048_units":worst_width,"shaping_cases":cases,
            "max_shaping_position_delta_8192_units":max_position_delta,
            "latin_core_glyphs":"pass","ttf_woff2_tables":"pass",
            "intentional_revisions_tested":sorted(redesigned),
            "non_exporting_glyphs_verified":sorted(not_exported),
            "stat_style_linking":"pass","soft_hyphen_shaping":"pass",
            "byte_identical_rebuild":bool(repeat)}
        print(path.stem,json.dumps(reports[path.stem]),flush=True)
    assert len(reports)==8,"Expected all eight faces"
    return reports


if __name__=="__main__":
    p=ArgumentParser(description=__doc__)
    p.add_argument("--reference",type=Path,required=True,help="Unpacked original v0.22.0 release")
    p.add_argument("--fonts",type=Path,default=ROOT/"fonts")
    p.add_argument("--repeat",type=Path)
    p.add_argument("--report",type=Path)
    a=p.parse_args(); result=validate(a.reference,a.fonts,a.repeat)
    if a.report:a.report.write_text(json.dumps(result,indent=2)+"\n")
