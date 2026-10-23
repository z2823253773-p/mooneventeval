"""Bind actual GitHub run/jobs to downloaded, hash-checked full verifier outputs."""
from pathlib import Path
import hashlib,json,subprocess,sys,zipfile
ROOT=Path(__file__).resolve().parents[2];STAGE=ROOT/'evidence/R1';REMOTE=STAGE/'remote-39914869650'
CODE='69f544fdcfd6bdd13bff273279da7dd5fdfc56d6';EXPORTED='c1e74f58b495e8bf83986715f57d6d8f3bff76bd'
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
run=read(REMOTE/'final-run.json');jobs=read(REMOTE/'final-jobs.json')['jobs']
assert run['head_sha']==EXPORTED and run['conclusion']=='success' and run['status']=='completed'
assert len(jobs)==2 and all(j['conclusion']=='success' and j['status']=='completed' for j in jobs)
assert {j['name'] for j in jobs}=={'verify (macos-14, arm64)','verify (ubuntu-24.04, x86_64)'}
for j in jobs:
 steps={s['name']:s['conclusion'] for s in j['steps']}
 for name in ['Restore exact original history and oversized historical proof','Assert actual runner architecture','Install and hash-verify pinned MoonBit binary/core','Create locked original reference environment','Same complete verifier as local','Keep actual receipts on success or failure']:assert steps[name]=='success',(j['name'],name)
rows=[];inventory=None
for folder,system,machine in [('verification-macos-14-arm64','Darwin','arm64'),('verification-ubuntu-24.04-x86_64','Linux','x86_64')]:
 root=REMOTE/'artifacts'/folder;r=read(root/'report.json');index=read(root/'SHA256SUMS.json')
 assert r['passed'] is True and r['git_head']==EXPORTED and r['source_unchanged'] is True
 assert r['remote_ci']=='CURRENT_JOB_ONLY' and r['published'] is False and r['personal_M2']=='NOT_PERFORMED'
 assert r['host']['system']==system and r['host']['machine']==machine
 assert len(r['required_steps'])==len(set(r['required_steps']))==len(r['steps'])==17
 assert [s['name'] for s in r['steps']]==r['required_steps']
 for s in r['steps']:
  assert s['passed'] is True and s['exit_code']==0 and not s['timed_out']
  for stream in ['stdout','stderr']:assert sha(root/s['name']/stream)==s[stream+'_sha256']
 for name,digest in index.items():
  assert not Path(name).is_absolute() and '..' not in Path(name).parts
  assert sha(root/name)==digest,name
 assert (r['moon_tests'],r['python_tests'],r['validation_tests'],r['cli_tests'])==(58,28,42,15)
 assert r['reference_identity']['python_version']=='3.11.14' and len(r['reference_identity']['packages'])==44
 assert r['reference_identity']['sed_eval_source_verified'] is True and r['reference_identity']['sed_eval_bytecode_verified'] is True
 if inventory is None:inventory=r['source_sha256']
 else:assert inventory==r['source_sha256'],'OS source inventories differ'
 parity=read(root/'parity/report.json');assert parity['passed'] and len(parity['cases'])==324 and not parity['unexplained']
 assert parity['git_head']==EXPORTED and parity['product_sha256']==r['product_sha256']
 count=0
 for c in parity['cases']:
  assert not c['differences'] and len(c['transforms'])==4 and all(t['passed'] for t in c['transforms'])
  for name in ['base']+[t['operation'] for t in c['transforms']]:
   p=read(root/'parity'/c['name']/name/'process.json');assert p['exit_code']==0 and not p['differences'];count+=1
 assert count==1620
 for name in ['consumer-cases','package-cases','example-cases','package-cases/unpacked-consumer','package-cases/unpacked-examples']:
  a=read(root/name/'report.json');assert a['passed'] is True and not a.get('differences')
 package=read(root/'package-cases/report.json');archive=root/'package-cases'/package['archive'];assert sha(archive)==package['archive_sha256']==r['archive_sha256']
 with zipfile.ZipFile(archive) as z:
  assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))==38 and 'LICENSE' in z.namelist()
  for name in z.namelist():assert hashlib.sha256(z.read(name)).hexdigest()==package['member_sha256'][name]==r['source_sha256'][name]
 rows.append(dict(artifact=folder,system=system,machine=machine,steps=17,moon=58,python=28,validation=42,cli=15,qualification_calls=count,source_files=len(r['source_sha256']),files_rehashed=len(index),product_sha256=r['product_sha256'],archive_sha256=r['archive_sha256'],reference_executable_sha256=r['reference_identity']['executable_sha256'],installed_tool_files=r['toolchain']['installed_regular_files_compared']))
# Native GitHub export differs only in an evidence path; product and all other
# tracked source bytes are independently bound back to the original author SHA.
for name,digest in inventory.items():
 assert not name.startswith('evidence/')
 data=subprocess.check_output(['git','show',CODE+':'+name],cwd=ROOT);assert hashlib.sha256(data).hexdigest()==digest,name
result=dict(passed=True,scope='actual successful two-job GitHub CI plus downloaded artifact/source bindings',run_id=run['id'],run_url=run['html_url'],event=run['event'],export_tested_sha=EXPORTED,original_author_code_sha=CODE,source_inventories_equal=True,jobs=rows,published=False,repository_visibility='private (separate API receipt)',personal_explanation='NOT_PERFORMED')
if '--check-only' in sys.argv:assert read(STAGE/'remote-verified.json')==result
else:(STAGE/'remote-verified.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result))
