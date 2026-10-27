# MoonEventEval

**输入带类别、起点和终点的参考事件与预测事件，输出一份可追查到具体事件的评测报告。** 本项目交付 MoonBit 评测库和原生文件 CLI，适用于已取得标注与预测结果的事件级评测；不读取音视频、不训练模型、不生成检测结果。

## 运行后得到什么

`evaluate` 将 JSON 或文本报告写到 **stdout**，可以重定向保存为文件；`explain-pair` 输出一个指定事件对是否满足配对条件的解释。默认输出文本，加 `--format json` 得到机器报告。

| 评测报告内容 | 可以据此回答的问题 |
|---|---|
| `summary` | 总参考数、总预测数、TP/FP/FN 和 Precision/Recall/F1 是多少？ |
| `by_label`、`by_recording` | 哪个类别或哪段录制需要检查？ |
| `matches` | 具体选中了哪些一对一配对，时间差和容差是多少？ |
| `false_positives`、`false_negatives` | 哪条预测未匹配、哪条参考未检出？是没有合格候选，还是在本次最大匹配中未选中？ |
| `work` | 本次候选检查、合格边和匹配工作步数是多少？ |

例如一条参考、两条合格预测，得到 TP=1、FP=1、FN=0。下面是实际报告的 **`summary` 字段节选**：

