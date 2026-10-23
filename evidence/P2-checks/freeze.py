"""Freeze the public visibility, anonymous Git and actual two-platform evidence."""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2];STAGE=ROOT/'evidence/P2-checks';MANIFEST=STAGE/'manifest.json'
def read(p):return json.loads(p.read_bytes())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
if '--create' in sys.argv:
    assert not MANIFEST.exists()
    meta=dict(scope='P2 public repository and actual full CI; not registration or independent human authorship',
        export_tested_sha='f406084d7f702fd569401b76ae86b65817f7aafa',
        evidence_sha256={str(p.relative_to(ROOT)):sha(p) for p in sorted(STAGE.rglob('*')) if p.is_file() and p!=MANIFEST and '__pycache__' not in p.parts})
    MANIFEST.write_text(json.dumps(meta,indent=2)+'\n')
else:meta=read(MANIFEST)
for name,digest in meta['evidence_sha256'].items():assert sha(ROOT/name)==digest,name
repo=read(STAGE/'repository-public.json');assert repo['private'] is False and repo['visibility']=='public'
assert (STAGE/'anonymous-ls-remote.log').read_text().strip()==meta['export_tested_sha']+'\trefs/heads/main'
local=read(STAGE/'local/report.json');assert local['passed'] is True and len(local['steps'])==17
for name,digest in read(STAGE/'local/SHA256SUMS.json').items():assert sha(STAGE/'local'/name)==digest,name
for row in local['steps']:assert row['exit_code']==0 and not row['timed_out'] and row['passed']
for record in STAGE.glob('20*.json'):
    receipt=read(record);assert receipt['exit_code']==0 and sha(ROOT/receipt['log'])==receipt['log_sha256']
assert read(STAGE/'public-final-audit.json')['findings']==[]
subprocess.run([sys.executable,str(STAGE/'verify_public_ci.py'),'--check-only'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
print(json.dumps(dict(passed=True,public=True,files=len(meta['evidence_sha256']),anonymous_git=True,remote_jobs=2,steps_per_job=17,registry_published=False,registration_submitted=False)))
