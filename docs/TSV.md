# 四列 TSV 导入

在仓库根目录构建native CLI后执行：

```sh
_build/native/release/build/cmd/mooneventeval/mooneventeval.exe import-tsv examples/tsv-reference.tsv --prediction examples/tsv-prediction.tsv > task.json
_build/native/release/build/cmd/mooneventeval/mooneventeval.exe evaluate task.json --format json
_build/native/release/build/cmd/mooneventeval/mooneventeval.exe explain-pair task.json --recording clip.wav --reference r2 --prediction p3 --format json
```

示例是本项目合成数据，预期TP=1、FP=1、FN=0。第二个预测仍是合格候选；解释不等于选中。输入文件只读，输出写stdout。导入默认JSON，可写`--format json`；`--format text`拒绝，非法/重复format沿用文本诊断规则。导入失败只有结构化错误，不含部分任务或评分。

每份文件都必须有精确表头：`filename`、`onset`、`offset`、`event_label`，用TAB分隔，列顺序/大小写固定。每个数据行恰好四列。支持严格UTF-8、单个初始BOM、LF/CRLF以及无末尾换行；拒绝空行、裸CR、额外或缺少列。引号是字段内容，不按CSV解码，不trim空格。

- filename作为录制ID，event_label作为类别，均按原字符串保留，不读取所指媒体文件。
- 时间沿用ASCII十进制秒字符串，最多六位小数；科学记数法、额外精度、前后空格明确拒绝，不经过Float64或舍入。输出可规范化`1.000000`为`1`，数值无损。
- 参考ID为r加物理行号，预测为p加物理行号，表头为1，因此首事件为r2/p2。相同行保留为独立事件；重排原行会改变事件ID和多解时的选择，原行号用于回查。
- 类别和录制取两文件并集，保留只有参考或预测的一侧；两文件均仅表头时无法推断类别，返回INVALID_SCHEMA。
- 默认config为collar_s="0.2"、offset_ratio="0.5"；需要其他配置可修改生成任务的config，再evaluate。
- 两份原始输入合计<=8 MiB，合计<=2000事件、1000录制、256类别；ID/类别<=256 Unicode码点，时间<=30天。生成JSON连同CLI末尾LF<=8 MiB，可直接作为evaluate文件输入。
- 文件读取错误先由native I/O返回；库先检查合计字节数，再按参考、预测顺序解析。格式错误INVALID_TSV；时间、范围、Unicode、资源错误保留既有code。path例如prediction[2].onset，对应预测文件第2行onset列；输入exit2、资源exit3。

此适配只支持本文四列子集。[DCASE强标注说明](https://dcase.community/challenge2024/task-sound-event-detection-with-heterogeneous-training-dataset-and-potentially-missing-labels)描述了同类四列结构，但其弱标签、软标签、无表头预测文件和完整评测协议不在此兼容声明内。没有导入第三方代码或数据。

MoonBit调用：`import_tsv(reference_bytes, prediction_bytes)`返回`Result[String, EvalError]`，成功字符串不带末尾LF；可交给`decode_task`、`evaluate`。库也为CLI末尾LF预留容量。所有评分仍由现有核心完成。
