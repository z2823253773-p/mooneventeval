// Catches decimal rounding, accidental Float parsing and cap off-by-one errors.

///|
test "decimal_exact" {
  for
    (text, expected) in [
      ("0", 0L),
      ("0.0", 0L),
      ("10.05", 10_050_000L),
      ("0.000001", 1L),
      ("1.234567", 1_234_567L),
      ("2592000", 2_592_000_000_000L),
      ("2592000.000000", 2_592_000_000_000L),
    ] {
    inspect(parse_time_us(text, "onset_s").unwrap() == expected, content="true")
  }
}

// Catches normalization/coercion of input that the grammar explicitly rejects.

///|
test "decimal_reject" {
  for
    text in [
      "", "01", "00", "1e-6", " 1", "1 ", "-0", "+1", ".1", "1.", "1.0000000", "1..0",
      "NaN", "Infinity", "１", "١", "1\n", "0x10",
    ] {
    match parse_time_us(text, "onset_s") {
      Err(error) => {
        inspect(error.code, content="INVALID_DECIMAL")
        inspect(error.path == Some("onset_s"), content="true")
      }
      Ok(_) => fail("invalid decimal accepted: " + text)
    }
  }
}

// Catches integer overflow before validation and invalid range/error mapping.

///|
test "decimal_range_and_long_input" {
  for
    text in [
      "2592000.000001", "2592001", "999999999999999999999999999999999999999999",
    ] {
    match parse_time_us(text, "offset_s") {
      Err(error) => {
        inspect(error.code, content="OUT_OF_RANGE")
        inspect(exit_code(error), content="2")
      }
      Ok(_) => fail("out-of-range time accepted")
    }
  }
  let huge = String::make(4096, '9')
  inspect(parse_time_us(huge, "offset_s") is Err(_), content="true")
  match parse_time_us(huge + "x", "offset_s") {
    Err(error) => inspect(error.code, content="INVALID_DECIMAL")
    Ok(_) => fail("malformed long decimal accepted")
  }
}

// Catches sharing the time cap with ratios, rejecting zero or wrong defaults.

///|
test "ratio_bounds" {
  inspect(parse_ratio_ppm("0", "ratio").unwrap() == 0L, content="true")
  inspect(parse_ratio_ppm("0.5", "ratio").unwrap() == 500_000L, content="true")
  inspect(
    parse_ratio_ppm("1.000000", "ratio").unwrap() == 1_000_000L,
    content="true",
  )
  for text in ["1.000001", "2", "2592000"] {
    match parse_ratio_ppm(text, "ratio") {
      Err(error) => inspect(error.code, content="OUT_OF_RANGE")
      Ok(_) => fail("out-of-range ratio accepted")
    }
  }
  let zero = config("0", "0").unwrap()
  inspect(zero.collar_us == 0L && zero.offset_ratio_ppm == 0L, content="true")
  let defaults = default_config()
  inspect(defaults.collar_us == 200_000L, content="true")
  inspect(defaults.offset_ratio_ppm == 500_000L, content="true")
  inspect(config("2592000.000001", "0.5") is Err(_), content="true")
  inspect(config("0.2", "1.000001") is Err(_), content="true")
}

// Catches factory bypasses, zero durations and code-unit/byte ID limits.

///|
test "event_factory_validation" {
  inspect(event("r", "alarm", "0", "0.000001") is Ok(_), content="true")
  inspect(event("r", "alarm", "2591999", "2592000") is Ok(_), content="true")
  for (onset, offset) in [("1", "1"), ("2", "1"), ("0", "2592001"), ("-1", "1")] {
    inspect(event("r", "alarm", onset, offset) is Err(_), content="true")
  }
  inspect(event("", "alarm", "0", "1") is Err(_), content="true")
  inspect(event("r", "", "0", "1") is Err(_), content="true")
  let id256 = String::make(256, '\u{10000}')
  inspect(event(id256, "alarm", "0", "1") is Ok(_), content="true")
  match event(id256 + "x", "alarm", "0", "1") {
    Err(error) => {
      inspect(error.code, content="RESOURCE_LIMIT")
      inspect(exit_code(error), content="3")
      inspect(
        error.limit == Some(256L) && error.observed == Some(257L),
        content="true",
      )
    }
    Ok(_) => fail("257 codepoint id accepted")
  }
  inspect(event("r", id256 + "x", "0", "1") is Err(_), content="true")
  let untrimmed = event(" ", " A ", "0", "1").unwrap()
  inspect(untrimmed.id == " " && untrimmed.label == " A ", content="true")
}
