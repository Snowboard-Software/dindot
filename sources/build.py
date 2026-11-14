"""Build all static DINDOT faces from the maintained UFO sources."""
from argparse import ArgumentParser
from pathlib import Path
import os
import subprocess
import sys
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
EPOCH = 1793966400  # 2026-11-06 12:00:00 UTC; deterministic build timestamp
OT_EPOCH = EPOCH + 2082844800


def build(output):
    ttf_dir = output / "ttf"
    web_dir = output / "webfonts"
    ttf_dir.mkdir(parents=True, exist_ok=True)
    web_dir.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, SOURCE_DATE_EPOCH=str(EPOCH), PYTHONHASHSEED="0")
    sources=sorted((ROOT / "sources").glob("*.ufo"))
    if len(sources)!=8:
        raise SystemExit(f"Expected eight UFO sources, found {len(sources)}")
    for source in sources:
        target = ttf_dir / f"{source.stem}.ttf"
        subprocess.run([
            sys.executable, "-m", "fontmake", "-u", str(source), "-o", "ttf",
            "--output-path", str(target), "--keep-overlaps", "--no-production-names",
            "--feature-writer", "None", "--no-auto-use-my-metrics",
        ], check=True, env=env)
        hinted = target.with_suffix(".hinted.ttf")
        subprocess.run([
            sys.executable, "-m", "ttfautohint", "--hinting-range-min=8",
            "--hinting-range-max=32", "--hinting-limit=32", "--no-info",
            "--default-script=latn", str(target), str(hinted),
        ], check=True, env=env)
        hinted.replace(target)
        f = TTFont(target, recalcTimestamp=False)
        f["head"].created = f["head"].modified = OT_EPOCH
        # RIBBI menu grouping is fully expressed by legacy nameIDs 1 and 2.
        if source.stem in {"DINDOT-Regular", "DINDOT-Italic", "DINDOT-Bold", "DINDOT-BoldItalic"}:
            f["name"].removeNames(nameID=16)
            f["name"].removeNames(nameID=17)
        f.save(target)
        f.flavor = "woff2"
        f.save(web_dir / f"{source.stem}.woff2")
        print(f"Built {source.stem}", flush=True)


if __name__ == "__main__":
    p = ArgumentParser(description=__doc__)
    p.add_argument("--output-dir", type=Path, default=ROOT / "fonts")
    build(p.parse_args().output_dir.resolve())
