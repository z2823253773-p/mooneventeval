# MoonEventEval 当前状态

更新：2026-10-21（America/Phoenix）。**T0、T1、T1b、T2完成；T2独立评审PASS。完整JSON产品、CLI/demo、产品parity/M2/A11仍未完成。**

## 当前入口与位置

- [contracts](contracts.md) → [修订计划v2](superpowers/plans/2026-10-20-mooneventeval-plan-v2.md) → [T2实际结果](reviews/2026-10-21-t2-results.md) / [独立评审](reviews/2026-10-21-t2-review.md) → [下一T3卡](superpowers/plans/tasks/T3-evaluation.md)。旧单文件v1计划已作废。
- Codex主实施者；工作树`/Users/henryz/Desktop/比赛/mooneventeval-t0`，分支`spike/t0-feasibility`。原仓库main仍`8a3075521312c9bf9ad196309422adaa0c67fbd2`，干净且无remote。复用已有局部工具链/参考venv，不重复T0/T1/T1b/T2。
- T2基线`bb23267ac56f040f17797106a36659bed1613cd8`；代码与被测SHA **`e96d130338ab379968a5cb4624788ba079dadda9`**。后续只提交状态/文档/证据，最新HEAD以git log为准；不把未测运行代码包装成已测。
- [T2 manifest](../evidence/T2/manifest.json)列文件hash、命令/退出码/日志、独立配对期望与实际输出、每轮耗时、mutation、review原收据。

## 已完成与实证

- T0固定MoonBit0.10.14+7d59c7ec9/清单/JSON/native短I/O/本地打包验收。T1精确时间、工厂/Unicode、码点排序、候选资格13项通过。
- T1b局部uv0.11.14/CPython3.11.14、NumPy1.26.4、dcase_util0.2.20、setuptools80.9.0；45个依赖hash锁与全新venv重建通过；原版sed_eval12个.py评测前核验。详情保留[T1b结果](reviews/2026-10-20-t1b-results.md)，其自检不是产品parity。
- T2包内first-free+完整显式栈DFS最大匹配，输出规范索引配对/度数/本次steps/search adjacency_checks；共享20M预算，操作前计步，失败不返回Matching。单边3、陷阱11、limit0..10逐界拒绝、跨组delta和1000层链通过。
- 部分注入oracle6项自检；两侧各0..3所有689图加seed20261020的64张4..7图，共753。检查最大基数、边合法性、双方唯一、顺序与度数；真实配对native输出落盘，重跑753组一致，fixture生成字节一致。
- native release直接二进制：完全500/1000为126250/502500步，稀疏1000为3000，长链1000为6997，均完整匹配；每图预热1轮+5轮，进程耗时含构图/断言/启动且排除编译，仅macOS arm64。没有全图/跨平台时间保证。
- 两个独立副本mutation控制组通过，预测重复使用和跳过增广均编译成功、行为失败。
- 被测SHA e96d130复验MoonBit25/25、原Python4/4、validation15/15；fmt/info/check/build经锁定wrapper通过，公开mbti无变化。
- fresh独立评审Critical0/Important0/Minor0；新副本release25/25、直接二进制753图/四bench、Hall公式753图、oracle6/6、生成器字节一致、两mutation均复验；其对原Python4/4与全validation15/15仅核日志/hash。评审收据已复制入仓库。

## 决定、作废与限制

- 用户“下一步”授权T2及first-free修订。固定开发策略标识`first-free-iterative-dfs/v1`；原v1纯DFS被该策略替代，预算不增加，未切HK。
- T3保证规范图索引、严格升序/去重/范围内邻接及合法共享budget；T2不是公开schema校验。每个root进入一次，失败first-free后DFS不重复计root；逻辑配对两个方向数组维护合计1步。O(E)度数统计不属于搜索步，受事件2000上界约束；Matching.steps是调用delta，总报告取共享used。
- T1声明级unused、T2 WorkBudget/Matching/maximum_matching局部临时豁免在T3正式消费后移除；不为消警告扩大公开接口。
- 原版sed_eval拒绝0 collar，适配器保留ValueError并标记域限制；产品0 collar仍合法，T3/T6用有理数oracle分类，不能epsilon或取消A11。raw/projected/substitution区分继续有效。
- TSV/CSV、数字时间、增加模式未批准；重名/转义等价JSON键后值覆盖仍是已披露限制。T3先核心后demo的门槛修订仍待相应批准，T1b成功不意味着A11通过。
- 未验证：原事件重排→规范图的端到端稳定性、JSON任务/报告、CLI/demo、八例本人复算讲解、完整产品parity/M2/A11、Linux/远端CI、包外消费/发布。赛事当前资格/换题/截止细则与真实需求仍未确认。没有访问临床数据、外发、合并、推送、报名变更或发布。

## 下一步与命令

下一实施目标：**T3严格输入、全任务评测、稳定JSON报告与开发probe**。读AGENTS/contracts/T3卡，消费T1工厂及T2接口；固定工具链会拒绝tuple/array的旧Show调试用法，测试优先布尔相等或目标版Debug，避免照抄旧inspect示例扩大deprecated豁免。原版参考已可用，须实际跑并分类zero-collar/浮点边界，不拿self-check充parity。

复验：

```sh
scripts/with-toolchain.sh moon test --target native --deny-warn
python3 -W error::ResourceWarning -m unittest discover -s tests
.venv-reference/bin/python -W error::ResourceWarning -m unittest discover -s validation/tests -v
python3 validation/check_matching_native.py --output-dir evidence/T2/recheck
python3 validation/mutate_matching.py
```

新checkout参考重建：`python3 validation/bootstrap_reference.py`；已有venv拒绝覆盖，需要另建时用`--venv .venv-reference-rebuild`。仅macOS arm64资格已验，不在全局Python安装。
