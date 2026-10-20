# MoonEventEval v0.1 Implementation Plan（评审修订v2）

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans for Codex-led implementation; independent reviews follow applicable review skills. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 先证明目标工具链可用，再交付时间事件最大匹配核心、可运行CLI/demo和限定独立验证。

**Architecture:** Codex主实施者顺序推进共享MoonBit核心；T1b参考环境单拆；T0和T3安排fresh只读评审。Claude Code偶尔接续单任务或评审，使用相同磁盘契约，不承担常驻主流程。

**Tech Stack:** 目标工具链与来源同环境核查文件；实际支持语法由T0实证后冻结。首版native，Python仅独立参考。

**Spec:** [PRD](../specs/2026-10-20-mooneventeval-prd-design.md)；[共享契约](../../contracts.md)；[反馈处置](../../reviews/2026-10-20-claude-feedback-disposition.md)。

**Status:** T0/T1已执行，fresh评审问题修复后主验收PASS；完整评测器/CLI未实现。其余标记待批准的算法/阶段修订保持待批准。v1计划停止作为执行入口，保留历史以供追溯。

## 本轮修正与需确认的变化

- 已修正计划的MoonBit字段为fn_count，JSON键fn和Python断言不变；临时审计脚本来源移入仓库，新文档检查脚本可从仓库运行，结构检查不证明可行性。
- 建议批准：把编译器关键点提前为2小时T0；匹配任务提前测500/1000完全图并采用可回溯的first-free+DFS；T1b限时3小时、T3核心可与参考状态分开，最终A11仍保留。
- TSV是产品范围增量，当前列BACKLOG待确认；不一起加通用CSV，不默认放开JSON数字时间。
- 重名JSON键仍是PRD明确的已知限制，补显式测试。若需要拒绝，再改契约，不写易漏转义等价键的简陋预扫描。
- 先做demo，较重故障注入和远端/多平台硬化后置；最终缺口照实记录，不能把删验收当完成。

## Global Constraints / 文件接口地图

全部来自 [contracts.md](../../contracts.md)，不要在各任务复制一套常量/输出字段。当前任务只读该文件、STATE和一张任务卡；需要产品意图时读PRD相关章节。

## 任务顺序

| 阶段 | 文件 | 关键退出条件 |
| --- | --- | --- |
| T0 | [可行性探针](tasks/T0-feasibility.md) | 目标编译/清单/解析/borrow/打包真实结果，独立评审 |
| T1 | [时间核心](tasks/T1-time.md) | 精确转换/候选规则/Unicode/分数微秒 |
| T1b | [参考环境](tasks/T1b-reference.md) | 原版self-check与hash锁，或明确3小时失败记录 |
| T2 | [匹配](tasks/T2-matching.md) | 穷举、合法性、提前密集图预算及mutation |
| T3 | [评测核心](tasks/T3-evaluation.md) | 输入/空集/指标/核心原型、早期独立审阅 |
| T4 | [解释报告](tasks/T4-reports.md) | 同源解释、规范输出、最终字节检查 |
| T5 | [CLI与demo](tasks/T5-cli-demo.md) | 真命令/退出码/三分钟脚本与图示；本人讲解单独记账 |
| T6 | [独立验收](tasks/T6-qualification.md) | 原版限定parity、变形、mutation与实际资源结果 |
| T7 | [候选包](tasks/T7-package.md) | 文档/许可/解包后消费者，不冒充注册表发布 |
| T8 | [CI与交接](tasks/T8-ci-handoff.md) | 本地与已授权远端结果分开，最终fresh审阅 |

T1b是独立排障窗口，可按当前环境择机执行，不强制子代理并行。未解释的产品/数学差异始终阻断；参考环境超时可让纯核心证据单独成立，但不能让A11变成通过。

## 时间与止损

撤回“T1–T3两天必能完成”的暗示。先执行T0得到事实，按实际耗时重估剩余任务；原10月22–28安排是历史条件目标，不是当前可行性承诺。10月31日窗口与具体时区/审核流程仍待核实。

T0最多2小时；T1b最多3小时排障。T2密集图不满足预算就先修算法/契约，不扩大上限；核心mutation活下来说明测试不足，先补反例。临近截止时优先交可解释核心、真实demo和明确证据，缺项不得改写成已完成。

## Codex/Claude Code接续

以AGENTS.md为主，CLAUDE.md只转到相同入口；不默认使用Claude Code的/clear，也不规定每任务必须新chat。任务结束把状态写盘；确需换chat由用户发起，主流程不自动创建聊天。独立评审用适用授权下的fresh只读agent，给契约/diff/真实结果，回传不超过20行结论及文件位置。

T1已结束；下一目标为T1b参考环境，其余待批准范围按contracts和STATE处理。此文不授权外发、推送、发包或改报名。
