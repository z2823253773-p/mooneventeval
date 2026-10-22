"""Compile and execute an independent public-API consumer of a local module."""
import argparse
import json
from pathlib import Path
import tempfile

from release_support import ROOT,WRAPPER,fresh,record,save,sha,machine_report


def check(source,output,*,main_text=None):
    source=Path(source).resolve()
    if not (source/'moon.mod').is_file() or not (source/'eventeval/moon.pkg').is_file():
        raise ValueError('source must be the MoonEventEval module root')
    output=fresh(output)
    with tempfile.TemporaryDirectory(prefix='mee-consumer-') as directory:
        consumer=Path(directory)
        module=(ROOT/'tests/consumer/moon.mod').read_text()
        workspace='members = '+json.dumps([str(consumer),str(source)],ensure_ascii=False)+'\n'
        main=main_text if main_text is not None else (ROOT/'tests/consumer/main/main.mbt').read_text()
        # This executable imports the public product package only, and no source is copied.
        pkg=(ROOT/'tests/consumer/main/moon.pkg').read_text()
        for name,contents in [('moon.mod',module),('moon.work',workspace),('main/moon.pkg',pkg),('main/main.mbt',main)]:
            path=consumer/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(contents,encoding='utf-8')
            target=output/'consumer'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(contents,encoding='utf-8')
        build=record([WRAPPER,'moon','build','main','--target','native','--release','--deny-warn','--target-dir',consumer/'_build'],consumer,output/'build')
        run=None;parsed=None;differences=[]
        if build['exit_code']==0:
            binaries=list((consumer/'_build').rglob('main.exe'))
            save(output/'build/artifacts.json',[str(p.relative_to(consumer)) for p in binaries])
            if len(binaries)!=1:raise ValueError('expected exactly one external consumer executable')
            binary=binaries[0]
            run=record([binary],consumer,output/'run')
            if run['exit_code']!=0 or (output/'run/stderr').read_bytes():differences.append('consumer execution failed')
            else:
                try:
                    parsed=machine_report((output/'run/stdout').read_bytes())
                    if parsed['summary']['counts']!=dict(reference=1,prediction=2,tp=1,fp=1,fn=0):differences.append('wrong A1 counts')
                    if parsed['status']!='completed':differences.append('report not completed')
                except (ValueError,KeyError,TypeError) as error:differences.append(str(error))
        else:differences.append('public consumer build failed')
        report=dict(passed=not differences,source=str(source),source_manifest_sha256=sha(source/'moon.mod'),
                    public_api_sha256=sha(source/'eventeval/pkg.generated.mbti'),
                    consumer_imports=['local/mooneventeval/eventeval'],consumer_source_sha256=sha(output/'consumer/main/main.mbt'),
                    build=build,run=run,differences=differences,report=parsed,
                    scope='fresh external module with path dependency; no copied product implementation; local native only')
        save(output/'report.json',report)
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--source',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();report=check(args.source,args.output)
    print(json.dumps(dict(passed=report['passed'],differences=report['differences'])))
    return 0 if report['passed'] else 1


if __name__=='__main__':raise SystemExit(main())
