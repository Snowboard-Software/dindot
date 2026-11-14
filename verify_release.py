"""Verify the checked-in candidate binaries, stylesheet and license checksums."""
from pathlib import Path
from hashlib import sha256
from argparse import ArgumentParser

ROOT=Path(__file__).resolve().parent

if __name__=="__main__":
    parser=ArgumentParser(description=__doc__)
    parser.add_argument("--compare",type=Path,help="Compare the 16 checked-in fonts with a fresh build directory")
    args=parser.parse_args()
    lines=(ROOT/"SHA256SUMS").read_text().splitlines()
    for line in lines:
        expected,name=line.split(None,1)
        assert sha256((ROOT/name.strip()).read_bytes()).hexdigest()==expected,name
    assert len(lines)==20,"Expected 16 fonts plus two stylesheets and two notices"
    print("Verified all 20 candidate files, including all 16 fonts.")
    if args.compare:
        fonts=list((ROOT/"fonts/ttf").glob("*.ttf"))+list((ROOT/"fonts/webfonts").glob("*.woff2"))
        assert len(fonts)==16
        for path in fonts:
            relative=path.relative_to(ROOT/"fonts")
            assert path.read_bytes()==(args.compare/relative).read_bytes(),f"Fresh build differs: {relative}"
        print("All 16 checked-in fonts match the fresh build byte for byte.")
