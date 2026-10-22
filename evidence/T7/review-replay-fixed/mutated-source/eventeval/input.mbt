///|
priv suberror DecodeFailure {
  DecodeFailure(EvalError)
}

///|
fn[T] decoded(
  result : Result[T, EvalError],
  prefix : String,
) -> T raise DecodeFailure {
  match result {
    Ok(value) => value
    Err(error) => raise DecodeFailure(prefix_error(error, prefix))
  }
}

///|
fn object_fields(
  value : Json,
  allowed : Array[String],
  path : String,
) -> Map[String, Json] raise DecodeFailure {
  let fields = match value {
    Object(fields) => fields
    _ =>
      raise DecodeFailure(input_error("INVALID_TYPE", "Expected object", path))
  }
  let keys = fields.keys().collect()
  keys.sort_by(compare_codepoints)
  for key in keys {
    if !allowed.contains(key) {
      raise DecodeFailure(
        input_error(
          "UNKNOWN_FIELD",
          "Unknown field",
          if path == "$" {
            key
          } else {
            path + "." + key
          },
        ),
      )
    }
  }
  fields
}

///|
fn required(
  fields : Map[String, Json],
  key : String,
  path : String,
) -> Json raise DecodeFailure {
  match fields.get(key) {
    Some(value) => value
    None =>
      raise DecodeFailure(
        input_error("MISSING_FIELD", "Required field missing", path),
      )
  }
}

///|
fn string_value(value : Json, path : String) -> String raise DecodeFailure {
  match value {
    String(value) => value
    _ =>
      raise DecodeFailure(
        input_error(
          "INVALID_TYPE", "Expected string; times are decimal seconds strings", path,
        ),
      )
  }
}

///|
fn array_value(value : Json, path : String) -> Array[Json] raise DecodeFailure {
  match value {
    Array(value) => value
    _ =>
      raise DecodeFailure(input_error("INVALID_TYPE", "Expected array", path))
  }
}

///|
fn decode_events(
  value : Json,
  path : String,
) -> Array[Event] raise DecodeFailure {
  let items = array_value(value, path)
  if items.length() > 2000 {
    raise DecodeFailure(resource_error(path, 2000L, items.length().to_int64()))
  }
  let events : Array[Event] = []
  for i in 0..<items.length() {
    let here = "\{path}[\{i}]"
    let fields = object_fields(
      items[i],
      ["id", "label", "onset_s", "offset_s"],
      here,
    )
    let id = string_value(required(fields, "id", here + ".id"), here + ".id")
    let label = string_value(
      required(fields, "label", here + ".label"),
      here + ".label",
    )
    let onset = string_value(
      required(fields, "onset_s", here + ".onset_s"),
      here + ".onset_s",
    )
    let offset = string_value(
      required(fields, "offset_s", here + ".offset_s"),
      here + ".offset_s",
    )
    events.push(decoded(event(id, label, onset, offset), here))
  }
  events
}

