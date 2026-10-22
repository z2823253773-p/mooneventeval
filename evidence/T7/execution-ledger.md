# SDD ledger — plan: docs/superpowers/plans/tasks/T7-package.md
Base: 914cffd301d40eff8f4b2ecd697adb5052ebb031
Task7 IN_PROGRESS; user 继续 authorizes the existing T7 local candidate plan. Existing isolated worktree reused, baseline Moon58/58, clean. No network/install/remote/publish/clinical access.
Pre-flight: T6 public eventeval API -> external module path dependency; opaque fields accessible only through factories/metrics/report. Archive must include C stub, modules, API/docs/examples/local installer+lock, exclude probes/plans/logs/venvs/toolchains. Package listing not consumer proof: unzip into separate temporary module and build/run there.
Ruling: use MIT with Hengrui Zhang from current repository commit author identity (no email in distributed attribution), retain Apache-2.0 core notice/license separately; no copied sed_eval product code or redistributed reference environment — matches approved MIT recommendation and actual local attribution/source inspection — cost if wrong: attribution/license correction before any publication.
Ruling: modern moon.mod uses module import and temporary moon.work members for local dependency resolution, replacing the planned old path-deps encoding — official module docs and locked parser reject the old deps syntax; public consumer still a separate temp module, no registry/network — cost if wrong: workspace resolution might accidentally mask absent archive dependencies, constrained by unpack-only source paths and recorded workspace members.
Task7 first GREEN: public consumer succeeds, wrong expected TP2 builds then behavior fails;38-member actual archive/source hashes match, fresh unpacked external consumer and extracted-wrapper native CLI build +6 README calls pass. Python11/11, Moon58/58, fmt-check/info pass. Initial old deps syntax, main raise requirement, workspace artifact path, list stderr framing and unsupported info flag failures preserved; corrected by direct tool evidence. No product/runtime/API changes.
Task 7: complete (commits 914cffd..a441ce8, tests: python3 scripts/package_candidate.py --output evidence/T7/package-task-done → {"passed": true, "members": 38, "published": false})
Task 7: complete (commits 914cffd..bb24ce3, tests: python3 scripts/package_candidate.py --output evidence/T7/package-task-done-final → {"passed": true, "members": 38, "published": false})

Final: sole reviewer 0 Critical /1 Important /0 Minor on a441ce89; grade I1 Important accepted. Final: fixed I1 explanation status false-green — test_failed_explanation_never_qualifies_package actual compiled serializer mutation RED→GREEN, full Python12/12 and Moon58/58, ordinary consumer/archive/unpack/docs green on bb24ce33. Original replay script final external-temp run rejects compiled failed explanation with gate1/replay0 and failed ledger; first nested-ignored-source replay was invalid/exit2 and not counted. No second independent review.
Final: Ruling: 远端CI/正式namespace与URL/注册表发布/赛事资格留待后续授权 — 当前只交付本地候选，未取得对应外部实证 — 若外推会误报远端交付或参赛资格.
Final: Ruling: 新下载安装及其他平台不记作完成 — 实测复用已装锁定工具链，仅Darwin arm64 — 若外推会漏安装链或跨平台故障.
Final: Ruling: 不把T7回归说成全部评分/资源/OS故障重新认证 — 运行源码与接口未改，T6限定证据继续单独有效 — 若误判会漏未采样输入或竞态.
Final: Ruling: 本人M2及真实外部用户反馈继续单列未完成 — 没有对应人工作业或反馈证据 — 若混淆会伪造个人/用户验收.
Final: Ruling: 署名只依据现有Git身份，许可材料核对不是法律结论 — 候选MIT及core声明与实际材料一致，未独立证明权利来源 — 若身份或权利不符，公开前须纠正.
Final: Ruling: 不宣称穷尽每个报告字段或未来文档变体的mutation — 本轮实际完成状态字段反例修复及有限回归 — 其他字段的新回归仍可能漏检.
Final: Ruling: 后续作者修复和冻结不冒称独立复审 — 独立评审只绑定a441ce89，作者单轮测试绑定bb24ce33 — 若表述不清会夸大独立保证.
Final: no new minor (deferred); inherited T6 M1 remains explicitly deferred and is not repaired or claimed repaired here. Branch/worktree preserved, no merge/push/publication. T8 next.
