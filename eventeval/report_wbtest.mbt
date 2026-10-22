///|
test "report_fractional_microsecond_and_canonical_signed_values" {
  inspect(format_scaled_seconds(1_500_000L, 12), content="0.0000015")
  inspect(format_scaled_seconds(-200_000L, 6), content="-0.2")
  inspect(format_scaled_seconds(0L, 12), content="0")
  inspect(
    format_scaled_seconds(2_592_000_000_000_000_000L, 12),
    content="2592000",
  )
}

///|
test "report_text_complete_selected_unmatched_and_undefined" {
  let e = event("e", "a", "1", "2").unwrap()
  let t = task(
    ["a", "unused"],
    [
      recording("empty", [], []).unwrap(),
      recording("x", [e], [
        e,
        event("p2", "a", "1", "2").unwrap(),
        event("far", "a", "10", "11").unwrap(),
      ]).unwrap(),
    ],
    default_config(),
  ).unwrap()
  let report = evaluate(t).unwrap()
  let text = report_text(report).unwrap()
  inspect(
    text.contains("所选配对") && text.contains("未定义"),
    content="true",
  )
  inspect(
    text.contains("TP=1") && text.contains("FP=2") && text.contains("FN=0"),
    content="true",
  )
  inspect(
    text.contains("unselected_in_maximum_matching") &&
    text.contains("no_eligible_candidate"),
    content="true",
  )
  inspect(
    text.contains("label=\"unused\"") && text.contains("recording=\"empty\""),
    content="true",
  )
  inspect(
    text.contains("candidate_count=1") && text.contains("candidate_count=0"),
    content="true",
  )
  inspect(text == report_text(report).unwrap(), content="true")
}

///|
test "report_json_explanation_identity_roundtrip_and_key_order" {
  let id = "r\u{0}\u{1}\n\"\\\u{10000}"
  let e = event(id, "a", "1", "2").unwrap()
  let t = task(["a"], [recording(id, [e], [e]).unwrap()], default_config()).unwrap()
  let explanation = explain_pair(t, id, id, id).unwrap()
  let json = explanation_json(explanation).unwrap()
  match @json.parse(json) {
    Object(fields) => {
      inspect(
        fields.keys().collect() ==
        [
          "schema_version", "semantics", "implementation_version", "status", "config",
          "recording_id", "reference", "prediction", "basis",
        ],
        content="true",
      )
      inspect(
        fields.get("recording_id") == Some(Json::string(id)),
        content="true",
      )
    }
    _ => fail("invalid explanation JSON")
  }
  let text = report_text(evaluate(t).unwrap()).unwrap()
  inspect(text.contains("\\u0001") && !text.contains("\u{1}"), content="true")
}

///|
test "report_legal_2000_event_capacity_and_text_identity_roundtrip" {
  let identity = String::make(256, '\u{9b}')
  let event = event(identity, identity, "0", "1").unwrap()
  let recordings = Array::makei(1000, i => {
    recording(String::make(250, '\u{9b}') + i.to_string(), [event], [event]).unwrap()
  })
  let input = task([identity], recordings, default_config()).unwrap()
  let result = evaluate(input).unwrap()
  inspect(
    result.metrics().counts.tp == 1000 && result.matching_steps == 3000L,
    content="true",
  )
  let json = report_json(result).unwrap()
  let text = report_text(result).unwrap()
  let json_bytes = @utf8.encode(json).length()
  let text_bytes = @utf8.encode(text).length()
  inspect(json_bytes <= 16_777_216 && text_bytes <= 16_777_216, content="true")
  inspect(text.contains("\u{9b}"), content="false")
  println(
    "{\"capacity\":\"legal-2000-events-c1-identities\",\"recordings\":1000,\"events\":2000,\"json_bytes\":\{json_bytes},\"text_bytes\":\{text_bytes},\"tp\":1000,\"matching_steps\":3000}",
  )
}
