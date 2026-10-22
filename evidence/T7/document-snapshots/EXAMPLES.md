# Three complete synthetic examples

Run from the module root after the [README build](README.md). Output blocks
are summaries of the full stable JSON reports, not substitute reports.

## Duplicate predictions

Input (`examples/duplicate.json`):

```json
{
  "schema_version": 1,
  "labels": [
    "alarm"
  ],
  "config": {
    "collar_s": "0.2",
    "offset_ratio": "0.5"
  },
  "recordings": [
    {
      "id": "clip-01",
      "reference": [
        {
          "id": "r1",
          "label": "alarm",
          "onset_s": "10",
          "offset_s": "12"
        }
      ],
      "prediction": [
        {
          "id": "p1",
          "label": "alarm",
          "onset_s": "10",
          "offset_s": "12"
        },
        {
          "id": "p2",
          "label": "alarm",
          "onset_s": "10.05",
          "offset_s": "12.05"
        }
      ]
    }
  ]
}
```

```sh
_build/native/release/build/cmd/mooneventeval/mooneventeval.exe evaluate examples/duplicate.json --format json
```

Expected summary:

```json
{
  "counts": {
    "reference": 1,
    "prediction": 2,
    "tp": 1,
    "fp": 1,
    "fn": 0
  },
  "precision": 0.5,
  "recall": 1.0,
  "f1": 0.6666666666666666
}
```

One reference and two eligible predictions yield one selected pair and one FP. No deduplication is performed. P=0.5, R=1, F1=2/3.

## Augmenting-path trap

Input (`examples/greedy-trap.json`):

```json
{
  "schema_version": 1,
  "labels": [
    "alarm"
  ],
  "config": {
    "collar_s": "0.2",
    "offset_ratio": "0.5"
  },
  "recordings": [
    {
      "id": "clip-01",
      "reference": [
        {
          "id": "r1",
          "label": "alarm",
          "onset_s": "10",
          "offset_s": "11"
        },
        {
          "id": "r2",
          "label": "alarm",
          "onset_s": "10.3",
          "offset_s": "11.3"
        }
      ],
      "prediction": [
        {
          "id": "p1",
          "label": "alarm",
          "onset_s": "10.15",
          "offset_s": "11.15"
        },
        {
          "id": "p2",
          "label": "alarm",
          "onset_s": "9.85",
          "offset_s": "10.85"
        }
      ]
    }
  ]
}
```

```sh
_build/native/release/build/cmd/mooneventeval/mooneventeval.exe evaluate examples/greedy-trap.json --format json
```

Expected summary:

```json
{
  "counts": {
    "reference": 2,
    "prediction": 2,
    "tp": 2,
    "fp": 0,
    "fn": 0
  },
  "precision": 1.0,
  "recall": 1.0,
  "f1": 1.0
}
```

r1 can match p1 or p2; r2 can match only p1. A first greedy r1→p1 choice must be rerouted to r1→p2, r2→p1 to reach TP2. Original sed_eval optimal also reaches TP2; this demonstrates the need for augmentation rather than a superiority claim.

## Inclusive exact onset boundary

Input (`examples/boundary.json`):

```json
{
  "schema_version": 1,
  "labels": [
    "alarm"
  ],
  "config": {
    "collar_s": "0.2",
    "offset_ratio": "0.5"
  },
  "recordings": [
    {
      "id": "clip-01",
      "reference": [
        {
          "id": "r1",
          "label": "alarm",
          "onset_s": "10",
          "offset_s": "12"
        }
      ],
      "prediction": [
        {
          "id": "p1",
          "label": "alarm",
          "onset_s": "10.2",
          "offset_s": "12.2"
        }
      ]
    }
  ]
}
```

```sh
_build/native/release/build/cmd/mooneventeval/mooneventeval.exe evaluate examples/boundary.json --format json
```

Expected summary:

```json
{
  "counts": {
    "reference": 1,
    "prediction": 1,
    "tp": 1,
    "fp": 0,
    "fn": 0
  },
  "precision": 1.0,
  "recall": 1.0,
  "f1": 1.0
}
```

The onset difference is exactly 0.2 seconds, equal to the collar. Offset difference 0.2 is within max(0.2, 2×0.5)=1 second. Both comparisons pass without floating-point epsilon.

## Explain the boundary pair

```sh
_build/native/release/build/cmd/mooneventeval/mooneventeval.exe explain-pair examples/boundary.json --recording clip-01 --reference r1 --prediction p1 --format json
```

Its basis reports signed onset/offset deltas `"0.2"`, onset limit `"0.2"`,
offset limit `"1"`, and all four pass/eligibility booleans true. No summary or
matching selection is asserted by this command. Replace `--format json` with
`--format text` for human-readable output. These are developer reproductions,
not evidence of the author's personal spoken demonstration.
