"""Record a reproducible native CLI demo; this is not personal explanation proof."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bin', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    binary = args.bin.resolve(); output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    assert not list(output.iterdir()), 'use a new output directory'
    rows = []
    for example, counts in [('duplicate', (1, 1, 0)), ('greedy-trap', (2, 0, 0)), ('boundary', (1, 0, 0))]:
        for fmt in ['text', 'json']:
            command = [str(binary), 'evaluate', f'examples/{example}.json', '--format', fmt]
            rows.append(record(output, example + '-' + fmt, command))
            if fmt == 'json':
                actual = json.loads((output / (example + '-' + fmt) / 'stdout').read_bytes())
                assert tuple(actual['summary']['counts'][k] for k in ['tp', 'fp', 'fn']) == counts
    for example, prediction in [('duplicate', 'p2'), ('boundary', 'p1')]:
        for fmt in ['text', 'json']:
            command = [str(binary), 'explain-pair', f'examples/{example}.json', '--recording',
                       'clip-01', '--reference', 'r1', '--prediction', prediction, '--format', fmt]
            name = example + '-explain-' + fmt
            rows.append(record(output, name, command))
            if fmt == 'json':
                actual = json.loads((output / name / 'stdout').read_bytes())
                assert actual['basis']['eligible'] is True and 'summary' not in actual
    for example in ['duplicate', 'greedy-trap', 'boundary']:
        (output / (example + '.input.json')).write_bytes((ROOT / 'examples' / (example + '.json')).read_bytes())
    report = dict(git_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                  product=str(binary), product_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),
                  commands=rows, passed=True, personal_explanation='NOT_PERFORMED',
                  scope='synthetic local native CLI transcripts; not a video or personal M2 evidence')
    (output / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(passed=True, native_calls=len(rows), personal_explanation='NOT_PERFORMED')))


def record(output, name, command):
    result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=10)
    folder = output / name; folder.mkdir()
    (folder / 'stdout').write_bytes(result.stdout); (folder / 'stderr').write_bytes(result.stderr)
    assert result.returncode == 0 and result.stderr == b'', (command, result.returncode, result.stderr)
    return dict(name=name, command=command, exit_code=result.returncode,
                stdout_sha256=hashlib.sha256(result.stdout).hexdigest(),
                stderr_sha256=hashlib.sha256(result.stderr).hexdigest())


if __name__ == '__main__':
    main()
