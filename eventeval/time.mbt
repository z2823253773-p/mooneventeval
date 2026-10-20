///|
/// Scan ASCII decimals without floating point or unbounded integer accumulation.
/// Syntax is checked even after the range flag is set; malformed input stays a
/// decimal error. Only a bounded prefix is ever multiplied.
fn parse_decimal_scaled(
  text : String,
  path : String,
  max_whole : Int64,
) -> Result[Int64, EvalError] {
  let mut whole = 0L
  let mut fraction = 0L
  let mut fraction_digits = 0
  let mut has_whole = false
  let mut leading_zero = false
  let mut decimal_point = false
  let mut too_large = false
  for ch in text.iter() {
    if ch == '.' && !decimal_point && has_whole {
      decimal_point = true
      continue
    }
    if ch < '0' || ch > '9' {
      return Err(
        input_error(
          "INVALID_DECIMAL", "Expected an ASCII decimal string with at most six fractional digits",
          path,
        ),
      )
    }
    let digit = (ch.to_int() - 48).to_int64()
    if decimal_point {
      fraction_digits = fraction_digits + 1
      if fraction_digits > 6 {
        return Err(
          input_error(
            "INVALID_DECIMAL", "Expected at most six fractional digits", path,
          ),
        )
      }
      fraction = fraction * 10L + digit
    } else {
      if leading_zero {
        return Err(
          input_error("INVALID_DECIMAL", "Leading zeros are not allowed", path),
        )
      }
      // Only presence is needed, so even huge integers cannot overflow a counter.
      has_whole = true
      leading_zero = whole == 0L && digit == 0L && !too_large
      if !too_large {
        if whole > max_whole / 10L ||
          (whole == max_whole / 10L && digit > max_whole % 10L) {
          too_large = true
        } else {
          whole = whole * 10L + digit
        }
      }
    }
  }
  if !has_whole || (decimal_point && fraction_digits == 0) {
    return Err(
      input_error("INVALID_DECIMAL", "Expected an ASCII decimal string", path),
    )
  }
  if too_large {
    return Err(
      input_error("OUT_OF_RANGE", "Decimal exceeds the allowed range", path),
    )
  }
  while fraction_digits < 6 {
    fraction = fraction * 10L
    fraction_digits = fraction_digits + 1
  }
  // max_whole is one of 2592000 or 1; these products are safely inside Int64.
  let scaled = whole * 1_000_000L + fraction
  if scaled > max_whole * 1_000_000L {
    Err(input_error("OUT_OF_RANGE", "Decimal exceeds the allowed range", path))
  } else {
    Ok(scaled)
  }
}

///|
fn parse_time_us(text : String, path : String) -> Result[Int64, EvalError] {
  parse_decimal_scaled(text, path, 2_592_000L)
}

///|
fn parse_ratio_ppm(text : String, path : String) -> Result[Int64, EvalError] {
  parse_decimal_scaled(text, path, 1L)
}

///|
/// Compare Unicode scalar values, rather than native String's representation.
#warnings("-unused_value")
fn compare_codepoints(a : String, b : String) -> Int {
  let left = a.iter()
  let right = b.iter()
  for x = left.next(), y = right.next() {
    match (x, y) {
      (None, None) => break 0
      (None, Some(_)) => break -1
      (Some(_), None) => break 1
      (Some(a), Some(b)) => {
        if a.to_int() < b.to_int() {
          break -1
        }
        if a.to_int() > b.to_int() {
          break 1
        }
        continue left.next(), right.next()
      }
    }
  }
}
