# MoonEventEval 当前状态

更新：2026-10-20（America/Phoenix）。**T0、T1、T1b完成；T2实施和本地验证已通过，待最终独立评审及交接。T1b原版参考self-check与哈希锁重建PASS；完整产品、产品parity/M2/A11尚未完成。**

## 当前入口与位置

- [contracts](contracts.md) → [修订计划v2](superpowers/plans/2026-10-20-mooneventeval-plan-v2.md) → [T1b实际结果](reviews/2026-10-20-t1b-results.md) / [独立评审](reviews/2026-10-20-t1b-review.md) → [下一T2卡](superpowers/plans/tasks/T2-matching.md)。旧单文件v1计划已作废。
- Codex主实施者；工作树 `/Users/henryz/Desktop/比赛/mooneventeval-t0`，分支 `spike/t0-feasibility`。原仓库main保持`8a3075521312c9bf9ad196309422adaa0c67fbd2`，无remote；先核对真实git状态，不重复T0/T1/T1b。
- T1b基线`0b6fcf7b7368a7e6793cd815b0b2d29b2926c210`；最后被测候选`221916c56b945805c92119a1fca53a58b9b29c29`（运行代码/锁提交dd99ff4，候选仅增加validation README）。最新文档/证据提交以git log为准。
- [T1b manifest](../evidence/T1b/manifest.json)含源码/锁hash、命令、退出码、失败及完整输出。安装/排障始于2026-10-21 06:11:27 UTC，三小时硬停止点09:11:27 UTC；本轮在预算内完成。

## 已完成与证据边界

- T0固定MoonBit工具链/清单/JSON/native短I/O/本地打包已验收；T1精确时间、工厂/Unicode、码点排序、候选资格已验收，MoonBit13/13与原Python工具4/4保持通过。T1历史上未装参考环境，现在T1b已独立完成，不混用两个阶段状态。
- T1b：局部uv0.11.14/CPython3.11.14、NumPy1.26.4、dcase_util0.2.20、setuptools80.9.0；45个完整依赖版本/hash锁。先锁build后端，再require-hashes/no-build-isolation在全新.venv-reference中真实重建sed_eval与dcase_util，依赖检查通过。
- 7项原版reference self-check及2项bootstrap安全检查共9/9；首轮/锁重建的45个依赖版本和4组完整结果一致；12个参考.py评测前核验hash。没有参考源码修改、NumPy别名补丁或产品输出充当oracle期望。
- 原版实际结果：重复预测TP1、A2 optimal TP2；跨类raw Nsubs1且FP/FN0，显式共同口径投影FP/FN1。raw NaN标记保留，投影零分母null。开发参考CLI的实际输出也与API一致。
- 独立评审未发现Critical/Important，评审者报告复跑9/9并核对来源/版本/完整输出；唯一Minor为候选STATE旧历史语句，本轮按计划最终状态更新消除，不改运行代码。
- 未完成：匹配、完整JSON任务/报告/产品CLI/demo、独立产品parity/M2/A11、本人复算/讲解、有理数oracle、Linux/远端CI、包外消费与正式发布。参考self-check不是这些交付的替代。

## 已作决定与适用限制

- T1b历史范围只包含参考环境；当前轮次执行T2。uv缓存、解释器、venv和bootstrap运行缓存局部化；保留缺pkg_resources的真实失败，补其未声明运行依赖setuptools80.9.0。没有NumPy别名失败，故1.23.5备用轮NOT_RUN，不制造失败或强行降级。
- 原版构造函数拒绝0 collar；适配器保留ValueError、flags明确不支持。产品0 collar仍合法，T3/T6须用有理数oracle并分类这一参考域限制，不能用epsilon或取消A11。
- raw/class_wise/projected/metric_definition_flags四区已冻结，见contracts。参考时间为Float64，不能代替Int64/有理数边界裁定；raw global substitution与投影必须分开。
- Python来源为uv选择的python-build-standalone，归档SHA及归档解释器/安装解释器一致；不冒称Python.org二进制认证。uv的PEP610 archive_info为空，来源证据依赖锁强制和源码核验，不伪称PEP610提供hash。
- 保留上游pkg_resources弃用等告警。T1声明级unused暂时豁免仍需T3消费时移除。T0 core只有历史hash一致，来源缺口未升级为认证。
- T1b三小时独立任务已获本轮授权并执行；T3先核心后参考的阶段门槛变更仍待相应批准。T2 first-free算法修订已随用户“下一步”获本阶段授权并实施；TSV/CSV/JSON数字时间及删除最终原版对照未批准。
- 赛事当前资格/换题/截止细则与真实需求仍未确认；没有临床数据访问、外发、推送、报名变更或发布。

## 下一步与命令

下一实施目标T2最大匹配、小图穷举、提前密集图检查；按任务卡核对并明确算法修订，不在参考适配器里写产品算法。

复验：`.venv-reference/bin/python -m unittest discover -s validation/tests -v`（9项）；`scripts/with-toolchain.sh moon test --target native --deny-warn`（13项）；`python3 -W error::ResourceWarning -m unittest discover -s tests`（4项）。

新checkout参考重建：`python3 validation/bootstrap_reference.py`。已有venv拒绝覆盖，需要新一套时用`--venv .venv-reference-rebuild`；仅macOS arm64资格已验。不要在agent-reach或全局Python安装。MoonBit局部工具链已在本工作树，无需重装。
