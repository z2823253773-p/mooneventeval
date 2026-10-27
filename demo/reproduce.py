"""Replay the delivered reports; optionally rerun the pinned original sed_eval.

Python only launches the native product / independent reference and checks
published examples. It does not implement the product's scoring algorithm.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PRODUCT = {
    'duplicate.json': ['evaluate', 'examples/duplicate.json', '--format', 'json'],
    'duplicate.txt': ['evaluate', 'examples/duplicate.json', '--format', 'text'],
    'greedy-trap.json': ['evaluate', 'examples/greedy-trap.json', '--format', 'json'],
    'boundary.json': ['evaluate', 'examples/boundary.json', '--format', 'json'],
    'boundary-explanation.json': ['explain-pair', 'examples/boundary.json', '--recording', 'clip-01', '--reference', 'r1', '--prediction', 'p1', '--format', 'json'],
    'eligible-unselected.json': ['explain-pair', 'examples/duplicate.json', '--recording', 'clip-01', '--reference', 'r1', '--prediction', 'p2', '--format', 'json'],
    'wrong-label.json': ['evaluate', 'demo/inputs/wrong-label.json', '--format', 'json'],
    'decimal-boundary.json': ['evaluate', 'demo/inputs/decimal-boundary.json', '--format', 'json'],
}
REFERENCE = {
    'duplicate.json': 'examples/duplicate.json',
    'greedy-trap.json': 'examples/greedy-trap.json',
    'wrong-label.json': 'demo/inputs/wrong-label.json',
    'decimal-boundary.json': 'demo/inputs/decimal-boundary.json',
}


def replay(args):
    binary = args.bin.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    receipts = []
    results = {}

    def execute(command, name, snapshot, is_json=True, reference=False):
        run = subprocess.run([str(x) for x in command], cwd=ROOT, capture_output=True, timeout=120)
        (output/(name+'.stdout')).write_bytes(run.stdout)
        (output/(name+'.stderr')).write_bytes(run.stderr)
        receipts.append(dict(command=[str(x) for x in command], exit_code=run.returncode,
                             stdout_sha256=hashlib.sha256(run.stdout).hexdigest(),
                             stderr_sha256=hashlib.sha256(run.stderr).hexdigest(), snapshot=str(snapshot.relative_to(ROOT))))
        # Locked upstream dependencies emit deprecation warnings; retain them.
        # Native product examples still require clean stderr.
        if run.returncode or (run.stderr and not reference):
            raise ValueError('documented command failed: '+name)
        text = run.stdout.decode('utf-8', errors='strict')
        if not text.endswith('\n') or '\r' in text:
            raise ValueError('unexpected report framing: '+name)
        result = json.loads(text) if is_json else text
        if args.write:
            snapshot.write_bytes(run.stdout)
        elif snapshot.read_bytes() != run.stdout:
            raise ValueError('published report drift: '+name)
        return result

    for name, command in PRODUCT.items():
        results[name] = execute([binary, *command], 'product-'+name, ROOT/'demo/output'/name, name.endswith('.json'))
        if name.endswith('.json'):
            assert results[name]['status'] == 'completed'
    for name, counts in {'duplicate.json': (1,1,0), 'greedy-trap.json': (2,0,0),
                         'boundary.json': (1,0,0), 'wrong-label.json': (0,1,1),
                         'decimal-boundary.json': (1,0,0)}.items():
        assert tuple(results[name]['summary']['counts'][key] for key in ['tp','fp','fn']) == counts
    assert results['eligible-unselected.json']['basis']['eligible'] is True
    assert results['duplicate.json']['false_positives'][0]['reason'] == 'unselected_in_maximum_matching'
    assert results['wrong-label.json']['matches'] == []
    readme = (ROOT/'README.md').read_text()
    section = readme.split('<!-- output-summary:start -->')[1].split('<!-- output-summary:end -->')[0]
    summary = json.loads(re.search(r'```json\n(.*?)```', section, re.S).group(1))
    assert summary == results['duplicate.json']['summary'], 'README summary drift'
    demo_text = (ROOT/'demo/README.md').read_text()
    assert '```text\n'+results['duplicate.txt']+'```' in demo_text, 'complete text report drift'
    references = {}
    if args.reference_python:
        for name, source in REFERENCE.items():
            # Resolving this symlink would bypass pyvenv.cfg and lose the locked environment.
            references[name] = execute([args.reference_python.absolute(), ROOT/'validation/sed_reference.py', ROOT/source],
                                       'reference-'+name, ROOT/'demo/reference'/name, reference=True)
        assert references['duplicate.json']['raw']['counts']['Ntp'] == 1
        assert references['greedy-trap.json']['raw']['counts']['Ntp'] == 2
        wrong = references['wrong-label.json']
        assert tuple(wrong['raw']['counts'][key] for key in ['Ntp','Nsubs','Nfp','Nfn']) == (0,1,0,0)
        assert tuple(wrong['projected']['counts'][key] for key in ['tp','fp','fn']) == (0,1,1)
        assert references['decimal-boundary.json']['raw']['counts']['Ntp'] == 0
    report = dict(passed=True, product_calls=len(PRODUCT), reference_calls=len(references),
                  reference_checked=bool(references), mode='write' if args.write else 'check',
                  product_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(), receipts=receipts,
                  scope='synthetic published-output replay; scoped original-reference demonstrations, not external user adoption')
    (output/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({key:report[key] for key in ['passed','product_calls','reference_calls','reference_checked']}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check',action='store_true');mode.add_argument('--write',action='store_true')
    parser.add_argument('--bin',type=Path,default=ROOT/'_build/native/release/build/cmd/mooneventeval/mooneventeval.exe')
    parser.add_argument('--reference-python',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    replay(parser.parse_args())
