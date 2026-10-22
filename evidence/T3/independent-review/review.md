# T3 单次 fresh-context 独立只读评审

范围：base `9c78a20aaa34514e218afd7ce26cae1e0ce03046` → head `e9c7f317bcd141aa34dbcc3e1ee6728415be3824`。
本报告只评价该候选；作者后续新增 RED 或修复不在本结论内。中断后恢复的是同一次评审，没有再派代理或进行第二轮评审。

## Strengths

- Recording/Task 工厂验证后复制输入数组，Event/Config/Recording/Task/Evaluation 保持封装，pairs() 返回新数组；实现与复制边界测试一致。
- 分组采用规范码点顺序、同组 eligibility 与 T2 matcher、全任务共享预算；计数先相加后计算微平均，声明但未使用的类别与空录制均保留。错误分支不会返回部分 Evaluation。
- 成功报告包含完整明细、精确十进制阈值和确定性工作计数。Fraction 秒空间 oracle 与部分注入 graph oracle 独立于产品的定点整数与增广路径实现。
- 已检查 binary64 差异的原始记录：10.3−10.1 对应 `0x1.99999999999c0p-3`，大于 0.2 的 `0x1.999999999999ap-3`；不是用泛称“浮点误差”掩盖差异。零 collar 的原版域限制和产品精确判断分开记录。
- 在 git archive 临时源码中重新执行锁定 native 测试：37/37 通过；release probe 构建退出码 0。原工作树/index/HEAD 未被评审者修改。

## Issues

### Critical (Must Fix)

无。

### Important (Should Fix)

1. **[P1] 字符串使用 MoonBit 转义，导致合法输入产生非法 JSON。**
   - 位置：`eventeval/report_json.mbt:125`（by_label 字符串）；同类问题也位于 `:64`、`:65`、`:88`、`:136`、`:147`、`:148`、`:184`、`:201`、`:202`。
   - `String.escape()` 是 MoonBit 字符串字面量转义；固定 core 对 U+0000–U+001F 中除 backspace/tab/LF/CR 外的 28 个字符生成 `\u{xx}`。JSON 只接受 `\uXXXX`，不能解析该输出。
   - 最小合法输入 `{"schema_version":1,"labels":["\u0001"],"recordings":[]}` 得到 exit 0/status completed，但 by_label.label 为 `"\u{01}"`，Python json.loads 抛 JSONDecodeError。32 个控制字符逐一实际执行，28 个失败。加未知根字段 `"\u0001":0` 时 exit 2 的 error.path 同样是非法 JSON，因而失败协议也损坏。
   - 影响：公开契约允许所有非空有效 Unicode ID/类别；调用方不能消费这种成功或失败报告。普通 JSON 输入不应使 JSON 输出失效。
   - 建议：所有用户来源的字符串都使用同一个真正的 JSON string encoder，例如固定 core 的 Json::String(...).stringify()；保留现有固定对象键序。覆盖成功报告各字符串位置与失败 path 的控制字符往返断言，不仅检查子串。
   - 收据：`label-control-01.input.json`、`label-control-01.stdout`、`unknown-control.input.json`、`unknown-control.stdout`、`review-checks.json`、`replay_review.py`。

2. **[P2] full-report comparator 规范化产品值并漏查类型/形状，会把违反机器契约的报告判为一致。**
   - 位置：`validation/compare.py:102`–`:110` 对实际事件时间规范化；`:78`–`:79`、`:131`、`:138`–`:139` 使用宽松 Python 相等；`:60`–`:73` 和 `:84`–`:90` 没有检查嵌套精确键集合/顺序。
   - 已用真实 probe 的正确输出作为基线，仅修改报告后调用 compare_document：将未匹配事件 onset_s 从 `"1"` 改成数字 `1`，仍返回 `[]`。把 schema_version 改成 true、work.candidate_checks 改成 false、work.eligible_edges 改成 0.0，或加入 summary/by_label 行/work 的额外字段，也均返回 `[]`。
   - 影响：T3 明确冻结字符串时间、整数计数和字段形状；现有比较器可能将这些产品回归记为完整报告通过。这里不是声称当前产品已输出数字时间，而是实际验证器假阴性。
   - 建议：先独立验证产品报告的字段、类型、规范十进制文本与固定顺序，再做数值/语义比较；仅规范化输入期望，不能纠正被测输出。对这些篡改加入拒绝测试。保持独立 oracle，不复制产品遍历逻辑。
   - 收据：`review-checks.json` 的 comparator_mutations，及可重放 `replay_review.py`。其中 matching_steps=1 的空报告也被接受；该额外收据不用于要求比较器复制 matcher 的精确计步算法。

