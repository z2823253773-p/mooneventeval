# P9 independent final-readiness review

Base: `226688abfb44d66080533e268230a8ac3efb80b1`
Candidate: `63249492789d7d153affe88b278cbe28ded17dd7`
Repository: `/Users/henryz/Desktop/比赛/mooneventeval-t0`

Assessment: **Hold remote publication until the Important provenance-validation finding is addressed.** No Critical finding. One Important and one Minor. This is a review of the P9 diff and delivery workflow, not a fresh mathematical/core review or organizer acceptance determination.

## Important

### I1. Corrupt SOURCE.json provenance is accepted and copied into a passing receipt

Location: `demo/public-data/reproduce.py:29-46`, receipt propagation at `108-110`.

`verify_source` pins only the license and DOI; provenance such as commit, authors and source URL is accepted without comparison to the actual fixed dataset identity. The success receipt then labels the unchecked `source['commit']` as its source commit. Consequently the replay can certify a source commit that does not exist and pass while its author attribution/source URL is corrupt. Since this new feature is explicitly source-backed public-data evidence and SOURCE.json is the entry point for its attribution, this is a material integrity gap, not a scoring defect.

Reproduced using an isolated copy of demo/public-data: change SOURCE.json commit to forty zeros, authors to `["Incorrect attribution"]`, and source_url to `https://example.invalid/wrong.tsv`; invoke the unchanged candidate replay with `--check --data-dir <copy> --bin <actual built CLI> --output <fresh>`. All six actual CLI calls run; exit0, passed=true, report.source_commit is forty zeros.

Evidence:
- `/private/tmp/mooneventeval-p9-review-tuyi3_5j/metadata-command.json`
- `/private/tmp/mooneventeval-p9-review-tuyi3_5j/data/SOURCE.json`
- `/private/tmp/mooneventeval-p9-review-tuyi3_5j/metadata-run/report.json`

Fix: anchor the expected SOURCE.json independently (for example, a pinned full-manifest digest in replay, or explicit strict comparison of all required provenance/selection/hash fields), reject changed/missing/extra metadata as appropriate, and add a mutation test of an attribution/provenance field. Preserve the local compressed-table/offline design.

## Minor

### M1. A timed-out product invocation loses its count and partial streams

Location: `demo/public-data/reproduce.py:60-65`, exception handling at `113-115`.

TimeoutExpired is raised before stdout/stderr and the receipt are written. The outer handler records failure, but the already-started invocation is absent: product_calls remains zero, receipts is empty, and partial stdout/stderr are discarded. This does not produce a false success, so it is Minor, but leaves the new failure-evidence protocol incomplete.

Reproduced with `/private/tmp/mooneventeval-p9-review-tuyi3_5j/timeout-bin`, a temporary executable that prints/flushed both streams then sleeps61s. The unchanged replay times out after60s and exits1. `/private/tmp/mooneventeval-p9-review-tuyi3_5j/timeout-run` contains only report.json with product_calls=0, receipts=[], and the TimeoutExpired error.

Fix: catch TimeoutExpired around the invocation, persist its partial streams and a receipt with timed_out=true and exit_code=null, count the invocation, then fail. An injected timeout unit test avoids a slow real60-second test.

## Independent checks performed

- Read applicable AGENTS.md, current plan/contracts additions, all29 changed files, replay and smoke dependencies, and original full CI/verifier boundary.
- Exact-candidate local shared clone at `/private/tmp/mooneventeval-p9-sparse-review`, sparse checkout using the exact workflow patterns: `.ci`, evidence, validation and spikes absent. Reused the already pinned installed toolchain via a temporary symlink; did not install a new compiler or claim an independent download.
- Ran real eight-step smoke in that clone: exit0,65 MoonBit tests,2 workflow tests,13 synthetic product commands,6 public-data calls, and external MoonBit consumer. Report `/private/tmp/mooneventeval-p9-sparse-smoke/report.json`, hashes `/private/tmp/mooneventeval-p9-sparse-smoke/SHA256SUMS.json`. Native compilation/execution here is macOS arm64, not Linux.
- Existing workflow tests independently executed as part of the smoke, including modified reference input and output snapshot rejection. Additional malformed SOURCE.json, changed license and changed gzip byte all exit1/passed=false/product_calls0; evidence `/private/tmp/mooneventeval-p9-review-tuyi3_5j/failure-matrix.json`.
- Checked84 local Markdown links in changed documents against exact-case tracked paths; all resolve, including docs/INSTALL.md and docs/demo.md.
- Confirmed no product core/API/CLI changes in this diff. Package policy still enumerates43 members and excludes demo/public-data. README and notices are updated package members, so a newly generated source candidate need not be byte-identical to the already published0.1.0 archive; current documentation keeps published P8 evidence and P9 source scope separate.
- Workflow addition retains manual full two-platform CI and original17 verifier steps, with public replay added afterward. Smoke explicitly marks reference and registry checks false. No observed false claim of new-HEAD full/remote acceptance in the current state documents.
- Notices separate MIT project code from CC BY4.0 annotation/derived data, include named authors, DOI, fixed source URL, license link and changes, and clearly disclose controlled predictions/no audio/no full DCASE or real-model claims.
- Source checkout/index/HEAD were not mutated. Initial and final status: only pre-existing/parent-owned untracked evidence/P9. All experiments/logs created under /private/tmp.

## Explicitly not judged / not performed

- No fresh general algorithm/security review, performance certification, Windows/JS/WASM support review, or real-model evaluation; product core is outside this diff.
- Did not run the expensive complete17-step local gate, full reference comparison, package/unpack gate, registry install or historical freeze; coordinator is running exact-commit acceptance separately.
- Did not execute GitHub-hosted workflows, independently confirm current action/Python availability, dispatch remote CI, push, publish, submit any organizer form, or contact anyone. Sparse-workflow success is local evidence, not a Linux/GitHub result.
- Did not independently authenticate the dataset license from the primary live endpoint: attempts to open the Zenodo API record and pinned raw GitHub source through the web tool failed. Local attribution structure was reviewed against the supplied manifest and coordinator's reported primary-source verification; this is not independent legal advice or license certification.
- Did not adjudicate contest compliance/organizer final acceptance, externally adopted usage, real user feedback, or whether the participant can personally present the material.
