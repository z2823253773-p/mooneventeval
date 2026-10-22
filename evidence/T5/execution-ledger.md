# SDD ledger — plan: docs/superpowers/plans/tasks/T5-cli-demo.md

Base: 41890b84505e790efef6c2f981512af04539a51e
Task5 IN_PROGRESS. Existing isolated branch spike/t0-feasibility, clean baseline49. User continues previously approved plan/PRD; T5 card's historical 修订待审 is superseded for this stage only. No reinstall/new worktree/remote/TSV.
Pre-flight: cli consumes T3 decode/evaluate/error and T4 explain/four renderers; signatures available, EvalError construction public. Native uses T0 synchronous #borrow and local toolchain. No semantic core changes needed.
Ruling: parse_args receives argv excluding executable; only standalone --help/--version are Help/Version, per CLI convention. Command first/path second, strict later option pairs. Pre-scan --format to retain valid JSON error mode, but duplicate/invalid format forces Text — prevents syntax errors losing requested machine protocol; cost if wrong: parser interface/convention mismatch, covered by unit/process tests.
Ruling: JSON errors stdout only, text errors stderr only; text diagnostic prints stable code plus JSON-quoted fixed error message, not raw path/identity. Successful payload receives exactly one final LF, and the CLI checks the framed UTF8 byte cap too — cost if wrong: protocol/terminal safety or a one-byte cap overrun.
Ruling: close is attempted once on every acquired FD (do not retry ambiguous EINTR close); primary read/resource errors retained, close failure after success becomes FILE_ERROR2. SIGPIPE ignored explicitly so EPIPE is reported with nonzero exit rather than claiming completed. Heavy injected faults remain T6, and no untested path is called verified — cost if wrong: FD leak, missed failure or unbounded process; native/process tests cover ordinary paths.

Task5 tests: missing APIs/native target RED diagnostics, 4 args GREEN; corrected invalid test fixture (labels cannot be empty) without changing product. Dash-prefixed/reserved-option IDs showed behavioral RED and GREEN; parser prescan now skips consumed ID values. Formatter needs second pass for initial comment spacing; no warning suppression (explicit Eq extension, Unicode String NUL syntax).
Ruling: all legal query IDs, including --format, remain queryable as option values; file-leading -- uses ./ spelling because no new -- separator is introduced — avoids an inaccessible legal event and preserves strict grammar; cost if wrong: option ambiguity, covered by reserved-ID unit/process tests.
Task5 native repeated close evidence runs actual whitebox under RLIMIT_NOFILE64 (host soft limit was1048575, so plain20000 iterations alone would not prove leak detection). Native test protocol checked,2/2; full Moon56, Python4, validation29, CLI9 tests (35 normal captures plus two pipe scenarios),46 raw-byte regressions and10 demo commands pass. >64KiB Unicode reports parse intact, partial pipe records1024-byte prefix/exit2. Heavy injected EINTR/short-write/close failures and personal M2 remain pending.

Final: Important1 accepted; unknown option value swallowed valid format. args_format_prescan_respects_unknown_option_values + real-process subtests RED→GREEN; no relaxed rejection. Full Moon57/Python4/validation29/CLI10,45 normal captures+2 pipes,46 byte regressions,64FD20000 reads,10 demo calls all pass. Reviewer original42 cases replay42/42 by author, not independent re-review. Final code/tested2c0a06d.
Final: Ruling: EINTR注入：循环已实现，注入验证留T6；误当覆盖会漏重试/中断缺陷。
Final: Ruling: 短读/短写/零写/close失败注入：分支存在，大输出和断管仅覆盖实际路径，其余留T6；误当通过会漏FD/部分写错误。
Final: Ruling: close(EINTR)跨平台语义：保留不重试策略以避免双重关闭，只验证macOS普通路径；不能据此保证移植。
Final: Ruling: CLI带LF精确16MiB落点：代码检查最终bytes，复用renderer等号/+1测试，但未构造真实CLI恰好落点；不能称全链该边界已测。
Final: Ruling: 非UTF8 OS argv/文件名：当前使用MoonBit String argv，无原始字节路径接口；误扩展承诺会遇编码/路径身份问题。
Final: Ruling: OS argv的NUL：exec无法传入，原生函数白盒实际拒绝；不能伪称真实进程携带NUL成功测试。
Final: Ruling: OOM/强杀/signal初始化失败等灾难：未注入，普通输入/I/O错误及typed退出映射已测；不能保证所有外部致命事件exit4。
Final: Ruling: 并发写普通文件/特殊文件系统：只承诺只读有界读取，不承诺快照事务；竞争修改可能得到非一致输入或输入错误。
Final: Ruling: 输出失败前缀：允许已写前缀，两个真实断管场景必须非零；调用者须检查退出码，不能把前缀当完整结果。
Final: Ruling: Linux/CI/安装/消费者/包/发布/赛事资格：分阶段未证明，不从本机结果外推可移植性/资格。
Final: Ruling: 本人推导/讲解/视频/M2：未发生，自动稿和收据不能替代；T5个人门槛仍未完成。
Final: Ruling: 最终A11/完整数学重审：核心未改和46历史字节回归不等于重新完成数学/原版全量验收，留T6。
Final: Ruling: 重名键last-wins、无TSV/CSV/stdin、./文件名、独立help/version：沿用已披露范围，不能被误读为通用导入或所有命令别名。
Final: Ruling: atime等读取副作用：只保证不覆盖内容，不承诺文件系统元数据零变化；不能当法证读取保证。
Final: minor (deferred): none. Machine implementation complete and tested; personal T5 step7/M2 NOT_PERFORMED, no task-done marker claiming the full human-containing task complete. This is an explicit remaining acceptance condition, not silently deleted. No merge/push/publish.
