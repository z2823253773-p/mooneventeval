from pathlib import Path
import subprocess,json,hashlib,sys
AUDIT=Path(__file__).resolve().parent;ROOT=AUDIT/'checkout';OUT=AUDIT/'nul-id-probe';OUT.mkdir()
BIN=ROOT/'_build/native/release/build/cmd/mooneventeval/mooneventeval.exe'
input=OUT/'input.json';input.write_text(json.dumps(dict(schema_version=1,labels=['a'],recordings=[dict(id='clip',reference=[dict(id='r\0',label='a',onset_s='1',offset_s='2')],prediction=[dict(id='p',label='a',onset_s='1',offset_s='2')])]),indent=2)+'\n')
def run(name,argv):
    folder=OUT/name;folder.mkdir()
    receipt=dict(argv=[str(x) for x in argv],cwd=str(ROOT))
    try:
        p=subprocess.run(receipt['argv'],cwd=ROOT,capture_output=True);stdout,stderr=p.stdout,p.stderr;receipt.update(exit_code=p.returncode,spawned=True)
    except ValueError as e:
        stdout=stderr=b'';receipt.update(exit_code=None,spawned=False,host_error=dict(type=type(e).__name__,message=str(e)))
    for label,b in [('stdout',stdout),('stderr',stderr)]:
        (folder/label).write_bytes(b);receipt[label+'_sha256']=hashlib.sha256(b).hexdigest()
    (folder/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return receipt,json.loads(stdout) if stdout else None
evalrec,report=run('evaluate',[BIN,'evaluate',input,'--format','json']);assert evalrec['exit_code']==0 and report['summary']['counts']['tp']==1 and report['matches'][0]['reference']['id']=='r\0'
base=[BIN,'explain-pair',input,'--recording','clip','--reference']
rawrec,_=run('raw-nul-selector',base+['r\0','--prediction','p','--format','json']);assert not rawrec['spawned']
escrec,error=run('escaped-selector',base+['r\\u0000','--prediction','p','--format','json']);assert escrec['exit_code']==2 and error['error']['code']=='ID_NOT_FOUND'
(OUT/'report.json').write_text(json.dumps(dict(confirmed=True,evaluation=evalrec,raw_nul_selector=rawrec,escaped_selector=escrec,consequence='Accepted ID U+0000 cannot be selected by raw argv and CLI has no escaping syntax; literal backslash-u0000 is a different ID'),indent=2)+'\n')
print(json.dumps(dict(confirmed=True,evaluation_exit=evalrec['exit_code'],raw_selector_spawned=rawrec['spawned'],escaped_selector_exit=escrec['exit_code'])))
