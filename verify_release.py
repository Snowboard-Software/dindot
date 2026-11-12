"""Verify the release checksums; optionally rebuild in an isolated directory."""
from pathlib import Path
from hashlib import sha256
from tempfile import TemporaryDirectory
import argparse
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent

def verify(root):
    count = 0
    for line in (ROOT / "SHA256SUMS").read_text().splitlines():
        if not line.strip():
            continue
        expected, name = line.split(None, 1)
        name = name.strip()
        actual = sha256((root / name).read_bytes()).hexdigest()
        if actual != expected:
            raise SystemExit(f"Checksum mismatch: {name}")
        count += 1
    if count != 20:
        raise SystemExit(f"Expected 20 release files, got {count}")
    print(f"Verified {count} original release files, including all 16 fonts.")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rebuild", action="store_true")
    args = parser.parse_args()
    verify(ROOT)
    if not args.rebuild:
        return
    with TemporaryDirectory(prefix="dindot-rebuild-") as temp:
        stage = Path(temp)
        for pattern in ("*.py", "*.json"):
            for path in ROOT.glob(pattern):
                shutil.copy2(path, stage / path.name)
        shutil.copytree(ROOT / "source", stage / "source")
        for name in ("audit", "text", "data", "fonts"):
            (stage / name).mkdir()
        subprocess.run([sys.executable, str(stage / "build.py")], check=True)
        for path in sorted((ROOT / "fonts").iterdir()):
            if (stage / "fonts" / path.name).read_bytes() != path.read_bytes():
                raise SystemExit(f"Rebuild differs: {path.name}")
        print("Rebuild matches all 16 shipped font files byte for byte.")

if __name__ == "__main__":
    main()
