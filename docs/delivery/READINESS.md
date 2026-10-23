# MoonEventEval 交付准备与下一阶段

更新2026-10-22（America/Phoenix）。用户明确表示不自行验证，技术复测与交付检查由Codex负责；不再把用户重跑测试作为工程继续条件。

## 本轮完成

- [本地交付ZIP](../../evidence/P1/MoonEventEval-0.1.0-local.zip)：19文件，含本机Darwin arm64可执行文件、38文件源候选zip、三案例、原始JSON输出、许可、算法讲解和逐文件hash。
- [离线演示实录](../../evidence/P1/delivery/MoonEventEval-0.1.0-local/DEMO.html)：三案例、增广路径图、边界解释和失败协议；静态本地文档，无网页依赖/联网请求，不是在线评分功能或本人录屏。
- [技术事实提纲](../../evidence/P1/delivery/MoonEventEval-0.1.0-local/TECHNICAL_FACTS.md)是代理材料，不能假称本人原创申报书或实际答辩经历。
- [交付验收](../../evidence/P1/delivery-verified.json)：实际ZIP CRC/19成员、18文件hash、HTML结构/五份实际JSON逐项核对；ZIP解出binary后再运行三个案例，全部正确。此前本轮demo10条命令及复制binary的5条命令也通过。
- [产品身份](../../evidence/P1/delivery-report.json)：仍为最终被测8aa37c5的原样binary/源zip；本轮运行所在文档HEAD7dd8801e，不冒称又一次完整17步验收。T8冻结完整性本轮实际复核通过。

首次组装在HTML页标题处遇未定义变量，失败日志及部分材料留在evidence/P1/failed-attempt；修正后才形成最终ZIP。初次成功ZIP因随后补充本地路径披露而重新打包，最终ZIP再次解出并运行三个案例，不把旧hash当最终值。

视觉验证限制：两次浏览器setup超时；原生Chrome导航产生了有标题的离线标签页，但file协议被浏览器安全策略拒绝内容观察，没有取得可验收页面截图。临时仅loopback预览服务已关闭，不绕过该限制；HTML结构/内容已检查，视觉渲染未认证。该限制由代理记录，不要求用户补测。

文本与源zip未发现本机绝对路径；原生binary含编译时路径，所以这是本地候选，未完成公开脱敏。原始内部证据/提交历史也不冒称公开安全版本。

## M2用语更正

[PRD里程碑](../superpowers/specs/2026-10-20-mooneventeval-prd-design.md)将M2定义为时间解析、候选、最大匹配通过A1–A3/小图穷举，以及可复现参考环境和首轮共有语义结果；这些机器条件已有T1–T3/T6/T8证据，M2最小核心已完成。历史状态把它和本人讲解合称“本人M2”，现显式作废该混用。

T5步骤7的代理演示和材料完成；用户现取消本地人工复测条件。没有本人讲解证据仍如实记录，但不是另一个未通过的M2，也不阻止代理继续工程。

## 公开要求核对

本轮读到的[官方官网源码](https://raw.githubusercontent.com/moonbitlang/Hackathon2026/main/src/App.tsx)写明：十月31日为报名/验收日期；提交需公开仓库与一页说明；开发记录可追踪，MoonBit为主，具有运行示例、测试和许可来源；允许AI辅助，参赛者仍须掌握技术路径并承担质量责任。已读文本未明确要求本人纸笔算例、亲手复测或录制本人视频，不能把内部选择的验收形式冒充强制条款。

[正式章程](https://bxup9uklfcb.feishu.cn/wiki/Dx4Bwd6D1i3GfHkajQCcF7SznEd)正文仍未取得；具体截止时区/时刻、个案换题是否认可、剩余提交次数、正式包发布要求均未确认。公开源码不是组委会对本项目的接受证明。见[本轮来源记录](../../evidence/P1/rules-check.json)。

## 下一阶段：真实远端CI

已只读确认连接器账号为z2823253773-p，拟先创建私有z2823253773-p/mooneventeval，推送现有代码/测试证据与真实Git历史，再手动运行已保存双平台workflow并检查结果。连接器可见仓库列表为空，不证明目标名绝对可用；实际创建前另核对CLI账号和仓库冲突。

本轮尚未创建/推送/触发CI/改为公开/发包/报名。需要用户明确授权的仅这一步远端操作，原因是[AGENTS](../../AGENTS.md)现有约定要求明确授权。先私有，是因为原始证据/Git元数据和native binary尚未做公开脱敏；远端验证成功也不自动改变公开性或正式发布。

后续执行先读PROJECT_STATE、contracts、本文件；保留冻结T8和原main，远端结果记录确切代码SHA/run URL/各OS，不用配置或本机通过代替远端结果。
