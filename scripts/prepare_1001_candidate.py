"""One-time source maintenance from candidate 1.000 to 1.001.

This is an audit trail, not part of normal builds. The checked-in UFOs remain
the maintained sources. Run with requirements-maintenance.txt installed.
"""
from pathlib import Path
from math import ceil, hypot, atan2
import copy
import json
import re
import sys

from ufoLib2 import Font
from ufoLib2.objects import Component, Glyph
from fontTools.pens.reverseContourPen import ReverseContourPen

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"sources/procedural"))
from extensions import cubic_path, stroke
sys.path.insert(0,str(ROOT/"scripts"))
from validate_fonts import FlattenPen
import skia

UNUSED=["acutecomb.loclPLK", "tonoscomb", "dieresistonoscomb",
        "circumflexcmb.case", "brevecmb.case", "hookabovecomb.case"]
CARONS={"Lcaron":"L", "dcaron":"d", "lcaron":"l", "tcaron":"t"}


def same(a,b):
    return a.x==b.x and a.y==b.y


def cross(a,b,c):
    return (b.x-a.x)*(c.y-b.y)-(b.y-a.y)*(c.x-b.x)


def cleanup_contour(c, upright):
    """Remove zero-length paths and redundant straight points in the source."""
    changed=0
    while len(c.points)>2:
        points=c.points;remove=None
        for i,p in enumerate(points):
            a=points[i-1];b=points[(i+1)%len(points)]
            if p.type=="line" and a.type is not None and same(a,p):
                remove=[i];break
            if p.type=="line" and b.type=="line" and a.type is not None:
                # Integer-grid rounding can leave points fractionally off a
                # straight line. Remove them only within one design unit.
                length=hypot(b.x-a.x,b.y-a.y)
                deviation=abs(cross(a,p,b))/length if length else 0
                if deviation<=1 and (p.x-a.x)*(b.x-p.x)+(p.y-a.y)*(b.y-p.y)>=0:
                    remove=[i];break
            if p.type=="qcurve":
                indices=[];j=(i-1)%len(points)
                while points[j].type is None and j!=i:
                    indices.append(j);j=(j-1)%len(points)
                if indices and same(points[j],p) and all(same(points[k],p) for k in indices):
                    remove=indices+[i];break
        if remove is None:break
        for i in sorted(remove,reverse=True):del c.points[i]
        changed+=len(remove)
    snapped=0
    if upright:
        # Only snap genuine near-horizontal/vertical line segments. Move the
        # adjacent curve handle by the same amount to retain its tangent.
        for i,p in enumerate(c.points):
            a=c.points[i-1]
            if p.type!="line" or a.type is None:continue
            dx,dy=p.x-a.x,p.y-a.y
            if not dx and not dy:continue
            vertical=0<abs(dx)<=2 and abs(dy)>abs(dx)*115
            horizontal=0<abs(dy)<=2 and abs(dx)>abs(dy)*115
            if not(vertical or horizontal):continue
            axis="x" if vertical else "y"
            target=round((getattr(a,axis)+getattr(p,axis))/2)
            for index,point,adjacent in [((i-1)%len(c.points),a,(i-2)%len(c.points)),
                                         (i,p,(i+1)%len(c.points))]:
                delta=target-getattr(point,axis)
                setattr(point,axis,target)
                handle=c.points[adjacent]
                if handle.type is None:setattr(handle,axis,getattr(handle,axis)+delta)
            snapped+=1
    fitted=0
    # A few native-script curves are represented as gently turning polylines.
    # Replace a tiny kink by a tangent quadratic only when its maximum corner
    # displacement is bounded to 1.5 units. This preserves the endpoint
    # tangents instead of flattening a real curve into a straight chord.
    for i,p in enumerate(c.points):
        a=c.points[i-1];b=c.points[(i+1)%len(c.points)]
        if p.type!="line" or b.type!="line" or a.type is None:continue
        dot=(p.x-a.x)*(b.x-p.x)+(p.y-a.y)*(b.y-p.y)
        turn=abs(cross(a,p,b))
        length=hypot(b.x-a.x,b.y-a.y)
        if dot>0 and length and atan2(turn,dot)<.1 and turn/length/2<=1.5:
            p.type=None;b.type="qcurve";fitted+=1
    return changed,snapped,fitted


def boundary(g,u):
    p=FlattenPen(u);g.draw(p)
    return p.geometry()


