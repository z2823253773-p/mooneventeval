# T6-qualification 任务卡

状态：用户“下一步”授权执行中；沿用固定PRD/契约，不取消最终验收。先读AGENTS.md、docs/PROJECT_STATE.md、docs/contracts.md，再读本卡；必要时读PRD相关章节。

原版参考A11仍是最终验收条件；超时只能报告部分完成。mutation验证产品测试，而不只验证比较器。

## Task 6: 全面独立对照、变形检查与资源实测

**Files:** 创建/完善 T6 地图文件、`validation/tests/test_comparison.py`、`validation/fixtures/comparison-baseline.json`、`tests/cli/test_resources.py`；证据 `evidence/T6/`。

**Interfaces:**
- Consumes：真实CLI、T1最终reference.lock、T2穷举和T3独立有理数oracle。
- Produces：`compare.py --phase qualification --product <exe> --output <dir>` 返回0=无未解释差异，非0=存在未解释差异/运行失败；`benchmark.py --product <exe> --output <dir>` 生成独立性能记录，不污染产品JSON。

- [ ] **1. 写验证器自身失败测试并运行 RED。** `test_comparison.py` 人工篡改一个TP、删一个预测独有录制、把 raw/projection偷换、把null改0、隐藏子进程失败，比较器必须非0且保留差异；相同最大配对数而身份不同不得假失败。`python3 -m unittest discover -s validation/tests -p test_comparison.py -v`。

用T3成功样例固定包含input/product/reference三键的comparison-baseline.json，作为比较器防伪一致测试夹具，不替代独立算法oracle：

```python
def test_changed_tp_is_rejected(self):
    fixture = json.loads(Path("validation/fixtures/comparison-baseline.json").read_text())
    bad = copy.deepcopy(fixture["product"])
    bad["summary"]["counts"]["tp"] += 1
    self.assertTrue(compare.compare_document(fixture["input"], bad, fixture["reference"]))
```
- [ ] **2. 实现确定性数据生成。** seed=20261020；精确二进制共有组采用0.125秒网格/c=0.25/q=0.5；普通十进制组采用默认配置，仅由独立Fraction计算每条候选比较的安全余量，预先排除≤1微秒者，保存生成总量/排除理由/剩余输入。另建不排除的精确边界组专门分析差异；三组不可混写成“全部兼容”。
- [ ] **3. 验证全链与变形性质。** CLI JSON实际跑每例；逐录制/类别计数、显式全局projection、双方有定义指标按1e−12；乱序报告稳定，合法整体平移保持配对计数，复制一个独立录制使计数翻倍，增加无候选预测只增加FP。全部结果再满足一对一、合法边、计数守恒。oracle不调用产品私有函数，也不从产品结果生成期望。
- [ ] **4. 跑资源等号/超1。** 覆盖1000/1001录制、256/257类别、2000/2001事件、256/257码点、30天与多1微秒、深度16/17、8 MiB等号/超1；20M工作步用内部可注入计数测试，不公开预算参数；16 MiB序列化边界沿T4。资源失败不得有部分分数；数值业务范围错误仍为2。
- [ ] **5. 实测稀疏/稠密/长路径。** release、记录CPU/OS/编译器/exe哈希，2000事件稀疏目标5秒；1000×1000稠密组与长增广链记录用时、峰值内存、退出码、工作步。可以明确预算未完成，但普通案例经常超预算即不可用，不仅调大上限。先记录本机macOS；Linux仅在获得可用授权执行环境后记录，否则明确未测，不让不可用环境阻塞本地核验，也不宣称Linux通过。
- [ ] **6. 跑 GREEN 并生成差异账本。** `python3 -m unittest discover -s validation/tests -v`；`.venv-reference/bin/python validation/compare.py --phase qualification --product <exe> --output evidence/T6/parity`；`python3 validation/benchmark.py --product <exe> --output evidence/T6/performance`。每个解释差异须有最小反例、原始值及原因；未解释差异保留并阻断，不能改期望或删样本。
- [ ] **7. 保存并提交。** `evidence/T6/manifest.json` 锁定产品SHA/工具链/数据种子/文件哈希/输出/退出码/比较范围；提交 `test: independently qualify event matching and time boundaries`。通过后再进入交付候选；测试数不等于需求验收。


- [ ] **8. 保留mutation证据。** 基线通过→每个可编译错误变体目标测试变红→恢复原文件哈希并重跑GREEN；记录invalid/equivalent/survived/killed。<=改<、max改min、错用预测时长、重复用预测、空集F1改1均需命中对应测试。交换max两操作数是等价变体，不能伪装有效mutation。
