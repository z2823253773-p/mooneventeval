"""Development-only independent report validation and original-reference comparison."""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import random
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from validation.graph_oracle import max_cardinality
from validation.rational_oracle import eligible, decimal_text, number


def metrics(reference, prediction, tp):
    return dict(counts=dict(reference=reference,prediction=prediction,tp=tp,
                            fp=prediction-tp,fn=reference-tp),
                precision=tp/prediction if prediction else None,
                recall=tp/reference if reference else None,
                f1=2*tp/(reference+prediction) if reference+prediction else None)


def oracle_document(document):
    """Expected counts, per-group graph and bases from independent time/graph oracles."""
    cfg = document.get('config', {})
    groups = {}
    by_label = {label:[0,0,0] for label in document['labels']}
    by_recording = {}
    candidate_checks = eligible_edges = 0
    for rec in document['recordings']:
        counts = [0,0,0]
        for label in document['labels']:
            refs=sorted((e for e in rec['reference'] if e['label']==label),key=lambda e:e['id'])
            preds=sorted((e for e in rec['prediction'] if e['label']==label),key=lambda e:e['id'])
            graph=[[p for p,pred in enumerate(preds) if eligible(ref,pred,cfg)['eligible']] for ref in refs]
            tp=max_cardinality(graph,len(preds))
            groups[(rec['id'],label)]=(refs,preds,graph,tp)
            row=[len(refs),len(preds),tp]
            counts=[x+y for x,y in zip(counts,row)]
            by_label[label]=[x+y for x,y in zip(by_label[label],row)]
            candidate_checks+=len(refs)*len(preds)
            eligible_edges+=sum(map(len,graph))
        by_recording[rec['id']]=metrics(*counts)
    total=[sum(row[i] for row in by_label.values()) for i in range(3)]
    return dict(summary=metrics(*total), by_label={k:metrics(*v) for k,v in by_label.items()},
                by_recording=by_recording,groups=groups,
                candidate_checks=candidate_checks,eligible_edges=eligible_edges)


def report_shape_differences(product):
    """Validate actual JSON types/keys before semantics; never repair product output."""
    errors=[]
    def issue(path,expected,actual):
        errors.append(dict(path=path,expected=expected,actual=actual))
    def obj(value,keys,path):
        if type(value) is not dict:
            issue(path,'object',value);return False
        if list(value)!=keys:
            issue(path+'.keys',keys,list(value));return False
        return True
    def text(value,path,decimal=False):
        if type(value) is not str:
            issue(path,'string',value);return
        if decimal:
            try:canonical=decimal_text(number(value))
            except (ValueError,TypeError,OverflowError):
                issue(path,'finite canonical decimal string',value);return
            if canonical!=value:issue(path,'canonical decimal string',value)
    def integer(value,path):
        if type(value) is not int or value<0:issue(path,'nonnegative integer',value)
    def metric(value,path):
        if not obj(value,['counts','precision','recall','f1'],path):return
        counts=value['counts']
        if obj(counts,['reference','prediction','tp','fp','fn'],path+'.counts'):
            for key,val in counts.items():integer(val,path+'.counts.'+key)
        for key in ['precision','recall','f1']:
            val=value[key]
            if val is not None and (type(val) not in (int,float) or not math.isfinite(val)):
                issue(path+'.'+key,'finite number or null',val)
    def event(value,path):
        if not obj(value,['id','label','onset_s','offset_s'],path):return
        for key in ['id','label']:text(value[key],path+'.'+key)
        for key in ['onset_s','offset_s']:text(value[key],path+'.'+key,True)
    def rows(key):
        value=product[key]
        if type(value) is not list:issue(key,'array',value);return []
        return value
    keys=['schema_version','semantics','implementation_version','status','config','summary',
          'by_label','by_recording','matches','false_positives','false_negatives','work']
    if not obj(product,keys,'$'):return errors
    integer(product['schema_version'],'schema_version')
    for key in ['semantics','implementation_version','status']:text(product[key],key)
    if obj(product['config'],['collar_s','offset_ratio'],'config'):
        for key,val in product['config'].items():text(val,'config.'+key,True)
    metric(product['summary'],'summary')
    for section,identifier in [('by_label','label'),('by_recording','recording_id')]:
        for i,row in enumerate(rows(section)):
            path=f'{section}[{i}]'
            if obj(row,[identifier,'metrics'],path):
                text(row[identifier],path+'.'+identifier);metric(row['metrics'],path+'.metrics')
    for i,row in enumerate(rows('matches')):
        path=f'matches[{i}]'
        if not obj(row,['recording_id','label','reference','prediction','basis'],path):continue
        text(row['recording_id'],path+'.recording_id');text(row['label'],path+'.label')
        event(row['reference'],path+'.reference');event(row['prediction'],path+'.prediction')
        basis=row['basis']
        flags=['label_match','onset_pass','offset_pass','eligible']
        decimals=['onset_delta_s','offset_delta_s','onset_limit_s','offset_limit_s']
        if obj(basis,flags+decimals,path+'.basis'):
            for key in flags:
                if type(basis[key]) is not bool:issue(path+'.basis.'+key,'boolean',basis[key])
            for key in decimals:text(basis[key],path+'.basis.'+key,True)
    for section in ['false_positives','false_negatives']:
        for i,row in enumerate(rows(section)):
            path=f'{section}[{i}]'
            if obj(row,['recording_id','event','candidate_count','reason'],path):
                text(row['recording_id'],path+'.recording_id');event(row['event'],path+'.event')
                integer(row['candidate_count'],path+'.candidate_count');text(row['reason'],path+'.reason')
    if obj(product['work'],['candidate_checks','eligible_edges','matching_steps'],'work'):
        for key,val in product['work'].items():integer(val,'work.'+key)
    return errors


