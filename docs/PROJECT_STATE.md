更新2026-11-13：**用户确认初审通过；P9最终验收准备进行中。** 用户未收到附加清单/截止/视频要求。正式0.1.0与P8冻结证据完整，基线原始226688abf/公开738e462fa。继续现有隔离工作树，按申报范围补公开标注接入、自动快速CI和当前验收入口，不改产品评分、API、CLI或已发布版本。计划见superpowers/plans/2026-11-13-final-readiness.md。

已实现DESED固定标注的11事件/2录制受控流程，6条实际产品命令；基线TP11/FP0/FN0，变体9/2/2。两项新真实测试通过，另输入与快照篡改均被拒绝。数据CC BY4.0归属与完整原始小表hash保留，预测不是实际模型输出。当前最终本地全门、独立审查和远端CI尚待本轮实测；不能用P8结果代替新HEAD。最终赛事验收尚无通过回执。以下为此前阶段记录。

更新2026-11-06：**P8完成正式Mooncakes发布及注册表安装消费验证。** 用户明确要求补齐最终验收指出的注册表缺口；已按正式命名空间发布z2823253773-p/mooneventeval@0.1.0（exit0 / 200OK），MIT，43成员。公开v0.1.0标签绑定304d590574d7ca54fd5a8c9d2781d7823f8802c9（作者affd168393780a9e8fc2fb757d156e0a6c6af938）。完整[双平台CI42241701394](https://github.com/z2823253773-p/mooneventeval/actions/runs/42241701394)成功，每OS17步/65 MoonBit/29根Python/42验证/19 CLI、1620调用及43成员包/解包消费；255源码hash一致。

真实仓库外、无workspace、未登录的客户端从网络安装精确版本，43/43文件与已审ZIP逐字节一致，7条安装/API/TSV/重复键/下载源码CLI构建及三案例命令全通过。版本页HTTP200。发布前独立评审0C/0I/1M，作者修正回执字段auth措辞并实跑注册表门，没有二次独立评审。收尾文档与字段变更不在已发布ZIP内，不声称收尾HEAD重跑双平台CI。

[正式发布与安装回执](delivery/MOONCAKES_RELEASE.md)、[安装指南](INSTALL.md)、证据evidence/P8；离线复核python3 evidence/P8/verify.py，在线复验python3 scripts/check_registry.py --archive evidence/P8/release-0.1.0.zip --output /tmp/mooneventeval-registry-recheck（新目录）。用户无需自行重复技术验证。当前仅确认退回中的发布/安装技术项已补齐，未代提交表单、未声称组委会通过。后续公开数据流程或轻量CI按后续明确任务推进，不在本轮扩展。

以下为P7及以前历史记录。

# MoonEventEval 当前状态

更新2026-11-05。**P7已完成：四列TSV导入。** MoonBit import_tsv与native import-tsv把两份有表头事件表生成可直接评测的任务JSON；时间精确、原行追溯、重复行保留，支持BOM/LF/CRLF，格式与范围错误映射文件侧/行/列。文档见[TSV](TSV.md)，计划见[P7](superpowers/plans/2026-11-02-tsv-import.md)。输入适配v4替代旧“仅JSON输入”限制；数学和原JSON报告不变，最小源码包42文件。

当前最终实测原始c05cb165281777a86356fe86f4079f9ed72e6de5 / 公开5874d6514d4ef3c34292ecced56446ea02c764a8。[CI42176209407](https://github.com/z2823253773-p/mooneventeval/actions/runs/42176209407)的macOS15 arm64 / Ubuntu24.04 x86_64各完整17步通过：65 MoonBit / 29根Python / 42验证 / 19 CLI、1620资格验证调用、42文件包/解包导入→评测、13产品/4原版回放。251源码hash一致并绑定公开Git，各8262基础产物及35演示文件已下载核验。

独立评审候选500b44a52，0 Critical / 0 Important / 1 Minor。作者已修正帮助文案对导入默认输出的误导，并完成最终实测；没有第二次独立评审。评审另核对40随机双侧Unicode输入、10旧CLI对照、8MiB制表符边界及实际42成员解包重建。原run42175638875的Mac14因镜像退役未分配runner就取消；按实际annotation和官方说明迁移Mac15后重新全门。一次本地验证跨提交被保护检查正确拒绝，固定最终提交后重跑通过；失败证据保留。

CI后的README链接、状态/计划/契约及证据归档属于后续文档提交，42成员源码包单独复验，不冒称后续HEAD又跑完整CI。离线核对：`python3 evidence/P7/verify.py`，见[P7证据](../evidence/P7/README.md)。用户无需自行复测。下一阶段公开数据完整使用流程、发包准备与轻量CI按已授权方向推进；正式注册表发布与报名仍独立，不自动操作。下方P6/P5仅保留历史阶段。

更新2026-11-02（America/Phoenix）。**P6 已完成：拒绝原始JSON重名键。** 输入契约v3收紧旧last-wins：同对象解码键重复（含转义等价键）返回DUPLICATE_KEY、Input/exit2、path="$"，无部分评分；先完成UTF-8/JSON语法/深度校验，再查重，最后校验schema。错误含安全截断键预览及BOM剥离后的零基UTF16偏移。typed API、数学规则、正常报告及38文件包不变。

原始最终实测 `7c46e83165a5565338715600c220ac3c37a472ec`，公开实测 `2a007a352dd349c45236bebb0f18b972ce2ac3a6`；[CI41446549940](https://github.com/z2823253773-p/mooneventeval/actions/runs/41446549940) 的macOS arm64 / Linux x86_64各完整17步、62 MoonBit / 29根Python / 42验证 / 16 CLI、1620资格验证调用、38文件打包/解包消费、13产品/4原版回放均通过。244源码hash相同并逐一绑定公开Git；各8192基础产物及35演示文件已下载、保存并复核。本地开发probe另56检查通过；三项可编译mutation被行为测试杀死。

独立评审原候选3ceabc725，0 Critical / 1 Important / 1 Minor，未发现产品代码缺陷。Important为选题事实说明残留旧last-wins表述，作者已修正；Minor为键预览测试允许退化成省略号，作者补强短控制字符与64非BMP码点的精确断言，并使空预览mutation变红。评审独立生成500案例：410无重名输入与基线输出逐字节一致，90重名输入正确失败，另8边界通过；作者复跑其原脚本，不冒称第二次独立评审。两项发现后的最终提交均完成真实验收。证据与离线复核见[P6](../evidence/P6/README.md)。

CI后的首页链接、状态、计划与证据收尾仅为后续文档提交；38文件源码包单独复验，不冒称后续HEAD又跑过完整CI。继续可执行 `python3 evidence/P6/verify.py` 核冻结归档；用户无需自行复测。下一阶段按已授权顺序定义薄TSV导入与公开数据流程，不自动发布包。计划：[P6](superpowers/plans/2026-11-02-duplicate-json-keys.md)。以下P5/P4段落仅是其历史阶段记录。

更新2026-11-02（America/Phoenix）。**P5 已完成：MoonBit 独立接入示例与贡献入口。** 新增完整仓库内的独立模块，实际调用公开 API，演示评测、合格但未选中的事件对解释和非法数字时间的 Result 处理；补齐 CONTRIBUTING、CHANGELOG 与 README/API 的运行说明。评分、输入、CLI、包名及 38 文件源码包契约不变。

原始实测 `f75963024b584e232114024cb2d83018cfb1f037`，公开实测 `b06207ae936e4179064ba4ccf7941cac61773f6e`；[run41434748035](https://github.com/z2823253773-p/mooneventeval/actions/runs/41434748035) 的 macOS arm64 / Linux x86_64 均成功。每平台完整17步、58 MoonBit / 29根Python / 42验证 / 15 CLI测试、1620资格验证调用、38文件打包解包消费，以及13产品/4原版回放；243源码hash一致并逐一绑定公开Git，两平台各8144基础产物及35演示文件完整保存和复核。编译后的示例另在空PATH环境成功运行。

独立评审针对初候选 `ff728dc0e`，0 Critical / 1 Important / 0 Minor。Important为贡献指南遗漏公开冷克隆所需的历史还原命令；作者确认并修正文档，在全新克隆验证原始证明哈希和HEAD不变，再以最终SHA重跑完整门。没有第二次独立复审；原报告和最终实测分别保留在 [P5证据](../evidence/P5/README.md)。CI完成后的首页链接、状态/计划及证据收尾属于后续文档提交，只单独复验38文件源码包，不冒称重跑完整CI。

本轮计划：[MoonBit 接入](superpowers/plans/2026-11-02-moonbit-integration.md)。沿用原隔离工作树与公开导出仓库，不改写旧历史或冻结证据；后续发布、报名结果仍需实际回执，不能从开发结果推断。

继续入口：运行 `python3 evidence/P5/verify.py` 可离线复核本轮归档与实际公开被测SHA。技术复测仍由Codex负责，用户无需重复验证。新增输入格式/评分模式继续先明确契约，BACKLOG不自动作为新需求；本轮不声称包注册表发布或外部采用。

更新2026-10-27（America/Phoenix）。**P4：再次风险审查与修订完成。1项呈现Important、2项状态Minor已修正；原始候选06ec1649b、远端被测e106a5d47在本地与双平台完整验收通过。** 剩余的正式申报写作、真实采用和组委会判断边界见[风险核查](delivery/REVIEW_RISKS.md)。

P4把P2已有的4份流程输入和5条命令公开到demo/workflows，快照回放为13产品+4原版命令；它们是合成预期任务，不是外部使用证明。[本轮run40467323131](https://github.com/z2823253773-p/mooneventeval/actions/runs/40467323131)两OS各完整17步及13产品+4原版演示成功。各233源码hash一致并绑定公开Git，8144基础产物及35演示文件逐项检查。后续CI入口/证据元数据HEAD不冒称重跑全门；原核心与输入契约不变。

用户提供的邮件截图显示2026-10-27 11:21的初审退回通知（截图未标注时区），允许10月31日前修改信息后重新审核。该通知取代P2“报名尚未提交”的状态；本代理未代提交表单。本轮按直接请求修订公开材料、可运行输出和参考范围，见[复审修订记录](delivery/REVIEW_REVISION.md)。

P3新增仓库demo，保存8份实际产品输出及4份锁定原版结果；README先展示输出清单与summary节选，THIRD_PARTY_NOTICES逐项解释参考/未移植部分及口径差异。评分核心、schema和CLI不变；CI新增一次demo重跑检查。P3最终原始代码/文档074509f2da1a4b275d7c752399a7e5989f7e717a，对应实际远端被测a613579b615e4ac7fd74ddcd704d4333707bcc4b；[run40447392163](https://github.com/z2823253773-p/mooneventeval/actions/runs/40447392163)两OS各完整17步+8产品/4原版重跑成功。各222源码hash一致且绑定公开Git，8144基础产物及25演示文件逐项复核。本轮后续证据/状态HEAD不冒称重跑过CI。个人申报材料及联系方式仍只在仓库外。

此前P2记录见[公开交付](delivery/PUBLIC_RELEASE.md)。原T8/P1/R1/P2冻结清单不修改。

## 当前入口

[契约](contracts.md) → [有效计划v2](superpowers/plans/2026-10-20-mooneventeval-plan-v2.md) → [验收地图](ACCEPTANCE.md) → [远端结果/交接](delivery/REMOTE_CI.md) → [交付包](delivery/READINESS.md)。旧v1不再执行。历史T6/T7/T8结果和manifest保留其各自SHA，不以旧hash核新文档。

## 当前身份与证据

- 当前公开仓库：https://github.com/z2823253773-p/mooneventeval，默认main；P2 API确认private=false，禁用凭证助手/认证头的匿名ls-remote成功。R1 frozen private=true只描述其历史时刻。
- P2公开候选原始文档代码23af827f87adad36b06cf11b30a82982848fd1f5，对应实际远端被测f406084d7f702fd569401b76ae86b65817f7aafa；[run39925966715](https://github.com/z2823253773-p/mooneventeval/actions/runs/39925966715)两OS各17步成功。各205源码hash相同、各8144产物hash下载复验通过，产品运行源码/API/工作流未变。后续证据文档HEAD不冒称重新运行。
- R1原始作者代码/被测等价源码 **69f544fdcfd6bdd13bff273279da7dd5fdfc56d6**；实际远端被测导出 **c1e74f58b495e8bf83986715f57d6d8f3bff76bd**；[run39914869650](https://github.com/z2823253773-p/mooneventeval/actions/runs/39914869650)整次success，Mac14 arm64与Ubuntu24.04 x86_64均success。两OS各204非证据源码hash相同，逐一绑定原始作者Git blobs。
- 每OS完整17步：Moon58、Python28、validation42、CLI15；各324bases+1296变形=1620产品调用、38文件源包/包外消费/解包CLI/六README命令。新工具链与原版参考环境在两runner实际安装。各8144产物hash已下载复验，[总表](../evidence/R1/remote-verified.json) / [冻结清单](../evidence/R1/manifest.json)。
- 本机原始工作树`/Users/henryz/Desktop/比赛/mooneventeval-t0`，分支`spike/t0-feasibility`；导出工作树`/Users/henryz/Desktop/比赛/mooneventeval-ci`，分支main。原main代码仍8a3075521312c9bf9ad196309422adaa0c67fbd2。后续文档/证据收尾HEAD用git查询，不与远端被测SHA混同。
- GitHub有100MiB单blob限制；原T7大日志150195290字节在导出提交树中省略，完整原始历史through4d5d3fbb由hash锁定bundle保留并在CI还原原始对象/日志。代码阶段40提交的作者/日期/说明和除该路径外的树一致已检查；GitHub原生SHA映射明确记录，不声称图完全不变。原始本地历史未改写。

## 完成项与限制

时间字符串精确转微秒/ppm、同类容差图、显式栈first-free+DFS最大基数匹配、同源解释、稳定JSON/text、真实native文件CLI及I/O/预算门、公开工厂/评测/渲染API均已实现。T2有753小图oracle；T6有有限mutation/I/O注入/资源和本机性能样本；R1不重做历史campaign，不扩成全部图/OS/竞态认证。

T6原版限定对照：315共有口径一致；9边界6一致/1具体binary64差异/2零collar域限制，未解释0。各base原版全局/逐录制/类实跑；变形由有理数/图oracle核验，1620不是1620次原版对照。

R1推送副本首轮本地总门暴露两份ignored reviewer binary未提交，按原始冻结hash补交后门通过。唯一独立R1复核1 Important existing proof未绑定原始Git blob已作者RED→GREEN修复；6恢复器/28Python及完整门/远端通过，无第二次独立复审。T8之前独立复核的作者处置仍按历史记录，不混作本轮新审阅。

## 固定边界、延期和未完成

- 仅UTF8 JSON字符串时间；P6按输入契约v3拒绝同对象重名/转义等价键。TSV/CSV、数字时间、sed_eval dict、stdin、新评分仍[BACKLOG](../BACKLOG.md)。
- T8 Minor：合法NUL ID可评测/API解释，literal OS argv不能选中。T6 Minor：超时非零，但部分stdout/stderr/process收据不完整。均未修复。
- 本人讲解/外部反馈无实际证据；用户已取消自行复测，不作工程阻塞。历史“本人M2”混用作废，PRD M2机器条件已完成。
- P1十九文件本地交付包、复制/ZIP解出程序三案例通过；本机binary含构建路径，未作公开脱敏。HTML结构/内容已验，file协议观察被浏览器安全策略拒绝，视觉核验未完成；不要求用户补测。
- 当前许可MIT，namespace仍local/mooneventeval；P2 GitHub已公开，注册表仍未发布。两OS binary/ZIP容器hash不同，源成员hash相同；不承诺跨平台/路径bit一致。
- 已获授权并执行私有建仓、推送/CI修复及P2公开仓库；正式发包、报名变更、外发消息未执行。无临床数据访问。赛事个案资格/换题/次数/截止具体时区或时刻仍待外部证据。

## 复核与后续

历史P4复核：`python3 evidence/P4-acceptance/freeze.py`。P3旧证据仍可按`python3 evidence/P3-acceptance/freeze.py`复核。原始local与下载产物按字节归档为3个ZIP，保留SHA256与自动复核器，避免将本轮3万余原始小文件散入提交；首次候选与最终候选严格分开。


独立克隆先导入[原始作者对象](../evidence/R1-provenance/README.md)，再按冻结原始SHA复核；不依赖本机Git缓存。该补充不改变产品代码或实际CI被测提交。

```sh
python3 evidence/R1-provenance/restore.py
python3 evidence/R1/freeze.py
python3 evidence/R1/verify_remote.py --check-only
```

P4技术修订完成，尚无重新提交/复审通过回执；后续代理先读AGENTS、contracts、本文和REVIEW_REVISION，核实际git与远端run，不重做已完成阶段。仓库公开已完成；正式报名仍须满足表单要求，包括一页Markdown、不使用AI编写申报书、至少三个完整预期场景及有效开发记录。代理材料不声明由本人独立撰写，不替代正式报名或本人理解。
