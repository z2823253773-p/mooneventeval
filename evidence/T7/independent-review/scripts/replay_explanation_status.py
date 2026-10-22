#!/usr/bin/env python3
"""Exit 1 if the release gate accepts an actually compiled failed explanation.

Replay after a fix with --checkout /absolute/checkout --output /fresh/output.
Only the fresh output tree is changed; no installed/global tools are modified.
"""
from pathlib import Path
import argparse
import difflib
import hashlib
import json
import os
import shutil
import subprocess
import sys

def digest(raw): return hashlib.sha256(raw).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--checkout', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    checkout = args.checkout.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()): raise ValueError('output must be fresh')
    source = output/'mutated-source'; source.mkdir()
    names = [line[2:] for line in (checkout/'.moonignore').read_text().splitlines()
             if line.startswith('!/') and not line.endswith('/')]
    for name in ['.moonignore', *names]:
        target = source/name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(checkout/name, target)
    product = source/'eventeval/report_json.mbt'
    original = product.read_text()
    before, explanation = original.split('pub fn explanation_json(', 1)
    needle = '("status", "\\\"completed\\\"")'
    replacement = '("status", "\\\"failed\\\"")'
    assert explanation.count(needle) == 1
    mutated = before+'pub fn explanation_json('+explanation.replace(needle, replacement, 1)
    product.write_text(mutated)
    (output/'mutation.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True), mutated.splitlines(True), fromfile='original/eventeval/report_json.mbt', tofile='mutated/eventeval/report_json.mbt')))
    command = ['env','PYTHONDONTWRITEBYTECODE=1',sys.executable,str(checkout/'scripts/package_candidate.py'), '--source',str(source),'--output',str(output/'gate')]
    result = subprocess.run(command, cwd=source, capture_output=True, timeout=180)
    (output/'stdout').write_bytes(result.stdout)
    (output/'stderr').write_bytes(result.stderr)
    receipt = dict(command=command,cwd=str(source),exit_code=result.returncode,
                   stdout_sha256=digest(result.stdout),stderr_sha256=digest(result.stderr),
                   original_source_sha256=digest(original.encode()),
                   mutated_source_sha256=digest(mutated.encode()))
    (output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    gate_report = output/'gate/report.json'
    explain_stdout = output/'gate/unpacked-examples/explain/stdout'
    report = json.loads(gate_report.read_text()) if gate_report.exists() else None
    actual = json.loads(explain_stdout.read_bytes()) if explain_stdout.exists() else None
    false_green = (result.returncode == 0 and report is not None and report['passed'] is True
                   and actual is not None and actual.get('status') == 'failed')
    summary = dict(false_green=false_green,gate_exit_code=result.returncode,
                   package_passed=None if report is None else report['passed'],
                   actual_explanation_status=None if actual is None else actual.get('status'),
                   scope='one serializer literal changed in a fresh source copy; real moon archive/unpack/build/run')
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary))
    if actual is None:
        print('Control did not reach the actual explanation; inspect stderr before classifying.', file=sys.stderr)
        return 2
    return 1 if false_green else 0

if __name__ == '__main__': raise SystemExit(main())
