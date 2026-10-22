# Public MoonBit API

Import `local/mooneventeval/eventeval` from the local source module. The module
name is a development identity, not a registry publication. The following
complete executable is the exact source compiled/run by the external consumer:

```moonbit
///|
fn main raise {
  let r = @eventeval.event("r1", "alarm", "10", "12").unwrap()
  let p1 = @eventeval.event("p1", "alarm", "10", "12").unwrap()
  let p2 = @eventeval.event("p2", "alarm", "10.05", "12.05").unwrap()
  let rec = @eventeval.recording("clip-01", [r], [p1, p2]).unwrap()
  let input = @eventeval.task(["alarm"], [rec], @eventeval.default_config()).unwrap()
  let evaluation = @eventeval.evaluate(input).unwrap()
  let counts = evaluation.metrics().counts
  assert_true(counts.tp == 1 && counts.fp == 1 && counts.fn_count == 0)
  println(@eventeval.report_json(evaluation).unwrap())
}
```

Create a separate module with `moon.mod`:

```text
name = "local/mooneventeval_consumer"
version = "0.0.0"
preferred_target = "native"
import { "local/mooneventeval@0.1.0" }
```

In its `main/moon.pkg`, import only `local/mooneventeval/eventeval` and set
`pkgtype(kind: "executable")`. A temporary `moon.work` lists the absolute paths
of this consumer and the source module in `members`. The locked toolchain
resolves that import locally. Build the consumer's `main` with native/release/
deny-warn; no registry fetch is required. Workspace build output includes the
module name, so use the compiler's emitted artifact path.

## Factories and evaluation

`event(id, label, onset_s, offset_s)`, `config(collar_s, offset_ratio)`,
`recording(id, reference, prediction)` and `task(labels, recordings, config)`
return `Result[Value, EvalError]`. `default_config()` supplies 0.2/0.5. Event,
Config, Recording and Task are opaque, and array inputs are validated/copied.
Use Result handling in applications; this synthetic example unwraps known
valid inputs and asserts expected counts.

`decode_task(Bytes)` checks bounded strict UTF-8 JSON and typed factories.
`evaluate(Task)` returns an opaque `Evaluation`; `.metrics()` returns Counts
and optional precision/recall/f1. Counts fields are reference/prediction/tp/fp/
**fn_count**; the JSON field is **fn**. `.pairs()` returns copied tuples
(recording ID, label, reference ID, prediction ID).

`report_json`/`report_text` render an Evaluation; `evaluate_json(Bytes)` combines
decode/evaluate/JSON. All return Result where failure is possible.
`explain_pair(task, recording_id, reference_id, prediction_id)` returns an opaque
PairExplanation; `explanation_json`/`explanation_text` render its exact basis.
Explanation does not run matching or assert selection.

## Errors and reports

`EvalError` has kind/code/message/path/limit/observed. `exit_code(error)` maps
to 2 input, 3 resource or 4 internal; `error_json(error)` is the common JSON
failure renderer. A failed Result contains no partial Evaluation.

JSON reports use schema_version 1 and semantics `collar-max-cardinality/v1`.
Completed evaluations contain config, summary, by_label, by_recording, matches,
false_positives, false_negatives and work. Each match contains both events and
basis. Explanations contain one pair and basis, without summary/work. Failures
contain status failed and error, without scores. Library renderers return JSON
without a CLI terminal LF; the file CLI appends/checks the LF within 16 MiB.

See [rules and limits](../README.md), [examples](../EXAMPLES.md) and
[validation scope](../VALIDATION.md). Only local native consumption is claimed.
