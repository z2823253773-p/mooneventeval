"""Run the actual native I/O whitebox executable with only 64 file descriptors."""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); output = args.output.resolve(); output.mkdir(parents=True, exist_ok=True)
    build = [str(ROOT / 'scripts/with-toolchain.sh'), 'moon', 'test', 'cmd/mooneventeval',
             '--target', 'native', '--release', '--deny-warn', '--build-only']
    result = subprocess.run(build, cwd=ROOT, capture_output=True, timeout=120)
    (output / 'build.stdout').write_bytes(result.stdout); (output / 'build.stderr').write_bytes(result.stderr)
    assert result.returncode == 0, result.stderr
    exe = ROOT / '_build/native/release/test/cmd/mooneventeval/mooneventeval.whitebox_test.exe'
    tests = json.loads((exe.parent / '__whitebox_test_info.json').read_bytes())['tests']['native_io_wbtest.mbt']
    rows = []
    def limit_descriptors():
        resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
    for test in tests:
        i = test['index']; command = [str(exe), f'native_io_wbtest.mbt:{i}-{i+1}']
        result = subprocess.run(command, cwd=ROOT, capture_output=True, preexec_fn=limit_descriptors, timeout=30)
        (output / f'{i}.stdout').write_bytes(result.stdout); (output / f'{i}.stderr').write_bytes(result.stderr)
        records = [json.loads(line) for line in result.stdout.splitlines() if line.startswith(b'{')]
        results = [r for r in records if r.get('type') == 'result']
        assert result.returncode == 0 and not result.stderr and len(results) == 1 and results[0]['message'] == '', (test, result.returncode, result.stdout, result.stderr)
        rows.append(dict(name=test['name'], command=command, exit_code=result.returncode,
                         test_protocol_passed=True, stdout_sha256=hashlib.sha256(result.stdout).hexdigest()))
    report = dict(passed=True, descriptor_limit=64, repeated_opens=20000, tests=rows,
                  executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),
                  scope='native NUL/directory/repeated close and invalid-fd write; not injected EINTR/short write/close failure')
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(passed=True, descriptor_limit=64, tests=len(rows))))


if __name__ == '__main__':
    main()
