///|
priv struct TsvRows {
  groups : Map[String, (Array[Event], Array[Event])]
  labels : Map[String, Bool]
  mut total : Int
}

///|
fn tsv_error(error : EvalError, here : String) -> EvalError {
  let column = match error.path {
    Some("onset_s") => ".onset"
    Some("offset_s") => ".offset"
    Some("label") => ".event_label"
    _ => ""
  }
  {
    kind: error.kind,
    code: error.code,
    message: error.message,
    path: Some(here + column),
    limit: error.limit,
    observed: error.observed,
  }
}

///|
fn read_tsv(
  bytes : Bytes,
  side : String,
  state : TsvRows,
) -> Result[Unit, EvalError] {
  let text = @utf8.decode(bytes, ignore_bom=true) catch {
    _ => return Err(input_error("INVALID_UTF8", "Expected strict UTF-8", side))
  }
  let mut number = 0
  let mut offset = 0
  for view in text.split("\n") {
    let raw = view.to_owned()
    let last = offset + raw.length() == text.length()
    offset = offset + raw.length() + 1
    if last && raw.is_empty() && number > 0 {
      break
    }
    number = number + 1
    let here = "\{side}[\{number}]"
    let row = if !last && raw.has_suffix("\r") {
      raw[0:raw.length() - 1].to_owned()
    } else {
      raw
    }
    if row.contains("\r") {
      return Err(
        input_error("INVALID_TSV", "Expected LF or CRLF line endings", here),
      )
    }
    if number == 1 {
      if row != "filename\tonset\toffset\tevent_label" {
        return Err(
          input_error(
            "INVALID_TSV", "Expected filename/onset/offset/event_label TAB header",
            here,
          ),
        )
      }
      continue
    }
    let cells : Array[String] = row
      .split("\t")
      .take(5)
      .map(v => v.to_owned())
      .collect()
    if cells.length() != 4 {
      return Err(
        input_error(
          "INVALID_TSV", "Expected exactly four TAB-separated fields", here,
        ),
      )
    }
    if state.total >= 2000 {
      return Err(resource_error("tsv.events", 2000L, 2001L))
    }
    match validate_identifier(cells[0], here + ".filename") {
      Err(e) => return Err(e)
      Ok(_) => ()
    }
    let id = (if side == "reference" { "r" } else { "p" }) + number.to_string()
    let ev = match event(id, cells[3], cells[1], cells[2]) {
      Err(e) => return Err(tsv_error(e, here))
      Ok(v) => v
    }
    if !state.labels.contains(cells[3]) && state.labels.length() >= 256 {
      return Err(resource_error(here + ".event_label", 256L, 257L))
    }
    if !state.groups.contains(cells[0]) && state.groups.length() >= 1000 {
      return Err(resource_error(here + ".filename", 1000L, 1001L))
    }
    let pair = match state.groups.get(cells[0]) {
      Some(v) => v
      None => {
        let v : (Array[Event], Array[Event]) = ([], [])
        state.groups[cells[0]] = v
        v
      }
    }
    if side == "reference" {
      pair.0.push(ev)
    } else {
      pair.1.push(ev)
    }
    state.labels[cells[3]] = true
    state.total = state.total + 1
  }
  Ok(())
}

///|
/// Convert the documented four-column TSV subset into a validated task JSON.
pub fn import_tsv(
  reference : Bytes,
  prediction : Bytes,
) -> Result[String, EvalError] {
  let size = reference.length().to_int64() + prediction.length().to_int64()
  if size > 8_388_608L {
    return Err(resource_error("tsv", 8_388_608L, size))
  }
  let state : TsvRows = { groups: Map([]), labels: Map([]), total: 0, }
  for (bytes, side) in [(reference, "reference"), (prediction, "prediction")] {
    match read_tsv(bytes, side, state) {
      Err(e) => return Err(e)
      Ok(_) => ()
    }
  }
  let recs : Array[Recording] = []
  for name, pair in state.groups {
    match recording(name, pair.0, pair.1) {
      Err(e) => return Err(e)
      Ok(v) => recs.push(v)
    }
  }
  let t = match task(state.labels.keys().collect(), recs, default_config()) {
    Err(e) => return Err(e)
    Ok(v) => v
  }
  let text = json_object([
    ("schema_version", "1"),
    ("labels", json_array(t.labels.map(s => s.quote_json()))),
    (
      "config",
      json_object([("collar_s", "\"0.2\""), ("offset_ratio", "\"0.5\"")]),
    ),
    (
      "recordings",
      json_array(
        t.recordings.map(r => {
          json_object([
            ("id", r.id.quote_json()),
            ("reference", json_array(r.reference.map(event_json))),
            ("prediction", json_array(r.prediction.map(event_json))),
          ])
        }),
      ),
    ),
  ])
  let output_size = @utf8.encode(text).length().to_int64() + 1L
  if output_size > 8_388_608L {
    Err(resource_error("task", 8_388_608L, output_size))
  } else {
    Ok(text)
  }
}
