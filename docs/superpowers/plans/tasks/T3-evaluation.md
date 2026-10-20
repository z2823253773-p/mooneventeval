# T3-evaluation 任务卡

状态：修订待审；未实施。先读AGENTS.md、docs/PROJECT_STATE.md、docs/contracts.md，再读本卡；必要时读PRD相关章节。

T3是核心证据门槛；原版参考未完成需单独列出，最终A11不因固定样例自动通过。

## Task 3: 严格输入、全任务评测与最小原型门槛

**Files:** 创建 T3 地图文件、`eventeval/input_wbtest.mbt`、`evaluation_wbtest.mbt`、`validation/rational_oracle.py`、`validation/compare.py`；扩展 model/report 模型；证据 `evidence/T3/`。

**Interfaces:**
- Consumes：T1 Event/Config/PairBasis 与 T2 maximum_matching。
- Produces（public）：`recording(id: String, reference: Array[Event], prediction: Array[Event]) -> Result[Recording, EvalError]`；`task(labels: Array[String], recordings: Array[Recording], config: Config) -> Result[Task, EvalError]`；`decode_task(input: Bytes) -> Result[Task, EvalError]`；`evaluate(task: Task) -> Result[Evaluation, EvalError]`；`report_json(report: Evaluation) -> Result[String, EvalError]`；`evaluate_json(input: Bytes) -> Result[String, EvalError]`；Evaluation 的两个共享访问方法。
- Python：`rational_oracle.eligible(reference: dict, prediction: dict, config: dict) -> dict` 使用 Decimal→Fraction 独立计算；`compare.compare_document(document: dict, product: dict, reference: dict) -> list[dict]` 返回差异，不覆盖任何输出。

- [ ] **1. 写输入失败测试并运行 RED。** schema/config 默认回显、unknown字段、缺字段、数字型时间、空 labels、未知类别、重复各侧ID/录制ID、同ID跨侧允许、JSON语法/重名键、非法UTF-8/代理项。验证拒绝所有未声明类型而不是自动纠正。运行 `scripts/with-toolchain.sh moon test eventeval --target native --filter '*input*'`。
- [ ] **2. 写评测失败测试。** A1/A2 完整配对与计数；第7节四种空集；有预测但没有参考的录制、声明但未使用类别、跨录制及错类别；by_label/by_recording 各自计数和等于全局；不平均 F1。R2 构造后修改原输入数组及返回 pairs 副本，重评结果不变；R1 非 BMP/组合字符顺序稳定而不合并。

```moonbit
test "evaluation_duplicate_counts" {
  let r = event("r1", "alarm", "10", "12").unwrap()
  let p1 = event("p1", "alarm", "10", "12").unwrap()
  let p2 = event("p2", "alarm", "10.05", "12.05").unwrap()
  let rec = recording("clip-01", [r], [p1, p2]).unwrap()
  let input = task(["alarm"], [rec], default_config()).unwrap()
  let m = evaluate(input).unwrap().metrics()
  inspect((m.counts.tp, m.counts.fp, m.counts.fn_count), content="(1, 1, 0)")
}
```
- [ ] **3. 实现 schema 与评测。** `decode_task` 先检查实际字节数、严格 UTF-8（允许一个开头 UTF-8 BOM 并在文档注明）、`@json.parse(max_nesting_depth=16)`，再校验字段；共享 typed 工厂防御性复制。先完成全输入校验才建图；按录制/类别分组并用唯一 budget，degree 支持未配对原因。排序计数/完整明细后生成 PRD 所列机器字段，输出数字只有计数和指标，时间不经 Double。
- [ ] **4. 运行 native GREEN。** `scripts/with-toolchain.sh moon test eventeval --target native --deny-warn`；用固定序列打乱输入，多最优解的配对身份及完整 JSON 同版本一致；改 ID 后计数相同。此时 report_json 已返回完整、受限 JSON，不能先返回部分 summary 占位。
- [ ] **5. 创建可外部驱动的核心探针。** `cmd/probe` 只接受一个小 JSON 文本参数，转 bytes 调用 evaluate_json，将完整成功/错误 JSON 输出；不把参数传输尺寸用来宣称 8 MiB 文件契约已验证。`scripts/with-toolchain.sh moon build cmd/probe --target native --release --deny-warn`，用实际生成的 probe.exe 驱动三个 examples。
- [ ] **6. 分开记录核心与参考状态。** T1b成功时运行 `validation/compare.py --phase prototype --product <probe.exe> --output evidence/T3/parity`：至少A1/A2、精确二进制网格案例及跨类别substitution反例，A2 optimal预期TP2；A3/A4由有理数裁定并保留sed_eval实际边界表现。原始参考与projected分开，TP精确一致，空定义差异按PRD记录，不要求最优配对身份相同。T1b超时时此项明确未完成，不生成成功parity文件，也不声称两方原始输出已取得。
- [ ] **7. 判定 M2 门槛并提交。** 【待批准阶段修订】时间/候选、独立有理数、全部小图、八例复算材料及真实原型证据具备才记核心门槛通过；T1b成功则跑原版对照，若三小时预算耗尽则A11仍未完成，可进入最薄demo而不能称完整验收。已经取得的未解释核心差异仍阻断，不能用参考环境超时掩盖。保存源码SHA/输入/两方原始输出/退出码；提交 `feat: evaluate validated event tasks with stable counts`。


- [ ] **8. 早期独立评审与mutation。** 用户批准执行后，用fresh只读评审者审契约、diff、实际命令/输出，不给实施推理过程；至少验证起点<=改<、终点<=改<、max改min、参考时长改预测时长能使对应E3/E4/E5/E6测试变红，再恢复基线。未编译的mutation标invalid，不算有效发现。
