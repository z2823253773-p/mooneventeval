#!/usr/bin/env python3
"""Freeze this review's original report, scripts and raw evidence by hash."""
from pathlib import Path
import hashlib
import json
import os

ROOT = Path(__file__).resolve().parents[1]
paths = []
for name in ['REVIEW.md','context.json','candidate-source.json','historical-fixture-copy.json','nominal.json','review-results.json']:
    paths.append(ROOT/name)
for name in ['scripts','evidence','results','controls']:
    paths += [path for path in (ROOT/name).rglob('*')
              if path.is_file() and not path.is_symlink()
              and '_build' not in path.parts and '__pycache__' not in path.parts]
for name in ['moon.mod','moon.work','main/moon.pkg','main/main.mbt']:
    paths.append(ROOT/'manual-consumer'/name)
paths += list((ROOT/'manual-consumer/_build').rglob('main.exe'))
paths.append(ROOT/'manual-unpacked/_build/native/release/build/cmd/mooneventeval/mooneventeval.exe')
for name in ['empty.json','invalid.json']:
    paths.append(ROOT/name)
files = {str(path.relative_to(ROOT)):dict(sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size)
         for path in sorted(set(paths))}
manifest = dict(schema_version=1,
                base='914cffd301d40eff8f4b2ecd697adb5052ebb031',
                candidate='a441ce89b57595c326031e8699b066777028f0b2',
                scope='Original independent T7 review; excludes subsequent author repair/closeout. Includes report, replay scripts, exact command receipts/raw outputs, real package archives and required standalone executables. Candidate export is captured by evidence/candidate-export/stdout plus candidate-source.json. Shared installed tools and intermediate build caches are excluded.',
                files=files)
target = ROOT/'SHA256SUMS.json'
target.write_text(json.dumps(manifest,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
for relative, info in files.items():
    path = ROOT/relative
    assert hashlib.sha256(path.read_bytes()).hexdigest() == info['sha256']
    path.chmod(path.stat().st_mode & ~0o222)
target.chmod(target.stat().st_mode & ~0o222)
print(json.dumps(dict(manifest=str(target),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),files=len(files),verified=True)))
