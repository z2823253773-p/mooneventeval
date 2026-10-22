///|
pub(all) struct CliOutput {
  stdout : Bytes
  stderr : Bytes
  exit_code : Int
}

///|
fn failure(format : OutputFormat, error : @eventeval.EvalError) -> CliOutput {
  if format == Json {
    {
      stdout: @utf8.encode(@eventeval.error_json(error) + "\n"),
      stderr: b"",
      exit_code: @eventeval.exit_code(error),
    }
  } else {
    {
      stdout: b"",
      stderr: @utf8.encode(
        "MoonEventEval failed: " +
        error.code +
        " " +
        Json::string(error.message).stringify() +
        "\n",
      ),
      exit_code: @eventeval.exit_code(error),
    }
  }
}

///|
pub fn render_arg_failure(error : ArgFailure) -> CliOutput {
  failure(error.format, error.error)
}

///|
fn render(
  request : CliRequest,
  bytes : Bytes,
) -> Result[String, @eventeval.EvalError] {
  let task = match @eventeval.decode_task(bytes) {
    Ok(t) => t
    Err(e) => return Err(e)
  }
  match request.operation {
    Evaluate(_) => {
      let evaluation = match @eventeval.evaluate(task) {
        Ok(v) => v
        Err(e) => return Err(e)
      }
      if request.format == Json {
        @eventeval.report_json(evaluation)
      } else {
        @eventeval.report_text(evaluation)
      }
    }
    ExplainPair(_, c, r, p) => {
      let pair = match @eventeval.explain_pair(task, c, r, p) {
        Ok(v) => v
        Err(e) => return Err(e)
      }
      if request.format == Json {
        @eventeval.explanation_json(pair)
      } else {
        @eventeval.explanation_text(pair)
      }
    }
    Help | Version => abort("help/version handled before input")
  }
}

///|
pub fn run(
  request : CliRequest,
  input : Result[Bytes, @eventeval.EvalError],
) -> CliOutput {
  let help = "MoonEventEval 0.1.0\nUsage:\n  mooneventeval evaluate FILE [--format text|json]\n  mooneventeval explain-pair FILE --recording ID --reference ID --prediction ID [--format text|json]\n  mooneventeval --help\n  mooneventeval --version\nInput: UTF-8 JSON task; default output: text. Files are read only.\nExit: 0 completed; 2 input/argument/file; 3 resource limit; 4 internal.\n"
  match request.operation {
    Help => return { stdout: @utf8.encode(help), stderr: b"", exit_code: 0, }
    Version =>
      return { stdout: b"MoonEventEval 0.1.0\n", stderr: b"", exit_code: 0, }
    _ => ()
  }
  let bytes = match input {
    Ok(b) => b
    Err(e) => return failure(request.format, e)
  }
  match render(request, bytes) {
    Err(e) => failure(request.format, e)
    Ok(text) => {
      let framed = if text.has_suffix("\n") { text } else { text + "\n" }
      let stdout = @utf8.encode(framed)
      if stdout.length() > 16_777_216 {
        failure(request.format, {
          kind: @eventeval.Resource,
          code: "RESOURCE_LIMIT",
          message: "Serialized report exceeds byte limit",
          path: Some("report"),
          limit: Some(16_777_216L),
          observed: Some(stdout.length().to_int64()),
        })
      } else {
        { stdout, stderr: b"", exit_code: 0, }
      }
    }
  }
}
