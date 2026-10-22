///|
/// Failure categories map to the CLI contract without throwing on bad input.
pub(all) enum FailureKind {
  Input
  Resource
  Internal
}

///|
/// Stable machine-readable error details. A missing observation stays absent.
pub(all) struct EvalError {
  kind : FailureKind
  code : String
  message : String
  path : String?
  limit : Int64?
  observed : Int64?
}

///|
pub fn exit_code(error : EvalError) -> Int {
  match error.kind {
    Input => 2
    Resource => 3
    Internal => 4
  }
}

///|
fn input_error(code : String, message : String, path : String) -> EvalError {
  { kind: Input, code, message, path: Some(path), limit: None, observed: None, }
}

///|
fn string_limit_error(path : String) -> EvalError {
  {
    kind: Resource,
    code: "RESOURCE_LIMIT",
    message: "ID or label exceeds 256 Unicode code points",
    path: Some(path),
    limit: Some(256L),
    observed: Some(257L),
  }
}
