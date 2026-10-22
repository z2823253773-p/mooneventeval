"""Create once / verify T5 immutable evidence and source bindings."""
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
STAGE = ROOT / 'evidence/T5'
MANIFEST = STAGE / 'manifest.json'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def verify(report):
    for name, expected in report['evidence_sha256'].items():
        assert digest((ROOT / name).read_bytes()) == expected, name
    sha = report['code_and_tested_sha']
    for name, expected in report['tested_source_sha256'].items():
        assert digest(subprocess.check_output(['git', 'show', f'{sha}:{name}'], cwd=ROOT)) == expected, name
    for row in report['commands']:
        assert digest((ROOT / row['log']).read_bytes()) == row['log_sha256'], row['log']
    review_root = STAGE / 'independent-review'
    for name, row in json.loads((review_root / 'SHA256SUMS.json').read_bytes()).items():
        assert digest((review_root / name).read_bytes()) == row['sha256'], name
    assert digest((review_root / 'review-evidence.tar.gz').read_bytes()) == 'ed7d6343ea0e0b1321a42ca75716156c98b8b483f7a2b125a78a5c3a854c83af'
    process = STAGE / 'process-final-verified'
    for path in process.glob('*/receipt.json'):
        row = json.loads(path.read_bytes())
        assert digest((path.parent / 'stdout').read_bytes()) == row['stdout_sha256'], path
        assert digest((path.parent / 'stderr').read_bytes()) == row['stderr_sha256'], path
    for path in process.rglob('*.gz'):
        gzip.decompress(path.read_bytes())  # Validate lossless fixture archive integrity.
    for folder, head_key, hash_key in [('process-final-verified/product.json', 'head', 'sha256'),
                                     ('cli-bytes-final-verified/report.json', 'git_head', 'product_sha256'),
                                     ('demo-final-verified/report.json', 'git_head', 'product_sha256')]:
        row = json.loads((STAGE / folder).read_bytes())
        assert row[head_key] == sha and row[hash_key] == report['product_sha256'], folder
    prior = ROOT / 'evidence/T3/parity-final'
    for row in json.loads((STAGE / 'cli-bytes-final-verified/report.json').read_bytes())['cases']:
        raw = (STAGE / 'cli-bytes-final-verified' / row['name'] / 'stdout').read_bytes()
        assert digest(raw) == row['stdout_sha256'] and raw == (prior / row['name'] / 'product.stdout').read_bytes(), row['name']
    demo = json.loads((STAGE / 'demo-final-verified/report.json').read_bytes())
    for row in demo['commands']:
        for stream in ['stdout', 'stderr']:
            assert digest((STAGE / 'demo-final-verified' / row['name'] / stream).read_bytes()) == row[stream + '_sha256'], row['name']
    assert demo['personal_explanation'] == 'NOT_PERFORMED'
    assert report['personal_explanation'] == 'NOT_PERFORMED'
    replay = json.loads((STAGE / 'review-replay-fixed/report.json').read_bytes())
    assert replay['git_head'] == sha and replay['passed'] == replay['cases'] == 42 and replay['failed'] == []
    assert replay['product_sha256'] == report['product_sha256'] and not replay['independent_re_review']
    print(json.dumps(dict(passed=True, tested_sha=sha, evidence_files=len(report['evidence_sha256']),
                          personal_explanation='NOT_PERFORMED')))


if '--create' in sys.argv:
    assert not MANIFEST.exists(), 'already frozen; do not overwrite'
    source = json.loads((STAGE / 'final-source.json').read_bytes())
    review = json.loads((STAGE / 'review-resolution.json').read_bytes())
    commands = []
    for path in sorted(STAGE.glob('20*.json')):
        row = json.loads(path.read_bytes())
        assert 'log_sha256' in row and 'exit_code' in row, path
        commands.append(dict(record=str(path.relative_to(ROOT)), **row))
    files = {str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in sorted(STAGE.rglob('*'))
             if p.is_file() and p != MANIFEST and '__pycache__' not in p.parts}
    report = dict(stage='T5 machine implementation/demo transcripts',
                  base_sha='41890b84505e790efef6c2f981512af04539a51e',
                  reviewed_candidate='1831fbc21199974b77c4a66675307d0071f88bb0',
                  code_and_tested_sha=source['git_head'], product_sha256=source['product_sha256'],
                  tested_source_sha256=source['source_sha256'],
                  tests=dict(moon=57, prior_python=4, validation=29, cli_unittests=10,
                             ordinary_cli_captures=45, broken_pipe_cases=2, old_report_bytes=46,
                             author_replay=42, demo_calls=10, native_fd_limit=64, repeated_reads=20000),
                  review=review, personal_explanation='NOT_PERFORMED',
                  commands=commands, evidence_sha256=files,
                  not_proven=['personal M2/spoken demo', 'injected EINTR/short-write/close failure',
                              'final A11', 'Linux/remote CI', 'package consumer/publishing/competition eligibility'])
    MANIFEST.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
else:
    report = json.loads(MANIFEST.read_bytes())
verify(report)
