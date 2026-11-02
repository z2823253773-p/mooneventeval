"""Recheck preserved P5 local/CI receipts and bind source bytes to public Git."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import zipfile

STAGE = Path(__file__).resolve().parent
ROOT = STAGE.parents[1]
CODE = 'b06207ae936e4179064ba4ccf7941cac61773f6e'
AUTHOR = 'f75963024b584e232114024cb2d83018cfb1f037'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_bytes())


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def archive(name):
    row = read(STAGE / 'archives.json')[name]
    path = STAGE / name
    require(path.stat().st_size == row['bytes'] and digest(path.read_bytes()) == row['sha256'], name)
    result = zipfile.ZipFile(path)
    infos = result.infolist()
    require(len(infos) == row['files'] == len(set(result.namelist())), 'archive file count: ' + name)
    require(sum(i.file_size for i in infos) < 2 * 1024**3, 'archive size: ' + name)
    for info in infos:
        p = PurePosixPath(info.filename)
        require(not p.is_absolute() and '..' not in p.parts and '\\' not in info.filename, 'unsafe archive path')
        require(((info.external_attr >> 16) & 0o170000) != 0o120000, 'archive symlink')
    require(result.testzip() is None, 'archive CRC: ' + name)
    return result


def check_gate(z, prefix, commit, inventory):
    report = json.loads(z.read(prefix + '/report.json'))
    require(report['passed'] is True and report['git_head'] == commit and report['source_unchanged'] is True, prefix)
    require(report['source_sha256'] == inventory, 'source inventory: ' + prefix)
    require(len(report['steps']) == len(report['required_steps']) == 17, 'gate count')
    require([s['name'] for s in report['steps']] == report['required_steps'], 'gate ordering')
    require([report[k] for k in ['moon_tests', 'python_tests', 'validation_tests', 'cli_tests']] == [58, 29, 42, 15], 'test counts')
    for step in report['steps']:
        require(step['passed'] is True and step['exit_code'] == 0 and not step['timed_out'], 'failed gate')
        for stream in ['stdout', 'stderr']:
            require(digest(z.read(prefix + '/' + step['name'] + '/' + stream)) == step[stream + '_sha256'], 'gate stream')
    index = json.loads(z.read(prefix + '/SHA256SUMS.json'))
    for path, sha in index.items():
        require(digest(z.read(prefix + '/' + path)) == sha, 'artifact digest: ' + path)
    require(b'test_documented_moonbit_consumer_runs_without_python_scoring' in z.read(prefix + '/python-tests/stderr'), 'new integration test not executed')
    parity = json.loads(z.read(prefix + '/parity/report.json'))
    require(parity['passed'] is True and not parity['unexplained'] and len(parity['cases']) == 324, 'qualification')
    require(report['qualification_product_calls'] == 1620 and parity['git_head'] == commit and parity['product_sha256'] == report['product_sha256'], 'qualification binding')
    package = json.loads(z.read(prefix + '/package-cases/report.json'))
    require(package['passed'] is True and len(package['members']) == 38, 'source package')
    require(digest(z.read(prefix + '/package-cases/' + package['archive'])) == package['archive_sha256'], 'package digest')
    return report, len(index)


def check_demo(z, prefix, inventory):
    report = json.loads(z.read(prefix + '/report.json'))
    require(report['passed'] is True and report['reference_checked'] is True and report['mode'] == 'check', 'demo status')
    require((report['product_calls'], report['reference_calls'], len(report['receipts'])) == (13, 4, 17), 'demo counts')
    for receipt in report['receipts']:
        snapshot = receipt['snapshot']
        product = snapshot.startswith('demo/output/')
        require(product or snapshot.startswith('demo/reference/'), 'unknown snapshot')
        leaf = ('product-' if product else 'reference-') + PurePosixPath(snapshot).name
        require(receipt['exit_code'] == 0, 'demo exit')
        for stream in ['stdout', 'stderr']:
            raw = z.read(prefix + '/' + leaf + '.' + stream)
            require(digest(raw) == receipt[stream + '_sha256'], 'demo stream')
            if stream == 'stdout':
                require(digest(raw) == inventory[snapshot], 'snapshot mismatch')
            elif product:
                require(raw == b'', 'product stderr')


def main():
    for path, sha in read(STAGE / 'SHA256SUMS.json').items():
        require(digest((STAGE / path).read_bytes()) == sha, 'frozen stage: ' + path)
    run, jobs = read(STAGE / 'run.json'), read(STAGE / 'jobs.json')['jobs']
    require(run['head_sha'] == CODE and run['status'] == 'completed' and run['conclusion'] == 'success', 'CI run')
    require(len(jobs) == 2 and all(j['conclusion'] == 'success' for j in jobs), 'CI jobs')
    require(read(STAGE / 'repository.json')['private'] is False, 'repository visibility receipt')
    rows = []
    with archive('local.zip') as local, archive('remote.zip') as remote:
        inventory = json.loads(local.read('local-final/report.json'))['source_sha256']
        check_gate(local, 'local-final', AUTHOR, inventory)
        check_demo(local, 'demo', inventory)
        require(json.loads(local.read('review-fix/report.json'))['passed'] is True, 'cold clone restoration')
        require(json.loads(local.read('runtime-no-python/report.json'))['passed'] is True, 'native runtime')
        for name, system, machine in [('verification-macos-14-arm64', 'Darwin', 'arm64'), ('verification-ubuntu-24.04-x86_64', 'Linux', 'x86_64')]:
            report, files = check_gate(remote, name, CODE, inventory)
            require(report['host']['system'] == system and report['host']['machine'] == machine, 'runner platform')
            require(report['remote_ci'] == 'CURRENT_JOB_ONLY', 'CI context')
            require(any(j['name'] == 'verify (' + ('macos-14' if system == 'Darwin' else 'ubuntu-24.04') + ', ' + machine + ')' for j in jobs), 'job identity')
            check_demo(remote, name + '/public-demo', inventory)
            rows.append(dict(platform=system + '/' + machine, gates=17, artifact_files=files))
        for name, sha in inventory.items():
            require(digest(subprocess.check_output(['git', 'show', CODE + ':' + name], cwd=ROOT)) == sha, 'public Git source: ' + name)
    with archive('metadata.zip') as metadata:
        package = json.loads(metadata.read('package/report.json'))
        require(package['passed'] is True and len(package['members']) == 38, 'metadata-only source package')
        require(digest(metadata.read('package/' + package['archive'])) == package['archive_sha256'], 'metadata package digest')
    print(json.dumps(dict(passed=True,stage='P5',run_id=run['id'],tested_public_sha=CODE,source_files=len(inventory),jobs=rows,registry_published=False)))


if __name__ == '__main__':
    main()
