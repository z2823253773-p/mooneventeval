"""Freeze once / verify T6 command, source and scientific-evidence bindings."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
STAGE=ROOT/'evidence/T6';MANIFEST=STAGE/'manifest.json'


def digest(data):return hashlib.sha256(data).hexdigest()


def read(path):return json.loads(path.read_bytes())


def verify(report):
    for name,value in report['evidence_sha256'].items():assert digest((ROOT/name).read_bytes())==value,name
    sha=report['code_and_tested_sha'];source=report['tested_source_sha256'];binary=report['product_sha256']
    for name,value in source.items():assert digest(subprocess.check_output(['git','show',f'{sha}:{name}'],cwd=ROOT))==value,name
    for row in report['commands']:assert digest((ROOT/row['log']).read_bytes())==row['log_sha256'],row['log']
    review=STAGE/'independent-review'
    assert digest((review/'SHA256SUMS.json').read_bytes())=='54d8861997d86125756e62dcb2483ad119eeafc8606d64f3c872bb525fbb57dd'
    for name,value in read(review/'SHA256SUMS.json').items():assert digest((review/name).read_bytes())==value,name
    paths=report['runs'];parity=STAGE/paths['parity'];r=read(parity/'report.json')
    assert r['passed'] and not r['unexplained'] and r['git_head']==sha and r['product_sha256']==binary
    assert len(r['cases'])==324 and {k:v['cases'] for k,v in r['groups'].items()}==dict(binary_grid=155,decimal_nonboundary=160,exact_boundary=9)
    for name,value in r['source_sha256'].items():assert source[name]==value,name
    generation=read(parity/'generation.json');assert generation['seed']==20261020 and generation['excluded_count']==10 and generation['proposed']==334
    process_count=0
    for case in r['cases']:
        assert not case['differences'] and len(case['transforms'])==4 and all(t['passed'] for t in case['transforms']),case['name']
        for name in ['base']+[t['operation'] for t in case['transforms']]:
            folder=parity/case['name']/name;row=read(folder/'process.json');assert row['exit_code']==0 and not row['differences']
            for stream in ['stdout','stderr']:assert digest((folder/stream).read_bytes())==row[stream+'_sha256'],folder
            assert not (folder/'stderr').read_bytes();process_count+=1
    assert process_count==1620
    perf=read(STAGE/paths['performance']/'report.json');assert perf['passed'] and perf['git_head']==sha and perf['product_sha256']==binary
    for case in perf['cases']:
        assert len(case['samples'])==3
        for i,row in enumerate(case['samples']):
            assert row['exit_code']==0 and not row['timed_out'] and row['peak_rss_bytes']>0
            assert digest((STAGE/paths['performance']/case['name']/str(i)/'stdout').read_bytes())==row['stdout_sha256']
            comparison=read(STAGE/paths['performance']/case['name']/str(i)/'comparison.json');assert comparison['passed'] and not comparison['differences']
            if case['name']=='sparse':assert row['wall_seconds']<5
    fault_root=STAGE/paths['faults'];faults=read(fault_root/'report.json')
    assert faults['passed'] and faults['production_binary_sha256']==binary and faults['production_source_sha256']==source['cmd/mooneventeval/io_stub.c']
    assert len(faults['cases'])==9
    for row in faults['cases']:
        folder=fault_root/row['name'];assert row['exit_code']==row['expected_exit'] and row['syscalls']['live_input_fds']==0
        assert digest((folder/'stdout').read_bytes())==row['stdout_sha256']
        assert digest((folder/'instrumented-io_stub.c').read_bytes())==row['instrumented_source_sha256']
    mutations=read(STAGE/paths['mutations']/'report.json')
    assert mutations['passed'] and mutations['status_counts']==dict(invalid=0,equivalent=1,survived=0,killed=6)
    for row in mutations['cases']:
        assert row['compiled'] and row['control_exit']==row['restored_exit']==0
        assert row['baseline_sha256']==row['restored_sha256']
        assert row['mutant_exit']!=0 if row['status']=='killed' else row['mutant_exit']==0
    cli=STAGE/paths['cli'];assert read(cli/'product.json')['sha256']==binary
    for path in cli.glob('*/receipt.json'):
        row=read(path)
        for stream in ['stdout','stderr']:assert digest((path.parent/stream).read_bytes())==row[stream+'_sha256']
    replay=read(STAGE/'review-replay-fixed/report.json')
    assert replay['passed'] and replay['git_head']==sha and replay['product_sha256']==binary and not replay['independent_re_review']
    assert len(replay['cases'])==5 and all(r['rejected_for_expected_reason'] and r['exit_code']!=0 for r in replay['cases'])
    print(json.dumps(dict(passed=True,tested_sha=sha,evidence_files=len(report['evidence_sha256']),qualification_processes=process_count)))


if '--create' in sys.argv:
    assert not MANIFEST.exists(),'already frozen; do not overwrite'
    source=read(STAGE/'final-source.json');resolution=read(STAGE/'review-resolution.json')
    commands=[dict(record=str(p.relative_to(ROOT)),**read(p)) for p in sorted(STAGE.glob('20*.json'))]
    report=dict(stage='T6',base_sha='b8cf27d02fa34a007185e15c23ea19bd0e412b4a',reviewed_candidate='fb4de0bbb28f0bed48d0529db6ebc946027a2a81',
                code_and_tested_sha=source['git_head'],product_sha256=source['product_sha256'],tested_source_sha256=source['source_sha256'],
                runs=source['runs'],review=resolution,commands=commands,
                qualification_scope='315 grid/safe-decimal bases common;9 exact boundary bases separate;4 exact-oracle transforms each; synthetic local native only',
                not_proven=['personal M2/spoken demo','all legal inputs/time/memory guarantee','all possible OS/filesystem/concurrency faults','Linux/remote CI','package consumer/publishing/competition eligibility'],
                evidence_sha256={str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in sorted(STAGE.rglob('*')) if p.is_file() and p!=MANIFEST and '__pycache__' not in p.parts})
    MANIFEST.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
else:report=read(MANIFEST)
verify(report)
