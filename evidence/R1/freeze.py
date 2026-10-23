"""Freeze R1's original/export/actual two-job CI evidence without changing old stages."""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2];STAGE=ROOT/'evidence/R1';MANIFEST=STAGE/'manifest.json'
def read(p):return json.loads(p.read_bytes())
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
if '--create' in sys.argv:
 assert not MANIFEST.exists(),'already frozen'
 report=read(STAGE/'remote-verified.json')
 meta=dict(stage='R1',scope='authorized PRIVATE repository/history transport and actual macOS-arm64/Linux-x86_64 full verification',original_author_code_sha=report['original_author_code_sha'],export_tested_sha=report['export_tested_sha'],run_id=report['run_id'],run_url=report['run_url'],private=True,public_release=False,personal_explanation='NOT_PERFORMED',review_candidate='07906089e24ec06772e3b176107d5613911a7b93',second_independent_review=False,
           evidence_sha256={str(p.relative_to(ROOT)):sha(p) for p in sorted(STAGE.rglob('*')) if p.is_file() and p!=MANIFEST and '__pycache__' not in p.parts})
 MANIFEST.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
else:meta=read(MANIFEST)
for name,digest in meta['evidence_sha256'].items():assert sha(ROOT/name)==digest,name
r=read(STAGE/'remote-verified.json');assert r['passed'] is True and r['export_tested_sha']==meta['export_tested_sha'] and r['original_author_code_sha']==meta['original_author_code_sha']
assert r['run_id']==meta['run_id'] and r['run_url']==meta['run_url']
repo=read(STAGE/'repository-final.json');assert repo['private'] is True and repo['full_name']=='z2823253773-p/mooneventeval'
mapping=read(STAGE/'export-map.json');assert mapping['mapping'][meta['original_author_code_sha']]==meta['export_tested_sha'] and mapping['commits']==len(mapping['mapping'])==40
assert mapping['author_dates_messages_preserved'] is True
review=STAGE/'independent-review';resolution=read(STAGE/'review-resolution.json')
assert sha(review/'SHA256SUMS.json')==resolution['manifest_sha256']
for name,row in read(review/'SHA256SUMS.json')['files'].items():assert sha(review/name)==row['sha256'] and (review/name).stat().st_size==row['bytes']
assert resolution['important']==1 and resolution['critical']==resolution['minor']==0 and not resolution['second_review']
# Frozen original reviewer files were added verbatim, never relabeled as new runs.
original_review=read(ROOT/'evidence/T7/independent-review/SHA256SUMS.json')['files']
for name,row in read(STAGE/'missing-tracked-proof.json')['files'].items():
 data=subprocess.check_output(['git','show',meta['original_author_code_sha']+':'+name],cwd=ROOT)
 assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']==original_review[name.split('independent-review/',1)[1]]['sha256']
local=read(STAGE/'export-final-local/report.json');assert local['passed'] is True and local['git_head']==meta['export_tested_sha'] and len(local['steps'])==17
for name,digest in read(STAGE/'export-final-local/SHA256SUMS.json').items():assert sha(STAGE/'export-final-local'/name)==digest
for p in STAGE.glob('20*.json'):
 command=read(p);assert sha(ROOT/command['log'])==command['log_sha256']
# Read-only full artifact/source revalidation; no network or frozen file writes.
subprocess.run([sys.executable,str(STAGE/'verify_remote.py'),'--check-only'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
print(json.dumps(dict(passed=True,files=len(meta['evidence_sha256']),export_tested_sha=meta['export_tested_sha'],remote_jobs=2,steps_per_job=17,qualification_calls_per_job=1620,private=True,published=False)))
