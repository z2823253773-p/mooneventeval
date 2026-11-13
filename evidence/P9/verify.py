"""Recheck preserved P9 local/CI receipts and bind source bytes to public Git."""
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
    report = json.loads(z.read((prefix + '/' if prefix else '') + 'report.json'))
    require(report['passed'] is True and report['git_head'] == commit and report['source_unchanged'] is True, prefix)
    require(report['source_sha256'] == inventory, 'source inventory: ' + prefix)
    require(len(report['steps']) == len(report['required_steps']) == 17, 'gate count')
    require([s['name'] for s in report['steps']] == report['required_steps'], 'gate ordering')
    require([report[k] for k in ['moon_tests', 'python_tests', 'validation_tests', 'cli_tests']] == json.loads((STAGE / 'bindings.json').read_bytes())['counts'], 'test counts')
    for step in report['steps']:
        require(step['passed'] is True and step['exit_code'] == 0 and not step['timed_out'], 'failed gate')
        for stream in ['stdout', 'stderr']:
            require(digest(z.read((prefix + '/' if prefix else '') + '' + step['name'] + '/' + stream)) == step[stream + '_sha256'], 'gate stream')
    require(b'test_duplicate_keys_fail_in_both_commands_and_formats' in z.read((prefix + '/' if prefix else '') + 'cli-tests/stderr'), 'new real CLI duplicate check not executed')
    require(b'test_import_then_evaluate_and_explain_without_conversion_script' in z.read((prefix + '/' if prefix else '') + 'cli-tests/stderr'), 'TSV real CLI workflow not executed')
    index = json.loads(z.read((prefix + '/' if prefix else '') + 'SHA256SUMS.json'))
    for path, sha in index.items():
        require(digest(z.read((prefix + '/' if prefix else '') + '' + path)) == sha, 'artifact digest: ' + path)
    require(b'test_documented_moonbit_consumer_runs_without_python_scoring' in z.read((prefix + '/' if prefix else '') + 'python-tests/stderr'), 'new integration test not executed')
    parity = json.loads(z.read((prefix + '/' if prefix else '') + 'parity/report.json'))
    require(parity['passed'] is True and not parity['unexplained'] and len(parity['cases']) == 324, 'qualification')
    require(report['qualification_product_calls'] == 1620 and parity['git_head'] == commit and parity['product_sha256'] == report['product_sha256'], 'qualification binding')
    package = json.loads(z.read((prefix + '/' if prefix else '') + 'package-cases/report.json'))
    require(package['passed'] is True and len(package['members']) == 43, 'source package')
    require(digest(z.read((prefix + '/' if prefix else '') + 'package-cases/' + package['archive'])) == package['archive_sha256'], 'package digest')
    return report, len(index)


def check_demo(z, prefix, inventory):
    report = json.loads(z.read((prefix + '/' if prefix else '') + 'report.json'))
    require(report['passed'] is True and report['reference_checked'] is True and report['mode'] == 'check', 'demo status')
    require((report['product_calls'], report['reference_calls'], len(report['receipts'])) == (13, 4, 17), 'demo counts')
    for receipt in report['receipts']:
        snapshot = receipt['snapshot']
        product = snapshot.startswith('demo/output/')
        require(product or snapshot.startswith('demo/reference/'), 'unknown snapshot')
        leaf = ('product-' if product else 'reference-') + PurePosixPath(snapshot).name
        require(receipt['exit_code'] == 0, 'demo exit')
        for stream in ['stdout', 'stderr']:
            raw = z.read((prefix + '/' if prefix else '') + '' + leaf + '.' + stream)
            require(digest(raw) == receipt[stream + '_sha256'], 'demo stream')
            if stream == 'stdout':
                require(digest(raw) == inventory[snapshot], 'snapshot mismatch')
            elif product:
                require(raw == b'', 'product stderr')

    return report



