"""Compare the real file CLI with all 46 archived T3 report byte streams."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--product', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); binary = args.product.resolve(); output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    prior = ROOT / 'evidence/T3/parity-final'
    rows = []
    for row in json.loads((prior / 'report.json').read_bytes())['cases']:
        name = row['case']; folder = output / name; folder.mkdir()
        input_path = folder / 'input.json'; input_path.write_bytes((prior / name / 'input.json').read_bytes())
        command = [str(binary), 'evaluate', str(input_path), '--format', 'json']
        result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=10)
        (folder / 'stdout').write_bytes(result.stdout); (folder / 'stderr').write_bytes(result.stderr)
        assert result.returncode == 0 and not result.stderr, (name, result.returncode, result.stderr)
        assert result.stdout == (prior / name / 'product.stdout').read_bytes(), name
        rows.append(dict(name=name, command=command, exit_code=result.returncode,
                         stdout_sha256=hashlib.sha256(result.stdout).hexdigest()))
    report = dict(passed=True, raw_byte_cases=len(rows), cases=rows, product=str(binary),
                  product_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),
                  git_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                  scope='file CLI against archived T3 bytes; no new sed_eval run or final A11')
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(passed=True, raw_byte_cases=len(rows))))


if __name__ == '__main__':
    main()
