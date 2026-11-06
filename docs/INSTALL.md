# 从 Mooncakes 安装 MoonEventEval

正式模块：[`z2823253773-p/mooneventeval@0.1.0`](https://mooncakes.io/docs/z2823253773-p/mooneventeval@0.1.0)。公开 API 包：`z2823253773-p/mooneventeval/eventeval`。源码与 MIT 许可见 [仓库](https://github.com/z2823253773-p/mooneventeval) 和 [第三方声明](../THIRD_PARTY_NOTICES.md)。旧 `local/mooneventeval` 不是安装名。

## 环境

支持 native 目标，macOS arm64 / Linux x86_64，需要原生 C 编译器。开发锁定 MoonBit `v0.10.14+7d59c7ec9`；旧于此版本的工具链不在本版本验证范围内。安装 MoonBit 见 [官方说明](https://www.moonbitlang.com/download/)。不要求 Python、sed_eval 或参考环境来调用评测库。

若使用本仓库锁定工具链，先在仓库根目录运行 `python3 scripts/install_toolchain.py`，下文所有 `moon` 命令可改用仓库的绝对路径 `/path/to/mooneventeval/scripts/with-toolchain.sh moon`。包装器仅提供编译器，不提供源码路径依赖。

## 独立项目：网络安装并调用公开 API

在仓库外新建目录，里面不要创建 `moon.work`。创建 `moon.mod`：

```text
name = "example/eventeval_consumer"
version = "0.0.0"
preferred_target = "native"
```

然后执行（无需登录或克隆本库）：

```sh
moon add z2823253773-p/mooneventeval@0.1.0
mkdir -p main
```

创建 `main/moon.pkg`：

```text
import {
  "z2823253773-p/mooneventeval/eventeval",
}
pkgtype(kind: "executable")
```

创建 `main/main.mbt`：

```moonbit
///|
fn main raise {
  let r = @eventeval.event("r1", "alarm", "10", "12").unwrap()
  let p1 = @eventeval.event("p1", "alarm", "10", "12").unwrap()
  let p2 = @eventeval.event("p2", "alarm", "10.05", "12.05").unwrap()
  let rec = @eventeval.recording("clip-01", [r], [p1, p2]).unwrap()
  let input = @eventeval.task(["alarm"], [rec], @eventeval.default_config()).unwrap()
  let evaluation = @eventeval.evaluate(input).unwrap()
  let counts = evaluation.metrics().counts
  assert_true(counts.tp == 1 && counts.fp == 1 && counts.fn_count == 0)
  println(@eventeval.report_json(evaluation).unwrap())
}
```

```sh
moon run main --target native --release --deny-warn
```

输出一份 JSON 评测报告，`status` 为 `completed`，summary 的 reference/prediction/tp/fp/fn 为 **1/2/1/1/0**；`p1` 被匹配，`p2` 为重复预测。这里 unwrap 的输入是已知合法的合成例子；业务代码应处理 Result，见 [API](API.md) 和 [完整错误处理示例](https://github.com/z2823253773-p/mooneventeval/tree/main/examples/moonbit-consumer)。

## 命令行程序

上面的 `moon add` 安装的是依赖源码，不会向系统 PATH 添加 `mooneventeval` 命令。使用 CLI 可克隆公开仓库，按 [README](../README.md) 的锁定工具链命令构建 `cmd/mooneventeval`；不需要参考环境。已有 TSV 可按 [TSV说明](TSV.md) 完成 import-tsv → evaluate → explain-pair。

本版本不声明 Windows、WASM 或 JS 兼容，不包含检测模型和媒体解码。匹配、误差解释、时间/事件/资源限制见 [API](API.md) 与 README。正式发布回执和仓库外安装实测记录在 [发布验收记录](https://github.com/z2823253773-p/mooneventeval/blob/main/docs/delivery/MOONCAKES_RELEASE.md)；包已发布不代表组委会已重新验收。
