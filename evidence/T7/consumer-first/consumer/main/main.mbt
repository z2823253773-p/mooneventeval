///|
fn main {
  let r = @eventeval.event("r1", "alarm", "10", "12").unwrap()
  let p1 = @eventeval.event("p1", "alarm", "10", "12").unwrap()
  let p2 = @eventeval.event("p2", "alarm", "10.05", "12.05").unwrap()
  let rec = @eventeval.recording("clip-01", [r], [p1, p2]).unwrap()
  let input = @eventeval.task(["alarm"], [rec], @eventeval.default_config()).unwrap()
  let evaluation = @eventeval.evaluate(input).unwrap()
  let counts = evaluation.metrics().counts
  assert_true(counts.tp == 1 && counts.fp == 1 && counts.fn_count == 0)
  println(@eventeval.report_json(evaluation).unwrap())
}
