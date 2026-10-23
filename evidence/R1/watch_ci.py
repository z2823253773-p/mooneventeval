"""Read-only receipts for the single explicitly authorized private CI run."""
from pathlib import Path
import hashlib,json,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[2]
run_id=int(sys.argv[1]);out=ROOT/'evidence/R1'/('remote-'+str(run_id));out.mkdir(exist_ok=True)
repo='repos/z2823253773-p/mooneventeval';previous=None
for attempt in range(100):
 rows={}
 for kind,path in [('run',repo+'/actions/runs/'+str(run_id)),('jobs',repo+'/actions/runs/'+str(run_id)+'/jobs')]:
  argv=['gh','api',path];start=time.monotonic();p=subprocess.run(argv,cwd=ROOT,capture_output=True,timeout=45)
  folder=out/(f'{attempt:03d}-'+kind);folder.mkdir(exist_ok=False)
  for n,b in [('stdout',p.stdout),('stderr',p.stderr)]:(folder/n).write_bytes(b)
  row=dict(command=argv,cwd=str(ROOT),exit_code=p.returncode,elapsed_seconds=time.monotonic()-start,stdout_sha256=hashlib.sha256(p.stdout).hexdigest(),stderr_sha256=hashlib.sha256(p.stderr).hexdigest())
  (folder/'receipt.json').write_text(json.dumps(row,indent=2)+'\n')
  if p.returncode:raise SystemExit('GitHub read failed; see '+str(folder))
  rows[kind]=json.loads(p.stdout)
 summary=dict(run_id=run_id,head_sha=rows['run']['head_sha'],status=rows['run']['status'],conclusion=rows['run']['conclusion'],jobs=[dict(name=j['name'],id=j['id'],status=j['status'],conclusion=j['conclusion'],current_step=next((s['name'] for s in j.get('steps',[]) if s['status']=='in_progress'),None)) for j in rows['jobs']['jobs']])
 text=json.dumps(summary)
 if text!=previous:print(text,flush=True);previous=text
 if summary['status']=='completed':
  (out/'final-run.json').write_text(json.dumps(rows['run'],indent=2)+'\n');(out/'final-jobs.json').write_text(json.dumps(rows['jobs'],indent=2)+'\n');break
 time.sleep(30)
else:raise SystemExit('bounded CI watch limit reached')
