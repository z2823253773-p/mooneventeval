# P6：拒绝原始JSON重名键验收

2026-11-02 America/Phoenix。用户授权继续推进前轮优化建议，本阶段先修订输入契约v3，拒绝同对象的解码键重复。JSON语法、Unicode与深度仍由锁定标准库负责；产品在schema校验前按原文对象作用域查重，不自写通用JSON解析器，不修改core。

## 行为与兼容性

同对象同名或转义等价键返回Input/DUPLICATE_KEY、exit2、path="$"，失败不含分数。不同对象可重用字段，不进行Unicode规范化。message提供最多64原始Unicode码点的安全预览，超长加省略号，并给出第二次键在剥离可选BOM后文本内的零基UTF16偏移。这个契约明确替代旧last-wins，不声称对旧重名键文件兼容。typed API、数学、正常输出、schema版本与未发布0.1.0源码候选身份不变。

## 实际验证

- 基线原始5b7dfafe6 / 公开e8caf55a2，初候选原始3ceabc725 / 公开29cec63c5。真实API/CLI先RED后GREEN。
- 初候选独立评审0 Critical / 1 Important / 1 Minor，见[原报告](independent-review/REVIEW.md)。Important是当前选题说明仍承诺旧覆盖行为；作者修正文档。Minor是预览测试未检查内容；作者补强断言并验证空预览mutation实际失败。没有第二次独立复审。
- 原始最终实测7c46e83165a5565338715600c220ac3c37a472ec / 公开最终实测2a007a352dd349c45236bebb0f18b972ce2ac3a6。[CI41446549940](https://github.com/z2823253773-p/mooneventeval/actions/runs/41446549940)的macOS arm64与Linux x86_64各完整17步成功：62 MoonBit、29根Python、42验证、16 CLI，1620真实产品调用、38文件包/解包/包外消费及13产品/4原版回放。244源码hash一致并逐项绑定公开Git，各8192基础产物及35演示文件保存核验。
- 本地开发probe56项通过；三个可编译mutation（跳过拒绝、原始token比较、空键预览）均由行为测试杀死，未把编译失败当mutation成功。
- 独立生成500案例：410无重名输入与基线stdout/stderr/退出码一致，90重名输入的首冲突键、偏移与预览均正确；另8字节/深度/错误优先级边界通过。作者另复跑原脚本，日志明确为author-replay，不把它当第二次独立评审。
- CI后的首页链接/状态/计划更新不是新的全量CI；该README另做38文件源码包复验，见metadata.zip。

## 离线复核

完整Git克隆中使用Python >=3.12和Git运行，无需工具链、原版参考环境或网络：

```sh
python3 evidence/P6/verify.py
```

检查冻结文件SHA256、ZIP大小/路径/CRC、run/jobs、实际完整门和流哈希、所有基础产物、13+4回放、两平台源码库存及其公开Git内容；并检查三项mutation及最终probe结果。使用显式失败检查，不依赖assert。

| 归档 | 内容 |
|---|---|
| local.zip | 初候选、文档修订和最终提交的本地完整门；RED/GREEN、真实CLI、probe、mutation、独立原报告与原脚本、作者回放及当时ledger |
| remote.zip | 本轮两平台实际下载的CI产物，不改写报告 |
| metadata.zip | 首页CI入口更新后的38文件源码包独立复验 |

归档字节数/成员数/hash见archives.json；最终证据由SHA256SUMS.json锁定。独立原脚本需在隔离目录内布置原始两版本及编译产物后运行，limits.py会在cwd写edge.json；不是可以在任意目录无准备运行的产品命令。日志保留生产路径。

本轮没有注册表发布、真实用户采用或官方验收回执声明，旧冻结阶段不修改。
