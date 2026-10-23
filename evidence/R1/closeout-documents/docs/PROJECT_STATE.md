# MoonEventEval 当前状态

更新2026-10-23（America/Phoenix）。**T0–T8/P1本地工程与R1私有双平台CI完成。用户取消自行复测，由Codex验收；PRD M2最小核心已完成。公开发布、赛事接受与本人理解不作已完成声明。**

## 当前入口

[契约](contracts.md) → [有效计划v2](superpowers/plans/2026-10-20-mooneventeval-plan-v2.md) → [验收地图](ACCEPTANCE.md) → [远端结果/交接](delivery/REMOTE_CI.md) → [交付包](delivery/READINESS.md)。旧v1不再执行。历史T6/T7/T8结果和manifest保留其各自SHA，不以旧hash核新文档。

## 当前身份与证据

- 私有仓库：https://github.com/z2823253773-p/mooneventeval，默认main；最终API确认private=true。
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
- 当前许可MIT，namespace仍local/mooneventeval；私有GitHub不是公开参赛/注册表发布。两OS binary/ZIP容器hash不同，源成员hash相同；不承诺跨平台/路径bit一致。
- 已获授权仅私有建仓、代码/证据/真实历史推送及CI/失败修复。保持私有；公开、发包、报名变更、外发消息仍须另有明确授权。无临床数据访问。赛事个案资格/换题/次数/截止具体时区或时刻仍待外部证据。

## 复核与后续

```sh
python3 evidence/R1/freeze.py
python3 evidence/R1/verify_remote.py --check-only
```

当前授权范围已完成；后续代理先读AGENTS、contracts、本文及REMOTE_CI，核实际git与远端run，不重做已完成阶段。公开发布前仍需单独做公开内容/身份与赛事要求核对；不自动改变可见性或提交报名。
