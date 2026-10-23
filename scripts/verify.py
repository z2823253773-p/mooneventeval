"""Run the complete local delivery gate from the current project directory.

No installs, remote operations, skipped-success modes or product budget overrides.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path,PurePosixPath
import platform
import re
import subprocess
import sys
import tarfile
import time
import zipfile

from release_support import fresh,record,save,sha


class VerificationFailure(RuntimeError):
    pass


def project_identity(root):
    root=Path(root).resolve();manifest=root/'moon.mod'
    if not manifest.is_file() or not re.search(r'^name\s*=\s*"local/mooneventeval"\s*$',manifest.read_text(),re.M):
        raise ValueError('current directory is not the MoonEventEval module root')
    for name in ['eventeval/moon.pkg','cmd/mooneventeval/moon.pkg','docs/toolchain.lock.json']:
        if not (root/name).is_file():raise ValueError('incomplete MoonEventEval checkout: '+name)
    if Path(subprocess.check_output(['git','rev-parse','--show-toplevel'],cwd=root,text=True).strip()).resolve()!=root:
        raise ValueError('current directory must be the MoonEventEval Git root')
    return root


def reference_python(root):
    path=Path(root)/'.venv-reference/bin/python'
    if not path.is_file() or not os.access(path,os.X_OK):raise ValueError('missing reference Python environment')
    return path


def require_binary(path):
    path=Path(path)
    if not path.is_file() or not os.access(path,os.X_OK):raise ValueError('actual release binary is missing or not executable')
    return sha(path)


def verify_toolchain(root):
    root=Path(root);lock=json.loads((root/'docs/toolchain.lock.json').read_bytes())
    target={('Darwin','arm64'):'darwin-aarch64',('Linux','x86_64'):'linux-x86_64'}.get((platform.system(),platform.machine()))
    if target is None:raise ValueError('unsupported toolchain platform; no fallback')
    home=root/'.tools/moonbit'/lock['version'];cache=root/'.tools/downloads'
    archives=[(cache/'moonbit.tar.gz',lock['binaries'][target],home),(cache/'core.tar.gz',lock['core_recorded_sha256'],home/'lib')]
    checked={};file_count=0
    for archive,want,destination in archives:
        if not archive.is_file():raise ValueError('missing toolchain archive: '+str(archive))
        actual=sha(archive)
        if actual!=want:raise ValueError('toolchain SHA-256 mismatch: '+archive.name)
        checked[archive.name]=actual
        with tarfile.open(archive,'r:gz') as tar:
            for member in tar:
                path=PurePosixPath(member.name)
                if path.is_absolute() or '..' in path.parts:raise ValueError('unsafe installed toolchain archive member')
                if not member.isfile():continue
                installed=destination.joinpath(*path.parts)
                if not installed.is_file():raise ValueError('installed toolchain file missing: '+str(path))
                with tar.extractfile(member) as stream:expected=hashlib.file_digest(stream,'sha256').hexdigest()
                if sha(installed)!=expected:raise ValueError('installed toolchain SHA-256 mismatch: '+str(path))
                file_count+=1
    sidecar=(cache/'moonbit.tar.gz.sha256').read_text().split()[0]
    if sidecar!=lock['binaries'][target]:raise ValueError('toolchain publisher sidecar SHA-256 mismatch')
    return dict(target=target,version=lock['version'],archives=checked,installed_regular_files_compared=file_count,
                core_provenance=lock['core_provenance'])


def run_step(name,command,root,evidence,env):
    started=time.monotonic()
    row=record(command,root,Path(evidence)/name,timeout=900) if not env else record_env(command,root,Path(evidence)/name,env)
    row['name']=name;row['elapsed_seconds']=round(time.monotonic()-started,4)
    row['passed']=row['exit_code']==0 and not row['timed_out']
    save(Path(evidence)/name/'receipt.json',row)
    if not row['passed']:raise VerificationFailure(name+' subprocess failed; see '+str(Path(evidence)/name))
    return row


def record_env(command,root,folder,overrides):
    # Keep the same binary-capture protocol, passing only explicit local test/cache env changes.
    folder=Path(folder);folder.mkdir(parents=True)
    env=dict(os.environ,**{k:str(v) for k,v in overrides.items()});timed_out=False
    try:
        process=subprocess.run([str(x) for x in command],cwd=root,env=env,capture_output=True,timeout=900)
        stdout,stderr,code=process.stdout,process.stderr,process.returncode
    except subprocess.TimeoutExpired as error:
        stdout,stderr,code=error.stdout or b'',error.stderr or b'',None;timed_out=True
    (folder/'stdout').write_bytes(stdout);(folder/'stderr').write_bytes(stderr)
    return dict(command=[str(x) for x in command],cwd=str(root),environment_overrides={k:str(v) for k,v in overrides.items()},
                exit_code=code,timed_out=timed_out,stdout_sha256=sha(folder/'stdout'),stderr_sha256=sha(folder/'stderr'))


def require_pass_report(path):
    path=Path(path)
    if not path.is_file():raise ValueError('missing artifact report: '+str(path))
    row=json.loads(path.read_bytes())
    if row.get('passed') is not True or row.get('skipped') or row.get('timed_out'):
        raise ValueError('failed or skipped artifact report: '+str(path))
    return row


def validate_package_archive(path):
    from package_candidate import archive_members
    names=archive_members(path)
    for name in ['LICENSE','THIRD_PARTY_NOTICES.md','cmd/mooneventeval/io_stub.c','eventeval/moon.pkg']:
        if name not in names:raise ValueError('archive missing '+name)
    return names


def source_inventory(root):
    paths=subprocess.check_output(['git','ls-files','-z'],cwd=root).decode().split('\0')
    return {name:sha(root/name) for name in paths if name and not name.startswith('evidence/')}


def clean_sources(root):
    changed=subprocess.check_output(['git','diff','HEAD','--name-only','-z'],cwd=root).decode().split('\0')
    untracked=subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z'],cwd=root).decode().split('\0')
    bad=[p for p in changed+untracked if p and not p.startswith('evidence/')]
    if bad:raise ValueError('commit source/document/config changes before verification: '+', '.join(sorted(set(bad))))


def check_test_protocol(folder,kind,minimum):
    raw=(folder/'stdout').read_text(errors='strict')+'\n'+(folder/'stderr').read_text(errors='strict')
    if kind=='moon':
        match=re.search(r'Total tests: (\d+), passed: (\d+), failed: (\d+)',raw)
        if not match or int(match[1])<minimum or match[1]!=match[2] or int(match[3])!=0:
            raise ValueError('invalid/empty native test success protocol')
        return int(match[1])
    match=re.search(r'^Ran (\d+) tests? in [0-9.]+s$',raw,re.M)
    if not match or int(match[1])<minimum or not re.search(r'^OK$',raw,re.M) or 'skipped=' in raw:
        raise ValueError('invalid/empty/skipped unittest success protocol')
    return int(match[1])


def validate_ci_config(root):
    # JSON is the deliberately restricted serialization of this YAML workflow.
    workflow=json.loads((root/'.github/workflows/ci.yml').read_bytes())
    lock=json.loads((root/'docs/ci-actions.lock.json').read_bytes())
    if workflow['on']!={'workflow_dispatch':{}} or workflow['permissions']!={'contents':'read'}:
        raise ValueError('CI trigger or permissions changed')
    job=workflow['jobs']['verify'];matrix=job['strategy']['matrix']['include']
    if {(r['os'],r['arch']) for r in matrix}!={('macos-14','arm64'),('ubuntu-24.04','x86_64')}:
        raise ValueError('CI platform matrix changed')
    steps=job['steps'];uses={step['uses'] for step in steps if 'uses' in step}
    if uses!={name+'@'+row['sha'] for name,row in lock['actions'].items()}:
        raise ValueError('CI actions do not match verified full-SHA pins')
    for use in uses:
        if not re.fullmatch(r'[\w-]+/[\w-]+@[0-9a-f]{40}',use):raise ValueError('unpinned CI action')
    commands='\n'.join(s.get('run','') for s in steps)
    if 'python3 scripts/verify.py --mode local --evidence evidence/T8/ci' not in commands:
        raise ValueError('CI does not call the unified verifier')
    if '--require-hashes' not in commands or '--no-build-isolation' not in commands:
        raise ValueError('CI reference hashes/build lock missing')
    return dict(passed=True,remote_executed=False,actions=sorted(uses),matrix=matrix,format='JSON subset of YAML; remote semantics untested')


def reference_probe_code(root):
    return '''import hashlib,importlib.metadata as md,json,pathlib,platform,re,sys
root=pathlib.Path(sys.argv[1]);sys.path.insert(0,str(root/'validation'))
import sed_reference
sed_eval=sed_reference._reference_module()
expected=dict(re.findall(r'^([A-Za-z0-9_.-]+)==([^\\s]+)',(root/'validation/reference.lock').read_text(),re.M))
actual={name:md.version(name) for name in expected}
assert expected==actual,(expected,actual)
exe=pathlib.Path(sys.executable).resolve()
print(json.dumps(dict(python_version=platform.python_version(),executable=str(exe),executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),packages=actual,sed_eval_source_verified=True,sed_eval_bytecode_verified=True)))
'''


def verify(root,output):
    root=Path(root).resolve();output=fresh(output)
    context='CURRENT_JOB_ONLY' if os.environ.get('GITHUB_ACTIONS')=='true' else 'NOT_RUN'
    result=dict(passed=False,mode='local',root=str(root),steps=[],scope='current-checkout local native delivery gate',
                remote_ci=context,published=False,personal_M2='NOT_PERFORMED',host=dict(system=platform.system(),machine=platform.machine(),python=platform.python_version()))
    try:
        project_identity(root)
        if Path(__file__).resolve()!=root/'scripts/verify.py':raise ValueError('invoke verify.py from this checkout; no foreign-script fallback')
        clean_sources(root)
        result['git_head']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
        before=source_inventory(root);result['source_sha256']=before
        result['toolchain']=verify_toolchain(root);python=reference_python(root)
        result['ci_configuration']=validate_ci_config(root)
        wrapper=root/'scripts/with-toolchain.sh';binary=root/'_build/native/release/build/cmd/mooneventeval/mooneventeval.exe'
        cache=dict(MPLCONFIGDIR=str(root/'.tools/reference-cache/matplotlib'),NUMBA_CACHE_DIR=str(root/'.tools/reference-cache/numba'))
        commands=[
            ('versions',[wrapper,'moon','version','--all'],{}),
            ('format',[wrapper,'moon','fmt','--check'],{}),
            ('interfaces',[wrapper,'moon','info','--target','native'],{}),
            ('native-check',[wrapper,'moon','check','--target','native','--deny-warn'],{}),
            ('native-tests',[wrapper,'moon','test','--target','native','--deny-warn'],{}),
            ('release-build',[wrapper,'moon','build','cmd/mooneventeval','--target','native','--release','--deny-warn'],{}),
            ('reference-identity',[python,'-c',reference_probe_code(root),root],cache),
            ('python-tests',[sys.executable,'-W','error::ResourceWarning','-m','unittest','discover','-s','tests','-v'],{}),
            ('validation-tests',[python,'-W','error::ResourceWarning','-m','unittest','discover','-s','validation/tests','-v'],cache),
            ('cli-tests',[sys.executable,'-W','error::ResourceWarning','-m','unittest','discover','-s','tests/cli','-v'],dict(MEE_BIN=str(binary),MEE_EVIDENCE=str(output/'cli-cases'))),
            ('qualification',[python,'validation/compare.py','--phase','qualification','--product',binary,'--output',output/'parity'],cache),
            ('consumer',[sys.executable,'scripts/check_consumer.py','--source',root,'--output',output/'consumer-cases'],{}),
            ('package',[sys.executable,'scripts/package_candidate.py','--output',output/'package-cases'],{}),
            ('examples',[sys.executable,'scripts/check_examples.py','--source',root,'--bin',binary,'--output',output/'example-cases'],{}),
            ('historical-T6',[sys.executable,'evidence/T6/freeze.py'],{}),
            ('historical-T7',[sys.executable,'evidence/T7/freeze.py'],{}),
            ('documentation',[sys.executable,'scripts/check_design_docs.py'],{}),
        ]
        result['required_steps']=[name for name,_,_ in commands]
        for name,command,env in commands:
            row=run_step(name,command,root,output,env);result['steps'].append(row)
            if name=='interfaces' and source_inventory(root)!=before:raise ValueError('generated interfaces changed tracked source files')
            if name=='native-tests':result['moon_tests']=check_test_protocol(output/name,'moon',58)
            if name=='release-build':result['product_sha256']=require_binary(binary)
            if name=='reference-identity':
                identity=json.loads((output/name/'stdout').read_bytes());lock=json.loads((root/'validation/python-reference.lock.json').read_bytes())
                if identity['python_version']!=lock['python_version'] or identity['sed_eval_source_verified'] is not True or identity.get('sed_eval_bytecode_verified') is not True:raise ValueError('reference Python/source/bytecode identity mismatch')
                if platform.system()=='Darwin' and identity['executable_sha256']!=lock['executable_sha256']:raise ValueError('qualified Mac reference executable hash differs')
                result['reference_identity']=identity
            if name in {'python-tests','validation-tests','cli-tests'}:
                result[name.replace('-','_')]=check_test_protocol(output/name,'python',{'python-tests':20,'validation-tests':41,'cli-tests':15}[name])
        parity=require_pass_report(output/'parity/report.json')
        if parity['unexplained'] or len(parity['cases'])!=324 or parity['product_sha256']!=result['product_sha256'] or parity['git_head']!=result['git_head']:
            raise ValueError('qualification scope/binary/commit mismatch')
        consumer=require_pass_report(output/'consumer-cases/report.json')
        package=require_pass_report(output/'package-cases/report.json');require_pass_report(output/'example-cases/report.json')
        archive=output/'package-cases'/package['archive'];validate_package_archive(archive)
        if sha(archive)!=package['archive_sha256']:raise ValueError('candidate archive hash differs')
        if source_inventory(root)!=before:raise ValueError('source/doc/config bytes changed during verification')
        clean_sources(root)
        if [row['name'] for row in result['steps']]!=result['required_steps']:raise ValueError('required step missing')
        result.update(passed=True,qualification_bases=324,qualification_product_calls=1620,
                      archive_sha256=package['archive_sha256'],archive_members=len(package['members']),source_unchanged=True)
    except Exception as error:
        result['error']=dict(type=type(error).__name__,message=str(error))
    save(output/'report.json',result)
    # Bind the exact resulting logs/artifacts independently of whether the gate passed.
    save(output/'SHA256SUMS.json',{str(p.relative_to(output)):sha(p) for p in sorted(output.rglob('*'))
                                 if p.is_file() and p.name!='SHA256SUMS.json'})
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--mode',choices=['local'],required=True);parser.add_argument('--evidence',type=Path,required=True)
    args=parser.parse_args();result=verify(Path.cwd(),args.evidence)
    print(json.dumps(dict(passed=result['passed'],git_head=result.get('git_head'),steps=len(result['steps']),error=result.get('error'),remote_ci=result['remote_ci'])))
    return 0 if result['passed'] else 1


if __name__=='__main__':raise SystemExit(main())
