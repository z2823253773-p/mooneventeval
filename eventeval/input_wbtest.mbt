// Catches permissive/coercing schema, bad encoding, incomplete factories and wrong limits.

///|
fn input_error_is(text : String, code : String, path : String?) -> Unit raise {
  match decode_task(@utf8.encode(text)) {
    Ok(_) => fail("invalid task was accepted")
    Err(error) => {
      inspect(error.code == code, content="true")
      inspect(error.path == path, content="true")
    }
  }
}

///|
test "input_schema_and_default_config" {
  let t = decode_task(
    b"{\"schema_version\":1,\"labels\":[\"a\"],\"recordings\":[]}",
  ).unwrap()
  let report = report_json(evaluate(t).unwrap()).unwrap()
  inspect(
    report.contains("\"collar_s\":\"0.2\",\"offset_ratio\":\"0.5\""),
    content="true",
  )
  input_error_is("{}", "MISSING_FIELD", Some("schema_version"))
  input_error_is("[]", "INVALID_TYPE", Some("$"))
  input_error_is(
    "{\"schema_version\":2,\"labels\":[\"a\"],\"recordings\":[]}",
    "INVALID_SCHEMA",
    Some("schema_version"),
  )
  input_error_is(
    "{\"schema_version\":1,\"labels\":[],\"recordings\":[]}",
    "INVALID_SCHEMA",
    Some("labels"),
  )
  input_error_is(
    "{\"schema_version\":1,\"labels\":[\"a\"],\"recordings\":[],\"typo\":0}",
    "UNKNOWN_FIELD",
    Some("typo"),
  )
  input_error_is(
    "{\"schema_version\":1,\"labels\":[\"a\"],\"recordings\":[],\"config\":{\"collar_s\":0.2}}",
    "INVALID_TYPE",
    Some("config.collar_s"),
  )
}

///|
test "input_encoding_syntax_duplicates_and_bom" {
  match decode_task(b"\xFF") {
    Ok(_) => fail("bad UTF8 accepted")
    Err(e) => inspect(e.code, content="INVALID_UTF8")
  }
  input_error_is("{", "INVALID_JSON", Some("$"))
  input_error_is("\"\\uD800\"", "INVALID_JSON", Some("$"))
  let t = decode_task(
    b"\xEF\xBB\xBF{\"schema_version\":1,\"labe\\u006cs\":[\"a\"],\"recordings\":[]}",
  ).unwrap()
  inspect(t.labels == ["a"], content="true")
  input_error_is(
    "{\"schema_version\":1,\"labels\":[\"a\",\"a\"],\"recordings\":[]}",
    "DUPLICATE_ID",
    Some("labels[1]"),
  )
}

///|
test "input_duplicate_keys_rejected_before_schema" {
  for
    text in [
      "{\"schema_version\":2,\"schema_version\":1,\"labels\":[\"a\"],\"recordings\":[]}",
      "{\"schema_version\":2,\"schema_versio\\u006e\":1,\"labels\":[\"a\"],\"recordings\":[]}",
      "{\"schema_version\":1,\"labels\":[\"a\"],\"recordings\":[],\"config\":{\"collar_s\":\"0.1\",\"collar_s\":\"0.2\"}}",
      "{\"unused\":{\"x\":1,\"x\":2}}", "{\"é\":1,\"\\u00e9\":2}", "{\"😀\":1,\"\\ud83d\\ude00\":2}",
      "{\"a\":{\"x\":1},\"a\":2}", "{\"a\":[{\"x\":1}],\"a\":2}", "{\"a/b\":1,\"a\\/b\":2}",
      "{\"a\\\"b\":1,\"a\\u0022b\":2}", "{\"a\\\\b\":1,\"a\\u005cb\":2}", "{\"\\n\":1,\"\\u000a\":2}",
      "{\"\\u0000\":1,\"\\u0000\":2}", "[{\"a\":1},{\"b\":{\"x\":1,\"x\":2}}]",
    ] {
    input_error_is(text, "DUPLICATE_KEY", Some("$"))
    match evaluate_json(@utf8.encode(text)) {
      Ok(_) => fail("duplicate-key task was scored")
      Err(error) => {
        inspect(exit_code(error) == 2, content="true")
        inspect(
          error_json(error).contains("\"status\":\"failed\""),
          content="true",
        )
        inspect(!error_json(error).contains("\"summary\""), content="true")
      }
    }
  }
}

