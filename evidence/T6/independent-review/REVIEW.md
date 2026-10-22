# MoonEventEval T6 — sole independent read-only review

Candidate: `fb4de0bbb28f0bed48d0529db6ebc946027a2a81`.
Base: `b8cf27d02fa34a007185e15c23ea19bd0e412b4a`.
Review root: `/var/folders/l0/z510jl1d0rxc2cpk2jkvmks80000gn/T/mee-t6-independent-weo09xrc`.
Original: `/Users/henryz/Desktop/比赛/mooneventeval-t0`.

This is one independent review. It does not review subsequent author fixes. All builds, fault injection, mutations and counterexamples ran in temporary copies. No original checkout, index, HEAD or branch changes were made by the reviewer. No network, installation, global configuration, additional agents or CPU query was used. The Apple M5 identity is reused from the author's separately approved read-only query receipt, copied as `cpu-query-author-receipt.json`; it is not a fresh independent hardware query.

The candidate was archived with code/docs/tests/examples and only the needed `evidence/T3/parity-final` fixtures. `.tools` and `.venv-reference` were linked to the existing local environments; `.git` pointed read-only to original metadata after checking candidate HEAD. `evidence/independent-audit.json` confirms 126 archived code/test/doc files match candidate Git blobs, with zero mismatches after the runs. Fresh release binary SHA256: `ca5ca36220842793369caf02f7c866ab1cc6961f7d0d8dfaa89a88ae94ea9ccc`.

## Strengths

- Qualification actually uses the file CLI and saves byte captures, command/exit/hash receipts. Exact Fraction eligibility and exhaustive partial injections are independent of product traversal. Accepted base graphs have at most 4 references and 4 predictions per recording/category; the four transforms do not turn them into impractically large exhaustive graphs.
- Generation is deterministic and performed before either evaluator runs. Fresh audit confirms 324 accepted inputs (155 binary grid, 160 safe decimal, 9 exact boundary), 10 retained rejected decimal proposals, and the stated new/inherited seed populations. The <=1 microsecond exclusion uses exact rational margins and covers both onset and offset comparisons.
- Product validation checks actual report shape and canonical times, event partition, legal selected edges, group cardinalities, unmatched candidate degrees, global/per-recording/per-label metrics and work bounds. Reference checking separately retains raw substitution counts and explicit projection; base recordings are rerun independently, including prediction-only recordings.
- Boundary classification is constrained: a concrete binary64 edge flip and an independently built float graph must explain all reference groups. Zero collar accepts only the exact known original ValueError. Fresh tests include unexpected-reference-error and wrong-boundary-output rejection.
- Four transforms are checked for each accepted base (1,296 transforms); reordering checks raw byte identity. Resource tests cover real CLI boundaries, and the internal 20M test checks the actual default limit without exposing a runtime budget flag.
- Fault injection compiles the actual C/Moon source copies, reports distinct instrumented hashes, and records counters/FD balance. Mutations compile first and fail actual named tests: six behavioral kills, one equivalent max-operand swap, all control/restored runs green. No compile failure was counted as a kill.

## Findings

### Critical: none found

### Important I1 — benchmark accepts explicitly ineligible selected pairs

Location: `validation/benchmark.py:60-61` (candidate source).

The checker verifies that a reported basis equals the independent predicate result, but never requires that result's `eligible` flag to be true. It also tests only uniqueness of report IDs, not exact membership of event data/recording/label in the supplied input. An internally truthful basis for an illegal selected pair therefore passes the benchmark's success gate.

Reproduction: `negative-controls/benchmark-ineligible` runs the fresh release executable, swaps the first two selected predictions, recomputes their bases truthfully, and leaves counts and work unchanged. The benchmark exits 0 and writes `passed: true`. Independent inspection finds two illegal selected pairs per sparse trial and one per chain trial (9 illegal pairs over the nine samples); the dense swaps remain equivalent legal matches. All event objects in this counterexample still belong to the input, so this is not dependent on fabricated data.

Evidence:
- `evidence/negative-benchmark-run/{command.json,stdout,stderr,receipt.json}`
- `evidence/negative-benchmark/report.json`
- `evidence/negative-benchmark/sparse/0/stdout`
- `evidence/negative-benchmark/chain/0/stdout`
- `evidence/independent-audit.json` → `performance_audit`

Required repair: validate matched event identities/data and recording/category against the input, require an exact complete one-to-one partition for these full-match workloads, and require independent eligibility **true** as well as basis equality. Add a regression using this corruption. Keep this polynomial for 1,000×1,000 workloads; do not invoke the exhaustive graph oracle used for small qualification cases.

### Important I2 — tolerant JSON decoding loses protocol violations and can abort the difference ledger

Location: `validation/compare.py:258-265`; downstream failure at `validation/qualify.py:115` / `save` at line 17.

