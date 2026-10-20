# MoonEventEval 当前状态

更新：2026-10-20（America/Phoenix）。**T0与T1完成；T1独立评审发现的Unicode工厂缺口已修复并主验收PASS。完整评测器和CLI尚未实现。**

## 入口与工作位置

- [contracts](contracts.md) → [修订计划v2](superpowers/plans/2026-10-20-mooneventeval-plan-v2.md) → [T1实际结果](reviews/2026-10-20-t1-results.md) → [下一T1b任务卡](superpowers/plans/tasks/T1b-reference.md)。旧单文件v1计划停止执行。
- Codex主实施者；工作树 `/Users/henryz/Desktop/比赛/mooneventeval-t0`，分支 `spike/t0-feasibility`。原仓库main基线`8a3075521312c9bf9ad196309422adaa0c67fbd2`，无remote。继续时先核对真实git状态，不重复实施T0/T1。
- 本轮T1基线`8d8f417c88542ee891379fdd158c6a4adc129ec8`；最终被测源码`650325eb981875df7e00b537c9648a8146ff8abb`；文档/证据提交以git log为准。证据[evidence/T1/manifest.json](../evidence/T1/manifest.json)。

## 完成项与实测边界

- T0：局部moonc v0.10.14+7d59c7ec9已安装校验；语法/清单/JSON/native短I/O/实际打包已验证。二进制符合发布者sidecar，core只符合历史SHA，不是发布者认证。
- T1：有界ASCII十进制扫描转Int64微秒/ppm；验证后封装Event/Config；UTF-16代理配对和256码点限制；Unicode码点排序；有符号解释偏差与精确collar/参考时长资格判断。
- MoonBit全套13/13、JSON前提6/6、Python4/4；native check/build、fmt检查通过。5个公式定向mutation均成功编译并导致行为断言失败，未把初次编译失败算作捕获。仅macOS arm64。
- 独立评审原为T1未达完整验收，发现安全substring可制造孤立代理、工厂却接受；已先RED再修复，主验收13/13及5个mutation再验通过。[评审原结论与处置](reviews/2026-10-20-t1-review.md)，未声称第二轮独立PASS。
- sed_eval固定源码仅只读核对公式，未安装/运行。T1b、独立parity/M2、匹配、完整JSON任务/报告/CLI/demo、本人纸笔复算/讲解、Linux/远端CI、包外消费与发布均未完成。

## 决定与限制

- Event/Config保持私有字段；业务数学在MoonBit，Python仅开发验证。本轮无Python参考依赖安装，无临床/科研原始数据访问。
- 解析深度参数deprecated局部兼容例外保持T0决定。T1另有声明级unused_field/unused_value暂时豁免，因为正式消费者在T3/T4；T3接入时移除，代价是此前会屏蔽这些声明的相应闲置告警，不能扩为全包关闭。
- ID/label错误：空值INVALID_SCHEMA、非法代理配对INVALID_UNICODE、码点超限RESOURCE_LIMIT（首先观察257）；时间/比例语法INVALID_DECIMAL、超界或非正时长OUT_OF_RANGE。任务索引路径前缀留T3。
- 本轮仅T1；参考环境归独立T1b，代价是parity未知。保留前次失败和原始日志，原日志尾随空格不做归一化；源码/文档空白检查排除evidence。
- first-free+DFS及T1b/T3阶段修订仍待相应批准；TSV/CSV、JSON数字时间、删除最终原版对照未批准；A11保留。赛事当前资格/换题/截止细则及真实需求仍未确认，没有外发、推送、报名变更或发布。

## 下一步与命令

下一实施目标T1b参考环境，尚未开始；按任务卡单独记录依赖安装、固定版本/哈希、self-check与失败，不改写T1为原版对照。T2算法调整尚未实施。

本地复验：`scripts/with-toolchain.sh moon test --target native --deny-warn`（当前13项）；`python3 -W error::ResourceWarning -m unittest discover -s tests`（4项）；`scripts/with-toolchain.sh moon fmt --check`；`python3 scripts/check_design_docs.py`。

已有局部工具链无需重装。新checkout才运行`python3 scripts/install_toolchain.py`（Python>=3.12、curl、native C编译器）；禁止用默认版冒充固定版本。spikes/T0是历史一次性探针，不复制成产品实现。
