from pathlib import Path
import subprocess, json, os, hashlib, time
ROOT=Path(__file__).resolve().parent
SRC=ROOT/'source'
ORIGINAL=Path('/Users/henryz/Desktop/比赛/mooneventeval-t0')
HEAD='d528d30b3e8b1feaea801c2058ec310206f78b65'
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
# check_reports records git identity using read-only rev-parse. Source is exact archive.
env['GIT_DIR']=subprocess.check_output(['git','rev-parse','--absolute-git-dir'],cwd=ORIGINAL,text=True).strip()
env['GIT_WORK_TREE']=str(SRC)
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ORIGINAL,text=True).strip()==HEAD
commands=[
 ('moon-suite',['scripts/with-toolchain.sh','moon','test','--target','native','--deny-warn']),
 ('python-suite',['python3','-W','error::ResourceWarning','-m','unittest','discover','-s','tests']),
 ('validation-suite',['.venv-reference/bin/python','-W','error::ResourceWarning','-m','unittest','discover','-s','validation/tests','-v']),
 ('probe-build',['scripts/with-toolchain.sh','moon','build','cmd/probe','--target','native','--release','--deny-warn']),
 ('renderers',['python3','validation/check_reports.py','--product','_build/native/release/build/cmd/probe/probe.exe','--output',str(ROOT/'renderers')]),
 ('probe-compatibility',['python3','validation/check_probe.py','--product','_build/native/release/build/cmd/probe/probe.exe','--output',str(ROOT/'probe-compatibility')]),
 ('json-controls',['python3','validation/check_json_controls.py','--product','_build/native/release/build/cmd/probe/probe.exe','--output',str(ROOT/'json-controls')]),
]
results=[]
for name,cmd in commands:
 start=time.monotonic()
 with (ROOT/(name+'.log')).open('wb') as log:
  p=subprocess.run(cmd,cwd=SRC,env=env,stdout=log,stderr=subprocess.STDOUT)
 row=dict(name=name,command=cmd,cwd=str(SRC),exit_code=p.returncode,seconds=time.monotonic()-start,log=name+'.log')
 results.append(row)
 (ROOT/'commands.json').write_text(json.dumps(results,indent=2)+'\n')
 print(json.dumps(row),flush=True)
 if p.returncode: print((ROOT/(name+'.log')).read_text()[-2500:],flush=True)
print('ALL DONE',flush=True)
