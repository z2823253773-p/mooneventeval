"""Assemble a local handoff from tested bytes and real copied-binary calls.
This is a delivery artifact generator, not product code or personal demo proof.
"""
from pathlib import Path
import hashlib,html,json,os,shutil,subprocess,time,zipfile
ROOT=Path(__file__).resolve().parents[2]
STAGE=ROOT/'evidence/P1'
OUT=STAGE/'delivery/MoonEventEval-0.1.0-local'
assert not OUT.exists(),'fresh artifact directory required'
OUT.mkdir(parents=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,data):
 p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True)
 p.write_bytes(data.encode('utf-8') if isinstance(data,str) else data)
def pretty(value):return json.dumps(value,ensure_ascii=False,indent=2)+'\n'
source=json.loads((ROOT/'evidence/T8/final-source.json').read_bytes())
final=json.loads((ROOT/'evidence/T8/final-local/report.json').read_bytes())
assert final['passed'] is True and final['product_sha256']==source['product_sha256']
binary=ROOT/'_build/native/release/build/cmd/mooneventeval/mooneventeval.exe'
assert sha(binary)==final['product_sha256']
write('bin/mooneventeval',binary.read_bytes());(OUT/'bin/mooneventeval').chmod(0o755)
archive=ROOT/'evidence/T8/final-local/package-cases/local-mooneventeval-0.1.0.zip'
assert sha(archive)==final['archive_sha256']
write('source/local-mooneventeval-0.1.0.zip',archive.read_bytes())
for name in ['duplicate','greedy-trap','boundary']:
 write('examples/'+name+'.json',(ROOT/'examples'/f'{name}.json').read_bytes())
for name in ['LICENSE','THIRD_PARTY_NOTICES.md','LICENSES/moonbit-core-LICENSE','LICENSES/moonbit-core-NOTICE']:
 write(name,(ROOT/name).read_bytes())
# Cold cwd is the delivery folder, with no MoonBit/reference environment variables.
# Only the executable and the copied JSON inputs are needed for these calls.
raw=STAGE/'copied-binary';raw.mkdir(exist_ok=False)
calls=[]
def call(name,args,want):
 argv=[str(OUT/'bin/mooneventeval'),*args]
 started=time.monotonic();p=subprocess.run(argv,cwd=OUT,env={'PATH':'/usr/bin:/bin','LANG':'en_US.UTF-8'},capture_output=True,timeout=10)
 elapsed=time.monotonic()-started
 folder=raw/name;folder.mkdir()
 for n,b in [('stdout',p.stdout),('stderr',p.stderr)]: (folder/n).write_bytes(b)
 row=dict(name=name,argv=argv,cwd=str(OUT),exit_code=p.returncode,elapsed_seconds=elapsed,stdout_sha256=sha(folder/'stdout'),stderr_sha256=sha(folder/'stderr'))
 (folder/'receipt.json').write_text(pretty(row))
 assert p.returncode==want,(name,p.returncode,p.stderr)
 assert not p.stderr,(name,p.stderr)
 actual=json.loads(p.stdout)
 safe=dict(name=name,command=['bin/mooneventeval',*args],exit_code=p.returncode,elapsed_seconds=elapsed,stdout_sha256=row['stdout_sha256'],stderr_sha256=row['stderr_sha256'],result=actual)
 write('transcripts/'+name+'.stdout.json',p.stdout)
 calls.append(safe);return actual
for name,want in [('duplicate',(1,1,0)),('greedy-trap',(2,0,0)),('boundary',(1,0,0))]:
 actual=call(name,['evaluate','examples/'+name+'.json','--format','json'],0)
 assert tuple(actual['summary']['counts'][k] for k in ['tp','fp','fn'])==want
basis=call('boundary-explain',['explain-pair','examples/boundary.json','--recording','clip-01','--reference','r1','--prediction','p1','--format','json'],0)['basis']
assert basis['eligible'] is True and basis['onset_delta_s']==basis['onset_limit_s']=='0.2'
error=call('missing-file',['evaluate','examples/missing.json','--format','json'],2)
assert error['status']=='failed' and error['error']['code']=='FILE_ERROR' and 'summary' not in error
identity=dict(name='MoonEventEval',version='0.1.0',scope='local engineering handoff, synthetic examples, agent-run transcripts; not a public release or personal explanation',
 tested_code_sha=final['git_head'],demo_checkout_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
 native_platform='Darwin arm64; no Linux/Windows runtime qualification',binary_sha256=sha(OUT/'bin/mooneventeval'),source_archive_sha256=sha(archive),
 acceptance=dict(local_steps=17,moon_tests=58,python_tests=22,validation_tests=42,cli_tests=15,qualification_bases=324,product_calls=1620,source_archive_members=38),
 remote_ci='NOT_RUN',published=False,personal_explanation='NOT_PERFORMED',user_manual_retest='WAIVED_BY_USER_2026-10-22',calls=calls)
