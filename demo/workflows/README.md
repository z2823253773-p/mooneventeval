# 三个完整工作流程（合成数据）

这里将用户拿来的材料、实际命令、报告字段和下一步用途连起来。输入来自此前P2的合成案例，现直接放到公开示例入口。**不是实地试用、真实音视频数据或用户采用证明**。先按根README构建；以下命令从仓库根运行。时间是最多六位小数的十进制秒字符串；已有TSV/CSV或模型输出需调用者先整理成JSON，本工具不负责读媒体或格式转换。

## 1. 检查多段音频的重复预测与漏检

**材料**：[audio.json](inputs/audio.json)，两段录制、alarm/door两个类别；一条alarm参考收到两条合格预测，一条door参考没有预测。

```sh
_build/native/release/build/cmd/mooneventeval/mooneventeval.exe evaluate demo/workflows/inputs/audio.json --format json > audio-result.json
```

**产物**：[完整报告](../output/workflow-audio.json)，TP=1/FP=1/FN=1，P=R=F1=0.5。查看`by_recording`和`by_label`分别定位audio-01的重复alarm预测与audio-02漏掉的door，再根据`false_positives`/`false_negatives`中的ID和时间回到调用者自己的音频检查。工具给出定位信息，不自动回放或修复音频。

## 2. 核对密集视频动作的候选竞争

**材料**：[video.json](inputs/video.json)，一段video-01里的两个jump参考和两个预测。r1可配p1/p2，r2只可配p1。

```sh
_build/native/release/build/cmd/mooneventeval/mooneventeval.exe evaluate demo/workflows/inputs/video.json --format json > video-result.json
```

**产物**：[完整报告](../output/workflow-video.json)，TP=2/FP=0/FN=0，`matches`列出r1与p2、r2与p1。开发者可以检查配对及其时间差/容差，区分候选冲突与确实漏掉的动作。仅适用于双方约定以起止点collar评测的片段任务，不计算IoU/mAP或替代其他视频基准。

## 3. 定位一次模型版本回归

**材料**：同一参考集的[旧版预测](inputs/regression-old.json)和[新版预测](inputs/regression-new.json)。合成变化只把p2起点从5.2改到5.21秒，参考起点为5秒、collar为0.2秒。

```sh
_build/native/release/build/cmd/mooneventeval/mooneventeval.exe evaluate demo/workflows/inputs/regression-old.json --format json > old-result.json
_build/native/release/build/cmd/mooneventeval/mooneventeval.exe evaluate demo/workflows/inputs/regression-new.json --format json > new-result.json
_build/native/release/build/cmd/mooneventeval/mooneventeval.exe explain-pair demo/workflows/inputs/regression-new.json --recording regression-01 --reference r2 --prediction p2 --format json > regression-explanation.json
```

**产物**：[旧版报告](../output/workflow-regression-old.json)为TP2/FP0/FN0、F1=1；[新版报告](../output/workflow-regression-new.json)为TP1/FP1/FN1、F1=0.5。外部脚本可比较`summary`和事件明细；[资格解释](../output/workflow-regression-explain.json)显示起点差0.21>0.2，`onset_pass=false`，终点通过，`eligible=false`。据此定位到起点越界，而不是笼统判断“模型变差”。双版本比较、阈值告警及训练操作由外部程序负责，CLI本身不包含回归管理功能。自动化调用应检查退出码及`status=completed`，不使用失败报告的评分。

## 重跑核对

```sh
python3 demo/reproduce.py --check --output /tmp/mooneventeval-workflows-check
```

使用一个尚不存在的新目录。该命令执行13条产品命令：原8条规则/报告示例加本页5条流程命令，检查快照、计数和回归原因。按`demo/README.md`准备参考环境并加`--reference-python .venv-reference/bin/python`可同时执行4个sed_eval对照。Python在此仅启动产品和检查交付示例，评分仍由MoonBit实现。