`run_file_product` decodes with ordinary `json.loads`. It does not enforce the single terminal LF or reject duplicate object keys. Those facts are already lost by the time the strict dictionary-shape checker runs. It also permits JSON's nonstandard NaN constants into the diagnostic data; `save(..., allow_nan=False)` then raises outside the per-case try block.

Fresh one-base/four-transform corruptions reproduce:

| Corruption | Observed candidate result |
| --- | --- |
| Remove the terminal LF | exit 0, `passed: true`, all four transforms pass |
| Replace terminal LF by CRLF | exit 0, `passed: true`, all four transforms pass |
| Duplicate the `status` key with the same value | exit 0, `passed: true`, all four transforms pass |
| Replace summary precision with literal NaN | exit 1 from uncaught diagnostic serialization ValueError; raw stdout and process receipt retained, but no case comparison or final report |

The first three are verifier false greens against the frozen output contract. The fourth does fail the process, but fails to produce the required usable difference ledger and stops the corpus. The known last-key-wins limitation for **input** JSON does not authorize duplicate keys in the frozen **output** format.

Evidence: for each mode `no-lf`, `crlf`, `duplicate-output-key`, `nan-output`:
- `evidence/negative-<mode>-run/{command.json,stdout,stderr,receipt.json}`
- `evidence/negative-<mode>/baseline/base/{input.json,stdout,stderr,process.json}`
- successful false greens additionally have `baseline/comparison.json` and `report.json`.
- `evidence/independent-audit.json` → `negative_outputs` records exact artifact availability and byte tails.

Required repair: validate raw framing, strict UTF-8, unique object keys at every depth, and finite JSON numbers before semantic comparison. Preserve original bytes and turn violations into serializable differences; ensure malformed/nonfinite reports cannot prevent final failed-ledger creation. Include regression controls for all four cases. Merely normalizing newlines or retaining the last duplicate key would preserve the false-green path.

### Minor M1 — timeout drops already-captured partial child bytes

Location: `validation/compare.py:258-259`.

The timeout exception occurs before stdout/stderr/process artifacts are written. The outer qualification catch correctly marks the case unexplained and exits nonzero, but discards `TimeoutExpired.stdout` / `.stderr` and the process receipt. A real child writes `partial stdout before timeout` and `partial stderr before timeout`, then sleeps beyond 30 seconds. Result is correctly failed; neither raw stream nor `process.json` exists.

Evidence: `negative-controls/timeout`, `evidence/negative-timeout-run/`, `evidence/negative-timeout/baseline/exception.txt`, `evidence/negative-timeout/report.json`, and the artifact checks in `independent-audit.json`.

This is an evidence-retention gap, not a false-green result. Follow-up should persist the exception's byte captures and a timed-out process record before returning a failed case. It can be explicitly deferred separately from I1/I2.

## Fresh independent execution versus inspected evidence

All rows below are fresh execution from the candidate temp archive. Every top-level command directory contains the exact argv/cwd, raw stdout/stderr, exit code, duration, and both stream hashes.

| Check | Fresh result | Evidence directory |
| --- | --- | --- |
| Native Moon suite | 58 passed, exit 0 | `evidence/moon-test/` |
| Release CLI build | exit 0 | `evidence/release-build/` |
| Original Python toolchain tests | 4 passed, exit 0 | `evidence/python-tests/` |
| Validation suite with ResourceWarning errors | 37 passed, exit 0 | `evidence/validation/` |
| Real CLI suite with ResourceWarning errors | 15 passed, exit 0 | `evidence/cli/`, `evidence/cli-cases/` |
| Full qualification | 324 bases + 1,296 transforms, 1,620 exit-0 process receipts; 321 common, 1 binary64 explanation, 2 zero-collar domain limits | `evidence/qualification/`, `evidence/parity-cases/` |
| Performance | three release subprocess samples each for sparse/dense/chain, exit 0 | `evidence/benchmark/`, `evidence/performance-cases/` |
| Actual-C fault injection | 9 modes pass, exit 0 | `evidence/io-faults/`, `evidence/io-fault-cases/` |
| Compiled product mutations | 6 killed, 1 equivalent, 0 invalid/survived; controls/restored green | `evidence/mutations/`, `evidence/mutation-cases/` |
| Independent evidence/source audit | zero candidate source mismatches; baseline performance has no illegal/foreign pairs | `evidence/evidence-audit/`, `evidence/independent-audit.json` |

Fresh sampled performance maxima: sparse 0.448503 seconds / 6,684,672 bytes peak RSS; dense 0.050965 seconds / 8,863,744 bytes; chain 0.063220 seconds / 6,897,664 bytes. These runs overlapped other local review work and are samples, not universal throughput claims. `wait4` obtains the individual child rusage, Darwin ru_maxrss is used as bytes, and the source correctly sets `Popen.returncode` after reaping. The valid unmodified release reports were separately checked for actual input-event membership and eligibility, so I1 does not assert the observed production benchmark output is wrong.

