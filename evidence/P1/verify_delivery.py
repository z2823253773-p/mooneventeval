"""Check the actual local handoff ZIP and execute its extracted binary."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib,json,os,subprocess,tempfile,zipfile
STAGE=Path(__file__).resolve().parent
bundle=STAGE/'delivery/MoonEventEval-0.1.0-local'
archive=STAGE/'MoonEventEval-0.1.0-local.zip'
sha=lambda b:hashlib.sha256(b).hexdigest()
report=json.loads((STAGE/'delivery-report.json').read_bytes())
assert sha(archive.read_bytes())==report['delivery_zip_sha256']
files=json.loads((bundle/'SHA256SUMS.json').read_bytes())
assert len(files)==18 and len(list(bundle.rglob('*')))>18
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None and len(z.namelist())==19
 for name,digest in files.items():
  data=z.read('MoonEventEval-0.1.0-local/'+name)
  assert sha(data)==digest==sha((bundle/name).read_bytes()),name
 with tempfile.TemporaryDirectory(prefix='mee-delivery-check-') as directory:
  z.extractall(directory)
  extracted=Path(directory)/'MoonEventEval-0.1.0-local';exe=extracted/'bin/mooneventeval';exe.chmod(0o755)
  assert sha(exe.read_bytes())==report['product_sha256']
  cold=[]
  for name,want in [('duplicate',(1,1,0)),('greedy-trap',(2,0,0)),('boundary',(1,0,0))]:
   p=subprocess.run([str(exe),'evaluate','examples/'+name+'.json','--format','json'],cwd=extracted,env={'PATH':'/usr/bin:/bin'},capture_output=True,timeout=10)
   assert p.returncode==0 and not p.stderr
   actual=json.loads(p.stdout);assert tuple(actual['summary']['counts'][k] for k in ['tp','fp','fn'])==want
   cold.append(dict(name=name,exit_code=p.returncode,stdout_sha256=sha(p.stdout)))
   target=STAGE/'zip-extracted-check'/name;target.mkdir(parents=True,exist_ok=False)
   (target/'stdout').write_bytes(p.stdout);(target/'stderr').write_bytes(p.stderr)
   (target/'receipt.json').write_text(json.dumps(dict(command=[str(exe),'evaluate','examples/'+name+'.json','--format','json'],cwd=str(extracted),exit_code=p.returncode,stdout_sha256=sha(p.stdout),stderr_sha256=sha(p.stderr)),indent=2)+'\n')
class Page(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.hrefs=[];self.details=0;self.pre=False;self.texts=[];self.pre_text=[]
 def handle_starttag(self,tag,attrs):
  attrs=dict(attrs)
  if 'id' in attrs:self.ids.append(attrs['id'])
  if 'href' in attrs:self.hrefs.append(attrs['href'])
  if tag=='details':self.details+=1
  if tag=='pre':self.pre=True;self.pre_text.append('')
  assert tag not in ['script','iframe','img','link','form'],tag
 def handle_endtag(self,tag):
  if tag=='pre':self.pre=False
 def handle_data(self,data):
  self.texts.append(data)
  if self.pre:self.pre_text[-1]+=data
page=Page();page.feed((bundle/'DEMO.html').read_text());page.close()
assert len(page.ids)==len(set(page.ids))==5 and page.details==5
assert all(x.startswith('#') and x[1:] in page.ids for x in page.hrefs)
actual_json=[json.loads(t) for t in page.pre_text if t.startswith('{')]
assert len(actual_json)==5
for name,counts in [('duplicate',(1,1,0)),('greedy-trap',(2,0,0)),('boundary',(1,0,0))]:
 actual=json.loads((bundle/'transcripts'/f'{name}.stdout.json').read_bytes())
 assert actual in actual_json and tuple(actual['summary']['counts'][k] for k in ['tp','fp','fn'])==counts
assert actual_json[3]['basis']['eligible'] is True
assert actual_json[4]['status']=='failed' and 'summary' not in actual_json[4]
with zipfile.ZipFile(bundle/'source/local-mooneventeval-0.1.0.zip') as z:assert z.testzip() is None and len(z.namelist())==38 and 'LICENSE' in z.namelist()
result=dict(passed=True,delivery_members=19,files_rehashed=len(files),extracted_binary_cases=cold,html_structure_passed=True,html_json_transcripts=5,visual_render_verified=False,scope='actual ZIP/extracted native binary plus offline HTML structure/content; no browser render claim')
(STAGE/'delivery-verified.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result))
