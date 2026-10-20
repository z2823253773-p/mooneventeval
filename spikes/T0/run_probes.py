"""Execute throwaway experiments; retain commands, output, hashes and outcomes."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

REPO = Path(__file__).resolve().parents[2]
STAGE = REPO/'evidence/T0'
STAMP = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
OUTPUT = STAGE/STAMP
OUTPUT.mkdir(parents=True)
TOOL = REPO/'.tools/moonbit/0.10.14+7d59c7ec9'
ENV = dict(os.environ, MOON_HOME=str(TOOL), PATH=str(TOOL/'bin')+os.pathsep+os.environ['PATH'])
RESULTS = []

def run(name, arguments, cwd=None, expected=0, observation=False):
    cwd = cwd or REPO
    log = OUTPUT/(name+'.log')
    with log.open('wb') as stream:
        try:
            child = subprocess.run(arguments, cwd=cwd, env=ENV, stdout=stream, stderr=subprocess.STDOUT, timeout=120)
            code = child.returncode
        except subprocess.TimeoutExpired:
            code = 124
    okay = code == expected if isinstance(expected, int) else code in expected
    row = {'name': name, 'command': [str(x) for x in arguments], 'cwd': str(cwd.relative_to(REPO)),
           'exit_code': code, 'expected_exit': expected, 'observation_only': observation,
           'pass': okay, 'log': str(log.relative_to(REPO)),
           'log_sha256': hashlib.sha256(log.read_bytes()).hexdigest()}
    RESULTS.append(row)
    print(json.dumps(row), flush=True)
    return code, log

if __name__ == '__main__':
    # Resolve script directory independently of CWD.
    PROBES = Path(__file__).resolve().parent
    run('versions', ['moon', 'version', '--all'])
    run('compiler', ['moonc', '-v'])
    RESULTS[-1]['pass'] &= (REPO/RESULTS[-1]['log']).read_text().startswith('v0.10.14+7d59c7ec9 ')
    run('field-old', ['moon', '-C', str(PROBES/'field_old'), 'test', '--target', 'native', '--deny-warn'], expected=[1, 255])
    RESULTS[-1]['pass'] &= 'The type Counts has no field fn.' in (REPO/RESULTS[-1]['log']).read_text()
    for case in ['field_new', 'inspect_plain', 'modern', 'json']:
        run(case, ['moon', '-C', str(PROBES/case), 'test', '--target', 'native', '--deny-warn'])
    # Compatibility observations, not positive acceptance gates.
    for case in ['inspect_bang', 'legacy']:
        run(case, ['moon', '-C', str(PROBES/case), 'test', '--target', 'native', '--deny-warn'], expected=[0, 1, 255], observation=True)
    code, _ = run('native-build', ['moon', '-C', str(PROBES/'native'), 'build', '--target', 'native', '--deny-warn'])
    if code == 0:
        build_root = PROBES/'native/_build/native/debug/build'
        executables = [path for path in build_root.glob('*.exe') if path.is_file()]
        if len(executables) == 1:
            code, log = run('native-process', [str(executables[0])], cwd=PROBES/'native', expected=7)
            RESULTS[-1]['stdout_exact'] = log.read_bytes() == b'T0\n'
            RESULTS[-1]['pass'] &= RESULTS[-1]['stdout_exact']
            RESULTS[-1]['binary_sha256'] = hashlib.sha256(executables[0].read_bytes()).hexdigest()
        else:
            RESULTS.append({'name': 'native-process', 'pass': False, 'reason': 'ambiguous/missing executable', 'paths': list(map(str, executables))})
    run('package-help', ['moon', 'package', '--help'])
    run('package-list', ['moon', '-C', str(PROBES/'modern'), 'package', '--list', '--frozen'])
    run('package', ['moon', '-C', str(PROBES/'modern'), 'package'])
    run('package-artifact', [sys.executable, str(PROBES/'check_package.py'), str(OUTPUT)])
    report = {'baseline_sha': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip(),
              'scope': 'T0 macOS arm64 throwaway probes only', 'results': RESULTS,
              'source_sha256': {str(path.relative_to(REPO)): hashlib.sha256(path.read_bytes()).hexdigest()
                                for path in sorted(PROBES.rglob('*'))
                                if path.is_file() and '_build' not in path.parts and '__pycache__' not in path.parts},
              'all_required_pass': all(r['pass'] for r in RESULTS if not r.get('observation_only'))}
    (OUTPUT/'results.json').write_text(json.dumps(report, indent=2)+'\n')
    print('RESULTS '+str(OUTPUT/'results.json'))
    raise SystemExit(0 if report['all_required_pass'] else 1)
