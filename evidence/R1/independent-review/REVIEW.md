# R1 CI history transport review

Reviewed original repository `/Users/henryz/Desktop/比赛/mooneventeval-t0`, base `4d5d3fbb93972e4d64866528b4f8919bc6d3c8aa` to HEAD `07906089e24ec06772e3b176107d5613911a7b93`. Read-only repository review; no repository changes, network, installation, full verifier, broad product tests, or giant-log content reads. Review-agent skill applied. Parent-reported supplemental snapshot work and subsequent author fixes are outside this independently reviewed candidate; no second independent review is performed.

## Findings

### Important [P2] Compare existing proof bytes to the original bundled blob — scripts/restore_ci_history.py:27

When a proof already exists, line 20 verifies only its size/hash against `history.json`. After import, line 27 compares only the original Git blob's size, and lines 28–31 skip its digest when the target exists. In a real temporary Git fixture, leaving the original bundle/tip untouched, replacing the proof with different bytes of the same length, and updating the row SHA to those bytes makes `restore()` return `passed=true` while `git show ORIGINAL_TIP:path` differs. This defeats the bootstrap's claimed original-proof identity on its existing-file path. The fresh-checkout path and unchanged historical frozen gate still compare hashes, so this is not evidence of a false final 17-step verification. Bind the expected row to the selected original object's digest even when no file write is required. Receipt: `edge-probes.json`, case `self_consistent_wrong_existing`; replay: `edge-probes.py`.

Critical: none found. Minor: none qualifying.

## Observed checks

- New shipped fixture suite: 5 tests, exit 0; exact binary bytes/original SHA recovered, HEAD unchanged, repeat succeeds, corrupted bundle/different existing bytes/wrong proof/path escape reject (`unit-tests.log`).
- Additional small fixtures: external parent symlink, final-component symlink, and wrong original tip reject with no proof write (`edge-probes.json`). Existing wrong-proof/metadata consistency bypass reproduced as above.
- Original bundle streamed hash matches `history.json`: 24,000,228 bytes, SHA256 `13b8ca0a030bc5918586b2788e159ea99a0b425b8d371442b145da08a544e630`; advertised ref is exactly the declared original `4d5d3fbb93972e4d64866528b4f8919bc6d3c8aa` (`bundle-identity.json`). No original giant proof bytes were read or printed.
- Workflow restores after setup-python and before unified verifier. `clean_sources()` exempts evidence, so restoring the omitted evidence path does not itself invalidate source cleanliness. T6/T7 freeze still use original tested SHAs; imported original commit objects satisfy that lookup mechanism. The new suite is included by existing unittest discovery. Reviewed supported APIs against the declared Python 3.14.6 and local Git 2.50.1; fixtures ran on current Darwin host only.

## Declined to judge / limitations

No remote GitHub acceptance, repository privacy, actual Linux/macOS CI execution, toolchain installation, full 17-step gate, original-history graph/export-map exhaustiveness, parent-reported missing ignored reviewer binaries, or broad T8/product/mathematics acceptance is certified by this review. Original bundle completeness was checked only by digest/ref advertisement, not by importing/expanding it or reading the giant log. The untracked export-map file was observed, not treated as committed proof. No TOCTOU stress/race testing was performed. Parent's supplemental snapshot and author fixes are outside this candidate assessment; this review does not certify them.
