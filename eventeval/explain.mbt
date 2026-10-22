///|
fn find_explanation_event(
  events : Array[Event],
  id : String,
  path : String,
) -> Result[Event, EvalError] {
  for event in events {
    if event.id == id {
      return Ok(event)
    }
  }
  Err(
    input_error(
      "ID_NOT_FOUND", "Event ID not found on the requested side", path,
    ),
  )
}

///|
pub fn explain_pair(
  input : Task,
  recording_id : String,
  reference_id : String,
  prediction_id : String,
) -> Result[PairExplanation, EvalError] {
  for recording in input.recordings {
    if recording.id != recording_id {
      continue
    }
    let reference = match
      find_explanation_event(recording.reference, reference_id, "reference_id") {
      Ok(e) => e
      Err(e) => return Err(e)
    }
    let prediction = match
      find_explanation_event(
        recording.prediction,
        prediction_id,
        "prediction_id",
      ) {
      Ok(e) => e
      Err(e) => return Err(e)
    }
    return Ok({
      config: input.config,
      recording_id,
      reference,
      prediction,
      basis: eligibility(reference, prediction, input.config),
    })
  }
  Err(input_error("ID_NOT_FOUND", "Recording ID not found", "recording_id"))
}
