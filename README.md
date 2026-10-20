# MoonEventEval

MoonBit event-time evaluation library under development. T1 provides validated
event/config factories and an internal exact collar-eligibility core. Matching,
JSON task evaluation, reports and the CLI are not implemented yet.

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
[T1 task](docs/superpowers/plans/tasks/T1-time.md) for boundaries and evidence.
The modules under `spikes/T0/` are separate throwaway experiments, including
deliberately invalid code. They are not product examples.
