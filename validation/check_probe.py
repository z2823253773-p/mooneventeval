"""Real argv-process schema/error checks; large-byte limits belong to MoonBit tests."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--product',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();exe=args.product.resolve();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    base=dict(schema_version=1,labels=['a'],recordings=[dict(id='x',reference=[dict(id='r',label='a',onset_s='1',offset_s='2')],prediction=[])])
    cases=[('no-argument',[],2,'INVALID_ARGUMENT'),('too-many-arguments',['{}','{}'],2,'INVALID_ARGUMENT'),
           ('syntax',['{'],2,'INVALID_JSON'),('invalid-escape',['"\\uD800"'],2,'INVALID_JSON'),
           ('depth',['['*17+'0'+']'*17],3,'RESOURCE_LIMIT')]
    def add(name,doc,code):cases.append((name,[json.dumps(doc,ensure_ascii=False)],2,code))
    for key in ['schema_version','labels','recordings']:
        doc=copy.deepcopy(base);del doc[key];add('missing-'+key,doc,'MISSING_FIELD')
    for scope in ['root','config','recording','event']:
        doc=copy.deepcopy(base)
        obj=doc if scope=='root' else doc.setdefault('config',{}) if scope=='config' else doc['recordings'][0] if scope=='recording' else doc['recordings'][0]['reference'][0]
        obj['unexpected']=True;add('unknown-'+scope,doc,'UNKNOWN_FIELD')
    for field in ['onset_s','offset_s','collar_s','offset_ratio']:
        for value in [1,True,None,[],{}]:
            doc=copy.deepcopy(base)
            obj=doc['recordings'][0]['reference'][0] if field in ['onset_s','offset_s'] else doc.setdefault('config',{})
            obj[field]=value;add('type-'+field+'-'+type(value).__name__,doc,'INVALID_TYPE')
    for text in ['1e0','+1','-1',' 1','01','1.','1.0000001','NaN','１']:
        doc=copy.deepcopy(base);doc['recordings'][0]['reference'][0]['onset_s']=text
        add('decimal-'+str(len(cases)),doc,'INVALID_DECIMAL')
    for field in ['id','label','onset_s','offset_s']:
        doc=copy.deepcopy(base);del doc['recordings'][0]['reference'][0][field]
        add('event-missing-'+field,doc,'MISSING_FIELD')
    for side in ['reference','prediction']:
        doc=copy.deepcopy(base);doc['recordings'][0][side]=[copy.deepcopy(base['recordings'][0]['reference'][0])]*2
        add('duplicate-'+side,doc,'DUPLICATE_ID')
    doc=copy.deepcopy(base);doc['recordings']*=2;add('duplicate-recording',doc,'DUPLICATE_ID')
    doc=copy.deepcopy(base);doc['labels']*=2;add('duplicate-label',doc,'DUPLICATE_ID')
    doc=copy.deepcopy(base);doc['labels']=[];add('empty-labels',doc,'INVALID_SCHEMA')
    doc=copy.deepcopy(base);doc['recordings'][0]['reference'][0]['label']='b';add('unknown-label',doc,'UNKNOWN_LABEL')
    doc=copy.deepcopy(base);doc['recordings'][0]['reference'][0]['offset_s']='1';add('zero-duration',doc,'OUT_OF_RANGE')
    cases.append(('bom',['\ufeff'+json.dumps(base)],0,None))
    cases.append(('duplicate-key-last-wins',['{"schema_version":2,"schema_version":1,"labels":["a"],"recordings":[]}'],0,None))
    cases.append(('escaped-duplicate-key-last-wins',['{"schema_version":2,"schema_versio\\u006e":1,"labels":["a"],"recordings":[]}'],0,None))
    cases.append(('explicit-defaults',[json.dumps({**base,'config':{}})],0,None))
    records=[]
    for name,arguments,exit_code,code in cases:
        run=subprocess.run([str(exe),*arguments],cwd=ROOT,text=True,capture_output=True,timeout=30)
        (out/(name+'.stdout')).write_text(run.stdout);(out/(name+'.stderr')).write_text(run.stderr)
        report=json.loads(run.stdout)
        assert run.returncode==exit_code,(name,run.returncode,run.stdout)
        assert not run.stderr,(name,run.stderr)
        if code:
            assert list(report)==['schema_version','status','error'],(name,report)
            assert report['status']=='failed' and report['error']['code']==code,(name,report)
            assert report['error']['kind']==('resource' if exit_code==3 else 'input')
            assert list(report['error'])==['kind','code','message','path','limit','observed']
        else:assert report['status']=='completed'
        records.append(dict(name=name,arguments=arguments,exit_code=run.returncode,error_code=code))
    result=dict(product=str(exe),product_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),
                git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                command_scope='real argv probe only, not native file I/O',cases=records,passed=True)
    (out/'report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(process_checks=len(cases),passed=True)))


if __name__=='__main__':main()
