from pathlib import Path
import json,sys,hashlib,subprocess,collections
root=Path(__file__).resolve().parent;source=root/'source';ev=root/'evidence';sys.path.insert(0,str(source))
from validation.generate_cases import qualification_cases
from validation.rational_oracle import eligible
rows=[]
for population in ['performance-cases','negative-benchmark']:
 for name in ['sparse','dense','chain']:
  folder=ev/population/name;doc=json.loads((folder/'input.json').read_bytes());r={e['id']:e for e in doc['recordings'][0]['reference']};p={e['id']:e for e in doc['recordings'][0]['prediction']}
  for i in range(3):
   actual=json.loads((folder/str(i)/'stdout').read_bytes());pairs=actual['matches']
   invalid=[dict(reference=m['reference']['id'],prediction=m['prediction']['id'],basis=m['basis']) for m in pairs if not eligible(m['reference'],m['prediction'],doc['config'])['eligible']]
   foreign=[m for m in pairs if m['reference']!=r.get(m['reference']['id']) or m['prediction']!=p.get(m['prediction']['id']) or m['recording_id']!='x' or m['label']!='a']
   rows.append(dict(population=population,case=name,trial=i,invalid_pairs=invalid,foreign_events=len(foreign)))
cases,excluded=qualification_cases();maxr=maxp=0
for c in cases:
 for rec in c['document']['recordings']:
  for lab in c['document']['labels']:
   maxr=max(maxr,sum(e['label']==lab for e in rec['reference']));maxp=max(maxp,sum(e['label']==lab for e in rec['prediction']))
report=json.loads((ev/'parity-cases/report.json').read_bytes());processes=list((ev/'parity-cases').glob('*/*/process.json'))
summary=dict(performance_audit=rows,corpus=dict(accepted=len(cases),excluded=len(excluded),categories=dict(collections.Counter(c['category'] for c in cases)),max_base_graph=[maxr,maxp],saved_process_receipts=len(processes),all_processes_exit_zero=all(json.loads(p.read_bytes())['exit_code']==0 for p in processes),transforms=sum(len(r['transforms']) for r in report['cases'])),negative_outputs={})
for name in ['no-lf','crlf','duplicate-output-key','nan-output','timeout']:
 folder=ev/('negative-'+name);raw=folder/'baseline/base/stdout';report=folder/'report.json';summary['negative_outputs'][name]=dict(report_exists=report.exists(),comparison_exists=(folder/'baseline/comparison.json').exists(),stdout_exists=raw.exists(),process_exists=(folder/'baseline/base/process.json').exists(),passed=json.loads(report.read_bytes())['passed'] if report.exists() else None,tail_hex=raw.read_bytes()[-12:].hex() if raw.exists() else None)
summary['source_files_checked']=0;summary['source_mismatches']=[]
sha='fb4de0bbb28f0bed48d0529db6ebc946027a2a81';original=Path('/Users/henryz/Desktop/比赛/mooneventeval-t0')
for row in subprocess.check_output(['git','ls-tree','-r',sha,'validation','eventeval','cli','cmd','scripts','docs','moon.mod','tests'],cwd=original,text=True).splitlines():
 meta,name=row.split('\t');oid=meta.split()[2];path=source/name
 if not path.exists():continue
 digest=subprocess.check_output(['git','hash-object','--stdin'],input=path.read_bytes(),cwd=original,text=False).decode().strip();summary['source_files_checked']+=1
 if digest!=oid:summary['source_mismatches'].append(name)
exe=source/'_build/native/release/build/cmd/mooneventeval/mooneventeval.exe';summary['product_sha256']=hashlib.sha256(exe.read_bytes()).hexdigest()
(ev/'independent-audit.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k!='performance_audit'},ensure_ascii=False,indent=2))
print('invalid pairs by population',dict(collections.Counter({pop:sum(len(r['invalid_pairs']) for r in rows if r['population']==pop) for pop in ['performance-cases','negative-benchmark']})))
