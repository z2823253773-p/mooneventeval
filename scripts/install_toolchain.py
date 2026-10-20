"""Install only the locked MoonBit release inside this checkout (Python >=3.12)."""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]

def verify_digest(path, expected):
    with path.open('rb') as stream:
        actual = hashlib.file_digest(stream, 'sha256').hexdigest()
    if actual != expected:
        raise ValueError(f'SHA-256 mismatch for {path.name}: {actual} != {expected}')
    return actual

def extract_checked(archive, destination):
    destination.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, 'r:gz') as tar:
        # Validate the complete archive before extracting any member. The data
        # filter additionally rejects special files and escaping link targets.
        members = tar.getmembers()
        for member in members:
            if PurePosixPath(member.name).is_absolute() or '..' in PurePosixPath(member.name).parts:
                raise ValueError(f'unsafe archive member: {member.name}')
            tarfile.data_filter(member, str(destination))
        tar.extractall(destination, members=members, filter='data')

def fetch(url, path):
    # Existing downloads are re-hashed below, never trusted by filename.
    if not path.exists():
        subprocess.run(['curl', '--fail', '--location', '--silent', '--show-error',
                        '--connect-timeout', '20', '--max-time', '180',
                        '--output', str(path)+'.part', url], check=True, timeout=190)
        Path(str(path)+'.part').replace(path)

def main():
    lock = json.loads((ROOT/'docs/toolchain.lock.json').read_text())
    target = {('Darwin', 'arm64'): 'darwin-aarch64',
              ('Linux', 'x86_64'): 'linux-x86_64'}.get((platform.system(), platform.machine()))
    if target is None:
        raise SystemExit('unsupported platform; no latest fallback')
    cache = ROOT/'.tools/downloads'
    cache.mkdir(parents=True, exist_ok=True)
    binary = cache/'moonbit.tar.gz'
    core = cache/'core.tar.gz'
    sidecar = cache/'moonbit.tar.gz.sha256'
    uri = f"{lock['base_url']}/binaries/{lock['encoded_version']}/moonbit-{target}.tar.gz"
    fetch(uri, binary)
    fetch(uri+'.sha256', sidecar)
    published = sidecar.read_text().split()[0]
    expected = lock['binaries'][target]
    if not re.fullmatch('[0-9a-f]{64}', published) or published != expected:
        raise ValueError('publisher sidecar differs from pinned binary digest')
    verify_digest(binary, expected)
    fetch(f"{lock['base_url']}/cores/core-{lock['encoded_version']}.tar.gz", core)
    verify_digest(core, lock['core_recorded_sha256'])
    destination = ROOT/'.tools/moonbit'/lock['version']
    if destination.exists():
        raise SystemExit(f'refusing to overwrite existing toolchain: {destination}')
    extract_checked(binary, destination)
    extract_checked(core, destination/'lib')
    for path in (destination/'bin').iterdir():
        if path.is_file() and not path.is_symlink() and path.suffix != '.wasm':
            path.chmod(path.stat().st_mode | 0o111)
    env = dict(os.environ, MOON_HOME=str(destination), PATH=str(destination/'bin')+os.pathsep+os.environ['PATH'])
    result = subprocess.run([str(destination/'bin/moonc'), '-v'], env=env, check=True, capture_output=True, text=True)
    version = result.stdout.strip()
    if not version.startswith(lock['moonc_prefix']):
        raise ValueError(f'compiler identity mismatch: {version}')
    print(json.dumps({'target': target, 'moonc': version, 'binary_sha256': expected,
                      'binary_provenance': 'pinned digest matches publisher sidecar and archive',
                      'core_sha256': lock['core_recorded_sha256'], 'core_provenance': lock['core_provenance']}))
    subprocess.run([str(destination/'bin/moon'), '-C', str(destination/'lib/core'),
                    'bundle', '--warn-list', '-a', '--all'], env=env, check=True, timeout=600)

if __name__ == '__main__':
    main()
