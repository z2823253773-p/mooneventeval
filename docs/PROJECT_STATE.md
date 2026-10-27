# MoonEventEval 当前状态

更新2026-10-26（America/Phoenix）。**P3：已按初审退回意见完成输出与sed_eval参考范围修订，独立复核及作者修复、本地完整门和本次双平台CI均完成。复审结果待组委会重新审核。** 公开仓库与P2实际双平台CI保持其历史证据；不能把此前工程通过当成初审通过。

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

- 仅UTF8 JSON字符串时间；重名/转义等价键last-wins。TSV/CSV、数字时间、sed_eval dict、stdin、新评分仍[BACKLOG](../BACKLOG.md)。
- T8 Minor：合法NUL ID可评测/API解释，literal OS argv不能选中。T6 Minor：超时非零，但部分stdout/stderr/process收据不完整。均未修复。
- 本人讲解/外部反馈无实际证据；用户已取消自行复测，不作工程阻塞。历史“本人M2”混用作废，PRD M2机器条件已完成。
- P1十九文件本地交付包、复制/ZIP解出程序三案例通过；本机binary含构建路径，未作公开脱敏。HTML结构/内容已验，file协议观察被浏览器安全策略拒绝，视觉核验未完成；不要求用户补测。
- 当前许可MIT，namespace仍local/mooneventeval；P2 GitHub已公开，注册表仍未发布。两OS binary/ZIP容器hash不同，源成员hash相同；不承诺跨平台/路径bit一致。
- 已获授权并执行私有建仓、推送/CI修复及P2公开仓库；正式发包、报名变更、外发消息未执行。无临床数据访问。赛事个案资格/换题/次数/截止具体时区或时刻仍待外部证据。

## 复核与后续

当前P3复核：`python3 evidence/P3-acceptance/freeze.py`。原始local与下载产物按字节归档为3个ZIP，保留SHA256与自动复核器，避免将本轮3万余原始小文件散入提交；首次候选与最终候选严格分开。


独立克隆先导入[原始作者对象](../evidence/R1-provenance/README.md)，再按冻结原始SHA复核；不依赖本机Git缓存。该补充不改变产品代码或实际CI被测提交。

```sh
python3 evidence/R1-provenance/restore.py
python3 evidence/R1/freeze.py
python3 evidence/R1/verify_remote.py --check-only
```

P3技术修订完成，尚无重新提交/复审通过回执；后续代理先读AGENTS、contracts、本文和REVIEW_REVISION，核实际git与远端run，不重做已完成阶段。仓库公开已完成；正式报名仍须满足表单要求，包括一页Markdown、不使用AI编写申报书、至少三个完整预期场景及有效开发记录。代理材料不声明由本人独立撰写，不替代正式报名或本人理解。
