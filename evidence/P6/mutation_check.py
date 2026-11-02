"""Run three compilable duplicate-check mutations against real native API tests."""
from pathlib import Path
import json
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
STAGE = ROOT / 'evidence/P6'
OUTPUT = STAGE / 'mutations-final'


def main():
    rows = []
    for name, old, new in [
        ('skip-rejection', 'if seen.contains(key) {', 'if seen.contains(key) && false {'),
        ('compare-raw-keys', 'Ok(String(key)) => key', 'Ok(String(_)) => text[start:index].to_owned()'),
        ('empty-key-preview', 'if count == 64 {', 'if count == 0 {'),
    ]:
        output = OUTPUT / name
        output.mkdir(parents=True, exist_ok=False)
        with tempfile.TemporaryDirectory(prefix='mee-p6-mutation-') as tmp:
            source = Path(tmp)
            shutil.copyfile(ROOT / 'moon.mod', source / 'moon.mod')
            shutil.copytree(ROOT / 'eventeval', source / 'eventeval')
            (source / '.tools').symlink_to(ROOT / '.tools', target_is_directory=True)
            path = source / 'eventeval/input.mbt'
            text = path.read_text()
            if text.count(old) != 1:
                raise ValueError('mutation anchor changed: ' + name)
            path.write_text(text.replace(old, new))
            result = subprocess.run(
                [ROOT / 'scripts/with-toolchain.sh', 'moon', 'test', 'eventeval',
                 '--target', 'native', '--deny-warn', '--filter', '*input_duplicate_keys*'],
                cwd=source, capture_output=True, timeout=120,
            )
            (output / 'stdout').write_bytes(result.stdout)
            (output / 'stderr').write_bytes(result.stderr)
            raw = (result.stdout + result.stderr).decode()
            protocol = re.search(r'Total tests: (\d+), passed: (\d+), failed: (\d+)', raw)
            killed = result.returncode != 0 and protocol is not None and int(protocol[1]) == 4 and int(protocol[3]) > 0
            row = dict(name=name, exit_code=result.returncode, compiled=protocol is not None,
                       failed_tests=int(protocol[3]) if protocol else None, killed=killed,
                       old=old,new=new)
            (output / 'receipt.json').write_text(json.dumps(row, indent=2) + '\n')
            rows.append(row)
    report = dict(passed=all(r['killed'] for r in rows), mutations=rows)
    (OUTPUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
