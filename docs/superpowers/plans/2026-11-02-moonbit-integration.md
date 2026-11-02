# MoonBit 接入示例实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让使用者在完整仓库中直接运行独立 MoonBit 模块，了解评测、事件对解释和错误处理，并能按清晰的贡献与许可说明继续开发。

**Architecture:** 复用公开 eventeval API，新增独立本地 workspace 示例；不修改评分核心、输入格式、CLI、公开 API 或 38 文件源码包。示例只使用 MoonBit，不依赖 Python 评分或 sed_eval。

**Tech Stack:** 已锁定 MoonBit native 工具链、Python unittest 开发验证。

**Spec:** 本文与[共享契约](../../contracts.md)；用户要求继续围绕申报方向开发，保持提交、README、许可证和使用说明完整，技术验证全权交给 Codex。沿用已选择的本会话顺序实施方式。

## Global Constraints

- 继续使用现有隔离工作树；原主工作树不改动。
- 仅合成事件；不宣称真实采用、注册表发布或竞赛验收通过。
- 保留 MIT 与第三方声明；示例依赖在本地解析，不申请或占用包名。
- 历史冻结证据保持原样；本轮日志写入 evidence/P5。

## Review Focus

- 示例能否按公开命令在独立模块中解析本地依赖，而非误用产品内部包。
- 无合格候选和候选未被选中不能混同；解释不证明选择。
- 非法数字时间应为 INVALID_TYPE，失败无 summary。
- 源码包不含接入示例，分发文档链接须指向公开完整仓库。
- 后续状态提交与实际被测 SHA 必须分列。

### Task 1: 可运行示例与开发入口

**Files:** examples/moonbit-consumer/{moon.mod,moon.work,main/moon.pkg,main/main.mbt,README.md}；tests/test_library_example.py；README.md；docs/API.md；CONTRIBUTING.md；CHANGELOG.md；docs/PROJECT_STATE.md。

**Interfaces:** 使用 event/config/recording/task/evaluate/report_json/explain_pair/explanation_json/decode_task/error_json；输出依次为评测、合格但未选中事件对的解释、预期输入失败三条 JSON。

- [x] 写集成测试：实际运行文档命令，检查 TP/FP/FN=1/1/0、选中 p1、p2 eligible=true 且解释不含 summary、数字 onset_s 被拒绝且错误路径精确。
- [x] 运行测试，确认示例未实现时失败。
- [x] 实现本地独立模块和 Result 处理；完整命令无需用户修改路径。
- [x] 重跑测试、native suite、统一 17 步门及 13+4 演示回放；人工核对许可证、README、开发指南与包内容。
- [x] 独立评审后处理实质发现，提交真实工作，同步公开仓库，运行双平台 CI 并更新状态，记录实测提交与限制。实测原始f75963024/公开b06207ae9，CI41434748035；评审和作者修复分列，见 evidence/P5。
