"""Rebuild the qualified development reference locally from hash locks.

Requires uv 0.11.14 on macOS arm64. Never overwrites a venv or installs globally.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]

def destination_for(root, name):
    if not re.fullmatch(r'\.venv-reference(?:-[A-Za-z0-9-]+)?', name):
        raise ValueError('destination must be a project-local .venv-reference[-name]')
    destination = Path(root)/name
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(f'refusing to overwrite {destination}')
    return destination

def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--venv',default='.venv-reference')
    args = parser.parse_args()
    target = destination_for(ROOT,args.venv)
    lock = json.loads((ROOT/'validation/python-reference.lock.json').read_text())
    if platform.system() != 'Darwin' or platform.machine() != 'arm64':
        raise SystemExit('reference environment currently qualified only on macOS arm64')
    env = dict(os.environ, UV_CACHE_DIR=str(ROOT/'.tools/uv-cache'),
               UV_PYTHON_INSTALL_DIR=str(ROOT/'.tools/python'),
               UV_PYTHON_BIN_DIR=str(ROOT/'.tools/python-bin'),
               UV_HTTP_TIMEOUT='60',UV_HTTP_RETRIES='1',
               MPLCONFIGDIR=str(ROOT/'.tools/reference-cache/matplotlib'),
               NUMBA_CACHE_DIR=str(ROOT/'.tools/reference-cache/numba'))
    def run(command, timeout=600):
        print(json.dumps({'command':list(map(str,command))}),flush=True)
        return subprocess.run(command,cwd=ROOT,env=env,check=True,timeout=timeout)
    version = subprocess.check_output(['uv','--version'],env=env,text=True).split()[1]
    if version != lock['uv_version']:
        raise RuntimeError('uv version differs from qualified reference installer')
    run(['uv','python','install',lock['python_version']],timeout=300)
    interpreter = ROOT/'.tools/python'/lock['python_directory']/'bin/python3.11'
    actual = subprocess.check_output([str(interpreter),'-c','import platform;print(platform.python_version())'],text=True).strip()
    if actual != lock['python_version'] or digest(interpreter) != lock['executable_sha256']:
        raise RuntimeError('Python source/build identity differs from reference lock')
    run(['uv','venv','--python',str(interpreter),str(target)])
    python = str(target/'bin/python')
    # Installing the locked backend first avoids unpinned isolated build deps.
    run(['uv','pip','install','--python',python,'--require-hashes','--only-binary',':all:',
         '-r','validation/reference-build.lock'])
    run(['uv','pip','sync','--python',python,'--require-hashes','--no-build-isolation',
         'validation/reference.lock'])
    run(['uv','pip','check','--python',python])
    run([python,'-m','unittest','discover','-s','validation/tests','-p','test_reference.py','-v'])

if __name__ == '__main__':
    main()
