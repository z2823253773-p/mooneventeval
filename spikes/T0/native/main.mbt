#borrow(path, buffer)
extern "C" fn read_small(path : Bytes, buffer : Bytes, capacity : Int, wanted : Int) -> Int = "spike_read"
#borrow(buffer)
extern "C" fn write_small(buffer : Bytes, capacity : Int, wanted : Int) -> Int = "spike_write"
extern "C" fn exit_with(code : Int) -> Unit = "exit"
fn main {
  let bytes = Bytes::make(8, b'\x00')
  if read_small(b"spike-input.bin\x00", bytes, 8, -1) != -2 { exit_with(91) }
  if read_small(b"spike-input.bin\x00", bytes, 8, 2147483647) != -2 { exit_with(92) }
  if read_small(b"spike-input.bin\x00", bytes, 8, 8) != 3 { exit_with(93) }
  if bytes[0] != b'T' || bytes[1] != b'0' || bytes[2] != b'\n' { exit_with(94) }
  if write_small(bytes, 8, 2147483647) != -2 { exit_with(95) }
  if write_small(bytes, 8, 3) != 3 { exit_with(96) }
  exit_with(7)
}