def compare_document(document: dict, product: dict, reference: dict) -> list[dict]:
    """Return discrepancies; never overwrite raw reference or product fields."""
    differences=report_shape_differences(product)
    if differences:return differences
    def diff(path,want,actual):
        differences.append(dict(path=path,expected=want,actual=actual))
    def metric(path,want,actual):
        if not isinstance(actual,dict):
            diff(path,want,actual);return
        actual_counts=actual.get('counts')
        if not isinstance(actual_counts,dict) or any(type(value) is not int for value in actual_counts.values()):
            diff(path+'.counts.types','integer counts',actual_counts)
        if actual.get('counts')!=want['counts']:
            diff(path+'.counts',want['counts'],actual.get('counts'))
        for key in ('precision','recall','f1'):
            expected=want[key]; got=actual.get(key,'missing')
            if expected is None:
                if got is not None:diff(path+'.'+key,expected,got)
            elif not isinstance(got,(int,float)) or isinstance(got,bool) or not math.isfinite(got) or abs(got-expected)>1e-12:
                diff(path+'.'+key,expected,got)
    oracle=oracle_document(document)
    required=['schema_version','semantics','implementation_version','status','config','summary',
              'by_label','by_recording','matches','false_positives','false_negatives','work']
    if list(product)!=required:diff('top_level_keys',required,list(product))
    for key,want in [('schema_version',1),('semantics','collar-max-cardinality/v1'),('implementation_version','0.1.0'),('status','completed')]:
        if product.get(key)!=want:diff(key,want,product.get(key))
    cfg=document.get('config',{})
    normalized={key:decimal_text(number(cfg.get(key,default))) for key,default in [('collar_s','0.2'),('offset_ratio','0.5')]}
    if product.get('config')!=normalized:diff('config',normalized,product.get('config'))
    metric('summary',oracle['summary'],product.get('summary'))
    for section,identifier in [('by_label','label'),('by_recording','recording_id')]:
        actual=product.get(section,[])
        wanted=sorted(oracle[section])
        if [row.get(identifier) for row in actual]!=wanted:diff(section+'.ids',wanted,actual)
        for row in actual:
            key=row.get(identifier)
            if key in oracle[section]:metric(section+'.'+key,oracle[section][key],row.get('metrics'))
    # Check exact partition of all input events and every selected basis/degree.
    expected_events={}
    degrees={}
    for (rec,label),(refs,preds,graph,_) in oracle['groups'].items():
        for side,events in [('reference',refs),('prediction',preds)]:
            for index,event in enumerate(events):
                identity=(rec,side,event['id']);expected_events[identity]=event
                degrees[identity]=len(graph[index]) if side=='reference' else sum(index in row for row in graph)
    seen=set(); group_pairs={key:0 for key in oracle['groups']}
    def use(rec,side,event):
        identity=(rec,side,event.get('id'))
        normalized=dict(event)  # Already validated; never normalize actual output.
        want=expected_events.get(identity)
        if want is not None:
            want={**want,'onset_s':decimal_text(number(want['onset_s'])),'offset_s':decimal_text(number(want['offset_s']))}
        if identity in seen or want!=normalized:diff('event_partition',want,event)
        seen.add(identity)
        return identity
    pair_order=[]
    for pair in product.get('matches',[]):
        rec=pair.get('recording_id'); r=pair.get('reference',{});p=pair.get('prediction',{})
        use(rec,'reference',r);use(rec,'prediction',p)
        if r.get('label')!=p.get('label') or pair.get('label')!=r.get('label'):diff('match.label','same labels',pair)
        if all(k in r and k in p for k in ['onset_s','offset_s','label']):
            basis=eligible(r,p,cfg)
            if not basis['eligible'] or pair.get('basis')!=basis:diff('match.basis',basis,pair.get('basis'))
        group=(rec,r.get('label'))
        if group in group_pairs:group_pairs[group]+=1
        pair_order.append((rec,pair.get('label'),r.get('id'),p.get('id')))
    if pair_order!=sorted(pair_order):diff('matches.order','sorted',pair_order)
    for section,side in [('false_positives','prediction'),('false_negatives','reference')]:
        order=[]
        for row in product.get(section,[]):
            event=row.get('event',{});identity=use(row.get('recording_id'),side,event)
            degree=degrees.get(identity)
            reason='no_eligible_candidate' if degree==0 else 'unselected_in_maximum_matching'
            if row.get('candidate_count')!=degree or row.get('reason')!=reason:diff(section+'.reason',dict(candidate_count=degree,reason=reason),row)
            order.append((row.get('recording_id'),event.get('label'),event.get('id')))
        if order!=sorted(order):diff(section+'.order','sorted',order)
    if seen!=set(expected_events):diff('event_partition','every event exactly once',sorted(set(expected_events)-seen))
    for key,want in oracle['groups'].items():
        if group_pairs[key]!=want[3]:diff('group.'+repr(key),want[3],group_pairs[key])
    work=product.get('work',{})
    for key in ['candidate_checks','eligible_edges']:
        if work.get(key)!=oracle[key]:diff('work.'+key,oracle[key],work.get(key))
    steps=work.get('matching_steps')
    if not isinstance(steps,int) or isinstance(steps,bool) or not 0<=steps<=20_000_000:diff('work.matching_steps','bounded integer',steps)
    metric('reference.projected',oracle['summary'],reference.get('projected'))
    return differences


