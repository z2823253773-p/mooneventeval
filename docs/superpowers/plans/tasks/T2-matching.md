# T2-matching 任务卡

状态：已完成并通过独立只读评审；代码e96d130，实际结果见docs/reviews/2026-10-21-t2-results.md。用户“下一步”授权当前T2及其中first-free策略。先读AGENTS.md、docs/PROJECT_STATE.md、docs/contracts.md，再读本卡；必要时读PRD相关章节。

算法修订本阶段执行已授权；T2本身就测密集图，不把资源风险延迟到交付阶段。

## Task 2: 最大匹配、小图穷举与提前密集图检查

**Files:** 创建 `eventeval/matching.mbt`、`matching_wbtest.mbt`、`matching_oracle_generated_wbtest.mbt`、`validation/graph_oracle.py`、`validation/tests/test_oracles.py`；证据 `evidence/T2/`。

**Interfaces:**
- Consumes：规范排序后的顶点、按预测索引升序的 adjacency；T1 EvalError。
- Produces（包内）：`maximum_matching(adjacency: Array[Array[Int]], prediction_count: Int, budget: WorkBudget) -> Result[Matching, EvalError]`；`consume_step(budget: WorkBudget) -> Result[Unit, EvalError]`。
- Python：`graph_oracle.max_cardinality(adjacency: list[list[int]], prediction_count: int) -> int`，用所有部分注入的枚举求最大值，不写另一份增广算法。

- [x] **1. 写失败测试。** `augmenting_trap` 输入 `[[0,1],[0]]`，结果两对 `(0,1),(1,0)`；`one_to_one_duplicate` 输入 `[[0,1]]` 只有一对；空两侧、1×0、全连接、孤立点、多个最优解的固定次序均覆盖。验证每对存在边、两侧各不重用。
- [x] **2. 锁定工作步口径并运行 RED。** 单边图 root进入+first-free边检查+改写=3步，小 limit=3 成功、limit=2 返回 Resource 且无 Matching；空图 0 步、一个无边参考 1 步。运行 `scripts/with-toolchain.sh moon test eventeval --target native --filter '*matching*'`，确认因缺算法/错误行为失败。

```moonbit
test "matching_one_edge_budget" {
  let budget : WorkBudget = { used: 0L, limit: 3L }
  let result = maximum_matching([[0]], 1, budget).unwrap()
  inspect(result.pairs == [(0, 0)], content="true")
  inspect(result.steps == 3L, content="true")
}
```
- [x] **3. 实现显式栈 DFS 增广。** 【本阶段实施策略】每个参考先按升序检查空闲预测，能直接配对就完成本轮；否则按升序启动完整DFS增广，不能把first-free当作不可回溯的永久贪心；每轮重置访问集合，路径经已占用预测回到其参考；找到空预测后反向改写整条路径。没有可增广路径才启动下一个参考。只在成功完成后返回配对；全任务共享 budget，不在每组重新给 20000000 步。
- [x] **4. 写独立 oracle 自检并生成静态期望。** `test_oracles.py` 断言 trap=2、全连接=较小侧、无边=0；枚举 R/P 各 0–3 的每张图，另加 seed=20261020 的 4–7 顶点图。`python3 validation/graph_oracle.py --emit-mbt eventeval/matching_oracle_generated_wbtest.mbt` 写入邻接与期望数据及生成器哈希；文件只含数据/调用/断言，不复制 oracle 算法到产品。
- [x] **5. 运行 GREEN。** `python3 -m unittest discover -s validation/tests -p test_oracles.py -v`，再运行 `scripts/with-toolchain.sh moon test eventeval --target native --deny-warn`；所有图最大基数及配对合法性精确一致，生成文件重跑不变。构造长增广路径确认不依赖宿主递归栈。
- [x] **5a. 提前检查密集图。** native release直接测500×500及1000×1000完全图、稀疏图和长增广链，记录邻接检查/步骤/耗时，完全图应完整匹配且不耗尽20000000步。旧DFS邻接检查数为n(n+1)(n+2)/6，n=500时20958500，已知会超预算；不能等T6才发现。first-free失败则暂停并提出固定次序HK方案，更新契约及穷举，不自动放宽预算。此处n=500/1000均在2000总事件限制内。
- [x] **5b. 检验测试能抓到错配。** 在隔离副本让一个预测可重复使用、或在首个局部匹配后跳过增广，对应合法性/trap测试必须失败；编译失败不计mutation被杀死。恢复基线后重新GREEN。

- [x] **6. 保存并提交。** 证据保留图输入、独立期望、真实结果、工作步边界及种子；提交 `feat: implement deterministic maximum event matching`。数量不是验收替代：任一非法配对或少算都阻断后续。

实际增加的开发文件：matching_benchmark_wbtest.mbt、validation/check_matching_native.py、validation/mutate_matching.py；只服务本卡native/反证检查，不增加产品接口。度数记账与搜索步区分、临时unused豁免及评审边界见contracts和结果文档。
