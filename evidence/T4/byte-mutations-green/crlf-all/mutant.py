#!/opt/homebrew/opt/python@3.14/bin/python3.14
import subprocess, sys
r = subprocess.run(['/Users/henryz/Desktop/比赛/mooneventeval-t0/_build/native/release/build/cmd/probe/probe.exe', *sys.argv[1:]], capture_output=True)
alter = True or "report-text" in sys.argv[2:] or "explain-text" in sys.argv[2:]
sys.stdout.buffer.write(r.stdout.replace(b"\n", b'\r\n') if alter else r.stdout)
sys.stderr.buffer.write(r.stderr)
sys.exit(r.returncode)
