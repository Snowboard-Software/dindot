"""Fetch and verify the immutable release used by migration regression checks."""
from hashlib import sha256
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile
from io import BytesIO

ROOT=Path(__file__).resolve().parents[1]
URL="https://github.com/Snowboard-Software/dindot/releases/download/v0.22.0/DINDOT-v0.22.0.zip"
SHA256="4a66ecca90a941f5961cb813671e153a4fb71c6d826119a15628345caded62c9"

if __name__=="__main__":
    with urlopen(URL,timeout=60) as response:
        data=response.read()
    assert sha256(data).hexdigest()==SHA256,"Reference release checksum mismatch"
    destination=ROOT/".cache/reference"
    destination.mkdir(parents=True,exist_ok=True)
    with ZipFile(BytesIO(data)) as archive:
        archive.extractall(destination)
    print(destination/"DINDOT-v0.22.0")
