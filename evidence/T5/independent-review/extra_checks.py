import pathlib,subprocess,json,hashlib,itertools,os
root=pathlib.Path(__file__).resolve().parent; work=root/'checkout'; out=root/'extra';out.mkdir()
exe=work/'_build/native/release/build/cmd/mooneventeval/mooneventeval.exe'
rows=[]
def call(name,args,code,fmt):
 r=subprocess.run([str(exe),*args],cwd=work,capture_output=True,timeout=8)
 folder=out/name;folder.mkdir();(folder/'stdout').write_bytes(r.stdout);(folder/'stderr').write_bytes(r.stderr)
 ok=r.returncode==code
 if fmt=='json':
  try: data=json.loads(r.stdout.decode('utf-8'));ok=ok and not r.stderr and r.stdout.endswith(b'\n') and not r.stdout.endswith(b'\n\n')
  except (ValueError,UnicodeError): ok=False
 else: ok=ok and not r.stdout and b'INVALID_ARGUMENT' in r.stderr
 row=dict(name=name,args=args,exit_code=r.returncode,expected_exit=code,expected_format=fmt,passed=ok,stdout_sha256=hashlib.sha256(r.stdout).hexdigest(),stderr_sha256=hashlib.sha256(r.stderr).hexdigest());rows.append(row);(folder/'receipt.json').write_text(json.dumps(row,indent=2)+'\n')
# All option orders, with every ID exactly a reserved option name.
doc=json.loads((work/'examples/boundary.json').read_bytes());rec=doc['recordings'][0];rec['id']='--format';rec['reference'][0]['id']='--prediction';rec['prediction'][0]['id']='--reference'
fixture=out/'reserved.json';fixture.write_text(json.dumps(doc)+'\n')
for i,opts in enumerate(itertools.permutations([['--recording','--format'],['--reference','--prediction'],['--prediction','--reference'],['--format','json']])):
 call('reserved-order-'+str(i),['explain-pair',str(fixture),*sum(opts,[])],0,'json')
# Canonical pair-aligned malformed option value must not hide real --format.
for value in ['ordinary','--recording','--reference','--prediction','--format']:
 call('unknown-value-'+value.replace('--',''),['evaluate','absent','--unknown',value,'--format','json'],2,'json')
for i,formats in enumerate([['--format','bad'],['--format','json','--format','text'],['--format','text','--format','json'],['--format','json','--format','json'],['--format'],['--format','']]):
 call('bad-format-'+str(i),['evaluate','absent',*formats],2,'text')
for i,args in enumerate([[],['evaluate'],['evaluate',''],['--help','extra'],['evaluate','absent','extra'],['explain-pair','absent','--recording','r','--reference','r']]):
 call('invalid-grammar-'+str(i),args,2,'text')
# File beginning -- is usable with ./ per documented spelling.
file=work/'--review-input.json';file.write_bytes((work/'examples/duplicate.json').read_bytes())
call('dash-filename',['evaluate','./--review-input.json','--format','json'],0,'json');file.unlink()
(out/'report.json').write_text(json.dumps(dict(cases=len(rows),passed=sum(r['passed'] for r in rows),failed=[r for r in rows if not r['passed']]),indent=2)+'\n');print(json.dumps(dict(cases=len(rows),passed=sum(r['passed'] for r in rows),failed=[r['name'] for r in rows if not r['passed']])))
