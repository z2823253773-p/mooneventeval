"""Bind actual GitHub run/jobs to downloaded, hash-checked full verifier outputs."""
from pathlib import Path
import hashlib,json,subprocess,sys,zipfile,tempfile
ROOT=Path(__file__).resolve().parents[2];STAGE=ROOT/'evidence/P3-acceptance';REMOTE=STAGE
CODE='a613579b615e4ac7fd74ddcd704d4333707bcc4b';EXPORTED=CODE
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if sys.flags.optimize:
 raise RuntimeError('artifact verification requires non-optimized Python')
HOLDER=tempfile.TemporaryDirectory(prefix='mooneventeval-p3-proof-');PROOF=Path(HOLDER.name)
ARCHIVES=read(STAGE/'archives.json')
for name,row in ARCHIVES.items():
 archive=STAGE/name
 assert sha(archive)==row['sha256'] and archive.stat().st_size==row['bytes'],name
 with zipfile.ZipFile(archive) as z:
  infos=z.infolist();assert len(infos)==row['files'] and len({i.filename for i in infos})==len(infos)
  assert sum(i.file_size for i in infos)<2*1024**3
  for i in infos:
   path=Path(i.filename)
   assert not path.is_absolute() and '..' not in path.parts and '\\' not in i.filename
   assert ((i.external_attr>>16)&0o170000)!=0o120000
  assert z.testzip() is None
  if name in ['remote-artifacts.zip','local-final.zip']:
   z.extractall(PROOF/archive.stem)
run=read(REMOTE/'run.json');jobs=read(REMOTE/'jobs.json')['jobs']
assert run['head_sha']==EXPORTED and run['conclusion']=='success' and run['status']=='completed'
assert len(jobs)==2 and all(j['conclusion']=='success' and j['status']=='completed' for j in jobs)
assert {j['name'] for j in jobs}=={'verify (macos-14, arm64)','verify (ubuntu-24.04, x86_64)'}
for j in jobs:
 steps={s['name']:s['conclusion'] for s in j['steps']}
 for name in ['Restore exact original history and oversized historical proof','Assert actual runner architecture','Install and hash-verify pinned MoonBit binary/core','Create locked original reference environment','Same complete verifier as local','Keep actual receipts on success or failure','Replay published reports and scoped sed_eval comparisons']:assert steps[name]=='success',(j['name'],name)
assert read(STAGE/'repository.json')['private'] is False
rows=[];inventory=None
for folder,system,machine in [('verification-macos-14-arm64','Darwin','arm64'),('verification-ubuntu-24.04-x86_64','Linux','x86_64')]:
 root=PROOF/'remote-artifacts'/folder;r=read(root/'report.json');index=read(root/'SHA256SUMS.json')
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
 demo=root/'public-demo';d=read(demo/'report.json')
 assert d['passed'] is True and d['mode']=='check' and d['reference_checked'] is True
 assert (d['product_calls'],d['reference_calls'],len(d['receipts']))==(8,4,12)
 assert d['product_sha256']==r['product_sha256']
 expected={'public-demo/report.json'};seen=set()
 for receipt in d['receipts']:
  snapshot=receipt['snapshot'];assert snapshot not in seen;seen.add(snapshot)
  assert snapshot.startswith('demo/output/') or snapshot.startswith('demo/reference/')
  prefix='product-' if snapshot.startswith('demo/output/') else 'reference-'
  leaf=prefix+Path(snapshot).name
  assert receipt['exit_code']==0
  for stream in ['stdout','stderr']:
   relative='public-demo/'+leaf+'.'+stream;expected.add(relative)
   assert sha(root/relative)==receipt[stream+'_sha256']
  assert sha(demo/(leaf+'.stdout'))==r['source_sha256'][snapshot]
  if prefix=='product-':assert (demo/(leaf+'.stderr')).read_bytes()==b''
 assert len([x for x in seen if x.startswith('demo/output/')])==8
 assert len([x for x in seen if x.startswith('demo/reference/')])==4
 actual={str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}
 assert actual==set(index)|{'SHA256SUMS.json'}|expected,'unindexed artifact files'
 rows.append(dict(artifact=folder,system=system,machine=machine,steps=17,moon=58,python=28,validation=42,cli=15,qualification_calls=count,source_files=len(r['source_sha256']),files_rehashed=len(index),product_sha256=r['product_sha256'],archive_sha256=r['archive_sha256'],reference_executable_sha256=r['reference_identity']['executable_sha256'],installed_tool_files=r['toolchain']['installed_regular_files_compared'],demo_product_calls=8,demo_reference_calls=4,demo_files_checked=len(expected)))
# Bind every downloaded non-evidence source file directly to the public Git graph.
# This commit is reachable in an independent public clone.
for name,digest in inventory.items():
 assert not name.startswith('evidence/')
 data=subprocess.check_output(['git','show',CODE+':'+name],cwd=ROOT);assert hashlib.sha256(data).hexdigest()==digest,name
local_root=PROOF/'local-final';local=read(local_root/'local/report.json')
assert local['passed'] is True and len(local['steps'])==17 and local['git_head']=='074509f2da1a4b275d7c752399a7e5989f7e717a'
assert local['source_sha256']==inventory,'local/public source inventory mismatch'
for name,digest in read(local_root/'local/SHA256SUMS.json').items():assert sha(local_root/'local'/name)==digest
for step in local['steps']:assert step['passed'] is True and step['exit_code']==0 and not step['timed_out']
assert read(local_root/'public-demo/report.json')['passed'] is True
result=dict(passed=True,scope='P3 actual two-job CI, complete local gate, scoped 8+4 published-report replay and integrity-checked archives',archives={name:row['sha256'] for name,row in ARCHIVES.items()},run_id=run['id'],run_url=run['html_url'],event=run['event'],export_tested_sha=EXPORTED,git_source_sha=CODE,source_inventories_equal=True,jobs=rows,registry_published=False,repository_visibility='public (separate API receipt)',personal_explanation='NOT_PERFORMED')
if '--check-only' in sys.argv:assert read(STAGE/'verified.json')==result
else:(STAGE/'verified.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result))
