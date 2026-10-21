"""Build then directly execute the locked native release whitebox artifact.

Times are process wall times, including graph construction, assertions and test
protocol; they exclude compilation and are not isolated matching-call timings.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import statistics
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]


def run_native(executable: Path, argument: str, raw_log: Path):
    command = [str(executable), argument]
    started = time.perf_counter()
    run = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=30)
    elapsed = time.perf_counter() - started
    raw_log.write_text(run.stdout + run.stderr)
    if run.returncode:
        raise RuntimeError(f"native process failed: {run.returncode}; {raw_log}")
    records = [json.loads(line) for line in run.stdout.splitlines() if line.startswith('{')]
    # Native MoonBit's driver can return process status 0 even on a failed test.
    results = [row for row in records if row.get('type') == 'result']
    if len(results) != 1 or results[0]['message'] != '':
        raise RuntimeError(f"native test protocol failed: {results}; {raw_log}")
    return records, {"command": command, "exit_code": run.returncode,
                     "elapsed_seconds": elapsed, "log": str(raw_log.relative_to(ROOT))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    command = [str(ROOT / 'scripts/with-toolchain.sh'), 'moon', 'test', 'eventeval',
               '--target', 'native', '--release', '--deny-warn', '--build-only']
    build = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=120)
    (output / 'native-release-build.log').write_text(build.stdout + build.stderr)
    if build.returncode:
        raise RuntimeError(f"release build failed: {build.returncode}")
    artifact = ROOT / '_build/native/release/test/eventeval/eventeval.whitebox_test.exe'
    metadata = json.loads((artifact.parent / '__whitebox_test_info.json').read_text())['tests']
    oracle_tests = metadata['matching_oracle_generated_wbtest.mbt']
    assert len(oracle_tests) == 1
    index = oracle_tests[0]['index']
    rows, audit_run = run_native(artifact,
        f'matching_oracle_generated_wbtest.mbt:{index}-{index + 1}',
        output / 'release-graph-audit.log')
    actual = [row for row in rows if 'case' in row]
    fixture = json.loads((ROOT / 'evidence/T2/graph-oracle-cases.json').read_text())
    expected = {row['id']: row for row in fixture['cases']}
    assert len(actual) == len(expected) == len({row['case'] for row in actual})
    for row in actual:
        case = expected[row['case']]
        pairs = row['pairs']
        assert len(pairs) == case['expected'], row
        assert len({r for r, _ in pairs}) == len(pairs), row
        assert len({p for _, p in pairs}) == len(pairs), row
        assert pairs == sorted(pairs), row
        assert all(p in case['adjacency'][r] for r, p in pairs), row
    (output / 'graph-oracle-actual.json').write_text(json.dumps(actual, indent=2) + '\n')
    benchmarks = []
    for test in metadata['matching_benchmark_wbtest.mbt']:
        index = test['index']
        argument = f'matching_benchmark_wbtest.mbt:{index}-{index + 1}'
        samples = []
        for iteration in range(6):  # One warmup followed by five fresh processes.
            rows, sample = run_native(artifact, argument,
                output / f'{test["name"]}-{iteration}.log')
            data = [row for row in rows if 'benchmark' in row]
            assert len(data) == 1 and data[0]['steps'] <= 20_000_000
            assert data[0]['pairs'] == data[0]['size_each_side']
            sample['measurement'] = data[0]
            sample['warmup'] = iteration == 0
            samples.append(sample)
        assert all(row['measurement'] == samples[0]['measurement'] for row in samples)
        benchmarks.append({"name": test['name'], "samples": samples,
            "median_seconds": statistics.median(row['elapsed_seconds'] for row in samples[1:])})
    sources = sorted((ROOT / 'eventeval').glob('*.mbt')) + [
        ROOT / 'moon.mod', ROOT / 'eventeval/moon.pkg', ROOT / 'docs/toolchain.lock.json',
        ROOT / 'scripts/with-toolchain.sh', Path(__file__)]
    report = {
        "utc": datetime.now(timezone.utc).isoformat(),
        "platform": platform.platform(), "machine": platform.machine(),
        "git_head": subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        "artifact": str(artifact.relative_to(ROOT)),
        "artifact_sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
        "build_command": command, "build_exit_code": build.returncode,
        "timing_scope": "fresh native process including graph construction/assertions/protocol; excludes compilation; not isolated matcher time",
        "graph_audit": {"cases": len(actual), "run": audit_run},
        "benchmarks": benchmarks,
    }
    (output / 'native-matching-report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({"graph_cases": len(actual), "benchmarks": [
        {**row['samples'][0]['measurement'], 'median_seconds': row['median_seconds']}
        for row in benchmarks]}, indent=2))


if __name__ == '__main__':
    main()
