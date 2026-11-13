"""Fast product gate, with no reference environment or historical proof restoration.

This gate complements, and never substitutes for, scripts/verify.py.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from release_support import ROOT,WRAPPER,fresh,save,sha
from verify import run_step,check_test_protocol,require_pass_report


def inventory():
    names=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT).decode().split('\0')
    return {name:sha(ROOT/name) for name in sorted(set(names))
            if name and not name.startswith('evidence/') and (ROOT/name).is_file()}


def smoke(output):
    out=fresh(output);binary=ROOT/'_build/native/release/build/cmd/mooneventeval/mooneventeval.exe'
    report=dict(passed=False,scope='fast native product gate; no sed_eval, historical audit or registry install',
                git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),steps=[])
    save(out/'report.json',report)
    try:
        before=inventory();report['materialized_source_sha256']=before
        report['inventory_scope']='materialized checkout, excluding evidence; CI intentionally uses sparse checkout'
        py=sys.executable
        commands=[
            ('format',[WRAPPER,'moon','fmt','--check']),
            ('native-check',[WRAPPER,'moon','check','--target','native','--deny-warn']),
            ('native-tests',[WRAPPER,'moon','test','--target','native','--deny-warn']),
            ('release-build',[WRAPPER,'moon','build','cmd/mooneventeval','--target','native','--release','--deny-warn']),
            ('public-workflow-tests',[py,'-W','error::ResourceWarning','-m','unittest','discover','-s','tests','-p','test_public_workflow.py','-v']),
            ('synthetic-demo',[py,'demo/reproduce.py','--check','--output',out/'synthetic-output']),
            ('public-data',[py,'demo/public-data/reproduce.py','--check','--bin',binary,'--output',out/'public-output']),
            ('moonbit-consumer',[py,'scripts/check_consumer.py','--source',ROOT,'--output',out/'consumer-output']),
        ]
        report['required_steps']=[name for name,_ in commands]
        for name,command in commands:
            report['steps'].append(run_step(name,command,ROOT,out,{}))
        report['moon_tests']=check_test_protocol(out/'native-tests','moon',65)
        report['workflow_tests']=check_test_protocol(out/'public-workflow-tests','python',4)
        require_pass_report(out/'synthetic-output/report.json')
        public=require_pass_report(out/'public-output/report.json')
        require_pass_report(out/'consumer-output/report.json')
        if before!=inventory():raise ValueError('materialized source changed during smoke gate')
        if public['product_sha256']!=sha(binary):raise ValueError('public workflow used a different product binary')
        report.update(passed=True,product_sha256=sha(binary),public_data_product_calls=6,source_unchanged=True,
                      reference_checked=False,registry_checked=False)
    except Exception as error:report['error']=type(error).__name__+': '+str(error)
    save(out/'report.json',report)
    save(out/'SHA256SUMS.json',{str(p.relative_to(out)):sha(p) for p in sorted(out.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.json'})
    print(json.dumps({k:report.get(k) for k in ['passed','git_head','moon_tests','workflow_tests','error']}))
    return 0 if report['passed'] else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    raise SystemExit(smoke(parser.parse_args().output))
