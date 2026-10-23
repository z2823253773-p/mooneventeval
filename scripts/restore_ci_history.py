"""Restore original proof objects omitted only from the GitHub transport tree."""
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(path):
 with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def git(root,*args):return subprocess.check_output(['git',*args],cwd=root,stderr=subprocess.PIPE)
def restore(root):
 root=Path(root).resolve()
 if Path(git(root,'rev-parse','--show-toplevel').decode().strip()).resolve()!=root:raise ValueError('wrong project root')
 meta=json.loads((root/'.ci/history.json').read_bytes());bundle=root/'.ci/original-history.bundle'
 if not bundle.is_file() or sha(bundle)!=meta['bundle_sha256']:raise ValueError('original history bundle digest mismatch')
 tip=meta['original_tip'];ref=meta['original_ref']
 if not re.fullmatch('[0-9a-f]{40}',tip) or not re.fullmatch(r'refs/heads/[A-Za-z0-9_./-]+',ref):raise ValueError('invalid original history identity')
 targets=[]
 for name,row in meta['omitted_files'].items():
  target=root/name
  if not name.startswith('evidence/') or '..' in Path(name).parts or not target.resolve().is_relative_to(root) or target.is_symlink():raise ValueError('unsafe proof path')
  if not re.fullmatch('[0-9a-f]{64}',row['sha256']) or not isinstance(row['bytes'],int) or row['bytes']<0:raise ValueError('invalid proof identity')
  if target.exists() and (not target.is_file() or target.stat().st_size!=row['bytes'] or sha(target)!=row['sha256']):raise ValueError('existing proof differs; refusing overwrite')
  targets.append((name,target,row))
 git(root,'bundle','verify',str(bundle))
 # Import under a separate evidence ref, never reset or rewrite the checked out ref.
 git(root,'fetch','--no-tags','--no-write-fetch-head',str(bundle),ref+':refs/ci-evidence/original')
 if git(root,'rev-parse','refs/ci-evidence/original').decode().strip()!=tip:raise ValueError('original history tip differs')
 for name,target,row in targets:
  if int(git(root,'cat-file','-s',tip+':'+name))!=row['bytes']:raise ValueError('original proof size differs')
  if not target.exists():
   target.parent.mkdir(parents=True,exist_ok=True);part=target.with_name(target.name+'.restore-part')
   with part.open('xb') as stream:subprocess.run(['git','show',tip+':'+name],cwd=root,stdout=stream,stderr=subprocess.PIPE,check=True)
   if part.stat().st_size!=row['bytes'] or sha(part)!=row['sha256']:raise ValueError('original proof digest differs')
   part.replace(target)
 return dict(passed=True,scope='lossless original history/proof restoration, not qualification by itself',original_tip=tip,bundle_sha256=meta['bundle_sha256'],restored_proofs={name:row for name,_,row in targets})
if __name__=='__main__':
 report=restore(ROOT);output=ROOT/'evidence/R1/ci-bootstrap/report.json';output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report))
