#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys
exe=Path(__file__).resolve().parent/'source/_build/native/release/build/cmd/probe/probe.exe'
r=subprocess.run([str(exe),*sys.argv[1:]],capture_output=True)
sys.stdout.buffer.write(r.stdout.replace(b'\n',b'\r\n'))
sys.stderr.buffer.write(r.stderr)
sys.exit(r.returncode)
