///|
fn format_scaled_seconds(value : Int64, digits : Int) -> String {
  let sign = if value < 0L { "-" } else { "" }
  let number = if value < 0L { -value } else { value }
  let mut factor = 1L
  for _ in 0..<digits {
    factor = factor * 10L
  }
  let whole = (number / factor).to_string()
  let remainder = number % factor
  if remainder == 0L {
    return sign + whole
  }
  let fraction = remainder.to_string()
  let padded = String::make(digits - fraction.length(), '0') + fraction
  let chars = padded.to_array()
  while chars.last() == Some('0') {
    ignore(chars.pop())
  }
  sign + whole + "." + String::from_array(chars)
}

///|
fn bounded_output(text : String, byte_limit : Int) -> Result[String, EvalError] {
  let size = @utf8.encode(text).length()
  if size > byte_limit {
    Err(resource_error("report", byte_limit.to_int64(), size.to_int64()))
  } else {
    Ok(text)
  }
}

///|
// A JSON string literal gives reversible identity quoting. Escape additional
// terminal/line/directional controls without hiding ordinary non-ASCII labels.
fn text_identity(value : String) -> String {
  let quoted = value.quote_json()
  let parts : Array[String] = []
  for ch in quoted.iter() {
    let n = ch.to_int()
    if n == 0x061C ||
      (n >= 127 && n <= 159) ||
      (n >= 0x200B && n <= 0x200F) ||
      (n >= 0x2028 && n <= 0x202E) ||
      (n >= 0x2060 && n <= 0x206F) ||
      n == 0xFEFF {
      let digits = n.to_string(radix=16)
      parts.push("\\u" + String::make(4 - digits.length(), '0') + digits)
    } else {
      parts.push(ch.to_string())
    }
  }
  parts.join("")
}
