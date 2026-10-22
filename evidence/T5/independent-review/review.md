# Independent T5 review — original report

Candidate: `1831fbc21199974b77c4a66675307d0071f88bb0`; base: `41890b84505e790efef6c2f981512af04539a51e`.
Review location: `/private/tmp/mee-t5-review-s5zp35lz`. One independent, read-only review pass. No source fixes and no second review. Original checkout/index/HEAD/branch were not modified by reviewer commands. Candidate source was extracted with `git archive`; builds/tests ran only in that temporary checkout, using symlinks to the existing pinned toolchain/reference venv. The temporary `.git` pointer was used only for read-only SHA/diff commands, and its HEAD was verified as the candidate both before and after the runs. Author may have separately changed status documents/untracked evidence in the original worktree.

## Strengths

- Thin dependency direction is preserved: native entrypoint handles argv/file/stream/process work; CLI dispatch calls the existing task decoder, evaluator, explainer and four renderers. `eventeval` has an empty base-to-candidate diff.
- Native I/O uses synchronous borrowed pointers, private bounded Int32 wrappers for ssize_t, read-only/nonblocking/cloexec open followed by regular-file fstat, NUL rejection before encoding, <=65536-byte calls and a hard 8MiB+1 read ceiling. Open/fstat/read/write retry EINTR; opened regular FDs are closed after aggregation and close(EINTR) is deliberately not retried. The successful read/close path survived 20,000 opens under 64 FDs.
- Real executable tests establish exit codes and actual byte streams, including invalid UTF8, depth17, 8MiB equality/+1, missing/unreadable/nonregular files, Unicode regular-file symlinks, zero-score and ineligible success, reserved-option query IDs, large Unicode output, immediate EPIPE and failure after a partial prefix. No `moon run` exit is substituted for product exit.
- Demo and README explicitly distinguish automated synthetic transcripts from personal spoken understanding, M2, final A11, Linux/CI and deferred fault injection. Existing T3 JSON byte reports remain unchanged in 46 real-file CLI replays.

## Critical

None found in this review.

## Important — I1: valid JSON error format is lost when an unknown option value resembles an ID option

Location: `cli/args.mbt:70-77`, particularly the unrecognized-token `scan = scan + 1` branch at line 77. The prescan scans unknown option values as if they were option keys. With the documented command/path followed by key/value-pair grammar, a value such as `--recording` belongs to the preceding unknown option; instead it consumes the following actual `--format` token. A value `--format` is likewise misread as an additional format flag with an invalid value.

Direct native reproduction (from checkout root):

```sh
_build/native/release/build/cmd/mooneventeval/mooneventeval.exe evaluate absent --unknown --recording --format json
```

Observed: exit 2, **0 stdout bytes**, 80 stderr bytes containing `MoonEventEval failed: INVALID_ARGUMENT "Invalid command or options; use --help"` plus LF.

Expected: exit 2, structured `INVALID_ARGUMENT` JSON on stdout and empty stderr. There is precisely one real `--format json` option in the documented pair positions. The unknown option must cause an argument error, but must not suppress the selected error protocol. `docs/contracts.md` T5 and `README.md:102-104` explicitly require the valid single JSON format to govern argument failures.

Control: replace the unknown option's value with `ordinary`; same otherwise-invalid invocation produces 182 stdout bytes of JSON and empty stderr. `--reference` and `--prediction` as the unknown value reproduce the same suppression; `--format` as the unknown value produces the same wrong text protocol by a false invalid-format classification. This is externally observable to machine callers and not merely a diagnostic wording issue.

Original raw evidence:

- `receipts/repro-format-unknown-id-name/{stdout.bin,stderr.bin,receipt.json}`
- `receipts/repro-format-control/{stdout.bin,stderr.bin,receipt.json}`
- `extra/unknown-value-{recording,reference,prediction,format}/{stdout,stderr,receipt.json}`
- `extra/report.json` (42 cases: 38 matched expectations, 4 expose this same defect)

Repair guidance: make error-format selection respect post-path key/value positions, including values of unknown keys, while preserving explicit handling for malformed command/path positions and the already-correct option-name ID values. Add RED→GREEN cases for the four values above and retain the existing duplicate/invalid-format and reserved-ID tests. Do not relax rejection of unknown options.

## Minor polish

No separate minor finding. The scripted demo's ten captured invocations are successful examples/explanations; the narrated missing-file failure also has real evidence in the process suite, not in `scripts/demo.py` itself. This does not block the machine implementation and does not prove a complete spoken demo.

## Independently rerun

All these ran against the extracted candidate and preserved binary stdout/stderr with command, cwd, exit code and hashes under `receipts/`:

