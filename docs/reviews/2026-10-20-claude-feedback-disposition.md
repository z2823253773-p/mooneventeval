# 外部计划反馈处置（Codex为主）

2026-10-20。这是一份技术评审处置与计划修订，未执行T0、未编译MoonBit、未实现产品。上次结构自查确实不能证明目标版本可行性；Counts.fn也未被该自查发现，此处明确修正，不再把文档覆盖当行为覆盖。

| 反馈 | 核实结果/边界 | 处置 |
| --- | --- | --- |
| 上次退回因为窄/薄 | 现有交接主因是与MoonRow主键CSV比较核心重合；窄/薄是本反馈的推断，且评审者称未读PRD | 保留查重与价值风险；两个命令数量不能判断库薄厚，新增格式也不能保证初审 |
| 薄TSV/CSV | JSON需转换的易用成本合理，但当前PRD明确排除CSV导入 | TSV列BACKLOG待确认；不默认做CSV解析器或放开数字时间 |
| 自查只看结构 | 属实；原先记录也注明非产品验收，但缺少编译可行性证据 | 新checker明确NOT_ASSESSED；先T0工具探针，再核心行为门槛 |
| 审计脚本在tmp | 属实，旧plan-check不能仅凭JSON复算其逻辑 | 原两份checker来源存scripts/review/；现行检查为scripts/check_design_docs.py，相对仓库定位；历史脚本只复现旧结构规则 |
| Counts.fn字段 | 官方词法列fn为关键字，旧计划不应使用；未实跑目标编译器错误 | 新契约fn_count→JSON键fn；Pythoncounts["fn"]不变。目标版编译属于T0，不编造结果 |
| manifest/inspect/parse/borrow/package | 本轮仅读到默认版本core和帮助，无法证明目标0.10.14全部支持；inspect!偏旧不等于必错 | 清单统一作为T0前置；卡片用inspect候选，真实语法/警告须实测冻结 |
| mutation缺失 | 原先主要验证比较器，产品变体缺少明确步骤 | T2/T3/T6增加可编译错误变体→红→恢复绿；等价/不可编译变体单列，不计有效kill |
| oracle共因失效 | 成立，多个工具来自同一规格仍可能共错 | 新增八个供本人复算例子，来源是AI构造/算术，不称用户已手算；仍保留独立参考与fresh审阅 |
| sed_eval阻断M2 | 环境确实是非产品高风险，不能无预算安装 | T1b独立、3小时排障上限；建议核心T3单独成立；最终A11不由固定样例自动替换，此阶段顺序改动待确认 |
| 升序Kuhn密集图预算 | 旧规定n×n完全图邻接检查为n(n+1)(n+2)/6；n=500为20958500，尚未计其他步即超20M | 密集图提前至T2；建议first-free再完整增广，仍需穷举与真实benchmark，不自动加预算 |
| 重名键覆盖矛盾 | 当前PRD已有明确限制；“无损”特指十进制时间，不代表保留原JSON全部词法信息 | 增加显式用例和警示；若要拒绝，必须能识别转义等价键，另行修订，不写粗糙split预扫 |
| 硬化投入失衡 | 提前证明核心/demo更重要，但文件安全、正确错误码、许可与包外调用仍是可用性底线 | 保留简单边界检查，较重故障注入后置；16MiB只按最终字节检查，无需自造流式设施；未做项不叫完成 |
| 没环境却要求Linux性能 | 本轮只有本机Mac，无远端授权 | 本机先测；Linux/远端结果明确未测，CI配置不算运行证据 |
| 缺demo/讲解 | 上版有三案例和CLI设想，但缺具体讲解交付 | docs/demo.md补三分钟脚本/贪心图；T5跑真命令，本人实际讲解独立记账 |
| sed_eval A2预期 | optimal数学/源码预期应是TP2，与目标一致，尚未实跑 | 对抗的是朴素贪心TP1，不虚构成熟工具少算作为卖点 |
| T1–T3两天估算 | 没有工具可行性/环境/核心实际耗时支撑 | 撤回暗示，先2小时T0，按实测重估；不承诺10月31日前审核通过 |
| 每Task必须新会话、/clear | 用户指定Codex为主；这是工作习惯建议，不是Codex强制规则 | AGENTS为入口，主chat按清晰阶段推进，必要时用户开新chat；不用Claude命令套Codex |
| 共享契约和分任务 | 适合本项目，也减少重复上下文 | docs/contracts.md+10张任务卡，v1显式停止执行；CLAUDE.md只指向同一入口 |
| 早期独立审阅 | 只末尾审查发现地基错误太迟 | T0与T3加入fresh只读审阅；执行获批后使用适用授权的子代理，不自动新建用户chat |

## 证据及未完成事项

本轮做了文档/源码只读核查和密集图计数算式计算；不是运行时benchmark。实际T0的字段编译、manifest、parse、borrow与package均未执行。当前产品也不存在，因此mutation只是已补入计划，尚未有kill率或红绿结果。

官方依据：

- [MoonBit词法关键字](https://docs.moonbitlang.com/en/latest/language/lexical-conventions.html)：fn为关键字；不能代替目标版本编译日志。
- [Codex AGENTS说明](https://learn.chatgpt.com/docs/agent-configuration/agents-md)：仓库指令入口；项目状态等文件是本项目约定。
- [Codex subagents说明](https://learn.chatgpt.com/docs/agent-configuration/subagents)：可把探索/评审噪声隔离并返回摘要；并行写入需要协调，增加代理会增加上下文成本。
- [官方Codex工作流示例](https://developers.openai.com/cookbook/examples/codex/iterating-development-workflows-with-codex)：AGENTS可识别，其他状态/阶段文件应按项目适配，不是必须照搬的目录规范。

历史审计来源原文件SHA-256：plan为`e1780e6bcd0457257ff05edd02979f46096bd47b4f8330fae386d4aba353ad8f`，PRD为`11bcb87b6647539bd8afd73173952307c3c24e1ea474d36b8a63d04aa8baf146`。存仓库时改为相对根定位，并把仓库外索引可用性改为显式报告而非不可移植的强制依赖；旧检查器含“无产品文件”等阶段断言，仅适合历史文档阶段，不应成为未来产品总验收脚本。

## 下一步审阅对象

[修订计划](../superpowers/plans/2026-10-20-mooneventeval-plan-v2.md) 和 [T0具体问题/探针](../superpowers/plans/tasks/T0-feasibility.md)。TSV与删减最终参考验收没有被自动批准；算法/核心门槛顺序修订在执行前确认。无需重新选择由哪个平台主导：已按用户确定的Codex为主整理。