# Prototype corpus and process driver are below; the library comparator above is
# deliberately usable without importing sed_eval or a product binary.
def prototype_cases():
    def event(id,on,off,label='alarm'):
        return dict(id=id,label=label,onset_s=on,offset_s=off)
    def doc(refs,preds,config=None,labels=None):
        result=dict(schema_version=1,labels=labels or ['alarm'],
                    recordings=[dict(id='clip-01',reference=refs,prediction=preds)])
        if config is not None:result['config']=config
        return result
    cases=[]
    for name in ['duplicate','greedy-trap','boundary']:
        cases.append((name,json.loads((ROOT/'examples'/f'{name}.json').read_text()),'decimal_boundary' if name=='boundary' else 'common'))
    fixed=[
      ('decimal-onset-binary64-flip',doc([event('r','10.1','12.1')],[event('p','10.3','12.3')]),'decimal_boundary'),
      ('E3-onset-outside',doc([event('r','10','12')],[event('p','10.200001','12.2')]),'decimal_boundary'),
      ('E4-offset-equal',doc([event('r','10','12')],[event('p','10','13')]),'decimal_boundary'),
      ('E4-offset-outside',doc([event('r','10','12')],[event('p','10','13.000001')]),'decimal_boundary'),
      ('E5-collar-dominates',doc([event('r','0','0.1')],[event('p','0.2','0.3')]),'decimal_boundary'),
      ('E6-reference-duration',doc([event('r','10','12')],[event('p','10','11')]),'decimal_boundary'),
      ('E7-fractional-microsecond',doc([event('r','10','10.000003')],[event('p','10','10.000004')],dict(collar_s='0',offset_ratio='0.5')),'zero_collar'),
      ('E7-fractional-outside',doc([event('r','10','10.000003')],[event('p','10','10.000005')],dict(collar_s='0',offset_ratio='0.5')),'zero_collar'),
      ('empty-both',doc([],[]),'common'),
      ('empty-reference',doc([],[event('p','1','2')]),'common'),
      ('empty-prediction',doc([event('r','1','2')],[]),'common'),
      ('no-edge',doc([event('r','1','2')],[event('p','3','4')]),'common'),
      ('cross-label-substitution',doc([event('r','1','2','A')],[event('p','1','2','B')],labels=['A','B','unused']),'common'),
      ('binary-grid-equal',doc([event('r','10','12')],[event('p','10.25','13')],dict(collar_s='0.25',offset_ratio='0.5')),'common'),
      ('binary-grid-outside',doc([event('r','10','12')],[event('p','10.375','13')],dict(collar_s='0.25',offset_ratio='0.5')),'common'),
      ('binary-grid-zero-ratio',doc([event('r','0','0.125')],[event('p','0.25','0.375')],dict(collar_s='0.25',offset_ratio='0')),'common'),
      ('overlap-multiple-optima',doc([event('r2','1','2'),event('r1','1','2')],[event('p3','1','2'),event('p2','1','2'),event('p1','1','2')]),'common'),
    ]
    cases+=fixed
    isolated=doc([event('r','1','2')],[])
    isolated['recordings'].append(dict(id='prediction-only',reference=[],prediction=[event('p','1','2')]))
    cases.append(('recording-isolation',isolated,'common'))
    unicode=doc([event('\U00010000','1','2','é'),event('\ue000','1','2','é'),event('r','1','2','e\u0301')],
                [event('p2','1','2','é'),event('p1','1','2','é'),event('p"\n\\','1','2','e\u0301')],labels=['é','e\u0301','\U00010000','\ue000'])
    unicode['recordings'][0]['id']='clip"\n\\'
    cases.append(('unicode-order-and-escaping',unicode,'common'))
    rng=random.Random(20261021)
    for i in range(24):
        refs=[];preds=[]
        for side,events in [('r',refs),('p',preds)]:
            for j in range(rng.randrange(0,5)):
                onset=rng.randrange(0,24)
                duration=rng.randrange(1,9)
                events.append(event(f'{side}{j}',decimal_text(number(str(onset))/8),
                                    decimal_text(number(str(onset+duration))/8),rng.choice(['A','B'])))
        cases.append((f'seed-grid-{i}',doc(refs,preds,dict(collar_s='0.25',offset_ratio='0.5'),['A','B','unused']),'common'))
    return cases


