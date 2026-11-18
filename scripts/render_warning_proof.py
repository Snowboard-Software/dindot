"""Render contextual caron and operator comparisons for all eight styles."""
from argparse import ArgumentParser
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from render_proof import shaped_text

if __name__=="__main__":
    p=ArgumentParser(description=__doc__)
    p.add_argument("--reference",type=Path,required=True)
    p.add_argument("--fonts",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True);a=p.parse_args()
    image=Image.new("RGB",(2300,1980),"#f7f6f2");d=ImageDraw.Draw(image)
    label=ImageFont.load_default(size=28)
    d.text((25,20),"DINDOT warning cleanup: carons in words, consistent math operators",font=label,fill="black")
    for i,style in enumerate(["Regular","Medium","SemiBold","Bold","Italic","MediumItalic","SemiBoldItalic","BoldItalic"]):
        y=85+i*232;d.text((25,y),style,font=label,fill="black")
        for x,folder,title in [(300,a.reference/"fonts/ttf","Previous 1.000 candidate"),
                               (1300,a.fonts/"ttf","Revised 1.001 candidate")]:
            d.text((x,y),title,font=label,fill="#555555")
            font=folder/f"DINDOT-{style}.ttf"
            shaped_text(image,(x,y+45),"Ľudovít ďateľ ľalia ťava",font,62)
            shaped_text(image,(x,y+128),"Ľ ď ľ ť   = ∝ + − × ÷",font,66)
    a.output.parent.mkdir(parents=True,exist_ok=True);image.save(a.output)
