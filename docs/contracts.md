# MoonEventEval 共享契约

版本：评审修订 v2，T0已获用户授权并完成，独立评审问题修复后主验收PASS。当前无产品消费者。已批准PRD的数学/资源/数据边界继续有效；T2 first-free修订已随用户“下一步”获得本阶段执行授权；仍明确标注的阶段顺序修订待相应批准。

入口：docs/PROJECT_STATE.md。JSON字符串时间仍是唯一获批文件输入；TSV/CSV不在本轮已批准实施范围。

## 关键更正

- MoonBit Counts字段为 `fn_count`，JSON仍写 `"fn"`；Python `counts["fn"]` 不变。目标编译器已实证旧字段解析失败、新字段及JSON映射通过。
- T0兼容性已实跑，见[结果](reviews/2026-10-20-t0-results.md)。统一使用`moon.mod`/`moon.pkg`、普通`inspect(...)`，不用已被目标版拒绝的`inspect!(...)`。旧JSON清单在目标版仍可运行但有弃用提示，不用于产品/消费者。
- 锁定工具链与运行命令来自`docs/toolchain.lock.json`和`scripts/with-toolchain.sh`；只在项目`.tools`安装，不能用默认版代替。core哈希仅与历史记录一致，不是发布者认证。
- 深度调用实证为`@json.parse(input, max_nesting_depth=16)`；该参数已弃用，需在唯一的小型解析兼容函数上加`#warnings("-deprecated")`，其余包/调用仍执行`--deny-warn`。这是固定版本兼容例外，不允许全局关闭警告。数组/对象16层成功、17层抛`@json.DepthLimitExceeded`，映射RESOURCE_LIMIT；普通语法错误另行映射。
- 严格字节解码使用`@utf8.decode`，不可用lossy版本；目标core直接拒绝孤立代理转义，合法代理对通过。重名及转义等价JSON键均后值覆盖，仍是显式已知限制。
- Native借用声明`#borrow(path, buffer)`/`#borrow(buffer)`及`options("native-stub": ["io_stub.c"])`通过。C stub只同步使用借用指针、不持有/释放它们；用`int32_t`封装有限`ssize_t`返回，不能直接把libc read/write的ssize_t当MoonBit Int。T0只证明短合成文件，完整I/O硬化仍在T5/T6。
- `moon package --list --frozen`与`moon package`均实跑，产物在模块`_build/publish/<module>-<version>.zip`；本地打包不等于包外消费或发布。
- **T2本阶段实施策略：**保留最大基数及同版本确定性，在升序DFS前加入first-free搜索；用户“下一步”授权执行当前T2卡。T2立即验证500/1000完全图和穷举；切换HK须另记决定及重验，不能悄悄替换所选配对。
- **阶段状态：**T1b三小时独立排障任务已获本轮授权并完成；**仍待批准**的是T3核心证据满足后先进入demo的门槛调整。A11原版参考仍是最终完整验收项，T1b自检不能将其记为通过。

## 继承的业务约束与标出的待批准调整

