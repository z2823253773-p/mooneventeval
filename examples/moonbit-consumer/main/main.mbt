///|
// The example handles Result explicitly; unexpected errors stop the demo.
fn[T] checked(result : Result[T, @eventeval.EvalError]) -> T raise {
  match result {
    Ok(value) => value
    Err(error) => fail(@eventeval.error_json(error))
  }
}

///|
fn main raise {
  let reference = checked(@eventeval.event("r1", "alarm", "10", "12"))
  let prediction_1 = checked(@eventeval.event("p1", "alarm", "10", "12"))
  let prediction_2 = checked(@eventeval.event("p2", "alarm", "10.05", "12.05"))
  let recording = checked(
    @eventeval.recording("clip-01", [reference], [prediction_1, prediction_2]),
  )
  let task = checked(
    @eventeval.task(["alarm"], [recording], @eventeval.default_config()),
  )
  let evaluation = checked(@eventeval.evaluate(task))
  println(checked(@eventeval.report_json(evaluation)))
  // p2 is eligible, although this deterministic matching selected p1.
  let explanation = checked(
    @eventeval.explain_pair(task, "clip-01", "r1", "p2"),
  )
  println(checked(@eventeval.explanation_json(explanation)))
  // This intentionally invalid input demonstrates library error handling.
  // The onset is a number, but the schema requires a decimal-second string.
  let invalid = b"{\"schema_version\":1,\"labels\":[\"alarm\"],\"recordings\":[{\"id\":\"clip-01\",\"reference\":[{\"id\":\"r1\",\"label\":\"alarm\",\"onset_s\":10,\"offset_s\":\"12\"}],\"prediction\":[]}]}"
  match @eventeval.decode_task(invalid) {
    Err(error) => println(@eventeval.error_json(error))
    Ok(_) => fail("Expected numeric onset_s to be rejected")
  }
}