def check_public(z,prefix,product_sha,inventory):
    root=(prefix+'/' if prefix else '')
    report=json.loads(z.read(root+'report.json'))
    require(report['passed'] is True and report['product_calls']==6,'public workflow status')
    require(report['product_sha256']==product_sha,'public workflow binary')
    source=json.loads(subprocess.check_output(['git','show',CODE+':demo/public-data/SOURCE.json'],cwd=ROOT))
    require(report['source_license']=='CC-BY-4.0' and report['source_commit']==source['commit'] and report['source_sha256']==source['source_sha256'],'public provenance')
    require(report['baseline_counts']==dict(reference=11,prediction=11,tp=11,fp=0,fn=0),'public baseline')
    require(report['regressed_counts']==dict(reference=11,prediction=11,tp=9,fp=2,fn=2),'public regression')
    require(len(report['receipts'])==6,'public command count')
    for row in report['receipts']:
        require(row['exit_code']==0 and row['timed_out'] is False,'public command failed')
        for stream,extension in [('stdout','.json'),('stderr','.stderr')]:
            raw=z.read(root+row['name']+extension)
            require(digest(raw)==row[stream+'_sha256'],'public stream')
            if stream=='stdout':require(digest(raw)==inventory['demo/public-data/output/'+row['name']+'.json'],'public snapshot')
            else:require(raw==b'','public stderr')
    require(digest(z.read(root+'analysis.md'))==inventory['demo/public-data/output/analysis.md'],'analysis snapshot')
    return report


