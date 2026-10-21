# SDD ledger — plan: docs/superpowers/plans/tasks/T2-matching.md

Base: bb23267ac56f040f17797106a36659bed1613cd8
Task 2 IN_PROGRESS. Reuse isolated worktree spike/t0-feasibility.
Ruling: user 下一步 authorizes the presented T2 including first-free then iterative DFS. No approval inferred for T3/demo gate, TSV, or changing 20M budget.
Ruling: graph indices are canonical, rows ascending/deduplicated/in-range, produced by T3; returned pairs ascend reference. T2 consumes T1 EvalError and produces Matching and shared WorkBudget for T3.
Ruling: steps are per-call delta, shared used is whole-task total. Logical pair rewrite counts once, root entry once even when first-free falls back; new DFS owner entries charged. Degree tally O(E) is bounded graph bookkeeping, not search work, consistent with the mandated 3-step single-edge test. Internal adjacency_checks makes benchmark evidence observable without a public API.
Risk: wrong traversal or accounting invalidates fixed pair and resource claims; exhaustive oracle, literal budget, chain, dense and mutation gates required before completion.

Task 2 RED: absent Matching/WorkBudget/maximum_matching; oracle module absent. Logs evidence/T2/*matching-red.*, *oracle-red.*. First compile exposed only unconstructed-private-struct and deprecated tuple Show warnings; narrow temporary WorkBudget annotation and boolean equality assertions fixed diagnostics without weakening deny-warn.
Task 2 GREEN: 753 graph fixtures (689 exhaustive, 64 seeded), legal unique sorted pairs verified in MoonBit and captured/rechecked independently by Python; byte-identical regeneration. Budget trap hand count 11, all limits 0..10 fail without Matching; group delta sharing and 1000-deep explicit stack pass.
Task 2 native: complete500=126250 steps, complete1000=502500, sparse1000=3000, chain1000=6997; all full cardinality under20M. Timing scope is direct fresh process including graph construction/assertions/protocol, excluding compilation. Two isolated behavioral mutants killed after passing controls; main source unchanged.
Task 2: complete (commits bb23267..e96d130, tests: scripts/with-toolchain.sh moon test eventeval --target native --deny-warn → Total tests: 25, passed: 25, failed: 0.)

Final review: fresh gpt-6-astra/high read-only /root/t2_independent_review, range bb23267..e96d130. Critical0 Important0 Minor0; no fix pass or re-review needed. Independently rebuilt25/25, Hall formula753/753, direct new binary753+fourbench, oracle6/6, regeneration and two behavior mutants. Full prior Python4/4+validation15/15 log/hash audit only; not independently rerun.
Final: Ruling: invalid internal adjacency/budget remains outside frozen preconditions — T3 must construct canonical in-range unique rows and bounded shared budget — cost if violated is incorrect pairing or panic; no public input-validation claim.
Final: Ruling: raw-event reorder stability remains a T3 gate, not established by canonical-graph tests — cost if skipped is input-order-dependent reports; no end-to-end stability claim yet.
Final: Ruling: sampled dense/chain success does not guarantee every legal graph under20M or Linux time — Resource remains valid and macOS-only timings are labeled — cost of extrapolation is misleading resource/performance promises.
Final deferred minors: none. Branch/worktree kept for staged T3; no integration requested, no merge/push/publication. Durable source/evidence/decisions/review copied to committed paths before removing only this plan's ignored workspace.
