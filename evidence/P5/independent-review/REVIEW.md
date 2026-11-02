# MoonEventEval P5 independent review

Reviewed author base 7171015a0c269eb057839fe99def33378c82ac8d through candidate ff728dc0efe0d4735f2422b3723cec42c1da1e78. Scope includes the applicable AGENTS.md, contracts, P5 plan, complete candidate diff and focused runnable checks. Verdict: changes requested for the contributor instructions.

## Critical

None.

## Important

**I1. A fresh public clone cannot run the advertised complete local gate using the contributor instructions.** CONTRIBUTING.md:17–21 lists the reference prerequisites, then runs the verifier directly. The GitHub transport deliberately omits the original history and one 150,195,290-byte proof from the native commit tree. The full gate invokes evidence/T6/freeze.py and evidence/T7/freeze.py. T6 reads original commit objects and T7 line 19 reads the omitted file listed in its manifest. A clone following the guide reaches a late historical verification failure. CI restores these prerequisites in a separate explicit step; .ci/README.md documents this.

Reproduction using the local checkout of the public export: `git cat-file -e HEAD:evidence/T7/independent-review/evidence/candidate-final-tracked-diff/stdout` returned 128. `.ci/history.json` and `evidence/T7/manifest.json` both bind that proof to SHA-256 20463bc4de0ce638b5e6c60ecbf7082f914833a9a7aa6e30e07c8f4437279c15. Add the CI-matching `python3 scripts/restore_ci_history.py` step for a public clone before the unified verifier and link .ci/README.md. The original author checkout already contains the historical proof. Preserve evidence from this reviewed SHA separately when publishing a correction.

## Minor

None.

## Independently checked

- Exported the candidate's eventeval, example, manifests, wrapper, reference to the installed locked toolchain, and integration test into a fresh temporary directory. No original repository build outputs, product CLI, Python scoring modules or sed_eval were present. The documented command and the actual new integration test passed. Executable import is public, and the workspace resolves the library by a relocatable relative path.
- Observed selected r1/p1, p2 with one candidate and reason unselected_in_maximum_matching, counts 1/1/0, and a separate explanation for r1/p2 with eligible true, no summary/work. The invalid numeric onset produced input INVALID_TYPE at recordings[0].reference[0].onset_s, with exactly schema_version/status/error as top-level fields. The process exited 0 for the intentionally handled failure. Inspection confirms unexpected Result errors abort and the CLI protocol is not changed.
- The candidate's actual local source ZIP has 38 paths. All 38 match their Git blobs at the candidate SHA, and all 28 package-local Markdown links resolve inside the archive. The full-repository example and new contributor/changelog files are excluded and are referenced by absolute public-repository URLs. ZIP SHA-256 b8ae783068d6c7f8d7570914873219004a8d4ed106550bb4d7962839b2a7226b.
- MIT and third-party notices are present. Redistributed core LICENSE and NOTICE match the locked core byte-for-byte. The example module imports only the existing public library. Documentation distinguishes bootstrap tooling and the compiled example, public Git repository and registry publication, and eligibility and actual matching.
- The integration test executes via normal unittest discovery in the unified gate. git diff --check passed. Candidate status labels P5 remote CI pending, with P4 results scoped to their historical SHAs. This review did not run the full delivery gate or remote CI and makes no claim about later metadata commits.