- 时间/比例只接受 ASCII 十进制字符串，语法 `^(0|[1-9][0-9]*)(\.[0-9]{1,6})?$`；秒转 Int64 微秒，比例转 ppm，无舍入、epsilon 或 Float64 时间判断。
- 每个事件满足 `0 <= onset < offset <= 2592000` 秒；`collar_s` 范围 0–2592000 秒，默认 `"0.2"`；`offset_ratio` 范围 0–1，默认 `"0.5"`。
- JSON `schema_version=1`；未知字段、缺失/错误类型、未知类别、重复录制 ID、同录制同侧重复事件 ID 为整任务错误；对象重名键后值覆盖；不去重事件。
- 输入 8 MiB，JSON 容器嵌套深度 16；录制/类别 1000/256；两侧合计 2000 事件；每个 ID/类别 256 个 Unicode 码点；匹配工作量 20000000 步；序列化报告 16 MiB，全部含等号。
- 每次搜索邻接边检查、搜索顶点进入及增广配对改写各算一步，操作前扣预算；跨组累计。邻接表已由调用方构建；一次O(E)度数统计不属于搜索步，受2000事件的图规模上界约束。单边图为进入root、检查边、配对改写共3步。公开接口不增加预算配置字段。
- 同录制同类别配对，起点 `abs(delta)<=collar`，终点 `abs(delta)*1000000<=max(collar*1000000, reference_duration*ratio_ppm)`；边界含等号，不增加区间相交要求。
- 最大基数一对一匹配，不优化时间误差；Unicode码点排序、显式栈、输入重排结果稳定，改ID不应改TP/FP/FN。T2采用first-free再DFS次序；原v1纯DFS记录只作历史，不在同一实现中混用。
- `TP=配对数`、`FP=预测数−TP`、`FN=参考数−TP`；全局先累计再微平均；P/R/F1 各自零分母为 null，F1 直接从计数计算。
- 退出码 0=完整评测/解释完成；2=输入、配置、参数或文件错误；3=资源限额导致未完成；4=内部非预期错误。失败不得含分数或部分配对；JSON 失败向 stdout 写结构化错误。
- 输出语义标识 `collar-max-cardinality/v1`，时间为规范十进制秒字符串；有效终点容差可至十二位小数。完成报告不含日期、运行耗时或本机路径。
- sed_eval 固定提交 `0cb1b6d11ceec4fe500cc9b31079c9d8666ed6eb`；保留原始 substitution/global FP/FN，共同口径投影必须显式命名；不宣称原始全局输出完全一致。
- T1b参考环境已实跑：macOS arm64、uv0.11.14、CPython3.11.14；45个依赖版本/哈希在`validation/reference.lock`，构建后端先按`reference-build.lock`装入，后续sync用`--require-hashes --no-build-isolation`，不隐式使用未锁构建依赖。原版12个.py的哈希按`reference-sources.json`在每次评测导入前核验。
- 开发接口`validation.sed_reference.evaluate_document(document)`只消费已验证的合成PRD文档，不代替产品schema校验；秒字符串显式转参考Float64，optimal参数固定为原版实现。结果四区为`raw:{counts,metrics}`（原始overall/overall metrics）、`class_wise:{label:{counts,metrics}}`、`projected:{counts:{reference,prediction,tp,fp,fn},precision,recall,f1}`、`metric_definition_flags`。projected TP来自原版class_wise TP之和，FP/FN重新按共同口径推导，不覆盖raw substitution/FP/FN。
- 参考非有限浮点保留为`{"nonfinite":"NaN"}`、`+Infinity`或`-Infinity`对应标记，原始0仍为0；projected零分母为null。flags包含raw/projected的precision/recall/f1是否有定义、binary64时间、original_sed_eval_optimal和`zero_collar_supported=false`。
- 实证参考域限制：原版构造函数拒绝collar=0，适配器保留ValueError，不用epsilon或改原版；产品0 collar仍有效，由有理数oracle验证。T3/T6必须将这一限制显式分类，不能记作一致/产品错误，也不能据此取消A11。T1b自检不等于产品parity或M2完成。
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
- T1实证补充：两个delta始终是有符号`prediction-reference`，通过与否才比较绝对值；录制相同由调用方分组保证，eligibility只负责类别/时间，不把事件ID当配对条件。
- T1工厂：Event/Config字段均`priv`；ID/label先按UTF-16 code units验证代理配对，非法Unicode报INVALID_UNICODE，不能只依赖JSON入口（目标core的安全substring可拆开代理对）。空ID/label报INVALID_SCHEMA，时间/比例语法报INVALID_DECIMAL，时间/比例范围及onset>=offset报OUT_OF_RANGE；码点超限报RESOURCE_LIMIT，observed记录首先观察到的257。字段path为工厂参数名，T3再加任务索引前缀。
- T1阶段局部例外：Event/PairBasis声明仅屏蔽unused_field，eligibility/compare_codepoints仅屏蔽unused_value，因为正式消费者尚在T3/T4；类型及函数保持包内/封装，不为清警告扩展公开API。T3接入正式消费者时移除这些临时注解；其余检查继续deny-warn。这不扩大T0的deprecated兼容豁免。
- `WorkBudget`（包内）：共享可变 `used/limit: Int64`；仅白盒测试可设小 limit。`Matching`（包内）：`pairs: Array[(Int,Int)]`、`reference_degree/prediction_degree: Array[Int]`、`steps: Int64`、`adjacency_checks: Int64`，索引对应规范排序后的顶点。后者仅为本次搜索邻接检查数，不混作T3候选资格检查数。
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

### T2确定性遍历细则（2026-10-21）

输入前置条件：规范排序的参考/预测索引，邻接行严格升序、无重复且索引在预测范围内；T3构图负责保证。root按参考索引升序，每个root进入计1步；先升序扫描该行，找到空闲预测就计1步改写配对并结束此root。没有空闲预测才清空本root访问标记，显式栈从root按邻接升序DFS；root不重复计进入步，每个新进入的占用者参考计1步。每次取出邻接边（含已访问预测）计1步，重复预测跳过；未访问的占用预测引向其参考，空闲预测触发从栈顶向root逆写路径，每条新配对计1步（两个方向数组维护算同一逻辑配对）。失败分支回退继续升序，不可撤销地停在贪心结果是错误。结果pairs按参考索引升序。预算不足时操作不执行，used保持已消费值，observed=used+1；整次只返回RESOURCE_LIMIT，不返回Matching。

这些内部函数尚无T3产品调用，T2可在maximum_matching/Matching/WorkBudget上局部豁免unused_value/unused_field/struct_never_constructed，T3接入后移除；不扩大公开API。

T2验收后固定策略标识：`first-free-iterative-dfs/v1`（开发记录，不增加报告字段）；源码提交e96d130，753图/四类native样例/两项mutation及独立评审通过，见docs/reviews/2026-10-21-t2-results.md。它不承诺全部合法图在预算内完成；输入排序/构图接入仍须T3端到端测试。

### T3接入约定（执行中）

用户“继续”授权当前T3；原版环境成功，本轮实际运行参考，不触发未批准的超时后demo门槛。`error_json(error: EvalError) -> String`作为唯一公开失败序列化函数供开发probe/后续CLI用；`evaluate_json`仍返回Result[String,EvalError]。JSON前允许一个UTF-8 BOM；schema_version比较JSON数值1（1.0/1e0同值可接受），时间数值仍拒绝。对象字段按schema声明顺序校验，未知键按Unicode码点排序决定首个错误；typed工厂也验证并复制数组，先完成输入校验才构图。八例推导由agent编写，不冒充用户本人复算，个人讲解验收仍需实际证据。

T3真实包外probe暴露EvalError原pub struct不可构造；改为pub(all)，保持字段不可变，适配层可创建参数/文件错误。Event/Config/Recording/Task/Evaluation仍封装。
