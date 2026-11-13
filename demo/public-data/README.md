# 用公开事件标注完成导入、评测和错误定位

本例使用DESED_public_eval的公开四列事件标注，不再只有手编的参考事件。来源、固定版本、原始hash和作者见[SOURCE.json](SOURCE.json)，再分发与改动见[NOTICE](NOTICE.md)。只使用前两段完整录制的11个事件、4个类别，不需要音频。完整小型原始标注表以gzip保存，可离线核对抽样。

**预测是受控构造，不是真实模型输出。** 基线复制参考；回归版人为制造起点偏移、遗漏和重复。这里演示真实格式接入和错误追踪，不声称模型得分、外部采用或完整DCASE兼容。

## 一条命令重跑与核对

从完整仓库根目录，先按README安装锁定工具链并构建native CLI，然后执行：

```sh
python3 demo/public-data/reproduce.py --check --output /tmp/mooneventeval-public-check
```

使用新的空输出目录。程序实际运行6条MoonBit产品命令：两次import-tsv、两次evaluate、两次explain-pair；Python只核对来源、编排命令和检查固定预期，不实现评分。数据或快照被篡改、命令非零、计数错误、解释错误都会失败。结果与错误分析保存到指定目录，公开固定成品见[output](output)。

## 自己运行产品命令

```sh
MEA_BIN=_build/native/release/build/cmd/mooneventeval/mooneventeval.exe
case_dir=$(mktemp -d /tmp/mooneventeval-public.XXXXXX)
"$MEA_BIN" import-tsv demo/public-data/reference.tsv --prediction demo/public-data/prediction-baseline.tsv > "$case_dir/baseline-task.json"
"$MEA_BIN" evaluate "$case_dir/baseline-task.json" --format json > "$case_dir/baseline.json"
"$MEA_BIN" import-tsv demo/public-data/reference.tsv --prediction demo/public-data/prediction-regressed.tsv > "$case_dir/regressed-task.json"
"$MEA_BIN" evaluate "$case_dir/regressed-task.json" --format json > "$case_dir/regressed.json"
"$MEA_BIN" explain-pair "$case_dir/regressed-task.json" --recording 1Ro0FgMWTUE_120_130.wav --reference r3 --prediction p3 --format json > "$case_dir/explain-shift.json"
"$MEA_BIN" explain-pair "$case_dir/regressed-task.json" --recording G5wlhYFdlxw_508_518.wav --reference r10 --prediction p12 --format json > "$case_dir/explain-duplicate.json"
```

生产脚本每一步都应检查退出码，不应把失败命令留下的文件作为完成报告；上面的reproduce.py已这样做。产品不会自动比较两个版本或设置质量阈值，这些是外部脚本的工作。

## 从报告走到下一步

| 数据 | reference/prediction | TP/FP/FN | P/R/F1 |
| --- | --- | --- | --- |
| 原样基线 | 11/11 | 11/0/0 | 1 |
| 受控回归 | 11/11 | 9/2/2 | 9/11，约0.818182 |

[完整错误分析](output/analysis.md)把两条FP和两条FN定位到事件与原始行。r3/p3起点差0.201>0.2，因此不合格；r12的Dishes被删去；r10/p12资格成立，但r10已与p10匹配，重复p12不会再次贡献TP。使用者据录制和时间回查自己的数据，而不是只看到一个下降的F1。

所有时间仍按字符串无损读取。四列格式之外的弱标注、软标签、无表头文件和其他基准协议不在本例支持范围。样例位于完整仓库，不在Mooncakes0.1.0的43成员库包中；库包的评分实现和此处运行的是同一MoonBit代码。
