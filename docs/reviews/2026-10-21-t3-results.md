# T3 严格输入与完整评测实际结果

状态：**T3实现完成；独立评审发现2项Important，均由作者RED→GREEN修复并完成提交后全量复验。没有二次独立复审。**M2本人复算/讲解和最终A11仍未完成，CLI/explain/demo是后续任务。

- 工作树`/Users/henryz/Desktop/比赛/mooneventeval-t0`，分支`spike/t0-feasibility`；基线`9c78a20aaa34514e218afd7ce26cae1e0ce03046`。
- 最初候选/独立评审SHA：e9c7f317bcd141aa34dbcc3e1ee6728415be3824；**最终代码及提交后被测SHA：508d5cf6cc5ef637f0931bbdaae36b1729256b03**。后续只文档/证据提交与运行代码分开记。
- 原main仍`8a3075521312c9bf9ad196309422adaa0c67fbd2`，干净、无remote；没有合并/外发/推送/发布。

## 已实现

公开Recording/Task工厂验证并复制输入数组，Event/Config及结果保持封装；Evaluation.metrics返回不可变计数/指标，pairs返回新数组。严格decode_task按实际8MiB字节、UTF8（仅开头一个BOM）、depth16、schema及typed工厂校验；时间只接受字符串。未知字段按码点排序定位；保留原事件索引错误路径；完整输入有效后才评测。重名及转义等价JSON键后值覆盖是已披露限制，不是拒绝。

录制/类别隔离，规范码点排序，first-free+完整显式栈最大匹配，一份全任务20M预算；候选计数只含同组构图配对检查；未匹配原因来自真实度数。全局计数先累计再算微平均，每个声明类别/录制有汇总，空集各自null。不平均F1，不把错类算substitution。匹配结果只选最大基数，不优化时间误差。

完整report_json固定键序，规范时间字符串，终点容差最高12位小数；最终UTF8字节数检查16MiB，失败不泄漏完成报告。error_json唯一失败结构；真实native argv probe输出JSON并按错误退出2/3/4。probe不是文件CLI，不冒称验证8MiB文件读入/短写/不可读文件。T1/T2暂时unused豁免已移除，其余deny-warn保持；唯一deprecated豁免仍是T0限定解析兼容函数。

## 实际验证

- 最终提交后MoonBit **38/38**（保留T1/T2全部25项，含753图，新增13项输入/评测/JSON控制字符）。原Python **4/4**；validation **29/29**（原15+有理数4+比较器10）。
- fmt/info/check/build通过锁定wrapper执行exit0，probe native release真实构建。新的mbti包含声明的工厂、结果访问与JSON函数，私有状态仍封装。
- 56项真实进程检查：未知/缺字段、非字符串时间/比例、非法十进制、重复标签/录制/同侧事件、语法/深度/代理转义、BOM、重名键，以及参数错误；核对exit/stdout失败形状及无stderr。
- MoonBit白盒另外测试输入8MiB等号/超1、深度16/17、类别256/257、录制1000/1001、全任务事件2000/2001；单个ID上限继承T1验证。输出16MiB有最终字节检查，本轮未制造私有非合法任务充当产品边界压力测试。完整A9资源/I/O验收仍待T4/T6。
- 防御性复制：修改传入事件/录制/类别数组及返回pairs副本后重评不变；码点私用区/BMP外、组合字符和转义输出均有机器测试。跨组5步预算导致整任务失败，正常两组总6步，不能重置或重复累加。
- 四种隔离源码mutation：起点<=改<、终点<=改<、max改min、参考时长改预测时长；control各1/1，变异均编译成功、行为失败各0/1，原文件不改。

## 原版参考与独立oracle

Fraction oracle由Decimal字符串直接构造，在秒域精确计算；图oracle枚举部分注入，与产品微秒/ppm及增广算法分离。比较器检查最大基数、每条基准/边、双侧唯一、所有事件恰出现一次、未配对候选度数/原因、行汇总与全局指标、规范顺序及图工作计数。

