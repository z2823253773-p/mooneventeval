from pathlib import Path
import subprocess, os, json, hashlib
original=Path('/Users/henryz/Desktop/比赛/mooneventeval-t0')
audit=Path('/private/tmp/mooneventeval-review-available')
copy=audit/'checkout'
copy.mkdir()
candidate='df2142688e991c244cae0a94623ccf8acf55f257'
run=lambda a,**kw:subprocess.check_output(a,**kw)
paths=run(['git','ls-tree','-rz',candidate],cwd=original).split(b'\0')
for row in paths:
    if not row: continue
    meta,name=row.split(b'\t',1);name=name.decode();mode,typ,obj=meta.decode().split()
    if name.startswith('evidence/'):continue
    dest=copy/name;dest.parent.mkdir(parents=True,exist_ok=True)
    data=run(['git','cat-file','blob',obj],cwd=original)
    if mode=='120000':dest.symlink_to(data.decode())
    else:
        dest.write_bytes(data)
        dest.chmod(0o755 if mode=='100755' else 0o644)
subprocess.run(['git','init','-q'],cwd=copy,check=True)
common=Path(run(['git','rev-parse','--git-common-dir'],cwd=original,text=True).strip())
if not common.is_absolute():common=(original/common).resolve()
(copy/'.git/objects/info/alternates').write_text(str(common/'objects')+'\n')
subprocess.run(['git','update-ref','--no-deref','HEAD',candidate],cwd=copy,check=True)
subprocess.run(['git','read-tree',candidate],cwd=copy,check=True)
(copy/'.git/info/exclude').write_text('.tools\n.venv-reference\n')
(copy/'.tools').mkdir()
for name in ['moonbit','downloads','python']:(copy/'.tools'/name).symlink_to(original/'.tools'/name,target_is_directory=True)
(copy/'.tools/reference-cache').mkdir()
(copy/'.venv-reference').symlink_to(original/'.venv-reference',target_is_directory=True)
(copy/'evidence').mkdir()
for name in ['T0','T1','T1b','T2','T3','T4','T5','T6','T7']:
    if (original/'evidence'/name).is_dir():(copy/'evidence'/name).symlink_to(original/'evidence'/name,target_is_directory=True)
meta=dict(original=str(original),copy=str(copy),candidate=candidate,objects_alternates=str(common/'objects'),tracked_non_evidence_files=sum(1 for p in copy.rglob('*') if p.is_file() and '.git' not in p.parts and '.tools' not in p.parts and 'evidence' not in p.parts),historical_evidence='T0-T7 symlinked read only; historical freeze scripts resolve original root',shared_tools='read-only use; fresh own reference-cache',original_status=run(['git','status','--porcelain=v1'],cwd=original,text=True),copy_diff=run(['git','diff','HEAD','--name-only'],cwd=copy,text=True))
(audit/'setup.json').write_text(json.dumps(meta,indent=2)+'\n')
print(json.dumps(meta))
