"""Recheck preserved P8 local/CI receipts and bind source bytes to public Git."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import zipfile

STAGE = Path(__file__).resolve().parent
ROOT = STAGE.parents[1]
CODE = json.loads((STAGE / 'bindings.json').read_bytes())['public']
AUTHOR = json.loads((STAGE / 'bindings.json').read_bytes())['author']


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
    require([report[k] for k in ['moon_tests', 'python_tests', 'validation_tests', 'cli_tests']] == json.loads((STAGE / 'bindings.json').read_bytes())['counts'], 'test counts')
    for step in report['steps']:
        require(step['passed'] is True and step['exit_code'] == 0 and not step['timed_out'], 'failed gate')
        for stream in ['stdout', 'stderr']:
            require(digest(z.read(prefix + '/' + step['name'] + '/' + stream)) == step[stream + '_sha256'], 'gate stream')
    require(b'test_duplicate_keys_fail_in_both_commands_and_formats' in z.read(prefix + '/cli-tests/stderr'), 'new real CLI duplicate check not executed')
    require(b'test_import_then_evaluate_and_explain_without_conversion_script' in z.read(prefix + '/cli-tests/stderr'), 'TSV real CLI workflow not executed')
    index = json.loads(z.read(prefix + '/SHA256SUMS.json'))
    for path, sha in index.items():
        require(digest(z.read(prefix + '/' + path)) == sha, 'artifact digest: ' + path)
    require(b'test_documented_moonbit_consumer_runs_without_python_scoring' in z.read(prefix + '/python-tests/stderr'), 'new integration test not executed')
    parity = json.loads(z.read(prefix + '/parity/report.json'))
    require(parity['passed'] is True and not parity['unexplained'] and len(parity['cases']) == 324, 'qualification')
    require(report['qualification_product_calls'] == 1620 and parity['git_head'] == commit and parity['product_sha256'] == report['product_sha256'], 'qualification binding')
    package = json.loads(z.read(prefix + '/package-cases/report.json'))
    require(package['passed'] is True and len(package['members']) == 43, 'source package')
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

    return report


def main():
    for path, sha in read(STAGE / 'SHA256SUMS.json').items():
        require(digest((STAGE / path).read_bytes()) == sha, 'frozen stage: ' + path)
    run, jobs = read(STAGE / 'run.json'), read(STAGE / 'jobs.json')['jobs']
    require(run['head_sha'] == CODE and run['status'] == 'completed' and run['conclusion'] == 'success', 'CI run')
    require(len(jobs) == 2 and all(j['conclusion'] == 'success' for j in jobs), 'CI jobs')
    require(read(STAGE / 'repository.json')['private'] is False, 'repository visibility receipt')
    rows = []
    with archive('local.zip') as local, archive('remote.zip') as remote:
        inventory = json.loads(local.read('accepted/report.json'))['source_sha256']
        local_report, _ = check_gate(local, 'accepted', AUTHOR, inventory)
        require(check_demo(local, 'demo', inventory)['product_sha256'] == local_report['product_sha256'], 'local demo binary binding')
        for name, system, machine in [('verification-macos-15-arm64', 'Darwin', 'arm64'), ('verification-ubuntu-24.04-x86_64', 'Linux', 'x86_64')]:
            report, files = check_gate(remote, name, CODE, inventory)
            require(report['host']['system'] == system and report['host']['machine'] == machine, 'runner platform')
            require(report['remote_ci'] == 'CURRENT_JOB_ONLY', 'CI context')
            require(any(j['name'] == 'verify (' + ('macos-15' if system == 'Darwin' else 'ubuntu-24.04') + ', ' + machine + ')' for j in jobs), 'job identity')
            require(check_demo(remote, name + '/public-demo', inventory)['product_sha256'] == report['product_sha256'], 'CI demo binary binding')
            rows.append(dict(platform=system + '/' + machine, gates=17, artifact_files=files))
        for name, sha in inventory.items():
            require(digest(subprocess.check_output(['git', 'show', CODE + ':' + name], cwd=ROOT)) == sha, 'public Git source: ' + name)
    with archive('registry.zip') as registry, zipfile.ZipFile(STAGE/'release-0.1.0.zip') as release:
        result = json.loads(registry.read('report.json'))
        require(result['passed'] is True and result['module'] == 'z2823253773-p/mooneventeval' and result['version'] == '0.1.0', 'registry report')
        require(result['no_workspace'] is True and result['login_performed'] is False, 'registry isolation')
        require(digest(registry.read('registry-checker.py')) == result['checker_sha256'], 'actual checker source')
        require(result['installed_members'] == 43 and result['api_reports'] == 3 and result['tsv_and_duplicate_key'] is True and result['installed_cli_examples'] == 3, 'registry scope')
        require(digest((STAGE/'release-0.1.0.zip').read_bytes()) == result['archive_sha256'], 'release archive')
        names = release.namelist()
        require(len(names) == len(set(names)) == 43, 'release members')
        require(result['installed_member_sha256'] == {n:digest(release.read(n)) for n in names}, 'registry bytes')
        for n in names:
            require(digest(release.read(n)) == inventory[n], 'release/public source: '+n)
        require(len(result['steps']) == 7, 'registry commands')
        for row in result['steps']:
            require(row['exit_code'] == 0 and not row['timed_out'], 'registry command failed')
            for stream in ['stdout','stderr']:
                require(digest(registry.read(row['name']+'/'+stream)) == row[stream+'_sha256'], 'registry stream')
        require(b'Downloading z2823253773-p/mooneventeval@0.1.0' in registry.read('add/stderr'), 'network installation not observed')
        api = [json.loads(x) for x in registry.read('run-api/stdout').splitlines()]
        require(len(api) == 3 and api[0]['summary']['counts'] == dict(reference=1,prediction=2,tp=1,fp=1,fn=0), 'installed evaluation')
        require(api[1]['basis']['eligible'] is True and api[2]['error']['code']=='INVALID_TYPE', 'installed explanation/error')
        require(json.loads(registry.read('run-tsv-and-duplicate-key/stdout'))['summary']['counts'] == dict(reference=1,prediction=2,tp=1,fp=1,fn=0), 'installed TSV')
        for n,c in [('duplicate',(1,1,0)),('greedy-trap',(2,0,0)),('boundary',(1,0,0))]:
            actual=json.loads(registry.read('cli-'+n+'/stdout'))['summary']['counts']
            require(tuple(actual[k] for k in ['tp','fp','fn']) == c, 'installed CLI')
    published = read(STAGE/'publish.json')
    require(published['exit_code'] == 0 and published['server_status'] == '200 OK' and published['credential_link_removed'] is True, 'publish receipt')
    with archive('registry.zip') as registry:
        for stream in ['stdout','stderr']:
            require(digest(registry.read('publish/'+stream)) == published[stream+'_sha256'], 'publishing stream')
        require(b'Server status: 200 OK' in registry.read('publish/stdout')+registry.read('publish/stderr'), 'server did not confirm')
        require(registry.read('registry-client-login-state.txt').strip() == b'Not logged in', 'client login state')
        require(digest(registry.read('registry-page.html')) == read(STAGE/'registry-page.json')['html_sha256'], 'public page bytes')

    tags = dict(line.split()[::-1] for line in (STAGE/'release-tag.txt').read_text().splitlines())
    require(tags.get('refs/tags/v0.1.0^{}') == CODE, 'public release tag')
    page = read(STAGE/'registry-page.json')
    require(page['http_status'] == 200 and page['identity_found'] is True and page['version_found'] is True, 'public package page')
    with archive('metadata.zip') as metadata:
        package = json.loads(metadata.read('package/report.json'))
        require(package['passed'] is True and len(package['members']) == 43, 'post-release docs package')
        require(digest(metadata.read('package/'+package['archive'])) == package['archive_sha256'], 'post-release docs archive')
    print(json.dumps(dict(passed=True,stage='P8' ,run_id=run['id'],tested_public_sha=CODE,source_files=len(inventory),jobs=rows,registry_published=True,installed_members=43)))


if __name__ == '__main__':
    main()
