"""Install the exact public release without a workspace; verify API, CLI and bytes.

Explicit online acceptance command, intentionally outside the offline/local gate.
No login or publication is performed. Pass the reviewed release ZIP to bind bytes.
"""
import argparse
import json
from pathlib import Path
import tempfile
import zipfile

from release_support import ROOT, WRAPPER, fresh, record, save, sha, machine_report
from package_candidate import archive_members, expected_files, validate_members

MODULE = 'z2823253773-p/mooneventeval'
VERSION = '0.1.0'

API_MAIN = r'''///|
fn main raise {
  let reference = b"filename\tonset\toffset\tevent_label\nclip.wav\t10.1\t12\talarm\n"
  let prediction = b"filename\tonset\toffset\tevent_label\nclip.wav\t10.3\t12.2\talarm\nclip.wav\t10.3\t12.2\talarm\n"
  let raw = @eventeval.import_tsv(reference, prediction).unwrap()
  let task = @eventeval.decode_task(@utf8.encode(raw)).unwrap()
  let evaluation = @eventeval.evaluate(task).unwrap()
  let counts = evaluation.metrics().counts
  assert_true(counts.tp == 1 && counts.fp == 1 && counts.fn_count == 0)
  match @eventeval.decode_task(b"{\"x\":1,\"x\":2}") {
    Err(error) => assert_true(error.code == "DUPLICATE_KEY")
    Ok(_) => fail("Duplicate JSON key accepted")
  }
  println(@eventeval.report_json(evaluation).unwrap())
}
'''


def check(archive, output):
    archive = Path(archive).resolve()
    names = archive_members(archive)
    validate_members(names, expected_files(ROOT))
    output = fresh(output)
    report = dict(passed=False, module=MODULE, version=VERSION,
                  archive_sha256=sha(archive), no_workspace=True, authenticated=False,
                  scope='developer-created native registry consumer, not external adoption', steps=[])
    save(output/'report.json', report)
    with tempfile.TemporaryDirectory(prefix='mee-registry-consumer-') as directory:
        consumer = Path(directory)
        (consumer/'moon.mod').write_text('name = "example/eventeval_registry_acceptance"\nversion = "0.0.0"\npreferred_target = "native"\n')
        def run(name, command, cwd=consumer):
            row = record(command, cwd, output/name, timeout=300)
            report['steps'].append(dict(name=name, **row))
            save(output/'report.json', report)
            if row['exit_code'] != 0 or row['timed_out']:
                raise RuntimeError('registry acceptance failed: '+name+' (see retained receipt)')
            return (output/name/'stdout').read_bytes()
        run('add', [WRAPPER, 'moon', 'add', MODULE+'@'+VERSION])
        if (consumer/'moon.work').exists():
            raise ValueError('unexpected local workspace')
        # moon add must resolve a downloaded dependency under this fresh module.
        installed = consumer/'.mooncakes'/MODULE
        with zipfile.ZipFile(archive) as package:
            actual = {str(p.relative_to(installed)) for p in installed.rglob('*') if p.is_file()}
            if actual != set(names):
                raise ValueError('installed release member set differs: '+repr(actual ^ set(names)))
            for name in names:
                if (installed/name).read_bytes() != package.read(name):
                    raise ValueError('installed/archive byte mismatch: '+name)
        report['installed_member_sha256'] = {name:sha(installed/name) for name in sorted(names)}
        for name, data in [('main/main.mbt', (ROOT/'examples/moonbit-consumer/main/main.mbt').read_text()),
                           ('main/moon.pkg', 'import { "'+MODULE+'/eventeval" }\npkgtype(kind: "executable")\n'),
                           ('api/main.mbt', API_MAIN),
                           ('api/moon.pkg', 'import { "'+MODULE+'/eventeval", "moonbitlang/core/encoding/utf8" }\npkgtype(kind: "executable")\n')]:
            path=consumer/name;path.parent.mkdir(exist_ok=True);path.write_text(data)
            saved=output/'consumer'/name;saved.parent.mkdir(parents=True,exist_ok=True);saved.write_text(data)
        for name in ['moon.mod', '.mooncakes/packages.json']:
            path=consumer/name
            if path.is_file():
                saved=output/'consumer'/name;saved.parent.mkdir(parents=True,exist_ok=True);saved.write_bytes(path.read_bytes())
        raw=run('run-api', [WRAPPER, 'moon', 'run', 'main', '--target', 'native', '--release', '--deny-warn'])
        reports=[json.loads(line) for line in raw.splitlines()]
        if len(reports)!=3:
            raise ValueError('expected evaluation, explanation and handled error')
        evaluation, explanation, failure=reports
        if evaluation['summary']['counts'] != dict(reference=1,prediction=2,tp=1,fp=1,fn=0):
            raise ValueError('wrong registry evaluation counts')
        if evaluation['matches'][0]['prediction']['id']!='p1' or evaluation['false_positives'][0]['event']['id']!='p2':
            raise ValueError('wrong duplicate prediction assignment')
        if explanation['basis']['eligible'] is not True or 'summary' in explanation:
            raise ValueError('invalid pair explanation')
        if failure['error']['code']!='INVALID_TYPE' or 'summary' in failure:
            raise ValueError('invalid Result/error handling')
        raw=run('run-tsv-and-duplicate-key', [WRAPPER, 'moon', 'run', 'api', '--target', 'native', '--release', '--deny-warn'])
        tsv=machine_report(raw)
        if tsv['summary']['counts']!=dict(reference=1,prediction=2,tp=1,fp=1,fn=0):
            raise ValueError('wrong TSV counts')
        builddir=output/'installed-cli-build'
        run('build-installed-cli', [WRAPPER, 'moon', 'build', 'cmd/mooneventeval', '--target', 'native', '--release', '--deny-warn', '--target-dir', builddir], installed)
        binary=builddir/'native/release/build/cmd/mooneventeval/mooneventeval.exe'
        for fixture, counts in [('duplicate',(1,1,0)),('greedy-trap',(2,0,0)),('boundary',(1,0,0))]:
            result=machine_report(run('cli-'+fixture, [binary,'evaluate',installed/'examples'/ (fixture+'.json'),'--format','json']))
            c=result['summary']['counts']
            if tuple(c[k] for k in ['tp','fp','fn']) != counts:
                raise ValueError('wrong installed CLI counts: '+fixture)
        report.update(passed=True, installed_members=len(names), api_reports=3,
                      tsv_and_duplicate_key=True, installed_cli_examples=3,
                      consumer_manifest=(consumer/'moon.mod').read_text())
        save(output/'report.json', report)
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    report=check(args.archive,args.output)
    print(json.dumps({k:report[k] for k in ['passed','module','version','installed_members','api_reports','installed_cli_examples']}))


if __name__=='__main__':main()
