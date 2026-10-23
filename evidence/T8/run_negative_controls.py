"""Five real top-level verifier failure controls, isolated from production files."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from release_support import fresh,save


def run(output):
    output=fresh(output);original_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    names=[p for p in subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0') if p and not p.startswith('evidence/')]
    objects=Path(subprocess.check_output(['git','rev-parse','--git-common-dir'],cwd=ROOT,text=True).strip())
    if not objects.is_absolute():objects=(ROOT/objects).resolve()
    rows=[]
    for case in ['missing-reference','bad-toolchain-hash','child-nonzero','missing-binary','archive-missing-license']:
        with tempfile.TemporaryDirectory(prefix='mee-verify-negative-') as directory:
            root=Path(directory)
            for name in names:
                target=root/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
            def git(*args):return subprocess.run(['git',*args],cwd=root,check=True,capture_output=True)
            git('init','-q');git('add','.')
            git('-c','user.name=Verification fixture','-c','user.email=fixture@example.invalid','commit','-qm','isolated verifier fixture')
            with (root/'.git/info/exclude').open('a') as f:f.write('\n.tools\n.venv-reference\n')
            # Read historical objects only; no operation writes the original Git directory.
            (root/'.git/objects/info/alternates').write_text(str(objects/'objects')+'\n')
            if case=='bad-toolchain-hash':
                (root/'.tools/downloads').mkdir(parents=True)
                (root/'.tools/downloads/moonbit.tar.gz').write_bytes(b'corrupted archive fixture')
            else:(root/'.tools').symlink_to(ROOT/'.tools',target_is_directory=True)
            if case!='missing-reference':(root/'.venv-reference').symlink_to(ROOT/'.venv-reference',target_is_directory=True)
            (root/'evidence').mkdir()
            for path in (ROOT/'evidence').iterdir():
                if path.name!='T8':(root/'evidence'/path.name).symlink_to(path,target_is_directory=path.is_dir())
            spec=importlib.util.spec_from_file_location('verify_fixture',root/'scripts/verify.py')
            module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
            original=module.run_step
            def inject(name,command,project,evidence,env):
                if case=='child-nonzero' and name=='format':command=[sys.executable,'-c','import sys;print("injected child failure");sys.exit(7)']
                row=original(name,command,project,evidence,env)
                if case=='missing-binary' and name=='release-build':
                    binary=project/'_build/native/release/build/cmd/mooneventeval/mooneventeval.exe'
                    assert binary.is_file();binary.unlink()
                if case=='archive-missing-license' and name=='package':
                    report=json.loads((evidence/'package-cases/report.json').read_bytes());archive=evidence/'package-cases'/report['archive']
                    with zipfile.ZipFile(archive) as z:members={n:z.read(n) for n in z.namelist() if n!='LICENSE'}
                    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
                        for n,data in members.items():z.writestr(n,data)
                return row
            module.run_step=inject
            proof=output/case;report=module.verify(root,proof)
            assert report['passed'] is False,case
            message=report['error']['message']
            expected={'missing-reference':'reference','bad-toolchain-hash':'SHA-256','child-nonzero':'format subprocess failed','missing-binary':'binary','archive-missing-license':'LICENSE'}[case]
            assert expected in message,(case,report.get('error'))
            if case=='child-nonzero':assert json.loads((proof/'format/receipt.json').read_bytes())['exit_code']==7
            if case=='archive-missing-license':assert len(report['steps'])==17 and all(row['passed'] for row in report['steps'])
            rows.append(dict(case=case,passed=False,rejected_for_expected_reason=True,error=report['error'],completed_subprocesses=len(report['steps']),fixture_sha=report.get('git_head')))
    assert not subprocess.check_output(['git','diff','HEAD','--','eventeval','cli','cmd/mooneventeval'],cwd=ROOT)
    save(output/'report.json',dict(passed=True,source_sha=original_sha,cases=rows,scope='expected top-level verifier failures in fresh fixture repositories; no product mutation score, no skip mode or modified production source',original_runtime_sources_unchanged=True))
    print(json.dumps(dict(passed=True,negative_controls=len(rows))))


if __name__=='__main__':run(Path(sys.argv[1]))