///|
fn decode_document(value : Json) -> Task raise DecodeFailure {
  let fields = object_fields(
    value,
    ["schema_version", "labels", "config", "recordings"],
    "$",
  )
  match required(fields, "schema_version", "schema_version") {
    Number(n, ..) =>
      if n != 1.0 {
        raise DecodeFailure(
          input_error(
            "INVALID_SCHEMA", "Expected schema_version 1", "schema_version",
          ),
        )
      }
    _ =>
      raise DecodeFailure(
        input_error(
          "INVALID_TYPE", "Expected schema_version number", "schema_version",
        ),
      )
  }
  let raw_labels = array_value(required(fields, "labels", "labels"), "labels")
  if raw_labels.length() > 256 {
    raise DecodeFailure(
      resource_error("labels", 256L, raw_labels.length().to_int64()),
    )
  }
  let labels : Array[String] = []
  for i in 0..<raw_labels.length() {
    labels.push(string_value(raw_labels[i], "labels[\{i}]"))
  }
  // Validate label semantics before checking any recording membership.
  match task(labels, [], default_config()) {
    Err(error) => raise DecodeFailure(error)
    Ok(_) => ()
  }
  let cfg = match fields.get("config") {
    None => default_config()
    Some(value) => {
      let fields = object_fields(value, ["collar_s", "offset_ratio"], "config")
      let collar = match fields.get("collar_s") {
        None => "0.2"
        Some(v) => string_value(v, "config.collar_s")
      }
      let ratio = match fields.get("offset_ratio") {
        None => "0.5"
        Some(v) => string_value(v, "config.offset_ratio")
      }
      decoded(config(collar, ratio), "config")
    }
  }
  let raw_recs = array_value(
    required(fields, "recordings", "recordings"),
    "recordings",
  )
  if raw_recs.length() > 1000 {
    raise DecodeFailure(
      resource_error("recordings", 1000L, raw_recs.length().to_int64()),
    )
  }
  let recs : Array[Recording] = []
  let mut total = 0
  // Validate original event paths/labels before recording factory canonicalizes order.
  for i in 0..<raw_recs.length() {
    let here = "recordings[\{i}]"
    let fields = object_fields(
      raw_recs[i],
      ["id", "reference", "prediction"],
      here,
    )
    let id = string_value(required(fields, "id", here + ".id"), here + ".id")
    let refs = decode_events(
      required(fields, "reference", here + ".reference"),
      here + ".reference",
    )
    let preds = decode_events(
      required(fields, "prediction", here + ".prediction"),
      here + ".prediction",
    )
    total = total + refs.length() + preds.length()
    if total > 2000 {
      raise DecodeFailure(resource_error("recordings", 2000L, total.to_int64()))
    }
    for j in 0..<refs.length() {
      if !labels.contains(refs[j].label) {
        raise DecodeFailure(
          input_error(
            "UNKNOWN_LABEL",
            "Undeclared label",
            here + ".reference[\{j}].label",
          ),
        )
      }
    }
    for j in 0..<preds.length() {
      if !labels.contains(preds[j].label) {
        raise DecodeFailure(
          input_error(
            "UNKNOWN_LABEL",
            "Undeclared label",
            here + ".prediction[\{j}].label",
          ),
        )
      }
    }
    recs.push(decoded(recording(id, refs, preds), here))
  }
  match task(labels, recs, cfg) {
    Ok(t) => t
    Err(e) => raise DecodeFailure(e)
  }
}

///|
// The only deprecated parser compatibility exception, qualified in T0.
#warnings("-deprecated")
fn parse_bounded(text : String) -> Result[Json, EvalError] {
  Ok(@json.parse(text, max_nesting_depth=16)) catch {
    @json.DepthLimitExceeded => Err(resource_error("$", 16L, 17L))
    _ =>
      Err(
        input_error(
          "INVALID_JSON", "Invalid JSON syntax or Unicode escape", "$",
        ),
      )
  }
}

///|
pub fn decode_task(input : Bytes) -> Result[Task, EvalError] {
  if input.length() > 8_388_608 {
    return Err(resource_error("$", 8_388_608L, input.length().to_int64()))
  }
  let text = @utf8.decode(input, ignore_bom=true) catch {
    _ => return Err(input_error("INVALID_UTF8", "Expected strict UTF-8", "$"))
  }
  let value = match parse_bounded(text) {
    Err(e) => return Err(e)
    Ok(v) => v
  }
  Ok(decode_document(value)) catch {
    DecodeFailure(e) => Err(e)
  }
}

///|
pub fn evaluate_json(input : Bytes) -> Result[String, EvalError] {
  let t = match decode_task(input) {
    Err(e) => return Err(e)
    Ok(t) => t
  }
  let report = match evaluate(t) {
    Err(e) => return Err(e)
    Ok(r) => r
  }
  report_json(report)
}
