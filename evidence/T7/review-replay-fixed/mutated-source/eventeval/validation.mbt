///|
fn resource_error(path : String, limit : Int64, observed : Int64) -> EvalError {
  {
    kind: Resource,
    code: "RESOURCE_LIMIT",
    message: "Resource limit exceeded",
    path: Some(path),
    limit: Some(limit),
    observed: Some(observed),
  }
}

///|
fn prefix_error(error : EvalError, prefix : String) -> EvalError {
  let path = match error.path {
    Some(path) => Some(prefix + "." + path)
    None => Some(prefix)
  }
  {
    kind: error.kind,
    code: error.code,
    message: error.message,
    path,
    limit: error.limit,
    observed: error.observed,
  }
}

///|
fn validate_side(
  events : Array[Event],
  path : String,
) -> Result[Unit, EvalError] {
  let seen : Map[String, Bool] = Map([])
  for i in 0..<events.length() {
    if seen.contains(events[i].id) {
      return Err(
        input_error(
          "DUPLICATE_ID",
          "Duplicate event ID on this side",
          "\{path}[\{i}].id",
        ),
      )
    }
    seen[events[i].id] = true
  }
  Ok(())
}

///|
pub fn recording(
  id : String,
  reference : Array[Event],
  prediction : Array[Event],
) -> Result[Recording, EvalError] {
  match validate_identifier(id, "id") {
    Err(e) => return Err(e)
    Ok(_) => ()
  }
  if reference.length() > 2000 {
    return Err(
      resource_error("reference", 2000L, reference.length().to_int64()),
    )
  }
  if reference.length() + prediction.length() > 2000 {
    return Err(
      resource_error(
        "prediction",
        2000L,
        (reference.length() + prediction.length()).to_int64(),
      ),
    )
  }
  match validate_side(reference, "reference") {
    Err(e) => return Err(e)
    Ok(_) => ()
  }
  match validate_side(prediction, "prediction") {
    Err(e) => return Err(e)
    Ok(_) => ()
  }
  let refs = reference.copy()
  let preds = prediction.copy()
  refs.sort_by((a, b) => compare_codepoints(a.id, b.id))
  preds.sort_by((a, b) => compare_codepoints(a.id, b.id))
  Ok({ id, reference: refs, prediction: preds, })
}

///|
pub fn task(
  labels : Array[String],
  recordings : Array[Recording],
  config : Config,
) -> Result[Task, EvalError] {
  if labels.is_empty() {
    return Err(
      input_error("INVALID_SCHEMA", "Expected at least one label", "labels"),
    )
  }
  if labels.length() > 256 {
    return Err(resource_error("labels", 256L, labels.length().to_int64()))
  }
  if recordings.length() > 1000 {
    return Err(
      resource_error("recordings", 1000L, recordings.length().to_int64()),
    )
  }
  let known : Map[String, Bool] = Map([])
  for i in 0..<labels.length() {
    match validate_identifier(labels[i], "labels[\{i}]") {
      Err(e) => return Err(e)
      Ok(_) => ()
    }
    if known.contains(labels[i]) {
      return Err(input_error("DUPLICATE_ID", "Duplicate label", "labels[\{i}]"))
    }
    known[labels[i]] = true
  }
  let seen : Map[String, Bool] = Map([])
  let mut total = 0
  for i in 0..<recordings.length() {
    let rec = recordings[i]
    if seen.contains(rec.id) {
      return Err(
        input_error(
          "DUPLICATE_ID",
          "Duplicate recording ID",
          "recordings[\{i}].id",
        ),
      )
    }
    seen[rec.id] = true
    total = total + rec.reference.length() + rec.prediction.length()
    if total > 2000 {
      return Err(resource_error("recordings", 2000L, total.to_int64()))
    }
    for j in 0..<rec.reference.length() {
      if !known.contains(rec.reference[j].label) {
        return Err(
          input_error(
            "UNKNOWN_LABEL",
            "Undeclared label",
            "recordings[\{i}].reference[\{j}].label",
          ),
        )
      }
    }
    for j in 0..<rec.prediction.length() {
      if !known.contains(rec.prediction[j].label) {
        return Err(
          input_error(
            "UNKNOWN_LABEL",
            "Undeclared label",
            "recordings[\{i}].prediction[\{j}].label",
          ),
        )
      }
    }
  }
  let copied_labels = labels.copy()
  let copied_recordings = recordings.copy()
  copied_labels.sort_by(compare_codepoints)
  copied_recordings.sort_by((a, b) => compare_codepoints(a.id, b.id))
  Ok({ labels: copied_labels, recordings: copied_recordings, config, })
}
