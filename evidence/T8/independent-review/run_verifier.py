from pathlib import Path
import subprocess, json, hashlib, time
root=Path('/private/tmp/mooneventeval-review-available/checkout');audit=root.parent
paths=subprocess.check_output(['git','ls-files','-z','evidence'],cwd=root)
subprocess.run(['git','update-index','--skip-worktree','-z','--stdin'],input=paths,cwd=root,check=True)
meta=json.loads((audit/'setup.json').read_bytes());meta['copy_diff_evidence_omitted_count']=len(meta.pop('copy_diff').splitlines());(audit/'setup.json').write_text(json.dumps(meta,indent=2)+'\n')
argv=['python3','scripts/verify.py','--mode','local','--evidence',str(audit/'full-verifier')]
start=time.monotonic();p=subprocess.run(argv,cwd=root,capture_output=True)
for n,b in [('stdout',p.stdout),('stderr',p.stderr)]:(audit/('full-verifier.'+n)).write_bytes(b)
receipt=dict(argv=argv,cwd=str(root),exit_code=p.returncode,elapsed_seconds=time.monotonic()-start,stdout_sha256=hashlib.sha256(p.stdout).hexdigest(),stderr_sha256=hashlib.sha256(p.stderr).hexdigest())
(audit/'full-verifier.receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt));print(p.stdout.decode(errors='replace')[-3000:]);print(p.stderr.decode(errors='replace')[-1000:])
