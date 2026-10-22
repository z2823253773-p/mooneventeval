# MoonEventEval 当前状态

更新：2026-10-21（America/Phoenix）。**T0、T1、T1b、T2和T3核心实施已完成。T3独立评审发现2项Important，作者单轮修复与全量复验通过；没有二次独立复审。本人复算/M2、最终A11、解释/文件CLI/demo仍未完成。**

## 当前入口与位置

- [contracts](contracts.md) → [修订计划v2](superpowers/plans/2026-10-20-mooneventeval-plan-v2.md) → [T3实际结果](reviews/2026-10-21-t3-results.md) / [评审与修复](reviews/2026-10-21-t3-review.md) → [下一T4卡](superpowers/plans/tasks/T4-reports.md)。旧单文件v1已作废。
- Codex主实施；工作树`/Users/henryz/Desktop/比赛/mooneventeval-t0`，分支`spike/t0-feasibility`。原main仍`8a3075521312c9bf9ad196309422adaa0c67fbd2`，干净、无remote。复用局部工具链/参考venv，不重跑安装或重做已完成阶段。
- T3基线`9c78a20aaa34514e218afd7ce26cae1e0ce03046`；最初候选/独立评审SHA`e9c7f317bcd141aa34dbcc3e1ee6728415be3824`；**最终代码/被测SHA `508d5cf6cc5ef637f0931bbdaae36b1729256b03`**。后续文档/证据提交看git log，不把它们冒称新的运行实现。
- [T3 manifest](../evidence/T3/manifest.json)冻结最终源码/产物/命令/日志hash、原始评审及修复失败→通过记录。parity-final、process-final、json-controls-final为最终运行目录；旧candidate/committed/fixed试跑证据保留，不能混作最终SHA。历史T2证据只证明其当时提交，随T3变化的STATE/contracts不能拿旧快照哈希验证当前文件。

## 已完成与实证边界

- T0工具链/清单/JSON/native短I/O/本地打包；T1精确十进制/Unicode/资格；T1b局部hash锁原版环境；T2显式栈first-free+DFS、753图、密集/长链及两mutation。原记录保留在各阶段results/manifest，不因T3进度被抹去。
- T3封装Recording/Task工厂与数组复制，严格decode_task、完整evaluate/report_json/evaluate_json、error_json、native开发argv probe。两侧事件先校验后建图，规范码点排序，同录制同类最大基数，唯一20M任务预算；全局微平均、空定义null，声明类别/空录制都纳入。
- JSON完整固定字段和数组顺序，精确规范时间/12位终点容差，FP/FN候选度数/原因；报告最后UTF8字节数限制16MiB。字段未知/类型/ID/类别/字节/深度限额及失败不含部分分数。仅开头一个BOM允许。
- 最终508d5cf提交后：MoonBit **38/38**（含T2的753图数据驱动检查）、原Python **4/4**、validation **29/29**；fmt/info/check/build均经锁定wrapper退出0。
- 56项真实argv输入/错误协议检查；64项U+0000..001F成功/失败JSON独立Python解析往返；复制、Unicode码点/组合字符、跨组预算、四种空集和微平均均有白盒/外部检查。
- Fraction时间oracle在秒域独立计算，图oracle枚举部分注入；46固定/seed20261021二进制网格原型任务全部实际跑probe+原版参考。43共同投影/每类原始计数/逐录制投影一致；1具体binary64边界差异；2原版拒绝0 collar，产品用精确oracle通过。46例重排stdout字节一致、改ID计数稳定；未解释差异0。
- 具体边界：10.3−10.1的binary64为0.20000000000000107>0.2，原版TP0而产品/精确oracleTP1；保留hex见证及双输出。错类保留raw Nsubs1/FP0/FN0及projected FP1/FN1，不混称原始全局相同。
- 四资格mutation（起点/终点<=改<、max改min、参考改预测时长）均control通过且变异编译成功、行为失败；最终资格源码hash未变，全产品38项回归通过。

## 独立评审与修复事实

- 唯一fresh评审复跑临时native37项、release probe、32控制字符、1错误路径、8种比较器篡改；发现Important2、Critical0、Minor0。未独立重跑整套sed_eval/Python/mutation，原报告及107份收据保存在independent-review，校验hash后复制。工具额度中断后恢复的是同一次评审，不是第二场。
- P1：String.escape是MoonBit显示语法，28控制字符会输出非法JSON。先观察真实ParseError/JSONDecodeError，再统一Json::string(...).stringify()；最终全控制字符在成功/错误报告、code/message/path均往返通过。T4须复用此JSON编码器。
- P2：比较器曾规范化被测时间并用Python宽松相等。四新回归RED→GREEN，先校验实际机器schema/类型/规范十进制/嵌套键序，再比较；不能纠正实际输出。作者重放原脚本的7项协议篡改现均被拒绝。
- 不复制matcher为精确计步oracle；比较器校验搜索步类型/范围，精确消费由产品白盒/共享预算测试保证。原评审额外空图steps=1篡改可被此比较器接受，不能把对照说成独立逐步计量证明。

## 决定与仍未完成

- 用户继续授权T3及常规修复；T1b成功实际对照，不使用未批准的超时后demo降级。TSV/CSV/数字时间/新模式/重名键拒绝未批准；重名/转义等价键后值覆盖继续明确披露。
- EvalError为pub(all)不可变字段，允许适配层创建参数/文件错误；Event/Config/Recording/Task/Evaluation仍封装。error_json是唯一失败序列化接口；公开decode以Result收拢私有结构化解码异常。
- T1/T2临时unused/struct-never-constructed豁免已移除；唯一deprecated兼容豁免仍是parse_bounded中T0验证的深度参数。不要在JSON序列化使用String.escape或照抄旧tuple Show。
- [八例推导](validation/T3-worked-examples.md)是agent材料，**不是本人纸笔/讲解证据**；M2个人条件未完成。T3机器实现并不代表M2/A11/全部A9通过。
- 待做：T4同源explain/text及内部序列化等号/超1（包括16MiB）；T5真实文件CLI/三分钟demo/本人讲解；T6广泛非边界原版parity/完整资源I/O资格与A11；T7包外消费者/许可/包；T8远端CI/最终交接。未核赛事当前资格/换题/截止细则，未确认真实用户需求。
- 只有本机macOS native证据；没有全合法图必在20M或墙钟/峰值内存保证。没有访问临床数据、合并、外发、推送、报名变更或发布。

## 下一步与复验命令

下一目标：**T4指定事件对解释、文本报告与输出预算**。读AGENTS/contracts/T4卡；复用当前Task/Evaluation、eligibility、decimal_string及quote_json，避免重写不一致的时间或转义逻辑。T4卡旧样例可能需要按实际接口/锁定版修正，先记录决定再实施。

```sh
scripts/with-toolchain.sh moon test --target native --deny-warn
python3 -W error::ResourceWarning -m unittest discover -s tests
.venv-reference/bin/python -W error::ResourceWarning -m unittest discover -s validation/tests -v
scripts/with-toolchain.sh moon build cmd/probe --target native --release --deny-warn
.venv-reference/bin/python validation/compare.py --phase prototype --product _build/native/release/build/cmd/probe/probe.exe --output evidence/T3/recheck-parity
python3 validation/check_probe.py --product _build/native/release/build/cmd/probe/probe.exe --output evidence/T3/recheck-process
python3 validation/check_json_controls.py --product _build/native/release/build/cmd/probe/probe.exe --output evidence/T3/recheck-controls
```

全新checkout才运行工具链安装/validation bootstrap，已有venv拒绝覆盖。仅macOS arm64资格已验，不在全局Python装依赖。
