# Sources and third-party notices

MoonEventEval's own source and documentation use the [MIT license](LICENSE).
Copyright attribution uses the repository's existing author name, Hengrui Zhang.
The three JSON examples are synthetic fixtures created for this project; they
contain no recordings, downloaded benchmark data or clinical data.

The product imports `moonbitlang/core` from the pinned local MoonBit toolchain
`0.10.14+7d59c7ec9`. Its local module manifest declares Apache-2.0. The unchanged
[core license](LICENSES/moonbit-core-LICENSE) and
[core notices](LICENSES/moonbit-core-NOTICE) are preserved, including upstream
notices for adapted algorithms. Core sources, compiler binaries and runtime
archives are not bundled in this source candidate. Native builds may link
MoonBit runtime/core components; these notices do not relicense those components
as MIT. Toolchain downloads retain their upstream terms.

The native I/O adapter is project code using platform C/POSIX interfaces. No
third-party C implementation is copied into the candidate.

Original `sed_eval` commit `0cb1b6d11ceec4fe500cc9b31079c9d8666ed6eb`
(MIT) is used only in the separate development reference environment. Its
algorithm/source and its Python dependencies are not included in this candidate
or imported by the product. See [validation scope](VALIDATION.md). No claim is
made that the product uses its raw global metric definitions unchanged.

## sed_eval reference scope

参考对象固定为 [sed_eval 提交 0cb1b6d](https://github.com/TUT-ARG/sed_eval/tree/0cb1b6d11ceec4fe500cc9b31079c9d8666ed6eb)，MIT；不是随上游 main 变化的模糊“参考”。源码与参考环境的锁在仓库 `validation/reference-sources.json`、`validation/reference.lock` 中；原版对照执行前校验源码及所用字节码。它们是开发验证材料，不是产品依赖。

### 参考了哪些规则

- `sound_event.EventBasedMetrics` 同时启用 onset/offset 判定，固定 `event_matching_type='optimal'`。
- 起点差的绝对值不超过 collar；终点差不超过 `max(collar, reference_duration * percentage_of_length)`，采用含等号比较。
- 同类别候选的图匹配最大化一对一配对数。上游本来就支持 optimal，不能把“优于顺序贪心”宣传成优于 sed_eval optimal。

这是方法/规则参考与独立运行对照。MoonBit 的整数时间、模型、构图、显式栈匹配、序列化、解释和 native I/O 是本仓库实现；没有逐文件移植上游 Python 模块，没有将其 Python 算法或依赖嵌入产品，也不声称发明了这些通用评测规则。

### 哪些地方相同，哪些不兼容

| 项目 | 锁定 sed_eval | MoonEventEval |
|---|---|---|
| 输入 | 参考/预测事件列表，时间转为 Python float；支持其容器接口 | 自定义 UTF-8 JSON 或 MoonBit API；秒为最多六位小数字符串 |
| 共同评测子集 | 启用起止点 collar 的 EventBasedMetrics optimal | 同录制、同类候选；上述 collar 规则与最大基数匹配 |
| 时间计算 | binary64；十进制边界可能受表示影响 | 整数微秒和整数比例；不加 epsilon，不对超精度输入取整 |
| 错类别 | 原版 overall 可记 substitution，并从 raw Nfp/Nfn 扣除 | 不跨类配对；未匹配预测记 FP，未匹配参考记 FN，不输出 substitution/ER |
| 共同口径对照 | 开发适配器保留 raw；另从 class-wise TP 和总事件数投影共同 FP/FN | 使用 TP=匹配数、FP=预测数-TP、FN=参考数-TP |
| 空分母 | 原始 Python 指标可能是 NaN；开发适配器另作 JSON 安全标记 | 指标为 null，不暗中换成 0 |
| 产品交付 | 声音事件评测工具集，含事件级、分段级及其他指标接口 | 有界事件级 CLI/库，报告具体事件配对、未匹配事件和候选资格解释 |
| 本项目不提供 | — | 分段网格评测、IoU/mAP、substitution/插入/删除错误率、音视频识别、TSV/CSV 直接读取 |

“共有口径一致”只指适配器明确投影的计数和双方都有定义的指标；不是 raw 字段相等，也不是完整功能兼容。多解时两个实现可选中不同的合法最大匹配，不要求事件对身份完全相同。

### 可复查的区别

- 重复预测：双方均得到 TP=1、FP=1、FN=0（此例无 substitution）。
- 增广路径例：双方 optimal 都得到 TP=2；不是超过上游的例子。
- 一条 alarm 参考与一条同时间 door 预测：原版 raw 为 Ntp=0、Nsubs=1、Nfp=0、Nfn=0；MoonEventEval 为 TP=0、FP=1、FN=1。原版共同口径投影也是 0/1/1。不能直接比较两个 raw FP/FN。
- 参考起点 10.1、预测起点 10.3、collar=0.2：精确十进制差等于容差；本产品 TP=1。锁定原版 binary64 的差值略大于 0.2，示例 TP=0。这是明确的数值语义差异，不把它计作一致。

完整输入、双方原始结果和重跑命令位于仓库 [demo](https://github.com/z2823253773-p/mooneventeval/tree/main/demo)。这里的四个例子是合成的规则演示，不代表真实数据兼容性认证；更广的有限验证范围见 [VALIDATION](VALIDATION.md)。

上游依据：[EventBasedMetrics 参数与 optimal 说明](https://github.com/TUT-ARG/sed_eval/blob/0cb1b6d11ceec4fe500cc9b31079c9d8666ed6eb/sed_eval/sound_event.py#L1108-L1146)、[raw substitution 和 FP/FN 计数](https://github.com/TUT-ARG/sed_eval/blob/0cb1b6d11ceec4fe500cc9b31079c9d8666ed6eb/sed_eval/sound_event.py#L1348-L1465)、[逐类计数](https://github.com/TUT-ARG/sed_eval/blob/0cb1b6d11ceec4fe500cc9b31079c9d8666ed6eb/sed_eval/sound_event.py#L1468-L1595)、[起止点判定函数](https://github.com/TUT-ARG/sed_eval/blob/0cb1b6d11ceec4fe500cc9b31079c9d8666ed6eb/sed_eval/sound_event.py#L1603-L1668)。
