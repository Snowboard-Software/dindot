"""Render the candidate and original release for human visual comparison."""
from argparse import ArgumentParser
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import freetype
import uharfbuzz as hb
from fontTools.unicodedata import script


def shaped_text(image,xy,text,path,size,language=None):
    """Use real shaping and rasterize the selected glyph IDs with FreeType."""
    face=freetype.Face(str(path));face.set_pixel_sizes(0,size)
    font=hb.Font(hb.Face(path.read_bytes()));font.scale=(size*64,size*64)
    x,y=xy;baseline=y+size
    runs=[];current="Latn"
    for char in text:
        s=script(char)
        if s in ("Zyyy","Zinh","Zzzz"):s=current
        if not runs or s!=current:runs.append([s,""])
        runs[-1][1]+=char;current=s
    for sc,run in runs:
        b=hb.Buffer();b.add_str(run);b.direction="ltr";b.script=sc
        if language:b.language=language
        hb.shape(font,b)
        for info,pos in zip(b.glyph_infos,b.glyph_positions):
            face.load_glyph(info.codepoint,freetype.FT_LOAD_RENDER)
            slot=face.glyph;bitmap=slot.bitmap
            if bitmap.width and bitmap.rows:
                mask=Image.frombytes("L",(bitmap.width,bitmap.rows),bytes(bitmap.buffer),"raw","L",abs(bitmap.pitch))
                image.paste((0,0,0),(round(x+pos.x_offset/64)+slot.bitmap_left,
                            round(baseline-pos.y_offset/64)-slot.bitmap_top),mask)
            x+=pos.x_advance/64

if __name__=="__main__":
    p=ArgumentParser(description=__doc__)
    p.add_argument("--reference",type=Path,required=True)
    p.add_argument("--fonts",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    image=Image.new("RGB",(1680,1450),"#f7f6f2")
    draw=ImageDraw.Draw(image)
    label=ImageFont.load_default(size=24)
    text="DINDOT 0123456789 €1,234.56 AVATAR fi fl Ελληνικά Кириллица"
    for i,style in enumerate(["Regular","BoldItalic"]):
        for j,(folder,title) in enumerate([(a.reference/"fonts","Published v0.22.0"),
                                          (a.fonts/"ttf","UFO candidate 1.000")]):
            y=i*240+j*105
            draw.text((30,y+8),title+" / "+style,font=label,fill="#444444")
            shaped_text(image,(30,y+39),text,folder/f"DINDOT-{style}.ttf",50)
    draw.text((30,500),"New Cyrillic coverage and mark attachments / candidate for design review",font=label,fill="#444444")
    samples=["Г г Ҕ ҕ К к Ҝ ҝ Н н Ҥ ҥ Ӏ ӏ Ӕ ӕ",
             "Ӑ ӑ Ӗ ӗ Ӝ ӝ Ӟ ӟ Ӥ ӥ Ӧ ӧ Ӱ ӱ Ӳ ӳ Ӵ ӵ",
             "◌̛  Ą́ Ę̃ Ė́ į̇́ Ū̃ є́ ї́ ё́ j̀ і́ ị́ l·l L·L"]
    for y,text in zip([550,660,770],samples):
        shaped_text(image,(30,y),text,a.fonts/"ttf/DINDOT-Regular.ttf",76,"ca")
    shaped_text(image,(30,900),"Ҕ ҕ Ҝ ҝ Ҥ ҥ Ӗ ӗ Ӵ ӵ ◌̛ Ą́ į̇́ і́ j̀",a.fonts/"ttf/DINDOT-BoldItalic.ttf",76)
    draw.text((30,1055),"All eight styles / candidate",font=label,fill="#444444")
    for i,style in enumerate(["Regular","Medium","SemiBold","Bold","Italic","MediumItalic","SemiBoldItalic","BoldItalic"]):
        x=30+(i//4)*820;y=1110+(i%4)*76
        shaped_text(image,(x,y),style+"  012345  €12.34",a.fonts/"ttf"/f"DINDOT-{style}.ttf",44)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    image.save(a.output)
