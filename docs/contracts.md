# MoonEventEval 共享契约

版本：评审修订 v2，T0已获用户授权并完成技术探针，独立评审中。当前无产品消费者。已批准PRD的数学/资源/数据边界继续有效；下面明确标注的算法和阶段顺序修订仍待相应批准。

入口：docs/PROJECT_STATE.md。JSON字符串时间仍是唯一获批文件输入；TSV/CSV不在本轮已批准实施范围。

## 关键更正

- MoonBit Counts字段为 `fn_count`，JSON仍写 `"fn"`；Python `counts["fn"]` 不变。目标编译器已实证旧字段解析失败、新字段及JSON映射通过。
- T0兼容性已实跑，见[结果](reviews/2026-10-20-t0-results.md)。统一使用`moon.mod`/`moon.pkg`、普通`inspect(...)`，不用已被目标版拒绝的`inspect!(...)`。旧JSON清单在目标版仍可运行但有弃用提示，不用于产品/消费者。
- 锁定工具链与运行命令来自`docs/toolchain.lock.json`和`scripts/with-toolchain.sh`；只在项目`.tools`安装，不能用默认版代替。core哈希仅与历史记录一致，不是发布者认证。
- 深度调用实证为`@json.parse(input, max_nesting_depth=16)`；该参数已弃用，需在唯一的小型解析兼容函数上加`#warnings("-deprecated")`，其余包/调用仍执行`--deny-warn`。这是固定版本兼容例外，不允许全局关闭警告。数组/对象16层成功、17层抛`@json.DepthLimitExceeded`，映射RESOURCE_LIMIT；普通语法错误另行映射。
- 严格字节解码使用`@utf8.decode`，不可用lossy版本；目标core直接拒绝孤立代理转义，合法代理对通过。重名及转义等价JSON键均后值覆盖，仍是显式已知限制。
- Native借用声明`#borrow(path, buffer)`/`#borrow(buffer)`及`options("native-stub": ["io_stub.c"])`通过。C stub只同步使用借用指针、不持有/释放它们；用`int32_t`封装有限`ssize_t`返回，不能直接把libc read/write的ssize_t当MoonBit Int。T0只证明短合成文件，完整I/O硬化仍在T5/T6。
- `moon package --list --frozen`与`moon package`均实跑，产物在模块`_build/publish/<module>-<version>.zip`；本地打包不等于包外消费或发布。
- **待批准算法修订：**保留最大基数及同版本确定性，建议在升序DFS前加入first-free搜索；T2立即验证500/1000完全图和穷举。算法身份与遍历策略在T2验收后记录；切换HK须记录决定及重验，不能悄悄替换所选配对。
- **待批准阶段修订：**T1b参考环境三小时排障预算，不挡T1纯核心；T3核心证据满足可先进入demo，但A11原版参考仍是最终完整验收项，超时只能报告未完成。

## 继承的业务约束与标出的待批准调整

- 时间/比例只接受 ASCII 十进制字符串，语法 `^(0|[1-9][0-9]*)(\.[0-9]{1,6})?$`；秒转 Int64 微秒，比例转 ppm，无舍入、epsilon 或 Float64 时间判断。
- 每个事件满足 `0 <= onset < offset <= 2592000` 秒；`collar_s` 范围 0–2592000 秒，默认 `"0.2"`；`offset_ratio` 范围 0–1，默认 `"0.5"`。
- JSON `schema_version=1`；未知字段、缺失/错误类型、未知类别、重复录制 ID、同录制同侧重复事件 ID 为整任务错误；对象重名键后值覆盖；不去重事件。
- 输入 8 MiB，JSON 容器嵌套深度 16；录制/类别 1000/256；两侧合计 2000 事件；每个 ID/类别 256 个 Unicode 码点；匹配工作量 20000000 步；序列化报告 16 MiB，全部含等号。
- 每次邻接边检查、搜索顶点进入及增广配对改写各算一步，操作前扣预算；跨组累计。公开接口不增加预算配置字段。
- 同录制同类别配对，起点 `abs(delta)<=collar`，终点 `abs(delta)*1000000<=max(collar*1000000, reference_duration*ratio_ppm)`；边界含等号，不增加区间相交要求。
- 最大基数一对一匹配，不优化时间误差；Unicode码点排序、显式栈、输入重排结果稳定，改ID不应改TP/FP/FN。v2建议的first-free再DFS次序为本轮待批准调整；原v1固定DFS记录只作历史，不在同一实现中混用。
- `TP=配对数`、`FP=预测数−TP`、`FN=参考数−TP`；全局先累计再微平均；P/R/F1 各自零分母为 null，F1 直接从计数计算。
- 退出码 0=完整评测/解释完成；2=输入、配置、参数或文件错误；3=资源限额导致未完成；4=内部非预期错误。失败不得含分数或部分配对；JSON 失败向 stdout 写结构化错误。
- 输出语义标识 `collar-max-cardinality/v1`，时间为规范十进制秒字符串；有效终点容差可至十二位小数。完成报告不含日期、运行耗时或本机路径。
- sed_eval 固定提交 `0cb1b6d11ceec4fe500cc9b31079c9d8666ed6eb`；保留原始 substitution/global FP/FN，共同口径投影必须显式命名；不宣称原始全局输出完全一致。
- 只使用合成或许可已确认的公开数据；不访问临床数据。保留原 MoonReconcile。新增 UI、格式、评分模式不在本计划内。
- 不创建远端、不发咨询、不修改表单、不推送、不正式发布；这些需用户另行明确授权。历史赛事规则不当作当前已确认条款，不为提交次数机械拆分提交。