### Minor (Nice to Have)

无。

## Recommendations

修复上述两个缺陷后，执行作者已有回归套件及针对性控制字符往返/比较器拒绝检查，保存新的实际被测 SHA、原始输出和退出码；不能继续用本次 e9c7f31 的通过日志替代修复后的证据。

## Declined to judge

- 正式文件 CLI、文件/流 I/O 故障、explain-pair、文本/demo：属于 T4/T5/T6 后续阶段；开发 argv probe 不承担这些接口。
- 广泛非边界随机 sed_eval 对照与最终 A11：T3 prototype 明确限定为固定合成/二进制网格，不足以完成最终对照门槛。
- M2 用户本人纸笔复算/讲解：八例材料明示 agent 编写，无法证明个人理解；不能据此宣布完成。
- Linux/跨平台、远端 CI、包外正式消费者、发包/赛事资格：未纳入此 T3 本地机器核心验收，且无相应实证。
- JSON 重名键后值覆盖与原版 zero collar 不支持：契约明确接受/分类的已知行为，本轮不要求擅改解析或参考算法。
- STATE/任务卡/最终 manifest 的收尾待写：作者明确待评审后更新，本轮不把这项流程顺序当作代码缺陷。
- 对所有合法图均在 20M 步内完成及宿主峰值内存/墙钟承诺：契约允许预算拒绝，并明确未作全图性能保证；本轮检查共享限额与无部分分数的实现/现有测试。

## Assessment

**Ready to merge? No（修复后再按实际结果验收）。**

**T3 当前实施能否验收？不能。** e9c7f31 对合法 Unicode 输入生成非法成功 JSON，并且普通未知字段错误也可能生成非法错误 JSON，直接违反 T3 核心机器协议。比较器还存在已复现的协议漏检，需同时补强。分组/精确数学/复制/预算部分未发现独立阻断缺陷，但其通过不能抵消 JSON 协议失败。

## 验证边界与可保存收据

直接复跑：native 37/37、release probe 构建、32 控制字符成功路径、1 个控制字符错误路径、8 个比较器篡改实例。
源码/证据阅读：契约、T3 卡、PRD §5–9、产品实现/测试、独立 oracle/comparator、原版 binary64 记录。未再次运行完整 sed_eval 46 例、全部 Python 套件或 mutation；这些属于作者提供证据，本报告不将其称为独立复跑。
未使用历史记忆作为判断依据。

临时目录：`/private/tmp/t3-independent-review-2o6zhped`。
- `review.md`：本报告。
- `receipt.json`：固定 base/head、源码提取方法、开始状态。
- `commands.json`：准确构建/测试命令、cwd 和退出码。
- `moon-test.log`、`probe-build.log`：原始完整日志。
- `replay_review.py`、`replay_review.log`、`review-checks.json`：脚本、原输出、所有输入命令/返回码/篡改详情。
- `label-control-*.input.json/.stdout/.stderr`、`unknown-control.*`：真实进程原始文件。
- `manifest.json`：可保存收据的 SHA-256，不包含临时源码与构建产物。

重放：`python3 -B /private/tmp/t3-independent-review-2o6zhped/replay_review.py /private/tmp/t3-independent-review-2o6zhped/source`。
脚本也可传入另一个已构建 probe 的源码目录，但当前报告结论只绑定原候选。
