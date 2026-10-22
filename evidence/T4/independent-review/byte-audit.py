from pathlib import Path
import subprocess,os,json,hashlib
root=Path(__file__).resolve().parent
src=root/'source'
original=Path('/Users/henryz/Desktop/比赛/mooneventeval-t0')
exe=src/'_build/native/release/build/cmd/probe/probe.exe'
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
env['GIT_DIR']=subprocess.check_output(['git','rev-parse','--absolute-git-dir'],cwd=original,text=True).strip()
env['GIT_WORK_TREE']=str(src)
prior=src/'evidence/T3/parity-final'
report=json.loads((prior/'report.json').read_text())
records=[]
for case in report['cases']:
 name=case['case']; raw=(prior/name/'input.json').read_text()
 p=subprocess.run([str(exe),raw],capture_output=True)
 baseline=(prior/name/'product.stdout').read_bytes()
 folder=root/'byte-audit'/name;folder.mkdir(parents=True,exist_ok=True)
 (folder/'stdout').write_bytes(p.stdout);(folder/'stderr').write_bytes(p.stderr)
 assert p.returncode==0 and p.stdout==baseline and not p.stderr
 records.append({'name':name,'exit_code':p.returncode,'raw_bytes':len(p.stdout),'sha256':hashlib.sha256(p.stdout).hexdigest()})
# Demonstrate same input, genuinely different bytes, but checker passes all 430 checks.
raw=(prior/report['cases'][0]['case']/'input.json').read_text()
a=subprocess.run([str(exe),raw],capture_output=True)
b=subprocess.run([str(root/'crlf-probe.py'),raw],capture_output=True)
(root/'real.stdout').write_bytes(a.stdout);(root/'mutant.stdout').write_bytes(b.stdout)
assert a.stdout != b.stdout and b'\r\n' in b.stdout
cmd=['python3','validation/check_reports.py','--product',str(root/'crlf-probe.py'),'--output',str(root/'crlf-accepted')]
r=subprocess.run(cmd,cwd=src,env=env,capture_output=True)
(root/'crlf-checker.stdout').write_bytes(r.stdout);(root/'crlf-checker.stderr').write_bytes(r.stderr)
result={'raw_baseline_checks':records,'raw_byte_equality_passed':len(records),'mutant_command':cmd,'mutant_exit_code':r.returncode,'mutant_differs_from_real_bytes':a.stdout!=b.stdout,'mutant_has_raw_crlf':b'\r\n' in b.stdout,'checker_stdout':r.stdout.decode(),'checker_stderr':r.stderr.decode()}
(root/'byte-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='raw_baseline_checks'}))