write('demo-data.json',pretty(identity))
write('START_HERE.md','''# MoonEventEval 本地交付包

直接打开 DEMO.html 查看三个案例、增广路径和本轮真实输出。不需要安装网页依赖，也不连接网络。它是代理执行的离线实录，不是用户本人演示。

本机运行（仅已验证 macOS arm64）：

```sh
bin/mooneventeval evaluate examples/duplicate.json --format json
bin/mooneventeval evaluate examples/greedy-trap.json --format text
bin/mooneventeval explain-pair examples/boundary.json --recording clip-01 --reference r1 --prediction p1 --format text
```

若解压工具未保留权限，执行 chmod +x bin/mooneventeval。不要绕过系统安全警告；其他Mac或其他平台并未实测。source/内为已验收38文件源候选；源码归档带有README、安装工具链说明和完整许可。

用户已取消自行复测，工程验收由Codex完成；这不表示参赛者已亲自讲解或已通过官方审核。公开仓库、Linux/远端CI、正式namespace/URL和发布未完成。

源与binary身份、当前五次复制binary调用在demo-data.json，原样输出在transcripts/；每个交付文件摘要在SHA256SUMS.json。当前输入只支持JSON字符串时间，重名键last-wins，NUL ID不能由literal CLI参数选中，超时部分输出取证有历史缺口。
''')
write('TECHNICAL_FACTS.md','''# 技术事实与讲解提纲

AI辅助事实材料，不是本人原创申报书或本人答辩记录。

问题：参考事件与预测事件数量不同时，先建立合法事件对，再得到TP/FP/FN。重复预测不去重，未被一对一匹配选中的预测仍是FP。

资格：同录制、同类，起点差绝对值不大于collar，终点差不大于max(collar,参考时长×offset_ratio)。时间是十进制字符串，内部Int64微秒/ppm交叉乘法，无epsilon。

最大匹配：每组规范排序后，先找空闲预测，必要时显式栈DFS增广并重写路径。trap案例三边为r1-p1、r1-p2、r2-p1；不可回退贪心取r1-p1只得1，增广后得r1-p2、r2-p1共2。原版sed_eval optimal在该例也得2，不宣称算法首创或超越它。

解释：explain-pair仅解释指定两事件是否合格，不代表这对已被全局匹配选中。重复案例p2合格仍可能是FP。总TP为各组最大配对数之和；FP=预测总数-TP，FN=参考总数-TP。微平均汇总计数后计算；空分母为null。

边界：10.2-10=0.2，等号通过；起点再多1微秒应不通过。参考[10,12]时长2，ratio=0.5，终点阈值max(0.2,1)=1。JSON时间数字拒绝；字符串不经Float64判断。

取舍：最大化配对数，不优化误差；等价最大匹配可因ID改变具体身份；20M共享工作预算用尽整任务失败。合成数据限定验证，不承诺所有合法图的耗时/内存、全部平台或真实数据普遍兼容。Python只作开发参考，产品业务在MoonBit，C负责I/O。

工程门：17步、58 Moon/22 Python/42验证/15 CLI，324base及1296变形、38文件解包消费。315非边界共同口径一致；9边界中6一致、1具体binary64差异、2原版零collar域限制。身份绑定见demo-data.json；并非1620次原版对照。
''')
# Simple offline document: native details/anchors, no JS, external resources, or app.
E=html.escape
parts=[]
labels={'duplicate':('01','重复预测','一条参考、两条预测 → TP 1 · FP 1 · FN 0','合格不等于被选中；重复预测不会被去重。'),
 'greedy-trap':('02','增广路径','三条候选边 → 最大配对数 2','朴素贪心可能只得到1；sed_eval optimal在此例也得到2。'),
 'boundary':('03','精确边界','10.2 − 10 = 0.2 → 等号通过','微秒/ppm整数比较，无epsilon；终点容差取max(collar,参考时长×比例)。')}
for name in ['duplicate','greedy-trap','boundary','boundary-explain','missing-file']:
 row=next(x for x in calls if x['name']==name)
 if name in labels:
  num,title,headline,desc=labels[name]
 else:num,title,headline,desc=('04','边界解释','起点偏差 0.2 / 阈值 0.2','该指定事件对eligible=true，不作全局匹配身份承诺。') if name=='boundary-explain' else ('05','失败也有协议','缺文件 → exit 2 · FILE_ERROR','失败输出没有summary或部分分数。')
 parts.append('<section id="'+name+'"><p class="eyebrow">'+num+' / '+title+'</p><h2>'+headline+'</h2><p>'+desc+'</p><pre class="cmd">$ '+E(' '.join(row['command']))+'</pre><details><summary>展开实际JSON输出 · exit '+str(row['exit_code'])+'</summary><pre>'+E(pretty(row['result']))+'</pre></details></section>')
