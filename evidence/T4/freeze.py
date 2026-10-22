"""Create once or verify the T4 immutable evidence manifest (stdlib only)."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
STAGE = ROOT / 'evidence/T4'
SHA = 'd00b0a62437056461510e85e4b2326d7cdf707b6'
MANIFEST = STAGE / 'manifest.json'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def verify(report):
    for name, expected in report['evidence_sha256'].items():
        assert digest((ROOT / name).read_bytes()) == expected, name
    for name, expected in report['tested_source_sha256'].items():
        data = subprocess.check_output(['git', 'show', f'{SHA}:{name}'], cwd=ROOT)
        assert digest(data) == expected, (SHA, name)
    for record in report['commands']:
        assert digest((ROOT / record['log']).read_bytes()) == record['log_sha256'], record['log']
    review = STAGE / 'independent-review'
    for row in json.loads((review / 'manifest.json').read_bytes())['files']:
        assert digest((review / row['path']).read_bytes()) == row['sha256'], row['path']
    final = json.loads((STAGE / 'renderers-verified/report.json').read_bytes())
    assert final['git_head'] == SHA and final['passed'] and final['process_runs'] == 430
    assert final['product_sha256'] == report['product_sha256']
    for name, expected in final['source_sha256'].items():
        assert report['tested_source_sha256'][name] == expected, name
    for row in final['cases']:
        raw = (STAGE / 'renderers-verified' / row['name'] / 'stdout').read_bytes()
        assert digest(raw) == row['stdout_sha256'], row['name']
    assert json.loads((STAGE / 'byte-mutations-verified/report.json').read_bytes())['passed']
    print(json.dumps(dict(passed=True, tested_sha=SHA,
                          evidence_files=len(report['evidence_sha256']), raw_processes=430)))


if '--create' in sys.argv:
    assert not MANIFEST.exists(), 'manifest already exists; do not overwrite frozen evidence'
    names = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', SHA], cwd=ROOT, text=True).splitlines()
    names = [n for n in names if n.startswith(('eventeval/', 'cmd/probe/', 'validation/'))
             or n in ['moon.mod', 'scripts/with-toolchain.sh']]
    source = {n: digest(subprocess.check_output(['git', 'show', f'{SHA}:{n}'], cwd=ROOT)) for n in names}
    commands = []
    for path in sorted(STAGE.glob('20*.json')):
        item = json.loads(path.read_bytes())
        assert 'log_sha256' in item and 'exit_code' in item, path
        commands.append(dict(record=str(path.relative_to(ROOT)), **item))
    files = {str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in sorted(STAGE.rglob('*'))
             if p.is_file() and p != MANIFEST and '__pycache__' not in p.parts}
    final = json.loads((STAGE / 'renderers-verified/report.json').read_bytes())
    report = dict(stage='T4', status='author fixed sole independent Important; no re-review',
                  base_sha='9886ce1d9c1390d298c9f34d77d7185ec3e4b043',
                  product_implementation_sha='d528d30b3e8b1feaea801c2058ec310206f78b65',
                  code_and_tested_sha=SHA, product_sha256=final['product_sha256'],
                  tests=dict(moon=49, prior_python=4, validation=29, renderer_processes=430,
                             old_json_raw_bytes=46, explanation_pairs=122, identity_cases=44,
                             prior_argv=56, prior_json_controls=64, negative_byte_controls=2),
                  review=dict(critical=0, important=1, minor=0, author_fixed=1, independent_re_review=False),
                  historical_warning='pre-fix text-mode renderer receipts do not establish raw-byte identity',
                  not_proven=['file CLI/demo', 'personal M2', 'final A11', 'complete resource I/O',
                              'universal memory/time performance', 'Linux/remote CI',
                              'package consumer/release/competition eligibility'],
                  commands=commands, tested_source_sha256=source, evidence_sha256=files)
    MANIFEST.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
else:
    report = json.loads(MANIFEST.read_bytes())
verify(report)
