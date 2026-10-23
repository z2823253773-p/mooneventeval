# R1 私有远端CI结果与交接

更新2026-10-23（America/Phoenix）。用户“授权”范围内的私有建仓、代码/证据/历史推送及双平台CI已完成。没有公开仓库、注册表发布、报名变更或向他人发送消息。

## 实际远端结果

[私有仓库](https://github.com/z2823253773-p/mooneventeval)；API最终确认private=true，默认main。[唯一远端运行](https://github.com/z2823253773-p/mooneventeval/actions/runs/39914869650)，workflow_dispatch，run39914869650，GitHub结论success，两job均success。

- 原始作者代码SHA：`69f544fdcfd6bdd13bff273279da7dd5fdfc56d6`。
- 实际导出/远端被测SHA：`c1e74f58b495e8bf83986715f57d6d8f3bff76bd`；两个OS的204个非证据源码hash相同，并逐一与原始作者SHA的Git blobs对上。
- macOS14 arm64和Ubuntu24.04 x86_64各17/17；各58 Moon、28 Python、42验证、15 CLI；324基础任务+1296变形共1620真实产品调用；各38文件源包、包外消费、解包CLI及六个README命令通过。
- 既有固定工具链/core和原版参考依赖在两台新runner实际安装、校验、构建和运行。Mac安装常规文件1384，Linux1383；参考Python3.11.14/44版本锁+原始sed_eval12文件/字节码核验通过。这里新增Linux与两种新安装证据，不认证Windows、所有Linux发行版或未来上游下载。
- [下载产物复验](../../evidence/R1/remote-verified.json)：每平台8144文件逐一hash复核；真实子进程退出0、无timeout/skip、原始SHA/产物绑定。原始run/jobs、日志和下载产物在evidence/R1/remote-39914869650。

两OS source成员hash一致，但原生binary和ZIP容器hash各自不同；按平台记录，不宣称跨平台或跨构建路径bit一致。原始统计/分区与315共有口径、9边界差异仍保持T6定义，不把1620变形都说成原版对照。

## 历史运输与修复

GitHub普通Git拒绝超过100MiB的blob；原T7评审原始diff为150195290字节。独立导出副本只从原生提交树移除此路径，40条代码阶段提交保留作者/日期/说明，并记录[原始→导出映射](../../evidence/R1/export-map.json)。完整原始历史through4d5d3fbb作为约23MiB bundle附带；导入独立证据ref，恢复同一原始SHA和原始大日志，再运行未删减总门。本地原始历史没有改写；不声称GitHub原生提交图与本地SHA完全相同。[锁](../../.ci/history.json) / [说明](../../.ci/README.md)。

推送副本首轮本地总门在15步后被T7历史门正确阻断：两份已归档reviewer binary被.gitignore排除，过去仅在本机。两文件共1054216字节，逐一对原始冻结manifest的hash验证后，在69f544fd明确新增证据提交。旧manifest/历史不改写。探索中的supplemental-ref办法已撤回，未进入最终代码；没有跳过历史门。

唯一独立R1复核候选07906089发现1 Important：existing proof只和metadata一致，不保证与bundle里的原始Git blob一致。作者先观察真实RED，再增加原始Git对象比较，6项恢复器/28项Python及最终完整门GREEN；独立原fixture同类反例已覆盖。没有第二次独立复审。原文和hash清单在[独立复核](../../evidence/R1/independent-review/REVIEW.md)，处置在[resolution](../../evidence/R1/review-resolution.json)。该评审没有认证后续作者改动、远端/隐私、全量图映射/大日志内容或TOCTOU；本轮作者以映射、原始hash、完整门、实际API和下载产物补足有限交付证据，不扩成普遍安全/竞态认证。

## 继续与限制

原始工作树mooneventeval-t0/spike/t0-feasibility保留；远端导出工作树mooneventeval-ci/main保留。原main分支/代码保持8a307552。本轮之后的内部文档/证据收尾提交与远端被测c1e74f58分开，不冒称后来HEAD重跑过CI。

独立克隆先导入[原始作者对象](../../evidence/R1-provenance/README.md)：自包含bundle提供冻结验证器所需69f544fd，不依赖本机缓存；原有CI历史包仍保持不变。

```sh
python3 evidence/R1-provenance/restore.py
python3 evidence/R1/freeze.py
python3 evidence/R1/verify_remote.py --check-only
```

新运行需要新的证据目录，不覆盖已冻结阶段。后续代码修复先在原始分支验证，再按记录同步导出副本；普通新文档/证据提交无需改写原始历史或使用force push。新的完整原始SHA若需历史引用，明确扩展bundle锁，不悄悄用映射SHA替代冻结SHA。

用户无需自行复测；PRD M2最小核心已完成，历史“本人M2”混用作废。本人理解/官方接受仍无完成证明；保持私有不能满足公开仓库条款。公开脱敏、正式namespace/Mooncakes、组委会换题/资格/报名/剩余次数/截止时刻等均未完成或未授权。T8 NUL ID的CLI寻址限制和T6 timeout部分输出取证缺口仍延期；TSV/CSV等仍在BACKLOG。
