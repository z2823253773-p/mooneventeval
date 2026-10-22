// Catches duplicate TP, local greedy, missing empty/isolated groups, aliasing and unstable sorting.

///|
fn evaluation_of(
  reference : Array[Event],
  prediction : Array[Event],
) -> Evaluation {
  evaluate(
    task(
      ["a"],
      [recording("x", reference, prediction).unwrap()],
      default_config(),
    ).unwrap(),
  ).unwrap()
}

///|
test "evaluation_A1_duplicate_and_A2_augment" {
  let e = evaluation_of([event("r", "a", "10", "12").unwrap()], [
    event("p1", "a", "10", "12").unwrap(),
    event("p2", "a", "10.05", "12.05").unwrap(),
  ])
  let c = e.metrics().counts
  inspect((c.tp, c.fp, c.fn_count) == (1, 1, 0), content="true")
  inspect(
    e.metrics().precision == Some(0.5) && e.metrics().recall == Some(1.0),
    content="true",
  )
  inspect(e.metrics().f1 == Some(2.0 / 3.0), content="true")
  inspect(e.pairs() == [("x", "a", "r", "p1")], content="true")
  let trap = evaluation_of(
    [
      event("r1", "a", "10", "11").unwrap(),
      event("r2", "a", "10.3", "11.3").unwrap(),
    ],
    [
      event("p1", "a", "10.15", "11.15").unwrap(),
      event("p2", "a", "9.85", "10.85").unwrap(),
    ],
  )
  inspect(
    trap.pairs() == [("x", "a", "r1", "p2"), ("x", "a", "r2", "p1")],
    content="true",
  )
}

///|
test "evaluation_empty_denominators_and_no_edges" {
  let a = event("e", "a", "1", "2").unwrap()
  let b = event("e", "a", "3", "4").unwrap()
  let empty = evaluation_of([], []).metrics()
  inspect(
    empty.precision == None && empty.recall == None && empty.f1 == None,
    content="true",
  )
  let fp = evaluation_of([], [a]).metrics()
  inspect(
    fp.precision == Some(0.0) && fp.recall == None && fp.f1 == Some(0.0),
    content="true",
  )
  let fn_only = evaluation_of([a], []).metrics()
  inspect(
    fn_only.precision == None &&
    fn_only.recall == Some(0.0) &&
    fn_only.f1 == Some(0.0),
    content="true",
  )
  let none = evaluation_of([a], [b]).metrics()
  inspect(
    none.precision == Some(0.0) &&
    none.recall == Some(0.0) &&
    none.f1 == Some(0.0),
    content="true",
  )
}

///|
test "evaluation_copy_and_reorder_codepoints" {
  let r = event("\u{10000}", "a", "1", "2").unwrap()
  let other = event("\u{E000}", "a", "1", "2").unwrap()
  let refs = [r, other]
  let preds = [
    event("p2", "a", "1", "2").unwrap(),
    event("p1", "a", "1", "2").unwrap(),
  ]
  let rec = recording("x", refs, preds).unwrap()
  refs.clear()
  preds.clear()
  let recs = [rec]
  let labels = ["a"]
  let input = task(labels, recs, default_config()).unwrap()
  labels.clear()
  recs.clear()
  let result = evaluate(input).unwrap()
  inspect(
    result.pairs() ==
    [("x", "a", "\u{E000}", "p1"), ("x", "a", "\u{10000}", "p2")],
    content="true",
  )
  let returned = result.pairs()
  returned.clear()
  inspect(result.pairs().length() == 2, content="true")
  let reordered = task(
    ["a"],
    [
      recording("x", [other, r], [
        event("p1", "a", "1", "2").unwrap(),
        event("p2", "a", "1", "2").unwrap(),
      ]).unwrap(),
    ],
    default_config(),
  ).unwrap()
  inspect(
    report_json(result).unwrap() ==
    report_json(evaluate(reordered).unwrap()).unwrap(),
    content="true",
  )
}

///|
test "evaluation_group_isolation_and_micro_counts" {
  let a = event("r", "a", "1", "2").unwrap()
  let b = event("p", "b", "1", "2").unwrap()
  let t = task(
    ["unused", "b", "a"],
    [recording("y", [], [a]).unwrap(), recording("x", [a], [b]).unwrap()],
    default_config(),
  ).unwrap()
  let e = evaluate(t).unwrap()
  inspect(
    (e.metrics().counts.tp, e.metrics().counts.fp, e.metrics().counts.fn_count) ==
    (0, 2, 1),
    content="true",
  )
  let json = report_json(e).unwrap()
  inspect(json.contains("\"by_label\":[{\"label\":\"a\""), content="true")
  inspect(
    json.contains("\"candidate_count\":0,\"reason\":\"no_eligible_candidate\""),
    content="true",
  )
}

