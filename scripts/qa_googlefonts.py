"""Stage the family in Google Fonts' directory layout and run Fontspector."""
from argparse import ArgumentParser
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]

if __name__=="__main__":
    p=ArgumentParser(description=__doc__)
    p.add_argument("--fontspector",required=True,type=Path)
    args=p.parse_args()
    staging=ROOT/".cache/googlefonts/dindot"
    staging.mkdir(parents=True,exist_ok=True)
    for path in (ROOT/"fonts/ttf").glob("*.ttf"):
        shutil.copy2(path,staging/path.name)
    shutil.copy2(ROOT/"OFL.txt",staging/"OFL.txt")
    dest=ROOT/"documentation/google-fonts"
    result=subprocess.run([str(args.fontspector.resolve()),"-p","googlefonts","-J","4",
        "--timeout","10","--json",str(dest/"fontspector-googlefonts.json"),
        "--ghmarkdown",str(dest/"fontspector-googlefonts.md"),
        *[str(p) for p in sorted(staging.glob("*.ttf"))]])
    raise SystemExit(result.returncode)
