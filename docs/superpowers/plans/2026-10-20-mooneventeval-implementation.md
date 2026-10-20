# MoonEventEval v0.1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现可复现、可嵌入的 MoonBit 时间事件评测库与本地 CLI，以精确时间候选图和最大基数一对一匹配产生逐事件解释及 TP/FP/FN。

**Architecture:** 业务语义集中在一个 `eventeval` 包，按时间、输入、匹配、评测及报告文件分工；纯 MoonBit `cli` 包处理参数和调度，native 入口只适配文件、标准流和退出码。Python 标准库 oracle 与独立 sed_eval 虚拟环境负责验证，不进入运行时依赖。

**Tech Stack:** 固定 MoonBit `moonc v0.10.14+7d59c7ec9` 及配套 core，首版 native；macOS arm64/Linux x86_64 CLI；少量 POSIX C I/O 包装；Python 3.11.14 + uv 生成参考环境哈希锁。本轮未安装这些目标环境。

**Spec:** [已批准的 PRD](../specs/2026-10-20-mooneventeval-prd-design.md)，批准依据为用户本次回复“确认进行实施计划”；批准前版本位于 `a9f5b8f7f1d7c2140b49ad14ceaf525da4566e93`。

**Status:** 计划待用户审阅并选择执行方式。所有实施复选框均未勾选；没有产品实现、构建、参考运行或发布证据。

## Global Constraints

- 时间/比例只接受 ASCII 十进制字符串，语法 `^(0|[1-9][0-9]*)(\.[0-9]{1,6})?$`；秒转 Int64 微秒，比例转 ppm，无舍入、epsilon 或 Float64 时间判断。
- 每个事件满足 `0 <= onset < offset <= 2592000` 秒；`collar_s` 范围 0–2592000 秒，默认 `"0.2"`；`offset_ratio` 范围 0–1，默认 `"0.5"`。
- JSON `schema_version=1`；未知字段、缺失/错误类型、未知类别、重复录制 ID、同录制同侧重复事件 ID 为整任务错误；对象重名键后值覆盖；不去重事件。
- 输入 8 MiB，JSON 容器嵌套深度 16；录制/类别 1000/256；两侧合计 2000 事件；每个 ID/类别 256 个 Unicode 码点；匹配工作量 20000000 步；序列化报告 16 MiB，全部含等号。
- 每次邻接边检查、搜索顶点进入及增广配对改写各算一步，操作前扣预算；跨组累计。公开接口不增加预算配置字段。
- 同录制同类别配对，起点 `abs(delta)<=collar`，终点 `abs(delta)*1000000<=max(collar*1000000, reference_duration*ratio_ppm)`；边界含等号，不增加区间相交要求。
- 最大基数一对一匹配，不优化时间误差；Unicode 码点排序、固定 DFS 增广次序、显式栈；输入重排结果稳定，改 ID 不应改 TP/FP/FN。
- `TP=配对数`、`FP=预测数−TP`、`FN=参考数−TP`；全局先累计再微平均；P/R/F1 各自零分母为 null，F1 直接从计数计算。
- 退出码 0=完整评测/解释完成；2=输入、配置、参数或文件错误；3=资源限额导致未完成；4=内部非预期错误。失败不得含分数或部分配对；JSON 失败向 stdout 写结构化错误。
- 输出语义标识 `collar-max-cardinality/v1`，时间为规范十进制秒字符串；有效终点容差可至十二位小数。完成报告不含日期、运行耗时或本机路径。
- sed_eval 固定提交 `0cb1b6d11ceec4fe500cc9b31079c9d8666ed6eb`；保留原始 substitution/global FP/FN，共同口径投影必须显式命名；不宣称原始全局输出完全一致。
- 只使用合成或许可已确认的公开数据；不访问临床数据。保留原 MoonReconcile。新增 UI、格式、评分模式不在本计划内。
- 不创建远端、不发咨询、不修改表单、不推送、不正式发布；这些需用户另行明确授权。历史赛事规则不当作当前已确认条款，不为提交次数机械拆分提交。

## Review Focus

1. **R1 Unicode：**补充平面字符和组合字符不得按 UTF-16 单元排序或归一化合并；非法 UTF-8/孤立代理项须拒绝（Task 1/3）。
2. **R2 调用方修改数组：**构造 Task 后修改原 labels/events 数组不得悄悄改变评测；Task 持有防御性副本，返回的数组也不暴露内部可变状态（Task 3）。
3. **R3 分数微秒：**参考时长 3 微秒、比例 0.5 得到 1.5 微秒终点容差，不能截断、四舍五入或显示成整数微秒（Task 1/4）。
4. **R4 转义后输出大小：**控制字符/非 ASCII ID 的 JSON 转义可能膨胀；限额按最终 UTF-8 字节，不能按字符数或未转义大小放行（Task 4）。
5. **R5 native 文件边界：**NUL 路径不得被 libc 截断；短读、EINTR、目录/FIFO、不完整写入和不可读文件不能产生成功报告或无限等待（Task 5）。

---

## 文件与接口地图

路径均相对本仓库根目录 `/Users/henryz/Desktop/比赛/mooneventeval`。本轮只写本文及状态文档；下列产品文件由执行阶段创建。

