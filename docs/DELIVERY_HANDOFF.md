# MoonEventEval 本地交付交接

本地工程验收完成；PRD M2最小核心已完成；用户取消自行复测，远端/赛事条件未完成。日期2026-10-22，America/Phoenix。

工作树：`/Users/henryz/Desktop/比赛/mooneventeval-t0`；分支`spike/t0-feasibility`。最终代码/被测SHA：8aa37c5aa55821d40a527e42ee9bc47ffc32371f；原main保持8a3075521312c9bf9ad196309422adaa0c67fbd2。没有remote创建、合并、推送、报名修改或正式发布。

## 已实测入口

```sh
python3 scripts/verify.py --mode local --evidence evidence/local-delivery-recheck
```

从干净已提交项目根运行，用新目录，不覆盖冻结证据。要求既有锁定工具链/下载档和`.venv-reference`；验证器不负责安装，不会跳过缺项。最终完整结果在evidence/T8/final-local/report.json：17子进程步骤通过，Moon58、Python22、validation42、CLI15，324基础任务及1296变形共1620实际产品调用，38成员源候选包及解包消费者/CLI/六命令通过。原始stdout/stderr/命令/退出码/产物hash与源码绑定独立保留。

原始构建命令：

```sh
scripts/with-toolchain.sh moon build cmd/mooneventeval --target native --release --deny-warn
_build/native/release/build/cmd/mooneventeval/mooneventeval.exe evaluate examples/duplicate.json --format json
_build/native/release/build/cmd/mooneventeval/mooneventeval.exe explain-pair examples/boundary.json --recording clip-01 --reference r1 --prediction p1 --format json
```

源候选只含运行源/API/native stub、三案例、公开文档/许可和安装器/锁。原生exe只认证本机Darwin arm64。Python只作开发验证，产品评分在MoonBit；C负责native I/O。候选身份local/mooneventeval@0.1.0，不是注册表发布。

## 继续时的边界

T6固定合成范围：315非边界共同口径一致；9边界中6一致、1具体binary64差异、2原版零collar域限制，不冒称全部原始指标一致。T6 M1超时部分输出取证缺口延期，输入JSON重名键last-wins已披露。

本人纸笔复算/三分钟口头demo/M2尚未完成，现有讲稿和八例推导是agent材料。正式namespace/仓库URL、远端CI、Linux实测、发布和赛事资格尚未完成；配置或自动日志不能代替它们。正式申报须用户本人基于确认事实改写。

后续代理先读AGENTS、PROJECT_STATE、contracts和本阶段结果；核实际git状态/HEAD，不按聊天记忆重做已完成阶段。唯一有效独立复核为df214268候选，作者I1缓存修复为8aa37c5；两个入口真实RED→GREEN、最终17步骤通过，无第二次独立复审。详见[结果](reviews/2026-10-22-t8-results.md)与[处置](reviews/2026-10-22-t8-review.md)。T8 M1含NUL的合法ID可评测/API解释，但不能由literal OS argv选择，仍延期。未经明确授权，不创建远端、推送、触发CI或发布。

最终证据冻结：`python3 evidence/T8/freeze.py`。后续内部文档/证据收尾HEAD与被测代码分别记账；使用git rev-parse HEAD查询当前HEAD。本轮保留原分支和工作树，无集成操作。

2026-10-22接续：用户将验证全权交给Codex，取消本地人工复测要求。历史“本人M2”混用已更正；本人讲解没有证据仍不编造。P1交付包及下一远端阶段见[交付准备](delivery/READINESS.md)。
