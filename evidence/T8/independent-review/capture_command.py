from pathlib import Path
import subprocess,sys,json,hashlib
AUDIT=Path(__file__).resolve().parent
name=sys.argv[1];argv=sys.argv[2:];p=subprocess.run(argv,cwd=AUDIT,capture_output=True)
for label,b in [('stdout',p.stdout),('stderr',p.stderr)]:(AUDIT/(name+'.'+label)).write_bytes(b)
(AUDIT/(name+'.receipt.json')).write_text(json.dumps(dict(argv=argv,cwd=str(AUDIT),exit_code=p.returncode,stdout_sha256=hashlib.sha256(p.stdout).hexdigest(),stderr_sha256=hashlib.sha256(p.stderr).hexdigest()),indent=2)+'\n')
print(p.stdout.decode(errors='replace'));print(p.stderr.decode(errors='replace'));raise SystemExit(p.returncode)
