# P8 independent prepublication review

Reviewed base `e0061b0bd12583be8b7e497a727c94f70b16501d` to head `affd168393780a9e8fc2fb757d156e0a6c6af938`, plus the actual `evidence/P8/preflight-package` artifact. Source, index, HEAD and credentials were not changed or inspected. No publication was attempted.

## Findings

- Critical: 0.
- Important: 0.
- Minor: 1 — `scripts/check_registry.py:41-43,55` writes `authenticated: false` unconditionally while `record()` inherits the caller environment and `WRAPPER` reuses the developer's existing `MOON_HOME`. The implementation proves that this script does not perform a login; it does not itself establish that the download is anonymous. Reproduction: inspect `release_support.py:27-31` (`subprocess.run` has no sanitized environment) and `scripts/with-toolchain.sh:3-6` (shared toolchain home), then note that every receipt gets this boolean before `moon add` executes. Rename the field to `login_performed: false`, omit the assertion, or separately establish an anonymous download. This does not invalidate an otherwise successful public-registry install or block publication.

## Evidence and assessment

- All product-source changes in this diff are namespace/import/generated-interface changes; no scoring or TSV implementation changed. Current product imports and consumer templates consistently use the formal namespace. Consumer `local/...` names refer to the consumer itself, not the former dependency identity.
- Independently validated all 43 actual ZIP members against the closed policy and current source bytes. ZIP SHA-256: `e34d6bd987e5f341c03b70a281ce29f93dc67c84302352dcf7de14c6e285784b`. No members differ from current source. No bundled absolute user/temp paths or private-key markers were found. The allowlist excludes evidence, clinical/raw data, credentials, compiler binaries and development reference sources.
- MIT attribution, core Apache license/notice, and the sed_eval development/reference boundary are present in the actual artifact. No newly copied third-party implementation was identified in this diff.
- Extracted the actual ZIP into `/private/tmp/mee-p8-review-2o23ac1k/package`; independently compiled and ran the exact MoonBit snippet extracted from its INSTALL document, and the registry acceptance script's API_MAIN, using a separately created consumer with an explicitly local workspace and the locked compiler. Both native/release/deny-warn runs exited 0 and returned reference/prediction/TP/FP/FN `1/2/1/1/0`. API_MAIN also actually exercised TSV conversion and duplicate-key rejection. Receipts/stdout/stderr are in `/private/tmp/mee-p8-review-2o23ac1k`. These runs prove copied-package API/doc correctness, not network installation.
- `check_registry.py` creates a fresh temporary module, invokes `moon add` for the exact version, checks the installed member set and every byte before compilation, then compiles API/TSV/error examples and builds/runs CLI from the installed package. It does not create a source workspace or path dependency. The wrapper only supplies the compiler/core. This is an appropriate postpublication gate, subject to obtaining an actual successful run and binding its archive hash to the published candidate.
- README/API/INSTALL provide a usable native library installation path, full compiler/package/source setup, expected counts and explicit CLI build instructions. They distinguish dependency installation from a command installed on PATH and do not claim Windows/JS/WASM support. The release receipt explicitly remains pending. The source package's install instructions are necessarily prospective until publication succeeds.

## Behaviors deliberately not judged

- Public registry publication, current anonymous availability, server receipt, tag-to-published-source binding, and fresh postpublication installation: not yet performed; must remain release gates, not inferred from local success.
- New full macOS/Linux CI and the separately running full local gate: not rerun or represented as independently passed here.
- Newer/older MoonBit, Windows/JS/WASM, other architectures, genuine external adoption, competition acceptance and submission: outside the claimed/tested scope.
- Unchanged matching/input/TSV semantics, historical evidence restoration and broad numerical correctness: no renewed full campaign; reviewed only for namespace/release regressions.

Assessment: no code/package blocker found for the planned immutable initial publication, provided the required full local gate and dual-platform prepublication CI actually pass. The postpublication registry gate and publication receipt remain mandatory completion work.