def binary64_witnesses(document):
    """Concrete exact-vs-binary candidate flips; not a blanket epsilon exemption."""
    cfg=document.get('config',{});c=float(cfg.get('collar_s','0.2'));q=float(cfg.get('offset_ratio','0.5'))
    witnesses=[]
    for rec in document['recordings']:
        for r in rec['reference']:
            for p in rec['prediction']:
                if r['label']!=p['label']:continue
                onset=abs(float(p['onset_s'])-float(r['onset_s']))
                offset=abs(float(p['offset_s'])-float(r['offset_s']))
                limit=max(c,(float(r['offset_s'])-float(r['onset_s']))*q)
                floating=onset<=c and offset<=limit
                exact=eligible(r,p,cfg)['eligible']
                if floating!=exact:
                    witnesses.append(dict(recording_id=rec['id'],reference=r['id'],prediction=p['id'],
                        exact_eligible=exact,binary64_eligible=floating,
                        binary64_onset_delta=onset.hex(),binary64_collar=c.hex(),
                        binary64_offset_delta=offset.hex(),binary64_offset_limit=limit.hex()))
    return witnesses


def run_prototype(product,output):
    from validation.sed_reference import evaluate_document
    output.mkdir(parents=True,exist_ok=True)
    records=[];unexplained=[];rng=random.Random(20261021)
    for name,document,category in prototype_cases():
        folder=output/name;folder.mkdir(exist_ok=True)
        text=json.dumps(document,ensure_ascii=False,separators=(',',':'))
        (folder/'input.json').write_text(text+'\n')
        command=[str(product),text]
        result=subprocess.run(command,text=True,capture_output=True,timeout=30)
        (folder/'product.stdout').write_text(result.stdout);(folder/'product.stderr').write_text(result.stderr)
        if result.returncode:raise RuntimeError(f'valid product case failed: {name}: {result.returncode}')
        actual=json.loads(result.stdout)
        (folder/'product.json').write_text(json.dumps(actual,ensure_ascii=False,indent=2)+'\n')
        oracle=oracle_document(document)
        serial_oracle={key:value for key,value in oracle.items() if key!='groups'}
        serial_oracle['groups']=[dict(recording_id=rec,label=label,reference=refs,prediction=preds,adjacency=graph,tp=tp)
                                  for (rec,label),(refs,preds,graph,tp) in oracle['groups'].items()]
        (folder/'rational-graph-oracle.json').write_text(json.dumps(serial_oracle,ensure_ascii=False,indent=2)+'\n')
        if category=='zero_collar':
            try:evaluate_document(document)
            except ValueError as error:
                reference=dict(domain_error=type(error).__name__,message=str(error),zero_collar_supported=False)
            else:raise RuntimeError('reference zero-collar domain changed; requalify before accepting')
            differences=compare_document(document,actual,dict(projected=oracle['summary']))
            classification='reference_domain_limit_product_checked_by_exact_oracle'
        else:
            reference=evaluate_document(document)
            (folder/'reference-original.json').write_text(json.dumps(reference,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
            differences=compare_document(document,actual,reference)
            classification='common_projection_equal'
            witnesses=binary64_witnesses(document)
            if differences and category=='decimal_boundary':
                # Boundary differences are allowed only when exact product checks
                # pass and the original TP equals an independently built float graph.
                exact_diffs=compare_document(document,actual,dict(projected=oracle['summary']))
                float_tp=0
                cfg=document.get('config',{});c=float(cfg.get('collar_s','0.2'));q=float(cfg.get('offset_ratio','0.5'))
                for rec in document['recordings']:
                    for label in document['labels']:
                        refs=[e for e in rec['reference'] if e['label']==label];preds=[e for e in rec['prediction'] if e['label']==label]
                        graph=[[i for i,p in enumerate(preds) if abs(float(p['onset_s'])-float(r['onset_s']))<=c and abs(float(p['offset_s'])-float(r['offset_s']))<=max(c,(float(r['offset_s'])-float(r['onset_s']))*q)] for r in refs]
                        float_tp+=max_cardinality(graph,len(preds))
                if not exact_diffs and witnesses and reference['projected']['counts']['tp']==float_tp and all(d['path'].startswith('reference.projected') for d in differences):
                    classification='documented_binary64_boundary_difference'
                else:unexplained.append(name)
            elif differences:unexplained.append(name)
            reference['prototype_binary64_witnesses']=witnesses
            # Original reference is independently rerun per recording. Class-wise
            # TP projection remains explicit and raw substitution is untouched.
            reference['prototype_by_recording']={rec['id']:evaluate_document({**document,'recordings':[rec]}) for rec in document['recordings']}
            if classification=='common_projection_equal':
                for recid,want in oracle['by_recording'].items():
                    got=reference['prototype_by_recording'][recid]['projected']
                    if got!=want:unexplained.append(name+':recording:'+recid)
                for label,want in oracle['by_label'].items():
                    raw=reference['class_wise'][label]['counts']
                    if tuple(int(raw[key]) for key in ['Nref','Nsys','Ntp','Nfp','Nfn'])!=tuple(want['counts'][key] for key in ['reference','prediction','tp','fp','fn']):unexplained.append(name+':label:'+label)
        if category=='zero_collar' and differences:unexplained.append(name)
        (folder/'reference.json').write_text(json.dumps(reference,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
        (folder/'comparison.json').write_text(json.dumps(dict(category=category,classification=classification,differences=differences),ensure_ascii=False,indent=2)+'\n')
        # Reorder every user-controlled array; whole machine report must be byte-identical.
        shuffled=copy.deepcopy(document);rng.shuffle(shuffled['labels']);rng.shuffle(shuffled['recordings'])
        for rec in shuffled['recordings']:
            rng.shuffle(rec['reference']);rng.shuffle(rec['prediction'])
        rerun=subprocess.run([str(product),json.dumps(shuffled,ensure_ascii=False)],text=True,capture_output=True,timeout=30)
        (folder/'reordered-input.json').write_text(json.dumps(shuffled,ensure_ascii=False,indent=2)+'\n')
        (folder/'reordered-product.stdout').write_text(rerun.stdout)
        if rerun.returncode or rerun.stdout!=result.stdout:unexplained.append(name+':input-order')
        renamed=copy.deepcopy(document)
        for rec in renamed['recordings']:
            for side in ['reference','prediction']:
                for i,e in enumerate(rec[side]):e['id']=f'renamed-{len(rec[side])-i}'
        renamed_result=subprocess.run([str(product),json.dumps(renamed,ensure_ascii=False)],text=True,capture_output=True,timeout=30)
        (folder/'renamed-input.json').write_text(json.dumps(renamed,ensure_ascii=False,indent=2)+'\n')
        (folder/'renamed-product.stdout').write_text(renamed_result.stdout)
        if renamed_result.returncode or json.loads(renamed_result.stdout)['summary']!=actual['summary']:unexplained.append(name+':rename-counts')
        records.append(dict(case=name,category=category,classification=classification,product_exit_code=result.returncode,
                            differences=len(differences),reorder_exit_code=rerun.returncode,renamed_exit_code=renamed_result.returncode,
                            reorder_byte_identical=rerun.stdout==result.stdout,renamed_counts_equal=json.loads(renamed_result.stdout)['summary']==actual['summary']))
    source_paths=list((ROOT/'eventeval').glob('*.mbt'))+list((ROOT/'cmd/probe').glob('*'))+[Path(__file__),ROOT/'validation/rational_oracle.py',ROOT/'validation/sed_reference.py',ROOT/'validation/graph_oracle.py']
    report=dict(phase='prototype',git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                product=str(product),product_sha256=hashlib.sha256(product.read_bytes()).hexdigest(),
                source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(source_paths)},
                seed=20261021,cases=records,unexplained=unexplained,
                scope='synthetic fixed/grid prototype; not broad random non-boundary corpus or final A11',
                passed=not unexplained)
    (output/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(cases=len(records),classifications={key:sum(row['classification']==key for row in records) for key in sorted({row['classification'] for row in records})},unexplained=unexplained)))
    return 0 if not unexplained else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase',choices=['prototype'],required=True)
    parser.add_argument('--product',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    raise SystemExit(run_prototype(args.product.resolve(),args.output.resolve()))