固定合成+seed20261021二进制网格共46份任务，全部实际执行probe及独立oracle：43份共同投影/每类原始计数/逐录制参考投影一致，1份有具体binary64见证的边界差异，2份原版0 collar域错误。每例保留input、product、reference-original（可调用域内）、原始raw/class_wise及显式projected、oracle邻接/期望和comparison。全部46例打乱数组后stdout字节一致；重命名事件ID后summary保持。详见evidence/T3/parity-final/report.json。

明确反例：r起点10.1、p起点10.3，精确差0.2；binary64差0.20000000000000107（hex 0x1.99999999999c0p-3），collar为0x1.999999999999ap-3。原版TP0，产品/精确oracle TP1。只有具体候选翻转、独立binary64图给出原版TP、产品精确检查全通过时才分类为数值边界差异；不允许任意“浮点误差”免责。

跨类别反例保留原始Nsubs1/Nfp0/Nfn0和projected FP1/FN1，未改原版算法/依赖，也不把投影说成原始全局输出相同。零collar原版ValueError原样保留，不能记作参考TP0或parity通过。预先声明的2项域限制与1项数值差异外，未解释差异0。这里只是原型范围，不是T6广泛非边界随机资格验证或最终A11。

## 失败与修复证据

初始RED确因目标API缺失；首次编译遇空Map字面量/旧Result.is_ok等目标版告警，按诊断改为Map([])/模式匹配，不扩大warning豁免。真实包外probe构建发现EvalError只读类型不能构造，改为pub(all)且字段保持不可变。56项进程检查发现空labels与事件同时存在时先报UNKNOWN_LABEL；补回归RED→GREEN，在读录制前完成labels工厂语义验证。比较器曾把False/0.0等同整数0，新增测试RED→GREEN，显式校验产品/投影计数整数。所有失败原日志保留，不当作PASS。

## 决定和未完成项

1. 用户继续授权当前T3；T1b成功故实际跑参考，不使用仍未批准的超时后demo降级。八例为agent推导，个人理解/M2不能自动通过；误用会虚报里程碑。
2. 增加error_json为失败序列化唯一接口；schema内部可抛私有DecodeFailure，但公开边界转换为Result。若遗漏捕获会使普通输入异常退出，已覆盖正常坏输入。
3. EvalError改pub(all)允许适配层创建参数/文件错误，仍不可变，不暴露Event/Task私有状态；代价是公开错误构造面，未增加产品输入配置。

[八组复算材料](../validation/T3-worked-examples.md)已可编辑/可运行，但本人纸笔与讲解仍需要实际证据。T4同源explain/text报告、T5文件CLI/demo、T6完整资格/A11、T7消费者/包、T8 CI均未完成；不将本机结果冒充远端。独立评审及作者裁定见[评审记录](2026-10-21-t3-review.md)，所有最终命令、输入输出和SHA见[evidence manifest](../../evidence/T3/manifest.json)。

## 独立评审两项修复

原候选的37项绿灯没有覆盖全部合法Unicode转义。独立评审真实执行32控制字符发现28个成功JSON不能解析，控制字符未知键的错误路径也非法：String.escape是MoonBit语法，不是JSON编码。新回归先出现真实ParseError/JSONDecodeError，再将所有报告/错误字符串统一经Json::string(...).stringify()；最终64项独立Python解析的成功/失败往返覆盖U+0000..001F、ID/标签/录制/匹配/FP/FN/错误path，全部通过。错误message/code/path的全控制字符在MoonBit测试中还分别往返检查。

比较器原先会纠正被测时间且使用Python宽松相等，使数字型时间、布尔schema_version、work bool/float及嵌套额外键漏检。四组新回归先4项失败；修复为先验证完整实际输出类型、规范十进制、嵌套精确键/顺序，再做独立数值比较，绝不规范化实际事件时间。最终比较器10/10、全validation29/29。作者重放原评审脚本，7项协议篡改全部被拒绝；额外空图matching_steps=1仍可通过该独立比较器，因为它仅校验搜索步类型/范围，精确消费由产品白盒/共享预算测试验证，不复制matcher算法作为oracle。

评审原结论为e9c7f31不可验收（Critical0/Important2/Minor0），原报告和107份收据原样保存。两修复同一作者修复轮次完成，实际被测508d5cf；不把作者复跑说成第二次独立评审或评审者批准修复。
