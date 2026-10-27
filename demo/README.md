# 看一份实际输出，再看参考范围

本目录交付的是已由真实 CLI 生成的报告快照。输入是带标签和时间区间的事件列表；输出是分数、配对明细与资格解释，不是识别结果或修复后的标注。

## 1. 用户会拿到什么

从仓库根目录构建后运行：

```sh
_build/native/release/build/cmd/mooneventeval/mooneventeval.exe evaluate examples/duplicate.json --format json > result.json
_build/native/release/build/cmd/mooneventeval/mooneventeval.exe evaluate examples/duplicate.json --format text > result.txt
```

这两份文件分别对应 [完整机器报告](output/duplicate.json) 和 [完整文本报告](output/duplicate.txt)。输入有一条参考和两条同类合格预测。**以下文本块就是该次 CLI 的完整 stdout**：

```text
MoonEventEval 0.1.0 | collar-max-cardinality/v1
状态：completed
配置：collar_s=0.2 offset_ratio=0.5
汇总：reference=1 prediction=2 TP=1 FP=1 FN=0 precision=0.5 recall=1 F1=0.6666666666666666
按类别：
  label="alarm" reference=1 prediction=2 TP=1 FP=1 FN=0 precision=0.5 recall=1 F1=0.6666666666666666
按录制：
  recording="clip-01" reference=1 prediction=2 TP=1 FP=1 FN=0 precision=0.5 recall=1 F1=0.6666666666666666
所选配对（最大基数；不优化时间误差）：
  recording="clip-01" label="alarm" reference=(id="r1" label="alarm" onset_s=10 offset_s=12) prediction=(id="p1" label="alarm" onset_s=10 offset_s=12) label_match=true onset_pass=true offset_pass=true eligible=true onset_delta_s=0 onset_limit_s=0.2 offset_delta_s=0 offset_limit_s=1
未匹配预测（FP）：
  recording="clip-01" id="p2" label="alarm" onset_s=10.05 offset_s=12.05 candidate_count=1 reason=unselected_in_maximum_matching
未匹配参考（FN）：
说明：有候选但未选中不表示该事件在所有最大匹配中均不可能被选中。
工作量：candidate_checks=2 eligible_edges=2 matching_steps=3
```

JSON 中：`matches[0]` 是 r1 与 p1；`false_positives[0]` 是未选中的 p2，其 `candidate_count=1`、`reason=unselected_in_maximum_matching`；`false_negatives=[]`。报告保留每条事件的ID/类别/时间及每对的时间差/容差，因此可以定位问题事件，不只看最终F1。

## 2. 资格解释与所选配对是两个问题

[边界解释](output/boundary-explanation.json) 展示起点差0.2、起点容差0.2等具体依据。[p2资格解释](output/eligible-unselected.json) 的 `eligible=true`，但上面的实际评测选择p1，p2仍出现在FP列表。解释只检查一对是否有资格，不运行最大匹配或证明它已被选中。

## 3. 与锁定原版 sed_eval 的四个对照

| 合成输入 | MoonEventEval 原始报告 | sed_eval 原始结果与说明 |
|---|---|---|
| [重复预测](../examples/duplicate.json) | [TP1/FP1/FN0](output/duplicate.json) | [Ntp1/Nfp1/Nfn0](reference/duplicate.json)；Nsubs0，双方一致 |
| [候选竞争](../examples/greedy-trap.json) | [TP2](output/greedy-trap.json) | [optimal也是Ntp2](reference/greedy-trap.json)；不宣传超过上游 |
| [alarm被预测成door](inputs/wrong-label.json) | [TP0/FP1/FN1](output/wrong-label.json) | [raw Ntp0/Nsubs1/Nfp0/Nfn0](reference/wrong-label.json)；另存共同口径投影0/1/1 |
| [10.1到10.3，容差0.2](inputs/decimal-boundary.json) | [TP1](output/decimal-boundary.json)，十进制差恰好合格 | [Ntp0](reference/decimal-boundary.json)，binary64边界差异；不计为一致 |

共同规则、未移植功能、许可证与固定上游源码定位见 [THIRD_PARTY_NOTICES](../THIRD_PARTY_NOTICES.md)。参考JSON的 `raw` 保留原始统计，`projected` 仅为开发适配器的共同口径；它们不是本产品新增输出字段。浮点非有限值也只在开发适配器中另作安全标记。

## 4. 重跑与检查快照漂移

产品报告不需要安装 sed_eval。构建后，用一个**尚不存在的新输出目录**运行：

```sh
python3 demo/reproduce.py --check --output /tmp/mooneventeval-report-check
```

它实际运行8条产品命令，将stdout与本目录8份快照逐字节比较，并检查声明的计数、解释及README摘要。要同时重跑4个参考例子，需先按仓库的锁定参考环境准备步骤安装依赖，然后：

```sh
python3 demo/reproduce.py --check --reference-python .venv-reference/bin/python --output /tmp/mooneventeval-reference-check
```

`--write`用于有意重新生成快照；它不是验证旧快照的命令。上游依赖可能发出弃用警告，脚本保存stderr；原版评分失败、快照不符或产品stderr非空仍失败。快照与规则均为合成开发演示，不是外部用户采用或真实音视频数据兼容性证明。

本目录随完整Git仓库提供，不属于38文件的最小源码包；最小包仍含三个可运行输入、库API、README、EXAMPLES及参考范围说明。
