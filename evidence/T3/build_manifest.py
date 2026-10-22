"""Build/check the T3 archival evidence manifest; source proof binds the tested commit."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[2]
FOLDER=ROOT/'evidence/T3'
MANIFEST=FOLDER/'manifest.json'
CODE_SHA='508d5cf6cc5ef637f0931bbdaae36b1729256b03'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    if args.check:
        report=json.loads(MANIFEST.read_text())
        for name,want in report['evidence_sha256'].items():assert sha(ROOT/name)==want,name
        for name,want in report['tested_source_sha256'].items():
            archived=subprocess.check_output(['git','show',CODE_SHA+':'+name],cwd=ROOT)
            assert hashlib.sha256(archived).hexdigest()==want,name
        for row in report['commands']:assert sha(ROOT/row['log'])==row['log_sha256'],row['log']
        print(json.dumps(dict(verified_evidence=len(report['evidence_sha256']),verified_tested_sources=len(report['tested_source_sha256']),verified_commands=len(report['commands']),all_match=True)))
        return
    parity=json.loads((FOLDER/'parity-final/report.json').read_text())
    process=json.loads((FOLDER/'process-final/report.json').read_text())
    controls=json.loads((FOLDER/'json-controls-final/report.json').read_text())
    assert parity['git_head']==process['git_head']==CODE_SHA
    assert parity['passed'] and not parity['unexplained'] and process['passed'] and controls['passed']
    assert len(parity['cases'])==46 and len(process['cases'])==56 and len(controls['checks'])==64
    assert parity['product_sha256']==process['product_sha256']==controls['product_sha256']
    assert sha(Path(parity['product']))==parity['product_sha256']
    for name,want in parity['source_sha256'].items():assert sha(ROOT/name)==want,name
    source_paths=sorted((ROOT/'eventeval').glob('*.mbt'))+sorted((ROOT/'cmd/probe').glob('*'))
    source_paths+=sorted((ROOT/'validation').glob('*.py'))+sorted((ROOT/'validation/tests').glob('*.py'))
    source_paths += [ROOT/'eventeval/moon.pkg',ROOT/'eventeval/pkg.generated.mbti',ROOT/'moon.mod',ROOT/'docs/toolchain.lock.json',ROOT/'scripts/with-toolchain.sh']
    sources={str(p.relative_to(ROOT)):sha(p) for p in source_paths if p.is_file()}
    for name,want in sources.items():
        assert hashlib.sha256(subprocess.check_output(['git','show',CODE_SHA+':'+name],cwd=ROOT)).hexdigest()==want,name
    commands=[]
    for path in sorted(FOLDER.glob('20*.json')):
        row=json.loads(path.read_text());assert sha(ROOT/row['log'])==row['log_sha256'],path
        commands.append(dict(record=str(path.relative_to(ROOT)),**row))
    raw_review=json.loads((FOLDER/'independent-review/manifest.json').read_text())
    for name,want in raw_review.items():assert sha(FOLDER/'independent-review'/name)==want,name
    # Only immutable receipts/snapshots are hashed. Later T4 changes to live
    # PROJECT_STATE/contracts do not invalidate this phase's historical proof.
    files=sorted(p for p in FOLDER.rglob('*') if p.is_file() and p!=MANIFEST and '__pycache__' not in p.parts)
    report=dict(stage='T3',status='implementation complete; two independent Important findings author-fixed and verified; no re-review',
        base_sha='9c78a20aaa34514e218afd7ce26cae1e0ce03046',reviewed_candidate='e9c7f317bcd141aa34dbcc3e1ee6728415be3824',code_and_tested_sha=CODE_SHA,
        public_semantics='collar-max-cardinality/v1',product_sha256=parity['product_sha256'],
        tests=dict(moonbit=38,prior_python=4,validation=29,process=56,control_process_roundtrips=64),
        prototype=dict(cases=46,common_projection_equal=43,documented_binary64_boundary_difference=1,reference_zero_collar_domain_limit=2,unexplained=0,
                       path='evidence/T3/parity-final/report.json',scope='fixed synthetic and seed20261021 binary-grid prototype, not final A11'),
        review=dict(critical=0,important=2,minor=0,important_author_fixed=2,independent_re_review=False,
                    raw_report='evidence/T3/independent-review/review.md',resolution='docs/reviews/2026-10-21-t3-review.md',
                    author_fixed_replay='evidence/T3/review-replay-fixed/review-checks.json'),
        mutations=dict(path='evidence/T3/mutations/report.json',compiled_behavioral_kills=4,
                       boundary_source_unchanged_through_final_fix=True),
        failures='Missing target APIs/oracles, pinned-toolchain diagnostics, opaque error construction, empty-label precedence, comparator loose integer equality, review JSON-control and comparator-schema regressions are retained RED/nonzero trials. Not passing runs.',
        not_proven=['personal M2 understanding','final A11 broad non-boundary corpus','explain/text/file CLI/demo','complete 16MiB and I/O boundaries','all-graph budget or wall-time guarantee','Linux/remote CI','package consumer/publishing/competition eligibility'],
        commands=commands,tested_source_sha256=sources,
        evidence_sha256={str(p.relative_to(ROOT)):sha(p) for p in files})
    MANIFEST.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(manifest=str(MANIFEST.relative_to(ROOT)),files=len(files),tested_sources=len(sources),commands=len(commands),tested_sha=CODE_SHA)))


if __name__=='__main__':main()