def compose_carons(u):
    report={}
    ab=u["caroncmb.alt"].getBounds(u)
    for name,base in CARONS.items():
        g=u[name];old_width=g.width
        original=g.getBounds(u)
        last=g.contours[-1].getBounds()
        # Preserve the existing caron position when it is still separate.
        # In the heaviest dcaron it intersects the body and has been merged.
        if last.yMin>800 and last.yMax-last.yMin<500 and last.xMax-last.xMin<400:
            dx=round(last.xMax-ab.xMax);dy=round(last.yMax-ab.yMax)
        else:
            dx=round(original.xMax-ab.xMax);dy=0
        bb=boundary(u[base],u)
        accent=Glyph(name="caron-proof")
        for shift in range(0,241,4):
            accent.components=[Component("caroncmb.alt",(1,0,0,1,dx+shift,dy))]
            if bb.distance(boundary(accent,u))>=24:break
        else:raise ValueError((name,"cannot place a distinct caron"))
        dx+=shift
        g.clearContours();g.components.clear()
        g.components.extend([Component(base),Component("caroncmb.alt",(1,0,0,1,dx,dy))])
        g.width=max(old_width,ceil(g.getBounds(u).xMax+16))
        g.note="Base plus distinct alternate caron; preserve a visible gap at every weight."
        report[name]={"base":base,"mark":"caroncmb.alt","mark_offset":[dx,dy],
                      "old_advance":old_width,"new_advance":g.width,"additional_gap_shift":shift}
    return report


def proportional(u):
    """Redraw the existing centreline at operator width, keeping stroke weight."""
    g=u["uni221D"];old_width=g.width
    width=u["plus"].width
    minus=u["minus"].getBounds(u)
    weight=(minus.yMax-minus.yMin)*.92
    axis=565;cx=width*.55
    left=max(90,weight/2+24)
    right=width-max(94,weight/2+32)
    path=cubic_path([
        ("M",right,axis-310),
        ("C",right-160,axis-420,cx+210,axis-420,cx,axis),
        ("C",cx-220,axis+420,left,axis+410,left,axis),
        ("C",left,axis-410,cx-220,axis-420,cx,axis),
        ("C",cx+210,axis+420,right-160,axis+420,right,axis+310),
    ])
    ink=stroke(path,weight)
    g.clearContours();g.components.clear();g.width=width
    pen=ReverseContourPen(g.getPen())
    for verb,points in ink:
        pts=[(float(p.x()),float(p.y())) for p in points]
        if verb==skia.Path.kMove_Verb:pen.moveTo(pts[0])
        elif verb==skia.Path.kLine_Verb:pen.lineTo(pts[-1])
        elif verb==skia.Path.kQuad_Verb:pen.qCurveTo(*pts[1:])
        elif verb==skia.Path.kCubic_Verb:pen.curveTo(*pts[1:])
        elif verb==skia.Path.kClose_Verb:pen.closePath()
        else:raise ValueError(verb)
    g.note="Redrawn at the common math advance; constant stroke width, not an affine squeeze."
    return {"old_advance":old_width,"new_advance":width,"stroke_width":weight}


def main():
    report={"version":"1.001","removed_codepoints":[173],"non_exporting_glyphs":UNUSED,
            "removed_glyphs":["uni00AD"],"styles":{}}
    for path in sorted((ROOT/"sources").glob("*.ufo")):
        u=Font.open(path)
        assert (u.info.versionMajor,u.info.versionMinor)==(1,0),"Run only on the unmodified 1.000 sources"
        assert u["uni00AD"].unicodes==[173]
        del u["uni00AD"]
        u.lib["public.skipExportGlyphs"]=UNUSED
        u.lib["public.glyphOrder"]=[n for n in u.lib["public.glyphOrder"] if n!="uni00AD"]
        for name in ["uni00AD"]+UNUSED:
            # These occurrences are GDEF classification, not active lookups.
            pattern=r"(?<![\w.])"+re.escape(name)+r"(?![\w.])"
            u.features.text=re.sub(pattern,"",u.features.text)
        carons=compose_carons(u)
        prop=proportional(u)
        clean={}
        for g in u:
            removed=snapped=fitted=0
            for c in g.contours:
                n,s,f=cleanup_contour(c,"Italic" not in path.stem)
                removed+=n;snapped+=s;fitted+=f
            if removed or snapped or fitted:
                clean[g.name]={"redundant_points_removed":removed,"axis_snaps":snapped,"bounded_quadratic_fits":fitted}
        u.info.versionMinor=1
        u.info.openTypeNameVersion="Version 1.001"
        u.info.openTypeNameUniqueID=u.info.openTypeNameUniqueID.replace("1.000;","1.001;")
        u.save(path,overwrite=True)
        report["styles"][path.stem]={"carons":carons,"proportional":prop,"outline_cleanup":clean}
        print(path.stem,len(clean),"outlines cleaned",flush=True)
    dest=ROOT/"documentation/google-fonts/warning-cleanup-changes.json"
    dest.write_text(json.dumps(report,indent=2)+"\n")


if __name__=="__main__":main()
