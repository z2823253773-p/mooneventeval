"""Build or verify T2's durable evidence manifest from the repository root."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / 'evidence/T2/manifest.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.check:
        manifest = json.loads(MANIFEST.read_text())
        for name, expected in manifest['files_sha256'].items():
            assert digest(ROOT / name) == expected, name
        for record in manifest['commands']:
            assert digest(ROOT / record['log']) == record['log_sha256'], record['log']
        print(json.dumps({'verified_files': len(manifest['files_sha256']),
                          'verified_commands': len(manifest['commands']), 'all_match': True}))
        return
    commands = []
    for path in sorted((ROOT / 'evidence/T2').glob('20*.json')):
        record = json.loads(path.read_text())
        assert digest(ROOT / record['log']) == record['log_sha256'], path
        commands.append({'record': str(path.relative_to(ROOT)), **record})
    native = json.loads((ROOT / 'evidence/T2/native-committed/native-matching-report.json').read_text())
    code_sha = 'e96d130338ab379968a5cb4624788ba079dadda9'
    assert native['git_head'] == code_sha
    for name, expected in native['source_sha256'].items():
        assert digest(ROOT / name) == expected, name
    fixtures = json.loads((ROOT / 'evidence/T2/graph-oracle-cases.json').read_text())
    assert len(fixtures['cases']) == 753
    files = sorted(path for path in (ROOT / 'evidence/T2').rglob('*')
                   if path.is_file() and path != MANIFEST and '__pycache__' not in path.parts)
    files += [ROOT / path for path in ['docs/contracts.md', 'docs/PROJECT_STATE.md',
              'docs/reviews/2026-10-21-t2-results.md', 'docs/reviews/2026-10-21-t2-review.md',
              'docs/superpowers/plans/tasks/T2-matching.md']]
    report = {
        'stage': 'T2', 'status': 'PASS; independent read-only review accepted',
        'base_sha': 'bb23267ac56f040f17797106a36659bed1613cd8',
        'code_and_tested_sha': code_sha,
        'strategy': 'first-free-iterative-dfs/v1',
        'moonbit_tests': {'passed': 25, 'failed': 0},
        'prior_python_tests': {'passed': 4, 'failed': 0},
        'validation_tests': {'passed': 15, 'failed': 0},
        'graph_cases': {'all_graphs_each_side_0_to_3': 689, 'seeded_each_side_4_to_7': 64,
                        'seed': 20261020, 'actual_pairs_saved': 753},
        'generator_sha256': fixtures['generator_sha256'],
        'native_report': 'evidence/T2/native-committed/native-matching-report.json',
        'native_steps': {row['samples'][0]['measurement']['benchmark']:
                         row['samples'][0]['measurement']['steps'] for row in native['benchmarks']},
        'mutation_report': 'evidence/T2/mutations/report.json',
        'review': {'report': 'docs/reviews/2026-10-21-t2-review.md',
                   'receipt': 'evidence/T2/independent-review/REVIEW_RECEIPT.md',
                   'critical': 0, 'important': 0, 'minor': 0,
                   'fresh_runs': 'MoonBit25/25, graph oracle6/6, Hall753, native753+fourbench, regeneration, two mutations',
                   'log_only': 'prior Python4/4 and full validation15/15'},
        'failure_interpretation': {
            'matching-red': 'missing target matching API, expected RED',
            'oracle-red': 'missing target graph oracle module, expected RED',
            'matching-first-green': 'implementation diagnostics: struct-never-constructed and deprecated tuple Show; repaired, not a passing run',
            'mutation logs': 'intentional behavioral failures after passing controls; not compiler errors'},
        'not_proven': ['public JSON task/schema/report', 'end-to-end raw input reordering',
                       'product sed_eval parity/M2/A11', 'all legal graphs under20M',
                       'Linux/remote CI', 'CLI/demo', 'package consumer/publishing'],
        'commands': commands,
        'files_sha256': {str(path.relative_to(ROOT)): digest(path) for path in files},
    }
    MANIFEST.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'manifest': str(MANIFEST.relative_to(ROOT)),
                      'files': len(files), 'commands': len(commands), 'tested_sha': code_sha}))


if __name__ == '__main__':
    main()
