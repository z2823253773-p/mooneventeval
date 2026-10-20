"""Focused T1 experiment in temporary copies; never edits the real package."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'evidence/T1/mutations-after-review'
TOOL = ROOT/'.tools/moonbit/0.10.14+7d59c7ec9'
ENV = dict(os.environ, MOON_HOME=str(TOOL), PATH=str(TOOL/'bin')+os.pathsep+os.environ['PATH'])

if __name__ == '__main__':
    OUT.mkdir(exist_ok=True)
    changes = [
        ('onset_strict', 'onset_abs <= config.collar_us', 'onset_abs < config.collar_us'),
        ('offset_strict', '1_000_000L <= offset_limit_scaled', '1_000_000L < offset_limit_scaled'),
        ('minimum_instead_of_maximum', 'fixed_scaled > ratio_scaled', 'fixed_scaled < ratio_scaled'),
        ('prediction_duration', '(reference.offset_us - reference.onset_us)', '(prediction.offset_us - prediction.onset_us)'),
        ('collar_ratio_swapped', 'let fixed_scaled = config.collar_us * 1_000_000L\n  let ratio_scaled = (reference.offset_us - reference.onset_us) *\n    config.offset_ratio_ppm', 'let fixed_scaled = config.offset_ratio_ppm * 1_000_000L\n  let ratio_scaled = (reference.offset_us - reference.onset_us) *\n    config.collar_us'),
    ]
    records = []
    original = (ROOT/'eventeval/eligibility.mbt').read_text()
    with tempfile.TemporaryDirectory(prefix='mooneventeval-T1-mutations-', dir='/private/tmp') as folder:
        temp = Path(folder)
        shutil.copyfile(ROOT/'moon.mod', temp/'moon.mod')
        shutil.copytree(ROOT/'eventeval', temp/'eventeval')
        for name, old, new in [('baseline', '', '')] + changes:
            if old:
                assert original.count(old) == 1, (name, 'mutation must target exactly one expression')
                source = original.replace(old, new, 1)
            else:
                source = original
            (temp/'eventeval/eligibility.mbt').write_text(source)
            log = OUT/(name+'.log')
            command = [str(TOOL/'bin/moon'), '-C', str(temp), 'test', '--target', 'native', '--deny-warn']
            with log.open('wb') as stream:
                result = subprocess.run(command, env=ENV, stdout=stream, stderr=subprocess.STDOUT, timeout=120)
            output = log.read_text()
            match = re.search(r'Total tests: (\d+), passed: (\d+), failed: (\d+)', output)
            assert match, (name, 'not a behavior result; inspect compile/runtime log')
            total, passed, failed = map(int, match.groups())
            killed = result.returncode != 0 and failed > 0
            assert (result.returncode == 0 and failed == 0) if name == 'baseline' else killed, name
            records.append({'name': name, 'command': command, 'exit_code': result.returncode,
                            'total': total, 'passed': passed, 'failed': failed,
                            'killed': killed if old else None, 'replacement': [old,new],
                            'mutated_source_sha256': hashlib.sha256(source.encode()).hexdigest(),
                            'log': str(log.relative_to(ROOT)),
                            'log_sha256': hashlib.sha256(log.read_bytes()).hexdigest()})
    report = {'scope': 'five targeted eligibility mutations, not exhaustive mutation coverage',
              'source_sha256': hashlib.sha256(original.encode()).hexdigest(), 'results': records}
    (OUT/'results.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({'baseline_passed':True,'mutations_killed':5,'results':str(OUT/'results.json')}))
