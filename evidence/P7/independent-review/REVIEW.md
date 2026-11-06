# P7 independent TSV review

Base `e9165492c454b8b4b1fa199a272f8240d20551ac`; candidate `500b44a526a30f11e96988bf174f7ca0e8c02cf9`. Read-only candidate review on macOS arm64, 2026-11-05. Independent local review; separate from the parent's gate and CI.

**Critical 0 · Important 0 · Minor 1**

**Minor — clarify the command-specific I/O in CLI help.** `cli/dispatch.mbt:79`. Run `mooneventeval --help`: usage includes import-tsv, but the common footer says “Input: UTF-8 JSON task; default output: text.” Actual import-tsv takes two UTF-8 TSV files, defaults to JSON, and rejects text. Specify both command families in the footer. No functional importer blocker found.

**Independent checks.** Read AGENTS, current state, P7 v4 contract, TSV guide, plan and implementation delta. Built base and candidate in temporary trees from Git blobs via pinned compiler. Built a 42-member candidate ZIP, matched every member byte-for-byte to source, unpacked and rebuilt native release CLI. Tested that binary with:
- 40 repeatable generated pairs of multi-recording, multi-label Unicode inputs with variable BOM/line endings, quotes, controls, combined characters and rows above 10. Compared each event against separately generated physical-row IDs, side, filename, label and exact Decimal time. Verified codepoint-sorted IDs (r10 before r2), labels and recordings; default config 0.2/0.5; every emitted JSON evaluated successfully.
- Exact 8 MiB combined input with one tab-heavy malformed row: structured INVALID_TSV at reference[2] in about 0.013s; combining one additional byte: RESOURCE_LIMIT at tsv with observed=8388609. Checked 256/257 labels and 1000/1001 recordings, both-header-only, one side empty, empty file, bare CR, extra blank line, double BOM, strict UTF-8, empty label and time beyond 30 days. Failures checked for exact error-only envelope, single-LF stdout, empty stderr and exit class.
- Unpacked bundled fixtures produced task JSON. Compared the base and candidate process (exit, stdout, stderr) exactly on ten legacy requests including both evaluate formats, explain, version, and argument/format diagnostics. Inspected event limit, output+LF bound, order of file errors and dispatch paths. No independent Linux or full-gate run.

Probe in temp tree: `cd /private/tmp/p7-tsv-audit.Vq9X2r && python3 review.py`. No repository changes.
