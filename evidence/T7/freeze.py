"""Freeze/verify T7 source, archive, raw process records and review bindings."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[2]
STAGE=ROOT/'evidence/T7'
MANIFEST=STAGE/'manifest.json'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_bytes())


def verify(meta):
    for name,value in meta['evidence_sha256'].items():assert sha(ROOT/name)==value,name
    for name,value in meta['tested_source_sha256'].items():
        data=subprocess.check_output(['git','show',meta['code_and_tested_sha']+':'+name],cwd=ROOT)
        assert hashlib.sha256(data).hexdigest()==value,name
    for name,row in read(STAGE/'independent-review/SHA256SUMS.json')['files'].items():
        assert sha(STAGE/'independent-review'/name)==row['sha256'],name
    assert sha(STAGE/'independent-review/SHA256SUMS.json')==meta['review']['manifest_sha256']
    commands=meta['commands']
    for row in commands:assert sha(ROOT/row['log'])==row['log_sha256'],row['log']
    assert len(meta['final_commands'])>=5
    for row in meta['final_commands']:
        assert row['exit_code']==0 and row['reason'] is None,row['command']
    for receipt in STAGE.rglob('receipt.json'):
        row=read(receipt)
        if 'stdout_sha256' not in row:continue
        for stream in ['stdout','stderr']:assert sha(receipt.parent/stream)==row[stream+'_sha256'],receipt
    source=meta['tested_source_sha256']
    package=STAGE/meta['runs']['package'];report=read(package/'report.json')
    assert report['passed'] and report['local_candidate_only'] and not report['published']
    archive=package/report['archive'];assert sha(archive)==report['archive_sha256']
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))
        assert set(z.namelist())==set(report['members'])==set(report['member_sha256'])
        assert len(z.namelist())==38
        for name in z.namelist():assert hashlib.sha256(z.read(name)).hexdigest()==report['member_sha256'][name]==source[name],name
    consumers=[STAGE/meta['runs']['consumer'],package/'unpacked-consumer']
    for folder in consumers:
        row=read(folder/'report.json');assert row['passed'] and not row['differences']
        assert row['build']['exit_code']==row['run']['exit_code']==0
        assert row['source_manifest_sha256']==source['moon.mod']
        assert row['public_api_sha256']==source['eventeval/pkg.generated.mbti']
        assert row['consumer_source_sha256']==source['tests/consumer/main/main.mbt']
        assert row['report']['summary']['counts']==dict(reference=1,prediction=2,tp=1,fp=1,fn=0)
        assert set(p.name for p in (folder/'consumer').iterdir())=={'moon.mod','moon.work','main'}
    workspace=(package/'unpacked-consumer/consumer/moon.work').read_text()
    assert 'mee-unpacked-' in workspace and str(ROOT) not in workspace
    assert report['cli_build']['exit_code']==0
    assert report['examples']['passed'] and len(report['examples']['commands'])==6 and not report['examples']['differences']
    for row in report['examples']['commands']:assert row['exit_code']==0 and not row['timed_out']
    if 'examples' in meta['runs']:
        row=read(STAGE/meta['runs']['examples']/'report.json');assert row['passed'] and not row['differences']
    replay=read(STAGE/'review-replay-external-fixed/author-receipt.json')
    assert replay['passed'] and replay['fixed_sha']==meta['code_and_tested_sha'] and not replay['independent_re_review']
    assert replay['summary']==dict(false_green=False,gate_exit_code=1,package_passed=False,actual_explanation_status='failed',scope='one serializer literal changed in a fresh source copy; real moon archive/unpack/build/run')
    assert sha(STAGE/'independent-review/scripts/replay_explanation_status.py')==replay['original_replay_script_sha256']
    print(json.dumps(dict(passed=True,tested_sha=meta['code_and_tested_sha'],files=len(meta['evidence_sha256']),archive_members=38,published=False)))


if '--create' in sys.argv:
    assert not MANIFEST.exists(),'already frozen; do not overwrite'
    source=read(STAGE/'final-source.json')
    commands=[dict(record=str(p.relative_to(ROOT)),**read(p)) for p in sorted(STAGE.glob('20*.json'))]
    meta=dict(stage='T7',base_sha='914cffd301d40eff8f4b2ecd697adb5052ebb031',code_and_tested_sha=source['git_head'],
              tested_source_sha256=source['source_sha256'],runs=source['runs'],review=read(STAGE/'review-resolution.json'),
              commands=commands,final_commands=[r for r in commands if r['record'] in source['final_command_records']],
              scope='local source candidate only; existing locked toolchain reused; independent external public API consumer and unpacked native CLI/docs checks',
              not_proven=['new toolchain download/install','other OS/architecture/remote CI','registry namespace/public repository/publication','personal M2/competition acceptance','all input graphs/OS faults'],
              evidence_sha256={name:sha(ROOT/name) for name in subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','evidence/T7'],cwd=ROOT,text=True).splitlines() if (ROOT/name).is_file() and ROOT/name!=MANIFEST})
    MANIFEST.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
else:meta=read(MANIFEST)
verify(meta)
