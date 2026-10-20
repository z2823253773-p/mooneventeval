# MoonEventEval 当前状态

更新：2026-10-20（America/Phoenix）。**用户已授权T0；技术探针通过，独立评审中。产品未实现。**

## 当前入口与位置

- [修订计划v2](superpowers/plans/2026-10-20-mooneventeval-plan-v2.md) → [contracts](contracts.md) → [T0卡](superpowers/plans/tasks/T0-feasibility.md) → [实际结果](reviews/2026-10-20-t0-results.md)。旧单文件v1计划停止执行。
- Codex主实施者；工作树 `/Users/henryz/Desktop/比赛/mooneventeval-t0`，分支 `spike/t0-feasibility`。原仓库main保持`8a3075521312c9bf9ad196309422adaa0c67fbd2`，无remote。
- T0开始15:51:16 UTC；安装16:02:52 UTC完成，早于16:21:16网络预算；总截止17:51:16 UTC。
- 被测源码`b69e6653bf0e1674226b2ceaa3e223cfd827e992`；最后证据`evidence/T0/20261020T160625Z/results.json`含命令、退出码、日志和源码哈希。文档/证据提交以git log为准。

## 已完成与限制

- 项目局部固定工具链已安装并校验：moonc v0.10.14+7d59c7ec9。二进制符合发布者sidecar及固定SHA；core仅符合历史观测SHA，不是发布者认证。
- 实跑旧fn失败/新fn_count成功、JSON键fn不变；inspect成功/inspect!失败；新清单成功/旧JSON清单仍能运行但弃用；JSON6/6；native短读写和真实退出7；真实本地包产物CRC/文件表/哈希。
- Python安装安全测试3/3，完整结构lint单列；均不代表产品正确。保留安装首次超时、JSON首轮警告失败、native首轮产物定位失败。
- Native只测macOS arm64短合成输入，未实现完整I/O；Python只有开发工具。产品、独立参考、mutation、本人复算/讲解、包外消费、Linux/远端CI、正式发布均未完成。

## 决定、作废与阻塞

- 作废：旧Counts.fn和inspect!写法、把深度参数视作无警告、清单格式混用、把结构lint当可行性证据。有效兼容写法已写回contracts。
- JSON深度参数在目标core弃用，但实际仍工作；唯一解析适配函数用局部#warnings("-deprecated")，其余仍deny-warn。升级目标版本必须重验，不扩大全局例外。
- 裁决：原生worktree工具报Not a git repository，改建相邻Git工作树；成本为手动维护生命周期。模块化T0用显式矩阵替代数字任务解析；成本为人工核对完整性。当前仅执行T0，成本为后续阶段仍需安排。
- first-free+DFS及T1b/T3阶段修订仍标待批准；TSV/CSV、JSON数字时间、删除最终原版对照未批准。A11原版参考仍为最终完整验收项。
- 外部缺口：选题/换题资格、赛事现行规则、截止具体时区/时刻、真实需求未确认；没有外发、推送、报名变更或发布。

## 下一步

完成T0 fresh只读评审，修复确实问题并记录结论。T1核心尚未开始。

复跑：`python3 spikes/T0/run_probes.py`；Python安全测试：`python3 -W error::ResourceWarning -m unittest discover -s tests`；结构：`python3 scripts/check_design_docs.py`。

新环境先`python3 scripts/install_toolchain.py`（Python>=3.12、curl、C编译器；仅支持锁文件内的平台；已有目标目录会拒绝覆盖），再用`scripts/with-toolchain.sh`执行命令。不要重新安装全局工具链，不把T0探针复制成产品。
