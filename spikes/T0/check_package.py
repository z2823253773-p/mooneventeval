"""Inspect and preserve the real local archive; no registry operation."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import zipfile

if __name__ == '__main__':
    archive = Path(__file__).resolve().parent/'modern/_build/publish/local-t0_modern-0.0.1.zip'
    with zipfile.ZipFile(archive) as package:
        assert package.testzip() is None
        names = package.namelist()
        assert {'moon.mod', 'moon.pkg', 'probe_wbtest.mbt'} == set(names), names
    output = Path(sys.argv[1])
    saved = output/archive.name
    shutil.copyfile(archive, saved)
    print(json.dumps({'source': str(archive), 'saved': str(saved), 'members': names,
                      'sha256': hashlib.sha256(saved.read_bytes()).hexdigest(), 'bytes': saved.stat().st_size}))
