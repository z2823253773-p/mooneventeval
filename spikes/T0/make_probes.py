"""Materialize small synthetic compiler experiments, not product code."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def module(name, source, imports='', executable=False, legacy=False, stub=None):
    folder = ROOT/name
    folder.mkdir(exist_ok=True)
    if legacy:
        (folder/'moon.mod.json').write_text(json.dumps({'name': f'local/t0_{name}', 'version': '0.0.1', 'preferred-target': 'native'}))
        (folder/'moon.pkg.json').write_text(json.dumps({}))
    else:
        (folder/'moon.mod').write_text(f'name = "local/t0_{name}"\nversion = "0.0.1"\npreferred_target = "native"\n')
        config = imports
        if executable:
            config += '\npkgtype(kind: "executable")\n'
        if stub:
            config += '\noptions("native-stub": ["io_stub.c"])\n'
            (folder/'io_stub.c').write_text(stub)
        (folder/'moon.pkg').write_text(config)
    (folder/('main.mbt' if executable else 'probe_wbtest.mbt')).write_text(source)

if __name__ == '__main__':
    module('field_old', '''struct Counts { fn : Int }
test "old field" { let c : Counts = { fn: 2 }; inspect(c.fn, content="2") }
''')
    module('field_new', '''struct Counts { fn_count : Int }
test "mapped JSON key" {
  let c : Counts = { fn_count: 2 }
  let j = Json::object({"fn": Json::number(c.fn_count.to_double())})
  inspect(j.stringify(), content="{\\"fn\\":2}")
}
''')
    module('inspect_plain', 'test "plain" { inspect(2, content="2") }\n')
    module('inspect_bang', 'test "bang" { inspect!(2, content="2") }\n')
    module('modern', 'test "manifest" { inspect(2, content="2") }\n')
    module('legacy', 'test "manifest" { inspect(2, content="2") }\n', legacy=True)
    module('json', r'''// Pinned core still supports this parameter but deprecates explicit use.
// Limit the compatibility exception to this function, not the package.
#warnings("-deprecated")
fn classification(input : String) -> String {
  try {
    @json.parse(input, max_nesting_depth=16) |> ignore
    "ok"
  } catch {
    @json.DepthLimitExceeded => "resource"
    _ => "syntax"
  }
}
test "array depth 16 and 17" {
  inspect(classification(String::make(16, '[') + "0" + String::make(16, ']')), content="ok")
  inspect(classification(String::make(17, '[') + "0" + String::make(17, ']')), content="resource")
}
test "object depth 16 and 17" {
  let mut value = "0"
  for _ in 0..<16 { value = "{\"k\":" + value + "}" }
  inspect(classification(value), content="ok")
  inspect(classification("{\"k\":" + value + "}"), content="resource")
}
test "syntax distinct from depth" {
  inspect(classification("[1,"), content="syntax")
}
test "last value wins including equivalent escaped keys" {
  inspect(@json.parse("{\"onset_s\":\"1\",\"onset_s\":\"2\"}").stringify(), content="{\"onset_s\":\"2\"}")
  inspect(@json.parse("{\"a\":1,\"\\u0061\":2}").stringify(), content="{\"a\":2}")
}
test "strict UTF8 rejects invalid bytes" {
  let invalid = try { @utf8.decode(b"\xFF") |> ignore; false } catch { _ => true }
  inspect(invalid, content="true")
  inspect(@utf8.decode(b"abc"), content="abc")
}
test "surrogate handling" {
  inspect(classification("\"\\uD800\""), content="syntax")
  inspect(classification("\"\\uDC00\""), content="syntax")
  inspect(classification("\"\\uD800\\uDC00\""), content="ok")
}
''', imports='import { "moonbitlang/core/json", "moonbitlang/core/encoding/utf8", } for "wbtest"\n')
    stub = r'''#include <stdint.h>
#include <limits.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
_Static_assert(sizeof(int32_t) == sizeof(int), "MoonBit Int must match C int");
_Static_assert(SSIZE_MAX >= INT32_MAX, "ssize_t must cover bounded Int requests");
// Borrowed pointers are used only synchronously, never stored or freed here.
int32_t spike_read(const uint8_t *path, uint8_t *buffer, int32_t capacity, int32_t wanted) {
  if (capacity < 0 || capacity > 65536 || wanted < 0 || wanted > capacity) return -2;
  int fd = open((const char *)path, O_RDONLY);
  if (fd < 0) return -1;
  ssize_t got = read(fd, buffer, (size_t)wanted);
  int saved_errno = errno;
  close(fd);
  errno = saved_errno;
  return got < 0 ? -1 : (int32_t)got; // got <= wanted <= 65536
}
int32_t spike_write(const uint8_t *buffer, int32_t capacity, int32_t wanted) {
  if (capacity < 0 || capacity > 65536 || wanted < 0 || wanted > capacity) return -2;
  ssize_t wrote = write(STDOUT_FILENO, buffer, (size_t)wanted);
  return wrote < 0 ? -1 : (int32_t)wrote;
}
'''
    module('native', r'''#borrow(path, buffer)
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
''', executable=True, stub=stub)
    (ROOT/'native/spike-input.bin').write_bytes(b'T0\n')
