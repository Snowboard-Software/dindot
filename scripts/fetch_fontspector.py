"""Install the pinned official Linux checker used by CI, verifying its digest."""
from pathlib import Path
from hashlib import sha256
from urllib.request import urlopen
from io import BytesIO
import tarfile
import shutil

ROOT=Path(__file__).resolve().parents[1]
URL="https://github.com/fonttools/fontspector/releases/download/fontspector-v1.9.1/fontspector-1.9.1-x86_64-unknown-linux-gnu.tar.gz"
SHA256="ff982bfbfb9edb60cb35512964fba2cc6560e94b492cf503f5dc9739c817a6b5"

if __name__=="__main__":
    with urlopen(URL,timeout=60) as response:data=response.read()
    assert sha256(data).hexdigest()==SHA256,"Fontspector release checksum mismatch"
    destination=ROOT/".cache/tools/fontspector-release"
    destination.mkdir(parents=True,exist_ok=True)
    with tarfile.open(fileobj=BytesIO(data),mode="r:gz") as archive:
        archive.extractall(destination,filter="data")
    binaries=[p for p in destination.rglob("fontspector") if p.is_file()]
    assert len(binaries)==1,"Expected one Fontspector binary"
    target=ROOT/".cache/tools/fontspector"
    shutil.copy2(binaries[0],target)
    target.chmod(0o755)
    print(target)
