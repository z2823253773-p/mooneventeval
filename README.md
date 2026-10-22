# MoonEventEval

MoonBit event-time evaluation library under development. T3 provides validated
event/config/recording/task factories, strict JSON task decoding, budgeted
maximum-cardinality matching, complete stable JSON reports and a development
argv probe. T4 adds same-basis pair explanations, safe text reports and shared final-byte
limits. T5 adds the native file CLI and reproducible demo transcripts. Personal
explanation, further I/O qualification and final packaging remain future gates.

Times are ASCII decimal **strings**, with at most six fractional digits. Core
comparisons use Int64 microseconds and integer ppm; no floating-point time
comparison or rounding is used. IDs and labels are compared exactly, with no
trimming or Unicode normalization.

## Local development

Requires Python >=3.12, curl and a native C compiler. Install the pinned local
toolchain on a new checkout (an existing installation is not overwritten):

```sh
python3 scripts/install_toolchain.py
scripts/with-toolchain.sh moon test --target native --deny-warn
python3 -W error::ResourceWarning -m unittest discover -s tests
```

The binary archive must match the pinned digest and publisher checksum. The
core archive is checked against a historical recorded digest, which is not a
publisher attestation. Global MoonBit installations are not modified.

The current public package is `local/mooneventeval/eventeval`. Its factories
return `Result[Event, EvalError]` and `Result[Config, EvalError]`; Event and
Config fields are private. This local module name is not a registry release.

See [current state](docs/PROJECT_STATE.md), [contracts](docs/contracts.md) and
[T3 task](docs/superpowers/plans/tasks/T3-evaluation.md) for boundaries and evidence.
The modules under `spikes/T0/` are separate throwaway experiments, including
deliberately invalid code. They are not product examples.

The [development reference environment](validation/README.md) now provides a
hash-locked original sed_eval self-check and an explicit common-count projection.
It is separate from the product and does not establish product parity.

## Development prototype

```sh
scripts/with-toolchain.sh moon build cmd/probe --target native --release --deny-warn
python3 validation/check_probe.py --product _build/native/release/build/cmd/probe/probe.exe --output evidence/T3/recheck-process
.venv-reference/bin/python validation/compare.py --phase prototype --product _build/native/release/build/cmd/probe/probe.exe --output evidence/T3/recheck-parity
```

`evaluate_json(Bytes)` returns `Result[String, EvalError]`; failures serialize
through `error_json(error)`. The development probe accepts one small JSON argv
argument and returns the full report/error with exit 0/2/3/4. This does not
establish file-reading I/O behavior; T5 now verifies that through the native CLI. `decode_task` checks
the actual byte count, strict UTF-8 (one initial BOM allowed), nesting depth 16,
then schema and shared typed factories. JSON object duplicate keys, including
escape-equivalent keys, use the last value: reports describe the parsed task
and do not prove the raw text had no duplicate keys. Numeric times are rejected.

The [eight worked examples](docs/validation/T3-worked-examples.md) include the
augmenting trap and exact boundaries; they are agent-authored derivations, not
evidence of the user's own explanation. Full product acceptance/A11 is pending.

## Pair explanations and text reports (T4)

The opaque `PairExplanation` comes from
`explain_pair(task, recording_id, reference_id, prediction_id)`.
`explanation_json` and `explanation_text` render the same eligibility basis used
by graph construction; they do not run matching or claim that an eligible pair
was selected. `report_text(evaluation)` shows selected pairs, exact signed time
deltas/tolerances, all label/recording metrics and unmatched candidate reasons.
Undefined metrics display `未定义`. All four renderers check the final UTF-8
output against 16 MiB, with no public budget override.

Text identities use reversible JSON quoting and escape terminal/directional
controls while preserving readable ordinary Unicode. This does not alter IDs.
The development probe also accepts `report-text`, or `explain-json`/`explain-text`
followed by recording/reference/prediction IDs after its JSON argument. It is
still an argv development adapter, not the file-reading product CLI. NUL cannot
be passed in OS argv IDs; the typed library API supports it and has whitebox
roundtrip coverage.

```sh
python3 validation/check_reports.py --product _build/native/release/build/cmd/probe/probe.exe --output evidence/T4/recheck
```

This checks the new renderers with a seconds-space Fraction oracle and performs
byte regressions against all 46 archived T3 reports; it does not rerun sed_eval.

## Native file CLI (T5)

The file CLI is implemented and locally verified on macOS arm64. Build with the
project's pinned toolchain, then run the executable directly:

```sh
scripts/with-toolchain.sh moon build cmd/mooneventeval --target native --release --deny-warn
_build/native/release/build/cmd/mooneventeval/mooneventeval.exe --help
_build/native/release/build/cmd/mooneventeval/mooneventeval.exe evaluate examples/duplicate.json --format json
_build/native/release/build/cmd/mooneventeval/mooneventeval.exe explain-pair examples/boundary.json --recording clip-01 --reference r1 --prediction p1
```

The command comes first, input file second, followed by option/value pairs.
Text is the default; `--format json` selects machine output, including argument
and input failures. An invalid or repeated `--format` produces a text diagnostic.
`--help` and `--version` must stand alone and do not read an input file. Query IDs
may start with `--` or equal option names. A filename starting with `--` can be
spelled with `./` to distinguish it from an option.

Inputs are read only: regular UTF-8 JSON files, including symlinks to regular
files, at most 8 MiB. Directories, FIFOs, devices and NUL paths are rejected.
No stdin, TSV/CSV, output-file option or numeric-time extension is added.
Successful reports go to stdout; text errors go to stderr; JSON errors go to
stdout. Exit codes: 0 completed (including zero score/ineligible pairs),
2 input/argument/file/output-I/O error, 3 resource limit, 4 unexpected internal
error. An output-device failure can leave a prefix already written; its nonzero
exit means that prefix is not a completed result.

See the [three-minute demo](docs/demo.md). Its automated transcripts do not prove
personal understanding or an actual spoken presentation. Linux/remote CI,
injected EINTR/short-write/close failures and final A11 remain future gates.