- `scripts/with-toolchain.sh moon test --target native --deny-warn`: exit 0; **56/56**.
- `scripts/with-toolchain.sh moon build cmd/mooneventeval --target native --release --deny-warn`: exit 0; actual release product executable. SHA256 in `metadata.json` and `process/product.json`.
- `python3 -W error::ResourceWarning -m unittest discover -s tests`: exit 0; **4/4**.
- `.venv-reference/bin/python -W error::ResourceWarning -m unittest discover -s validation/tests -v`: exit 0; **29/29**. An existing upstream pkg_resources deprecation UserWarning was emitted; no ResourceWarning failure. This includes reference self-checks, not a new comprehensive product/reference parity run.
- `MEE_BIN=<release exe> MEE_EVIDENCE=<review>/process python3 -W error::ResourceWarning -m unittest discover -s tests/cli -v`: exit 0; **9/9**, **35** ordinary process-call receipts plus immediate and partial broken-pipe receipts.
- `python3 validation/check_cli_reports.py --product <release exe> --output <review>/cli-bytes`: exit 0; **46** raw byte comparisons passed.
- `python3 validation/check_native_io.py --output <review>/native-low-fd`: exit 0; built test metadata with `--build-only`, ran both native whitebox tests under **64 FDs**, including **20,000** repeated reads.
- `python3 scripts/demo.py --bin <release exe> --output <review>/demo`: exit 0; **10** native calls; personal_explanation remains `NOT_PERFORMED`.
- Reviewer `extra_checks.py`: **42** additional real-process cases, including all **24 permutations** of the four explain-pair options with IDs literally reserved option names; **38** expected results and **4** failures belonging to I1. This exploratory script reports mismatches in its JSON report; its own exit 0 is not an acceptance assertion.
- Read-only source diff, requirements snapshot, toolchain identity and platform capture are also in `receipts/`. Compiler was `v0.10.14+7d59c7ec9 (2026-09-18)` on local Darwin arm64.

## Considered but declined to certify or judge as delivered behavior

- Injected EINTR at open/fstat/read/write: retry loops inspected; no injected signal/syscall fault run, and deferred T6 scope is explicit.
- Injected short read/write counts, zero writes, and close failures: control flow inspected; large real output and broken pipes ran, but they do not prove every synthetic fault path.
- Close(EINTR) descriptor-release portability: deliberate documented no-retry policy avoids unsafe double-close; no cross-platform guarantee claimed.
- Exact CLI post-LF 16MiB equality/+1: final UTF8 framing/check inspected; full Moon suite reran the existing renderer exact-byte tests, but no new real-file fixture was tuned to land at the CLI framing boundary.
- Arbitrary invalid-byte OS argv/filenames: not certified; product consumes MoonBit String argv, and this review did not add an unapproved raw-byte filename interface.
- NUL through OS argv: impossible with native exec argv; the actual native function's NUL rejection was rerun in whitebox tests instead.
- Catastrophic allocation failure, process kill, signal-handler installation failure and all unexpected-runtime-fault exits: not injected or claimed; ordinary input/I/O failures and typed exit-category routing were tested.
- Regular files concurrently modified/truncated and unusual pseudo-filesystem/device behavior: no snapshot/transactional read semantics are promised; regular-file gate and bounded byte aggregation inspected, not stress-qualified against racing writers.
- Prefix on stdout after a downstream write failure: exercised and deliberately allowed by the contract; nonzero exit and stderr FILE_ERROR, not rollback, are the correctness condition.
- Linux, remote CI, global installation/bootstrap, package consumers, packaging/release, competition eligibility and submission: outside this local T5 review; no network/install/global environment changes were performed.
- Personal derivation, spoken/video demo and M2: deliberately incomplete and cannot be inferred from agent-generated docs/logs.
- Final A11/full sed_eval parity and exhaustive core mathematics re-audit: unchanged core plus existing suites/46 historical-byte comparisons were checked; no claim of final A11 or re-proving every core behavior.
- Existing JSON duplicate-key last-wins behavior, no TSV/CSV/stdin, `--` filenames via `./`, and standalone-only help/version: explicit scope/grammar decisions, not defects introduced by T5.
- Read access side effects beyond “no input content overwrite” (e.g. OS access-time bookkeeping): not audited and not claimed.

## Verdict

**Changes requested for the candidate's machine implementation because of I1.** No Critical finding; one Important protocol defect with direct native reproduction. The successful suites establish substantial local behavior but do not cancel the failing case or complete the personal/T6/A11/platform gates. Author may perform the agreed one-pass RED→GREEN fix; this report is the original independent review, not approval of a later revision and not a request for a second review.

Evidence root contains `candidate.tar`, source/executable metadata, the original `review.md`, `run.py`, `extra_checks.py`, replay instructions, and `SHA256SUMS.json`. Preserve original bytes when archiving. The author should archive the original report unchanged, alongside any separate resolution.
