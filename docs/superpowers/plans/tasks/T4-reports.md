# T4-reports 任务卡

状态：已完成；产品d528d30、最终验证器/被测d00b0a6，独立Important1作者RED→GREEN修复，无二次复审。结果见docs/reviews/2026-10-21-t4-results.md；沿用T3固定接口与JSON编码。先读AGENTS.md、docs/PROJECT_STATE.md、docs/contracts.md，再读本卡；必要时读PRD相关章节。

保留准确解释、规范输出及最终UTF-8字节数检查；不提前做不必要的定制序列化设施。

## Task 4: 指定事件对解释、完整报告与输出预算

**Files:** 创建 T4 地图文件、`eventeval/explain_wbtest.mbt`、`report_wbtest.mbt`、`serialization_wbtest.mbt`；扩展 `report_json.mbt`；证据 `evidence/T4/`。

**Interfaces:**
- Consumes：Task/Evaluation、T1 eligibility、T3 report_json。
- Produces（public）：`explain_pair(task: Task, recording_id: String, reference_id: String, prediction_id: String) -> Result[PairExplanation, EvalError]`；`explanation_json(value: PairExplanation) -> Result[String, EvalError]`；`report_text(value: Evaluation) -> Result[String, EvalError]`；`explanation_text(value: PairExplanation) -> Result[String, EvalError]`。
- Produces（包内）：`format_scaled_seconds(value: Int64, fractional_digits: Int) -> String`；`bounded_serialize(value: Json, byte_limit: Int) -> Result[String, EvalError]`，限额参数仅内部/测试使用。

- [x] **1. 写失败测试。** A3前后边界、不同标签、找不到ID、未进入当前匹配但有候选、候选为零；解释不含计数、不运行 matching。R3 断言终点容差显示 `"0.0000015"`，负时间偏差有负号，零不输出 `-0`；文本明确“所选配对”与“未定义”。
- [x] **2. 加 R4 序列化测试并运行 RED。** ID 含换行、引号、反斜线和非 ASCII；JSON往返保留原值，文本安全转义且不改变身份；内部小 byte_limit 按真实 UTF-8 输出等号/超1检查，按最终字节数检查后返回Resource；不要求自写流式序列化器。运行 `scripts/with-toolchain.sh moon test eventeval --target native --filter '*report*'` 及 explain/serialization 筛选。

```moonbit
test "report_fractional_microsecond" {
  inspect(format_scaled_seconds(1_500_000L, 12), content="0.0000015")
}
```
- [x] **3. 实现同源解释与稳定序列化。** explain_pair 在完整已校验 Task 内选择同录制两侧事件，只调用 eligibility；阈值 scaled 用十二位秒精度规范格式化。JSON对象键固定顺序或使用统一规范写入器（不依赖 HashMap 遍历）；按编码后字节计预算，检查完整报告后才返回。匹配、FP/FN都带事件信息/degree/准确原因；不输出候选图。
- [x] **4. 运行 GREEN 与回归。** `scripts/with-toolchain.sh moon test eventeval --target native --deny-warn`；重复运行同版本报告字节相同。对真实 16 MiB 边界使用内部序列化测试构造字符串，不要求不可能的合法2000事件任务恰好触顶；合法任务另测输出容量。不能扩大schema或增加公开限额参数来测试。
- [x] **5. 保存并提交。** 归档解释JSON/文本、规范化/转义/字节边界结果；提交 `feat: explain event pairs and render bounded reports`。
