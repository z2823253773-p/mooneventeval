"""Refresh delivery with the current 38-file source package; keep runtime identity."""
from pathlib import Path
import hashlib,json,subprocess,zipfile
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'evidence/P1';out=P/'delivery/MoonEventEval-0.1.0-local'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
proof=json.loads((P/'package-current/report.json').read_bytes());assert proof['passed'] and len(proof['members'])==38 and not proof['published']
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
for name,value in proof['member_sha256'].items():
 assert sha(ROOT/name)==value
 assert hashlib.sha256(subprocess.check_output(['git','show',head+':'+name],cwd=ROOT)).hexdigest()==value
source=P/'package-current'/proof['archive'];assert sha(source)==proof['archive_sha256']
(out/'source/local-mooneventeval-0.1.0.zip').write_bytes(source.read_bytes())
binding=dict(package_checkout_sha=head,archive_sha256=sha(source),member_sha256=proof['member_sha256'],scope='new public VALIDATION terminology only; original runtime/API and full17-step gate remain bound to8aa37c5')
(P/'package-source.json').write_text(json.dumps(binding,ensure_ascii=False,indent=2)+'\n')
f=out/'demo-data.json';data=json.loads(f.read_bytes());data.update(full_gate_tested_sha=data['tested_code_sha'],source_package_checkout_sha=head,source_archive_sha256=sha(source));f.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
files={str(f.relative_to(out)):sha(f) for f in sorted(out.rglob('*')) if f.is_file() and f.name!='SHA256SUMS.json'}
(out/'SHA256SUMS.json').write_text(json.dumps(files,ensure_ascii=False,indent=2)+'\n')
archive=P/'MoonEventEval-0.1.0-local.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(out.rglob('*')):
  if f.is_file():
   info=zipfile.ZipInfo('MoonEventEval-0.1.0-local/'+str(f.relative_to(out)),date_time=(2026,10,22,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=((0o100755 if f.name=='mooneventeval' else 0o100644)<<16);z.writestr(info,f.read_bytes())
f=P/'delivery-report.json';r=json.loads(f.read_bytes());r.update(delivery_zip_sha256=sha(archive),source_archive_sha256=sha(source),source_package_checkout_sha=head,full_gate_tested_sha=r['tested_code_sha']);f.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
(P/'zip-extracted-check').rename(P/'zip-extracted-check-before-source-refresh')
(P/'delivery-verified.json').rename(P/'delivery-verified-before-source-refresh.json')
print(json.dumps({'package_checkout_sha':head,'source_archive_sha256':sha(source),'final_zip_sha256':sha(archive)}))
