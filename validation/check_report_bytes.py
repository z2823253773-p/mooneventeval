"""Negative controls for renderer verification: altered raw newlines must fail."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--product', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    product = args.product.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, replacement, text_only, expected_error in [
        ('crlf-all', b'\r\n', False, 'changed evaluation JSON bytes'),
        ('cr-text', b'\r', True, 'unsafe raw text control'),
    ]:
        folder = output / name
        folder.mkdir(parents=True, exist_ok=True)
        wrapper = folder / 'mutant.py'
        wrapper.write_text(
            f'#!{sys.executable}\n'
            'import subprocess, sys\n'
            f'r = subprocess.run([{str(product)!r}, *sys.argv[1:]], capture_output=True)\n'
            f'alter = {not text_only!r} or "report-text" in sys.argv[2:] or "explain-text" in sys.argv[2:]\n'
            f'sys.stdout.buffer.write(r.stdout.replace(b"\\n", {replacement!r}) if alter else r.stdout)\n'
            'sys.stderr.buffer.write(r.stderr)\n'
            'sys.exit(r.returncode)\n', encoding='utf-8')
        wrapper.chmod(0o755)
        command = [sys.executable, str(ROOT / 'validation/check_reports.py'),
                   '--product', str(wrapper), '--output', str(folder / 'capture')]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=120)
        (folder / 'checker.stdout').write_bytes(result.stdout)
        (folder / 'checker.stderr').write_bytes(result.stderr)
        # Reproduce the first captured call directly to establish exact archival.
        capture = folder / 'capture' / ('text/duplicate' if text_only else 'regression/duplicate')
        document = json.dumps(json.loads((capture / 'input.json').read_bytes()),
                              ensure_ascii=True, separators=(',', ':'))
        mode = ['report-text'] if text_only else []
        witness = subprocess.run([str(wrapper), document, *mode], capture_output=True, timeout=30)
        (folder / 'witness.stdout').write_bytes(witness.stdout)
        archived = (capture / 'stdout').read_bytes()
        rows.append(dict(name=name, command=command, checker_exit=result.returncode,
                         expected_assertion=expected_error,
                         rejected=result.returncode != 0 and expected_error.encode() in result.stderr,
                         witness_has_cr=b'\r' in witness.stdout,
                         archive_preserves_bytes=archived == witness.stdout,
                         witness_sha256=hashlib.sha256(witness.stdout).hexdigest(),
                         archive_sha256=hashlib.sha256(archived).hexdigest()))
    report = dict(cases=rows, passed=all(row['rejected'] and row['witness_has_cr']
                                       and row['archive_preserves_bytes'] for row in rows))
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report))
    raise SystemExit(0 if report['passed'] else 1)


if __name__ == '__main__':
    main()