| 路径 | 单一职责 / 创建任务 |
| --- | --- |
| `moon.mod`、`.gitignore`、`README.md` | 本地模块 `local/mooneventeval@0.1.0`、构建忽略、起步说明（T1）；这不是已注册包名，正式发布前再核实 namespace |
| `scripts/install_toolchain.py`、`scripts/with-toolchain.sh`、`docs/toolchain.lock.json` | 项目局部工具链安装、校验、运行和来源锁（T1） |
| `eventeval/moon.pkg`、`model.mbt`、`errors.mbt` | 不可变/封装模型、稳定错误和常量（T1，后续扩展输出模型） |
| `eventeval/time.mbt`、`eligibility.mbt` | 无损十进制转换、码点比较、时间候选依据（T1） |
| `eventeval/matching.mbt` | 有预算的确定性二分图匹配，无时间/JSON 依赖（T2） |
| `eventeval/input.mbt`、`validation.mbt`、`evaluation.mbt`、`report_json.mbt` | schema、复制校验、分组与指标、稳定机器报告（T3） |
| `cmd/probe/moon.pkg`、`main.mbt` | 开发专用、小 JSON 参数探针，调用真实 evaluate_json；不读文件、不发布为产品命令（T3） |
| `eventeval/explain.mbt`、`report_text.mbt`、`serialization.mbt` | 指定事件对解释、人类报告、最终字节预算（T4） |
| `cli/moon.pkg`、`args.mbt`、`dispatch.mbt` | 可测试的参数/调用/退出码决策（T5） |
| `cmd/mooneventeval/moon.pkg`、`main.mbt`、`native_io.mbt`、`io_stub.c` | 只读有界文件与标准流 I/O、进程退出（T5） |
| `examples/duplicate.json`、`greedy-trap.json`、`boundary.json` | 三份完整合成场景（T3），配套解释说明（T5/7） |
| `validation/reference-requirements.in`、`reference-constraints.txt`、`reference.lock`、`bootstrap_reference.py`、`sed_reference.py` | 原版参考环境、原始结果与明确投影（T1/3/6） |
| `validation/graph_oracle.py`、`rational_oracle.py`、`generate_cases.py`、`compare.py`、`benchmark.py` | 独立穷举、有理数、确定性用例、比较与性能记录（T2/3/6） |
| `validation/tests/test_reference.py`、`test_oracles.py`、`test_comparison.py` | 独立验证器自己的反例与防伪一致检查（T1/2/6） |
| `eventeval/*_wbtest.mbt`、`cli/args_test.mbt`、`tests/cli/test_cli.py` | 对应任务的白盒/接口/真实进程验收 |
| `tests/consumer/moon.mod.json`、`main/moon.pkg.json`、`main/main.mbt` | 包外消费者模板（T7），由脚本复制到临时目录运行 |
| `.moonignore`、`LICENSE`、`THIRD_PARTY_NOTICES.md`、`docs/API.md`、`EXAMPLES.md`、`VALIDATION.md` | 包内容、许可、真实可运行说明（T7） |
| `scripts/verify.py`、`scripts/check_consumer.py`、`scripts/package_candidate.py`、`tests/test_verify.py`、`.github/workflows/ci.yml` | 统一检查及故障测试、包外调用、候选归档、授权后可触发的 CI（T7/8） |
| `docs/PROJECT_STATE.md`、`docs/ACCEPTANCE.md`、`evidence/<stage>/` | 当前状态、逐项证据、输入/输出/失败与版本（各任务） |

依赖方向：`cmd -> cli -> eventeval`；Python 验证器只能从外部调用探针/真实二进制，产品不 import Python。eventeval 保持一个包，避免数组/错误/时间类型跨多层分包重复公开；文件各有职责，不能把全部实现堆进 model 或 main。

### 共享类型约定

- `EvalError`：`kind: FailureKind`（Input/Resource/Internal）、`code: String`、`message: String`、`path: String?`、`limit: Int64?`、`observed: Int64?`；`exit_code(error)` 唯一映射 2/3/4。
- 稳定 code 集合：`INVALID_JSON`、`INVALID_UTF8`、`INVALID_UNICODE`、`INVALID_SCHEMA`、`UNKNOWN_FIELD`、`MISSING_FIELD`、`INVALID_TYPE`、`INVALID_DECIMAL`、`OUT_OF_RANGE`、`DUPLICATE_ID`、`UNKNOWN_LABEL`、`ID_NOT_FOUND`、`INVALID_ARGUMENT`、`FILE_ERROR`、`RESOURCE_LIMIT`、`INTERNAL_ERROR`；任何资源种类用RESOURCE_LIMIT，path/limit/observed区分。深度超限不是INVALID_JSON，未知recording/event查询为ID_NOT_FOUND。
- `Event`、`Config`、`Recording`、`Task` 为封装类型；通过下列工厂创建。Task 不暴露内部数组，工厂验证并复制传入数组；新建事件/config 时也检查范围。
- `Counts`：`reference/prediction/tp/fp/fn: Int`；`Metrics`：`counts: Counts`、`precision/recall/f1: Double?`。
- `PairBasis`（包内）：`label_match/onset_pass/offset_pass/eligible: Bool`、`onset_delta_us/offset_delta_us/onset_limit_us/offset_limit_scaled: Int64`；scaled 的单位为微秒×1000000。
- `WorkBudget`（包内）：共享可变 `used/limit: Int64`；仅白盒测试可设小 limit。`Matching`（包内）：`pairs: Array[(Int,Int)]`、`reference_degree/prediction_degree: Array[Int]`、`steps: Int64`，索引对应规范排序后的顶点。
- Matching.steps只记录本次调用消耗（退出used减进入used）；全任务work.matching_steps直接取最终共享budget.used，不再次累加各次累计值。
- `Evaluation`、`PairExplanation` 为封装结果；`Evaluation::metrics() -> Metrics`，`Evaluation::pairs() -> Array[(String,String,String,String)]` 返回副本，四元组为录制/类别/参考ID/预测ID。完整数据通过报告函数访问。

