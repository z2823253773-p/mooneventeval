"""Execute the documented three CLI scenarios and public API snippet."""
import argparse
import json
from pathlib import Path
from release_support import ROOT,WRAPPER,fresh,record,save,sha,machine_report

BINARY='_build/native/release/build/cmd/mooneventeval/mooneventeval.exe'
EXPECTED={
    'duplicate':(dict(reference=1,prediction=2,tp=1,fp=1,fn=0),{('r1','p1')}),
    'greedy-trap':(dict(reference=2,prediction=2,tp=2,fp=0,fn=0),{('r1','p2'),('r2','p1')}),
    'boundary':(dict(reference=1,prediction=1,tp=1,fp=0,fn=0),{('r1','p1')}),
}


def check(source,binary,output):
    source=Path(source).resolve();binary=Path(binary).resolve();output=fresh(output)
    rows=[];differences=[]
    import re
    blocks=re.findall(r'```json\n(.*?)```',(source/'EXAMPLES.md').read_text(),re.S)
    if len(blocks)!=6:raise ValueError('EXAMPLES must have three complete input/summary pairs')
    documentation=[json.loads(block) for block in blocks]
    readme=(source/'README.md').read_text()
    for option in ['--help','--version']:
        command=[BINARY,option]
        if ' '.join(command) not in readme:raise ValueError('README missing documented command')
        row=record([binary,option],source,output/option[2:]);rows.append(row)
        raw=(output/option[2:] /'stdout').read_bytes()
        if row['exit_code']!=0 or (output/option[2:] /'stderr').read_bytes() or not raw.endswith(b'\n'):differences.append(option+' failed')
        if option=='--version' and raw!=b'MoonEventEval 0.1.0\n':differences.append('unexpected version')
    for index,(name,(counts,pairs)) in enumerate(EXPECTED.items()):
        command=[BINARY,'evaluate','examples/'+name+'.json','--format','json']
        if ' '.join(command) not in readme:raise ValueError('README missing '+name+' command')
        row=record([binary]+command[1:],source,output/name);rows.append(row)
        if row['exit_code']!=0 or (output/name/'stderr').read_bytes():differences.append(name+' command failed');continue
        report=machine_report((output/name/'stdout').read_bytes())
        if report['status']!='completed' or report['summary']['counts']!=counts:differences.append(name+' counts/status')
        actual={(p['reference']['id'],p['prediction']['id']) for p in report['matches']}
        if actual!=pairs or len(report['matches'])!=counts['tp']:differences.append(name+' pairs')
        if any(p['basis']['eligible'] is not True for p in report['matches']):differences.append(name+' ineligible pair')
        metrics=report['summary']
        p=counts['tp']/counts['prediction'];r=counts['tp']/counts['reference'];f=2*counts['tp']/(counts['reference']+counts['prediction'])
        if (metrics['precision'],metrics['recall'],metrics['f1'])!=(p,r,f):differences.append(name+' metrics')
        save(output/(name+'.summary.json'),metrics)
        if documentation[2*index]!=json.loads((source/'examples'/(name+'.json')).read_bytes()) or documentation[2*index+1]!=metrics:differences.append(name+' EXAMPLES drift')
    command=[BINARY,'explain-pair','examples/boundary.json','--recording','clip-01','--reference','r1','--prediction','p1','--format','json']
    if ' '.join(command) not in readme:raise ValueError('README missing explain command')
    row=record([binary]+command[1:],source,output/'explain');rows.append(row)
    if row['exit_code']!=0 or (output/'explain/stderr').read_bytes():differences.append('explain command failed')
    else:
        report=machine_report((output/'explain/stdout').read_bytes())
        expected=dict(label_match=True,onset_pass=True,offset_pass=True,eligible=True,onset_delta_s='0.2',offset_delta_s='0.2',onset_limit_s='0.2',offset_limit_s='1')
        if report.get('status')!='completed' or 'error' in report:differences.append('explain must be completed without error')
        if report['basis']!=expected or 'summary' in report or report['recording_id']!='clip-01':differences.append('explain basis')
    # Docs/API.md's first MoonBit block is the exact source exercised by the external consumer.
    import re
    api=(source/'docs/API.md').read_text();blocks=re.findall(r'```moonbit\n(.*?)```',api,re.S)
    if not blocks or blocks[0].strip()!=(ROOT/'tests/consumer/main/main.mbt').read_text().strip():differences.append('API snippet drift')
    result=dict(passed=not differences,source=str(source),product_sha256=sha(binary),commands=rows,differences=differences,
                input_sha256={name:sha(source/'examples'/ (name+'.json')) for name in EXPECTED},
                scope='actual README help/version/three JSON evaluations/boundary explanation; install command not rerun; API snippet bound to separately executed external consumer')
    save(output/'report.json',result)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,default=ROOT);p.add_argument('--bin',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();r=check(a.source,a.bin,a.output);print(json.dumps(dict(passed=r['passed'],differences=r['differences'])));return 0 if r['passed'] else 1


if __name__=='__main__':raise SystemExit(main())
