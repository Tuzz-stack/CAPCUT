"""Fetch an exact public engine release without running npm lifecycle scripts."""
from pathlib import Path
import hashlib
import json
import shutil
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parent
TARGET = ROOT / '.cache'
EXPECTED = 'de0724a36eaf3166e7f1ff38d0f4478b95ccc47725e9597b3fe66d3d3e18baa2'
URL = 'https://registry.npmjs.org/opencode-linux-x64/-/opencode-linux-x64-1.18.23.tgz'

def main():
    TARGET.mkdir(exist_ok=True)
    binary = TARGET / 'opencode'
    if not binary.exists():
        archive = TARGET / 'opencode.tgz'
        with urllib.request.urlopen(URL, timeout=60) as response, archive.open('wb') as output:
            shutil.copyfileobj(response, output)
        assert hashlib.sha1(archive.read_bytes()).hexdigest() == 'd734d600eff64472aac6fdbbd097c093e9903d70'
        with tarfile.open(archive) as package:
            member = package.getmember('package/bin/opencode')
            assert member.isfile() and member.size == 184584320
            with package.extractfile(member) as source, binary.open('wb') as output:
                shutil.copyfileobj(source, output)
        archive.unlink()
    assert hashlib.sha256(binary.read_bytes()).hexdigest() == EXPECTED
    binary.chmod(0o755)
    print(json.dumps({'url':URL,'sha256':EXPECTED,'bytes':binary.stat().st_size}))

if __name__ == '__main__':
    main()
