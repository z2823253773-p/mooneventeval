"""Independent JSON parser roundtrips all 32 control characters through the real probe."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--product',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();exe=args.product.resolve();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    records=[]
    for code in range(32):
        char=chr(code);label='label'+char;recid='recording'+char
        def event(id,on,off):return dict(id=id+char,label=label,onset_s=on,offset_s=off)
        doc=dict(schema_version=1,labels=[label],recordings=[dict(id=recid,
          reference=[event('r','1','2'),event('orphan-r','10','11')],
          prediction=[event('p','1','2'),event('orphan-p','20','21')])])
        for variant,document,expected_exit in [('completed',doc,0),('failed',{**doc,'unknown'+char:0},2)]:
            run=subprocess.run([str(exe),json.dumps(document)],capture_output=True,text=True,timeout=30)
            stem=f'{code:02x}-{variant}'
            (out/(stem+'.input.json')).write_text(json.dumps(document,indent=2)+'\n')
            (out/(stem+'.stdout')).write_text(run.stdout);(out/(stem+'.stderr')).write_text(run.stderr)
            assert run.returncode==expected_exit and not run.stderr,(stem,run.returncode,run.stderr)
            parsed=json.loads(run.stdout)
            if variant=='completed':
                assert parsed['summary']['counts']==dict(reference=2,prediction=2,tp=1,fp=1,fn=1)
                assert parsed['by_label'][0]['label']==label
                assert parsed['by_recording'][0]['recording_id']==recid
                assert parsed['matches'][0]['recording_id']==recid
                assert parsed['matches'][0]['reference']['id']=='r'+char
                assert parsed['matches'][0]['prediction']['id']=='p'+char
                assert parsed['false_positives'][0]['event']['id']=='orphan-p'+char
                assert parsed['false_negatives'][0]['event']['id']=='orphan-r'+char
            else:
                assert parsed['error']['code']=='UNKNOWN_FIELD'
                assert parsed['error']['path']=='unknown'+char
                assert 'summary' not in parsed and 'matches' not in parsed
            records.append(dict(control_codepoint=code,variant=variant,exit_code=run.returncode,json_roundtrip=True))
    (out/'report.json').write_text(json.dumps(dict(product=str(exe),product_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),checks=records,passed=True),indent=2)+'\n')
    print(json.dumps(dict(process_checks=len(records),all_controls_roundtrip=True)))


if __name__=='__main__':main()
