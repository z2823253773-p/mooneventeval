# MoonEventEval 当前状态

更新：2026-10-22（America/Phoenix）。**T0至T6限定本地机器实现/验收完成；T6唯一独立评审的2项Important已作者单轮修复并复验，1项Minor延期，无第二次独立复审。T7本地消费者/38文件候选包/解包CLI及示例完成，唯一评审1项Important已作者单轮修复复验，无新增Minor或第二次独立复审。T8统一验证器与手动CI配置已实现，失败测试初轮通过；首次完整本地总验证和整分支唯一评审待做。本人M2/口头讲解、远端CI/发布与赛事资格未完成。**

## 当前入口和SHA

- [契约](contracts.md) → [有效计划v2](superpowers/plans/2026-10-20-mooneventeval-plan-v2.md) → [T6结果](reviews/2026-10-22-t6-results.md) / [评审处置](reviews/2026-10-22-t6-review.md) → [验收地图](ACCEPTANCE.md) → [T7结果](reviews/2026-10-22-t7-results.md) / [评审处置](reviews/2026-10-22-t7-review.md) → [T8任务卡](superpowers/plans/tasks/T8-ci-handoff.md)。旧v1作废；个人部分仍见[T5卡](superpowers/plans/tasks/T5-cli-demo.md)和[demo讲稿](demo.md)。
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
- T7包外API消费、归档解包后再消费、README示例/许可/本地候选已完成；T8需统一检查/CI/交接。正式作者/namespace/仓库URL未确认时不得编造。远端创建、外发、合并、推送、报名变更、发布仍需明确授权；本轮无上述操作，无临床数据访问。赛事当前资格/换题/截止未核实。

## 复验和继续

先核实际git状态，再读AGENTS/contracts/T8卡。快速核冻结证据：

```sh
python3 evidence/T6/freeze.py
scripts/with-toolchain.sh moon test --target native --deny-warn
.venv-reference/bin/python -W error::ResourceWarning -m unittest discover -s validation/tests -v
```

重新生成对照用全新未冻结目录，例如evidence/local-recheck-t6；不要向冻结T6新增日志。产品构建命令：`scripts/with-toolchain.sh moon build cmd/mooneventeval --target native --release --deny-warn`。下一步读T8卡，先为统一检查器写实际失败控制，再实现本地总验证与未触发的CI配置；不是发布或把远端记为已运行。


## T7 已完成（限定本地机器验收）

基线914cffd301d40eff8f4b2ecd697adb5052ebb031。新增scripts/check_consumer.py、package_candidate.py、check_examples.py、release_support.py及tests/consumer模板；未改eventeval/cli/native运行源码或公开API。moon.mod仅新增MIT/readme/description；namespace仍local/mooneventeval，无repository URL。

独立临时consumer现代moon.mod import配合moon.work本地成员（旧path-deps语法不适用）；只import公开eventeval，A1 TP1/FP1/FN0并解析report。故意断言TP2时build成功、实际执行失败。包白名单38文件，保留运行源/native stub/生成接口/完整案例/公开文档/工具链安装器和锁；排除probe/原始证据/计划/本地工具。实际moon package --list --frozen与zip成员/源码bytes一致，解包到新临时目录后再跑包外consumer、解包原生CLI构建及README六命令（help/version/三案例/explain）；复用已有工具链，不重下载。

最终12 Python（8新发布门+4工具链）、58 Moon通过；fmt/check及info实际通过。初次moon info错误带--deny-warn和清单格式检查失败日志保留，不能称初次成功；修正工具参数/格式后才通过。EXAMPLES完整JSON输入和summary逐块核对真实输出；API首个MoonBit块与实际编译消费者逐字一致。

LICENSE署名取当前git作者Hengrui Zhang（不分发邮箱）；MIT及core原始Apache-2.0 LICENSE/NOTICE保留。无sed_eval/Python依赖或下载数据进入候选。T7仅本地候选，正式作者身份/namespace/URL如未来更改须重验；T8/本人M2/发布仍待完成。原评审候选a441ce89b57595c326031e8699b066777028f0b2，最终代码/被测**bb24ce33962ebf6276265075edb3df10e16e6601**；后续收尾提交仅文档/证据。独立评审原样521文件在evidence/T7/independent-review，1 Important解释完成状态门缺口已真实编译反例RED→GREEN修复。作者原始脚本重放gate exit1/failed账本保留，非第二次独立复审。最终consumer-final、package-final、examples-final及[manifest](../evidence/T7/manifest.json)可复核；`python3 evidence/T7/freeze.py`。T7未改运行源码/公开API，T6历史冻结继续有效，但当前moon.mod/公开README已按T7更新，不以历史当前文件hash断言检验T7。


## T8 实施中

基线7f325643cf12d3cab5a60f9808af3ec94d11caed。scripts/verify.py仅检测当前cwd项目，不回退脚本所在目录，要求干净已提交源码；全17检查步骤/产物/hash绑定，缺失或跳过不通过。新tests/test_verify.py覆盖错误根目录、缺binary/参考、工具链hash变更、子命令非0、候选缺LICENSE、失败/跳过报告、CI权限/浮动pin/缩减命令、空/跳过测试协议。初轮10验证器测试通过；完整机器结果尚待实际运行。

.github/workflows/ci.yml为标准JSON形式YAML，workflow_dispatch手动触发，macos-14 arm64/ubuntu-24.04 x86_64，四Actions完整SHA取官方release→commit实查，docs/ci-actions.lock.json记录来源；只保存配置，不推送/触发/发布。CI用相同verify；原版依赖同一hash锁，Linux身份另记，不伪称已完成跨平台认证。细节见[统一验证](VALIDATION.md)。
