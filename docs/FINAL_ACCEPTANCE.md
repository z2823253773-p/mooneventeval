# MoonEventEval 最终验收入口

更新2026-11-13。用户已确认初审通过；本轮最终候选已通过本地完整门、GitHub自动快速门及macOS/Linux完整门，最终验收仍由组委会评定。本页按已申报的事件评测库/CLI范围组织工程交付，不以合成例、测试数或AI材料充当真实用户采用。

## 当前交付是什么

MoonBit核心把参考事件与预测事件按录制/类别隔离，采用精确十进制时间和最大基数一对一匹配，输出整体/分组指标、配对及未匹配明细、时间资格解释。支持自定义JSON、严格四列TSV导入、MoonBit公开API；不是检测模型、音视频播放器或完整sed_eval移植。

- 公开仓库：[z2823253773-p/mooneventeval](https://github.com/z2823253773-p/mooneventeval)
- 正式库：[z2823253773-p/mooneventeval@0.1.0](https://mooncakes.io/docs/z2823253773-p/mooneventeval@0.1.0)，安装`moon add z2823253773-p/mooneventeval@0.1.0`。
- 发布源码：[v0.1.0](https://github.com/z2823253773-p/mooneventeval/tree/v0.1.0)，304d59057；[P8真实发布/仓库外安装回执](delivery/MOONCAKES_RELEASE.md)包括43/43文件一致及API/CLI实际消费。P9补充示例与CI不覆盖这个已发布版本。
- 环境：macOS arm64 / Linux x86_64，native，锁定MoonBit v0.10.14+7d59c7ec9；[安装与完整调用代码](INSTALL.md)。库的评分运行不需要Python或sed_eval。

## 评委从哪里开始

在完整仓库根目录，先按README完成工具链安装和native构建：

```sh
python3 scripts/install_toolchain.py
scripts/with-toolchain.sh moon build cmd/mooneventeval --target native --release --deny-warn
_build/native/release/build/cmd/mooneventeval/mooneventeval.exe evaluate examples/duplicate.json --format json
python3 demo/public-data/reproduce.py --check --output /tmp/mooneventeval-final-public
```

工具链安装器拒绝覆盖已有安装，已安装时跳过第一行。输出目录需新建/为空；公开数据不联网、不下载音频。第一例为TP1/FP1/FN0；公开标注基线11/0/0，受控回归9/2/2。完整结果、原始来源和错误定位见[公开数据流程](../demo/public-data/README.md)。按[三分钟讲解](demo.md)可解释算法、时间边界、参考范围和工程取舍。

## 申报内容与可查交付

| 检查项 | 实现/使用入口 | 验证范围 |
| --- | --- | --- |
| MoonBit为主要实现 | eventeval时间/资格/构图/匹配/评测/报告，cli调度，cmd文件入口 | Python仅开发编排/验证；C stub仅native I/O |
| 公开持续开发 | 公开Git历史、README、CHANGELOG、CONTRIBUTING | 保留实质功能/修复/测试提交，不凑空提交；本期有效工作由赛方认定 |
| JSON/TSV接入与指标 | [API](API.md)、[TSV](TSV.md)、examples | 重复事件保留、重名键拒绝、整体/分组计数和空分母null |
| 场景及结果用途 | 三个[合成工作流程](../demo/workflows/README.md)与[公开标注流程](../demo/public-data/README.md) | 从材料到导入、报告、定位和后续人工核查；无真实模型成绩/外部采用声明 |
| 能安装、能调用 | 正式Mooncakes包、[独立MoonBit示例](../examples/moonbit-consumer/README.md) | 注册表精确版本下载、字节核对、API/错误/CLI实测见P8；源码消费者随当前门重跑 |
| 测试与CI | 自动[快速CI](https://github.com/z2823253773-p/mooneventeval/actions/workflows/smoke.yml)、手动[完整双平台CI](https://github.com/z2823253773-p/mooneventeval/actions/workflows/ci.yml) | 快速门8步无参考环境；完整门17步保留资格/参考/打包和历史校验，另回放公开数据 |
| 许可与来源 | [MIT](../LICENSE)、[第三方说明](../THIRD_PARTY_NOTICES.md)、[数据归属](../demo/public-data/NOTICE.md) | sed_eval规则参考与未移植范围明确；core保留许可/NOTICE；DESED标注按CC BY4.0归属 |
| 可解释与复现 | [演示提纲](demo.md)、源码/API、固定输入/输出和命令收据 | 讲解材料不冒充本人答辩经历，参赛者仍需能够说明自己的技术取舍 |

## 两种复验命令不能混用

快速产品门：

```sh
python3 scripts/smoke.py --output /tmp/mooneventeval-final-smoke
```

它检查格式、native编译/65项MoonBit测试、4项公开流程测试（含数据/结果/来源篡改和真实进程超时反例）、13条合成产品命令、6条公开数据命令与包外MoonBit消费者。它不运行sed_eval、不恢复旧历史，也不声称注册表安装或完整资格对照。

完整开发门（需要[贡献指南](../CONTRIBUTING.md)中的参考环境和原始历史还原）：

```sh
python3 scripts/verify.py --mode local --evidence /tmp/mooneventeval-final-full
python3 demo/reproduce.py --check --reference-python .venv-reference/bin/python --output /tmp/mooneventeval-final-demo
python3 demo/public-data/reproduce.py --check --output /tmp/mooneventeval-final-data
```

P9最终被测公开SHA为`de2c8e200cbb2e392f3368f262fda3e07ba70c53`，作者SHA为`173864bb285abad4a1e7bd3ee63d09a557a43f3f`。[完整双平台run43410461615](https://github.com/z2823253773-p/mooneventeval/actions/runs/43410461615)及[自动快速run43410412628](https://github.com/z2823253773-p/mooneventeval/actions/runs/43410412628)实际成功。每OS完整17步/65MoonBit/33根Python/42验证/19CLI，275源码hash绑定公开Git，另6条公开数据命令。唯一独立评审的1Important/1Minor经作者反例测试修复后，以最终SHA重跑全部门；无二次独立复审。`python3 evidence/P9/verify.py`可离线核对本轮归档。后续证据/链接收尾HEAD不冒称重跑完整CI。P8历史发布证据仍可运行`python3 evidence/P8/verify.py`离线核对。

## 已知边界

- 无通用CSV、无表头TSV、数字型JSON时间、stdin、Windows/WASM/JS兼容声明；不做IoU/mAP、分段指标和substitution错误率。
- 2,000参考+预测事件、8MiB输入、20M匹配工作步和16MiB输出等限额见README；复杂合法图也可能资源失败，不承诺所有输入运行时间。
- JSON/API可使用NUL标识符，但literal OS argv无法携带NUL，CLI解释不能选中这种ID；T6历史超时记录仍有部分子进程流档案缺口。这些限制未隐瞒，也不冒称本轮修复。
- 公开参考标注来自DESED；两套预测均是受控构造。它证明接入和错误追溯，不代表真实模型评估结果或完整DCASE基准认证。

## 规则来源和外部状态

按[官方十一月官网源码9d9c17a](https://github.com/moonbitlang/Hackathon2026/blob/9d9c17a92d0b7e285f7ebb61df68f5c1849d732f/src/App.tsx)核对MoonBit实现、公开开发、可运行示例/测试、实质工作、开源来源及可解释性。该来源把具体日期交由官方通知确定；用户本轮未收到附加清单或日期，不套用旧十月截止或其他比赛的提交数量要求。正式章程及个案通知优先；不自动提交报名/验收表、不对官方结果作保证。
