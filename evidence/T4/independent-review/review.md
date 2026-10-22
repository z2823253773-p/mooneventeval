# T4 independent read-only review

Base: `9886ce1d9c1390d298c9f34d77d7185ec3e4b043`  
Head: `d528d30b3e8b1feaea801c2058ec310206f78b65`  
Reviewed checkout: `/Users/henryz/Desktop/比赛/mooneventeval-t0`  
Rerun workspace: `/private/tmp/mooneventeval-t4-review-sxuadgmt/source`, extracted by `git archive` at the exact head. This is the one requested independent review; no subagents or product fixes were used.

## Strengths

- `eventeval/explain.mbt:20-52` confines lookup to the requested recording and side and calls the existing `eligibility` directly. `evaluation.mbt:63,98` uses that same function. No matching call, counts, or selected-pair inference enters explanations. Missing IDs return the specified paths and `ID_NOT_FOUND`.
- `eventeval/model.mbt:195-201` keeps every PairExplanation field private, and the generated public interface has no construction or budget escape hatch. Existing Task factories copy and validate input before this API is reachable.
- `eventeval/report_text.mbt:16-86` renders every external identity through `text_identity`, retains signed exact time values, uses “所选配对”/“未定义”, distinguishes candidate-free from unselected candidates, and explains the limits of that inference. `serialization.mbt:36-54` preserves JSON-decodable identity while escaping C0/DEL/C1 and the specified line/direction controls, including U+061C.
- `report_json.mbt:166,230` and `report_text.mbt:71,86` all route final output into `serialization.mbt:24-30`. The gate measures UTF-8 bytes and accepts equality. The shared gate's exact 16 MiB/+1 tests, small UTF-8/escape tests, and actual legal 2000-event capacity test all passed on my rerun. The test-only JSON adapter does not create a public knob or a second production serializer.
- Original JSON encoding and error structure remain intact in the inspected diff. My additional binary-mode comparison confirmed all 46 archived T3 reports are actually byte-identical with this native candidate; this confirmation does not depend on the flawed text-mode check described below.

## Issues

### Critical (Must Fix)

None found.

### Important (Should Fix)

1. **[P2] Preserve raw process bytes before hashing, archiving, or checking byte stability.**
   - Location: `validation/check_reports.py:33-36`, also the comparison at line 44.
   - `subprocess.run(..., text=True)` performs universal-newline conversion before the script sees stdout/stderr. `write_text`, `stdout.encode()` hashing and `read_text()` baseline comparison consequently operate on normalized text. A real CR or CRLF can be replaced with LF before the unsafe-control scan too. These files and hashes cannot support the stated raw-output and exact-byte claims.
   - Reproduction: `crlf-probe.py` calls the unchanged compiled probe and changes each stdout LF to CRLF. `byte-audit.py` first establishes different real byte streams (`real.stdout` versus `mutant.stdout`) and then runs the unchanged checker against the wrapper. The checker still exits **0**, reporting **46 byte regressions, 122 explanations, 44 identity cases, 430 process runs, passed=true**. See `byte-audit.json`, `crlf-checker.stdout`, and `crlf-accepted/report.json`. This is a demonstrated false green, not a hypothetical platform issue.
   - Effect: a line-ending byte regression or raw CR in text can be silently normalized out, and archived stdout plus its digest no longer prove the bytes actually emitted. The current production candidate itself passed my separate raw-byte baseline check; this finding concerns the required verification/archival implementation.
   - Fix: capture binary stdout/stderr; write and hash those bytes directly; compare evaluation bytes to `read_bytes()` baselines. Decode a separate UTF-8 copy strictly for JSON/text semantic checks, without newline translation. Add a negative test that rejects the CRLF-changing wrapper (and preferably a raw-CR case) and verify preserved artifact bytes/hashes. Regenerate the final renderer evidence after the author's single RED→GREEN repair.

### Minor (Nice to Have)

None recorded.

## Recommendations

Make the one focused checker/archival repair and rerun its negative regression, the real renderer suite, and appropriate regressions. Do not change otherwise-correct report serialization merely to address this validation flaw. Final evidence should distinguish the product source SHA, validation-script SHA, built binary hash and immutable raw-output hashes. No further independent review is requested by this report.