def main():
    for name,want in read(STAGE/'SHA256SUMS.json').items():require(digest((STAGE/name).read_bytes())==want,'frozen file: '+name)
    for filename,run_id in [('full-run.json',43410461615),('smoke-run.json',43410412628)]:
        run=read(STAGE/filename)
        require(run['id']==run_id and run['head_sha']==CODE and run['status']=='completed' and run['conclusion']=='success','actual CI run')
    full_jobs=read(STAGE/'full-jobs.json')['jobs'];quick_jobs=read(STAGE/'smoke-jobs.json')['jobs']
    require(len(full_jobs)==2 and all(j['conclusion']=='success' and j['run_id']==43410461615 for j in full_jobs),'full jobs')
    require(len(quick_jobs)==1 and quick_jobs[0]['conclusion']=='success' and quick_jobs[0]['run_id']==43410412628,'quick job')
    require(read(STAGE/'repository.json')['visibility']=='public','public repository')
    artifacts=read(STAGE/'artifacts.json')
    rows=[]
    with archive('local.zip') as local:
        inventory=json.loads(local.read('accepted-reviewed/report.json'))['source_sha256']
        local_report,_=check_gate(local,'accepted-reviewed',AUTHOR,inventory)
        require(check_demo(local,'demo-reviewed',inventory)['product_sha256']==local_report['product_sha256'],'local demo binary')
        check_public(local,'public-reviewed',local_report['product_sha256'],inventory)
        for marker in [b'test_modified_provenance_is_rejected',b'test_timed_out_process_retains_partial_streams_and_invocation']:
            require(marker in local.read('accepted-reviewed/python-tests/stderr'),'new rejection test missing')
        rejected=json.loads(local.read('reviewer-provenance-rejected/report.json'))
        require(rejected['passed'] is False and rejected['product_calls']==0,'reviewer original corruption not rejected')
        # Fresh network install of the unchanged published0.1.0, bound to its archived bytes.
        registry=json.loads(local.read('registry/report.json'))
        require(registry['passed'] is True and registry['installed_members']==43 and registry['api_reports']==3 and registry['installed_cli_examples']==3,'registry consumption')
        require(registry['module']=='z2823253773-p/mooneventeval' and registry['version']=='0.1.0' and registry['no_workspace'] is True and registry['login_performed'] is False,'registry identity')
        release=ROOT/'evidence/P8/release-0.1.0.zip'
        require(digest(release.read_bytes())==registry['archive_sha256'],'registered archive binding')
        with zipfile.ZipFile(release) as z:
            require(registry['installed_member_sha256']=={n:digest(z.read(n)) for n in z.namelist()},'43 installed bytes')
            for n in z.namelist():
                if n not in {'README.md','THIRD_PARTY_NOTICES.md'}:
                    require(inventory[n]==digest(z.read(n)),'published library changed: '+n)
        require(read(STAGE/'cache-isolation.json')['original_cache_restored'] is True,'original package cache not restored')
        require(b'Downloading z2823253773-p/mooneventeval@0.1.0' in local.read('registry/add/stderr'),'actual network installation')
        require(registry['checker_sha256']==inventory['scripts/check_registry.py'],'registry checker source')
        require(len(registry['steps'])==7,'registry steps')
        for step in registry['steps']:
            require(step['exit_code']==0 and not step['timed_out'],'registry failed')
            for stream in ['stdout','stderr']:require(digest(local.read('registry/'+step['name']+'/'+stream))==step[stream+'_sha256'],'registry stream')
        for filename,artifact_name,system,machine in [
            ('ci-macos.zip','verification-macos-15-arm64','Darwin','arm64'),
            ('ci-linux.zip','verification-ubuntu-24.04-x86_64','Linux','x86_64')]:
            metadata=next(a for a in artifacts['full'] if a['name']==artifact_name)
            require(metadata['digest']=='sha256:'+digest((STAGE/filename).read_bytes()) and metadata['workflow_run']['head_sha']==CODE,'original GitHub ZIP digest')
            with archive(filename) as remote:
                report,count=check_gate(remote,'',CODE,inventory)
                require(report['host']['system']==system and report['host']['machine']==machine and report['remote_ci']=='CURRENT_JOB_ONLY','runner identity')
                require(check_demo(remote,'public-demo',inventory)['product_sha256']==report['product_sha256'],'CI demo binding')
                check_public(remote,'public-data',report['product_sha256'],inventory)
                rows.append(dict(platform=system+'/'+machine,gates=17,artifact_files=count,public_calls=6))
    with archive('ci-smoke.zip') as quick:
        report=json.loads(quick.read('report.json'))
        require(report['passed'] is True and report['git_head']==CODE and report['source_unchanged'] is True,'quick status')
        require(report['moon_tests']==65 and report['workflow_tests']==4 and len(report['steps'])==8,'quick scope')
        require(report['reference_checked'] is False and report['registry_checked'] is False,'quick overclaim')
        require([s['name'] for s in report['steps']]==report['required_steps'],'quick steps')
        for name,want in report['materialized_source_sha256'].items():require(inventory[name]==want,'sparse source: '+name)
        for step in report['steps']:
            require(step['passed'] is True and step['exit_code']==0 and not step['timed_out'],'quick failure')
            for stream in ['stdout','stderr']:require(digest(quick.read(step['name']+'/'+stream))==step[stream+'_sha256'],'quick stream')
        for name,want in json.loads(quick.read('SHA256SUMS.json')).items():require(digest(quick.read(name))==want,'quick artifact')
        check_public(quick,'public-output',report['product_sha256'],inventory)
        require(json.loads(quick.read('synthetic-output/report.json'))['reference_checked'] is False,'quick reference boundary')
        meta=artifacts['smoke'][0];require(meta['digest']=='sha256:'+digest((STAGE/'ci-smoke.zip').read_bytes()),'quick original ZIP digest')
    # Bind every frozen source byte to the actual public tested Git commit.
    for name,want in inventory.items():require(digest(subprocess.check_output(['git','show',CODE+':'+name],cwd=ROOT))==want,'Git source: '+name)
    source_bytes=subprocess.check_output(['git','show',CODE+':demo/public-data/SOURCE.json'],cwd=ROOT)
    source=json.loads(source_bytes)
    program=subprocess.check_output(['git','show',CODE+':demo/public-data/reproduce.py'],cwd=ROOT)
    require(digest(source_bytes).encode() in program,'source manifest not pinned')
    import gzip
    raw=gzip.decompress(subprocess.check_output(['git','show',CODE+':demo/public-data/source/public-eval.tsv.gz'],cwd=ROOT))
    require(len(raw)==source['source_bytes']==119823 and digest(raw)==source['source_sha256'],'upstream original bytes')
    license=read(STAGE/'source-record.json')
    require(license['license']['id']=='cc-by-4.0' and [a['name'] for a in license['creators']]==source['authors'],'record license/attribution')
    with archive('metadata.zip') as metadata:
        package=json.loads(metadata.read('package/report.json'))
        require(package['passed'] is True and len(package['members'])==43,'closing docs package')
        require(digest(metadata.read('package/'+package['archive']))==package['archive_sha256'],'closing docs package bytes')
    print(json.dumps(dict(passed=True,stage='P9',tested_public_sha=CODE,source_files=len(inventory),full_run=43410461615,smoke_run=43410412628,jobs=rows,quick_gates=8,registry_installed_members=43,data_license='CC-BY-4.0')))


if __name__=='__main__':main()
