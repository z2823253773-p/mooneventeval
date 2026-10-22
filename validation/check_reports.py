"""External T4 renderer checks, exact time oracle and old-report byte regressions."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from validation.rational_oracle import eligible,decimal_text,number


def canonical_event(event):
    return {**event,'onset_s':decimal_text(number(event['onset_s'])),
            'offset_s':decimal_text(number(event['offset_s']))}


def unsafe(n):
    return n<32 and n!=10 or n==0x061C or 127<=n<=159 or 0x200B<=n<=0x200F or 0x2028<=n<=0x202E or 0x2060<=n<=0x206F or n==0xFEFF


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--product',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();exe=args.product.resolve();output=args.output.resolve();output.mkdir(parents=True,exist_ok=True)
    records=[]
    def run(name,document,mode=None,ids=(),expected_exit=0):
        folder=output/name;folder.mkdir(parents=True,exist_ok=True)
        text=json.dumps(document,ensure_ascii=True,separators=(',',':'))
        command=[str(exe),text]+([mode] if mode else [])+list(ids)
        result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=30)
        (folder/'input.json').write_text(text+'\n');(folder/'stdout').write_text(result.stdout);(folder/'stderr').write_text(result.stderr)
        assert result.returncode==expected_exit and not result.stderr,(name,result.returncode,result.stderr,result.stdout[:400])
        records.append(dict(name=name,mode=mode or 'evaluate-json',ids=list(ids),exit_code=result.returncode,stdout_sha256=hashlib.sha256(result.stdout.encode()).hexdigest()))
        return result.stdout
    prior=ROOT/'evidence/T3/parity-final'
    old=json.loads((prior/'report.json').read_text())
    explanations=0
    for case in old['cases']:
        name=case['case'];document=json.loads((prior/name/'input.json').read_text())
        evaluation=run('regression/'+name,document)
        assert evaluation==(prior/name/'product.stdout').read_text(),name+' changed evaluation JSON bytes'
        text=run('text/'+name,document,'report-text')
        assert not any(unsafe(ord(ch)) for ch in text),name+' unsafe raw text control'
        assert text.startswith('MoonEventEval 0.1.0') and '所选配对' in text and text.endswith('\n')
        summary=json.loads(evaluation)['summary']
        line=next(line for line in text.split('\n') if line.startswith('汇总：'))
        for label,key in [('reference','reference'),('prediction','prediction'),('TP','tp'),('FP','fp'),('FN','fn')]:
            assert f"{label}={summary['counts'][key]}" in line
        if any(summary[key] is None for key in ['precision','recall','f1']):assert '未定义' in line
        if name=='duplicate':assert 'unselected_in_maximum_matching' in text and 'candidate_count=1' in text
        for rec in document['recordings']:
            for r in rec['reference']:
                for p in rec['prediction']:
                    # OS argv cannot contain NUL; typed whitebox tests cover it.
                    ids=(rec['id'],r['id'],p['id'])
                    assert not any('\0' in value for value in ids)
                    stem=f'explanation/{name}-{explanations}'
                    raw=run(stem,document,'explain-json',ids)
                    actual=json.loads(raw)
                    assert list(actual)==['schema_version','semantics','implementation_version','status','config','recording_id','reference','prediction','basis']
                    assert type(actual['schema_version']) is int and actual['schema_version']==1
                    assert actual['semantics']=='collar-max-cardinality/v1' and actual['implementation_version']=='0.1.0' and actual['status']=='completed'
                    cfg=document.get('config',{})
                    assert actual['config']=={k:decimal_text(number(cfg.get(k,v))) for k,v in [('collar_s','0.2'),('offset_ratio','0.5')]}
                    assert actual['recording_id']==rec['id'] and actual['reference']==canonical_event(r) and actual['prediction']==canonical_event(p)
                    assert actual['basis']==eligible(r,p,cfg)
                    assert all(type(actual['basis'][key]) is bool for key in ['label_match','onset_pass','offset_pass','eligible'])
                    rendered=run(stem+'-text',document,'explain-text',ids)
                    assert not any(unsafe(ord(ch)) for ch in rendered)
                    assert '是否被选中' in rendered and '汇总：' not in rendered and '工作量：' not in rendered
                    for key in ['onset_delta_s','offset_delta_s','onset_limit_s','offset_limit_s']:
                        assert f'{key}={actual["basis"][key]}' in rendered
                    explanations+=1
    # All C0 controls in data labels, plus terminal/directional identity hazards.
    chars=[chr(i) for i in range(32)]+['\x7f','\x85','\x9b','\u061c','\u200b','\u2028','\u2029','\u202e','\u2066','\ufeff','中','\U00010000']
    for i,char in enumerate(chars):
        suffix=char if char!='\0' else 'nul-query-fallback'
        label='中文'+char;recid='clip'+suffix;rid='r'+suffix;pid='p'+suffix
        event=lambda id:dict(id=id,label=label,onset_s='1',offset_s='2')
        doc=dict(schema_version=1,labels=[label],recordings=[dict(id=recid,reference=[event(rid)],prediction=[event(pid)])])
        raw=run(f'identities/{i}-json',doc,'explain-json',(recid,rid,pid));parsed=json.loads(raw)
        assert parsed['reference']['id']==rid and parsed['reference']['label']==label
        text=run(f'identities/{i}-text',doc,'explain-text',(recid,rid,pid))
        assert not any(unsafe(ord(ch)) for ch in text)
        assert len(text.split('\n'))==9,'identity forged a line'
        decoder=json.JSONDecoder()
        reference_line=next(line for line in text.split('\n') if line.startswith('参考：'))
        start=reference_line.index('id=')+3;identity,_=decoder.raw_decode(reference_line[start:]);assert identity==rid
        start=reference_line.index(' label=')+7;identity,_=decoder.raw_decode(reference_line[start:]);assert identity==label
    doc=json.loads((ROOT/'examples/duplicate.json').read_text());rec=doc['recordings'][0]
    for key,ids in [('recording_id',('absent','r1','p1')),('reference_id',(rec['id'],'absent','p1')),('prediction_id',(rec['id'],'r1','absent'))]:
        error=json.loads(run('missing/'+key,doc,'explain-json',ids,2))
        assert error['error']['code']=='ID_NOT_FOUND' and error['error']['path']==key and error['status']=='failed'
    invalid=copy.deepcopy(doc);invalid['recordings'].append(dict(id='later-invalid',reference=[dict(id='bad',label='undeclared',onset_s='0',offset_s='1')],prediction=[]))
    error=json.loads(run('full-validation-before-lookup',invalid,'explain-json',(rec['id'],'r1','p1'),2))
    assert error['error']['code']=='UNKNOWN_LABEL'
    # Per-report repeat determinism, distinct from matching being deterministic.
    first=run('repeat-first',doc,'report-text');second=run('repeat-second',doc,'report-text');assert first==second
    report=dict(git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                product=str(exe),product_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),
                source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'eventeval').glob('*.mbt'))+sorted((ROOT/'cmd/probe').glob('*'))+[Path(__file__)] if p.is_file()},
                old_report_byte_regressions=len(old['cases']),explanation_pairs=explanations,
                identity_cases=len(chars),process_runs=len(records),cases=records,passed=True,
                scope='native argv/library renderers only; no product file CLI, no final A11')
    (output/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({key:report[key] for key in ['old_report_byte_regressions','explanation_pairs','identity_cases','process_runs','passed']}))


if __name__=='__main__':main()
