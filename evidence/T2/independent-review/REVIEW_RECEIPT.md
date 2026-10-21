# T2 independent review execution receipt

Reviewed repository: /Users/henryz/Desktop/比赛/mooneventeval-t0
Range: bb23267ac56f040f17797106a36659bed1613cd8..e96d130338ab379968a5cb4624788ba079dadda9
Independent reviewer did not mutate repository checkout, index, or HEAD.
All builds/mutations were in this temporary directory.

## Fresh release build and execution

Copied moon.mod and eventeval/ from the reviewed checkout into this directory.
Command (cwd=this directory):

    /Users/henryz/Desktop/比赛/mooneventeval-t0/scripts/with-toolchain.sh moon test eventeval --target native --release --deny-warn

Exit 0; 25 passed / 0 failed. Raw log: moon-review.log.
Then directly executed this directory's _build/native/release/test/eventeval/eventeval.whitebox_test.exe using filename:index-index+1 selection from __whitebox_test_info.json. Each process returned 0 and exactly one result record with empty message.

Raw direct-execution logs:
- matching_oracle_exhaustive_and_seeded.log (753 graph records; exact equality to native-committed/graph-oracle-actual.json)
- matching_benchmark_complete_500.log (125250 adjacency checks; 126250 steps; 500 pairs)
- matching_benchmark_complete_1000.log (500500 adjacency checks; 502500 steps; 1000 pairs)
- matching_benchmark_sparse_1000.log (1000 adjacency checks; 3000 steps; 1000 pairs)
- matching_benchmark_chain_1000.log (2999 adjacency checks; 6997 steps; 1000 pairs)

## Independent expectation and evidence audit

Executed an independent Hall-deficiency/min-cut formula on all 753 fixture graphs:

    n = len(graph)
    hall = min(n - mask.bit_count() + len({p for r, row in enumerate(graph)
                if mask & (1 << r) for p in row}) for mask in range(1 << n))

All fixture expected values equaled hall. Every recorded pair was in-range and an actual edge; reference and prediction indices were each unique; pair arrays were sorted. Case IDs were unique and exhaustive count was 753. This check was executed inline; its stdout is in the reviewer tool transcript, not a separate raw log.

All native-committed report source hashes matched current files, artifact hash matched current binary, and report git_head matched the reviewed head. All *committed*.json receipt log SHA-256 values matched their logs.

Called validation.graph_oracle.emit_mbt with temporary output paths. Both regenerated.mbt and regenerated-cases.json are byte-identical to the committed generated MoonBit fixture and graph-oracle-cases.json. Retained both temporary regenerated files.

Command (cwd=reviewed repository; -B prevents Python bytecode writes):

    python3 -B -m unittest discover -s validation/tests -p test_oracles.py -v

Exit 0; 6 passed. Raw log: python-oracle-review.log.

## Behavioral mutations

Each subdirectory prediction-reuse/ and greedy-only/ is an independent copy of moon.mod and eventeval/. Ran baseline then mutated copy using:

    /Users/henryz/Desktop/比赛/mooneventeval-t0/scripts/with-toolchain.sh moon test eventeval --target native --deny-warn --filter TEST_NAME

prediction-reuse: TEST_NAME=matching_one_to_one_duplicate_and_isolated; replaced `if prediction_match[p] == -1 {` with `if true {`.
greedy-only: TEST_NAME=matching_augmenting_trap; inserted `if reference_match[root] == -1 { continue }` immediately before visited-array initialization.

Both baseline controls exit 0 (1 passed); both mutants exit 2 (1 behavioral expect assertion failure). Compiler errors were not counted as kills. Logs: prediction-reuse/control.log, prediction-reuse/mutant.log, greedy-only/control.log, greedy-only/mutant.log. Mutated source files remain under their temporary subdirectories for inspection. Original matching.mbt content was checked unchanged.

## Verification boundary

Freshly reran MoonBit 25/25, graph-oracle Python 6/6, direct native graph/benchmark executions, regeneration, and both mutations. Reviewed existing committed Python 4/4 and full validation 15/15 logs and their hashes; did not independently rerun those two entire pre-existing suites. No Linux, public API/JSON integration, publishing, or worst-case wall-time claim.
