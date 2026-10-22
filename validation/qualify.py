"""Real file-CLI qualification with exact oracle, original reference and transforms."""
import copy
import hashlib
import json
from pathlib import Path
import random
import subprocess
import traceback

from validation.compare import (ROOT, binary64_witnesses, compare_document,
                                compare_reference, oracle_document, run_file_product)
from validation.generate_cases import SEED, qualification_cases
from validation.rational_oracle import decimal_text, number


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def float_edge(r, p, cfg):
    c = float(cfg.get('collar_s', '.2')); q = float(cfg.get('offset_ratio', '.5'))
    return dict(eligible=r['label'] == p['label'] and abs(float(p['onset_s'])-float(r['onset_s'])) <= c
                and abs(float(p['offset_s'])-float(r['offset_s'])) <= max(c, (float(r['offset_s'])-float(r['onset_s']))*q))


def transformations(document, rng):
    shuffled = copy.deepcopy(document); rng.shuffle(shuffled['labels']); rng.shuffle(shuffled['recordings'])
    for rec in shuffled['recordings']:
        rng.shuffle(rec['reference']); rng.shuffle(rec['prediction'])
    shifted = copy.deepcopy(document)
    for rec in shifted['recordings']:
        for e in rec['reference'] + rec['prediction']:
            for key in ['onset_s', 'offset_s']: e[key] = decimal_text(number(e[key]) + 1)
    doubled = copy.deepcopy(document)
    doubled['recordings'] += [{**copy.deepcopy(rec), 'id': 'clone:' + rec['id']} for rec in document['recordings']]
    extra = copy.deepcopy(document)
    extra['recordings'][0]['prediction'].append(dict(id='~no-candidate', label=document['labels'][0], onset_s='2591990', offset_s='2591991'))
    return [('reordered', shuffled), ('shifted', shifted), ('doubled', doubled), ('extra-prediction', extra)]


def serialize_oracle(oracle):
    return {**{k:v for k,v in oracle.items() if k != 'groups'},
            'groups':[dict(recording_id=k[0], label=k[1], reference=v[0], prediction=v[1], adjacency=v[2], tp=v[3])
                      for k,v in oracle['groups'].items()]}


