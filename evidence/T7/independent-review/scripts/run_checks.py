#!/usr/bin/env python3
"""Independent T7 command receipts; execute only in the temporary candidate."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
import sys
import time

AUDIT = Path(__file__).resolve().parents[1]
CONTEXT = json.loads((AUDIT / 'context.json').read_text())
SOURCE = Path(CONTEXT['source'])

def record(label, command, cwd=SOURCE, timeout=180):
    folder = AUDIT / 'evidence' / label
    folder.mkdir(parents=True)
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    start = time.monotonic()
    timed_out = False
    try:
        result = subprocess.run([str(x) for x in command], cwd=cwd,
                                capture_output=True, timeout=timeout)
        stdout, stderr, code = result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired as error:
        stdout, stderr, code = error.stdout or b'', error.stderr or b'', None
        timed_out = True
    (folder / 'stdout').write_bytes(stdout)
    (folder / 'stderr').write_bytes(stderr)
    receipt = dict(command=[str(x) for x in command], cwd=str(cwd),
                   started_utc=started, elapsed_seconds=time.monotonic()-start,
                   exit_code=code, timed_out=timed_out,
                   stdout_sha256=hashlib.sha256(stdout).hexdigest(),
                   stderr_sha256=hashlib.sha256(stderr).hexdigest())
    (folder / 'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(dict(label=label, exit_code=code, timed_out=timed_out,
                          elapsed_seconds=round(receipt['elapsed_seconds'], 3))), flush=True)
    return receipt

def nominal():
    wrapper = SOURCE / 'scripts/with-toolchain.sh'
    rows = []
    rows.append(record('moon-tests', [wrapper,'moon','test','--target','native','--deny-warn']))
    rows.append(record('python-tests', ['python3','-W','error::ResourceWarning','-m','unittest','discover','-s','tests','-v']))
    rows.append(record('source-consumer', ['python3','scripts/check_consumer.py','--source','.', '--output',AUDIT/'results/source-consumer']))
    rows.append(record('package', ['python3','scripts/package_candidate.py','--output',AUDIT/'results/package']))
    rows.append(record('fmt-check', [wrapper,'moon','fmt','--check']))
    rows.append(record('moon-info', [wrapper,'moon','info']))
    (AUDIT/'nominal.json').write_text(json.dumps(rows, indent=2)+'\n')
    return all(row['exit_code']==0 for row in rows)

if __name__ == '__main__':
    raise SystemExit(0 if nominal() else 1)
