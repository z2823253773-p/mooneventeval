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
