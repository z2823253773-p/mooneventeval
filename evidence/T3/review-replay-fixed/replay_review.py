"""Read-only reviewer checks; product argv bytes and comparator mutation receipts."""
import copy, hashlib, json, pathlib, subprocess, sys
out=pathlib.Path(__file__).resolve().parent
src=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else out/'source'
exe=src/'_build/native/release/build/cmd/probe/probe.exe'
sys.path.insert(0,str(src))
from validation.compare import compare_document
results=[]
base=dict(schema_version=1,labels=['a'],recordings=[])
for code in range(32):
    text=json.dumps({**base,'labels':[chr(code)]},ensure_ascii=True)
    p=subprocess.run([str(exe),text],capture_output=True)
    name=f'label-control-{code:02x}'
    (out/(name+'.input.json')).write_text(text+'\n')
    (out/(name+'.stdout')).write_bytes(p.stdout);(out/(name+'.stderr')).write_bytes(p.stderr)
    try: json.loads(p.stdout);parsed=True
    except Exception: parsed=False
    results.append(dict(name=name,command=[str(exe),text],exit_code=p.returncode,valid_json=parsed))
text=json.dumps({**base,'\x01':0})
p=subprocess.run([str(exe),text],capture_output=True)
(out/'unknown-control.input.json').write_text(text+'\n');(out/'unknown-control.stdout').write_bytes(p.stdout);(out/'unknown-control.stderr').write_bytes(p.stderr)
try: json.loads(p.stdout);parsed=True
except Exception:parsed=False
results.append(dict(name='unknown-control',command=[str(exe),text],exit_code=p.returncode,valid_json=parsed))
# Independent mutation of correct product output to probe comparator rejection.
p=subprocess.run([str(exe),json.dumps(base)],capture_output=True,check=True)
correct=json.loads(p.stdout);reference={'projected':correct['summary']}
mutations=[]
for name,alter in [
 ('schema_version_boolean',lambda d:d.update(schema_version=True)),
 ('work_count_boolean',lambda d:d['work'].update(candidate_checks=False)),
 ('work_count_float',lambda d:d['work'].update(eligible_edges=0.0)),
 ('summary_extra_key',lambda d:d['summary'].update(unexpected=42)),
 ('row_extra_key',lambda d:d['by_label'][0].update(unexpected=42)),
 ('work_extra_key',lambda d:d['work'].update(unexpected=42)),
 ('work_wrong_step',lambda d:d['work'].update(matching_steps=1)),
]:
 d=copy.deepcopy(correct);alter(d);diffs=compare_document(base,d,reference)
 mutations.append(dict(name=name,differences=diffs,accepted=not diffs,product=d))
# Event time normalization also must be enforced by a canonical report checker.
event=dict(id='r',label='a',onset_s='1',offset_s='2')
doc={**base,'recordings':[dict(id='x',reference=[event],prediction=[])]}
p=subprocess.run([str(exe),json.dumps(doc)],capture_output=True,check=True)
d=json.loads(p.stdout);d['false_negatives'][0]['event']['onset_s']=1
mutations.append(dict(name='numeric_event_time',differences=compare_document(doc,d,{'projected':d['summary']}),product=d))
report=dict(product_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),cases=results,malformed_success=sum(x['exit_code']==0 and not x['valid_json'] for x in results),comparator_mutations=mutations)
(out/'review-checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'malformed_success':report['malformed_success'],'malformed_error':not results[-1]['valid_json'],'comparator_mutations_accepted':[(x['name'],not x['differences']) for x in mutations]}))
