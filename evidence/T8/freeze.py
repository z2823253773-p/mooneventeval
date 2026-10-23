"""Freeze/verify the final T8 local delivery evidence and separate review scope."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[2]
STAGE=ROOT/'evidence/T8'
MANIFEST=STAGE/'manifest.json'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_bytes())


def verify_local(folder,expected_sha):
    row=read(folder/'report.json')
    assert row['passed'] is True and row['git_head']==expected_sha and row['source_unchanged'] is True
    assert row['published'] is False and row['personal_M2']=='NOT_PERFORMED'
    assert row['remote_ci']=='NOT_RUN'
    assert len(row['required_steps'])==len(set(row['required_steps']))==len(row['steps'])==17
    assert [s['name'] for s in row['steps']]==row['required_steps']
    for step in row['steps']:
        assert step['passed'] is True and step['exit_code']==0 and step['timed_out'] is False,step['name']
        for stream in ['stdout','stderr']:assert sha(folder/step['name']/stream)==step[stream+'_sha256'],step['name']
    for name,value in read(folder/'SHA256SUMS.json').items():assert sha(folder/name)==value,name
    assert row['moon_tests']>=58 and row['python_tests']>=22 and row['validation_tests']>=41 and row['cli_tests']>=15
    assert row['toolchain']['installed_regular_files_compared']==1384
    assert row['reference_identity']['sed_eval_bytecode_verified'] is True
    assert row['reference_identity']['python_version']=='3.11.14' and row['reference_identity']['sed_eval_source_verified'] is True
    assert len(row['reference_identity']['packages'])==44
    parity=read(folder/'parity/report.json');assert parity['passed'] is True and not parity['unexplained']
    assert len(parity['cases'])==324 and parity['git_head']==expected_sha and parity['product_sha256']==row['product_sha256']
    assert {k:v['cases'] for k,v in parity['groups'].items()}==dict(binary_grid=155,decimal_nonboundary=160,exact_boundary=9)
    process_count=0
    for case in parity['cases']:
        assert not case['differences'] and len(case['transforms'])==4 and all(t['passed'] for t in case['transforms'])
        for name in ['base']+[t['operation'] for t in case['transforms']]:
            process=read(folder/'parity'/case['name']/name/'process.json')
            assert process['exit_code']==0 and not process['differences'];process_count+=1
    assert process_count==1620
    package=read(folder/'package-cases/report.json');assert package['passed'] is True and package['local_candidate_only'] and not package['published']
    archive=folder/'package-cases'/package['archive'];assert sha(archive)==package['archive_sha256']==row['archive_sha256']
    with zipfile.ZipFile(archive) as z:
        names=z.namelist();assert z.testzip() is None and len(names)==len(set(names))==38
        assert set(names)==set(package['members'])==set(package['member_sha256'])
        for name in names:
            assert hashlib.sha256(z.read(name)).hexdigest()==package['member_sha256'][name]==row['source_sha256'][name],name
        assert {'LICENSE','cmd/mooneventeval/io_stub.c','docs/API.md'}<=set(names)
    for name in ['consumer-cases','example-cases','package-cases/unpacked-consumer','package-cases/unpacked-examples']:
        artifact=read(folder/name/'report.json');assert artifact['passed'] is True and not artifact['differences'],name
    return row


def verify(meta):
    for name,value in meta['evidence_sha256'].items():assert sha(ROOT/name)==value,name
    for name,value in meta['tested_source_sha256'].items():
        data=subprocess.check_output(['git','show',meta['code_and_tested_sha']+':'+name],cwd=ROOT)
        assert hashlib.sha256(data).hexdigest()==value,name
    result=verify_local(STAGE/meta['final_local_run'],meta['code_and_tested_sha'])
    assert result['source_sha256']==meta['tested_source_sha256']
    review_root=STAGE/'independent-review';index=read(review_root/'SHA256SUMS.json')
    assert sha(review_root/'SHA256SUMS.json')==meta['review']['manifest_sha256']
    for row in index['files']:
        name=row['path'];assert sha(review_root/name)==row['sha256'] and (review_root/name).stat().st_size==row['bytes'],name
    negatives=STAGE/meta['negative_controls'];report=read(negatives/'report.json')
    assert report['passed'] is True and len(report['cases'])==5 and report['source_sha']==meta['negative_source_sha']
    assert {r['case'] for r in report['cases']}=={'missing-reference','bad-toolchain-hash','child-nonzero','missing-binary','archive-missing-license'}
    for row in report['cases']:
        assert row['passed'] is False and row['rejected_for_expected_reason'] is True
        actual=read(negatives/row['case']/'report.json');assert actual['passed'] is False and actual['error']==row['error']
        for name,value in read(negatives/row['case']/'SHA256SUMS.json').items():assert sha(negatives/row['case']/name)==value
    replay=read(STAGE/'author-cache-replay/report.json')
    assert replay['passed'] is True and replay['git_head']==meta['code_and_tested_sha'] and len(replay['cases'])==2
    for row in replay['cases']:
        assert row['expected_rejection'] is True and row['exit_code']!=0
        for stream in ['stdout','stderr']:assert sha(STAGE/'author-cache-replay'/row['name']/stream)==row[stream+'_sha256']
    for command in meta['commands']:assert sha(ROOT/command['log'])==command['log_sha256'],command['log']
    print(json.dumps(dict(passed=True,tested_sha=meta['code_and_tested_sha'],files=len(meta['evidence_sha256']),local_steps=17,qualification_calls=1620,negative_controls=5,remote_ci='NOT_RUN',published=False)))


if '--create' in sys.argv:
    assert not MANIFEST.exists(),'already frozen; do not overwrite'
    source=read(STAGE/'final-source.json');resolution=read(STAGE/'review-resolution.json')
    commands=[dict(record=str(p.relative_to(ROOT)),**read(p)) for p in sorted(STAGE.glob('20*.json'))]
    files=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','evidence/T8'],cwd=ROOT,text=True).splitlines()
    meta=dict(stage='T8',base_sha='7f325643cf12d3cab5a60f9808af3ec94d11caed',whole_branch_base='8a3075521312c9bf9ad196309422adaa0c67fbd2',
              code_and_tested_sha=source['git_head'],tested_source_sha256=source['source_sha256'],final_local_run=source['run'],
              negative_controls=source['negative_controls'],negative_source_sha=source['negative_source_sha'],review=resolution,commands=commands,
              scope='final current-cwd local native delivery gate; source commit and later documentation closeout remain distinct',
              not_proven=['remote CI/Linux runtime/new install','formal namespace/public repository/registry publication','personal M2/real user feedback/competition approval','all legal graph runtime/memory or all OS/filesystem races'],
              evidence_sha256={name:sha(ROOT/name) for name in files if (ROOT/name).is_file() and ROOT/name!=MANIFEST})
    MANIFEST.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
else:meta=read(MANIFEST)
verify(meta)
