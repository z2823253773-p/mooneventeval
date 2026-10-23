# Validation scope

MoonBit implements the product's exact-decimal rules and matching. Python is
used only for independent development checks. The public [API](docs/API.md)
and [three examples](EXAMPLES.md) are also tested from a freshly unpacked
local source candidate, using the existing pinned local toolchain.

## Independent comparisons

T6 generated 334 proposals: new seed20261020 populations plus 46 inherited
fixtures. Before product or reference execution, an independent Fraction
calculation excluded 10 ordinary-decimal tasks with any relevant comparison
margin <=1 microsecond, retaining their inputs and reasons. The 324 retained
bases are 155 binary-grid, 160 safe-decimal and 9 exact-boundary tasks.

The 315 grid/safe-decimal bases agree with the original `sed_eval` common
metric definitions. The nine boundary cases are separate: six agree; one has
a demonstrated binary64 edge flip (10.3−10.1 exceeds 0.2 in binary64); two use
zero collar, which the original reference refuses. Product boundary behavior
is checked with independent exact rationals. These three differences are not
reported as equality. There are no unexplained differences in this corpus.

Original `sed_eval` commit `0cb1b6d11ceec4fe500cc9b31079c9d8666ed6eb`
is hash-checked and unpatched in a separate locked environment. It runs on
each base globally and per recording, including class counts and both-defined
metrics. Its raw global substitution/FP/FN definitions are retained. A
separately named common-count projection derives TP from class counts and
FP/FN from event totals; projection agreement is not full raw-output equality.
Undefined original metrics are not silently converted to zero.

Each base also receives shuffle, translation, independent-recording duplication
and no-candidate-prediction transforms: 1,620 real file-CLI product calls total.
Transforms use exact rational eligibility and exhaustive partial-injection
matching for small groups; they are not 1,620 original-reference comparisons.
Same-product shuffle checks stdout bytes. Alternate legal maximum pair
identities across implementations are accepted.

## Resource, performance and negative controls

T6's final code/tested SHA is `7b8a453f58307e4118eeae7ad78d79859af6eeed`:
58 MoonBit, 41 validation and 15 real CLI tests passed. Count/Unicode/time/depth/
8 MiB boundaries, internal 20M work equality/+1 and shared 16 MiB serialization
boundaries are covered. The exact CLI post-LF 16 MiB landing point was not
constructed. Nine compile-time I/O fault cases use temporary copies of actual
native source; six compilable algorithm mutations are killed by behavioral
tests, with one equivalent max-operand swap recorded separately.

Three fixed 2,000-event graph families each ran three release subprocesses on
macOS arm64/Apple M5. Final sampled maximum wall time was 0.0493 seconds;
maximum per-child peak RSS was 8,994,816 bytes. These finite samples do not
prove all legal graphs, machines or OS/filesystem races meet those bounds.

The sole independent T6 review found two Important verifier defects. The
author repaired eligibility/membership checking and strict machine-output
parsing, then replayed five original corruptions successfully. This was author
verification, not a second independent review. Deferred Minor M1: timeouts
correctly fail, but the T6 comparator still does not persist partial captured
stdout/stderr/process receipts. Runtime input duplicate-key last-wins remains
an explicit limitation. Linux, remote CI and participant understanding/explanation evidence
remain unverified.

## Reproduce in the full development checkout

Raw evidence, reference scripts/environment and internal state are intentionally
excluded from the source candidate. In the full development checkout:

```sh
scripts/with-toolchain.sh moon test --target native --deny-warn
python3 -W error::ResourceWarning -m unittest discover -s tests -v
.venv-reference/bin/python -W error::ResourceWarning -m unittest discover -s validation/tests -v
python3 evidence/T6/freeze.py
python3 scripts/check_consumer.py --source . --output evidence/local-consumer-recheck
python3 scripts/package_candidate.py --output evidence/local-package-recheck
```

Use fresh output directories. The reference environment needs its separate
locked bootstrap; the source candidate neither supplies it nor claims that
installing the product installs the reference. Installer network/download
verification is distinct from reuse of the already-installed pinned compiler.
Formal registry namespace, public URL, publication and competition eligibility
are not established by local archive/consumer checks.


## Unified local delivery gate (full development checkout)

```sh
python3 scripts/verify.py --mode local --evidence evidence/local-delivery-recheck
```

Run from a clean committed project root, with the pinned local toolchain archive/
installation and locked `.venv-reference` already present. The verifier performs
no installs. It records version/format/interface/native build/test, Python and
original-reference tests, actual CLI cases, independent qualification, external
consumer, real package/unpack/examples and historical evidence checks. Missing,
skipped, nonzero or failed artifacts cannot produce a passing total. Each run
requires a fresh evidence directory and binds source bytes and tested commit.

The saved manual-only CI matrix calls the same entry point for macOS arm64 and
Linux x86_64, with full action commit pins and hash-locked dependencies. A saved
workflow is configuration only; no remote job or Linux execution is claimed by
this source candidate. Participant understanding, formal namespace/URL, publication and
competition acceptance remain separate. Internal execution detail belongs to
`docs/VALIDATION.md` in the full development checkout, which is not bundled here.

The internal M2 minimum-core milestone has passed its machine checks. User-run
retesting was waived on 2026-10-22; automated engineering acceptance is delegated
to Codex. This does not assert that the participant has personally demonstrated
understanding or received organizer approval.
