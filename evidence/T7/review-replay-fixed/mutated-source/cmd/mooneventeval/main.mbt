///|
extern "C" fn terminate(code : Int) -> Unit = "exit"

///|
fn emit(output : @cli.CliOutput) -> Int {
  match write_all(1, output.stdout) {
    Err(e) => {
      let diagnostic = @cli.render_arg_failure({ format: @cli.Text, error: e, })
      let _ = write_all(2, diagnostic.stderr)
      return @eventeval.exit_code(e)
    }
    Ok(_) => ()
  }
  match write_all(2, output.stderr) {
    Err(e) => @eventeval.exit_code(e)
    Ok(_) => output.exit_code
  }
}

///|
fn main {
  if native_init() < 0 {
    let diagnostic = @cli.render_arg_failure({
      format: @cli.Text,
      error: internal_error(),
    })
    terminate(emit(diagnostic))
  } else {
    let all = @env.args()
    let args = []
    for i in 1..<all.length() {
      args.push(all[i])
    }
    let output = match @cli.parse_args(args) {
      Err(e) => @cli.render_arg_failure(e)
      Ok(request) => {
        let input = match request.operation {
          @cli.Evaluate(path) | @cli.ExplainPair(path, _, _, _) =>
            read_file_bounded(path)
          @cli.Help | @cli.Version => Ok(b"")
        }
        @cli.run(request, input)
      }
    }
    terminate(emit(output))
  }
}
