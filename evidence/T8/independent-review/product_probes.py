from pathlib import Path
from fractions import Fraction
from functools import lru_cache
import hashlib,json,random,subprocess
AUDIT=Path(__file__).resolve().parent;ROOT=AUDIT/'checkout';OUT=AUDIT/'product-probes';OUT.mkdir()
BIN=ROOT/'_build/native/release/build/cmd/mooneventeval/mooneventeval.exe'
rng=random.Random(22102026);receipts=[]
def save(path,v):path.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def text(us):
    whole,part=divmod(us,1000000)
    return str(whole)+('.'+str(part).zfill(6).rstrip('0') if part else '')
def basis(r,p,cfg):
    c=Fraction(cfg['collar_s']);q=Fraction(cfg['offset_ratio']);on=Fraction(p['onset_s'])-Fraction(r['onset_s']);off=Fraction(p['offset_s'])-Fraction(r['offset_s']);lim=max(c,(Fraction(r['offset_s'])-Fraction(r['onset_s']))*q)
    flags=dict(label_match=r['label']==p['label'],onset_pass=abs(on)<=c,offset_pass=abs(off)<=lim)
    return flags,all(flags.values()),(on,off,c,lim)
def cardinality(rs,ps,cfg):
    @lru_cache(None)
    def best(i,mask):
        if i==len(rs):return 0
        result=best(i+1,mask)
        for j,p in enumerate(ps):
            if mask>>j&1==0 and basis(rs[i],p,cfg)[1]:result=max(result,1+best(i+1,mask|1<<j))
        return result
    return best(0,0)
def metrics(n,m,tp):return dict(counts=dict(reference=n,prediction=m,tp=tp,fp=m-tp,fn=n-tp),precision=tp/m if m else None,recall=tp/n if n else None,f1=2*tp/(n+m) if n+m else None)
def call(name,argv):
    folder=OUT/name;folder.mkdir();p=subprocess.run([str(x) for x in argv],cwd=ROOT,capture_output=True)
    (folder/'stdout').write_bytes(p.stdout);(folder/'stderr').write_bytes(p.stderr)
    receipt=dict(argv=[str(x) for x in argv],cwd=str(ROOT),exit_code=p.returncode,stdout_sha256=hashlib.sha256(p.stdout).hexdigest(),stderr_sha256=hashlib.sha256(p.stderr).hexdigest())
    save(folder/'receipt.json',receipt);receipts.append(receipt)
    assert p.returncode==0 and not p.stderr,(name,receipt)
    assert p.stdout.endswith(b'\n') and not p.stdout.endswith(b'\n\n') and b'\r' not in p.stdout
    return json.loads(p.stdout),p.stdout
labels=['A','\ue000','\U00010000','e\u0301','é','q\n\"\\\x00'];ids=['\U00010000','\ue000','id\n\"\\\x00','0','😀']
records=[]
for k in range(48):
    cfg=dict(collar_s=rng.choice(['0','0.000001','0.000003','0.2','2592000']),offset_ratio=rng.choice(['0','0.000001','0.333333','0.5','1']))
    recs=[]
    for ri in range(2):
        sides=[]
        for si in range(2):
            events=[]
            for j in range(rng.randrange(5)):
                start=rng.choice([0,1,999999,1000000,2591998000000])+rng.randrange(7)
                end=start+rng.choice([1,3,1000000,1999993]);end=min(end,2592000000000)
                events.append(dict(id=ids[j],label=labels[rng.randrange(len(labels))],onset_s=text(start),offset_s=text(end)))
            sides.append(events)
        recs.append(dict(id=['\U00010000','\ue000'][ri],reference=sides[0],prediction=sides[1]))
    document=dict(schema_version=1,labels=labels,config=cfg,recordings=recs)
    inp=OUT/f'input-{k:02d}.json';save(inp,document)
    actual,raw=call(f'evaluate-{k:02d}',[BIN,'evaluate',inp,'--format','json'])
    n=sum(len(r['reference']) for r in recs);m=sum(len(r['prediction']) for r in recs);tp=sum(cardinality(r['reference'],r['prediction'],cfg) for r in recs)
    assert actual['summary']==metrics(n,m,tp),(k,actual['summary'],metrics(n,m,tp))
    assert [r['label'] for r in actual['by_label']]==sorted(labels)
    assert [r['recording_id'] for r in actual['by_recording']]==sorted(r['id'] for r in recs)
    for rec in recs:
        got=next(row['metrics'] for row in actual['by_recording'] if row['recording_id']==rec['id'])
        assert got==metrics(len(rec['reference']),len(rec['prediction']),cardinality(rec['reference'],rec['prediction'],cfg))
        for i,r in enumerate(rec['reference']):
            for j,p in enumerate(rec['prediction']):
                if '\x00' in r['id'] or '\x00' in p['id']:continue
                explanation,_=call(f'explain-{k:02d}-{recs.index(rec)}-{i}-{j}',[BIN,'explain-pair',inp,'--recording',rec['id'],'--reference',r['id'],'--prediction',p['id'],'--format','json'])
                want,ok,numbers=basis(r,p,cfg);b=explanation['basis']
                assert explanation['status']=='completed' and 'summary' not in explanation and 'work' not in explanation
                assert {x:b[x] for x in want}==want and b['eligible']==ok
                assert tuple(Fraction(b[x]) for x in ['onset_delta_s','offset_delta_s','onset_limit_s','offset_limit_s'])==numbers
    # Check actual selected events and complete side partition independently.
    used=set()
    for pair in actual['matches']:
        rec=next(r for r in recs if r['id']==pair['recording_id']);r=pair['reference'];p=pair['prediction']
        assert r in rec['reference'] and p in rec['prediction'] and basis(r,p,cfg)[1]
        for side,e in [('reference',r),('prediction',p)]:
            key=(rec['id'],side,e['id']);assert key not in used;used.add(key)
    for section,side in [('false_negatives','reference'),('false_positives','prediction')]:
        for row in actual[section]:
            rec=next(r for r in recs if r['id']==row['recording_id']);assert row['event'] in rec[side]
            key=(rec['id'],side,row['event']['id']);assert key not in used;used.add(key)
    assert len(used)==n+m
    records.append(dict(case=k,counts=actual['summary']['counts'],config=cfg))
save(OUT/'report.json',dict(passed=True,cases=records,processes=len(receipts),seed=22102026,oracle='independent Fraction eligibility + memoized subset cardinality; actual pair membership/partition; all same-recording pair explanations',product_sha256=hashlib.sha256(BIN.read_bytes()).hexdigest()))
print(json.dumps(dict(passed=True,cases=len(records),processes=len(receipts))))