Inspected, not freshly independently produced: the approved CPU query receipt; candidate source/docs/contracts/PRD; existing T3 fixture bytes and original reference source/hash locks. Historical T6 author trial directories were not treated as final candidate proof. I did not independently reinstall or rebuild the locked reference environment. Its actual original-source hash verification ran on reference evaluation; no reference patching was used. The known upstream pkg_resources deprecation UserWarning appears in the captured reference stderr; it is distinct from a ResourceWarning failure.

## Considered boundaries deliberately not judged as delivered behavior

1. Personal M2 paper derivation/oral explanation: no personal evidence in scope; automated derivation/test logs cannot satisfy it.
2. Linux/other OS/architecture, remote CI, packaging/consumer and publication: no authorized live target here; local Darwin arm64 results do not establish them.
3. Clinical or real business performance/data quality: corpus is synthetic and no clinical data was accessed.
4. Universal 20M/time/memory guarantee for every legal 2,000-event graph: neither the corpus nor three benchmark families proves it; the contract explicitly disclaims this. Internal exact budget boundary and sampled performance were judged.
5. Exhaustive maximum matching at benchmark sizes: deliberately not attempted because the independent oracle enumerates partial injections exponentially; small-group use is safe and the large fixed graph constructions have inspectable known full matchings.
6. All possible OS/filesystem/concurrency failure sequences: nine compile-time wrappers provide finite coverage only. Close EIO/EINTR modes close the underlying descriptor then return an injected error; they demonstrate one-attempt control flow for that scenario, not every platform's ambiguous close ownership semantics.
7. Byte-identical optimum identities across different implementations: explicitly outside the cardinality parity claim. Alternate legal maximum solutions are accepted; same-product input reorder byte identity was judged.
8. Raw sed_eval undefined metrics, extra error-rate metrics and full raw/projected equivalence: only both-defined common metrics and declared raw substitution identities are promised. Original undefined/nonfinite markers were not treated as automatically erroneous or coerced to product null. I did not expand this review into arbitrary mutation of undocumented reference output fields.
9. Binary64/product equivalence on exact decimal edges and collar zero: deliberate domain/representation differences are judged by exact oracle, concrete flips and float-graph explanation, not waived wholesale. No claim of general floating-point equivalence is accepted.
10. Runtime input duplicate-key rejection: the documented input last-key-wins limitation remains out of this T6 implementation; it does not excuse output-key duplication (I2).
11. Old argv-probe phase as current file-CLI proof: prototype retained for historical use; it was inspected but not rerun as qualification. Its prior newline handling was not treated as evidence for this phase.
12. Final author closeout manifest/task completion text, later commits and subsequent repairs: author was still preparing these concurrently. This review is bound to the named candidate and the captured reruns, and is not a second review of any future fix.
13. General adversarial toolchain replacement, Python `-O`, corrupted global interpreter or malicious custom huge `cases=` inputs: not normal supported invocation or the promised deterministic corpus. No claims about those were added.
14. Cosmetic formatting/refactoring in compact Python scripts: not a blocker; the findings concern demonstrated gate behavior, not stylistic preferences.

## Verdict

**Request changes: 0 Critical, 2 Important, 1 Minor.** The current release behavior passed the independent nominal runs, and no core mathematical/runtime defect was demonstrated. T6's own success gates still have reproduced false greens (I1/I2), so the candidate should not be called fully qualified until the author performs the authorized single repair pass, retains RED→GREEN evidence and runs the appropriate final checks. This report ends the one independent review; author fix verification is not independent re-review.

## Replay and artifact map

`candidate-source.diff` is the scoped source/docs/test diff. `capture_command.py` is the runner used for top-level raw logs. `make_negative_controls.py`, `negative_qualification.py`, `negative-controls/` and their run receipts preserve the original reproductions. `audit_evidence.py` independently validates receipts and reports.

`replay_negative.py` accepts a fresh output directory and a chosen source/product, so the author can replay the same corruption against repaired code without editing the archived candidate:

```sh
/Users/henryz/Desktop/比赛/mooneventeval-t0/.venv-reference/bin/python /var/folders/l0/z510jl1d0rxc2cpk2jkvmks80000gn/T/mee-t6-independent-weo09xrc/replay_negative.py --source /Users/henryz/Desktop/比赛/mooneventeval-t0 --product /Users/henryz/Desktop/比赛/mooneventeval-t0/_build/native/release/build/cmd/mooneventeval/mooneventeval.exe --output /tmp/mee-t6-author-replay-benchmark --mode benchmark-ineligible
```

For I2 use the same command with a distinct fresh output and `--mode no-lf`, `crlf`, `duplicate-output-key`, or `nan-output`. Fixed behavior must return nonzero and retain a usable failed ledger/raw captures; the NaN control already returns nonzero in the candidate, so return code alone is insufficient for that control. Optional M1 mode is `timeout` (30 seconds).

`SHA256SUMS.json` hashes this report, replay scripts, scoped diff, CPU receipt and every independent evidence file (excluding itself); `SHA256SUMS.sha256` provides the manifest hash.