## Verification performed by this reviewer

Exact commands, working directories, exit codes, timing and log paths are in `commands.json`; `replay.py` replays them. The copied `.tools` and `.venv-reference` entries are symlinks to the already-installed locked local dependencies; no installation or network access was performed. Python bytecode writing was disabled. The checker only reads the original git directory to label the archived source's verified head.

- Locked native Moon suite: **49/49**, exit 0. This includes the 16,777,216-byte equality and 16,777,217 rejection and the 2000-event sample: JSON **4,015,857** bytes, text **11,023,901** bytes, TP 1000, steps 3000.
- Original Python tests: **4/4**, exit 0. Validation tests: **29/29**, exit 0.
- Native release probe build: exit 0.
- Existing T4 renderer checker: **430** runs, exit 0 (its text-normalization limitation is the Important finding).
- Original argv checks: **56**, exit 0. Original JSON control-character checks: **64**, exit 0.
- Reviewer-added binary capture/comparison: **46/46** original T3 outputs byte-identical, saved under `byte-audit/`.
- Reviewer-added CRLF mutation: altered output is demonstrably different, yet the current checker returns exit 0 / 430 passed. This is an expected failure of the verifier acceptance criterion, retained in full.

I also inspected the author's five `*committed*.json` receipts and verified their log hashes, the renderer source hashes against the exact archive, and the original binary hash against the stated receipt. Those copied receipts are in `author-receipts/`. Historical RED/GREEN runs and author chronology were not independently reproduced; the reruns above provide present-state evidence. I did not rerun original sed_eval parity, packaging, full performance profiling or remote CI.

All execution and created files for this review stayed in the temporary directory. The original HEAD stayed at the supplied head, and the review issued no checkout/index/branch writes. The before/after original status snapshots differ only by new untracked author closeout artifacts created concurrently; this report does not claim that the entire directory was globally frozen.

## Declined to judge

- Product file CLI, unreadable-file handling and other T5/T6 A9 I/O paths: explicitly future tasks; the current argv probe is a development adapter, not a promised file CLI.
- Full A11 sed_eval parity, user M2/personal explanation, demo, package consumer, remote CI, publishing and competition eligibility: separate future or personal acceptance gates, not T4 completion criteria; no such completion is asserted here.
- A legal 2000-event task landing exactly on the 16 MiB report limit: the approved T4 rule explicitly permits internal exact-byte boundary construction plus a separate legal-capacity sample; these tests exercise the real shared production gate.
- Arbitrary `Int64::MIN` or arbitrary decimal precision passed to `format_scaled_seconds`: the helper is private, and all production callers are validated, bounded values with 6 or 12 digits. I did not require a general-purpose formatting API outside those invariants.
- Requiring candidate degree fields on selected JSON matches from the task card's shorthand: the frozen contract and PRD define selected matches with events/basis and candidate_count on FP/FN; adding fields would violate the frozen schema. I judged the explicit schema.
- Confusable ordinary Unicode, combining marks, all invisible format code points beyond the specified terminal/line/direction hazards, and terminal-specific rendering behavior: the accepted rule preserves readable ordinary Unicode and exact identity, not a universal anti-spoofing normalization scheme. No broader rendering-safety guarantee was assessed.
- Universal wall-clock, peak-memory, cross-platform or whole-legal-input performance guarantees: not claimed by the current native sample evidence and not established by a final byte cap.
- In-progress task/state/manifest checkboxes awaiting this review's outcome: expressly scheduled for the author's final closeout; I did not treat their pending state as a completed-work misrepresentation or a missing T4 feature.

## Assessment

**Ready to merge? With fixes.**

**T4可验收？当前还不能最终验收；完成上述唯一 Important 的验证器修复及作者单轮 RED→GREEN 复验后，可据更新证据收尾。** 产品渲染/解释实现与所读 T4 契约一致，未发现产品行为错误；目前阻断的是已复现的“改写原始字节后仍宣称逐字节检查通过”证据缺陷。Critical 0 / Important 1 / Minor 0。