def run_qualification(product, output, cases=None):
    from validation.sed_reference import evaluate_document
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):raise FileExistsError('use a fresh empty qualification output directory')
    if cases is None: cases, excluded = qualification_cases()
    else: excluded = []
    save(output/'generation.json', dict(seed=SEED, categories={k:sum(c['category']==k for c in cases) for k in sorted({c['category'] for c in cases})},
                                       accepted=len(cases), excluded_count=len(excluded), proposed=len(cases)+len(excluded),
                                       accepted_inputs_and_margins=cases, excluded=excluded,
                                       inherited_prototype_seed=20261021,
                                       rule='Before evaluation, reject whole decimal input if any same-recording/same-label onset or offset margin <= 0.000001 seconds'))
    rng = random.Random(SEED); records = []; unexplained = []
    for case in cases:
        name=case['name']; document=case['document']; folder=output/name; folder.mkdir()
        differences=[]; classification='unexplained'; transforms=[]
        try:
            base=run_file_product(product,document,folder/'base')
            differences += base['differences']
            exact=oracle_document(document); save(folder/'exact-oracle.json',serialize_oracle(exact))
            if not differences:
                differences += compare_document(document,base['product'],dict(projected=exact['summary']))
            if not differences:
                if number(document.get('config',{}).get('collar_s','0.2')) == 0:
                    try:evaluate_document(document)
                    except ValueError as error:
                        if str(error)!='t_collar needs to be float > 0':raise
                        save(folder/'reference.json',dict(domain_error='ValueError', message=str(error), exact_collar_s='0', zero_collar_supported=False))
                        classification='reference_zero_collar_domain_limit_exact_checked'
                    else: differences.append(dict(path='reference.domain',expected='original rejects zero collar',actual='accepted'))
                else:
                    reference=evaluate_document(document); save(folder/'reference.json',reference)
                    ref_diffs=compare_reference(document,reference,exact)
                    by_rec={rec['id']:evaluate_document({**document,'recordings':[rec]}) for rec in document['recordings']}
                    save(folder/'reference-by-recording.json',by_rec)
                    for rec in document['recordings']:
                        expected=oracle_document({**document,'recordings':[rec]})
                        ref_diffs += [{**d,'recording_id':rec['id']} for d in compare_reference({**document,'recordings':[rec]},by_rec[rec['id']],expected)]
                    if not ref_diffs: classification='common_counts_and_both_defined_metrics_equal'
                    elif case['category']=='exact_boundary':
                        witnesses=binary64_witnesses(document); floating=oracle_document(document,float_edge)
                        save(folder/'binary64-witnesses.json',witnesses); save(folder/'float-oracle.json',serialize_oracle(floating))
                        float_diffs=compare_reference(document,reference,floating)
                        for rec in document['recordings']:
                            expected=oracle_document({**document,'recordings':[rec]},float_edge)
                            float_diffs += compare_reference({**document,'recordings':[rec]},by_rec[rec['id']],expected)
                        if witnesses and not float_diffs:
                            classification='documented_binary64_boundary_difference'
                            save(folder/'explained-differences.json',ref_diffs)
                        else:differences += ref_diffs + float_diffs
                    else:differences += ref_diffs
            if not differences:
                for operation, transformed in transformations(document,rng):
                    result=run_file_product(product,transformed,folder/operation)
                    ds=list(result['differences']); expected=oracle_document(transformed)
                    if not ds:ds += compare_document(transformed,result['product'],dict(projected=expected['summary']))
                    if not ds:
                        counts=result['product']['summary']['counts']; original=base['product']['summary']['counts']
                        want={k:2*v for k,v in original.items()} if operation=='doubled' else dict(original)
                        if operation=='extra-prediction':want['prediction']+=1;want['fp']+=1
                        if counts!=want:ds.append(dict(path='metamorphic.counts',expected=want,actual=counts))
                        if operation=='reordered' and result['stdout']!=base['stdout']:ds.append(dict(path='reordered.bytes',expected='identical',actual='different'))
                    differences += [{**d,'transform':operation} for d in ds]
                    transforms.append(dict(operation=operation,exit_code=result['exit_code'],passed=not ds))
        except Exception as error:
            differences.append(dict(path='runner.exception',expected='successful run',actual=repr(error)))
            (folder/'exception.txt').write_text(traceback.format_exc())
        if differences:unexplained.append(name);classification='unexplained'
        row=dict(name=name,category=case['category'],classification=classification,differences=differences,transforms=transforms)
        save(folder/'comparison.json',row);records.append(row)
    sources=sorted((ROOT/'validation').glob('*.py'))+sorted((ROOT/'eventeval').glob('*.mbt'))+sorted((ROOT/'cli').glob('*.mbt'))+sorted((ROOT/'cmd/mooneventeval').glob('*'))
    report=dict(phase='qualification',seed=SEED,git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                product=str(product),product_sha256=hashlib.sha256(product.read_bytes()).hexdigest(),
                source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources if p.is_file()},
                cases=records,unexplained=unexplained,passed=not unexplained,
                groups={g:dict(cases=sum(c['category']==g for c in records),classifications={k:sum(c['category']==g and c['classification']==k for c in records) for k in sorted({c['classification'] for c in records if c['category']==g})}) for g in sorted({c['category'] for c in records})},
                scope='synthetic fixed/seeded small graphs, original reference per base recording/class; four transforms checked by exact oracle; not personal M2/cross-platform proof')
    save(output/'report.json',report)
    print(json.dumps(dict(cases=len(records),unexplained=unexplained,classifications={k:sum(r['classification']==k for r in records) for k in sorted({r['classification'] for r in records})})))
    return int(bool(unexplained))
