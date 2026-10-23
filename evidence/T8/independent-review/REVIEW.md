# MoonEventEval T8 and whole-branch independent review

Candidate: `df2142688e991c244cae0a94623ccf8acf55f257`.
T8 base: `7f325643cf12d3cab5a60f9808af3ec94d11caed`.
Whole-branch base: `8a3075521312c9bf9ad196309422adaa0c67fbd2`.
Original checkout: `/Users/henryz/Desktop/比赛/mooneventeval-t0` (read only).
Review copy: `/private/tmp/mooneventeval-review-available/checkout`.

This is the bounded replacement for the unavailable strongest-model review seat. No other reviewer or subagent was dispatched by this reviewer. No fixes were implemented. Later author fixes or closeout commits are not independently reviewed by this report.

## Strengths

- Maximum matching uses a first-free fast path followed by complete iterative augmenting DFS, with full backward path rewrites and one-to-one owner arrays (`eventeval/matching.mbt:56-132`). Budget is consumed before each charged operation and is shared across groups; errors return no partial Evaluation. Current native tests exercise all 689 graphs up to 3×3, 64 larger seeded graphs, augmenting chains, dense cases and budget boundaries.
- Eligibility is a single shared function for evaluation and explanations (`eventeval/eligibility.mbt:5`, `eventeval/evaluation.mbt:63`, `eventeval/explain.mbt:49`). Decimal syntax/range checks avoid unbounded accumulation; the largest scaled comparison is 2,592,000,000,000,000,000, within Int64. Identifier validation checks surrogate pairing and codepoint limits before sorting. Micro metrics pool counts, and the reference adapter keeps raw substitution accounting separate from the explicitly named projection.
- Native borrowed pointers are synchronous, never retained/freed; requests are bounded before converting ssize_t; short I/O and EINTR are handled, opened FDs are closed once, FIFO/device inputs are rejected, and SIGPIPE becomes an ordinary output failure. Current CLI tests include large Unicode output, partial pipe failure and input limits. Historical source-fault injection proof remains separately labeled.
- T8 checks actual cwd/Git root and clean committed source; compares pinned archives and 1,384 installed archive-member regular files; verifies the built executable; requires both successful processes and expected artifact reports; refuses empty/skipped suites; detects source mutation; and binds actual source, binary and archive hashes. Packaging independently compiles/runs a public API consumer, validates all 38 archive members against source bytes, then builds/runs the unpacked CLI and documented examples.
- CI is manually dispatched with read-only contents permission, full-SHA Action pins, architecture assertions and the same full verifier command. The configuration and documentation clearly distinguish saved CI configuration from an actual remote run.

## Issues

### Critical (Must Fix)

None found.

### Important (Should Fix)

**I1 — Verified reference source can execute different cached Python code.**

Locations: `validation/sed_reference.py:19-26`; `scripts/verify.py:164-173` and `scripts/verify.py:191-203`.

The adapter verifies the 12 `.py` files, then imports them through the normal Python loader. The reference identity probe also imports `sed_eval` using normal inherited import/cache behavior. Python can execute a timestamp-valid `.pyc` whose bytecode differs from the verified `.py`; Python/package versions and the interpreter hash do not detect this. Thus `sed_eval_source_verified=true` does not establish that the reference code actually executed is the original source that was checked. This matters because the original independent reference is a central acceptance claim, and cached code can survive source restoration or be selected through an inherited Python import path.

Reproduction, wholly isolated from the original venv: `reference_pyc_probe.py` copies the original sed_eval source package to an audit fixture, keeps every source byte unchanged, and creates one timestamp-valid `__init__.pyc` that substitutes a collar of 1000. The exact `verify.reference_probe_code` exits 0, verifies all pinned package versions, and reports source verification true. `sed_reference.evaluate_document` then returns TP=1 for reference [1,2], prediction [3,4], collar 0.2, ratio 0.5; the exact rule gives TP=0. Both subprocesses have raw streams/argv/cwd/environment/exit/hash receipts in `reference-pyc-probe/identity/` and `reference-pyc-probe/scoring/`. `PYTHONDONTWRITEBYTECODE=1` was set, demonstrating that disabling writes alone does not prevent cache reads.

This is an identity-gate counterexample, not evidence that the actual original venv was modified, and not a claim that all 324 qualification cases would pass this deliberately broad mutation. The fresh unmodified full gate passed.

Fix direction: execute reference subprocesses with controlled import paths and a fresh per-run pycache prefix (or another mechanism that guarantees execution of the verified source rather than preexisting bytecode). Apply the same policy to identity, validation tests and qualification. Add this cached-bytecode negative control; `-B` alone is insufficient.

### Minor (Nice to Have)

**M1 — The CLI-addressable identifier domain is narrower than the accepted JSON/API domain.**

Locations: `eventeval/model.mbt:31-65`; `cli/args.mbt:106-118`; `README.md:42-51` and `README.md:68-73`.

A JSON event or recording ID containing U+0000 is accepted as valid Unicode. Evaluation succeeds and preserves the ID. `explain-pair` treats selectors as literal argv strings: OS argv cannot contain NUL, and a literal `r\u0000` selects a different ID and returns ID_NOT_FOUND. The public API can represent this string; this is a narrow CLI addressability limitation, not invalid schema, invalid matching, or a score error.

Reproduction: `nul_id_probe.py`; input and exact process receipts under `nul-id-probe/`. Evaluate exits 0 with TP1 for reference ID `r` followed by NUL; the raw selector is rejected by the host before spawn (correctly recorded as no process/exit), while the literal escaped selector actually runs and exits 2/ID_NOT_FOUND.

