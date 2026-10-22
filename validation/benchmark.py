"""Native file CLI performance; per-child wait4 peak RSS, not cumulative rusage."""
import argparse
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import platform
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from validation.rational_oracle import decimal_text, eligible
from validation.compare import decode_machine_report, report_shape_differences


def performance_cases(size=1000):
    def e(id, onset):return dict(id=id,label='a',onset_s=decimal_text(onset),offset_s=decimal_text(onset+1))
    for name in ['sparse','dense','chain']:
        refs=[];preds=[]
        for i in range(size):
            p=Fraction(2*i if name=='sparse' else 1 if name=='dense' else 2+Fraction(i,8))
            r=p if name!='chain' else p+Fraction(1,16) if i<size-1 else Fraction(2)-Fraction(1,16)
            refs.append(e(f'r{i:04d}',r));preds.append(e(f'p{i:04d}',p))
        yield name,dict(schema_version=1,labels=['a'],config=dict(collar_s='0.0625' if name=='chain' else '0.25',offset_ratio='0.5'),recordings=[dict(id='x',reference=refs,prediction=preds)])


def measured(command,folder,timeout=30):
    folder.mkdir();started=time.perf_counter();timed_out=False
    with (folder/'stdout').open('wb') as stdout,(folder/'stderr').open('wb') as stderr:
        proc=subprocess.Popen(command,cwd=ROOT,stdout=stdout,stderr=stderr)
        while True:
            pid,status,usage=os.wait4(proc.pid,os.WNOHANG)
            if pid:break
            if time.perf_counter()-started>timeout:
                os.kill(proc.pid,signal.SIGKILL);pid,status,usage=os.wait4(proc.pid,0);timed_out=True;break
            time.sleep(.005)
        proc.returncode=os.waitstatus_to_exitcode(status)
    return dict(command=command,exit_code=proc.returncode,timed_out=timed_out,
                wall_seconds=time.perf_counter()-started,peak_rss_bytes=usage.ru_maxrss*(1 if sys.platform=='darwin' else 1024),
                user_seconds=usage.ru_utime,system_seconds=usage.ru_stime,
                stdout_sha256=hashlib.sha256((folder/'stdout').read_bytes()).hexdigest())


def validate_performance_report(document,actual,name):
    """Polynomial membership/partition/eligibility checks for known perfect graphs."""
    errors=report_shape_differences(actual)
    if errors:return errors
    def issue(path,want,got):errors.append(dict(path=path,expected=want,actual=got))
    rec=document['recordings'][0];size=len(rec['reference'])
    counts=dict(reference=size,prediction=size,tp=size,fp=0,fn=0)
    if actual['summary']['counts']!=counts:issue('summary.counts',counts,actual['summary']['counts'])
    for key in ['precision','recall','f1']:
        value=actual['summary'][key]
        if value is None or abs(value-1)>1e-12:issue('summary.'+key,1,value)
    expected_metric=dict(counts=counts,precision=1,recall=1,f1=1)
    for key,want in [('schema_version',1),('status','completed'),('semantics','collar-max-cardinality/v1'),('implementation_version','0.1.0'),
                     ('config',document['config']),('by_label',[dict(label='a',metrics=expected_metric)]),
                     ('by_recording',[dict(recording_id=rec['id'],metrics=expected_metric)]),('false_positives',[]),('false_negatives',[])]:
        if actual[key]!=want:issue(key,want,actual[key])
    refs={e['id']:e for e in rec['reference']};preds={e['id']:e for e in rec['prediction']}
    seen_refs=set();seen_preds=set()
    for pair in actual['matches']:
        r=pair['reference'];p=pair['prediction']
        if refs.get(r['id'])!=r or preds.get(p['id'])!=p:issue('match.membership','exact input events',pair)
        if r['id'] in seen_refs or p['id'] in seen_preds:issue('match.one_to_one','unique sides',pair)
        seen_refs.add(r['id']);seen_preds.add(p['id'])
        if pair['recording_id']!=rec['id'] or pair['label']!='a':issue('match.group','input recording/label',pair)
        basis=eligible(r,p,document['config'])
        if not basis['eligible'] or pair['basis']!=basis:issue('match.eligibility',dict(eligible=True,basis=basis),pair['basis'])
    if seen_refs!=set(refs) or seen_preds!=set(preds) or len(actual['matches'])!=size:issue('match.partition','every input event exactly once',dict(references=len(seen_refs),predictions=len(seen_preds),pairs=len(actual['matches'])))
    edges=size if name=='sparse' else size*size if name=='dense' else 2*size-1
    steps=3*size if name=='sparse' else size*(size+5)//2 if name=='dense' else 7*size-3
    want=dict(candidate_checks=size*size,eligible_edges=edges,matching_steps=steps)
    if actual['work']!=want:issue('work',want,actual['work'])
    return errors


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--product',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--cpu-name',help='Previously measured CPU identity when sandbox denies sysctl; retain its separate receipt')
    args=parser.parse_args();exe=args.product.resolve();output=args.output.resolve();output.mkdir(parents=True,exist_ok=True)
    rows=[]
    for name,doc in performance_cases():
        folder=output/name;folder.mkdir();path=folder/'input.json';path.write_text(json.dumps(doc,separators=(',',':'))+'\n')
        samples=[]
        for i in range(3):
            trial=folder/str(i);row=measured([str(exe),'evaluate',str(path),'--format','json'],trial)
            assert row['exit_code']==0 and not (trial/'stderr').read_bytes(),row
            actual=decode_machine_report((trial/'stdout').read_bytes())
            differences=validate_performance_report(doc,actual,name)
            (trial/'comparison.json').write_text(json.dumps(dict(passed=not differences,differences=differences),indent=2)+'\n')
            assert not differences,differences[:3]
            row['work']=actual['work'];samples.append(row)
        assert name!='sparse' or all(s['wall_seconds']<5 for s in samples),'sparse target missed'
        rows.append(dict(name=name,samples=samples))
    cpu=args.cpu_name or (subprocess.check_output(['sysctl','-n','machdep.cpu.brand_string'],text=True).strip() if sys.platform=='darwin' else platform.processor())
    compiler=subprocess.check_output([str(ROOT/'scripts/with-toolchain.sh'),'moonc','-v'],text=True).strip()
    report=dict(passed=True,git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),product=str(exe),product_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),
                platform=platform.platform(),machine=platform.machine(),cpu=cpu,logical_cpus=os.cpu_count(),compiler=compiler,cases=rows,
                measurement='wall includes launch/read/evaluate/JSON/write to local file; wait4 per-child ru_maxrss; three independent release process samples',
                scope='local samples only; not all-graph budget, cross-platform or universal peak/time guarantee')
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(passed=True,cases=[dict(name=r['name'],max_wall_seconds=max(s['wall_seconds'] for s in r['samples']),max_rss_bytes=max(s['peak_rss_bytes'] for s in r['samples'])) for r in rows])))


if __name__=='__main__':main()
