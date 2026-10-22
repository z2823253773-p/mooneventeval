"""Author replay of the unchanged reviewer's 42-case script; not a re-review."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args(); output = args.output.resolve(); output.mkdir(parents=True, exist_ok=True)
assert not list(output.iterdir()), 'use a fresh evidence directory'
exe = ROOT / '_build/native/release/build/cmd/mooneventeval/mooneventeval.exe'
original = ROOT / 'evidence/T5/independent-review/extra_checks.py'
with tempfile.TemporaryDirectory(prefix='mee-t5-author-replay-') as tmp:
    work = Path(tmp) / 'checkout'; work.mkdir()
    shutil.copytree(ROOT / 'examples', work / 'examples')
    linked = work / '_build/native/release/build/cmd/mooneventeval/mooneventeval.exe'
    linked.parent.mkdir(parents=True); linked.symlink_to(exe)
    script = Path(tmp) / 'extra_checks.py'; shutil.copy2(original, script)
    assert script.read_bytes() == original.read_bytes()
    result = subprocess.run([sys.executable, str(script)], capture_output=True, timeout=120)
    (output / 'runner.stdout').write_bytes(result.stdout); (output / 'runner.stderr').write_bytes(result.stderr)
    assert result.returncode == 0, result.stderr
    shutil.copytree(Path(tmp) / 'extra', output / 'extra')
    report = json.loads((output / 'extra/report.json').read_bytes())
    assert report['cases'] == report['passed'] == 42 and report['failed'] == [], report
    report.update(author_replay=True, independent_re_review=False,
                  git_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                  reviewer_script_sha256=hashlib.sha256(script.read_bytes()).hexdigest(),
                  product_sha256=hashlib.sha256(exe.read_bytes()).hexdigest())
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))