///|
test "input_duplicate_keys_do_not_merge_scopes_or_values" {
  input_error_is(
    "{\"x\":{\"id\":1},\"y\":{\"id\":2}}",
    "UNKNOWN_FIELD",
    Some("x"),
  )
  input_error_is("{\"x\":[{\"id\":1},{\"id\":2}]}", "UNKNOWN_FIELD", Some("x"))
  input_error_is(
    "{\"é\":1,\"e\\u0301\":2}",
    "UNKNOWN_FIELD",
    Some("e\u{0301}"),
  )
  input_error_is(
    "{\"x\":\"{\\\"x\\\":1,\\\"x\\\":2}\"}",
    "UNKNOWN_FIELD",
    Some("x"),
  )
  // Event field names repeat across distinct objects; event IDs can contain
  // quotes, braces, slashes and key-like text without becoming JSON structure.
  let id = "brace{} : \\\"id\\\": \\".quote_json()
  let ev = "{\"id\":" +
    id +
    ",\"label\":\"a\",\"onset_s\":\"1\",\"offset_s\":\"2\"}"
  let text = "{\"schema_version\":1,\"labels\":[\"a\"],\"recordings\":[{\"id\":\"x\",\"reference\":[" +
    ev +
    "],\"prediction\":[" +
    ev +
    "]}]}"
  let result = evaluate(decode_task(@utf8.encode(text)).unwrap()).unwrap()
  inspect(result.metrics().counts.tp == 1, content="true")
}

///|
test "input_duplicate_keys_preserve_encoding_syntax_resource_priority" {
  input_error_is("{\"x\":1,\"x\":2,}", "INVALID_JSON", Some("$"))
  input_error_is("{\"x\":1,\"x\":\"\\ud800\"}", "INVALID_JSON", Some("$"))
  input_error_is(
    "{\"x\":0,\"x\":" +
    String::make(16, '[') +
    "0" +
    String::make(16, ']') +
    "}",
    "RESOURCE_LIMIT",
    Some("$"),
  )
  match decode_task(b"{\"x\":1,\"x\":2}\xff") {
    Ok(_) => fail("invalid UTF-8 accepted")
    Err(error) => inspect(error.code, content="INVALID_UTF8")
  }
}

///|
test "input_duplicate_keys_bound_diagnostic_preview" {
  for bom in ["", "\u{feff}"] {
    // The second quote is at UTF-16 index 8, despite the first key being one
    // Unicode scalar; the optional BOM is removed before offset accounting.
    let text = bom + "{\"😀\":1,\"\\ud83d\\ude00\":2}"
    match decode_task(@utf8.encode(text)) {
      Ok(_) => fail("escaped duplicate accepted")
      Err(error) =>
        inspect(
          error.message.has_suffix("offset 8 (zero-based)"),
          content="true",
        )
    }
  }
  let key = String::make(100_000, '😀')
  let text = "{\"" + key + "\":1,\"" + key + "\":2}"
  match decode_task(@utf8.encode(text)) {
    Ok(_) => fail("large duplicate key accepted")
    Err(error) => {
      inspect(error.code, content="DUPLICATE_KEY")
      inspect(@utf8.encode(error.message).length() < 1024, content="true")
      inspect(@json.parse(error_json(error)) is Object(_), content="true")
    }
  }
}

