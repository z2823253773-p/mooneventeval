# 薄 TSV 导入实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 两份四列事件TSV直接生成可评测的任务JSON，保留精确时间与原始行追溯；用户已授权继续此增量。

**Architecture:** MoonBit公开import_tsv(Bytes, Bytes)返回任务JSON；CLI新增import-tsv REFERENCE --prediction PREDICTION。复用现有工厂、排序、序列化、错误与native有界只读I/O；后续evaluate/explain-pair处理该JSON，不新增评分规则。

**Tech Stack:** 锁定MoonBit/native；现有Python进程测试与打包/CI。

**Spec:** [共享契约](../../contracts.md) P7输入适配v4；[TSV说明](../../TSV.md)。

## Global Constraints

- 表头必须为filename、onset、offset、event_label四列，TAB分隔，大小写/顺序精确；UTF-8，可选初始BOM，LF/CRLF，可无末尾LF。拒绝空行、裸CR、额外/缺少列；不做CSV引号解码或trim。
- 两文件原始字节合计<=8 MiB；两侧合计<=2000事件、<=1000录制、<=256类别，沿用时间/标识符限制。
- 时间文本进入既有精确工厂，不经Float64；拒绝科学记数法与超六位小数，不舍入。
- 录制ID=filename；ID=r{物理行号}/p{物理行号}，首数据行编号2；相同行也保留。标签/录制取两侧并集；双侧无事件明确报错。
- 默认config=0.2/0.5；成功输出可被decode_task直接读取的schema1 JSON，含CLI末尾LF<=8 MiB。库返回不带LF；文件只读、失败无部分JSON。
- CLI导入默认JSON，可显式--format json；--format text拒绝，非法/重复format仍遵循旧文本诊断规则。旧两命令默认与参数不变。
- 新INVALID_TSV用于格式，工厂错误保留code并映射到reference[line].column或prediction[line].column；资源exit3，输入exit2。
- 数学/正常JSON报告及未发布0.1.0候选身份不变。最小包新增解析文件、说明与两合成TSV，38→42成员，旧冻结包不改写。

## Review Focus

- 预测侧文件实际读到、不同格式/原CLI未回归；两文件错误与大小预算明确。
- 行号/两侧/列名能回查，CRLF/BOM不会污染字段；空行不可静默丢弃。
- 重复行保留，不把同名文件标签去重成事件；两侧并集保留单侧录制。
- 时间无损、极值与输入/导出JSON资源边界；可运行导出→evaluate→explain。
- 本次支持四列子集，不宣称DCASE完整协议/预测格式兼容，不引入媒体数据或第三方源码。

### Task 1: TSV 到任务JSON完整流程

**Files:** eventeval/tsv.mbt、tsv_wbtest.mbt、pkg.generated.mbti；cli/{args,dispatch,args_test,pkg.generated.mbti}.mbt；cmd/mooneventeval/main.mbt；tests/cli/test_tsv.py；examples/tsv-*.tsv；docs/TSV.md；.moonignore；scripts/package_candidate.py及check_examples.py；README/API/CHANGELOG/状态与契约。

**Interfaces:** import_tsv(reference:Bytes,prediction:Bytes)->Result[String,EvalError]；Operation新增ImportTsv；run增加可选prediction输入结果，原调用仍有效。

- [ ] 写实际CLI导入/评测/错误测试，旧程序RED。
- [ ] 写工厂、边界与行追溯测试；实现MoonBit转换与CLI，定向GREEN。
- [ ] 将导入流程纳入打包解包与使用示例检查，更新契约/文档/演示来源。
- [ ] 独立评审，处理实质发现；完整17步与旧13+4回放，本地与双平台CI。
- [ ] 提交真实历史，归档证据、校验公开源码与产物，更新状态。旧阶段冻结证据不变。
