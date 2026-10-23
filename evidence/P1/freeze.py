"""Freeze the delegated local delivery; no remote or personal acceptance claim."""
from pathlib import Path
import hashlib,json,subprocess,sys,zipfile
ROOT=Path(__file__).resolve().parents[2];STAGE=ROOT/'evidence/P1';MANIFEST=STAGE/'manifest.json'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_bytes())
if '--create' in sys.argv:
 assert not MANIFEST.exists(),'already frozen'
 meta=dict(stage='P1',scope='delegated local delivery and public-source readiness observations',base_sha='7dd8801edcbe9ee885efdfd9c896250c79d0dacb',full_gate_tested_sha='8aa37c5aa55821d40a527e42ee9bc47ffc32371f',package_checkout_sha=read(STAGE/'package-source.json')['package_checkout_sha'],remote_ci='NOT_RUN',published=False,personal_explanation='NOT_PERFORMED',user_manual_retest='WAIVED_BY_USER_2026-10-22',visual_render_verified=False,evidence_sha256={str(p.relative_to(ROOT)):sha(p) for p in sorted(STAGE.rglob('*')) if p.is_file() and p!=MANIFEST})
 MANIFEST.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
else:meta=read(MANIFEST)
for name,digest in meta['evidence_sha256'].items():assert sha(ROOT/name)==digest,name
r=read(STAGE/'delivery-report.json');v=read(STAGE/'delivery-verified.json');binding=read(STAGE/'package-source.json')
assert r['passed'] is True and v['passed'] is True and r['published'] is False and r['remote_ci']=='NOT_RUN'
assert r['user_manual_retest']==meta['user_manual_retest'] and r['personal_explanation']=='NOT_PERFORMED'
assert r['native_binary_contains_build_paths'] is True and r['public_redaction_complete'] is False
assert r['browser_render_verified'] is False and v['visual_render_verified'] is False
assert r['delivery_members']==v['delivery_members']==19
assert r['copied_binary_calls']==5 and r['actual_exit_codes']==[0,0,0,0,2]
assert r['source_package_checkout_sha']==meta['package_checkout_sha']==binding['package_checkout_sha']
for name,digest in binding['member_sha256'].items():
 data=subprocess.check_output(['git','show',meta['package_checkout_sha']+':'+name],cwd=ROOT)
 assert hashlib.sha256(data).hexdigest()==digest,name
bundle=STAGE/'delivery/MoonEventEval-0.1.0-local';archive=STAGE/'MoonEventEval-0.1.0-local.zip'
assert sha(archive)==r['delivery_zip_sha256']
files=read(bundle/'SHA256SUMS.json');assert len(files)==18
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None and len(z.namelist())==19
 for name,digest in files.items():assert hashlib.sha256(z.read('MoonEventEval-0.1.0-local/'+name)).hexdigest()==digest==sha(bundle/name),name
assert sha(bundle/'bin/mooneventeval')==r['product_sha256']
assert sha(bundle/'source/local-mooneventeval-0.1.0.zip')==r['source_archive_sha256']==binding['archive_sha256']
with zipfile.ZipFile(bundle/'source/local-mooneventeval-0.1.0.zip') as z:
 assert z.testzip() is None and len(z.namelist())==38
 for name,digest in binding['member_sha256'].items():assert hashlib.sha256(z.read(name)).hexdigest()==digest
for name,want in [('duplicate',(1,1,0)),('greedy-trap',(2,0,0)),('boundary',(1,0,0))]:
 folder=STAGE/'zip-extracted-check'/name;receipt=read(folder/'receipt.json');actual=read(folder/'stdout')
 assert receipt['exit_code']==0 and sha(folder/'stdout')==receipt['stdout_sha256'] and (folder/'stderr').read_bytes()==b''
 assert tuple(actual['summary']['counts'][k] for k in ['tp','fp','fn'])==want
for case in ['duplicate','greedy-trap','boundary','boundary-explain','missing-file']:
 folder=STAGE/'copied-binary'/case;receipt=read(folder/'receipt.json')
 assert receipt['exit_code']==(2 if case=='missing-file' else 0)
 for stream in ['stdout','stderr']:assert sha(folder/stream)==receipt[stream+'_sha256']
demo=read(STAGE/'demo/report.json');assert demo['passed'] is True and len(demo['commands'])==10
for row in demo['commands']:
 assert row['exit_code']==0
 for stream in ['stdout','stderr']:assert sha(STAGE/'demo'/row['name']/stream)==row[stream+'_sha256']
assert read(STAGE/'package-current/report.json')['passed'] is True
for p in STAGE.glob('20*.json'):
 row=read(p);assert sha(ROOT/row['log'])==row['log_sha256']
print(json.dumps(dict(passed=True,files=len(meta['evidence_sha256']),delivery_members=19,source_members=38,full_gate_tested_sha=meta['full_gate_tested_sha'],package_checkout_sha=meta['package_checkout_sha'],user_manual_retest=meta['user_manual_retest'],remote_ci='NOT_RUN',published=False,visual_render_verified=False)))
