# Review replay and artifact map

Read `review.md` first. This is the original single-pass review of candidate 1831fbc21199974b77c4a66675307d0071f88bb0, not a verdict on subsequent author fixes.

`metadata.json` identifies the source archive, per-file source hashes, exact candidate/base, original source location, product SHA256 and local platform. `candidate.tar` holds the reviewed source and needed T3 byte baselines. `product/mooneventeval.exe` is the actual independently built/replayed release binary. `receipts/*/receipt.json` records each executed command, cwd, exit and stdout/stderr SHA256. Raw command outputs are `stdout.bin`/`stderr.bin`. Inner test evidence is under `process/`, `cli-bytes/`, `native-low-fd/`, `demo/` and `extra/`; these contain original binary stdout/stderr. The final manifest hashes all evidence files outside the disposable build checkout.

The original independent reproduction can be replayed directly with the preserved binary (from any directory):

```sh
/path/to/evidence/product/mooneventeval.exe evaluate absent --unknown --recording --format json
/path/to/evidence/product/mooneventeval.exe evaluate absent --unknown ordinary --format json
```

Both exit 2; first wrongly emits text stderr, second correctly emits JSON stdout. The file need not exist: argument rejection precedes file open.

To rebuild, extract `candidate.tar` into a NEW temporary checkout; symlink its `.tools` and `.venv-reference` to the existing pinned originals. Do not install or change globals. Run the command arrays recorded in the receipts from that checkout, substituting the new absolute evidence/output paths. Use a new output directory for each command. `run.py` is the original raw-capture wrapper; its parent must contain `checkout/` and `receipts/`. `extra_checks.py` is the exact independent 42-case grammar probe; its parent must also contain that checkout and a nonexistent `extra/` directory.

Commands that write a `git_head` label need detached metadata for the reviewed candidate, not the author's later HEAD. In the temporary checkout only, either use a detached temporary clone at the candidate or create a `.git` directory whose `HEAD` contains the candidate hash and whose `objects` directory is a read-only-use symlink to the existing original repository common object store. Do not copy a pointer that now resolves to a later author HEAD. Always verify `git rev-parse HEAD` before labels are produced.

Main original commands (exact original cwd/path/env values are in receipts):

```sh
scripts/with-toolchain.sh moon test --target native --deny-warn
scripts/with-toolchain.sh moon build cmd/mooneventeval --target native --release --deny-warn
python3 -W error::ResourceWarning -m unittest discover -s tests
.venv-reference/bin/python -W error::ResourceWarning -m unittest discover -s validation/tests -v
MEE_BIN=_build/native/release/build/cmd/mooneventeval/mooneventeval.exe MEE_EVIDENCE=<new-output>/process python3 -W error::ResourceWarning -m unittest discover -s tests/cli -v
python3 validation/check_cli_reports.py --product _build/native/release/build/cmd/mooneventeval/mooneventeval.exe --output <new-output>/cli-bytes
python3 validation/check_native_io.py --output <new-output>/native-low-fd
python3 scripts/demo.py --bin _build/native/release/build/cmd/mooneventeval/mooneventeval.exe --output <new-output>/demo
python3 ../extra_checks.py
```

The native FD helper performs `moon test cmd/mooneventeval --target native --release --deny-warn --build-only` before reading test metadata, then runs each actual native whitebox executable under RLIMIT_NOFILE=64. The extra probe exits 0 to save its exploratory report even if expectations fail; its `extra/report.json` explicitly lists the four I1 failures. Do not count its process exit as an acceptance pass.

No patches/fixes were made to reviewed product sources. Review source snapshots, source diffs and explicit limitations are retained separately from the author's expected resolution.
