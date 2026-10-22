// Removing close eventually exhausts descriptors; NUL must never truncate a path.

///|
test "native_read_nul_regular_and_repeated_close" {
  match read_file_bounded("examples/duplicate.json\u0000suffix") {
    Err(e) => inspect(e.code, content="FILE_ERROR")
    Ok(_) => abort("NUL path accepted")
  }
  match read_file_bounded("examples") {
    Err(e) => inspect(e.code, content="FILE_ERROR")
    Ok(_) => abort("directory accepted")
  }
  for _ in 0..<20000 {
    inspect(
      read_file_bounded("examples/duplicate.json") is Ok(_),
      content="true",
    )
  }
}

///|
test "native_write_empty_and_invalid_descriptor" {
  inspect(write_all(-1, b"") is Ok(_), content="true")
  match write_all(-1, b"data") {
    Err(e) => inspect(e.code, content="FILE_ERROR")
    Ok(_) => abort("failed write accepted")
  }
}
