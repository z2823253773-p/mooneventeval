# MoonEventEval

MoonBit event-time evaluation library under development. T3 provides validated
event/config/recording/task factories, strict JSON task decoding, budgeted
maximum-cardinality matching, complete stable JSON reports and a development
argv probe. Product CLI, explain-pair, native file I/O and final packaging remain
later stages.

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
establish the future file-reading CLI's 8 MiB I/O behavior. `decode_task` checks
the actual byte count, strict UTF-8 (one initial BOM allowed), nesting depth 16,
then schema and shared typed factories. JSON object duplicate keys, including
escape-equivalent keys, use the last value: reports describe the parsed task
and do not prove the raw text had no duplicate keys. Numeric times are rejected.

The [eight worked examples](docs/validation/T3-worked-examples.md) include the
augmenting trap and exact boundaries; they are agent-authored derivations, not
evidence of the user's own explanation. Full product acceptance/A11 is pending.