///|
test "input_event_paths_and_isolation" {
  let prefix = "{\"schema_version\":1,\"labels\":[\"a\"],\"recordings\":[{\"id\":\"x\",\"reference\":["
  let suffix = "],\"prediction\":[]}]}"
  input_error_is(
    prefix +
    "{\"id\":\"r\",\"label\":\"a\",\"onset_s\":1,\"offset_s\":\"2\"}" +
    suffix,
    "INVALID_TYPE",
    Some("recordings[0].reference[0].onset_s"),
  )
  input_error_is(
    prefix +
    "{\"id\":\"r\",\"label\":\"a\",\"onset_s\":\"1.0000001\",\"offset_s\":\"2\"}" +
    suffix,
    "INVALID_DECIMAL",
    Some("recordings[0].reference[0].onset_s"),
  )
  input_error_is(
    prefix +
    "{\"id\":\"r\",\"label\":\"b\",\"onset_s\":\"1\",\"offset_s\":\"2\"}" +
    suffix,
    "UNKNOWN_LABEL",
    Some("recordings[0].reference[0].label"),
  )
  let e = event("same", "a", "1", "2").unwrap()
  inspect(
    task(["a"], [recording("x", [e], [e]).unwrap()], default_config()) is Ok(_),
    content="true",
  )
  match recording("x", [e, e], []) {
    Ok(_) => fail("duplicate event accepted")
    Err(e) => inspect(e.code, content="DUPLICATE_ID")
  }
  let rec = recording("x", [e], []).unwrap()
  match task(["a"], [rec, rec], default_config()) {
    Ok(_) => fail("duplicate recording accepted")
    Err(e) => inspect(e.code, content="DUPLICATE_ID")
  }
}

///|
test "input_resource_equal_and_plus_one" {
  let empty = "{\"schema_version\":1,\"labels\":[\"a\"],\"recordings\":[]}"
  inspect(
    decode_task(
      @utf8.encode(empty + String::make(8_388_608 - empty.length(), ' ')),
    )
    is Ok(_),
    content="true",
  )
  match
    decode_task(
      @utf8.encode(empty + String::make(8_388_609 - empty.length(), ' ')),
    ) {
    Ok(_) => fail("byte limit accepted")
    Err(e) => {
      inspect(exit_code(e) == 3, content="true")
      inspect(e.limit == Some(8_388_608L), content="true")
    }
  }
  input_error_is(
    String::make(17, '[') + "0" + String::make(17, ']'),
    "RESOURCE_LIMIT",
    Some("$"),
  )
  input_error_is(
    String::make(16, '[') + "0" + String::make(16, ']'),
    "INVALID_TYPE",
    Some("$"),
  )
  let labels = Array::makei(256, i => "l\{i}")
  inspect(task(labels, [], default_config()) is Ok(_), content="true")
  labels.push("extra")
  match task(labels, [], default_config()) {
    Ok(_) => fail("label limit accepted")
    Err(e) => inspect(exit_code(e) == 3, content="true")
  }
  let recs = Array::makei(1000, i => recording("r\{i}", [], []).unwrap())
  inspect(task(["a"], recs, default_config()) is Ok(_), content="true")
  recs.push(recording("extra", [], []).unwrap())
  match task(["a"], recs, default_config()) {
    Ok(_) => fail("recording limit accepted")
    Err(e) => inspect(exit_code(e) == 3, content="true")
  }
  let events = Array::makei(2000, i => event("e\{i}", "a", "0", "1").unwrap())
  let rec = recording("x", events, []).unwrap()
  inspect(task(["a"], [rec], default_config()) is Ok(_), content="true")
  match
    task(
      ["a"],
      [rec, recording("y", [events[0]], []).unwrap()],
      default_config(),
    ) {
    Ok(_) => fail("total event limit accepted")
    Err(e) => inspect(exit_code(e) == 3, content="true")
  }
}

///|
test "input_empty_labels_precedes_event_membership" {
  input_error_is(
    "{\"schema_version\":1,\"labels\":[],\"recordings\":[{\"id\":\"x\",\"reference\":[{\"id\":\"r\",\"label\":\"a\",\"onset_s\":\"1\",\"offset_s\":\"2\"}],\"prediction\":[]}]}",
    "INVALID_SCHEMA",
    Some("labels"),
  )
}
