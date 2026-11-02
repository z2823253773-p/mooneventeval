# P5：MoonBit 接入与开源开发入口验收

2026-11-02 America/Phoenix。用户授权继续围绕申报方向开发与维护开源材料。交付为独立本地 MoonBit 模块、真实编译集成测试、贡献指南、变更记录及 README/API 入口；没有修改评分、输入、CLI、模块身份或38文件包契约。

## 实际结果

- 初候选原始ff728dc0e / 公开82a93901d；独立评审0 Critical / 1 Important / 0 Minor，见[原报告](independent-review/REVIEW.md)。Important：贡献指南漏写公开冷克隆的历史证据还原步骤。
- 作者核查后在原始f75963024 / 公开b06207ae9修正。新克隆确实缺失该历史证明；运行恢复器后SHA正确、HEAD不变。最终原始提交重新通过完整17步门，没有第二次独立复审。
- [实际双平台CI41434748035](https://github.com/z2823253773-p/mooneventeval/actions/runs/41434748035)，被测b06207ae936e4179064ba4ccf7941cac61773f6e，两job成功。每OS：58 MoonBit、29根Python、42验证、15 CLI，1620产品资格验证调用，38文件包/解包/包外消费者及13产品+4原版演示回放。
- 两OS的243源码hash相同并绑定公开Git；每OS8144基础产物及35演示文件按哈希复核。新增测试真实编译/执行独立模块；另以空PATH执行编译后的native示例，仍输出三条预期JSON。
- CI后的README链接/状态/计划更新不是新的全量CI。该README另通过38文件源码包验收，保存在metadata.zip。

## 离线复核

在包含该被测提交的完整Git克隆中执行（Python >=3.12与Git；无需工具链、参考环境或网络）：

```sh
python3 evidence/P5/verify.py
```

核对冻结文件哈希、归档字节数/路径/CRC、实际run/jobs、完整门退出码与流哈希、基础产物、13+4报告回放、两平台源码库存及其公开Git内容。验证使用显式失败检查，不依赖Python assert。后续状态提交不会冒充被测源码。

| 归档 | 保存内容 |
|---|---|
| local.zip | 初候选/最终本地完整门、RED/GREEN日志、示例执行、空PATH运行、冷克隆恢复、原独立评审与当时ledger |
| remote.zip | 实际下载的两平台完整CI产物，不重新生成或改写报告 |
| metadata.zip | CI链接更新后的38文件源码包独立复验 |

归档大小、成员数与SHA256见archives.json；全部最终证据文件由SHA256SUMS.json锁定。日志保留生产时路径。独立评审只覆盖其候选，作者修复、后续元数据和本复核器不冒称已由同一评审认证。

没有包注册表发布、真实外部采用或竞赛最终验收的声明。旧阶段冻结证据保持原样。
