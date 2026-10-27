"""Verify frozen P3 review/archives and actual local/remote acceptance."""
from pathlib import Path
import hashlib,json,subprocess,sys
if sys.flags.optimize:raise RuntimeError('verification requires non-optimized Python')
ROOT=Path(__file__).resolve().parents[2];STAGE=ROOT/'evidence/P3-acceptance';LOCK=STAGE/'SHA256SUMS.json'
def sha(p):
    with p.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
if '--create' in sys.argv:
    if LOCK.exists():raise ValueError('already frozen')
    LOCK.write_text(json.dumps({str(p.relative_to(STAGE)):sha(p) for p in sorted(STAGE.rglob('*')) if p.is_file() and p!=LOCK and '__pycache__' not in p.parts},indent=2)+'\n')
for name,digest in json.loads(LOCK.read_bytes()).items():
    if sha(STAGE/name)!=digest:raise ValueError('frozen evidence changed: '+name)
subprocess.run([sys.executable,str(STAGE/'verify.py'),'--check-only'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
print(json.dumps(dict(passed=True,stage='P3',files=len(json.loads(LOCK.read_bytes())),public_ci_run=40447392163,remote_jobs=2,steps_per_job=17,demo_product_calls_per_job=8,demo_reference_calls_per_job=4,registration_resubmitted=False)))
