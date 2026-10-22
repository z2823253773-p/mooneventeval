///|
#borrow(path)
extern "C" fn native_open(path : Bytes) -> Int = "mee_open_readonly"

///|
#borrow(buffer)
extern "C" fn native_read(fd : Int, buffer : Bytes, count : Int) -> Int = "mee_read"

///|
extern "C" fn native_close(fd : Int) -> Int = "mee_close"

///|
#borrow(buffer)
extern "C" fn native_write(fd : Int, buffer : Bytes, count : Int) -> Int = "mee_write"

///|
extern "C" fn native_init() -> Int = "mee_init"

///|
fn io_error() -> @eventeval.EvalError {
  {
    kind: @eventeval.Input,
    code: "FILE_ERROR",
    message: "Cannot read a regular input file or write output",
    path: Some("file"),
    limit: None,
    observed: None,
  }
}

///|
fn internal_error() -> @eventeval.EvalError {
  {
    kind: @eventeval.Internal,
    code: "INTERNAL_ERROR",
    message: "Unexpected native I/O failure",
    path: None,
    limit: None,
    observed: None,
  }
}

///|
fn read_file_bounded(path : String) -> Result[Bytes, @eventeval.EvalError] {
  if path.contains("\u0000") {
    return Err(io_error())
  }
  let fd = native_open(@utf8.encode(path + "\u0000"))
  if fd < 0 {
    return Err(io_error())
  }
  let collected = @buffer.Buffer::Buffer(size_hint=65536)
  let buffer = Bytes::make(65536, b'\x00')
  let mut failure = None
  while collected.length() <= 8_388_608 {
    let remaining = 8_388_609 - collected.length()
    let wanted = if remaining < 65536 { remaining } else { 65536 }
    let n = native_read(fd, buffer, wanted)
    if n == 0 {
      break
    }
    if n < 0 || n > wanted {
      failure = Some(if n == -1 { io_error() } else { internal_error() })
      break
    }
    collected.write_bytes(buffer[:n])
  }
  let closed = native_close(fd)
  if collected.length() > 8_388_608 {
    return Err({
      kind: @eventeval.Resource,
      code: "RESOURCE_LIMIT",
      message: "Input exceeds byte limit",
      path: Some("input"),
      limit: Some(8_388_608L),
      observed: Some(8_388_609L),
    })
  }
  if failure is Some(e) {
    return Err(e)
  }
  if closed < 0 {
    return Err(io_error())
  }
  Ok(collected.to_bytes())
}

///|
fn write_all(fd : Int, bytes : Bytes) -> Result[Unit, @eventeval.EvalError] {
  let mut offset = 0
  while offset < bytes.length() {
    let remaining = bytes.length() - offset
    let wanted = if remaining < 65536 { remaining } else { 65536 }
    let chunk = bytes[offset:offset + wanted].to_owned()
    let n = native_write(fd, chunk, wanted)
    if n <= 0 || n > wanted {
      return Err(
        if n == -2 || n > wanted {
          internal_error()
        } else {
          io_error()
        },
      )
    }
    offset = offset + n
  }
  Ok(())
}
