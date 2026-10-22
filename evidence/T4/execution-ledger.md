# SDD ledger — plan: docs/superpowers/plans/tasks/T4-reports.md

Base: 9886ce1d9c1390d298c9f34d77d7185ec3e4b043
Task4 IN_PROGRESS; reuse clean named isolated worktree, local pinned toolchain/reference environment. No install, remote, main change or new user chat.
Pre-flight: T1 eligibility supplies both graph and explanation; T3 Task/Event/Config private canonical state feeds lookup; Evaluation already has full selected/unmatched/candidate-degree/basis data. T4 must preserve existing evaluation JSON bytes and error serializer. No public budget parameter or schema expansion.
Ruling: user's 继续 authorizes T4 only. Rename package-private decimal_string to planned format_scaled_seconds and keep its existing unquoted canonical semantics; task snippet's extra quotes are a plan typo, JSON quoting remains the separate standard encoder. Cost if wrong: double quoting/changed time values, caught by full-report parity and literal formatting tests.
Ruling: preserve fixed JSON writer and share bounded_output with bounded_serialize(Json, limit); do not parse/re-serialize whole reports merely to apply a byte limit. All four public report/explanation renderers enforce the same final UTF8 16MiB cap, test limits remain internal. Cost if wrong: output/order drift or false byte-limit evidence.
Ruling: text identities are JSON-quoted and additionally escape DEL/C1, Unicode line separators and directional/format controls that could forge terminal lines; normal non-ASCII text remains readable and the quoted identity JSON-decodes to exactly the original value. Development probe gains report-text/explain-json/explain-text modes solely to exercise public functions externally; original one-argument evaluation remains. Cost if wrong: unsafe/altered display identity or developer-probe compatibility regression; process checks cover both.

Ruling: bounded_serialize(Json,limit) is a whitebox-only adapter around the real common bounded_output gate, placed in serialization_wbtest; product reports already have explicit fixed-order strings and should not be parsed/re-serialized or carry unused runtime test helpers. T5 consumes public renderers, not this helper. Cost if wrong: internal helper placement differs from the card, while exact final-byte behavior still needs actual renderer routing and regression proof.

Task4 RED target explain/text/serialization APIs missing; GREEN48, then capacity adds49th test. A native-probe-only output adaptation hit pinned syntax/missing print/deprecated StringView.to_string diagnostics; use println(trim_end(...).to_owned()) to preserve exactly one terminal LF, no C I/O expansion. First format check failed pinned formatter's initial-comment blank line; second fmt/check clean, no warning suppression.
Task4 author review added missing U+061C directional-mark escape: serialization_identity_quote_roundtrip_controls_and_direction RED→GREEN, full49. Tests include embedded NUL in typed explanation IDs. External candidate430 processes:46 old JSON byte regressions,122 pair bases vs Fraction oracle,44 identity cases and errors/repeat; original argv56 and JSONcontrols64 also pass.
Task4 capacity valid2000 events/1000recordings: JSON4015857 bytes, text11023901 bytes, TP1000, steps3000. Real16MiB exact/plus1 internal serialization tests pass. This is bounded-capacity evidence for prescribed samples, not a universal memory/time guarantee.
Task 4: complete (commits 9886ce1..d528d30, tests: scripts/with-toolchain.sh moon test eventeval --target native --deny-warn → Total tests: 49, passed: 49, failed: 0.)

Final review: Critical0/Important1/Minor0 at d528d30. Important raw-byte verifier finding accepted; author two-mutant RED confirms false-green and altered archives, GREEN rejects CRLF JSON and raw-CR text and preserves their exact bytes. Strict UTF8 decoding is separate from raw capture/hash/comparison; product source unchanged. Full final suite pending. No second review.
Task 4: complete (commits 9886ce1..d00b0a6, tests: scripts/with-toolchain.sh moon test eventeval --target native --deny-warn → Total tests: 49, passed: 49, failed: 0.)

Final: fixed Important raw-byte capture — check_report_bytes CRLF/raw-CR RED→GREEN2/2, native49/49, Python4/4, validation29/29, real renderer430/430. Final verifier/tested d00b0a6, product source d528d30 unchanged. No second reviewer.
Final: Ruling: 文件CLI/不可读文件及其余A9 I/O：留T5/T6；当前只交付库函数与开发argv。若把probe当CLI会漏真实文件行为。
Final: Ruling: 最终A11、个人M2/demo、消费者/CI/发布/赛事资格：分阶段或本人条件，尚未完成；误当完成会造成验收/资格误报。
Final: Ruling: 合法2000事件恰好16MiB：不强造不可达任务；真实共同byte gate测16MiB等号/+1，另有合法容量例；不能外推全域内存/性能。
Final: Ruling: 私有格式函数的任意Int64::MIN/任意精度：仅支持经验证的范围及6/12位生产调用；将来扩大前置条件需新测试，否则可能溢出/误格式。
Final: Ruling: 所选JSON match不新增degree：冻结schema以事件/basis为准，候选数在FP/FN；擅加字段会破坏机器契约。
Final: Ruling: Unicode普通混淆/组合字和未列格式码点：保留精确身份及普通Unicode可读，仅承诺指定终端/分行/方向控制转义；不能称通用反欺骗。
Final: Ruling: 全域墙钟/峰值/跨平台性能：当前只有macOS规定样本，20M资源预算允许拒绝；不能保证所有合法图在预算内。
Final: Ruling: 未完成的状态/manifest交接：本次收尾更新并冻结快照；旧阶段证据只绑定当时源码，不哈希声称当前活动文档永不变。
Final: minor (deferred): none. T4 closed; T5 not started; no merge/push/publish.