### 机器报告字段冻结

T3/T4实现如下形状，不能由不同任务各自命名：顶层 `schema_version=1`、`semantics="collar-max-cardinality/v1"`、`implementation_version="0.1.0"`、`status="completed"`、`config`、`summary`、`by_label`、`by_recording`、`matches`、`false_positives`、`false_negatives`、`work`。config使用输入字段名及规范秒/比例字符串。summary为 `{counts:{reference,prediction,tp,fp,fn},precision,recall,f1}`；类别/录制行分别为 `{label,metrics}` / `{recording_id,metrics}`，metrics同summary形状。

匹配行为 `{recording_id,label,reference,prediction,basis}`，两事件使用输入的id/label/onset_s/offset_s字段及规范时间；basis为 `{label_match,onset_pass,offset_pass,eligible,onset_delta_s,offset_delta_s,onset_limit_s,offset_limit_s}`。未匹配行为 `{recording_id,event,candidate_count,reason}`；work为 `{candidate_checks,eligible_edges,matching_steps}`。explain报告沿用版本/状态/config，并包含recording_id、reference、prediction、basis，不含summary、work或匹配身份推断。

失败形状为 `{schema_version:1,status:"failed",error:{kind,code,message,path,limit,observed}}`；kind为小写input/resource/internal，后三个可为null。输出采用上述固定键序，所有数组按PRD排序；错误不携带完成报告字段。

## Task 1: 精确时间与候选判断，连同可复现验证环境

**Files:** 创建 T1 地图文件；测试 `eventeval/time_wbtest.mbt`、`eventeval/eligibility_wbtest.mbt`、`validation/tests/test_reference.py`；证据 `evidence/T1/`。

**Interfaces:**
- Consumes：PRD 的十进制语法、范围、容差公式及固定 sed_eval 源码。
- Produces（public）：`event(id: String, label: String, onset_s: String, offset_s: String) -> Result[Event, EvalError]`；`config(collar_s: String, offset_ratio: String) -> Result[Config, EvalError]`；`default_config() -> Config`。
- Produces（包内）：`parse_time_us(text: String, path: String) -> Result[Int64, EvalError]`、`parse_ratio_ppm(text: String, path: String) -> Result[Int64, EvalError]`、`eligibility(reference: Event, prediction: Event, config: Config) -> PairBasis`、`compare_codepoints(a: String, b: String) -> Int`。
- Python：`sed_reference.evaluate_document(document: dict) -> dict` 返回 raw、class_wise、projected、metric_definition_flags 四区，尚不比较产品。

- [ ] **1. 固定隔离执行位置和工具链。** 先按 using-git-worktrees 技能，从本计划最终提交创建 `feature/eventeval-v0.1` 与隔离 worktree，记录真实基线。工具链解包到该 worktree 的 `.tools/moonbit/0.10.14+7d59c7ec9/`；只由 `with-toolchain.sh` 为子进程设置 MOON_HOME/PATH，不改 shell 配置或默认安装。下载 URL、精确哈希和停止条件见[环境核查附件](../../research/2026-10-20-plan-environment.md)；不允许 latest 或哈希不符继续。
- [ ] **2. 写失败测试。** `decimal_exact`：`"10.05" -> 10050000`、`"0.000001" -> 1`、`"2592000" -> 2592000000000`；`decimal_reject` 拒绝 `"01"`、`"1e-6"`、`" 1"`、`"-0"`、七位小数和超界；`ratio_bounds` 检查 0/1/超界及零 collar。

