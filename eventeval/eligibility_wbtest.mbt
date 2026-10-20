// Catches using < at the onset boundary or accidentally rounding one microsecond.

///|
test "eligibility_A3_onset_boundary" {
  let r = event("r", "a", "10", "12").unwrap()
  let cfg = default_config()
  let equal = eligibility(r, event("p", "a", "10.2", "12").unwrap(), cfg)
  inspect(equal.onset_pass && equal.eligible, content="true")
  inspect(equal.onset_delta_us == 200_000L, content="true")
  inspect(
    eligibility(r, event("p", "a", "10.200001", "12").unwrap(), cfg).eligible,
    content="false",
  )
  let early = eligibility(r, event("p", "a", "9.8", "12").unwrap(), cfg)
  inspect(early.onset_delta_us == -200_000L && early.eligible, content="true")
}

// Catches <, min/sum, prediction-duration and collar/ratio confusion.

///|
test "eligibility_A4_offset_boundary_and_reference_duration" {
  let r = event("r", "a", "10", "12").unwrap()
  let equal = eligibility(
    r,
    event("p", "a", "10", "13").unwrap(),
    default_config(),
  )
  inspect(equal.offset_limit_scaled == 1_000_000_000_000L, content="true")
  inspect(equal.offset_pass && equal.eligible, content="true")
  inspect(
    eligibility(
      r,
      event("p", "a", "10", "13.000001").unwrap(),
      default_config(),
    ).eligible,
    content="false",
  )
  let shortened = eligibility(
    r,
    event("p", "a", "10", "11").unwrap(),
    default_config(),
  )
  inspect(
    shortened.offset_delta_us == -1_000_000L && shortened.eligible,
    content="true",
  )
  inspect(
    eligibility(
      r,
      event("p", "a", "10", "10.999999").unwrap(),
      default_config(),
    ).eligible,
    content="false",
  )
}

// Catches an added interval-overlap requirement and failure to use max(collar,ratio).

///|
test "eligibility_collar_dominates_without_overlap" {
  let r = event("r", "a", "0", "0.1").unwrap()
  let p = event("p", "a", "0.2", "0.3").unwrap()
  let basis = eligibility(r, p, default_config())
  inspect(basis.offset_limit_scaled == 200_000_000_000L, content="true")
  inspect(basis.eligible, content="true")
  inspect(
    eligibility(
      r,
      event("p", "a", "0.2", "0.300001").unwrap(),
      default_config(),
    ).eligible,
    content="false",
  )
}

// Catches whole-microsecond rounding of the 1.5us reference-duration threshold.

///|
test "eligibility_R3_fractional_microsecond" {
  let r = event("r", "a", "10", "10.000003").unwrap()
  let cfg = config("0", "0.5").unwrap()
  let one = eligibility(r, event("p", "a", "10", "10.000004").unwrap(), cfg)
  inspect(one.offset_limit_scaled == 1_500_000L, content="true")
  inspect(one.offset_delta_us == 1L && one.eligible, content="true")
  inspect(
    eligibility(r, event("p", "a", "10", "10.000005").unwrap(), cfg).eligible,
    content="false",
  )
}

// Catches arithmetic overflow near the maximum permitted cross product.

///|
test "eligibility_maximum_scaled_and_zero_tolerances" {
  let r = event("r", "a", "0", "2592000").unwrap()
  let p = event("p", "a", "0.000001", "0.000002").unwrap()
  let basis = eligibility(r, p, config("2592000", "1").unwrap())
  inspect(
    basis.offset_limit_scaled == 2_592_000_000_000_000_000L,
    content="true",
  )
  inspect(basis.eligible, content="true")
  let short = event("r", "a", "0", "1").unwrap()
  inspect(
    eligibility(short, short, config("0", "0").unwrap()).eligible,
    content="true",
  )
  inspect(
    eligibility(
      short,
      event("p", "a", "0", "1.000001").unwrap(),
      config("0", "0").unwrap(),
    ).eligible,
    content="false",
  )
}

// Catches treating IDs as labels, normalizing labels or suppressing timing basis.

///|
test "eligibility_label_and_id_rules" {
  let r = event("same", "A", "1", "2").unwrap()
  let p = event("same", "a", "1", "2").unwrap()
  let basis = eligibility(r, p, default_config())
  inspect(basis.label_match || basis.eligible, content="false")
  inspect(basis.onset_pass && basis.offset_pass, content="true")
  inspect(
    eligibility(r, event("different", "A", "1", "2").unwrap(), default_config()).eligible,
    content="true",
  )
}

// Catches UTF-16 ordering, prefix reversal and normalization of distinct strings.

///|
test "codepoints_R1_ordering" {
  inspect(compare_codepoints("\u{E000}", "\u{10000}") < 0, content="true")
  inspect(compare_codepoints("\u{10000}", "\u{E000}") > 0, content="true")
  inspect(compare_codepoints("a", "aa") < 0, content="true")
  inspect(compare_codepoints("aa", "a") > 0, content="true")
  inspect(compare_codepoints("", "") == 0, content="true")
  inspect(compare_codepoints("a\u{10000}", "a\u{10000}") == 0, content="true")
  inspect(compare_codepoints("é", "e\u{301}") > 0, content="true")
}
