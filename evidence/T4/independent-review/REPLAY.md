# Replay

Use the existing `source/` exact archive or extract `head.tar` into a new `source/` beside these scripts. Reuse the pinned toolchain and reference venv by linking source/.tools and source/.venv-reference to the original checkout's existing dependencies (the current copy already has these links). No global installation is required.

Run from any directory:

```
python3 /private/tmp/mooneventeval-t4-review-sxuadgmt/replay.py
python3 /private/tmp/mooneventeval-t4-review-sxuadgmt/byte-audit.py
```

`replay.py` verifies the original HEAD is the reviewed SHA before attaching read-only git metadata. `byte-audit.py` depends on the release binary produced by the first script and on executable permission on `crlf-probe.py`. If copying this evidence directory, use the copied absolute script paths; their sibling source/output locations are relative to `__file__`. The original dependency/git metadata checkout path is explicit in the scripts and must be updated deliberately if relocating machines.

The CRLF mutation is expected to produce a checker exit 0 on the reviewed flawed verifier. After the fix, a nonzero checker exit is the intended negative-control result. `real.stdout`, `mutant.stdout` and `byte-audit.json` are the raw reproduction witness. No product source is changed by the mutation.
