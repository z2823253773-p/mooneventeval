# Lossless original-history transport

GitHub rejects ordinary Git blobs above100MiB. One original independent-review
raw diff is150,195,290 bytes. The original local branch and all frozen proof stay
unchanged. The GitHub export omits only that path from its native commit
trees, preserving author/date/message and recording the commit-ID mapping.
It carries original-history.bundle (about23MiB) with the exact full original
history through4d5d3fbb, including the oversized blob. This is not an invented
history, an LFS pointer, or a claimed byte-identical native GitHub commit graph.

Before the unchanged full verifier, restore_ci_history.py checks the bundle
hash, imports it under refs/ci-evidence/original (without resetting HEAD),
checks its original tip and restores the exact proof bytes. T6/T7 historical
source SHA and file-hash checks remain mandatory; no evidence gate is removed.
New verification results use the actual dispatched GitHub export SHA.

history.json binds the original ref/tip, bundle digest and omitted file bytes/
digest. The bootstrap refuses corrupted bundles, path escapes, mismatched proof
and overwriting different existing data. Local fixture tests exercise those
failures and exact repeatable restoration. The source package excludes .ci,
reference environments and original raw evidence under its existing whitelist.

This transport was originally introduced during the PRIVATE R1 phase. The
repository was subsequently made PUBLIC under P2 authorization; see
[the current state](../docs/PROJECT_STATE.md) for actual public/CI status.
Namespace/package publication and registration are separate actions. Internal
logs and binaries retain build paths; original historical proof is unchanged.
