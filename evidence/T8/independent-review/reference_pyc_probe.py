from pathlib import Path
import hashlib,importlib._bootstrap_external,importlib.util,json,os,shutil,subprocess,sys
AUDIT=Path(__file__).resolve().parent;ROOT=AUDIT/'checkout';OUT=AUDIT/'reference-pyc-probe';OUT.mkdir();fixture=OUT/'pythonpath';fixture.mkdir()
python=ROOT/'.venv-reference/bin/python'
find=subprocess.run([str(python),'-c',"import importlib.util;print(next(iter(importlib.util.find_spec('sed_eval').submodule_search_locations)))"],capture_output=True,cwd=ROOT,check=True)
source=Path(find.stdout.decode().strip());package=fixture/'sed_eval';shutil.copytree(source,package,ignore=shutil.ignore_patterns('__pycache__'))
init=package/'__init__.py';before=hashlib.sha256(init.read_bytes()).hexdigest()
# Timestamp pyc files are accepted using source mtime/size, without comparing bytecode
# to source. Generate with the SAME qualified interpreter in this isolated package.
code='''from pathlib import Path
import importlib._bootstrap_external as b,importlib.util
p=Path(__import__('sys').argv[1]);s=p.stat()
payload="""\n_review_original_metrics=sound_event.EventBasedMetrics
class _ReviewPatchedMetrics(_review_original_metrics):
    def __init__(self,*args,**kwargs):
        kwargs['t_collar']=1000.0
        super().__init__(*args,**kwargs)
sound_event.EventBasedMetrics=_ReviewPatchedMetrics
"""
c=compile(p.read_text()+payload,str(p),'exec');pyc=Path(importlib.util.cache_from_source(str(p)));pyc.parent.mkdir(parents=True,exist_ok=True);pyc.write_bytes(b._code_to_timestamp_pyc(c,int(s.st_mtime),s.st_size))
'''
create=subprocess.run([str(python),'-c',code,str(init)],capture_output=True,cwd=ROOT,check=True)
assert hashlib.sha256(init.read_bytes()).hexdigest()==before
sys.path.insert(0,str(ROOT/'scripts'));import verify
probe=verify.reference_probe_code(ROOT)
env=dict(os.environ,PYTHONPATH=str(fixture),PYTHONDONTWRITEBYTECODE='1',MPLCONFIGDIR=str(OUT/'matplotlib'),NUMBA_CACHE_DIR=str(OUT/'numba'))
def run(name,argv):
    folder=OUT/name;folder.mkdir();p=subprocess.run([str(x) for x in argv],cwd=ROOT,env=env,capture_output=True)
    for n,data in [('stdout',p.stdout),('stderr',p.stderr)]:(folder/n).write_bytes(data)
    receipt=dict(argv=[str(x) for x in argv],cwd=str(ROOT),environment_overrides={k:env[k] for k in ['PYTHONPATH','PYTHONDONTWRITEBYTECODE','MPLCONFIGDIR','NUMBA_CACHE_DIR']},exit_code=p.returncode,stdout_sha256=hashlib.sha256(p.stdout).hexdigest(),stderr_sha256=hashlib.sha256(p.stderr).hexdigest())
    (folder/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');assert p.returncode==0,p.stderr
    return json.loads(p.stdout)
identity=run('identity',[python,'-c',probe,ROOT]);assert identity['sed_eval_source_verified'] is True
scorecode='''import json,sys
sys.path.insert(0,sys.argv[1])
from validation.sed_reference import evaluate_document
D=dict(schema_version=1,labels=['a'],config=dict(collar_s='0.2',offset_ratio='0.5'),recordings=[dict(id='x',reference=[dict(id='r',label='a',onset_s='1',offset_s='2')],prediction=[dict(id='p',label='a',onset_s='3',offset_s='4')])])
print(json.dumps(evaluate_document(D)))
'''
scored=run('scoring',[python,'-c',scorecode,ROOT]);assert scored['projected']['counts']['tp']==1
(OUT/'report.json').write_text(json.dumps(dict(confirmed=True,source_file_hash_unchanged=True,identity_source_verified=identity['sed_eval_source_verified'],identity_all_package_versions_verified=True,expected_tp_from_exact_rule=0,patched_cached_code_tp=scored['projected']['counts']['tp'],scope='isolated package mirror via PYTHONPATH; original venv and source read only; no claim entire qualification passes with this intentionally broad mutation'),indent=2)+'\n')
print(json.dumps(dict(confirmed=True,source_verified=True,expected_tp=0,actual_tp=scored['projected']['counts']['tp'])))
