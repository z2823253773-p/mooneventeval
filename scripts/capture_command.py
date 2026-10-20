"""Capture a command to disk without filling the chat with raw output."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time
from datetime import datetime, timezone

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', required=True)
    parser.add_argument('--name', required=True)
    parser.add_argument('--timeout', type=int, default=600)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if not all(re.fullmatch(r'[A-Za-z0-9_-]+', x) for x in (args.stage, args.name)):
        parser.error('stage/name must be simple identifiers')
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not command or args.timeout <= 0:
        parser.error('provide a command and a positive timeout')
    root = Path(__file__).resolve().parents[1]
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    folder = root/'evidence'/args.stage
    folder.mkdir(parents=True, exist_ok=True)
    log = folder/f'{stamp}-{args.name}.log'
    record = log.with_suffix('.json')
    started = time.monotonic()
    reason = None
    with log.open('wb') as stream:
        try:
            run = subprocess.run(command, cwd=root, stdout=stream, stderr=subprocess.STDOUT, timeout=args.timeout)
            code = run.returncode if run.returncode >= 0 else 128-run.returncode
        except subprocess.TimeoutExpired:
            code, reason = 124, 'timeout'
        except OSError as exc:
            code, reason = 127, str(exc)
            stream.write((reason+'\n').encode('utf-8'))
    payload = {
        'command': command, 'cwd': str(root), 'exit_code': code, 'reason': reason,
        'elapsed_seconds': round(time.monotonic()-started, 3),
        'log': str(log.relative_to(root)), 'log_sha256': hashlib.sha256(log.read_bytes()).hexdigest(),
        'scope': args.stage, 'assessment': 'command result only; not an automatic product acceptance claim'
    }
    record.write_text(json.dumps(payload, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'exit_code': code, 'record': str(record.relative_to(root)), 'log': payload['log']}, ensure_ascii=False))
    if code:
        for line in log.read_text(errors='replace').splitlines()[-30:]:
            print(line, file=sys.stderr)
    return code

if __name__ == '__main__':
    raise SystemExit(main())
