"""Replay one independent reviewer counterexample against a chosen source/product.
Run using the project's hash-locked .venv-reference/bin/python.
Output must not exist; no product source files are changed.
"""
import argparse,json,subprocess,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--product',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--mode',choices=['benchmark-ineligible','no-lf','crlf','duplicate-output-key','nan-output','timeout'],required=True);a=p.parse_args();source=a.source.resolve();exe=a.product.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
sys.path.insert(0,str(source))
base=f'''#!{sys.executable}
import json,subprocess,sys
sys.path.insert(0,{str(source)!r})
from validation.rational_oracle import eligible
result=subprocess.run([{str(exe)!r}]+sys.argv[1:],capture_output=True)
sys.stderr.buffer.write(result.stderr)
raw=result.stdout
'''
mods={
'benchmark-ineligible':"actual=json.loads(raw);pairs=actual['matches'];pairs[0]['prediction'],pairs[1]['prediction']=pairs[1]['prediction'],pairs[0]['prediction']\nfor m in pairs[:2]:m['basis']=eligible(m['reference'],m['prediction'],actual['config'])\nraw=(json.dumps(actual,ensure_ascii=False,separators=(',',':'))+'\\n').encode()\n",
'no-lf':"raw=raw.removesuffix(b'\\n')\n",
'crlf':"raw=raw.removesuffix(b'\\n')+b'\\r\\n'\n",
'duplicate-output-key':"raw=raw.replace(b'\"status\":\"completed\"',b'\"status\":\"completed\",\"status\":\"completed\"',1)\n",
'nan-output':"actual=json.loads(raw);actual['summary']['precision']=float('nan');raw=(json.dumps(actual)+'\\n').encode()\n",
}
wrapper=out/'product-wrapper'
if a.mode=='timeout':wrapper.write_text(f'#!{sys.executable}\nimport sys,time\nsys.stdout.buffer.write(b"partial stdout before timeout");sys.stdout.flush()\nsys.stderr.buffer.write(b"partial stderr before timeout");sys.stderr.flush()\ntime.sleep(35)\n')
else:wrapper.write_text(base+mods[a.mode]+'sys.stdout.buffer.write(raw)\nsys.exit(result.returncode)\n')
wrapper.chmod(0o755)
if a.mode=='benchmark-ineligible':
 command=[sys.executable,str(source/'validation/benchmark.py'),'--product',str(wrapper),'--output',str(out/'run'),'--cpu-name','Apple M5'];(out/'command.json').write_text(json.dumps(command,indent=2));raise SystemExit(subprocess.call(command,cwd=source))
from validation.qualify import run_qualification
fixture=json.loads((source/'validation/fixtures/comparison-baseline.json').read_bytes());case=dict(name='baseline',category='decimal_nonboundary',document=fixture['input'])
raise SystemExit(run_qualification(wrapper,out/'run',cases=[case]))