graph='''<section><p class="eyebrow">增广路径 / 算法讲解</p><h2>从一次选择，找到两个配对</h2><svg viewBox="0 0 620 220" role="img" aria-label="三条边r1-p1、r1-p2、r2-p1。最终选择r1-p2和r2-p1。"><path d="M100 55H510" stroke="#b8b6b0" stroke-width="2" stroke-dasharray="6 6"/><path d="M100 55L510 165M100 165L510 55" stroke="#16876c" stroke-width="5"/><g fill="#fff" stroke="#212925" stroke-width="2"><circle cx="100" cy="55" r="28"/><circle cx="100" cy="165" r="28"/><circle cx="510" cy="55" r="28"/><circle cx="510" cy="165" r="28"/></g><g fill="#212925" text-anchor="middle" font-size="19"><text x="100" y="61">r1</text><text x="100" y="171">r2</text><text x="510" y="61">p1</text><text x="510" y="171">p2</text></g></svg><p>先占r1→p1后，沿r2→p1→r1→p2增广。灰虚线是被替换的早期选择，绿线是最终两对。这个图是讲解示意，候选及结果由实际案例输出核对。</p></section>'''
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src data:; base-uri 'none'; form-action 'none'"><title>MoonEventEval · 离线演示实录</title><style>*{box-sizing:border-box}body{margin:0;background:#f2f0e9;color:#202a25;font:17px/1.75 system-ui,-apple-system,sans-serif}main{max-width:940px;margin:auto;padding:48px 24px}header{padding:24px 0 48px}h1{font-size:clamp(38px,7vw,70px);line-height:1.1;letter-spacing:-2px;margin:16px 0}h2{font-size:26px;line-height:1.4}section{background:#fffefb;border:1px solid #deded5;border-radius:16px;padding:30px;margin:22px 0}.eyebrow{color:#177157;font-size:13px;letter-spacing:2px;font-weight:700}.badge{display:inline-block;background:#dfede3;border-radius:20px;padding:4px 14px;font-size:13px}nav a{color:#185d49;margin-right:16px}pre{overflow:auto;font:13px/1.7 ui-monospace,Menlo,monospace;white-space:pre-wrap;overflow-wrap:anywhere;background:#f0f1eb;padding:18px;border-radius:8px}.cmd{background:#202c26;color:#e4f3e7}summary{cursor:pointer;color:#155c46;font-weight:600}svg{width:100%;max-height:240px}.meta{color:#626e65;font-size:14px}footer{padding:24px 0;font-size:14px}a{color:#155c46}@media(max-width:520px){section{padding:20px}main{padding:28px 16px}h2{font-size:22px}}@media print{details{display:block}pre{font-size:10px}section{break-inside:avoid}}</style><main><header><span class="badge">本机真实输出 · 离线可读 · 代理执行</span><h1>MoonEventEval</h1><p>时间事件先配对，再计算指标。用三个反例讲清重复预测、最大匹配与精确边界。</p><p class="meta">产品0.1.0 / Darwin arm64 / 被测代码 '''+code[:12]+'''</p><nav><a href="#duplicate">重复预测</a><a href="#greedy-trap">增广陷阱</a><a href="#boundary">精确边界</a><a href="#missing-file">失败协议</a></nav></header>'''+''.join(parts[:2])+graph+''.join(parts[2:])+'''<footer>这是本轮复制binary后的命令实录，不是在线评分服务、视频或本人讲解记录。技术验收由Codex完成；公开仓库、远端CI/Linux、新安装、发布与赛事资格未完成。输入只支持JSON字符串时间；已知限制见START_HERE.md。源码包、许可、逐文件hash和完整事实材料随目录提供。</footer></main></html>'''
write('DEMO.html',page)
# Audit the actual export for host paths, runtime environments and unsafe paths.
for p in OUT.rglob('*'):
 if p.is_file() and p.suffix in {'.md','.html','.json'}:
  text=p.read_text();assert all(token not in text for token in ['/Users/','/private/tmp/', '.venv-reference/bin/', 'Hengrui@']),p
files={str(p.relative_to(OUT)):sha(p) for p in sorted(OUT.rglob('*')) if p.is_file()}
write('SHA256SUMS.json',pretty(files))
zip_path=STAGE/'MoonEventEval-0.1.0-local.zip'
assert not zip_path.exists()
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(OUT.rglob('*')):
  if p.is_file():
   info=zipfile.ZipInfo('MoonEventEval-0.1.0-local/'+str(p.relative_to(OUT)),date_time=(2026,10,22,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
   info.external_attr=((0o100755 if p.name=='mooneventeval' else 0o100644)<<16);z.writestr(info,p.read_bytes())
with zipfile.ZipFile(zip_path) as z:
 assert z.testzip() is None and len(z.namelist())==len(files)+1
 assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in z.namelist())
report=dict(passed=True,scope='agent-run local handoff assembly; no remote publication or personal demonstration',checkout_sha=identity['demo_checkout_sha'],tested_code_sha=final['git_head'],product_sha256=sha(binary),source_archive_sha256=sha(archive),delivery_zip_sha256=sha(zip_path),delivery_members=len(files)+1,copied_binary_calls=5,actual_exit_codes=[r['exit_code'] for r in calls],host_path_scan_passed=True,browser_render_verified=False,browser_note='two CUA browser access attempts timed out; no visual verification claimed',remote_ci='NOT_RUN',published=False,user_manual_retest='WAIVED_BY_USER_2026-10-22',personal_explanation='NOT_PERFORMED')
(STAGE/'delivery-report.json').write_text(pretty(report))
print(pretty(report))
