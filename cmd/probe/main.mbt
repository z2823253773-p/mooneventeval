// Development-only argv probe. No file I/O or product CLI interface.

///|
extern "C" fn terminate(code : Int) -> Unit = "exit"

///|
fn main {
  let args = @env.args()
  if args.length() != 2 {
    let error : @eventeval.EvalError = {
      kind: @eventeval.Input,
      code: "INVALID_ARGUMENT",
      message: "Expected one small JSON task argument",
      path: None,
      limit: None,
      observed: None,
    }
    println(@eventeval.error_json(error))
    terminate(@eventeval.exit_code(error))
  } else {
    match @eventeval.evaluate_json(@utf8.encode(args[1])) {
      Ok(report) => println(report)
      Err(error) => {
        println(@eventeval.error_json(error))
        terminate(@eventeval.exit_code(error))
      }
    }
  }
}
