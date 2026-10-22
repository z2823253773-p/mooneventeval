# MoonEventEval 当前状态

更新：2026-10-22（America/Phoenix）。**T0至T4机器实现完成；T5本机文件CLI和自动demo已实现、评审问题作者单轮修复并复验通过，无第二次独立复审。T5步骤7的本人推导/口头讲解尚未完成。下一机器任务T6独立对照与硬化；个人M2、最终A11、消费者/CI/发布仍未完成。**

## 当前入口和SHA

- [contracts](contracts.md) → [有效计划v2](superpowers/plans/2026-10-20-mooneventeval-plan-v2.md) → [T5实际结果](reviews/2026-10-22-t5-results.md) / [评审修复](reviews/2026-10-22-t5-review.md) → [T6任务卡](superpowers/plans/tasks/T6-qualification.md)。个人部分参见[T5卡](superpowers/plans/tasks/T5-cli-demo.md)和[demo讲稿](demo.md)。旧单文件v1作废。
- Codex主实施；工作树`/Users/henryz/Desktop/比赛/mooneventeval-t0`，分支`spike/t0-feasibility`。原main仍8a3075521312c9bf9ad196309422adaa0c67fbd2；沿用现有局部工具链/参考venv，不重装、不改main或remote。
- T5基线41890b84505e790efef6c2f981512af04539a51e；初始实现/评审1831fbc21199974b77c4a66675307d0071f88bb0；**最终代码/被测2c0a06d7131eef059e91fcf91b9f68379a013411**。其后收尾仅文档/证据提交，见git log。
- 真实binary：`_build/native/release/build/cmd/mooneventeval/mooneventeval.exe`，SHA256 `7a65bacefef1c3b70d4b851dc4fae1b337ce9114eea4addefddcf3be92f1940d`。[T5 manifest](../evidence/T5/manifest.json)冻结源码、binaryhash、原始bytes、命令、评审、修复与文档快照；`python3 evidence/T5/freeze.py`复验。
- 最终证据目录process-final-verified、cli-bytes-final-verified、native-fd-final-verified、demo-final-verified、review-replay-fixed；candidate/committed/RED均只作历史，不混算最终提交。既有T0–T4证据绑定当时SHA，当前活动文档以新快照为准。

## 已完成与证据边界

- T0固定工具链/清单/JSON/native短I/O/本地包探针；T1精确十进制/Unicode/资格；T1b原版参考hash锁环境；T2显式栈first-free+DFS、753图/密集/长链与mutation；T3封装Task、完整decode/evaluate/JSON/error，T4同源解释/文本/16MiB最终UTF8限额。结果/manifest及历次评审修复均保留。
- T3原型46任务：43共同投影一致，1具体binary64边界差异（10.3−10.1>0.2：原版TP0、精确产品TP1），2原版拒绝0 collar而独立Fraction通过。四资格mutation为编译后行为杀死。不是最终A11。
- T4精确16MiB等号/+1、中文/NUL字节检查；合法2000事件容量JSON4,015,857/text11,023,901字节、TP1000/steps3000；430 renderer检查。旧text=True验证器问题已修复，不能把旧normalized文件称原始byte证据。
- T5新cli包parse_args/run/render_arg_failure，新native入口只做I/O/退出；eventeval数学核心与开发probe从T5基线至最终diff为空。正式文件CLI与旧argv probe明确分开。
- T5最终Moon **57/57**、原Python **4/4**、validation **29/29**，锁定fmt/info/check/build/release build退出0。最终提交后再跑Moon57。CLI **10/10**真实进程测试、45正常调用档案及立即/部分断管2场景；46历史JSON原始stdout逐字节相同；demo10次真实成功命令。
- 文件8MiB等号成功/+1退出3，depth17退出3；schema/UTF8/参数/未知ID/文件错误退出2；TP0/不合格解释仍0。普通Unicode符号链接成功，缺文件/目录/FIFO/设备/不可读文件拒绝。NUL路径为原生函数白盒实测（exec argv不能含NUL）。
- 65536字节读写块、总读入最多8MiB+1、只读非阻塞open/fstat普通文件；20000读在64FD实际native白盒及协议通过。>64KiB Unicode完整输出，立即/写出1024字节后断管均exit2；前缀不可撤回，不能当完成结果。EINTR/短写/close注入尚未全部实测。
- 唯一fresh评审候选实际复跑56Moon/4Python/29validation/9CLI/46bytes/64FD/demo10，另42参数场景38通过、4揭示I1。I1为未知选项value吞掉真正format；作者单元及进程RED→GREEN，最终57/10全套通过，原样42场景重放全过；该重放不是第二次独立评审。

## 固定决定与仍未完成

- 只接UTF8 JSON/字符串时间；重名/转义等价JSON键后值覆盖仍披露。TSV/CSV/数字时间/stdin/新评分/输出文件开关均未加。
- 命令第一、文件第二、后续key/value成对；parse_args不含exe。格式预扫描未知key也消费value，保留ID值等于--format等保留名；filename以--开头用./。仅独立--help/--version，不读取文件。
- 成功stdout一个终端LF（也计最终16MiB）；text错误stderr、JSON失败stdout。JSON统一error_json/quote_json，不用String.escape。文件/输出I/O普通失败=2；4仅内部异常类别，不宣称所有OS灾难都exit4。
- close只尝试一次，不重试歧义EINTR；SIGPIPE显式忽略，EPIPE转FILE_ERROR非零。仅已验证本机Darwin arm64；不保证任意合法图20M内成功、全域时间/峰值内存或跨平台行为。
- [八例推导](validation/T3-worked-examples.md)及demo稿由agent整理，**不是本人纸笔/讲解**。T5步骤7本人部分/M2未完成，因此未生成声称整项完成的task-done标记，只记录机器部分实证。自动日志不能替代个人条件。
- 下一T6：广泛独立原版对照/变形/资源等号/性能及故障注入与A11。**当前compare.py原型仍面向开发argv probe，T6须按真实文件CLI协议接入qualification，不能直接把旧原型脚本通过当作CLI全链通过。**T7消费者/许可/包、T8CI/交接仍待做。
- 没有临床数据访问、外发、合并、推送、报名变更或发布。赛事当前资格/换题/截止未核实。

## 复验和继续

```sh
scripts/with-toolchain.sh moon test --target native --deny-warn
scripts/with-toolchain.sh moon build cmd/mooneventeval --target native --release --deny-warn
MEE_BIN=_build/native/release/build/cmd/mooneventeval/mooneventeval.exe MEE_EVIDENCE=evidence/T5/recheck-process python3 -W error::ResourceWarning -m unittest discover -s tests/cli -v
python3 validation/check_cli_reports.py --product _build/native/release/build/cmd/mooneventeval/mooneventeval.exe --output evidence/T5/recheck-bytes
python3 validation/check_native_io.py --output evidence/T5/recheck-native
python3 scripts/demo.py --bin _build/native/release/build/cmd/mooneventeval/mooneventeval.exe --output evidence/T5/recheck-demo
```

用新输出目录，别覆盖冻结收据。下次先核实际git状态，读AGENTS/contracts/T6卡；本人讲解单独记实际日期/SHA/推导，不让agent代填完成。