///|
test "evaluation_full_report_basis_and_failure_json" {
  let e = evaluate(
    task(
      ["a"],
      [
        recording("x", [event("r", "a", "10", "10.000003").unwrap()], [
          event("p", "a", "10", "10.000004").unwrap(),
        ]).unwrap(),
      ],
      config("0", "0.5").unwrap(),
    ).unwrap(),
  ).unwrap()
  let json = report_json(e).unwrap()
  inspect(json.contains("\"offset_limit_s\":\"0.0000015\""), content="true")
  inspect(
    json.contains("\"onset_delta_s\":\"0\",\"offset_delta_s\":\"0.000001\""),
    content="true",
  )
  inspect(
    json.contains(
      "\"work\":{\"candidate_checks\":1,\"eligible_edges\":1,\"matching_steps\":3}",
    ),
    content="true",
  )
  let error = input_error("INVALID_SCHEMA", "bad", "$")
  inspect(
    error_json(error),
    content="{\"schema_version\":1,\"status\":\"failed\",\"error\":{\"kind\":\"input\",\"code\":\"INVALID_SCHEMA\",\"message\":\"bad\",\"path\":\"$\",\"limit\":null,\"observed\":null}}",
  )
}

///|
test "evaluation_shared_budget_fails_whole_task" {
  let e = event("e", "a", "0", "1").unwrap()
  let t = task(
    ["a"],
    [recording("x", [e], [e]).unwrap(), recording("y", [e], [e]).unwrap()],
    default_config(),
  ).unwrap()
  let budget : WorkBudget = { used: 0L, limit: 5L, }
  match evaluate_with_budget(t, budget) {
    Ok(_) => fail("partial task returned Evaluation")
    Err(error) => {
      inspect(exit_code(error) == 3 && budget.used == 5L, content="true")
      let json = error_json(error)
      inspect(
        json.contains("\"summary\"") || json.contains("\"matches\""),
        content="false",
      )
    }
  }
  let done = evaluate(t).unwrap()
  inspect(done.matching_steps == 6L, content="true")
}

///|
test "evaluation_micro_is_not_mean_and_row_totals_reconcile" {
  let e = event("e", "a", "0", "1").unwrap()
  let miss = event("m", "a", "3", "4").unwrap()
  let t = task(
    ["a", "unused"],
    [recording("x", [e], [e]).unwrap(), recording("y", [], [e, miss]).unwrap()],
    default_config(),
  ).unwrap()
  let result = evaluate(t).unwrap()
  inspect(result.metrics().f1 == Some(0.5), content="true")
  for rows in [result.by_label, result.by_recording] {
    let mut r = 0
    let mut p = 0
    let mut tp = 0
    let mut fp = 0
    let mut fn_count = 0
    for row in rows {
      let c = row.1.counts
      r = r + c.reference
      p = p + c.prediction
      tp = tp + c.tp
      fp = fp + c.fp
      fn_count = fn_count + c.fn_count
    }
    inspect((r, p, tp, fp, fn_count) == (1, 3, 1, 2, 0), content="true")
  }
}

///|
test "evaluation_json_control_characters_roundtrip_success_and_error" {
  let controls = "\u{0}\u{1}\u{2}\u{3}\u{4}\u{5}\u{6}\u{7}\u{8}\u{9}\u{a}\u{b}\u{c}\u{d}\u{e}\u{f}\u{10}\u{11}\u{12}\u{13}\u{14}\u{15}\u{16}\u{17}\u{18}\u{19}\u{1a}\u{1b}\u{1c}\u{1d}\u{1e}\u{1f}\"\\\u{10000}"
  let e = event(controls, controls, "0", "1").unwrap()
  let result = evaluate(
    task([controls], [recording(controls, [e], [e]).unwrap()], default_config()).unwrap(),
  ).unwrap()
  let json = report_json(result).unwrap()
  // Valid JSON must parse, unlike MoonBit's \u{xx} display syntax.
  let parsed = @json.parse(json)
  match parsed {
    Object(fields) =>
      match fields.get("by_label").unwrap() {
        Array(rows) =>
          match rows[0] {
            Object(row) =>
              inspect(
                row.get("label") == Some(Json::string(controls)),
                content="true",
              )
            _ => fail("invalid by_label row")
          }
        _ => fail("invalid by_label")
      }
    _ => fail("invalid report")
  }
  let error : EvalError = {
    kind: Input,
    code: controls,
    message: controls,
    path: Some(controls),
    limit: None,
    observed: None,
  }
  match @json.parse(error_json(error)) {
    Object(fields) =>
      match fields.get("error").unwrap() {
        Object(body) => {
          inspect(
            body.get("code") == Some(Json::string(controls)),
            content="true",
          )
          inspect(
            body.get("message") == Some(Json::string(controls)),
            content="true",
          )
          inspect(
            body.get("path") == Some(Json::string(controls)),
            content="true",
          )
        }
        _ => fail("invalid error object")
      }
    _ => fail("invalid failed report")
  }
}
