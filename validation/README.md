# Development reference environment

This directory is not a product runtime dependency. The qualified environment
is macOS arm64, uv 0.11.14, Python 3.11.14, NumPy 1.26.4 and dcase_util 0.2.20.
All 45 resolved versions/hashes are in `reference.lock`. The exact sed_eval
commit/archive and source-file hashes are in `reference-sources.json`.

On a new checkout, run from the repository root with Python >=3.12 and uv:

```sh
python3 validation/bootstrap_reference.py
.venv-reference/bin/python -m unittest discover -s validation/tests -v
```

Existing environments are never overwritten. To independently rebuild again:

```sh
python3 validation/bootstrap_reference.py --venv .venv-reference-rebuild
```

The bootstrap uses project-local uv/Python/runtime caches, checks the Python
build identity, preinstalls the hash-locked build backend, then synchronizes
the complete lock with hash enforcement and build isolation disabled. It runs
dependency checks and the real reference self-check. First trial failures and
the successful rebuild are retained under `evidence/T1b/`.

`sed_reference.evaluate_document(document)` accepts already validated synthetic
PRD documents, not product output. Its four result sections keep raw overall
counts/metrics, class-wise counts/metrics, the explicitly named common-count
projection, and metric-definition flags. Raw NaN/Infinity use explicit tagged
objects, never zero. The original reference uses Float64 time.

The upstream constructor rejects zero collar. The adapter preserves that error;
the product's valid zero collar cases belong to the exact rational oracle.
Passing this self-check does not establish product parity, Linux support, or
completion of the final independent acceptance gate.

The first compatible trial needed setuptools 80.9.0 because dcase_util imports
`pkg_resources` without declaring its runtime provider. Its deprecation warning
is preserved. No NumPy alias or reference algorithm is patched.

sed_eval is MIT licensed, Copyright (c) 2016 Tampere University of Technology.
Its archive's `LICENSE.txt` SHA is retained in `reference-sources.json`;
the upstream commit is linked in `reference-requirements.in`.

## Matching validation (T2)

The stdlib-only graph oracle enumerates all legal partial injections; it does
not share the product's augmenting-path algorithm. From the repository root:

```sh
python3 -m unittest discover -s validation/tests -p test_oracles.py -v
python3 validation/graph_oracle.py --emit-mbt eventeval/matching_oracle_generated_wbtest.mbt --cases-json evidence/T2/graph-oracle-cases.json
scripts/with-toolchain.sh moon test --target native --deny-warn
python3 validation/check_matching_native.py --output-dir evidence/T2/native
python3 validation/mutate_matching.py
```

The 753 fixed cases comprise every graph with 0–3 vertices per side and 64
seeded graphs with 4–7 per side. The generated MoonBit file contains literals
and test calls only. The generator invokes the locked formatter for byte-stable
regeneration. Full inputs/expectations and actual selected pairs are retained.

The native checker builds a release whitebox executable, then invokes that
artifact directly; it checks MoonBit's result protocol as well as process status.
Benchmark times include process startup, graph construction, validity assertions
and test protocol; compilation is excluded. They are macOS arm64 observations,
not isolated matcher-call timings or a cross-platform performance guarantee.
Mutation copies are disposable directories under ignored `.tools/`; controls
must pass and mutant assertions must fail. Compiler failures do not count.

## T3 exact and prototype checks

`rational_oracle.py` converts Decimal input strings to Fraction and works in
seconds, separately from product microsecond/ppm arithmetic. `compare.py` checks
full report partitions/bases/degrees/metrics against independent time and graph
oracles, then compares the original reference's explicit projection, per-label
raw counts and independently rerun per-recording projections. Raw results are
retained. Whole reports must remain byte-identical after reordering; renaming
event IDs may change selected identities but must preserve summary counts.

```sh
.venv-reference/bin/python -W error::ResourceWarning -m unittest discover -s validation/tests -v
.venv-reference/bin/python validation/compare.py --phase prototype --product _build/native/release/build/cmd/probe/probe.exe --output evidence/T3/parity
python3 validation/check_probe.py --product _build/native/release/build/cmd/probe/probe.exe --output evidence/T3/process
python3 validation/mutate_eligibility.py
```

Prototype cases are fixed synthetic and seeded binary grids, not the later
non-boundary random corpus. Zero collar preserves the original reference error
and uses exact-oracle checks; it is not reference parity. A declared decimal
boundary difference is classified only when exact product checks pass, specific
binary64 candidate flips exist, and original reference TP equals an independently
built binary64 graph oracle. Unexplained differences block success. There is no
epsilon or sample deletion. Product runtime never imports these Python tools.