```moonbit
test "decimal_exact" {
  inspect!(parse_time_us("10.05", "onset_s").unwrap() == 10_050_000L, content="true")
  inspect!(parse_time_us("0.000001", "onset_s").unwrap() == 1L, content="true")
  inspect!(parse_time_us("2592000", "offset_s").unwrap() == 2_592_000_000_000L, content="true")
}
```
- [ ] **3. 写候选/字符失败测试。** A3、A4 等号及超 1 微秒；参考时长主导与固定 collar 主导；不相交短事件可合格；R1 比较 U+E000 与 U+10000（前者排前）；R3 用 r=[10,10.000003]、c=0、q=0.5，期望 scaled=1500000，终点偏差 1 微秒合格、2 微秒不合格。
- [ ] **4. 运行 RED。** `scripts/with-toolchain.sh moon test eventeval --target native --filter '*decimal*'`，再运行候选/字符测试；期望因缺目标API或目标行为而失败，不能把工具链损坏、错误导入或缺依赖当作行为 RED。初始化 manifest 与测试导入属于本任务必需搭建，保留实际诊断。
- [ ] **5. 实现上面签名及错误常量。** 有界逐字符十进制积累，范围验证先于乘法；比例与时间共用精确扫描而保留不同上限；不调用 Double.parse。所有事件/config 有效性由同一函数定义，标签条件不代替录制分组。码点比较不依赖未经证明的 String 默认比较。
- [ ] **6. 建立未改算法的参考环境。** `bootstrap_reference.py` 使用项目局部 uv Python 3.11.14 及 `.venv-reference/`，从固定提交取得 sed_eval；requirements.in使用该提交的GitHub archive URL并锁归档hash，不用仅有同版本号的PyPI替代物或editable/VCS未哈希安装。第一套约束 `numpy<2`、`dcase_util==0.2.20`；执行 import 和重复检测 self-check。若实际报 NumPy 旧别名兼容失败，只允许第二次新环境加入 `numpy==1.23.5`，保留首轮失败；其他失败或第二次失败即阻断该阶段，不修改参考源码、不伪装运行成功。用 `uv pip compile --generate-hashes` 产出最终精确锁，重新建环境以 `uv pip sync --require-hashes` 复现；验证器记录完整 Python/依赖版本及源码哈希。
- [ ] **7. 验证 GREEN 与解析前提。** `scripts/with-toolchain.sh moon test eventeval --target native --deny-warn`；`.venv-reference/bin/python -m unittest discover -s validation/tests -p test_reference.py -v`。参考 self-check 断言重复样例 Ntp=1/Nsys=2/Nref=1，并保留 raw。原型测试实际确认 core JSON 重名键后值覆盖、16 层深度参数生效、UTF-8 严格解码和孤立代理项行为；若标准解析器会保留孤立代理项，在业务字符串校验中拒绝，不换契约。
- [ ] **8. 保存并提交。** `evidence/T1/manifest.json` 记录命令、退出码、版本、下载/源码哈希及失败；日志分开保留。提交 `feat: define exact event time and collar eligibility`；参考锁及其 self-check 可作为独立实质提交，不凑次数。未通过参考门槛时可保留时间核心 WIP，但不得将 M2 标为完成或继续 CLI/UI。

## Task 2: 确定性最大匹配与独立图穷举

**Files:** 创建 `eventeval/matching.mbt`、`matching_wbtest.mbt`、`matching_oracle_generated_wbtest.mbt`、`validation/graph_oracle.py`、`validation/tests/test_oracles.py`；证据 `evidence/T2/`。

**Interfaces:**
- Consumes：规范排序后的顶点、按预测索引升序的 adjacency；T1 EvalError。
- Produces（包内）：`maximum_matching(adjacency: Array[Array[Int]], prediction_count: Int, budget: WorkBudget) -> Result[Matching, EvalError]`；`consume_step(budget: WorkBudget) -> Result[Unit, EvalError]`。
- Python：`graph_oracle.max_cardinality(adjacency: list[list[int]], prediction_count: int) -> int`，用所有部分注入的枚举求最大值，不写另一份增广算法。

- [ ] **1. 写失败测试。** `augmenting_trap` 输入 `[[0,1],[0]]`，结果两对 `(0,1),(1,0)`；`one_to_one_duplicate` 输入 `[[0,1]]` 只有一对；空两侧、1×0、全连接、孤立点、多个最优解的固定次序均覆盖。验证每对存在边、两侧各不重用。
- [ ] **2. 锁定工作步口径并运行 RED。** 单边图 root进入+边检查+改写=3步，小 limit=3 成功、limit=2 返回 Resource 且无 Matching；空图 0 步、一个无边参考 1 步。运行 `scripts/with-toolchain.sh moon test eventeval --target native --filter '*matching*'`，确认因缺算法/错误行为失败。

