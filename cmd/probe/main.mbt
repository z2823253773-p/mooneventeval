// Development-only argv probe. No file I/O or product CLI interface.

///|
extern "C" fn terminate(code : Int) -> Unit = "exit"

///|
fn render(
  args : Array[String],
  mode : String,
) -> Result[String, @eventeval.EvalError] {
  let bytes = @utf8.encode(args[1])
  if mode == "evaluate-json" {
    return @eventeval.evaluate_json(bytes)
  }
  let input = match @eventeval.decode_task(bytes) {
    Ok(t) => t
    Err(e) => return Err(e)
  }
  if mode == "report-text" {
    let evaluation = match @eventeval.evaluate(input) {
      Ok(r) => r
      Err(e) => return Err(e)
    }
    return @eventeval.report_text(evaluation)
  }
  let explanation = match
    @eventeval.explain_pair(input, args[3], args[4], args[5]) {
    Ok(e) => e
    Err(e) => return Err(e)
  }
  if mode == "explain-json" {
    @eventeval.explanation_json(explanation)
  } else {
    @eventeval.explanation_text(explanation)
  }
}

///|
fn main {
  let args = @env.args()
  let mode = if args.length() == 2 {
    "evaluate-json"
  } else if args.length() == 3 && args[2] == "report-text" {
    "report-text"
  } else if args.length() == 6 &&
    (args[2] == "explain-json" || args[2] == "explain-text") {
    args[2]
  } else {
    "invalid"
  }
  if mode == "invalid" {
    let error : @eventeval.EvalError = {
      kind: @eventeval.Input,
      code: "INVALID_ARGUMENT",
      message: "Expected a small JSON task, optionally report-text or explain-json/explain-text with recording/reference/prediction IDs",
      path: None,
      limit: None,
      observed: None,
    }
    println(@eventeval.error_json(error))
    terminate(@eventeval.exit_code(error))
  } else {
    match render(args, mode) {
      Ok(report) => println(report.trim_end(chars="\n").to_owned())
      Err(error) => {
        println(@eventeval.error_json(error))
        terminate(@eventeval.exit_code(error))
      }
    }
  }
}
