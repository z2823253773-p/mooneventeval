P4最新（2026-10-27）：评审风险再查与作者修订完成；三个合成工作流程已公开，CLI核心/schema不变。原始候选06ec1649b、远端被测e106a5d47，[双平台run40467323131](https://github.com/z2823253773-p/mooneventeval/actions/runs/40467323131)各17步+13产品/4原版演示通过；参考风险见[REVIEW_RISKS](delivery/REVIEW_RISKS.md)。正式申报写作、真实采用、个案资格仍不是代理可认证事项；未代提交。后续元数据HEAD不冒称重跑完整CI。

# MoonEventEval 当前交接

更新2026-10-26。**P3修订完成：用户已提供初审退回通知；输出和sed_eval范围按[REVIEW_REVISION](delivery/REVIEW_REVISION.md)修订，[新CI](https://github.com/z2823253773-p/mooneventeval/actions/runs/40447392163)在a613579b6双平台通过17步及8+4演示；原始本地074509f2。本代理未重新提交报名，不能把技术通过当作复审通过。**

以下P2为历史交付：**P2已获直接授权并完成仓库公开；最新入口为[PUBLIC_RELEASE](delivery/PUBLIC_RELEASE.md)。匿名Git访问通过，公开后run39925966715两OS各17步成功，各8144产物下载复验。** 用户将技术验证交由Codex，PRD M2机器门已完成，无需用户自行复测。最新结果以[REMOTE_CI](delivery/REMOTE_CI.md)和[PROJECT_STATE](PROJECT_STATE.md)为准。

私有仓库：https://github.com/z2823253773-p/mooneventeval；[实际双平台CI](https://github.com/z2823253773-p/mooneventeval/actions/runs/39914869650)成功，实际被测导出SHA`c1e74f58b495e8bf83986715f57d6d8f3bff76bd`对应原始作者代码`69f544fdcfd6bdd13bff273279da7dd5fdfc56d6`。各OS17/17、58 Moon/28 Python/42验证/15CLI、1620产品调用及38文件包/解包消费通过；新安装和Linux实跑已有证据。两OS204源码hash一致，各8144产物hash下载复核通过。

原始分支spike/t0-feasibility与导出main均保留，本地原main8a307552不变。独立导出图只移除一个超大原始日志路径，完整原始历史bundle在CI校验还原；不force push、不改写原始历史、不把映射SHA冒充原始SHA。源码及后续文档提交和实际CI被测SHA分开。

[P1交付包及原样本机程序](delivery/READINESS.md)仍是其历史身份；binary含构建路径，仅作本地候选。视觉核验受file协议策略限制未认证。正式公开候选不直接拿全部原始证据/历史或本机binary公开。

独立克隆先运行`python3 evidence/R1-provenance/restore.py`导入锁定原始作者Git对象，不依赖本机缓存；产品和CI被测提交不变。后续复核：`python3 evidence/R1/freeze.py`、`python3 evidence/R1/verify_remote.py --check-only`。新总门用干净已提交根、新证据目录；不要覆盖冻结阶段。当前授权范围已完成，保持私有；正式namespace/Mooncakes/公开/报名/个案资格与本人理解无新增完成证明。NUL CLI选择和timeout部分取证Minor保留，TSV等仍BACKLOG。不得按旧状态要求用户补做本地验证。
