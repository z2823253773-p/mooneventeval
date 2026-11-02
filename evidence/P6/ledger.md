# P6：拒绝同对象JSON重名键

计划：docs/superpowers/plans/2026-11-02-duplicate-json-keys.md。
基线原始5b7dfafe6 / 公开e8caf55a2，工作树干净；基线native58通过。

- 用户授权按建议继续推进；本阶段将旧last-wins明确收紧为DUPLICATE_KEY，先改契约v3，不改变typed API、数学规则或正常输出。
- RED：4项API测试中2失败，旧实现接受重复/转义等价键；真实CLI四个输入均错误exit0。见red.log及cli-red。
- 编译过程遇目标版if作为加法操作数语法不接受、substring与StringView.to_string弃用；保留compile-first/substring/stringview日志，改为正常if赋值与to_owned，不扩展warning豁免。
- GREEN：4项API与真实CLI反例通过；开发probe56个进程检查通过。两项可编译mutation均被行为测试杀死：跳过拒绝、比较原始token而不解码。
- 已决定：标准JSON语法/深度优先于键检查，键检查优先于schema；path为$，message安全截断预览和BOM剥离后的零基UTF16位置。候选尚未发布，保持0.1.0候选身份，以输入契约v3/Git SHA明确此收紧。
- 待完成：完整门、独立评审、实际双平台CI、证据归档与交接。

- Task 1 complete：原始最终实测7c46e8316，公开最终实测2a007a352。初候选3ce和文档修订4d96的完整17步分别保留；最终提交62/29/42/16、1620产品调用、38文件源码包及13/4演示均通过。
- 评审0 Critical / 1 Important / 1 Minor；当前定位文档已改，预览测试已加精确断言。第三个可编译空预览mutation被新测试杀死；未二次独立复审。
- 评审500差分与8边界，作者复跑原脚本通过。limits脚本使用cwd写edge.json，作者回放产生的临时输入已移入本轮证据，没有保留在仓库根目录。
- CI41446549940双平台成功；244源码hash和各8192基础产物已下载逐项核验。首页CI链接更新后的38成员包单独复验通过；后续元数据不冒称新的完整CI。
- 下一阶段薄TSV输入契约/公开数据流程，继续沿用用户已授权方向；正式注册表发布仍是独立动作。
