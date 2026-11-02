# P5：MoonBit 接入示例与开源开发入口

计划：docs/superpowers/plans/2026-11-02-moonbit-integration.md。
基线原始 HEAD：7171015a0c269eb057839fe99def33378c82ac8d。
基线公开 HEAD：7fed24dec8f7fda7a89b0fd2e02fe2ac54e30501。

- 基线 native 测试：58/58，exit 0，baseline/native-tests.log。
- RED：新增真实独立模块集成测试，示例缺失时报明确断言失败，exit 1，red.log。第一次命令因目录尚未创建而报错，随后将缺失模块检查写成断言，未把该报错当行为失败证据。
- 决定：复用现有 API；本轮不改变 JSON/评分/CLI 语义、包名或源码包白名单。示例属于完整仓库的开发接入演示。
- 待完成：示例编译/行为、文档、统一门、独立评审、远端 CI 与最终记录。

- Task 1 complete：原始实测f75963024，公开实测b06207ae9；本地完整17步及13/4回放通过。CI41434748035双平台各同门通过，243源码hash逐项绑定公开Git。
- 独立评审：初候选ff728dc0e，0 Critical / 1 Important / 0 Minor；作者修复遗漏的历史还原文档，并以新克隆复现缺失→恢复的真实行为，再运行最终完整门。未二次独立复审。
- 首页CI链接更新后单独源码包复验PASS，38成员；不冒称元数据HEAD通过完整CI。
- 原始/远端产物原样ZIP归档；自动复核器检查字节、退出码、Git来源，冻结后不覆盖。
- 阶段决策未改变评分或产品接口；无延期Minor。
