"""Author replay of five original reviewer negatives; not an independent re-review."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args();output=args.output.resolve();output.mkdir(parents=True,exist_ok=True)
assert not list(output.iterdir()),'use a fresh output directory'
script=ROOT/'evidence/T6/independent-review/replay_negative.py'
manifest=json.loads((script.parent/'SHA256SUMS.json').read_bytes())
assert hashlib.sha256(script.read_bytes()).hexdigest()==manifest['replay_negative.py']
exe=ROOT/'_build/native/release/build/cmd/mooneventeval/mooneventeval.exe';rows=[]
for mode in ['benchmark-ineligible','no-lf','crlf','duplicate-output-key','nan-output']:
    target=output/mode
    command=[sys.executable,str(script),'--source',str(ROOT),'--product',str(exe),'--output',str(target),'--mode',mode]
    result=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=120)
    (target/'runner.stdout').write_bytes(result.stdout);(target/'runner.stderr').write_bytes(result.stderr)
    assert result.returncode!=0,(mode,'false green')
    if mode=='benchmark-ineligible':
        comparison=json.loads((target/'run/sparse/0/comparison.json').read_bytes())
        assert not comparison['passed'] and any(d['path']=='match.eligibility' for d in comparison['differences'])
    else:
        report=json.loads((target/'run/report.json').read_bytes())
        assert not report['passed'] and report['unexplained']==['baseline']
        comparison=json.loads((target/'run/baseline/comparison.json').read_bytes())
        assert any(d['path']=='stdout' for d in comparison['differences'])
        assert b'Traceback' not in result.stderr
    row=dict(mode=mode,command=command,exit_code=result.returncode,rejected_for_expected_reason=True,
             stdout_sha256=hashlib.sha256(result.stdout).hexdigest(),stderr_sha256=hashlib.sha256(result.stderr).hexdigest())
    (target/'replay-receipt.json').write_text(json.dumps(row,indent=2)+'\n');rows.append(row)
report=dict(passed=True,author_replay=True,independent_re_review=False,cases=rows,
            git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            product_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),
            original_script_sha256=manifest['replay_negative.py'],minor_timeout_output_retention='DEFERRED')
(output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(passed=True,reviewer_negative_controls=len(rows),independent_re_review=False)))
