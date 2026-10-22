import subprocess,sys,pathlib,json,time,hashlib
root=pathlib.Path('/var/folders/l0/z510jl1d0rxc2cpk2jkvmks80000gn/T/mee-t6-independent-weo09xrc');work=root/'source';name=sys.argv[1];command=sys.argv[2:];out=root/'evidence'/name;out.mkdir(parents=True,exist_ok=False)
(out/'command.json').write_text(json.dumps({'cwd':str(work),'argv':command},ensure_ascii=False,indent=2))
t=time.time()
with (out/'stdout').open('wb') as so,(out/'stderr').open('wb') as se:r=subprocess.run(command,cwd=work,stdout=so,stderr=se)
(out/'receipt.json').write_text(json.dumps({'exit_code':r.returncode,'elapsed_s':time.time()-t,'stdout_sha256':hashlib.sha256((out/'stdout').read_bytes()).hexdigest(),'stderr_sha256':hashlib.sha256((out/'stderr').read_bytes()).hexdigest()},indent=2))
print(name,r.returncode,'elapsed',time.time()-t,'evidence',out)
print((out/'stdout').read_text(errors='replace')[-2500:]);print((out/'stderr').read_text(errors='replace')[-2500:]);sys.exit(r.returncode)
