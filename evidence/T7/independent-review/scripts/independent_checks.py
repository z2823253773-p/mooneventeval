#!/usr/bin/env python3
"""Fresh archive/docs checks independent of the candidate's T7 check functions."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import sys
import zipfile
from run_checks import AUDIT, SOURCE, CONTEXT, record

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def require_zero(receipt):
    assert receipt['exit_code'] == 0, receipt

def main():
    package = AUDIT/'results/package/local-mooneventeval-0.1.0.zip'
    extracted = AUDIT/'manual-unpacked'
    extracted.mkdir()
    prior = json.loads((AUDIT/'candidate-source.json').read_text())['sha256']
    members = []
    with zipfile.ZipFile(package) as archive:
        for info in archive.infolist():
            raw = archive.read(info)
            digest = hashlib.sha256(raw).hexdigest()
            assert digest == prior[info.filename], info.filename
            path = extracted/info.filename
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
            path.chmod((info.external_attr >> 16) & 0o777)
            members.append(dict(name=info.filename, sha256=digest, mode=oct(path.stat().st_mode & 0o777)))
    assert len(members) == 38
    lock = json.loads((extracted/'docs/toolchain.lock.json').read_text())
    installed = Path(CONTEXT['original'])/'.tools/moonbit'/lock['version']
    (extracted/'.tools/moonbit').mkdir(parents=True)
    (extracted/'.tools/moonbit'/lock['version']).symlink_to(installed, target_is_directory=True)
    notices = {}
    for name in ['LICENSE', 'NOTICE']:
        supplied = extracted/('LICENSES/moonbit-core-'+name)
        upstream = installed/'lib/core'/name
        assert supplied.read_bytes() == upstream.read_bytes()
        notices[name] = dict(source=str(upstream), sha256=sha(supplied))
    wrapper = extracted/'scripts/with-toolchain.sh'
    require_zero(record('locked-moon-version', [wrapper,'moon','version'], extracted))
    require_zero(record('locked-moonc-version', [wrapper,'moonc','-v'], extracted))
    consumer = AUDIT/'manual-consumer'
    (consumer/'main').mkdir(parents=True)
    api = (extracted/'docs/API.md').read_text()
    (consumer/'moon.mod').write_text(re.search(r'```text\n(.*?)```', api, re.S).group(1))
    (consumer/'main/main.mbt').write_text(re.search(r'```moonbit\n(.*?)```', api, re.S).group(1))
    (consumer/'main/moon.pkg').write_text('import { "local/mooneventeval/eventeval" }\npkgtype(kind: "executable")\n')
    (consumer/'moon.work').write_text('members = '+json.dumps([str(consumer), str(extracted)])+'\n')
    quarantine = AUDIT/'quarantined-original-copy'
    quarantine.mkdir()
    moved = []
    try:
        # Make the copied original product source unavailable: any fallback is an error.
        for name in ['eventeval', 'cli', 'cmd']:
            shutil.move(SOURCE/name, quarantine/name)
            moved.append(name)
        require_zero(record('independent-consumer-build', [wrapper,'moon','build','main','--target','native','--release','--deny-warn','--target-dir',consumer/'_build'], consumer))
        binaries = list((consumer/'_build').rglob('main.exe'))
        assert len(binaries) == 1, binaries
        require_zero(record('independent-consumer-run', [binaries[0]], consumer))
        raw = (AUDIT/'evidence/independent-consumer-run/stdout').read_bytes()
        report = json.loads(raw)
        assert raw.endswith(b'\n') and not raw.endswith(b'\n\n')
        assert report['status'] == 'completed'
        assert report['summary']['counts'] == dict(reference=1, prediction=2, tp=1, fp=1, fn=0)
        assert len(report['matches']) == 1
        require_zero(record('independent-cli-build', [wrapper,'moon','build','cmd/mooneventeval','--target','native','--release','--deny-warn'], extracted))
        binary = extracted/'_build/native/release/build/cmd/mooneventeval/mooneventeval.exe'
        readme_commands = re.findall(r'^_build/[^\n]+', (extracted/'README.md').read_text(), re.M)
        assert len(readme_commands) == 6, readme_commands
        expectations = {'duplicate':(1,1,0), 'greedy-trap':(2,0,0), 'boundary':(1,0,0)}
        for index, line in enumerate(readme_commands):
            args = line.split()
            require_zero(record('literal-readme-'+str(index+1), [str(extracted/args[0]), *args[1:]], extracted))
            folder = AUDIT/'evidence'/('literal-readme-'+str(index+1))
            assert (folder/'stderr').read_bytes() == b''
            raw = (folder/'stdout').read_bytes()
            assert raw.endswith(b'\n') and not raw.endswith(b'\n\n')
            if args[1] == '--help': assert b'evaluate' in raw and b'explain-pair' in raw
            elif args[1] == '--version': assert raw == b'MoonEventEval 0.1.0\n'
            elif args[1] == 'evaluate':
                row = json.loads(raw)
                counts = row['summary']['counts']
                assert row['status'] == 'completed'
                assert tuple(counts[key] for key in ['tp','fp','fn']) == expectations[Path(args[2]).stem]
                assert all(type(value) is int for value in counts.values())
            else:
                row = json.loads(raw)
                assert row['status'] == 'completed' and row['basis']['eligible'] is True
                assert row['reference']['id'] == 'r1' and row['prediction']['id'] == 'p1'
        require_zero(record('documented-text-explanation', [binary,'explain-pair','examples/boundary.json','--recording','clip-01','--reference','r1','--prediction','p1','--format','text'], extracted))
        empty = AUDIT/'empty.json'
        empty.write_text(json.dumps(dict(schema_version=1, labels=['alarm'], config=dict(collar_s='0.2', offset_ratio='0.5'), recordings=[])))
        require_zero(record('documented-empty-metrics', [binary,'evaluate',empty,'--format','json'], extracted))
        summary = json.loads((AUDIT/'evidence/documented-empty-metrics/stdout').read_bytes())['summary']
        assert all(summary[key] is None for key in ['precision','recall','f1'])
        malformed = AUDIT/'invalid.json'; malformed.write_bytes(b'{')
        error_receipt = record('documented-invalid-json', [binary,'evaluate',malformed,'--format','json'], extracted)
        assert error_receipt['exit_code'] == 2
        error = json.loads((AUDIT/'evidence/documented-invalid-json/stdout').read_bytes())
        assert error['status'] == 'failed' and 'summary' not in error
        assert (AUDIT/'evidence/documented-invalid-json/stderr').read_bytes() == b''
    finally:
        for name in moved: shutil.move(quarantine/name, SOURCE/name)
    require_zero(record('validation-tests', ['env','PYTHONDONTWRITEBYTECODE=1',SOURCE/'.venv-reference/bin/python','-W','error::ResourceWarning','-m','unittest','discover','-s','validation/tests','-v']))
    require_zero(record('real-cli-tests', ['env','PYTHONDONTWRITEBYTECODE=1','MEE_BIN='+str(binary),'MEE_EVIDENCE='+str(AUDIT/'results/cli-tests'),'python3','-W','error::ResourceWarning','-m','unittest','discover','-s','tests/cli','-v']))
    (AUDIT/'independent.json').write_text(json.dumps(dict(passed=True, archive=str(package), archive_sha256=sha(package), members=members, notices=notices, copied_source_quarantined_during_build=True, consumer=str(consumer), unpacked=str(extracted), product_sha256=sha(binary)), indent=2)+'\n')
    print('independent archive, literal documentation, API, error/empty and regression checks passed')

if __name__ == '__main__': main()