## 文件与接口地图


路径均相对本仓库根目录 `/Users/henryz/Desktop/比赛/mooneventeval`。下列产品文件仍由实施阶段创建；清单格式统一在T0验证，不混用未验证格式。

| 路径 | 单一职责 / 创建任务 |
| --- | --- |
| `moon.mod`、`.gitignore`、`README.md` | 本地模块 `local/mooneventeval@0.1.0`、构建忽略、起步说明（T1）；这不是已注册包名，正式发布前再核实 namespace |
| `scripts/install_toolchain.py`、`scripts/with-toolchain.sh`、`docs/toolchain.lock.json` | 项目局部工具链安装、校验、运行和来源锁（T0） |
| `eventeval/moon.pkg`、`model.mbt`、`errors.mbt` | 不可变/封装模型、稳定错误和常量（T1，后续扩展输出模型） |
| `eventeval/time.mbt`、`eligibility.mbt` | 无损十进制转换、码点比较、时间候选依据（T1） |
| `eventeval/matching.mbt` | 有预算的确定性二分图匹配，无时间/JSON 依赖（T2） |
| `eventeval/input.mbt`、`validation.mbt`、`evaluation.mbt`、`report_json.mbt` | schema、复制校验、分组与指标、稳定机器报告（T3） |
| `cmd/probe/moon.pkg`、`main.mbt` | 开发专用、小 JSON 参数探针，调用真实 evaluate_json；不读文件、不发布为产品命令（T3） |
| `eventeval/explain.mbt`、`report_text.mbt`、`serialization.mbt` | 指定事件对解释、人类报告、最终字节预算（T4） |
| `cli/moon.pkg`、`args.mbt`、`dispatch.mbt` | 可测试的参数/调用/退出码决策（T5） |
| `cmd/mooneventeval/moon.pkg`、`main.mbt`、`native_io.mbt`、`io_stub.c` | 只读有界文件与标准流 I/O、进程退出（T5） |
| `examples/duplicate.json`、`greedy-trap.json`、`boundary.json` | 三份完整合成场景（T3），配套解释说明（T5/7） |
| `validation/reference-requirements.in`、`reference-constraints.txt`、`reference.lock`、`bootstrap_reference.py`、`sed_reference.py` | 原版参考环境、原始结果与明确投影（T1b/3/6） |
| `validation/graph_oracle.py`、`rational_oracle.py`、`generate_cases.py`、`compare.py`、`benchmark.py` | 独立穷举、有理数、确定性用例、比较与性能记录（T2/3/6） |
| `validation/tests/test_reference.py`、`test_oracles.py`、`test_comparison.py` | 独立验证器自己的反例与防伪一致检查（T1/2/6） |
| `eventeval/*_wbtest.mbt`、`cli/args_test.mbt`、`tests/cli/test_cli.py` | 对应任务的白盒/接口/真实进程验收 |
| `tests/consumer/moon.mod`、`main/moon.pkg`、`main/main.mbt` | 包外消费者模板（T7），由脚本复制到临时目录运行 |
| `.moonignore`、`LICENSE`、`THIRD_PARTY_NOTICES.md`、`docs/API.md`、`EXAMPLES.md`、`VALIDATION.md` | 包内容、许可、真实可运行说明（T7） |
| `scripts/verify.py`、`scripts/check_consumer.py`、`scripts/package_candidate.py`、`tests/test_verify.py`、`.github/workflows/ci.yml` | 统一检查及故障测试、包外调用、候选归档、授权后可触发的 CI（T7/8） |
| `docs/PROJECT_STATE.md`、`docs/ACCEPTANCE.md`、`evidence/<stage>/` | 当前状态、逐项证据、输入/输出/失败与版本（各任务） |

