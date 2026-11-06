# 在自己的 MoonBit 程序中使用 MoonEventEval

这是一个独立模块，通过公开的 `z2823253773-p/mooneventeval/eventeval` 接口使用本地源码，未复制评分实现。事件均为合成数据；示例适合学习接口和作为接入起点，不代表真实数据集试用。

## 运行

在完整仓库根目录执行。若尚未安装项目工具链，先按根 README 运行 `python3 scripts/install_toolchain.py`；Python 仅用于安装/开发验证，编译出的示例不使用 Python 或 sed_eval 评分。

```sh
scripts/with-toolchain.sh moon -C examples/moonbit-consumer run main --target native --release --deny-warn
```

`moon.work` 以相对路径同时引用本示例和两层目录之上的评测库，不需要更改绝对路径、全局安装或从注册表下载本库。此仓库内示例用workspace解析源码，正式依赖为 `z2823253773-p/mooneventeval@0.1.0`；不依赖workspace的注册表安装见 [安装指南](../../docs/INSTALL.md)。

命令成功退出时，stdout 依次输出三条单行 JSON：

| 行 | 结果 | 如何使用 |
|---|---|---|
| 1 | completed 评测；TP=1、FP=1、FN=0，选中 r1/p1，p2 未匹配 | 查看 summary、matches 和 false_positives，定位重复预测 |
| 2 | completed 解释；r1/p2 的 eligible=true | 判断两事件是否满足起止点容差；它仍未被第一行的匹配选中 |
| 3 | failed 输入；INVALID_TYPE，路径 recordings[0].reference[0].onset_s | 定位数字时间，修成字符串后重新验证；失败没有分数 |

第三行是示例**预期捕获的错误**，所以示例进程成功退出；它不是文件 CLI 的失败退出协议。真实文件 CLI 的输入失败仍为 exit 2。本示例输出是三条独立 JSON，不是单个 CLI 报告。

## 改成自己的程序

- 在 `main/main.mbt` 中用 `event`、`recording`、`task` 工厂构造数据；起止秒值传入字符串，最多六位小数。
- 若已取得 UTF-8 JSON 字节，改用 `decode_task` 得到相同的 Task，然后调用 `evaluate`。
- 对每个 `Result` 显式处理 `Ok`/`Err`。示例的 `checked` 在意外失败时停止演示并保留结构化错误；接入服务时应把错误返回调用者，再由应用决定退出、提示或重试。
- `report_json`/`report_text` 输出评测；`explain_pair` 及相应 renderer 输出资格解释。解释不执行最大匹配，不证明已选中。
- 移到自己的目录时，调整 `moon.work` 的两个 members；模块与包配置可直接参考本目录文件，路径依赖仍需指向实际库源码。

本目录仅随完整 Git 仓库提供，不在 43 文件源码包内。配置和代码遵循仓库 [MIT](../../LICENSE)，依赖声明见 [第三方说明](../../THIRD_PARTY_NOTICES.md)。完整接口见 [API](../../docs/API.md)；所有输入、评分与资源限制仍适用。
