# MoonEventEval 当前状态

更新：2026-10-20（America/Phoenix）。**Codex为主，产品未实现，目标工具链未安装、T0未运行。**

## 当前入口

- [修订计划v2](superpowers/plans/2026-10-20-mooneventeval-plan-v2.md) → [contracts](contracts.md) → [当前T0卡](superpowers/plans/tasks/T0-feasibility.md)。用户原回复“确认进行实施计划”，PRD v1曾获准写计划；v2算法/阶段调整及T0具体探针待审阅。原单文件v1计划已停止执行。
- 用户指定Codex为主、Claude Code偶尔参与；当前主实施者顺序工作，T0/T3增加fresh只读评审。无需再次选择主平台，不自动开用户chat。
- 接续读取AGENTS、本文件、contracts和当前卡；临时聊天摘要不替代磁盘契约。CLAUDE.md只转到同一入口。

## 已完成及证据边界

- 已完成：反馈核查、字段计划修正fn_count→JSON fn、共享契约及任务拆分、八个待本人复算例、demo草案、可落盘日志/文档检查脚本。
- 旧DFS完全图的邻接检查数学计数：n=500为20958500，已超20M预算；这是算式推导，不是算法运行时benchmark。
- 本轮代码基线为文档提交 `e8af47df8e978e195b6980cab4b6bf4669a2ff7c`；无被测产品SHA。文档最终HEAD以git log为准。
- 未完成：目标编译器探针、MoonBit产品代码/测试、参考环境/parity、mutation实跑、本人复算/讲解、包外消费、远端CI、注册表发布或组委会换题确认。

## 决定、作废及阻塞

- 作废：旧Counts.fn、只在T6测密集图、把v1结构自查视为可行性、没有实测支撑的两天核心排程。
- 待批准：2小时T0、first-free再DFS并提前密集图验证、T1b三小时独立排障且T3核心状态单列；A11最终原版对照仍保留。
- 未批准范围：TSV/CSV新增入口、JSON数字时间、删除最终原版对照；见BACKLOG.md。不默认把外部建议当用户批准。
- 外部缺口仍在：选题重复性/换题计次/剩余次数、正式章程当前细则、截止具体时区/时刻、真实需求。没有remote/推送/外发/报名变更。

## 下一步及命令

当前可运行的文档检查：`python3 scripts/check_design_docs.py`。日志版：`python3 scripts/capture_command.py --stage review --name docs -- python3 scripts/check_design_docs.py`。

下一实施目标只做T0。用户批准T0问题/探针后，按适用技能建立隔离worktree，先核对 `git status --short --branch` 和工具链发行证据；不要直接开始完整产品开发。

给新Codex/Claude Code的接续提示：读取AGENTS.md、本文件、contracts.md与T0卡，核对真实git状态；仅在已有明确批准时执行T0。结束写命令/退出码/日志/通过与未测项，不把默认版结果冒充锁定版本结果。