Resolve deliberately: document the CLI subset and available library path, or add an explicit escaped selector mechanism. Do not silently reject or reinterpret currently valid JSON/API IDs as an incidental fix. Severity is Minor because only an unusual identifier prevents CLI explanation; evaluation and the library remain usable.

## Fresh verification and evidence scope

- One full run only: `python3 scripts/verify.py --mode local --evidence /private/tmp/mooneventeval-review-available/full-verifier`, cwd review copy. Exit 0, 17 steps, 41.88 s. 58 MoonBit / 22 Python / 41 validation / 15 CLI tests; 324 qualification bases + 1,296 transforms = 1,620 real product calls; 38-member archive. `full-verifier.receipt.json`, raw top-level streams and per-step/artifact receipts are preserved.
- The independent build's actual SHA256 is `8644fcc90426bfb89343e6855f54dc087cd904d2859f5d0884f686918877bb80`. Binary identity is taken from this run's report, not assumed equal to an author's build in another path.
- Seven fresh bounded rejection controls passed: wrong cwd, dirty committed source requirement, source mutation after three actual successful steps, corrupt installed compiler mirror against real pinned archives, empty Python suite, skipped Python suite, failing Moon suite. See `targeted_controls.py` and `targeted-controls/report.json`. No shared tool file was overwritten.
- Extra independent product probes: 48 documents, 281 real product processes, seed 22102026. Independent Fraction timing and memoized subset cardinality, actual selected event membership/one-to-one partition, per-recording/global metrics, Unicode ordering, 0/max collar and fractional ratios, and all argv-representable pair explanations passed. `product_probes.py`, `product-probes/report.json`, all inputs and per-process raw receipts are preserved. NUL selectors were excluded from these successful explanation counts and separately reproduced above.
- The first product-probe fixture attempted to place an embedded NUL in argv and failed in Python before spawn. Its partial artifacts remain in `product-probes-initial-fixture-error/`; it is not counted as a product failure or a passing probe.
- Historical T0–T7 evidence was symlinked read only. The T6/T7 freeze scripts resolve the original checkout and validate historical proof; they are not fresh recompilation of old fault/mutation/performance campaigns. The current core/CLI/qualification/consumer/package commands ran in the new copy.
- Source identities and original/copy state comparisons are in `setup.json`, `final-state.json` and the full gate report. The audit manifest excludes checkout Git/build/tool caches and shared symlink targets; the deliberately altered reference bytecode is retained as finding evidence.

## Considered and deferred boundaries (declined to judge as new defects)

- Remote CI execution, hosted runner availability/label semantics, Action service behavior, fresh downloads and Linux bootstrap/runtime: not executed because this review explicitly forbids network/install/remote actions. Static configuration was reviewed; no cross-platform or remote-pass claim is made.
- Namespace/registry publication, remote repository operations, competition eligibility/registration, external users, clinical data, and personal M2/oral explanation: outside this local engineering review; no operations or acceptance claims were made.
- T6 performance/mutation/native fault-injection campaigns: historical receipts/freeze validation only here; no new CPU query or broad campaign. The fresh normal-path native/CLI/qualification tests do not certify every OS, filesystem, signal race or legal graph.
- Existing T6 timeout partial-output/process-receipt Minor remains a separately recorded author deferral; this review did not trigger that 30-second timeout or claim it fixed.
- Duplicate and escape-equivalent input JSON keys: intentional last-value-wins contract, documented limitation; no new duplicate-key rejection required. Output duplicate-key/finite/Unicode checks remain independently exercised.
- Nonoverlapping events qualifying under a large collar, ID-dependent choice among equally maximum matchings, and legal graphs exhausting the fixed work budget: specified behavior, not defects. No timing-error optimization or universal completion guarantee is claimed.
- Original sed_eval zero-collar rejection, binary64 boundary differences, and substitution-vs-projection differences: explicitly declared domains/definitions, retained by qualification rather than hidden with epsilon or rewritten raw counts.
- Arbitrary supply-chain attestation beyond the pinned archive-member/source/version checks, and binary bit identity across different build directories: not claimed by the contract or this review. I1 concerns the narrower advertised original-reference execution identity, not a demand for complete supply-chain certification.
- Lexical arbitrary-precision interpretation of numeric schema_version was not separately qualified; the approved exact decimal-string rules apply to event/config values. No finding is asserted about version-number parsing without a dedicated reviewed contract/probe.
- T8 final acceptance-document updates and author fixes after the reviewed candidate are pending author closeout, not silently included in this candidate's review or test identity.

## Recommendations

Close I1 before treating the reference identity check as proof of the executed original reference. Record a deliberate ruling for the NUL CLI boundary. Keep the existing distinction among current local checks, historical evidence, unrun remote/Linux scope and personal requirements. Subsequent fixes require author verification of affected checks; this report is the one independent review, not an implicit second review of those fixes.

## Assessment

**Ready to merge? With fixes.**

The matching, exact time/Unicode model, shared explanations, micro metrics, native I/O and local packaging passed the current bounded verification with no confirmed mathematical defect. The reference execution identity gap should be closed before acceptance relies on that guarantee; the NUL selector limitation is a minor explicit-domain decision. No remote merge, push or publication is authorized or implied.

## Post-candidate boundary observed at finalization

The original checkout still reports candidate HEAD, but the final read-only snapshot observes these working-tree modifications: `scripts/verify.py`, `validation/sed_reference.py`, `validation/tests/test_reference.py`. They are absent from the clean review copy and are not reviewed or included in the fresh candidate verification. The reviewer made no edits to the original checkout.
