# MoonEventEval P4 复审风险独立只读审查

审查基线：`a8ee78dab1383be29f9d2328093fbe3a44ea4130`，工作树初始/结束均 clean。按任务给定，对应公开 main `b78349435c20326be45148af391de2f58606f97a`；本次未联网验证此映射。仅检查本地材料与既存程序；不构建、不跑完整总门、不推送、不修改仓库。

结论：工程 Critical 0；Important 1（使用场景呈现）；Minor 2（版本入口、历史状态措辞）。另有一项已知申报材料合规边界，不能由代码验收或 AI 改稿消除。以下是可能影响首次接触评委理解/采用的风险，不预测组委会最终结果。

## Important

### I1. “三个实际场景”目前主要呈现为三个算法反例，使用目的与完整操作链没有放在评委入口

- 依据：`docs/PROJECT_POSITIONING.md:9-13`称“三个实际场景”，列出的却是重复预测、增广陷阱和精确边界；`EXAMPLES.md:10,77,150`也按这三个规则组织。三个输入均是同一 `clip-01/alarm` 的小型合成事件，确实可运行，但运行成功只证明规则，不自动证明三类实际接入或用户需求。
- 现成可用内容已经在 `docs/superpowers/specs/2026-10-20-mooneventeval-prd-design.md:17-27`：使用者假设、拿来的材料、动作、结果/决策，并明确无真实试用和“不换三个行业名当需求验证”。首页 `README.md:3,72-80`没有把这条需求—操作—产物链引出来。
- 风险：即使“输出是什么”已补齐，评委仍可能把项目理解成仅展示三条数学边界的专用演示；若其“至少三个完整预期场景”按用户任务判定，当前入口的说服力弱。不能据此断言已违反该条，也不建议为数量新增功能。
- 最低成本修复：在 EXAMPLES 开头把上述现有三任务逐一映射到已有输入/命令/报告字段/下一步人工检查；如“定位重复报警的具体 FP”“核查候选竞争后的配对”“解释容差边界并区分候选与所选配对”。保留“合成、预期任务、无真实采用证明”，把 POSITIONING 的“实际场景”改成“可运行的合成预期任务”。无需新算法、新数据或新行业标签。

## Minor

### M1. 首页 CI 指向旧轮次，新报告快照的验证入口分散

- 依据：`README.md:47-48`指向 run `39914869650`，`README.md:134-137`继续解释该轮基础门；新增 demo 的实际双平台验证 run `40447392163`只在 `docs/PROJECT_STATE.md:7`及 `docs/delivery/REVIEW_REVISION.md:17`给出。当前 workflow 的 demo 步骤在 `.github/workflows/ci.yml:85-87`。
- 风险：评委点击首页 CI 时，不能直接看到首页当前 demo 是在哪一轮重跑的，容易把新演示当作只提交了静态文本。旧 CI 声明本身不假；这是可发现性及版本对应问题。
- 最低成本修复：首页将最新演示验证链接与其实际被测提交并列，保留旧 run 为历史基础证据；明确后续文档 HEAD 没有重新跑 CI。`docs/demo.md:3`的“目标仅已验证本机 macOS”也应限定为 T5 历史脚本，避免被读成当前仅支持单平台。

### M2. 仍有不带历史前缀的 PRIVATE/未公开断言，与公开项目入口冲突

- 依据：`.ci/README.md:23-25`现在时写“The repository stays PRIVATE”；`README.md:46-51`给出公开源码与当前本地模块身份；`docs/PROJECT_STATE.md:17-18,38`说明后来已公开。`.ci/README.md`没有像 `docs/delivery/READINESS.md:3`那样标出其历史阶段。
- 风险：不是评分问题，但评委浏览复现/CI材料时会遇到互相冲突的发布状态；大量内部状态文件会增加理解成本。
- 最低成本修复：只在 `.ci/README.md`加一行历史范围提示并链接当前状态；不要重写冻结原始证据。首页可给出“先看报告 → 三任务命令 → 参考范围 → 最新 CI”的短路径，降低进入内部计划的概率。

## 已知申报材料边界（独立于工程分级）

任务提供的表单截图已明确“一页 Markdown”且“不要 AI 编写”。`docs/delivery/REVIEW_REVISION.md:26`也明确现有仓库外申报材料为 AI 辅助材料，不证明满足写作要求；`docs/PROJECT_STATE.md:54`保留该限制。本次没有查看、修改或认证仓库外申报稿。若继续把 AI 稿直接充作符合该条的正式申报书，仍有材料被退回的实质风险。最低成本只能交付事实/命令索引供参赛者自行撰写和核对，不能靠 AI 重写、排成一页、删去 AI 标签或工程通过来认证合规。

## 实质内容与小范围复现

- 无证据支持“只有 Python 包装或只有指标公式”：时间解析、资格判定、预算匹配、分组评测、事件明细渲染均在 MoonBit：`eventeval/time.mbt:5-89`、`eligibility.mbt:5-43`、`matching.mbt:36-145`、`evaluation.mbt:31-160`、`report_json.mbt:1-231`；native I/O 是 `cmd/mooneventeval/io_stub.c:1-48`。价值在确定的输入/报告工作流，测试数量不作为使用价值证据。
- 输出与参考范围已实质修复：`README.md:3-38`明确报告、stdout、完整成品与 eligibility/selection 区分；`THIRD_PARTY_NOTICES.md:30-60`明确规则借鉴、未移植功能、substitution/投影和 binary64 差异，未看到仍声称超过 sed_eval optimal 或全量兼容。
- 既存 binary SHA256：`7a65bacefef1c3b70d4b851dc4fae1b337ce9114eea4addefddcf3be92f1940d`。运行 README 所列三个 evaluate 及边界 explain-pair 共四条：均 exit 0、stderr 0 字节；输出分别与 `demo/output/duplicate.json`、`greedy-trap.json`、`boundary.json`、`boundary-explanation.json`逐字节相同。前三者 TP/FP/FN 为 1/1/0、2/0/0、1/0/0；解释差值/容差均与文档一致。这是既存 binary 的烟测，未声称本轮从基线重新构建或复跑原版。
- 首次安装依赖与支持边界已明示：`README.md:47-66,84-95,124-128`写明两平台、Python/curl/C 编译器、自定义 JSON 和 2,000 事件上限；`scripts/install_toolchain.py:42-45`确实只接受 Darwin arm64/Linux x86_64。未发现值得用新增格式/平台/模型功能解决的当前承诺矛盾。

建议顺序：先修 I1 的现成内容映射，再修 M1/M2 的入口状态；保留核心功能边界，把正式申报稿来源问题单独交给参赛者处理。
