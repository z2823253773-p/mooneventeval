# MoonEventEval 当前状态

更新：2026-10-21（America/Phoenix）。**T0、T1、T1b、T2、T3、T4核心实施已完成。T4唯一独立评审发现1项Important验证器问题，作者单轮RED→GREEN修复并全量复验通过；无第二次独立复审。下一目标T5文件CLI/demo。本人M2、最终A11、后续I/O/消费者/CI/发布均未完成。**

## 当前入口

- [contracts](contracts.md) → [有效计划v2](superpowers/plans/2026-10-20-mooneventeval-plan-v2.md) → [T4结果](reviews/2026-10-21-t4-results.md) / [评审修复](reviews/2026-10-21-t4-review.md) → [T5任务卡](superpowers/plans/tasks/T5-cli-demo.md)。旧单文件v1作废。
- Codex主实施；工作树`/Users/henryz/Desktop/比赛/mooneventeval-t0`，分支`spike/t0-feasibility`。原main仍8a3075521312c9bf9ad196309422adaa0c67fbd2，不在其中实施；沿用局部锁定工具链/参考venv，不重装。
- T4基线9886ce1d9c1390d298c9f34d77d7185ec3e4b043；产品实现/评审候选d528d30b3e8b1feaea801c2058ec310206f78b65；**最终验证器及被测SHA d00b0a62437056461510e85e4b2326d7cdf707b6**。其后收尾仅文档/证据提交，以git log为准。
- [T4 manifest](../evidence/T4/manifest.json)冻结源码、binary、命令、日志及文档快照。最终运行目录renderers-verified、byte-mutations-verified。旧text-mode检查不能支持原始字节证明，均保留为历史；最终原始bytes捕获另有430实测。T3及更早证据仍绑定其历史SHA，不拿旧manifest证明当前活动文档。

## 已完成与边界

- T0固定编译器/清单/JSON/native短I/O/局部包探针；T1精确十进制/Unicode/资格；T1b原版参考hash锁环境；T2显式栈first-free+DFS、753图、密集/长链及2mutation。各阶段results与manifest保留。
- T3严格Task/Event/Config封装与复制、decode/evaluate/JSON/error/dev argv；同录制同类规范码点排序/最大基数，任务共享20M预算、全局微平均、undefined=null、完整机器字段。最终508d5cf：38 Moon、4 Python、29 validation；56 argv及64控制字符。两项独立Important已作者修复，未二次复审。
- T3固定/seed二进制网格46原型：43共同投影一致，1已说明binary64边界差异（10.3−10.1>0.2导致原版TP0、精确产品TP1），2原版拒绝0 collar由Fraction oracle覆盖；未解释差异0。四资格mutation为编译成功后的行为杀死。不是最终A11。
- T4公开explain_pair/explanation_json/report_text/explanation_text及封装PairExplanation。解释同源eligibility、不跑匹配或猜选中身份；文本完整配置/指标/所选配对/FP-FN依据/工作量，身份可逆安全引用；JSON固定顺序，精确12位容差与signed delta。
- 四renderer共用最终UTF8 16MiB门；内部16,777,216等号通过、+1拒绝，中文5字节/NUL转义8字节均测等号与超限。合法2000事件容量例TP1000/steps3000，JSON4,015,857、文本11,023,901字节。只证明规定样本，不保证全域时间/内存。
- 最终Moon **49/49**、原Python **4/4**、validation **29/29**；锁定fmt/info/check/build通过。最终提交后task-done49/49。430真实报告调用：46旧JSON原始byte一致、122对Fraction依据、44身份类和错误/重复确定性。56原argv/64 JSON控制检查亦在本阶段及独立评审复跑通过；NUL查询ID由typed测试覆盖（OS argv不能含NUL）。
- T4唯一fresh评审独立复跑49/4/29/430/56/64、额外binary核46份一致；发现text=True验证器false-green。作者两换行变异RED→GREEN修复，原始档案hash实证吻合；无产品改动、无二次评审。详见评审原文/作者resolution。

## 决定及未完成

- 时间仍为严格字符串，重名/转义等价JSON键后值覆盖是已披露边界。TSV/CSV/数字时间/新模式/拒绝重名键尚未批准扩展；不能暗中改schema。
- 必须用JSON专用quote_json（Json::string(...).stringify()），不用String.escape。内部decimal_string已改名format_scaled_seconds，返回未引号正文。bounded_serialize仅白盒适配器，产品用bounded_output；T5使用四公开renderer/error_json。
- [八例推导](validation/T3-worked-examples.md)是agent材料，不是本人纸笔/讲解；M2个人条件尚未完成。T4未重跑sed_eval，不冒称最终A11或完整A9。
- 待做T5真实文件CLI/三分钟demo/本人讲解，T6广泛对照/完整资源I/O及A11，T7包外消费者/许可/包，T8 CI/最终交接。仅本机macOS native，不保证全合法图在20M内成功。
- 没有访问临床数据、外发、推送、合并、报名变更或发布；赛事当前资格/换题/截止尚未核实。

## 下一步

读AGENTS/contracts/T5卡，先核对实际git状态。复用现有decode/evaluate/explain及四renderer，开发probe不是产品CLI；按T5做有界真实文件I/O与参数/退出协议，先验证最高风险切片。个人demo讲解单独记录，不能由agent替代。

```sh
scripts/with-toolchain.sh moon test --target native --deny-warn
python3 -W error::ResourceWarning -m unittest discover -s tests
.venv-reference/bin/python -W error::ResourceWarning -m unittest discover -s validation/tests -v
scripts/with-toolchain.sh moon build cmd/probe --target native --release --deny-warn
python3 validation/check_reports.py --product _build/native/release/build/cmd/probe/probe.exe --output evidence/T4/recheck
python3 validation/check_report_bytes.py --product _build/native/release/build/cmd/probe/probe.exe --output evidence/T4/recheck-byte-mutations
```

全新checkout才运行工具链/参考bootstrap；已有venv拒绝覆盖。重跑输出使用新目录，保留冻结证据。
