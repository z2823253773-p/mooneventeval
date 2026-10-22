///|
// String.escape is a MoonBit display literal, not a JSON string encoder.
fn String::quote_json(self : String) -> String {
  Json::string(self).stringify()
}

///|
fn json_object(fields : Array[(String, String)]) -> String {
  "{" + fields.map(pair => pair.0.quote_json() + ":" + pair.1).join(",") + "}"
}

///|
fn json_array(items : Array[String]) -> String {
  "[" + items.join(",") + "]"
}

///|
fn optional_double(value : Double?) -> String {
  match value {
    None => "null"
    Some(number) => number.to_string()
  }
}

///|
fn metrics_json(metrics : Metrics) -> String {
  let c = metrics.counts
  json_object([
    (
      "counts",
      json_object([
        ("reference", c.reference.to_string()),
        ("prediction", c.prediction.to_string()),
        ("tp", c.tp.to_string()),
        ("fp", c.fp.to_string()),
        ("fn", c.fn_count.to_string()),
      ]),
    ),
    ("precision", optional_double(metrics.precision)),
    ("recall", optional_double(metrics.recall)),
    ("f1", optional_double(metrics.f1)),
  ])
}

///|
fn event_json(event : Event) -> String {
  json_object([
    ("id", event.id.quote_json()),
    ("label", event.label.quote_json()),
    ("onset_s", format_scaled_seconds(event.onset_us, 6).quote_json()),
    ("offset_s", format_scaled_seconds(event.offset_us, 6).quote_json()),
  ])
}

///|
fn basis_json(basis : PairBasis) -> String {
  json_object([
    ("label_match", basis.label_match.to_string()),
    ("onset_pass", basis.onset_pass.to_string()),
    ("offset_pass", basis.offset_pass.to_string()),
    ("eligible", basis.eligible.to_string()),
    (
      "onset_delta_s",
      format_scaled_seconds(basis.onset_delta_us, 6).quote_json(),
    ),
    (
      "offset_delta_s",
      format_scaled_seconds(basis.offset_delta_us, 6).quote_json(),
    ),
    (
      "onset_limit_s",
      format_scaled_seconds(basis.onset_limit_us, 6).quote_json(),
    ),
    (
      "offset_limit_s",
      format_scaled_seconds(basis.offset_limit_scaled, 12).quote_json(),
    ),
  ])
}

///|
fn unmatched_json(item : UnmatchedEvent) -> String {
  json_object([
    ("recording_id", item.recording_id.quote_json()),
    ("event", event_json(item.event)),
    ("candidate_count", item.candidate_count.to_string()),
    (
      "reason",
      (if item.candidate_count == 0 {
        "no_eligible_candidate"
      } else {
        "unselected_in_maximum_matching"
      }).quote_json(),
    ),
  ])
}

///|
pub fn report_json(report : Evaluation) -> Result[String, EvalError] {
  let text = json_object([
    ("schema_version", "1"),
    ("semantics", "\"collar-max-cardinality/v1\""),
    ("implementation_version", "\"0.1.0\""),
    ("status", "\"completed\""),
    (
      "config",
      json_object([
        (
          "collar_s",
          format_scaled_seconds(report.config.collar_us, 6).quote_json(),
        ),
        (
          "offset_ratio",
          format_scaled_seconds(report.config.offset_ratio_ppm, 6).quote_json(),
        ),
      ]),
    ),
    ("summary", metrics_json(report.summary)),
    (
      "by_label",
      json_array(
        report.by_label.map(row => {
          json_object([
            ("label", row.0.quote_json()),
            ("metrics", metrics_json(row.1)),
          ])
        }),
      ),
    ),
    (
      "by_recording",
      json_array(
        report.by_recording.map(row => {
          json_object([
            ("recording_id", row.0.quote_json()),
            ("metrics", metrics_json(row.1)),
          ])
        }),
      ),
    ),
    (
      "matches",
      json_array(
        report.matches.map(pair => {
          json_object([
            ("recording_id", pair.recording_id.quote_json()),
            ("label", pair.label.quote_json()),
            ("reference", event_json(pair.reference)),
            ("prediction", event_json(pair.prediction)),
            ("basis", basis_json(pair.basis)),
          ])
        }),
      ),
    ),
    ("false_positives", json_array(report.false_positives.map(unmatched_json))),
    ("false_negatives", json_array(report.false_negatives.map(unmatched_json))),
    (
      "work",
      json_object([
        ("candidate_checks", report.candidate_checks.to_string()),
        ("eligible_edges", report.eligible_edges.to_string()),
        ("matching_steps", report.matching_steps.to_string()),
      ]),
    ),
  ])
  bounded_output(text, 16_777_216)
}

///|
pub fn error_json(error : EvalError) -> String {
  let kind = match error.kind {
    Input => "input"
    Resource => "resource"
    Internal => "internal"
  }
  let path = match error.path {
    None => "null"
    Some(value) => value.quote_json()
  }
  let limit = match error.limit {
    None => "null"
    Some(value) => value.to_string()
  }
  let observed = match error.observed {
    None => "null"
    Some(value) => value.to_string()
  }
  json_object([
    ("schema_version", "1"),
    ("status", "\"failed\""),
    (
      "error",
      json_object([
        ("kind", kind.quote_json()),
        ("code", error.code.quote_json()),
        ("message", error.message.quote_json()),
        ("path", path),
        ("limit", limit),
        ("observed", observed),
      ]),
    ),
  ])
}

///|
pub fn explanation_json(value : PairExplanation) -> Result[String, EvalError] {
  let text = json_object([
    ("schema_version", "1"),
    ("semantics", "\"collar-max-cardinality/v1\""),
    ("implementation_version", "\"0.1.0\""),
    ("status", "\"failed\""),
    (
      "config",
      json_object([
        (
          "collar_s",
          format_scaled_seconds(value.config.collar_us, 6).quote_json(),
        ),
        (
          "offset_ratio",
          format_scaled_seconds(value.config.offset_ratio_ppm, 6).quote_json(),
        ),
      ]),
    ),
    ("recording_id", value.recording_id.quote_json()),
    ("reference", event_json(value.reference)),
    ("prediction", event_json(value.prediction)),
    ("basis", basis_json(value.basis)),
  ])
  bounded_output(text, 16_777_216)
}
