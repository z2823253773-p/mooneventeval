# Independent P6 review

Reviewed the whole diff from 5b7dfafe6b069d333f73a8375845651cd6cb6d9a through 3ceabc725ed9eb213d9da086717f4ff7d5b39829 against AGENTS.md, the P6 plan, and the v3 input contract. Locally rebuilt both SHAs from archived Git source with the locked MoonBit compiler. No tracked or frozen-evidence edits.

## Findings

- Critical — 0.
- Important — 1. `docs/PROJECT_POSITIONING.md:21` still calls duplicate-key last-wins a current product limitation. `docs/选题差异咨询素材.md:3` links to this file as the source for current implemented facts. A user copying that statement to explain duplicate input would describe the opposite of the new runtime. Update that line to state v3 rejects duplicates, retaining last-wins only in an explicitly historical context. `docs/demo.md:58` has the same phrase in a page explicitly scoped to T5 at line 1. Clarifying that line if using it as a rerunnable talk script is sufficient, without rewriting frozen evidence.
- Minor — 1. `eventeval/input_wbtest.mbt:147–169` tests message size, JSON validity and the offset, yet never asserts which key the message contains, the exact 64-scalar prefix, or how it quotes controls. A temporary mutant changing `eventeval/input.mbt:255` from 64 to 0 replaces every nonempty key with `"..."`. All four targeted MoonBit duplicate-key tests and the native CLI duplicate-key test still passed. Add exact assertions for a short key containing a control and a supplementary code point, as well as a key with 64 supplementary code points followed by a distinct 65th scalar, verifying truncation and offset.
- No production blocker found. The string walk skips escaped units inside strings, matches the pinned parser's four whitespace characters, and scopes decoded-key maps to braces. Key-token decoding, map work and whitespace lookahead do not introduce repeated scans of whole suffixes. The scanner uses an explicit stack bounded by the parser's 16-container limit. The largest diagnostic prefix is 64 original scalars plus a truncation marker.

## Independent native-process checks

- Seed 836223 generated 500 nested JSON documents using varied escaped or literal key forms, control characters, punctuation, supplementary and combining characters, 64/65-scalar keys, JSON whitespace and alternating BOM. All 410 unique-key documents produced byte-identical stdout/stderr and equal exit codes across the two releases. All 90 duplicate-bearing documents returned Input/DUPLICATE_KEY, exit 2, path "$". Each candidate message decoded to the expected first-conflicting key preview and exact zero-based UTF-16 offset, as computed independently during generation.
- Eight directed tests passed. At exactly 8 MiB, 420,000 earlier unique keys followed by a duplicate and two roughly 4 MiB repeated keys both returned the right duplicate offset. One byte over the cap returned RESOURCE_LIMIT. Depth 16 returned DUPLICATE_KEY and 17 returned RESOURCE_LIMIT. Trailing malformed syntax, a trailing lone surrogate, and a trailing invalid UTF-8 byte returned the respective syntax/encoding error despite an earlier duplicate.
- `git diff --check 5b7dfaf 3ceabc7` passed. The changed paths exclude scoring, report code, package metadata, and frozen evidence. Full gate/pack verification, CI and subsequent metadata are outside this review.

Private reproducibility workspace: /private/tmp/mee-p6-reviewed.Iv3ZiJgB (differential.py, limits.py and mutant).
