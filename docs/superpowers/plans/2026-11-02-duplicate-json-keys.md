# 拒绝 JSON 重名键实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 原始文件/字节输入中同一对象的重名键明确失败，防止静默覆盖；用户“那你继续推进”授权实施上一轮建议，先完成此输入契约修订。

**Architecture:** 在严格UTF-8和有界标准JSON解析成功后，对原文进行一次对象作用域扫描。完整字符串token由原解析器解码后比较；不自写Unicode转义解析、不改变core。typed工厂不受影响，数学与匹配不变。

**Tech Stack:** 锁定MoonBit native；已有Python真实进程验证。

**Spec:** [共享契约](../../contracts.md) P6修订；本轮收紧旧last-wins，不宣称对重名键输入兼容。

## Global Constraints

- UTF-8/JSON语法/深度错误优先于重名键，重名键优先于schema校验。
- 逐对象比较解码后的精确Unicode字符串，不规范化；不同对象可以重用键。
- 新错误DUPLICATE_KEY，Input/exit2，path="$"；不返回部分评分。
- message含最多64个Unicode码点的安全键预览及第二个键的零基UTF-16位置（可选BOM剥离后）；不把整份长键放进错误。
- 不改变schema_version、评分语义、38文件产品包或未发布0.1.0候选身份；本轮以输入契约v3与Git SHA标记兼容性改变。
- 历史冻结证据保持原状；本轮写evidence/P6。

## Review Focus

- 转义等价键、原始/转义非BMP字符必须识别；规范等价但码点不同的键不能误合并。
- 对象嵌套、兄弟对象、数组中的对象作用域；字符串中的冒号/花括号不是结构。
- 反斜杠及引号转义，合法值重复不能误判键重复。
- 已知输入字节/深度上限和错误优先级；大键错误文本不能失控。
- 历史last-wins证据保留历史标签，当前契约/PRD/说明/开发probe不能继续承诺覆盖行为。

### Task 1: 原始键检查与兼容性修订

**Files:** eventeval/input.mbt、input_wbtest.mbt；tests/cli/test_cli.py；validation/check_probe.py；contracts/PRD/README/API/VALIDATION/CHANGELOG/PROJECT_STATE/ACCEPTANCE；evidence/P6。

**Interfaces:** decode_task(Bytes)、evaluate_json(Bytes)保持签名；新增DUPLICATE_KEY错误；typed API与正常报告不变。

- [ ] 写真实decode/API与CLI行为反例，确认旧实现错误接受重复字段；记录RED。
- [ ] 实现原文作用域检查，沿用标准解析器解码键；运行GREEN与边界/转义/作用域用例。
- [ ] 更新当前契约及旧条款作废说明，更新开发probe；检查历史记录不被改写。
- [ ] 跑完整17步、开发probe、13+4演示；独立评审并修复实质问题。
- [ ] 保留真实提交，推送与双平台CI，复核产物并更新交接状态。
