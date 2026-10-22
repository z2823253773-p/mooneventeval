///|
/// An event can only be constructed by the validated factory outside this package.
pub struct Event {
  priv id : String
  priv label : String
  priv onset_us : Int64
  priv offset_us : Int64
}

///|
/// Exact fixed collar and ratio, measured in microseconds and ppm respectively.
pub struct Config {
  priv collar_us : Int64
  priv offset_ratio_ppm : Int64
}

///|
/// Signed prediction-minus-reference deltas are retained for later explanation.
priv struct PairBasis {
  label_match : Bool
  onset_pass : Bool
  offset_pass : Bool
  eligible : Bool
  onset_delta_us : Int64
  offset_delta_us : Int64
  onset_limit_us : Int64
  offset_limit_scaled : Int64
}

///|
fn validate_identifier(text : String, path : String) -> Result[Unit, EvalError] {
  // Validate UTF-16 before counting code points: safe substring operations in
  // the pinned core can split a surrogate pair, despite JSON rejecting it.
  let units = text.code_units()
  let mut index = 0
  let mut count = 0
  while index < units.length() {
    let first = units[index]
    if first.is_leading_surrogate() {
      if index + 1 >= units.length() ||
        !units[index + 1].is_trailing_surrogate() {
        return Err(
          input_error("INVALID_UNICODE", "Unpaired UTF-16 surrogate", path),
        )
      }
      index = index + 2
    } else {
      if first.is_trailing_surrogate() {
        return Err(
          input_error("INVALID_UNICODE", "Unpaired UTF-16 surrogate", path),
        )
      }
      index = index + 1
    }
    count = count + 1
    if count > 256 {
      return Err(string_limit_error(path))
    }
  }
  if count == 0 {
    Err(input_error("INVALID_SCHEMA", "ID or label must not be empty", path))
  } else {
    Ok(())
  }
}

///|
pub fn event(
  id : String,
  label : String,
  onset_s : String,
  offset_s : String,
) -> Result[Event, EvalError] {
  match validate_identifier(id, "id") {
    Err(error) => return Err(error)
    Ok(_) => ()
  }
  match validate_identifier(label, "label") {
    Err(error) => return Err(error)
    Ok(_) => ()
  }
  let onset_us = match parse_time_us(onset_s, "onset_s") {
    Ok(value) => value
    Err(error) => return Err(error)
  }
  let offset_us = match parse_time_us(offset_s, "offset_s") {
    Ok(value) => value
    Err(error) => return Err(error)
  }
  if onset_us >= offset_us {
    return Err(
      input_error("OUT_OF_RANGE", "Expected onset_s < offset_s", "offset_s"),
    )
  }
  Ok({ id, label, onset_us, offset_us, })
}

///|
pub fn config(
  collar_s : String,
  offset_ratio : String,
) -> Result[Config, EvalError] {
  let collar_us = match parse_time_us(collar_s, "collar_s") {
    Ok(value) => value
    Err(error) => return Err(error)
  }
  let offset_ratio_ppm = match parse_ratio_ppm(offset_ratio, "offset_ratio") {
    Ok(value) => value
    Err(error) => return Err(error)
  }
  Ok({ collar_us, offset_ratio_ppm, })
}

///|
pub fn default_config() -> Config {
  { collar_us: 200_000L, offset_ratio_ppm: 500_000L, }
}

///|
pub struct Recording {
  priv id : String
  priv reference : Array[Event]
  priv prediction : Array[Event]
}

///|
pub struct Task {
  priv labels : Array[String]
  priv recordings : Array[Recording]
  priv config : Config
}

///|
pub struct Counts {
  reference : Int
  prediction : Int
  tp : Int
  fp : Int
  fn_count : Int
}

///|
pub struct Metrics {
  counts : Counts
  precision : Double?
  recall : Double?
  f1 : Double?
}

///|
priv struct SelectedPair {
  recording_id : String
  label : String
  reference : Event
  prediction : Event
  basis : PairBasis
}

///|
priv struct UnmatchedEvent {
  recording_id : String
  event : Event
  candidate_count : Int
}

///|
pub struct Evaluation {
  priv config : Config
  priv summary : Metrics
  priv by_label : Array[(String, Metrics)]
  priv by_recording : Array[(String, Metrics)]
  priv matches : Array[SelectedPair]
  priv false_positives : Array[UnmatchedEvent]
  priv false_negatives : Array[UnmatchedEvent]
  priv candidate_checks : Int
  priv eligible_edges : Int
  priv matching_steps : Int64
}

///|
pub fn Evaluation::metrics(self : Evaluation) -> Metrics {
  self.summary
}

///|
pub fn Evaluation::pairs(
  self : Evaluation,
) -> Array[(String, String, String, String)] {
  self.matches.map(p => {
    (p.recording_id, p.label, p.reference.id, p.prediction.id)
  })
}

///|
pub struct PairExplanation {
  priv config : Config
  priv recording_id : String
  priv reference : Event
  priv prediction : Event
  priv basis : PairBasis
}
