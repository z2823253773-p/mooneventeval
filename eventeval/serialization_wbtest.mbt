// Test-only adapter exercises the product's common byte gate after standard
// JSON serialization, without adding an unused runtime helper or public knob.

///|
fn bounded_serialize(
  value : Json,
  byte_limit : Int,
) -> Result[String, EvalError] {
  bounded_output(value.stringify(), byte_limit)
}

// Catches UTF16-character counting instead of final UTF8 bytes and off-by-one caps.

///|
test "serialization_utf8_escaping_equal_and_plus_one" {
  let value = Json::string("中")
  let text = bounded_serialize(value, 5).unwrap()
  inspect(@utf8.encode(text) == b"\x22\xe4\xb8\xad\x22", content="true")
  match bounded_serialize(value, 4) {
    Ok(_) => fail("UTF8 output limit ignored")
    Err(e) =>
      inspect(
        exit_code(e) == 3 && e.limit == Some(4L) && e.observed == Some(5L),
        content="true",
      )
  }
  let control = Json::string("\u{0}")
  inspect(
    @utf8.encode(bounded_serialize(control, 8).unwrap()).length() == 8,
    content="true",
  )
  inspect(bounded_serialize(control, 7) is Err(_), content="true")
  inspect(bounded_serialize(Json::string(""), 2) is Ok(_), content="true")
  inspect(bounded_serialize(Json::string(""), 1) is Err(_), content="true")
}

///|
test "serialization_real_16MiB_equal_and_plus_one" {
  let limit = 16_777_216
  let at = bounded_serialize(Json::string(String::make(limit - 2, 'a')), limit).unwrap()
  inspect(@utf8.encode(at).length() == limit, content="true")
  match bounded_serialize(Json::string(String::make(limit - 1, 'a')), limit) {
    Ok(_) => fail("16MiB plus one accepted")
    Err(e) => {
      inspect(e.code, content="RESOURCE_LIMIT")
      inspect(
        e.limit == Some(16_777_216L) && e.observed == Some(16_777_217L),
        content="true",
      )
    }
  }
}

///|
test "serialization_identity_quote_roundtrip_controls_and_direction" {
  let id = "中文\"\\\n\u{0}\u{7f}\u{85}\u{9b}\u{61c}\u{2028}\u{2029}\u{202e}\u{2066}\u{10000}"
  let quoted = text_identity(id)
  inspect(@json.parse(quoted) == Json::string(id), content="true")
  for ch in quoted.iter() {
    let code = ch.to_int()
    inspect(
      code >= 32 &&
      !(code >= 127 && code <= 159) &&
      code != 0x061C &&
      code != 0x2028 &&
      code != 0x2029 &&
      code != 0x202e &&
      code != 0x2066,
      content="true",
    )
  }
  inspect(quoted.contains("中文"), content="true")
}