<!-- output-summary:start -->
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
  "recall": 1,
  "f1": 0.6666666666666666
}
```
<!-- output-summary:end -->

完整成品：[JSON 报告](https://github.com/z2823253773-p/mooneventeval/blob/main/demo/output/duplicate.json) · [文本报告](https://github.com/z2823253773-p/mooneventeval/blob/main/demo/output/duplicate.txt) · [成品与对照说明](https://github.com/z2823253773-p/mooneventeval/blob/main/demo/README.md)。输入和运行命令见下文及 [EXAMPLES](EXAMPLES.md)。

报告中的匹配以最大配对数为目标，不优化时间误差。`explain-pair` 的 `eligible=true` 仅表示满足候选条件，**不表示该对已被最大匹配选中**。分母为零的指标输出 `null`；输入或资源错误返回失败状态，不返回完成评分。JSON 字段与库接口见 [API](docs/API.md)。

## 与 sed_eval 的关系

本项目是**参考事件级评测规则的 MoonBit 实现，不是 sed_eval 的全量移植或输出兼容替代品**。具体参考的是锁定提交的 `EventBasedMetrics`：同类别事件的起止点 collar 判定、终点按参考时长放宽的规则，以及 optimal 一对一最大匹配。sed_eval 本身已有 optimal 匹配，最大匹配不是本项目相对它的新算法。

本项目实现范围是整数时间比较、确定性匹配、事件明细/解释、稳定 JSON/文本和 MoonBit API；不实现 sed_eval 的分段评测、替代/插入/删除错误率等完整指标。参考规则、未移植部分、计数差异、许可证和锁定源码链接见 [参考范围与来源](THIRD_PARTY_NOTICES.md)。

Source repository: [z2823253773-p/mooneventeval](https://github.com/z2823253773-p/mooneventeval).
Native execution has been verified on **macOS arm64 and Linux x86_64** in
[the complete two-platform CI run](https://github.com/z2823253773-p/mooneventeval/actions/runs/39914869650).
The module identity is **local/mooneventeval 0.1.0**, a source candidate that
has not been published to a package registry. Python is development tooling,
not the scoring implementation.

## Build and run

Requires Python >=3.12, curl and a native C compiler. On a new checkout or
unpacked candidate, install the pinned local toolchain:

```sh
python3 scripts/install_toolchain.py
```

It installs only under `.tools`, checks pinned hashes and refuses to overwrite
an existing installation. No global installation is changed. Current local
verification reused the existing toolchain; the linked CI run independently
installed and verified it on both runner platforms.
Pinned compiler: `v0.10.14+7d59c7ec9`.

```sh
scripts/with-toolchain.sh moon build cmd/mooneventeval --target native --release --deny-warn
_build/native/release/build/cmd/mooneventeval/mooneventeval.exe --help
_build/native/release/build/cmd/mooneventeval/mooneventeval.exe --version
_build/native/release/build/cmd/mooneventeval/mooneventeval.exe evaluate examples/duplicate.json --format json
_build/native/release/build/cmd/mooneventeval/mooneventeval.exe evaluate examples/greedy-trap.json --format json
_build/native/release/build/cmd/mooneventeval/mooneventeval.exe evaluate examples/boundary.json --format json
_build/native/release/build/cmd/mooneventeval/mooneventeval.exe explain-pair examples/boundary.json --recording clip-01 --reference r1 --prediction p1 --format json
```

The three evaluations return TP/FP/FN **1/1/0**, **2/0/0**, **1/0/0**.
See [complete examples](EXAMPLES.md) for inputs, output summaries and reasoning,
and [public API](docs/API.md) for a standalone MoonBit consumer.

## Rules and input

Input is a regular UTF-8 JSON file (symlinks to regular files are accepted),
with `schema_version: 1`, declared labels, config and recordings. See the full
[duplicate fixture](examples/duplicate.json). No stdin or TSV/CSV is accepted.

Times and config values are ASCII decimal **strings**, with at most six
fractional digits. Time comparisons use Int64 microseconds and integer ppm;
there is no floating-point time comparison, rounding or epsilon. Numeric times
are rejected. IDs/labels are exact Unicode strings without trimming or
normalization. Duplicate JSON object keys, including escape-equivalent keys,
use the **last value**; raw input duplicate rejection is a known limitation.
Unknown schema fields, duplicate recording/event IDs and unknown labels fail
the whole task. One initial UTF-8 BOM is allowed.

Pairs must have the same recording and label. Onset difference is at most
`collar_s`; offset difference is at most
`max(collar_s, reference_duration * offset_ratio)`. Equality passes. Defaults:
collar `"0.2"`, ratio `"0.5"`. Events need not overlap. Matching maximizes the
number of pairs, not timing accuracy; IDs determine a stable traversal order.
An explanation checks eligibility without claiming a pair was selected.

TP is the number of selected pairs, FP is predictions minus TP, FN is references
minus TP. Global metrics pool counts before averaging. Each metric's zero
denominator yields `null`; two empty sides yield P/R/F1 all `null`. F1 is
computed directly as `2*TP/(reference+prediction)`.

## CLI protocol and limits

The command is first, the filename second, then option/value pairs. Text is
the default; `--format json` selects machine reports and JSON failures.
`--help`/`--version` stand alone. IDs may equal option names; spell a filename
starting with `--` using `./`. Invalid or repeated format selection gives a
text diagnostic. Files are read only; directories, FIFOs and devices fail.

Success goes to stdout with one terminal LF. Text failures go to stderr;
JSON failures go to stdout. Exit **0** means complete (including zero scores or
an ineligible explanation), **2** input/argument/file/output-I/O error,
**3** resource limit, **4** unexpected internal error. Failed evaluations have
no partial scores. Output I/O failure can leave an incomplete prefix: its
nonzero exit makes that prefix unusable as a completed report.

Limits include equality: input 8 MiB, nesting depth 16, 1,000 recordings,
256 labels, 2,000 reference+prediction events total, 256 Unicode codepoints per
ID/label, event times and collar at most 2,592,000 seconds (30 days), ratio 0–1,
matching work 20,000,000 steps, final UTF-8 output including LF 16 MiB. A legal
large graph may exhaust the work budget; no universal runtime guarantee is made.

## Evidence and licensing

[Validation](VALIDATION.md) explains the independent original-reference scope,
exact boundary differences, resource tests, mutations and remaining gaps.
The linked CI run passed all 17 verification steps on each platform, including
58 MoonBit tests, 15 CLI tests and 1,620 actual product invocations per platform.
These are synthetic developer checks, not user feedback, personal presentation
proof or competition acceptance.

Own source/docs: [MIT](LICENSE). External core/runtime notices are retained in
[third-party notices](THIRD_PARTY_NOTICES.md). The source candidate excludes
reference environments, local toolchains, probes, internal plans and raw logs.
