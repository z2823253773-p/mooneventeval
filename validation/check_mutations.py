"""Compile each temporary mutant, require behavioral kills, preserve equivalent status."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    specs=[
      ('onset-strict','eligibility.mbt','onset_abs <= config.collar_us','onset_abs < config.collar_us','eligibility_A3_onset_boundary',False),
      ('offset-strict','eligibility.mbt','offset_abs * 1_000_000L <= offset_limit_scaled','offset_abs * 1_000_000L < offset_limit_scaled','eligibility_A4_offset_boundary_and_reference_duration',False),
      ('minimum-collar','eligibility.mbt','if fixed_scaled > ratio_scaled','if fixed_scaled < ratio_scaled','eligibility_A4_offset_boundary_and_reference_duration',False),
      ('prediction-duration','eligibility.mbt','(reference.offset_us - reference.onset_us)','(prediction.offset_us - prediction.onset_us)','eligibility_A4_offset_boundary_and_reference_duration',False),
      ('reuse-prediction','matching.mbt','if prediction_match[p] == -1 {','if true {','matching_one_to_one_duplicate_and_isolated',False),
      ('empty-f1-one','evaluation.mbt','f1: if reference + prediction == 0 {\n      None','f1: if reference + prediction == 0 {\n      Some(1.0)','evaluation_empty_denominators_and_no_edges',False),
      ('swapped-max-equivalent','eligibility.mbt','if fixed_scaled > ratio_scaled {\n    fixed_scaled\n  } else {\n    ratio_scaled','if ratio_scaled > fixed_scaled {\n    ratio_scaled\n  } else {\n    fixed_scaled','*',True),
    ]
    originals={n:hashlib.sha256((ROOT/'eventeval'/n).read_bytes()).hexdigest() for n in {r[1] for r in specs}}
    rows=[]
    with tempfile.TemporaryDirectory(prefix='mee-mutations-') as temp:
        work=Path(temp);shutil.copytree(ROOT/'eventeval',work/'eventeval');shutil.copy2(ROOT/'moon.mod',work/'moon.mod')
        for n in ['scripts/with-toolchain.sh','docs/toolchain.lock.json']:
            p=work/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/n,p)
        (work/'.tools').symlink_to(ROOT/'.tools',target_is_directory=True)
        for name,file,before,after,test,equivalent in specs:
            folder=out/name;folder.mkdir();path=work/'eventeval'/file;data=path.read_text();assert data.count(before)==1,(name,data.count(before))
            command=[str(work/'scripts/with-toolchain.sh'),'moon','test','eventeval','--target','native','--deny-warn','--filter',test]
            def run(label,args):
                result=subprocess.run(args,cwd=work,capture_output=True,timeout=120)
                (folder/(label+'.stdout')).write_bytes(result.stdout);(folder/(label+'.stderr')).write_bytes(result.stderr)
                return result
            control=run('control',command);assert control.returncode==0 and b'failed: 0' in control.stdout,(name,control.stdout,control.stderr)
            changed=data.replace(before,after);path.write_text(changed)
            (folder/'mutation.diff').write_text(''.join(difflib.unified_diff(data.splitlines(True),changed.splitlines(True),fromfile=file,tofile=file)))
            build=run('build',command+['--build-only'])
            if build.returncode:status='invalid';result=build
            else:
                result=run('mutant',command)
                killed=result.returncode!=0 and (b'failed\n' in result.stdout or b' failed' in result.stdout or b'PanicError' in result.stderr+result.stdout)
                status='equivalent' if equivalent and result.returncode==0 else 'killed' if killed else 'survived'
            path.write_text(data);assert hashlib.sha256(path.read_bytes()).hexdigest()==originals[file]
            restored=run('restored',command);assert restored.returncode==0 and b'failed: 0' in restored.stdout
            row=dict(name=name,target_test=test,status=status,compiled=build.returncode==0,control_exit=control.returncode,mutant_exit=result.returncode,restored_exit=restored.returncode,
                     baseline_sha256=originals[file],mutant_sha256=hashlib.sha256(changed.encode()).hexdigest(),restored_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
            (folder/'receipt.json').write_text(json.dumps(dict(command=command,**row),indent=2)+'\n');rows.append(row)
    for name,digest in originals.items():assert hashlib.sha256((ROOT/'eventeval'/name).read_bytes()).hexdigest()==digest
    passed=all(r['status']==('equivalent' if s[-1] else 'killed') for r,s in zip(rows,specs))
    (out/'report.json').write_text(json.dumps(dict(passed=passed,cases=rows,production_source_unchanged=True,status_counts={s:sum(r['status']==s for r in rows) for s in ['invalid','equivalent','survived','killed']}),indent=2)+'\n')
    print(json.dumps(dict(passed=passed,statuses={r['name']:r['status'] for r in rows})))
    raise SystemExit(0 if passed else 1)


if __name__=='__main__':main()
