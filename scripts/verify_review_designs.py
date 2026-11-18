"""Verify the actual design behind the remaining dotted-zero QA heuristic."""
from argparse import ArgumentParser
from pathlib import Path
import json
from fontTools.ttLib import TTFont
from fontTools.pens.transformPen import TransformPen
from validate_fonts import FlattenPen, shape

ROOT=Path(__file__).resolve().parents[1]

def contours(font,name):
    gs=font.getGlyphSet();pen=FlattenPen(gs);gs[name].draw(pen)
    return len(pen.contours)

def verify(folder):
    result={}
    changes=json.loads((ROOT/"documentation/google-fonts/warning-cleanup-changes.json").read_text())
    repertoire=json.loads((ROOT/"documentation/google-fonts/subset-serving-audit.json").read_text())
    expected={int(cp[2:],16) for cp in repertoire["expected_codepoints"]}
    for path in sorted((folder/"ttf").glob("*.ttf")):
        font=TTFont(path);assert set(font.getBestCmap())==expected,path.name
        glyphs={}
        for name in ["zero.osf","zero.tlf","zero.tosf","uni2152"]:
            plain=name+".ss04"
            a,b=contours(font,name),contours(font,plain)
            assert a==b+1,(path.name,name,a,b)
            assert font["hmtx"][name]==font["hmtx"][plain],(path.name,name,"plain-zero spacing changed")
            glyphs[name]={"default_contours":a,"plain_zero_contours":b,"difference":"one intentional zero dot"}
        for features in [{"onum":True,"pnum":True},{"onum":True,"tnum":True},{"lnum":True,"tnum":True}]:
            dotted=shape(path,"0",features)[0][0]
            plain=shape(path,"0",dict(features,ss04=True))[0][0]
            assert contours(font,dotted)==contours(font,plain)+1,(path.name,features)
        gaps={};gs=font.getGlyphSet()
        for name,change in changes["styles"][path.stem]["carons"].items():
            body=FlattenPen(gs);gs[change["base"]].draw(body)
            mark=FlattenPen(gs);dx,dy=change["mark_offset"]
            gs[change["mark"]].draw(TransformPen(mark,(1,0,0,1,dx,dy)))
            distance=body.geometry().distance(mark.geometry())
            assert distance>=20,(path.name,name,"caron too close",distance)
            gaps[name]=distance
        result[path.stem]={"zero_design":glyphs,"caron_minimum_gaps_2048_units":gaps,
                           "exact_repertoire":"pass","encoded_codepoints":len(expected)}
    assert len(result)==8
    return result

if __name__=="__main__":
    p=ArgumentParser(description=__doc__);p.add_argument("--fonts",type=Path,default=ROOT/"fonts")
    p.add_argument("--report",type=Path);a=p.parse_args();result=verify(a.fonts)
    if a.report:a.report.write_text(json.dumps(result,indent=2)+"\n")
    print("Verified intentional zero dots, exact repertoire and distinct caron gaps in all eight styles.")