```moonbit
test "matching_one_edge_budget" {
  let budget : WorkBudget = { used: 0L, limit: 3L }
  let result = maximum_matching([[0]], 1, budget).unwrap()
  inspect!(result.pairs, content="[(0, 0)]")
  inspect!(result.steps == 3L, content="true")
}
```
- [ ] **3. 实现显式栈 DFS 增广。** 每个参考按索引从小到大启动搜索；预测升序；每轮重置访问集合，路径经已占用预测回到其参考；找到空预测后反向改写整条路径。没有可增广路径才启动下一个参考。只在成功完成后返回配对；全任务共享 budget，不在每组重新给 20000000 步。
- [ ] **4. 写独立 oracle 自检并生成静态期望。** `test_oracles.py` 断言 trap=2、全连接=较小侧、无边=0；枚举 R/P 各 0–3 的每张图，另加 seed=20261020 的 4–7 顶点图。`python3 validation/graph_oracle.py --emit-mbt eventeval/matching_oracle_generated_wbtest.mbt` 写入邻接与期望数据及生成器哈希；文件只含数据/调用/断言，不复制 oracle 算法到产品。
- [ ] **5. 运行 GREEN。** `python3 -m unittest discover -s validation/tests -p test_oracles.py -v`，再运行 `scripts/with-toolchain.sh moon test eventeval --target native --deny-warn`；所有图最大基数及配对合法性精确一致，生成文件重跑不变。构造长增广路径确认不依赖宿主递归栈。
- [ ] **6. 保存并提交。** 证据保留图输入、独立期望、真实结果、工作步边界及种子；提交 `feat: implement deterministic maximum event matching`。数量不是验收替代：任一非法配对或少算都阻断后续。

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
  inspect!((m.counts.tp, m.counts.fp, m.counts.fn), content="(1, 1, 0)")
}
```
- [ ] **3. 实现 schema 与评测。** `decode_task` 先检查实际字节数、严格 UTF-8（允许一个开头 UTF-8 BOM 并在文档注明）、`@json.parse(max_nesting_depth=16)`，再校验字段；共享 typed 工厂防御性复制。先完成全输入校验才建图；按录制/类别分组并用唯一 budget，degree 支持未配对原因。排序计数/完整明细后生成 PRD 所列机器字段，输出数字只有计数和指标，时间不经 Double。
- [ ] **4. 运行 native GREEN。** `scripts/with-toolchain.sh moon test eventeval --target native --deny-warn`；用固定序列打乱输入，多最优解的配对身份及完整 JSON 同版本一致；改 ID 后计数相同。此时 report_json 已返回完整、受限 JSON，不能先返回部分 summary 占位。
- [ ] **5. 创建可外部驱动的核心探针。** `cmd/probe` 只接受一个小 JSON 文本参数，转 bytes 调用 evaluate_json，将完整成功/错误 JSON 输出；不把参数传输尺寸用来宣称 8 MiB 文件契约已验证。`scripts/with-toolchain.sh moon build cmd/probe --target native --release --deny-warn`，用实际生成的 probe.exe 驱动三个 examples。
- [ ] **6. 实跑首轮独立对照。** `validation/compare.py --phase prototype --product <probe.exe> --output evidence/T3/parity`：至少运行 A1/A2、精确二进制网格案例及跨类别 substitution 反例；A3/A4 由有理数裁定并保留 sed_eval 的实际边界表现。原始参考结果与 projected 分开，TP精确一致，空定义差异按 PRD 记录；不要求最优配对身份相同。
- [ ] **7. 判定 M2 门槛并提交。** 时间/匹配 tests、小图穷举、真实原型输出和参考环境/首轮共有语义同时具备才记“最小核心通过”。任一未解释差异则停在修核心，不进入 T4/T5。保存源码SHA/输入/两方原始输出/退出码；提交 `feat: evaluate validated event tasks with stable counts`。

## Task 4: 指定事件对解释、完整报告与输出预算

**Files:** 创建 T4 地图文件、`eventeval/explain_wbtest.mbt`、`report_wbtest.mbt`、`serialization_wbtest.mbt`；扩展 `report_json.mbt`；证据 `evidence/T4/`。

**Interfaces:**
- Consumes：Task/Evaluation、T1 eligibility、T3 report_json。
- Produces（public）：`explain_pair(task: Task, recording_id: String, reference_id: String, prediction_id: String) -> Result[PairExplanation, EvalError]`；`explanation_json(value: PairExplanation) -> Result[String, EvalError]`；`report_text(value: Evaluation) -> Result[String, EvalError]`；`explanation_text(value: PairExplanation) -> Result[String, EvalError]`。
- Produces（包内）：`format_scaled_seconds(value: Int64, fractional_digits: Int) -> String`；`bounded_serialize(value: Json, byte_limit: Int) -> Result[String, EvalError]`，限额参数仅内部/测试使用。

- [ ] **1. 写失败测试。** A3前后边界、不同标签、找不到ID、未进入当前匹配但有候选、候选为零；解释不含计数、不运行 matching。R3 断言终点容差显示 `"0.0000015"`，负时间偏差有负号，零不输出 `-0`；文本明确“所选配对”与“未定义”。
- [ ] **2. 加 R4 序列化测试并运行 RED。** ID 含换行、引号、反斜线和非 ASCII；JSON往返保留原值，文本安全转义且不改变身份；内部小 byte_limit 按真实 UTF-8 输出等号/超1检查，Resource错误无半截JSON。运行 `scripts/with-toolchain.sh moon test eventeval --target native --filter '*report*'` 及 explain/serialization 筛选。

```moonbit
test "report_fractional_microsecond" {
  inspect!(format_scaled_seconds(1_500_000L, 12), content="\"0.0000015\"")
}
```
- [ ] **3. 实现同源解释与稳定序列化。** explain_pair 在完整已校验 Task 内选择同录制两侧事件，只调用 eligibility；阈值 scaled 用十二位秒精度规范格式化。JSON对象键固定顺序或使用统一规范写入器（不依赖 HashMap 遍历）；按编码后字节计预算，检查完整报告后才返回。匹配、FP/FN都带事件信息/degree/准确原因；不输出候选图。
- [ ] **4. 运行 GREEN 与回归。** `scripts/with-toolchain.sh moon test eventeval --target native --deny-warn`；重复运行同版本报告字节相同。对真实 16 MiB 边界使用内部序列化测试构造字符串，不要求不可能的合法2000事件任务恰好触顶；合法任务另测输出容量。不能扩大schema或增加公开限额参数来测试。
- [ ] **5. 保存并提交。** 归档解释JSON/文本、规范化/转义/字节边界结果；提交 `feat: explain event pairs and render bounded reports`。

## Task 5: 本地 native CLI 与真实失败路径

**Files:** 创建 T5 地图文件与 `cli/args_test.mbt`、`tests/cli/test_cli.py`；证据 `evidence/T5/`。

**Interfaces:**
- Consumes：T3/T4 全部 public API 和 EvalError。
- Produces（cli public）：`parse_args(args: Array[String]) -> Result[CliRequest, ArgFailure]`；`run(request: CliRequest, input: Result[Bytes, EvalError]) -> CliOutput`；`render_arg_failure(error: ArgFailure) -> CliOutput`。
- `CliRequest`：`operation: Operation`（Evaluate(path)/ExplainPair(path,recording,reference,prediction)/Help/Version）、`format: OutputFormat`（Text/Json）。`ArgFailure` 携带输出格式与 EvalError。`CliOutput`：`stdout/stderr: Bytes`、`exit_code: Int`。
- Produces（入口包内）：`read_file_bounded(path: String) -> Result[Bytes, EvalError]`；`write_all(fd: Int, bytes: Bytes) -> Result[Unit, EvalError]`。C `mee_open_readonly(path)->Int32`、`mee_read(fd,buffer,count)->Int32`、`mee_close(fd)->Int32`、`mee_write(fd,buffer,count)->Int32`；Bytes以#borrow传递，包装函数明确 ssize_t→Int32 范围，不存借用指针，不包含业务规则。

- [ ] **1. 写参数失败测试并运行 RED。** 评测与 explain-pair 的精确命令、默认text、--format json、缺文件/缺ID/未知及重复选项、未知命令；Help/Version只允许单独调用且不读文件。合法 `--format json` 出现时即使其他参数错误也返回JSON；format本身非法或重复时返回text诊断。命令在首位、文件在第二位、选项在其后，不引入未定义的环境默认值。运行 `scripts/with-toolchain.sh moon test cli --target native`。
- [ ] **2. 写真实进程失败测试。** Python `unittest` 用 `MEE_BIN` 指向 release exe；A1结果与退出0；零分/不合格解释仍退出0；坏schema/未知ID/不可读文件=2；8 MiB等号（合法JSON加空白）成功，超1=3；深度17=3；JSON错误仅failed，无summary/matches/NaN。测试调用exe而非把moon run的状态当产品退出码。

```python
def test_duplicate_real_process(self):
    run = subprocess.run([os.environ["MEE_BIN"], "evaluate", "examples/duplicate.json", "--format", "json"], capture_output=True, text=True)
    self.assertEqual(run.returncode, 0, run.stderr)
    counts = json.loads(run.stdout)["summary"]["counts"]
    self.assertEqual((counts["tp"], counts["fp"], counts["fn"]), (1, 1, 0))