依赖方向：`cmd -> cli -> eventeval`；Python 验证器只能从外部调用探针/真实二进制，产品不 import Python。eventeval 保持一个包，避免数组/错误/时间类型跨多层分包重复公开；文件各有职责，不能把全部实现堆进 model 或 main。

### 共享类型约定

- `EvalError`：`kind: FailureKind`（Input/Resource/Internal）、`code: String`、`message: String`、`path: String?`、`limit: Int64?`、`observed: Int64?`；`exit_code(error)` 唯一映射 2/3/4。
- 稳定 code 集合：`INVALID_JSON`、`INVALID_UTF8`、`INVALID_UNICODE`、`INVALID_SCHEMA`、`UNKNOWN_FIELD`、`MISSING_FIELD`、`INVALID_TYPE`、`INVALID_DECIMAL`、`OUT_OF_RANGE`、`DUPLICATE_ID`、`UNKNOWN_LABEL`、`ID_NOT_FOUND`、`INVALID_ARGUMENT`、`FILE_ERROR`、`RESOURCE_LIMIT`、`INTERNAL_ERROR`；任何资源种类用RESOURCE_LIMIT，path/limit/observed区分。深度超限不是INVALID_JSON，未知recording/event查询为ID_NOT_FOUND。
- `Event`、`Config`、`Recording`、`Task` 为封装类型；通过下列工厂创建。Task 不暴露内部数组，工厂验证并复制传入数组；新建事件/config 时也检查范围。
- `Counts`：`reference/prediction/tp/fp/fn_count: Int`；`Metrics`：`counts: Counts`、`precision/recall/f1: Double?`。
- `PairBasis`（包内）：`label_match/onset_pass/offset_pass/eligible: Bool`、`onset_delta_us/offset_delta_us/onset_limit_us/offset_limit_scaled: Int64`；scaled 的单位为微秒×1000000。
- `WorkBudget`（包内）：共享可变 `used/limit: Int64`；仅白盒测试可设小 limit。`Matching`（包内）：`pairs: Array[(Int,Int)]`、`reference_degree/prediction_degree: Array[Int]`、`steps: Int64`，索引对应规范排序后的顶点。
- Matching.steps只记录本次调用消耗（退出used减进入used）；全任务work.matching_steps直接取最终共享budget.used，不再次累加各次累计值。
- `Evaluation`、`PairExplanation` 为封装结果；`Evaluation::metrics() -> Metrics`，`Evaluation::pairs() -> Array[(String,String,String,String)]` 返回副本，四元组为录制/类别/参考ID/预测ID。完整数据通过报告函数访问。

### 机器报告字段冻结

T3/T4实现如下形状，不能由不同任务各自命名：顶层 `schema_version=1`、`semantics="collar-max-cardinality/v1"`、`implementation_version="0.1.0"`、`status="completed"`、`config`、`summary`、`by_label`、`by_recording`、`matches`、`false_positives`、`false_negatives`、`work`。config使用输入字段名及规范秒/比例字符串。summary为 `{counts:{reference,prediction,tp,fp,fn},precision,recall,f1}`；类别/录制行分别为 `{label,metrics}` / `{recording_id,metrics}`，metrics同summary形状。

匹配行为 `{recording_id,label,reference,prediction,basis}`，两事件使用输入的id/label/onset_s/offset_s字段及规范时间；basis为 `{label_match,onset_pass,offset_pass,eligible,onset_delta_s,offset_delta_s,onset_limit_s,offset_limit_s}`。未匹配行为 `{recording_id,event,candidate_count,reason}`；work为 `{candidate_checks,eligible_edges,matching_steps}`。explain报告沿用版本/状态/config，并包含recording_id、reference、prediction、basis，不含summary、work或匹配身份推断。

失败形状为 `{schema_version:1,status:"failed",error:{kind,code,message,path,limit,observed}}`；kind为小写input/resource/internal，后三个可为null。输出采用上述固定键序，所有数组按PRD排序；错误不携带完成报告字段。



## 文档入口和证据规则

有效执行入口为docs/superpowers/plans/2026-10-20-mooneventeval-plan-v2.md及tasks/任务文件。旧单文件计划已作废，不能与本契约拼接使用。

结构检查只证明文件结构；T0证明目标工具兼容性；T3证明核心行为；T6证明限定独立对照。命令、退出码、被测SHA、失败样例各自落盘，不能互相替代。

JSON对象重名键仍依PRD后值覆盖，是已知限制；在T0/T3加入明确用例和文档警示。若改为拒绝，先设计能识别转义等价键的词法检查，另行修改契约，不引入天真的split预扫描。
