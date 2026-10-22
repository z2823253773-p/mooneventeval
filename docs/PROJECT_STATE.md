# MoonEventEval 当前状态

更新：2026-10-22（America/Phoenix）。**T0至T6限定本地机器实现/验收完成；T6唯一独立评审的2项Important已作者单轮修复并复验，1项Minor延期，无第二次独立复审。下一步T7包外消费者/候选包。本人M2/口头讲解、T7/T8、发布与赛事资格未完成。**

## 当前入口和SHA

- [契约](contracts.md) → [有效计划v2](superpowers/plans/2026-10-20-mooneventeval-plan-v2.md) → [T6结果](reviews/2026-10-22-t6-results.md) / [评审处置](reviews/2026-10-22-t6-review.md) → [验收地图](ACCEPTANCE.md) → [T7任务卡](superpowers/plans/tasks/T7-package.md)。旧v1作废；个人部分仍见[T5卡](superpowers/plans/tasks/T5-cli-demo.md)和[demo讲稿](demo.md)。
- Codex主实施；工作树`/Users/henryz/Desktop/比赛/mooneventeval-t0`，分支`spike/t0-feasibility`。原main基线8a3075521312c9bf9ad196309422adaa0c67fbd2；沿用局部工具链及参考venv，不重装、不改main/remote。
- T6基线b8cf27d02fa34a007185e15c23ea19bd0e412b4a；评审候选fb4de0bbb28f0bed48d0529db6ebc946027a2a81；**最终代码/被测7b8a453f58307e4118eeae7ad78d79859af6eeed**。后续收尾提交仅文档/证据，实际HEAD用git log查询，不冒称又一代码复测。
- 生产binary：`_build/native/release/build/cmd/mooneventeval/mooneventeval.exe`，SHA256 `7a65bacefef1c3b70d4b851dc4fae1b337ce9114eea4addefddcf3be92f1940d`。T6未改数学/CLI/native运行源码，只加白盒边界测试及开发验证器。
- [T6 manifest](../evidence/T6/manifest.json) / [源码绑定](../evidence/T6/final-source.json)。最终parity-verified、performance-verified、cli-verified；faults/mutations复用*-committed，其产品源码与最终一致。历史候选/RED目录不混作最终通过证据。原始独立评审8363档案单独hash冻结。

## 已完成与限制

- T0锁定工具链；T1精确十进制/Unicode/资格；T1b原版参考hash锁；T2显式栈first-free+DFS/753小图；T3封装Task/解码/评测；T4同源解释/JSON/text/最终16MiB字节门；T5真实文件CLI与自动demo。各阶段历史SHA/manifest继续保留，不拿旧hash检验新文档。
- T6 seed20261020新128网格+160十进制候选，加46旧例，共334。Fraction预排除10个<=1us不安全十进制任务，保留输入/理由；324接受：155网格、160安全十进制、9边界。315共有口径一致；边界6一致/1具体binary64差异/2原版零collar限制，未解释0。
- 每base四变形（乱序bytes相同、平移、复制、无候选预测），共1620真实文件产品调用；每base原版全局/逐录制/类别及双方定义指标实跑，变形由独立Fraction/部分注入oracle验证，不声称1620次原版对照。
- 最终Moon58/58、原Python4/4、validation41/41、CLI15/15；release等构建退出0。评审候选独立重跑的是37 validation；修复后41及原样5反例重放是作者复验，不是第二次独立评审。
- 真实资源等号/超1（录制/类别/事件/码点/30天/depth/8MiB）、内部实际20M门、T4实际16MiB门通过；CLI带LF恰好16MiB落点未造。2000事件三图族各3次：最终最慢0.0493秒，峰值8,994,816字节，仅Darwin arm64/Apple M5本机样本，不保证全部合法图。
- 9类实际源码临时编译故障注入通过，含Unicode短读写/EINTR/失败/一次close及signal初始化。6可编译错误mutation杀死、1等价、0invalid/survived，恢复hash与GREEN；生产源码未变。有限覆盖，不认证所有OS/FS/竞态。
- I1性能门原来会接纳不合格配对，现要求真实输入成员/完整一对一覆盖与独立eligible=true。I2输出门原来吞换行/重名键或非有限数崩账本，现严格bytes/JSON/Unicode并保留失败账本。
- **Minor M1延期：超时正确非零失败，但部分stdout/stderr及process收据未保存。** 当前成功样本未触发超时；不能声称全部异常取证完备。

## 固定决定与未完成

- 仅UTF8 JSON、字符串时间；输入重名/转义等价键后值覆盖仍披露。TSV/CSV、数字时间/stdin/新评分未获范围修订，仍在BACKLOG。
- 机器输出严格单LF；普通文件/输出I/O错误2、资源3、内部异常4。close尝试一次，SIGPIPE忽略/EPIPE非零；前缀可能已输出，不能当完成结果。
- [八例推导](validation/T3-worked-examples.md)与demo稿是agent材料，**不是本人纸笔/讲解**。T5步骤7本人部分/M2仍未勾选。自动日志不能替代本人条件。
- T7需实际包外API消费、归档解包后再消费、README示例/许可/本地候选；T8需CI/交接。正式作者/namespace/仓库URL未确认时不得编造。远端创建、外发、合并、推送、报名变更、发布仍需明确授权；本轮无上述操作，无临床数据访问。赛事当前资格/换题/截止未核实。

## 复验和继续

先核实际git状态，再读AGENTS/contracts/T7卡。快速核冻结证据：

```sh
python3 evidence/T6/freeze.py
scripts/with-toolchain.sh moon test --target native --deny-warn
.venv-reference/bin/python -W error::ResourceWarning -m unittest discover -s validation/tests -v
```

重新生成对照用全新未冻结目录，例如evidence/local-recheck-t6；不要向冻结T6新增日志。产品构建命令：`scripts/with-toolchain.sh moon build cmd/mooneventeval --target native --release --deny-warn`。T7第一步是独立临时模块仅import公开eventeval API，运行A1断言；不是发布或重做T6。
