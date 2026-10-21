"""Behavioral mutation gate in disposable copies; never edits the working source."""
from __future__ import annotations
import difflib
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'evidence/T2/mutations'


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    source = ROOT / 'eventeval/matching.mbt'
    baseline = source.read_text()
    wrapper = str(ROOT / 'scripts/with-toolchain.sh')
    mutations = [
        ('prediction-reuse', 'if prediction_match[p] == -1 {', 'if true {',
         'matching_one_to_one_duplicate_and_isolated'),
        ('greedy-only', '    let visited = Array::make(prediction_count, false)',
         '    if reference_match[root] == -1 { continue }\n'
         '    let visited = Array::make(prediction_count, false)',
         'matching_augmenting_trap'),
    ]
    report = []
    for name, old, new, test in mutations:
        assert baseline.count(old) == 1
        mutated = baseline.replace(old, new, 1)
        diff = ''.join(difflib.unified_diff(baseline.splitlines(True), mutated.splitlines(True),
                                          fromfile='baseline/matching.mbt', tofile=f'{name}/matching.mbt'))
        (OUTPUT / f'{name}.diff').write_text(diff)
        with tempfile.TemporaryDirectory(prefix=f'mutation-{name}-', dir=ROOT / '.tools') as temporary:
            copy = Path(temporary)
            shutil.copy2(ROOT / 'moon.mod', copy / 'moon.mod')
            shutil.copytree(ROOT / 'eventeval', copy / 'eventeval')
            command = [wrapper, 'moon', 'test', 'eventeval', '--target', 'native',
                       '--deny-warn', '--filter', test]
            control = subprocess.run(command, cwd=copy, text=True, capture_output=True, timeout=120)
            (OUTPUT / f'{name}-control.log').write_text(control.stdout + control.stderr)
            assert control.returncode == 0 and 'passed: 1, failed: 0' in control.stdout
            (copy / 'eventeval/matching.mbt').write_text(mutated)
            result = subprocess.run(command, cwd=copy, text=True, capture_output=True, timeout=120)
            log = result.stdout + result.stderr
            (OUTPUT / f'{name}-mutated.log').write_text(log)
            killed = (result.returncode != 0 and 'passed: 0, failed: 1' in log
                      and ('@EXPECT_FAILED' in log or 'expect test failed' in log.lower()))
            report.append({"mutation": name, "test": test, "command": command,
                           "control_exit": control.returncode, "mutated_exit": result.returncode,
                           "killed_by_behavior": killed, "diff": f'{name}.diff',
                           "baseline_sha256": hashlib.sha256(baseline.encode()).hexdigest(),
                           "mutated_sha256": hashlib.sha256(mutated.encode()).hexdigest()})
            if not killed:
                print(log[-4000:])
                raise RuntimeError(f'{name} did not fail by a behavioral assertion')
    assert source.read_text() == baseline
    (OUTPUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
