"""Negative control: a wrong published summary must fail even under Python -O."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--expect-rejected',action='store_true');args=parser.parse_args()
root=Path(__file__).resolve().parents[2];args.output.mkdir(parents=True,exist_ok=False)
with tempfile.TemporaryDirectory(prefix='mooneventeval-p3-opt-') as temp:
    fixture=Path(temp);(fixture/'demo').mkdir()
    readme=(root/'README.md').read_text()
    if readme.count('"precision": 0.5')!=1:raise ValueError('missing exact README fixture')
    (fixture/'README.md').write_text(readme.replace('"precision": 0.5','"precision": 0.25'))
    shutil.copy2(root/'demo/README.md',fixture/'demo/README.md')
    for name in ['demo/output','demo/inputs','examples']:
        (fixture/name).symlink_to(root/name,target_is_directory=True)
    code='''import argparse,importlib.util,pathlib,sys
spec=importlib.util.spec_from_file_location("replay",sys.argv[1]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.ROOT=pathlib.Path(sys.argv[2])
m.replay(argparse.Namespace(bin=pathlib.Path(sys.argv[3]),output=pathlib.Path(sys.argv[4]),write=False,check=True,reference_python=None))
'''
    rows={}
    for name,options in [('normal',[]),('optimized',['-O'])]:
        command=[sys.executable,*options,'-c',code,str(root/'demo/reproduce.py'),str(fixture),str(root/'_build/native/release/build/cmd/mooneventeval/mooneventeval.exe'),str(fixture/name)]
        run=subprocess.run(command,capture_output=True,timeout=120)
        (args.output/(name+'.stdout')).write_bytes(run.stdout);(args.output/(name+'.stderr')).write_bytes(run.stderr)
        rows[name]=dict(exit_code=run.returncode,rejected=run.returncode!=0)
    report=dict(expected_rejected=args.expect_rejected,results=rows)
    (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    if not rows['normal']['rejected'] or rows['optimized']['rejected']!=args.expect_rejected:
        raise ValueError('optimization negative control did not match expected pre/post behavior')
    print(json.dumps(report))
