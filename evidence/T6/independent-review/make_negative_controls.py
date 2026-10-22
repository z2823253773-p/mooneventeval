from pathlib import Path
import sys
root=Path(__file__).resolve().parent;source=root/'source';exe=source/'_build/native/release/build/cmd/mooneventeval/mooneventeval.exe';out=root/'negative-controls';out.mkdir()
base=f'''#!{sys.executable}
import json, subprocess, sys
sys.path.insert(0,{str(source)!r})
from validation.rational_oracle import eligible
result=subprocess.run([{str(exe)!r}]+sys.argv[1:],capture_output=True)
sys.stderr.buffer.write(result.stderr)
raw=result.stdout
'''
mods={
'benchmark-ineligible':'''actual=json.loads(raw)
pairs=actual['matches']
pairs[0]['prediction'],pairs[1]['prediction']=pairs[1]['prediction'],pairs[0]['prediction']
for m in pairs[:2]:m['basis']=eligible(m['reference'],m['prediction'],actual['config'])
raw=(json.dumps(actual,ensure_ascii=False,separators=(',',':'))+'\\n').encode()
''',
'no-lf':"raw=raw.removesuffix(b'\\n')\n",
'crlf':"raw=raw.removesuffix(b'\\n')+b'\\r\\n'\n",
'duplicate-output-key':"raw=raw.replace(b'\"status\":\"completed\"',b'\"status\":\"completed\",\"status\":\"completed\"',1)\n",
'nan-output':"actual=json.loads(raw);actual['summary']['precision']=float('nan');raw=(json.dumps(actual)+'\\n').encode()\n",
}
for name,mod in mods.items():
 p=out/name;p.write_text(base+mod+'sys.stdout.buffer.write(raw)\nsys.exit(result.returncode)\n');p.chmod(0o755)
slow=out/'timeout';slow.write_text(f'#!{sys.executable}\nimport sys,time\nsys.stdout.buffer.write(b"partial stdout before timeout");sys.stdout.flush()\nsys.stderr.buffer.write(b"partial stderr before timeout");sys.stderr.flush()\ntime.sleep(35)\n');slow.chmod(0o755)
(root/'negative_qualification.py').write_text('''import json,sys,traceback
from pathlib import Path
root=Path(__file__).resolve().parent
sys.path.insert(0,str(root/'source'))
from validation.qualify import run_qualification
fixture=json.loads((root/'source/validation/fixtures/comparison-baseline.json').read_bytes())
mode=sys.argv[1]
case=dict(name='baseline',category='decimal_nonboundary',document=fixture['input'])
code=run_qualification(root/'negative-controls'/mode,root/'evidence'/('negative-'+mode),cases=[case])
print('QUALIFICATION_RETURN',code)
raise SystemExit(code)
''')
print(out)
