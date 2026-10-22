///|
pub(all) enum OutputFormat {
  Text
  Json
} derive(Eq)

///|
pub extend OutputFormat with Eq::{equal, not_equal}

///|
pub(all) enum Operation {
  Evaluate(String)
  ExplainPair(String, String, String, String)
  Help
  Version
} derive(Eq)

///|
pub extend Operation with Eq::{equal, not_equal}

///|
pub(all) struct CliRequest {
  operation : Operation
  format : OutputFormat
}

///|
pub(all) struct ArgFailure {
  format : OutputFormat
  error : @eventeval.EvalError
}

///|
fn arg_error(format : OutputFormat) -> ArgFailure {
  {
    format,
    error: {
      kind: @eventeval.Input,
      code: "INVALID_ARGUMENT",
      message: "Invalid command or options; use --help",
      path: None,
      limit: None,
      observed: None,
    },
  }
}

///|
pub fn parse_args(args : Array[String]) -> Result[CliRequest, ArgFailure] {
  // Error format is selected before rejecting any other syntax.
  let mut format_count = 0
  let mut format = Text
  let mut bad_format = false
  let mut scan = 0
  while scan < args.length() {
    let i = scan
    if args[i] == "--format" {
      format_count = format_count + 1
      if i + 1 >= args.length() {
        bad_format = true
      } else if args[i + 1] == "json" {
        format = Json
      } else if args[i + 1] != "text" {
        bad_format = true
      }
    }
    // ID values may literally be option names; they are not format flags.
    if args[i] == "--recording" ||
      args[i] == "--reference" ||
      args[i] == "--prediction" ||
      args[i] == "--format" {
      scan = scan + 2
    } else {
      scan = scan + 1
    }
  }
  if bad_format || format_count > 1 {
    return Err(arg_error(Text))
  }
  if args.length() == 1 {
    if args[0] == "--help" {
      return Ok({ operation: Help, format: Text, })
    }
    if args[0] == "--version" {
      return Ok({ operation: Version, format: Text, })
    }
  }
  if args.length() < 2 {
    return Err(arg_error(format))
  }
  let command = args[0]
  if command != "evaluate" && command != "explain-pair" {
    return Err(arg_error(format))
  }
  let path = args[1]
  if path.is_empty() || path.has_prefix("--") {
    return Err(arg_error(format))
  }
  let mut recording = None
  let mut reference = None
  let mut prediction = None
  let mut i = 2
  while i < args.length() {
    if i + 1 >= args.length() {
      return Err(arg_error(format))
    }
    let key = args[i]
    let value = args[i + 1]
    if value.is_empty() {
      return Err(arg_error(format))
    }
    match key {
      "--format" => ()
      "--recording" if command == "explain-pair" && recording is None =>
        recording = Some(value)
      "--reference" if command == "explain-pair" && reference is None =>
        reference = Some(value)
      "--prediction" if command == "explain-pair" && prediction is None =>
        prediction = Some(value)
      _ => return Err(arg_error(format))
    }
    i = i + 2
  }
  if command == "evaluate" {
    return Ok({ operation: Evaluate(path), format, })
  }
  match (recording, reference, prediction) {
    (Some(c), Some(r), Some(p)) =>
      Ok({ operation: ExplainPair(path, c, r, p), format, })
    _ => Err(arg_error(format))
  }
}
