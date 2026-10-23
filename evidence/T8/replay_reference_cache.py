"""Author replay of the original cached-code fixture; not independent re-review."""
import hashlib,json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import verify
OUT=ROOT/'evidence/T8/author-cache-replay'
OUT.mkdir(exist_ok=False)
fixture=ROOT/'evidence/T8/independent-review/reference-pyc-probe/pythonpath'
env=dict(os.environ,PYTHONPATH=str(fixture),PYTHONDONTWRITEBYTECODE='1',MPLCONFIGDIR=str(ROOT/'.tools/reference-cache/matplotlib'),NUMBA_CACHE_DIR=str(ROOT/'.tools/reference-cache/numba'))
commands={'identity':verify.reference_probe_code(ROOT),'scoring':"import sys;sys.path.insert(0,sys.argv[1]+'/validation');from sed_reference import evaluate_document;print(evaluate_document(dict(schema_version=1,labels=['a'],recordings=[])))"}
rows=[]
for name,code in commands.items():
 folder=OUT/name;folder.mkdir()
 argv=[str(ROOT/'.venv-reference/bin/python'),'-c',code,str(ROOT)]
 p=subprocess.run(argv,cwd=ROOT,env=env,capture_output=True)
 for stream,data in [('stdout',p.stdout),('stderr',p.stderr)]: (folder/stream).write_bytes(data)
 row=dict(name=name,argv=argv,cwd=str(ROOT),exit_code=p.returncode,expected_rejection=p.returncode!=0 and b'reference bytecode mismatch' in p.stderr,stdout_sha256=hashlib.sha256(p.stdout).hexdigest(),stderr_sha256=hashlib.sha256(p.stderr).hexdigest())
 (folder/'receipt.json').write_text(json.dumps(row,indent=2)+'\n');rows.append(row)
assert all(r['expected_rejection'] for r in rows),rows
report=dict(passed=True,scope='author replay using original immutable reviewer cache fixture, no second independent review',git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),cases=rows)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':True,'entrypoints_rejected':2,'scope':report['scope']}))
