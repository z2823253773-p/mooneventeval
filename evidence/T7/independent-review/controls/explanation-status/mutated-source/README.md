# MoonEventEval

Evaluate labelled time events with exact decimal boundaries and deterministic
maximum-cardinality one-to-one matching. Explain why a reference/prediction
pair is eligible, including the exact onset and offset tolerances.

This is **local/mooneventeval 0.1.0, a local source candidate**. There is no
registered package or public repository URL claimed here. Native execution has
been verified on macOS arm64; other platforms and remote CI remain unverified.
Python is development tooling, not the scoring implementation.

## Build and run

Requires Python >=3.12, curl and a native C compiler. On a new checkout or
unpacked candidate, install the pinned local toolchain:

```sh
python3 scripts/install_toolchain.py
```

It installs only under `.tools`, checks pinned hashes and refuses to overwrite
an existing installation. No global installation is changed. Current local
verification reused the existing toolchain; it did not repeat a download.
Pinned compiler: `v0.10.14+7d59c7ec9`.

```sh
scripts/with-toolchain.sh moon build cmd/mooneventeval --target native --release --deny-warn
_build/native/release/build/cmd/mooneventeval/mooneventeval.exe --help
_build/native/release/build/cmd/mooneventeval/mooneventeval.exe --version
_build/native/release/build/cmd/mooneventeval/mooneventeval.exe evaluate examples/duplicate.json --format json
_build/native/release/build/cmd/mooneventeval/mooneventeval.exe evaluate examples/greedy-trap.json --format json
_build/native/release/build/cmd/mooneventeval/mooneventeval.exe evaluate examples/boundary.json --format json
_build/native/release/build/cmd/mooneventeval/mooneventeval.exe explain-pair examples/boundary.json --recording clip-01 --reference r1 --prediction p1 --format json
```

The three evaluations return TP/FP/FN **1/1/0**, **2/0/0**, **1/0/0**.
See [complete examples](EXAMPLES.md) for inputs, output summaries and reasoning,
and [public API](docs/API.md) for a standalone MoonBit consumer.

## Rules and input

Input is a regular UTF-8 JSON file (symlinks to regular files are accepted),
with `schema_version: 1`, declared labels, config and recordings. See the full
[duplicate fixture](examples/duplicate.json). No stdin or TSV/CSV is accepted.

Times and config values are ASCII decimal **strings**, with at most six
fractional digits. Time comparisons use Int64 microseconds and integer ppm;
there is no floating-point time comparison, rounding or epsilon. Numeric times
are rejected. IDs/labels are exact Unicode strings without trimming or
normalization. Duplicate JSON object keys, including escape-equivalent keys,
use the **last value**; raw input duplicate rejection is a known limitation.
Unknown schema fields, duplicate recording/event IDs and unknown labels fail
the whole task. One initial UTF-8 BOM is allowed.

Pairs must have the same recording and label. Onset difference is at most
`collar_s`; offset difference is at most
`max(collar_s, reference_duration * offset_ratio)`. Equality passes. Defaults:
collar `"0.2"`, ratio `"0.5"`. Events need not overlap. Matching maximizes the
number of pairs, not timing accuracy; IDs determine a stable traversal order.
An explanation checks eligibility without claiming a pair was selected.

TP is the number of selected pairs, FP is predictions minus TP, FN is references
minus TP. Global metrics pool counts before averaging. Each metric's zero
denominator yields `null`; two empty sides yield P/R/F1 all `null`. F1 is
computed directly as `2*TP/(reference+prediction)`.

## CLI protocol and limits

The command is first, the filename second, then option/value pairs. Text is
the default; `--format json` selects machine reports and JSON failures.
`--help`/`--version` stand alone. IDs may equal option names; spell a filename
starting with `--` using `./`. Invalid or repeated format selection gives a
text diagnostic. Files are read only; directories, FIFOs and devices fail.

Success goes to stdout with one terminal LF. Text failures go to stderr;
JSON failures go to stdout. Exit **0** means complete (including zero scores or
an ineligible explanation), **2** input/argument/file/output-I/O error,
**3** resource limit, **4** unexpected internal error. Failed evaluations have
no partial scores. Output I/O failure can leave an incomplete prefix: its
nonzero exit makes that prefix unusable as a completed report.

Limits include equality: input 8 MiB, nesting depth 16, 1,000 recordings,
256 labels, 2,000 reference+prediction events total, 256 Unicode codepoints per
ID/label, event times and collar at most 2,592,000 seconds (30 days), ratio 0–1,
matching work 20,000,000 steps, final UTF-8 output including LF 16 MiB. A legal
large graph may exhaust the work budget; no universal runtime guarantee is made.

## Evidence and licensing

[Validation](VALIDATION.md) explains the independent original-reference scope,
exact boundary differences, resource tests, mutations and remaining gaps.
These are synthetic developer checks, not user feedback, personal presentation
proof, remote CI or competition acceptance.

Own source/docs: [MIT](LICENSE). External core/runtime notices are retained in
[third-party notices](THIRD_PARTY_NOTICES.md). The source candidate excludes
reference environments, local toolchains, probes, internal plans and raw logs.
