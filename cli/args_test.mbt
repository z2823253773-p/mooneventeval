// Catch lost JSON failure mode, permissive grammar and wrong dispatch/exit routing.

///|
test "args_format_prescan_respects_unknown_option_values" {
  for key in ["--unknown", "unknown"] {
    for value in ["--recording", "--reference", "--prediction", "--format"] {
      let result = @cli.parse_args([
        "evaluate", "absent", key, value, "--format", "json",
      ])
      inspect(result is Err(_), content="true")
      if result is Err(e) {
        inspect(e.format == @cli.Json, content="true")
        let output = @cli.render_arg_failure(e)
        inspect(
          output.stdout.length() > 0 &&
          output.stderr.length() == 0 &&
          output.exit_code == 2,
          content="true",
        )
      }
    }
  }
}

///|
test "args_success_default_and_exact_explanation" {
  let r = @cli.parse_args(["evaluate", "task.json"]).unwrap()
  inspect(r.format == @cli.Text, content="true")
  inspect(r.operation == @cli.Evaluate("task.json"), content="true")
  let r = @cli.parse_args([
    "explain-pair", "t", "--prediction", "p", "--format", "json", "--recording",
    "c", "--reference", "r",
  ]).unwrap()
  inspect(r.operation == @cli.ExplainPair("t", "c", "r", "p"), content="true")
  inspect(r.format == @cli.Json, content="true")
}

///|
test "args_query_ids_may_start_with_dashes" {
  let result = @cli.parse_args([
    "explain-pair", "t", "--recording", "--clip", "--reference", "--ref", "--prediction",
    "--pred",
  ])
  inspect(result is Ok(_), content="true")
  if result is Ok(r) {
    inspect(
      r.operation == @cli.ExplainPair("t", "--clip", "--ref", "--pred"),
      content="true",
    )
  }
  let reserved = @cli.parse_args([
    "explain-pair", "t", "--recording", "--format", "--reference", "--reference",
    "--prediction", "--format", "--format", "json",
  ])
  inspect(reserved is Ok(_), content="true")
  if reserved is Ok(r) {
    inspect(
      r.format == @cli.Json &&
      r.operation ==
      @cli.ExplainPair("t", "--format", "--reference", "--format"),
      content="true",
    )
  }
}

///|
test "args_invalid_grammar_and_format_precedence" {
  for
    args in [
      [],
      ["evaluate"],
      ["wat", "t"],
      ["evaluate", "t", "--recording", "c"],
      ["--format", "json", "evaluate", "t"],
      ["evaluate", "--format", "json"],
      ["--help", "t"],
      ["--version", "--format", "json"],
      ["explain-pair", "t", "--recording", "c"],
      [
        "explain-pair", "t", "--recording", "c", "--reference", "r", "--prediction",
        "p", "--prediction", "p",
      ],
    ] {
    inspect(@cli.parse_args(args) is Err(_), content="true")
  }
  for
    args in [
      ["wat", "--format", "json"],
      ["evaluate", "t", "--bad", "x", "--format", "json"],
      ["explain-pair", "t", "--format", "json"],
    ] {
    match @cli.parse_args(args) {
      Err(e) => {
        inspect(e.format == @cli.Json, content="true")
        inspect(@cli.render_arg_failure(e).exit_code, content="2")
      }
      Ok(_) => abort("invalid arguments accepted")
    }
  }
  for
    args in [
      ["evaluate", "t", "--format", "bad"],
      ["evaluate", "t", "--format", "json", "--format", "json"],
      ["evaluate", "t", "--format"],
    ] {
    match @cli.parse_args(args) {
      Err(e) => inspect(e.format == @cli.Text, content="true")
      Ok(_) => abort("invalid format accepted")
    }
  }
}

///|
test "dispatch_help_version_ignore_failed_input" {
  let failure : @eventeval.EvalError = {
    kind: @eventeval.Input,
    code: "FILE_ERROR",
    message: "Unreadable",
    path: None,
    limit: None,
    observed: None,
  }
  for arg in ["--help", "--version"] {
    let o = @cli.run(@cli.parse_args([arg]).unwrap(), Err(failure))
    inspect(o.exit_code, content="0")
    inspect(o.stderr.length() == 0 && o.stdout.length() > 0, content="true")
  }
}

///|
test "dispatch_machine_errors_and_zero_success" {
  let request = @cli.parse_args(["evaluate", "ignored", "--format", "json"]).unwrap()
  let o = @cli.run(request, Ok(b"{}"))
  inspect(o.exit_code, content="2")
  inspect(o.stderr.length() == 0, content="true")
  inspect(
    @utf8.decode(o.stdout).contains("\"status\":\"failed\""),
    content="true",
  )
  let input = b"{\"schema_version\":1,\"labels\":[\"a\"],\"recordings\":[]}"
  let o = @cli.run(request, Ok(input))
  inspect(o.exit_code, content="0")
  inspect(@utf8.decode(o.stdout).contains("\"tp\":0"), content="true")
  for kind in [@eventeval.Input, @eventeval.Resource, @eventeval.Internal] {
    let e : @eventeval.EvalError = {
      kind,
      code: "test",
      message: "a\nb",
      path: None,
      limit: None,
      observed: None,
    }
    let o = @cli.run(request, Err(e))
    inspect(o.exit_code == @eventeval.exit_code(e), content="true")
    inspect(!@utf8.decode(o.stdout).contains("\"summary\""), content="true")
  }
  let text = @cli.run(@cli.parse_args(["evaluate", "x"]).unwrap(), Ok(b"{}"))
  inspect(
    text.stdout.length() == 0 && text.stderr.length() > 0 && text.exit_code == 2,
    content="true",
  )
}
