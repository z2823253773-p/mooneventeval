// Pinned core still supports this parameter but deprecates explicit use.
// Limit the compatibility exception to this function, not the package.
#warnings("-deprecated")
fn classification(input : String) -> String {
  try {
    @json.parse(input, max_nesting_depth=16) |> ignore
    "ok"
  } catch {
    @json.DepthLimitExceeded => "resource"
    _ => "syntax"
  }
}
test "array depth 16 and 17" {
  inspect(classification(String::make(16, '[') + "0" + String::make(16, ']')), content="ok")
  inspect(classification(String::make(17, '[') + "0" + String::make(17, ']')), content="resource")
}
test "object depth 16 and 17" {
  let mut value = "0"
  for _ in 0..<16 { value = "{\"k\":" + value + "}" }
  inspect(classification(value), content="ok")
  inspect(classification("{\"k\":" + value + "}"), content="resource")
}
test "syntax distinct from depth" {
  inspect(classification("[1,"), content="syntax")
}
test "last value wins including equivalent escaped keys" {
  inspect(@json.parse("{\"onset_s\":\"1\",\"onset_s\":\"2\"}").stringify(), content="{\"onset_s\":\"2\"}")
  inspect(@json.parse("{\"a\":1,\"\\u0061\":2}").stringify(), content="{\"a\":2}")
}
test "strict UTF8 rejects invalid bytes" {
  let invalid = try { @utf8.decode(b"\xFF") |> ignore; false } catch { _ => true }
  inspect(invalid, content="true")
  inspect(@utf8.decode(b"abc"), content="abc")
}
test "surrogate handling" {
  inspect(classification("\"\\uD800\""), content="syntax")
  inspect(classification("\"\\uDC00\""), content="syntax")
  inspect(classification("\"\\uD800\\uDC00\""), content="ok")
}
