"""Four semantic mutation gates in isolated MoonBit copies, never the real source."""
import difflib
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/'evidence/T3/mutations'


def main():
    OUTPUT.mkdir(parents=True,exist_ok=True)
    source=ROOT/'eventeval/eligibility.mbt';baseline=source.read_text()
    mutants=[
      ('onset-strict','onset_abs <= config.collar_us','onset_abs < config.collar_us','eligibility_A3_onset_boundary'),
      ('offset-strict','offset_abs * 1_000_000L <= offset_limit_scaled','offset_abs * 1_000_000L < offset_limit_scaled','eligibility_A4_offset_boundary_and_reference_duration'),
      ('minimum-tolerance','fixed_scaled > ratio_scaled','fixed_scaled < ratio_scaled','eligibility_collar_dominates_without_overlap'),
      ('prediction-duration','reference.offset_us - reference.onset_us','prediction.offset_us - prediction.onset_us','eligibility_A4_offset_boundary_and_reference_duration'),
    ]
    report=[]
    for name,old,new,test in mutants:
        assert baseline.count(old)==1
        changed=baseline.replace(old,new,1)
        (OUTPUT/(name+'.diff')).write_text(''.join(difflib.unified_diff(baseline.splitlines(True),changed.splitlines(True),fromfile='baseline/eligibility.mbt',tofile=name+'/eligibility.mbt')))
        with tempfile.TemporaryDirectory(prefix='T3-'+name+'-',dir=ROOT/'.tools') as temporary:
            copy=Path(temporary);shutil.copy2(ROOT/'moon.mod',copy/'moon.mod');shutil.copytree(ROOT/'eventeval',copy/'eventeval')
            command=[str(ROOT/'scripts/with-toolchain.sh'),'moon','test','eventeval','--target','native','--deny-warn','--filter',test]
            control=subprocess.run(command,cwd=copy,text=True,capture_output=True,timeout=120)
            (OUTPUT/(name+'-control.log')).write_text(control.stdout+control.stderr)
            assert control.returncode==0 and 'passed: 1, failed: 0' in control.stdout
            (copy/'eventeval/eligibility.mbt').write_text(changed)
            run=subprocess.run(command,cwd=copy,text=True,capture_output=True,timeout=120)
            log=run.stdout+run.stderr;(OUTPUT/(name+'-mutated.log')).write_text(log)
            killed=run.returncode!=0 and 'passed: 0, failed: 1' in log and 'expect test failed' in log.lower()
            report.append(dict(name=name,test=test,command=command,control_exit_code=control.returncode,mutated_exit_code=run.returncode,
                               killed_by_behavior=killed,baseline_sha256=hashlib.sha256(baseline.encode()).hexdigest(),
                               mutated_sha256=hashlib.sha256(changed.encode()).hexdigest()))
            if not killed:raise RuntimeError(name+' was not killed by a compiled behavioral test; inspect saved log')
    assert source.read_text()==baseline
    (OUTPUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(valid_mutants=len(report),behaviorally_killed=sum(r['killed_by_behavior'] for r in report),source_unchanged=True)))


if __name__=='__main__':main()
