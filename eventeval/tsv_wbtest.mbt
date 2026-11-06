///|
test "tsv_limits_precision_scope_and_rows" {
  let h = "filename\tonset\toffset\tevent_label\n"
  let good = @utf8.encode(h + "a\t0\t1\tx\n")
  for
    (row, code, path) in [
      ("a\t1e0\t2\tx", "INVALID_DECIMAL", "prediction[2].onset"),
      ("a\t1.0000001\t2\tx", "INVALID_DECIMAL", "prediction[2].onset"),
      ("a\t2\t1\tx", "OUT_OF_RANGE", "prediction[2].offset"),
      ("a\t0\t1\tx\textra", "INVALID_TSV", "prediction[2]"),
      ("", "INVALID_TSV", "prediction[2]"),
      ("a\r\t0\t1\tx", "INVALID_TSV", "prediction[2]"),
    ] {
    match import_tsv(good, @utf8.encode(h + row + "\n")) {
      Ok(_) => fail("bad TSV accepted")
      Err(e) => {
        inspect(e.code == code, content="true")
        inspect(e.path == Some(path), content="true")
      }
    }
  }
  let rows = Array::makei(2000, _ => "a\t0\t1\tx\n").join("")
  let empty = @utf8.encode(h)
  inspect(import_tsv(@utf8.encode(h + rows), empty) is Ok(_), content="true")
  match import_tsv(@utf8.encode(h + rows), good) {
    Ok(_) => fail("2001 events accepted")
    Err(e) =>
      inspect(e.kind is Resource && e.observed == Some(2001L), content="true")
  }
  inspect(import_tsv(empty, empty) is Err(_), content="true")
  inspect(import_tsv(b"\xff", empty) is Err(_), content="true")
  let at = @utf8.encode(
    h + "a\t0\t1\t" + String::make(8_388_608 - h.length() * 2 - 6, 'x'),
  )
  match import_tsv(at, empty) {
    Ok(_) => fail("oversized label accepted")
    Err(e) =>
      inspect(e.path == Some("reference[2].event_label"), content="true")
  }
  match import_tsv(at, @utf8.encode(h + "x")) {
    Ok(_) => fail("combined byte cap accepted")
    Err(e) =>
      inspect(
        e.path == Some("tsv") && e.observed == Some(8_388_609L),
        content="true",
      )
  }
}

///|
test "tsv_unicode_literal_quotes_and_generated_ids" {
  let h = "filename\tonset\toffset\tevent_label\n"
  let raw = @utf8.encode(h + "\"片\"\t0.000001\t1.000000\t 类 \n")
  let text = import_tsv(raw, raw).unwrap()
  let t = decode_task(@utf8.encode(text)).unwrap()
  let result = evaluate(t).unwrap()
  inspect(result.metrics().counts.tp == 1, content="true")
  inspect(result.pairs()[0] == ("\"片\"", " 类 ", "r2", "p2"), content="true")
}
