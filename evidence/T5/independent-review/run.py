import sys,subprocess,pathlib,json,hashlib,datetime,os
root=pathlib.Path(__file__).resolve().parent
name=sys.argv[1]; command=sys.argv[2:]; started=datetime.datetime.now(datetime.timezone.utc).isoformat()
r=subprocess.run(command,cwd=root/'checkout',capture_output=True)
folder=root/'receipts'/name;folder.mkdir()
(folder/'stdout.bin').write_bytes(r.stdout);(folder/'stderr.bin').write_bytes(r.stderr)
(folder/'receipt.json').write_text(json.dumps(dict(command=command,cwd=str(root/'checkout'),started=started,exit_code=r.returncode,stdout_sha256=hashlib.sha256(r.stdout).hexdigest(),stderr_sha256=hashlib.sha256(r.stderr).hexdigest(),env={k:os.environ[k] for k in ['MEE_BIN','MEE_EVIDENCE'] if k in os.environ}),indent=2)+'\n')
print(json.dumps(dict(name=name,exit_code=r.returncode,stdout_bytes=len(r.stdout),stderr_bytes=len(r.stderr))))
print(r.stdout[-2000:].decode(errors='replace'));print(r.stderr[-2000:].decode(errors='replace'))
sys.exit(r.returncode)
