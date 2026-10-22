// Catches disagreement with graph eligibility, accidental selected-identity inference,
// missing same-recording lookup and loss of signed/exact time basis.

///|
fn explain_task(
  refs : Array[Event],
  preds : Array[Event],
  cfg : Config,
) -> Task {
  task(["a", "b"], [recording("x", refs, preds).unwrap()], cfg).unwrap()
}

///|
test "explain_onset_boundary_and_same_basis_as_match" {
  let r = event("r", "a", "10", "12").unwrap()
  let p = event("p", "a", "10.2", "12.2").unwrap()
  let t = explain_task([r], [p], default_config())
  let e = explain_pair(t, "x", "r", "p").unwrap()
  inspect(e.basis.eligible && e.basis.onset_pass, content="true")
  inspect(e.basis.onset_delta_us == 200_000L, content="true")
  let evaluation = evaluate(t).unwrap()
  inspect(
    basis_json(e.basis) == basis_json(evaluation.matches[0].basis),
    content="true",
  )
  let t = explain_task(
    [r],
    [event("p", "a", "10.200001", "12.2").unwrap()],
    default_config(),
  )
  inspect(
    explain_pair(t, "x", "r", "p").unwrap().basis.eligible,
    content="false",
  )
}

///|
test "explain_unselected_eligible_and_label_mismatch" {
  let r = event("r", "a", "1", "2").unwrap()
  let t = explain_task(
    [r],
    [
      event("p1", "a", "1", "2").unwrap(),
      event("p2", "a", "1", "2").unwrap(),
      event("p3", "b", "1", "2").unwrap(),
    ],
    default_config(),
  )
  inspect(
    evaluate(t).unwrap().pairs() == [("x", "a", "r", "p1")],
    content="true",
  )
  let e = explain_pair(t, "x", "r", "p2").unwrap()
  inspect(e.basis.eligible, content="true")
  let json = explanation_json(e).unwrap()
  inspect(
    json.contains("\"summary\"") ||
    json.contains("\"work\"") ||
    json.contains("\"matches\""),
    content="false",
  )
  let mismatch = explain_pair(t, "x", "r", "p3").unwrap()
  inspect(
    mismatch.basis.label_match || mismatch.basis.eligible,
    content="false",
  )
  inspect(
    mismatch.basis.onset_pass && mismatch.basis.offset_pass,
    content="true",
  )
  let far = explain_task(
    [r],
    [event("far", "a", "10", "11").unwrap()],
    default_config(),
  )
  inspect(
    explain_pair(far, "x", "r", "far").unwrap().basis.eligible,
    content="false",
  )
}

///|
test "explain_missing_ids_do_not_cross_recordings" {
  let e = event("same", "a", "1", "2").unwrap()
  let t = task(
    ["a"],
    [recording("r", [e], []).unwrap(), recording("p", [], [e]).unwrap()],
    default_config(),
  ).unwrap()
  for
    pair in [
      ("absent", "same", "same", "recording_id"),
      ("r", "absent", "same", "reference_id"),
      ("r", "same", "same", "prediction_id"),
    ] {
    match explain_pair(t, pair.0, pair.1, pair.2) {
      Ok(_) => fail("unknown or cross-recording event was selected")
      Err(error) => {
        inspect(error.code, content="ID_NOT_FOUND")
        inspect(
          exit_code(error) == 2 && error.path == Some(pair.3),
          content="true",
        )
      }
    }
  }
}

///|
test "explain_fractional_and_negative_threshold_text" {
  let t = explain_task(
    [event("r", "a", "10", "10.000003").unwrap()],
    [event("p", "a", "10", "10.000004").unwrap()],
    config("0", "0.5").unwrap(),
  )
  let e = explain_pair(t, "x", "r", "p").unwrap()
  inspect(
    explanation_json(e).unwrap().contains("\"offset_limit_s\":\"0.0000015\""),
    content="true",
  )
  let t = explain_task(
    [event("r", "a", "10", "12").unwrap()],
    [event("p", "a", "9.8", "11.8").unwrap()],
    default_config(),
  )
  let text = explanation_text(explain_pair(t, "x", "r", "p").unwrap()).unwrap()
  inspect(
    text.contains("onset_delta_s=-0.2") && text.contains("offset_delta_s=-0.2"),
    content="true",
  )
  inspect(
    text.contains("是否被选中") && !text.contains("TP="),
    content="true",
  )
}