```
- [ ] **3. 实现参数/调度和有界 native I/O。** CLI库决定输出/退出码；入口读取 argv、只读 open、每次最多65536字节且全程最多8 MiB+1，关闭所有已开描述符。拒绝NUL路径及非普通文件；open先用非阻塞方式避免FIFO挂起，fstat后拒绝设备/目录/FIFO；允许读取普通文件符号链接。C包装处理EINTR/短读，MoonBit驱动聚合；输出预检后写入，底层短写循环或明确内部/IO失败。日志不污染stdout，输入绝不覆盖。
- [ ] **4. 验证 R5 和内部错误路径。** C包装的测试构建注入短读/EINTR/短写，不增加用户开关；真实缺文件/目录/FIFO/NUL（NUL用入口函数测试，OS argv无法携带）及断开输出管道有界终止。输出设备失败可能已写出前缀，不能承诺撤回；必须非零且不能记录completed证据。错误4仅用于非预期故障，不把普通文件错误改成4。
- [ ] **5. 运行 GREEN。** `scripts/with-toolchain.sh moon test cli --target native --deny-warn`；`scripts/with-toolchain.sh moon build cmd/mooneventeval --target native --release --deny-warn`；`MEE_BIN=_build/native/release/build/cmd/mooneventeval/mooneventeval.exe python3 -m unittest discover -s tests/cli -v`。记录实际exe路径/哈希/命令，三份examples在text/json都能跑，explain-pair单独运行。
- [ ] **6. 保存并提交。** 归档真实输入/输出/退出码与所有限额/失败记录；提交 `feat: expose event evaluation through a bounded native CLI`。CLI目标先声明已验证的本机OS，Linux支持等CI/实机证明后再写。

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
- [ ] **5. 实测稀疏/稠密/长路径。** release、记录CPU/OS/编译器/exe哈希，2000事件稀疏目标5秒；1000×1000稠密组与长增广链记录用时、峰值内存、退出码、工作步。可以明确预算未完成，但普通案例经常超预算即不可用，不仅调大上限。macOS/Linux分别记录，不混峰值内存计量单位。
- [ ] **6. 跑 GREEN 并生成差异账本。** `python3 -m unittest discover -s validation/tests -v`；`.venv-reference/bin/python validation/compare.py --phase qualification --product <exe> --output evidence/T6/parity`；`python3 validation/benchmark.py --product <exe> --output evidence/T6/performance`。每个解释差异须有最小反例、原始值及原因；未解释差异保留并阻断，不能改期望或删样本。
- [ ] **7. 保存并提交。** `evidence/T6/manifest.json` 锁定产品SHA/工具链/数据种子/文件哈希/输出/退出码/比较范围；提交 `test: independently qualify event matching and time boundaries`。通过后再进入交付候选；测试数不等于需求验收。

## Task 7: 包外调用、可发布候选与可运行文档

**Files:** 创建/完善 T7 地图文件、`docs/PROJECT_STATE.md`、`docs/ACCEPTANCE.md`；证据 `evidence/T7/`。

**Interfaces:**
- Consumes：稳定public API、T6证据及可运行CLI。
- Produces：`scripts/check_consumer.py --source <module-root> --output <dir>`；`scripts/package_candidate.py --output <dir>`；README命令及API示例实际运行记录。脚本返回0只表示本地消费/候选检查成功，不表示注册表发布。

- [ ] **1. 先写会失败的外部消费者。** 临时目录内独立moon.mod.json，path依赖指向待测模块；仅 import `local/mooneventeval/eventeval`，通过public工厂与evaluate构造A1并断言tp=1/fp=1/fn=0及报告可解析；缺API/字段或路径指回测试源码即失败。消费者自身不复制匹配/指标逻辑。

```moonbit
test "consumer_duplicate" {
  let r = @eventeval.event("r1", "alarm", "10", "12").unwrap()
  let p1 = @eventeval.event("p1", "alarm", "10", "12").unwrap()
  let p2 = @eventeval.event("p2", "alarm", "10.05", "12.05").unwrap()
  let rec = @eventeval.recording("clip-01", [r], [p1, p2]).unwrap()
  let input = @eventeval.task(["alarm"], [rec], @eventeval.default_config()).unwrap()
  let m = @eventeval.evaluate(input).unwrap().metrics()
  inspect!((m.counts.tp, m.counts.fp, m.counts.fn), content="(1, 1, 0)")
}
```
- [ ] **2. 实现候选打包及消费脚本。** 使用 `moon package --list --frozen` 和实际归档；解包到新的临时目录再运行包外消费者，避免只测工作树。`.moonignore` 明确保留core/cli/native stub、README、LICENSE、NOTICE和必要API/案例；排除探针、虚拟环境、工具链、构建产物、原始日志、内部咨询/计划。逐项核对归档实际文件及README链接；下载/发包不在此步骤。
- [ ] **3. 补齐文档与许可。** 自有实现建议MIT，新增LICENSE/署名以确认的仓库作者信息为准；引入代码/数据逐项保留许可。README写实际工具链、安装/编译/两命令/空值/限制，EXAMPLES写三项任务的完整输入-操作-输出-解释；VALIDATION说明projection/浮点/空集边界及复现命令。未有真实反馈就只写开发者复现，未测后端不宣称支持。
- [ ] **4. 核对待公开身份。** 本地 `local/mooneventeval` 是开发名。无远端/namespace授权时，记录正式仓库URL和包名未完成，候选标为本地；不填虚构URL。收到具体授权后才替换namespace/URL，并重跑包外消费/包内容/链接检查；不能把原namespace候选当新包实测结果。
- [ ] **5. 运行 GREEN。** `python3 scripts/check_consumer.py --source . --output evidence/T7/consumer`；`python3 scripts/package_candidate.py --output evidence/T7/package`；实际运行README三案例及explain命令。归档清单、SHA-256、API快照、消费者输入输出/退出码分开保存。
- [ ] **6. 保存并提交。** 提交 `docs: document runnable event evaluation and package contracts`；打包策略/消费者可单独成实质提交。更新ACCEPTANCE每项A1–A12的证据链接，未满足项明确列出，不以本地打包替代Mooncakes发布。

## Task 8: 统一检查、CI配置与最终可审阅交接

**Files:** 创建 `scripts/verify.py`、`tests/test_verify.py`、`.github/workflows/ci.yml`；完善 `docs/PROJECT_STATE.md`、`docs/ACCEPTANCE.md`、`docs/VALIDATION.md`；证据 `evidence/T8/`。

**Interfaces:**
- Consumes：T1–T7所有已通过阶段、工具链锁与reference.lock。
- Produces：`python3 scripts/verify.py --mode local --evidence <dir>`（本地真实检查）；CI调用同一脚本，OS/arch必须实测；最终交接包含当前分支/SHA、证据范围、未完成事项。
- verify.py以当前工作目录为项目根，首先要求该目录有本项目manifest；不因脚本路径位于另一份仓库就静默改测另一份代码。

- [ ] **1. 写检查器失败测试/故障注入。** 在tests/test_verify.py验证缺少实际binary、子命令非0、缺参考环境、改动工具链哈希、归档缺LICENSE任一情况必须非0，不能生成总通过；运行 `python3 -m unittest discover -s tests -p test_verify.py -v` 确认RED再实现检查器。可在临时复制品注入，不改已验证基线；证据解析不能把“未运行/跳过”当成功。

```python
def test_missing_project_never_passes(self):
    repo = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory() as directory:
        run = subprocess.run([sys.executable, str(repo / "scripts/verify.py"), "--mode", "local", "--evidence", str(Path(directory) / "proof")], cwd=directory, capture_output=True)
        self.assertNotEqual(run.returncode, 0)
