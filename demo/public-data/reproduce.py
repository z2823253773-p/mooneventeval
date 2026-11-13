"""Replay public annotations with controlled predictions through the real MoonBit CLI."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
DATA=Path(__file__).resolve().parent
SOURCE_MANIFEST_SHA256='13f1e8601520bc532d347d8cf789f216ce338fce75c7e27eb0fb65d9631e7281'
COMMAND_TIMEOUT_SECONDS=60
FIRST='1Ro0FgMWTUE_120_130.wav'
SECOND='G5wlhYFdlxw_508_518.wav'
BASE=dict(reference=11,prediction=11,tp=11,fp=0,fn=0)
REGRESSED=dict(reference=11,prediction=11,tp=9,fp=2,fn=2)


def require(condition,message):
    if not condition:raise ValueError(message)


def sha(raw):return hashlib.sha256(raw).hexdigest()


def save(path,row):path.write_text(json.dumps(row,ensure_ascii=False,indent=2,allow_nan=False)+'\n')


def verify_source(data):
    manifest=(data/'SOURCE.json').read_bytes()
    require(sha(manifest)==SOURCE_MANIFEST_SHA256,'source attribution/provenance manifest changed')
    source=json.loads(manifest)
    require(source['license']=='CC-BY-4.0' and source['doi']=='10.5281/zenodo.3588172','unexpected source/license')
    for name,want in source['sha256'].items():
        require(sha((data/name).read_bytes())==want,'input hash changed: '+name)
    raw=gzip.decompress((data/'source/public-eval.tsv.gz').read_bytes())
    require(len(raw)==source['source_bytes'] and sha(raw)==source['source_sha256'],'upstream bytes changed')
    lines=raw.splitlines(keepends=True)
    require(len(lines)-1==source['source_data_rows'],'upstream row count')
    selected=lines[0]+b''.join(lines[i-1] for i in source['selected_physical_lines'])
    require(selected==(data/'reference.tsv').read_bytes(),'reference is not the attributed upstream subset')
    require(selected==(data/'prediction-baseline.tsv').read_bytes(),'baseline is not an exact copy')
    rows=[line.decode().rstrip('\n').split('\t') for line in selected.splitlines(keepends=True)[1:]]
    require(len(rows)==11 and {row[0] for row in rows}=={FIRST,SECOND},'unexpected selected recordings')
    require(rows[1][1]=='2.618' and rows[-1][3]=='Dishes' and rows[8][3]=='Dishes','unexpected controlled mutation targets')
    rows[1][1]='2.819';rows=rows[:-1]+[rows[8].copy()]
    expected=lines[0]+''.join('\t'.join(row)+'\n' for row in rows).encode()
    require(expected==(data/'prediction-regressed.tsv').read_bytes(),'predictions do not match disclosed controlled changes')
    return source


def replay(args):
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    require(not any(out.iterdir()),'use a fresh output directory')
    report=dict(passed=False,product_calls=0,scope='public annotations with controlled predictions; not model performance or external adoption')
    save(out/'report.json',report)
    try:
        data=args.data_dir.resolve();source=verify_source(data);binary=args.bin.resolve()
        require(binary.is_file(),'build the native release CLI first')
        snapshots=data/'output';receipts=[];results={}
        report['receipts']=receipts
        def run(name,argv):
            timed_out=False
            try:
                process=subprocess.run([str(binary),*map(str,argv)],capture_output=True,timeout=COMMAND_TIMEOUT_SECONDS)
                stdout,stderr,exit_code=process.stdout,process.stderr,process.returncode
            except subprocess.TimeoutExpired as error:
                stdout,stderr,exit_code=error.stdout or b'',error.stderr or b'',None
                timed_out=True
            (out/(name+'.json')).write_bytes(stdout)
            (out/(name+'.stderr')).write_bytes(stderr)
            receipts.append(dict(name=name,args=list(map(str,argv)),exit_code=exit_code,timed_out=timed_out,
                                 stdout_sha256=sha(stdout),stderr_sha256=sha(stderr)))
            report['product_calls']=len(receipts);save(out/'report.json',report)
            require(not timed_out,'product command timed out: '+name)
            require(exit_code==0 and stderr==b'','product command failed: '+name)
            require(stdout.endswith(b'\n') and not stdout.endswith(b'\n\n'),'invalid JSON framing')
            actual=json.loads(stdout)
            if not args.write:require(stdout==(snapshots/(name+'.json')).read_bytes(),'snapshot changed: '+name)
            results[name]=actual
            return actual
        for variant in ['baseline','regressed']:
            run('task-'+variant,['import-tsv',data/'reference.tsv','--prediction',data/('prediction-'+variant+'.tsv')])
            value=run(variant,['evaluate',out/('task-'+variant+'.json'),'--format','json'])
            require(value['summary']['counts']==(BASE if variant=='baseline' else REGRESSED),'wrong '+variant+' counts')
            require(value['status']=='completed','evaluation not completed')
        task=out/'task-regressed.json'
        shift=run('explain-shift',['explain-pair',task,'--recording',FIRST,'--reference','r3','--prediction','p3','--format','json'])
        duplicate=run('explain-duplicate',['explain-pair',task,'--recording',SECOND,'--reference','r10','--prediction','p12','--format','json'])
        require(shift['basis']['onset_delta_s']=='0.201' and shift['basis']['onset_limit_s']=='0.2','wrong shift explanation')
        require(shift['basis']['eligible'] is False and shift['basis']['offset_pass'] is True,'wrong shift eligibility')
        require(duplicate['basis']['eligible'] is True,'duplicate should be eligible')
        regression=results['regressed']
        require({x['event']['id'] for x in regression['false_positives']}=={'p3','p12'},'wrong false positives')
        require({x['event']['id'] for x in regression['false_negatives']}=={'r3','r12'},'wrong false negatives')
        require(any(x['reference']['id']=='r10' and x['prediction']['id']=='p10' for x in regression['matches']),'wrong selected duplicate candidate')
        analysis='''# 公开标注接入与受控回归分析

参考来自DESED_public_eval公开事件标注的前两段完整录制，11事件、4类别。预测均为开发者受控构造，不是任何真实模型输出。

| 运行 | TP | FP | FN | Precision / Recall / F1 |
| --- | --- | --- | --- | --- |
| 原样复制参考的基线 | 11 | 0 | 0 | 1 |
| 三项受控改动 | 9 | 2 | 2 | 9/11（约0.818182） |

- 第一段录制的r3/p3：起点2.618→2.819，差0.201秒，大于0.2秒容差，终点通过但整体不合格。因此p3误检、r3漏检；应回查该事件的起点定位。
- 第二段录制的r12：预测删除了5.306–5.758秒的Dishes，形成漏检；应检查这一时间段。
- 第二段r10/p12：复制的3.448–3.698秒Dishes仍满足资格，但r10已与p10匹配，p12未选中，计重复误检。资格解释为true不等于已经配对。

工具不播放音频或修复标注。此例证明公开四列TSV可以导入、评测、解释并回查原始行，不证明完整DCASE协议兼容、实际模型质量或真实用户采用。原始来源、许可、作者和改动见SOURCE.json与NOTICE.md。
'''
        (out/'analysis.md').write_text(analysis)
        if args.write:
            snapshots.mkdir(exist_ok=True)
            for name in results:(snapshots/(name+'.json')).write_bytes((out/(name+'.json')).read_bytes())
            (snapshots/'analysis.md').write_text(analysis)
        else:require((snapshots/'analysis.md').read_text()==analysis,'analysis snapshot changed')
        report.update(passed=True,product_calls=len(receipts),product_sha256=sha(binary.read_bytes()),
                      source_license=source['license'],source_sha256=source['source_sha256'],source_commit=source['commit'],
                      selected_rows=11,recordings=2,baseline_counts=BASE,regressed_counts=REGRESSED,receipts=receipts)
        save(out/'report.json',report)
        return report
    except Exception as error:
        report.update(error=type(error).__name__+': '+str(error));save(out/'report.json',report)
        raise


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group(required=True);mode.add_argument('--check',action='store_true');mode.add_argument('--write',action='store_true')
    parser.add_argument('--data-dir',type=Path,default=DATA)
    parser.add_argument('--bin',type=Path,default=ROOT/'_build/native/release/build/cmd/mooneventeval/mooneventeval.exe')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    try:
        result=replay(args);print(json.dumps({k:result[k] for k in ['passed','product_calls','baseline_counts','regressed_counts']}));return 0
    except Exception as error:print(str(error),file=sys.stderr);return 1


if __name__=='__main__':raise SystemExit(main())
