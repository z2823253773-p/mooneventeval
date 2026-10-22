# Independent T7 review

Candidate: `a441ce89b57595c326031e8699b066777028f0b2`  
Base: `914cffd301d40eff8f4b2ecd697adb5052ebb031`  
Reviewed checkout: `/Users/henryz/Desktop/比赛/mooneventeval-t0` (read only).  
Audit root: `/private/tmp/mooneventeval-t7-independent-a441ce89-az9yv886`.

This is the single independent review of the named candidate. Checks ran in a fresh candidate export with locally pinned read-only Git metadata. Existing locked toolchain/reference installations were reused through local links. No remote, network, install, global configuration, clinical-data or additional CPU-discovery operation was performed. Concurrent or subsequent author fixes and closeout are outside this review.

All 156 exported candidate source/document/test files retained their initial hashes. The temporary Git index also names deliberately omitted historical evidence, so its final whole-tree diff reports those absent files; source integrity is established by `candidate-source.json` and `review-results.json`. The original checkout's final diff reflects concurrent author repair and is retained only as an observation, not assessed as part of this candidate.

## Strengths

- The candidate preserves production `eventeval`, `cli`, `cmd` and generated API bytes: their base-to-candidate diff is empty. The T7 implementation stays within documentation, licensing and local distribution verification.
- The real `moon package --list --frozen` and archive agree on 38 files. Every member's bytes match the exported candidate. The native stub, generated interfaces, three fixtures, installer/lock and public documents are present; private plans, logs, probes and environments are excluded. Existing archive traversal, duplicate-member, symlink and missing-member controls pass.
- Package consumption is real. Both the candidate gate and an independent manual consumer compiled and ran public factories/evaluate/report. During the independent builds, the copied original `eventeval`, `cli` and `cmd` directories were moved out of the candidate: the fresh extracted source still built the consumer and CLI. The workspace points only to the new consumer and extracted module; no product source fallback was available.
- The six literal README runtime commands, the exact API code block, documented text explanation, empty-metric behavior and malformed-JSON behavior worked. EXAMPLES inputs and summaries agree with actual outputs. Locked core LICENSE/NOTICE copies match upstream bytes. Local identity, toolchain reuse, synthetic validation, untested platforms and non-publication limits are stated accurately.
- Independent nominal checks passed: 58 MoonBit tests, 11 Python release/toolchain tests, final 41 validation tests, 15 real CLI tests, fmt/check, info, public consumer and actual package/unpacked scenarios. Command/cwd/stdout/stderr/exit/hash receipts are retained under `evidence/` and `results/`.

## Issues

### Critical (Must Fix)

None found.

### Important (Should Fix)

**I1 / P2 — The explanation acceptance check can mark a failed report and its package successful.**

- **File:** `scripts/check_examples.py:50-52`; propagated at `scripts/package_candidate.py:97-98`.
- **Problem:** After an exit-0 explanation, the verifier checks the basis, absence of `summary`, and recording ID, but never checks `status`. An explanation carrying `"status":"failed"` satisfies this predicate and leaves `differences` empty. The package gate then emits `passed: true` and exits 0.
- **Reproduced effect:** In a fresh temporary source copy, change only `explanation_json`'s serialized status literal from `completed` to `failed`. Run the actual full `package_candidate.py` path, including `moon package`, archive validation, fresh unpack, public consumer, native CLI build and six commands. Everything exits successfully; the archived/build-tested explanation actually says `failed`. This is a concrete acceptance defect, not an allegation that the unmodified candidate currently emits failed explanations.
- **Why it matters:** T7's success signal is intended to establish that the documented explanation works from the packaged product. It currently blesses a report that contradicts the success protocol, so a serializer regression can pass the advertised release check even though a reasonable caller cannot treat that result as a completed explanation.
- **Fix:** Require `status == "completed"` and reject an error-shaped explanation before accepting its basis. Add a behavioral negative test using the real or faithfully replayed failed-status output. Preserve the failed receipt/report and require a nonzero gate result; do not change production scoring merely to satisfy the verifier.
- **Evidence:** `controls/explanation-status/summary.json`, `mutation.diff`, `receipt.json`, `gate/report.json`, and `gate/unpacked-examples/explain/stdout`. The control's package process returned 0 with `passed: true` and `actual_explanation_status: failed`.
- **Replay:**

  ```sh
  python3 /private/tmp/mooneventeval-t7-independent-a441ce89-az9yv886/scripts/replay_explanation_status.py --checkout /absolute/path/to/checkout --output /fresh/output/directory
  ```

  Exit 1 means the false-green is reproduced. Exit 0 means the mutation reached the explanation and was rejected. Exit 2 means the control did not reach that point and must not be called a successful fix. The replay edits only its fresh source copy.

### Minor (Nice to Have)

None separately raised.

## Recommendations

Repair I1 in one author pass, replay the preserved counterexample RED to GREEN, and rerun the ordinary T7 gates. Keep the original review and its hashes immutable; label any post-review fix checks as author verification. No second independent review or expansion into T8 is required by this report.

The first validation-suite invocation lacked two small historical fixture sets omitted from the lean export, giving two setup errors; the next invocation still lacked one `product.json`, giving one setup error. After those committed fixture bytes were copied into the temporary tree, all 41 tests passed. These setup failures and raw logs remain preserved and are not counted as product defects or hidden as initial success.

## Declined to judge

- Remote CI, registry publication, formal namespace/public URL and competition eligibility: separate T8/publication/authorization work; T7 makes only local claims.
- Fresh network toolchain download/install and other platforms: prohibited in this review; actual checks reuse the locked local installation, and the public documentation distinguishes this boundary.
- Broad requalification of unchanged scoring/native logic across all inputs, resource exhaustion and OS/filesystem races: outside this packaging delta; finite regression suites were rerun, without replacing the separate T6 evidence scope.
- Personal paper/oral M2 completion and external user feedback: human evidence is separate from these machine checks and remains explicitly unclaimed.
- Independent proof of human authorship/rights or a legal opinion on license suitability: the committed ruling uses the existing Git author name; this review verifies actual attribution and copied upstream notice bytes only.
- Exhaustive mutation coverage of every report field and future documentation variant: not performed. The demonstrated explanation-completion false-green is reported above rather than being excused by specification silence.
- Subsequent author repair, new commits, evidence freeze and closeout: they are not part of candidate `a441ce89` and are not independently reviewed by this report.

## Assessment

**Ready to merge? With fixes.**

**Reasoning:** The named candidate's actual local package and documented behavior work, with independently demonstrated archive/source separation and honest scope. Fix the one confirmed explanation false-green before treating the T7 release gate as accepted; no production/core/API defect was found in this delta.