```
- [ ] **2. 实现统一检查。** 记录 `moon version --all`；检查格式和生成接口不产生未提交diff；native check/test及release build；真实CLI测试、独立对照、消费者和包内容检查；各子进程保留退出码和日志，全部通过才完成本地总表。先按最终代码SHA验证，后续文档提交与被测SHA分别记账。
- [ ] **3. 写固定版本CI。** macOS arm64与Linux x86_64矩阵，安装校验同一固定工具链/core，Python参考环境从同一哈希锁同步；CI调用verify而非另写缩减测试。第三方Actions固定提交SHA后使用，权限contents:read；没有远端授权时仅保存配置和本地检查，状态为“远端未运行”。绝不配置自动发包、自动改报名或密钥输出。
- [ ] **4. 完成分支级独立复核。** 按用户选择的执行方式进行：Native由当前实施者顺序完成后请一名fresh reviewer在可用的最强模型上审整条分支；Subagent-driven按任务独立审阅后仍做整分支审阅。复核重点为最大匹配完备性、预算传播、输入精度/Unicode、解释与全局projection、native借用生命周期、包外契约；有问题修复并重跑受影响检查，不能把审阅意见当测试结果。
- [ ] **5. 运行最终验证并交接。** 先提交已完成的产品/检查器/CI配置为 `ci: verify the event evaluation delivery candidate`，核对代码工作树干净并记录被测SHA；再运行 `python3 scripts/verify.py --mode local --evidence evidence/T8/local`，核对归档hash及每个A项证据。本轮新增证据文档可随后提交，但不能因此把后来HEAD说成已经实测的代码SHA。授权后如有远端CI，再记录确切run URL/被测SHA/OS结果；未授权则明列远端CI、正式包、报名未完成。
- [ ] **6. 保存并提交交付证据。** 提交 `docs: record event evaluation candidate acceptance evidence`，最终核对干净工作树，区分被测代码SHA与此文档HEAD；交付本地可运行结果及事实清单。公开选题差异说明须更新为真实已实现范围；正式申报由用户本人基于确认事实撰写。按finishing-a-development-branch流程处理分支，不自动推送、合并或发布。

## 统一证据与阶段顺序

每个stage的manifest包含：阶段状态、产品SHA（含dirty标志）、oracle/参考SHA、工具链/OS/架构、原始argv、退出码、输入/输出/错误文件及SHA-256、比较器版本和排除范围。报告与失败原件只追加，修复后另建run；不能覆盖历史失败造成“首次就通过”的假象。日志不收集临床/账号敏感材料，体积过大的合成输入保留生成器/种子/哈希及可复算命令。

顺序固定为 **T1 → T2 → T3（最小核心门槛）→ T4 → T5 → T6（独立验收门槛）→ T7 → T8**。没有共享接口冻结前不并行改同一核心包；无论执行方式，任务未过门槛不启动下一任务。若核心失败，只修相关层与独立参考，暂停CLI/UI外围扩展。

PRD时间目标保持：M2在10月22–23日对应T1–T3；10月24–25日T4–T5；10月26日T6；10月27–28日T7–T8；10月29–30日缓冲。均按America/Phoenix，只是有条件目标；官网截止具体时区/时刻及审核流程仍待用户核实。审批或技术失败占用时间时如实更新，不把日期排程当完成证据。

## 计划自查与执行交接

| PRD范围 | 责任任务 |
| --- | --- |
| 用户任务/三案例/易用流程 | T3、T4、T5、T7 |
| 精确时间/容差/安全上界/Unicode | T1、T3、T4 |
| 最大匹配/重叠/重复/固定选择/预算 | T2、T3、T6 |
| 输入错误/空集/跨录制类别/指标 | T3、T5、T6 |
| 稳定输出/指定对解释/资源失败 | T4、T5、T6 |
| 独立穷举/有理数/sed_eval/差异边界 | T1、T2、T3、T6 |
| 文档/许可/包外消费/CI/交付证据 | T7、T8 |
| 非目标/数据边界/查重与赛事不确定性 | Global Constraints，T7/T8事实交接；不靠实现消除外部未确认事项 |

计划编写者逐项检查接口命名、任务依赖、五项Review Focus的归属、PRD A1–A12覆盖和步骤可操作性；记录见 [计划自查](../../reviews/2026-10-20-plan-review.md)。本计划建议 **Native 顺序实施，结束后独立复核整分支**，因为八项任务共享模型、错误、精度和报告契约，且M2/M4是串行证据门槛；用户也可选择Subagent-driven逐任务实施/审阅。

用户审阅本计划并选择执行方式后，才调用对应 executing-plans 或 subagent-driven-development 技能；执行时先建立隔离worktree，不在本轮搭建产品或安装依赖。
