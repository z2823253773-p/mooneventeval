"""Retain receipt for bounded range-download workaround used during T0."""
import hashlib
import json
from pathlib import Path
import re
import shutil

REPO = Path(__file__).resolve().parents[2]
CACHE = REPO/'.tools/downloads'
if __name__ == '__main__':
    ranges = [(40000000,51999999), (52000000,63999999), (64000000,75999999), (76000000,85223028)]
    receipt = {'url': 'https://cli.moonbitlang.com/binaries/0.10.14%2B7d59c7ec9/moonbit-darwin-aarch64.tar.gz',
               'first_request_exit': 28, 'first_request_log': 'evidence/T0/download-binary.log',
               'range_requests': [], 'prefix_bytes': 40000000}
    for i, (start, end) in enumerate(ranges):
        header = (CACHE/f'part{i}.headers').read_text()
        expected = f'bytes {start}-{end}/85223029'
        actual = re.findall(r'content-range:\s*([^\r\n]+)', header, re.I)[-1]
        part = CACHE/f'part{i}'
        assert actual == expected and part.stat().st_size == end-start+1, (actual, expected)
        receipt['range_requests'].append({'range': [start,end], 'content_range': actual,
            'bytes': part.stat().st_size, 'exit_code': 0,
            'sha256': hashlib.sha256(part.read_bytes()).hexdigest(), 'log': f'evidence/T0/download-part{i}.log'})
    with (CACHE/'moonbit.tar.gz').open('rb') as source, (CACHE/'assembled.tar.gz').open('wb') as target:
        prefix = source.read(40000000)
        assert len(prefix) == 40000000
        target.write(prefix)
        for i in range(4):
            with (CACHE/f'part{i}').open('rb') as source_part:
                shutil.copyfileobj(source_part, target)
    actual = hashlib.sha256((CACHE/'assembled.tar.gz').read_bytes()).hexdigest()
    expected = json.loads((REPO/'docs/toolchain.lock.json').read_text())['binaries']['darwin-aarch64']
    assert actual == expected, (actual, expected)
    # Preserve the still-running slow transfer under a separate filename.
    (CACHE/'moonbit.tar.gz').rename(CACHE/'slow-transfer.tar.gz')
    (CACHE/'assembled.tar.gz').rename(CACHE/'moonbit.tar.gz')
    receipt['assembled_sha256'] = actual
    receipt['publisher_sidecar'] = (CACHE/'moonbit.tar.gz.sha256').read_text().strip()
    receipt['platform_scope'] = 'macOS arm64 only; no Linux execution'
    (REPO/'evidence/T0/download-receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt))
