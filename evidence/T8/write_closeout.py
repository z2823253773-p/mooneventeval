"""Write internal closeout documents after the final committed-source gate."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2]
r=json.loads((ROOT/'evidence/T8/final-local/report.json').read_bytes())
assert r['passed'] is True and r['git_head']=='8aa37c5aa55821d40a527e42ee9bc47ffc32371f'
code=r['git_head']
def put(name,text):(ROOT/name).write_text(text.strip()+'\n',encoding='utf-8')
put('docs/reviews/2026-10-22-t8-results.md',f'''# T8 本地统一验收结果

日期2026-10-22，America/Phoenix。本地工程门完成；本人M2、Linux/远端CI、新安装、发布及赛事资格未完成。

## 身份与实跑

基线7f325643cf12d3cab5a60f9808af3ec94d11caed；整分支从8a3075521312c9bf9ad196309422adaa0c67fbd2审至df2142688e991c244cae0a94623ccf8acf55f257。唯一有效fresh reviewer审的是该候选；最强模型席位先遇用量上限，未给出评审，随后由可用gpt-6.1-sol xhigh替补。不是两次有效评审。

最终代码/被测 **{code}**。后续提交为内部文档/证据收尾，不冒称文档HEAD重新实跑。产品运行源码/公开API与评审候选相同。最终测试前193个源码hash全部与当前bytes相符；freeze按被测SHA的Git blobs核对，允许后续内部文档更新。

实际命令：`python3 scripts/verify.py --mode local --evidence evidence/T8/final-local`，由task-done执行，退出0，17/17步骤成功。Moon58、根Python22、validation42、CLI15，无跳过。324 base+1296变形共1620次真实产品调用；315非边界共同口径一致，9边界6一致/1具体binary64差异/2原版零collar域限制，未解释0。包外consumer、38文件真实归档及解包后consumer/native CLI/README六命令通过。

生产binary SHA256 `{r['product_sha256']}`；候选zip SHA256 `{r['archive_sha256']}`。工具/core安装1384常规文件对锁定档内bytes；参考Python3.11.14、44版本锁和sed_eval原始12文件通过，选中字节码也与源码新编译代码一致。core摘要不是发布者认证，其他Python依赖仅按版本/安装锁范围，不作完整供应链证明。

## 负例与复核

[最终总表](../../evidence/T8/final-local/report.json)、[源码绑定](../../evidence/T8/final-source.json)、[最终命令](../../evidence/T8/final-task-done.log)、[冻结清单](../../evidence/T8/manifest.json)。五个真实总门负例在[negative-controls-isolated](../../evidence/T8/negative-controls-isolated/report.json)：缺参考、工具链档hash错误、真实子进程exit7、构建后删除实际binary、全部17子进程退出0后从实际zip删除LICENSE，均正确拒绝。它们在df214268执行，保留其SHA，不伪称修复后再跑；I1的新增缓存负例在最终代码重测。

[唯一独立复核原文](../../evidence/T8/independent-review/REVIEW.md)与[原始manifest](../../evidence/T8/independent-review/SHA256SUMS.json)原样9134文件hash验证归档，作者修复不在其范围。复核另有独立17/17总跑、48输入/281产品进程、7拒绝控制；独立路径构建binary有自己的hash。历史T6/T7 freeze只核历史证据；不称重做故障/mutation/性能campaign。

I1 Important：正确.py可能执行被改.pyc。作者先新增真实子进程反例，身份/评分两个入口均观察到RED（错误放行、TP1而精确应TP0）；修复为导入前核对当前解释器选中缓存代码与已hash源码新编译代码，身份探针走同一门。42验证测试及最终17步骤GREEN；[原始缓存fixture作者重放](../../evidence/T8/author-cache-replay/report.json)两入口均拒绝。首个测试fixture缺import路径的错误也保留，不能当有效RED。无第二次独立复审。

T8 M1 Minor延期：NUL字符ID合法且可评测/API调用，但OS argv不能包含NUL，CLI explain无法选中；不静默收窄schema或解释转义。继承T6 M1超时部分stdout/stderr/process收据缺口仍延期。

## 保留范围

CI只有手动矩阵配置和本地结构检查；未推送、触发、合并、发布或改报名。Linux/新安装和Action服务语义未实跑。本人手算/讲解/M2、外部用户、正式namespace/URL、赛事资格均无新增证据。输入仍JSON字符串时间，重名键last-wins；TSV/CSV/stdin不在已实现范围。所有决定见[作者账本](../../evidence/T8/author-ledger.md)；选择保留原分支/工作树。
''')
put('docs/reviews/2026-10-22-t8-review.md','''# T8 整分支评审处置

唯一有效独立复核候选df214268；0 Critical、1 Important、1 Minor，原结论With fixes。[原文](../../evidence/T8/independent-review/REVIEW.md)与[原始hash清单](../../evidence/T8/independent-review/SHA256SUMS.json)原样保留。最强模型首席因额度失败未产生结论；替补gpt-6.1-sol xhigh fresh reviewer完成，未再发起复审。

作者按使用者影响重分级：I1保持Important，进入唯一一轮作者修复；T8 M1保持Minor延期。I1两入口真实RED→GREEN、42验证测试、最终17/17总门及原fixture重放见[T8结果](2026-10-22-t8-results.md)。最终代码8aa37c5，评审不覆盖作者后续diff；没有把作者验证写成第二次独立审阅。

T8 M1：NUL事件/录制ID能评测和通过公开API解释，但无法用literal OS argv选中。将其作为明确CLI限制记录；以后增加escaped-selector需单独定契约，不能悄悄拒绝已有合法输入。继承T6 M1超时取证延期。

评审declined-to-judge各项已逐条作决定并记录成本：[完整作者账本](../../evidence/T8/author-ledger.md)。包括远端/Linux/新安装未运行；注册/赛事/个人条件不属工程验收；历史campaign不作新跑；重名键既有语义；大collar/等价匹配/预算既有契约；原版域/浮点/投影差异；完整供应链和跨路径bit身份未认证；schema_version数字词法精度未单独资格化；最终作者修复/文档排除于独立候选评审。
''')
put('docs/PROJECT_STATE.md',f'''# MoonEventEval 当前状态

更新2026-10-22（America/Phoenix）。**T0–T8本地工程任务完成；T5本人手算/口头demo/M2仍未完成。T8整分支唯一有效独立评审的1项Important已作者单轮RED→GREEN修复并通过最终总门，无第二次独立复审；1项新Minor和1项继承Minor延期。远端CI/Linux、新安装、正式发布与赛事资格未完成。**

## 当前入口与身份

[契约](contracts.md) → [有效计划v2](superpowers/plans/2026-10-20-mooneventeval-plan-v2.md) → [验收地图](ACCEPTANCE.md) → [T8结果](reviews/2026-10-22-t8-results.md) / [评审处置](reviews/2026-10-22-t8-review.md) → [最终交接](DELIVERY_HANDOFF.md) / [已实现选题事实](PROJECT_POSITIONING.md)。v1已作废。本人部分见[T5卡](superpowers/plans/tasks/T5-cli-demo.md)与[demo稿](demo.md)。

- 工作树`/Users/henryz/Desktop/比赛/mooneventeval-t0`；分支`spike/t0-feasibility`，保留待用户后续决定。原main基线8a3075521312c9bf9ad196309422adaa0c67fbd2；无remote/merge/push/CI触发/发布/报名变更，无临床数据访问。
- T8最终代码/被测 **{code}**；独立评审候选df2142688e991c244cae0a94623ccf8acf55f257。之后内部文档/证据提交与代码被测SHA分开，当前HEAD用git查询。
- 最终实际17/17：Moon58、Python22、validation42、CLI15，324bases+1296变形共1620产品调用；38文件真实源候选包、解包后consumer/native CLI及README六命令通过。源码193hash测试前后不变；后续文档按Git历史绑定。[总表](../evidence/T8/final-local/report.json) / [manifest](../evidence/T8/manifest.json)。
- 生产binary SHA256 `{r['product_sha256']}`。候选archive SHA256 `{r['archive_sha256']}`，只限定本机Darwin arm64。local/mooneventeval@0.1.0不是注册表发布身份。

## 已完成及证据范围

T0工具链/版本语法实编译；T1精确十进制/Unicode/资格；T1b原版参考hash锁；T2显式栈first-free+DFS、753小图；T3封装输入/评测；T4同源解释/稳定报告/16MiB字节门；T5真实文件CLI与agent自动demo；T6限定对照/变形/预算/I/O注入/mutation；T7公开API包外消费及解包；T8当前cwd统一检查器、真实失败控制、未触发手动CI、整分支复核和交接。

T6参考324基础任务：155网格/160安全十进制/9边界。315共有口径一致；边界6一致/1具体binary64差异/2零collar原版域限制，未解释0。保留raw substitutions并显式projection；合成/固定seed范围，不认证任意真实数据普遍兼容。每base原版全局/逐录制/类实跑，四变形由独立有理数/图oracle核验；1620不是1620次原版对照。

[T6结果](reviews/2026-10-22-t6-results.md) / [评审](reviews/2026-10-22-t6-review.md)：代码/被测7b8a453f58307e4118eeae7ad78d79859af6eeed，2 Important作者修复；真实限额/9类I/O注入/6可编译mutation杀死，本机性能样本，无全部图/OS/竞态保证。[T7结果](reviews/2026-10-22-t7-results.md) / [评审](reviews/2026-10-22-t7-review.md)：代码/被测bb24ce33962ebf6276265075edb3df10e16e6601，1 Important作者修复。各历史manifest只对其历史SHA；不可按旧源码hash检验新文档。

T8复核原样9134文件；独立17步骤、额外48输入/281产品调用/7拒绝控制通过。I1缓存字节码绕过源码核验，作者已修复：身份与评分导入前都比较选中缓存与已hash源码新编译代码，两个入口真实RED→GREEN和原fixture作者重放均拒绝，最终总门GREEN。没有第二次独立复审。最强review席位额度失败后由可用gpt-6.1-sol xhigh替补，原失败未计为有效评审。

## 固定决定、延期与未完成

- 输入仅UTF8 JSON/字符串时间；重名及转义等价键last-wins。TSV/CSV、数字时间、sed_eval dict、stdin、新评分仍[BACKLOG](../BACKLOG.md)，未获范围修订。
- T8 M1延期：含NUL的合法ID可评测/API解释，CLI literal argv无法选中。T6 M1延期：超时正确非零，但部分stdout/stderr/process收据缺口。不称两者已修复。
- 机器输出单LF；I/O错误2、资源3、内部4；可能已输出前缀不等于完成。预算/large collar/等价匹配身份语义仍按契约，不保证所有合法图总能完成。
- [八例](validation/T3-worked-examples.md)和demo稿是agent材料，不能替代本人纸笔复算/三分钟讲解/M2或外部反馈。
- 手动CI保存Mac ARM/Linux x64矩阵及完整SHA action pins，调用同一verify；无远端执行或Linux资格化。正式作者/namespace/仓库URL/赛事资格仍待确认，不能编造。无自动发布、远端创建或报名授权。

## 复验与下一步

```sh
python3 evidence/T8/freeze.py
python3 scripts/verify.py --mode local --evidence evidence/local-delivery-recheck
```

总门须干净已提交根目录、新证据目录、现有锁定工具/档和参考venv，不自动下载/跳过。新复验认证当时HEAD，不改冻结T8。下一步由本人按demo稿实际复算并讲解，记录真实M2结果；需要新输入格式或远端操作时先明确相应范围。后续Codex/Claude Code先读本文件、AGENTS、contracts与对应任务，核实际git状态，不重做已完成阶段。
''')
# Final handoff and factual positioning reuse the earlier explicitly labeled draft,
# preserving that draft as historical preparation evidence.
s=(ROOT/'evidence/T8/document-drafts/DELIVERY_HANDOFF.md').read_text()
s=s.replace('本地交付交接草稿','本地交付交接').replace('当前独立整分支复核尚未完成；本稿不是最终验收结论。','本地工程验收完成；本人M2/远端/赛事条件未完成。')
s=s.replace('本轮初始已提交代码/被测SHA：df2142688e991c244cae0a94623ccf8acf55f257','最终代码/被测SHA：'+code).replace('首次完整结果在evidence/T8/local/report.json','最终完整结果在evidence/T8/final-local/report.json').replace('validation41','validation42')
s=s.replace('当前复核状态以磁盘最终记录为准。','唯一有效独立复核为df214268候选，作者I1缓存修复为8aa37c5；两个入口真实RED→GREEN、最终17步骤通过，无第二次独立复审。详见[结果](reviews/2026-10-22-t8-results.md)与[处置](reviews/2026-10-22-t8-review.md)。T8 M1含NUL的合法ID可评测/API解释，但不能由literal OS argv选择，仍延期。')
s+='\n最终证据冻结：`python3 evidence/T8/freeze.py`。后续内部文档/证据收尾HEAD与被测代码分别记账；使用git rev-parse HEAD查询当前HEAD。本轮保留原分支和工作树，无集成操作。\n'
put('docs/DELIVERY_HANDOFF.md',s)
s=(ROOT/'evidence/T8/document-drafts/PROJECT_POSITIONING.md').read_text().replace('当前整分支独立复核仍在进行。','本地工程复核和作者修复验证已完成，边界见[T8结果](reviews/2026-10-22-t8-results.md)。')
s+='\n已知限制：输入JSON重名键last-wins；含NUL的合法ID可评测/API解释，literal OS argv不能选中；超时部分输出取证仍有历史缺口。不能宣传为所有异常取证完整。\n'
put('docs/PROJECT_POSITIONING.md',s)
p=ROOT/'docs/ACCEPTANCE.md';s=p.read_text();s=s.replace('本人M2/口头演示、CI/正式发布与赛事资格未完成。','T8最终代码/被测8aa37c5，本地17步骤及整分支评审后的作者修复通过；本人M2/口头演示、远端CI/Linux/正式发布与赛事资格未完成。')
s=s.replace('字符串时间唯一输入；重名键last-wins仍明确限制','字符串时间唯一输入；重名键last-wins、NUL ID的CLI不可选中仍明确限制')
s=s.replace('CI在T8，未发布/提交赛事','T8当前17/17门、42验证测试、5真实总门负例、缓存绕过RED→GREEN、唯一整分支评审及38文件再验；CI仅保存配置，未发布/提交赛事')
s+='\n[T8结果](reviews/2026-10-22-t8-results.md) / [评审处置](reviews/2026-10-22-t8-review.md) / [最终交接](DELIVERY_HANDOFF.md)区分最终被测8aa37c5、评审候选df214268和之后内部文档HEAD。本人条件仍未完成。\n';put('docs/ACCEPTANCE.md',s)
p=ROOT/'docs/VALIDATION.md';s=p.read_text().replace('Mac额外锁解释器hash；','选中.pyc必须与已hash源码新编译代码相同且在导入前检查，身份探针使用同一门；Mac额外锁解释器hash；')
s=s.replace('当前阶段尚待首次完整本地总验证与一次整分支独立评审；最终实测SHA、结果与收尾SHA分别回填PROJECT_STATE及本阶段结果。','最终实测8aa37c5总17/17、Moon58/Python22/validation42/CLI15。整分支唯一评审候选df214268的缓存Important已作者RED→GREEN修复并通过总门，未第二次独立复审。收尾内部文档HEAD与被测SHA分别记账，见[T8结果](reviews/2026-10-22-t8-results.md)。')
put('docs/VALIDATION.md',s)
p=ROOT/'docs/contracts.md';s=p.read_text();s=s.replace('原版12个.py的哈希按`reference-sources.json`在每次评测导入前核验。','原版12个.py的哈希按`reference-sources.json`在每次评测导入前核验；当前解释器选中的现存.pyc须与已核验源码新编译代码相同，缓存不符在导入前拒绝（T8 I1）。')
s+='\n## 已披露的CLI标识符边界\n\n合法JSON/API ID可含U+0000，评测保留其值；OS argv不容NUL，literal CLI explain-pair选择器无法寻址该ID，转义文本不自动解码。T8 M1延期，不改变现有schema或公开API；可通过库调用解释。\n';put('docs/contracts.md',s)
p=ROOT/'BACKLOG.md';s=p.read_text();s+='\n| NUL ID的CLI选择 | JSON/API合法ID含NUL时仍可评测/API解释，OS argv不能包含NUL | T8 M1延期；如增加escaped-selector须明定编码和歧义规则，不默改schema或把现有literal参数解释成转义 |\n';put('BACKLOG.md',s)
p=ROOT/'docs/superpowers/plans/tasks/T8-ci-handoff.md';s=p.read_text();a=s.index('状态：');b=s.index('\n\n',a);s=s[:a]+'状态：限定本地工程任务已完成；最终代码/被测8aa37c5，17/17总门。唯一有效整分支评审候选df214268有1 Important作者RED→GREEN修复，1 Minor延期；无第二次独立复审。内部文档/证据收尾与被测SHA分开；远端/Linux/本人M2仍未完成。'+s[b:];s=s.replace('- [ ]','- [x]')
s+='\n本轮实际结果与修订：最终目录为evidence/T8/final-local（初轮local保留）；T8 I1修复后validation42。五项总门负例在候选df214268执行；新增缓存反例与最终总门在8aa37c5执行。后续仅内部文档/证据收尾；选择保留工作树/分支，未合并/推送/触发CI/发布。详见[结果](../../../reviews/2026-10-22-t8-results.md)。\n';put('docs/superpowers/plans/tasks/T8-ci-handoff.md',s)
p=ROOT/'docs/superpowers/plans/2026-10-20-mooneventeval-plan-v2.md';s=p.read_text();s=s.replace('T1b/T2/T3/T4已完成，各评审Important的作者修复已复验；下一机器目标为T6独立对照与硬化，T5本人讲解仍待实际发生，其余待批准范围按contracts和STATE处理。','T0–T8本地工程阶段已完成，各有效评审Important的作者修复已复验，最终代码/被测8aa37c5；T5本人讲解/M2仍待实际发生，Linux/远端/发布未运行，其余待批准范围按contracts和STATE处理。');put('docs/superpowers/plans/2026-10-20-mooneventeval-plan-v2.md',s)
# Preserve exact final internal documents with the evidence, without asserting a
# self-referential future commit hash.
for name in ['docs/PROJECT_STATE.md','docs/contracts.md','docs/ACCEPTANCE.md','docs/VALIDATION.md','docs/DELIVERY_HANDOFF.md','docs/PROJECT_POSITIONING.md','docs/reviews/2026-10-22-t8-results.md','docs/reviews/2026-10-22-t8-review.md','BACKLOG.md','docs/superpowers/plans/tasks/T8-ci-handoff.md','docs/superpowers/plans/2026-10-20-mooneventeval-plan-v2.md']:
 target=ROOT/'evidence/T8/closeout-documents'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/name).read_bytes())
print('internal closeout documents and exact snapshots written; runtime/public package unchanged')
