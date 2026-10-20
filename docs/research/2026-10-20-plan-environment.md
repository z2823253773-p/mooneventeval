# 实施计划的环境与来源核查

2026-10-20（America/Phoenix）。本轮只读检查，没有安装工具链/参考环境、搭建产品、运行产品测试或创建worktree。

## 已实际观察

- 本仓库开始时 `main@a9f5b8f7f1d7c2140b49ad14ceaf525da4566e93`，工作树干净，无AGENTS.md和产品文件。
- 当前默认 `moon 0.1.20260713 (75c7e1f)`、`moonc v0.10.4+2cc641edf`；本机core同版本。本轮未改动默认工具链。
- Apple clang 21.0.0，arm64-apple-darwin25.4.0；Node v24.15.0（计划不以其为产品依赖）；Python 3.12.13，当前python3来自agent-reach环境，因此执行阶段必须另建参考环境，禁止向该环境直接安装依赖。uv 0.11.14已存在。
- `moon help build/test/package/info/add`已读取：本地工具支持native/release、test文件路径/filter、package --list --frozen；add没有本地path选项，包外消费要在独立manifest写path依赖，不能编造 `moon add --path`。
- 本机core JSON源码确认后值覆盖和max_nesting_depth；其 `parse.mbt` SHA-256 为 `6ba22ceb31ebb792387d154217668dd61e97987b15ddb63e25378ca4d4c5e3a1`。但计划固定的是另一配套版本，T1仍须实测，不把旧源码检查冒充目标版本运行。

## 计划工具链来源与冻结方式

选择 `moonc v0.10.14+7d59c7ec9` 是为了使用已有可审计的固定发行路径；不是本轮探针已经通过，也不是“最新版本”推荐。

从本地 MoonTick 仓库只读查看 `.github/workflows/ci.yml`，其当前HEAD为 `b8923bc4ed22c87e99142ba893477182e1b4e203`；只参考工具链发行路径/哈希与借用I/O形式，没有复制旧项目业务代码或改动旧仓库。

| 内容 | 计划固定值 |
| --- | --- |
| 版本URL段 | `0.10.14%2B7d59c7ec9` |
| macOS arm64二进制 | `https://cli.moonbitlang.com/binaries/0.10.14%2B7d59c7ec9/moonbit-darwin-aarch64.tar.gz` |
| 二进制记录SHA-256 | `20967f9389ac54508899ee2fc051a3470d051452bac5818a9696ed4c144f3ec3` |
| Linux x86_64二进制 | `https://cli.moonbitlang.com/binaries/0.10.14%2B7d59c7ec9/moonbit-linux-x86_64.tar.gz` |
| 二进制记录SHA-256 | `9226694de9ff978db1ecf820b7710c4224e84ec7a76b19a222d96f0cd4e31b6a` |
| 配套core | `https://cli.moonbitlang.com/cores/core-0.10.14%2B7d59c7ec9.tar.gz` |
| core历史观察SHA-256 | `6f18b8fdea18f85e628a75e4a1bd3977c5a5c9c6a836fd8824192b0e6bd91b14` |

这些值本轮是从本地固定提交的CI文本读取，**未重新下载对应归档**；web工具也未取得二进制sidecar内容。不能说已重新核验官方当前分发物。

T1安装器必须在新目录下载，要求二进制实算hash、记录hash及官方`.sha256` sidecar三者一致；core实算hash与历史观察hash一致后仅标为“与记录一致”，不标官方签名验证。归档变化、sidecar不可核对、下载失败或编译器版本不符，均保留失败并停止；不改用latest、不覆盖旧默认环境。写入docs/toolchain.lock.json后，CI按相同hash校验，不能仅打印差异后继续。

安装前校验归档成员不越过目标目录。工具链只放worktree内`.tools/`，不得执行远程安装脚本；`with-toolchain.sh`仅为子进程设置标准MOON_HOME/PATH，记录moon/moonc/moonrun/core版本。二进制发行包执行位缺失时只给新安装目录内必要工具补执行位，不递归改变其他目录权限。

## 参考工具依赖的本轮证据

固定 [sed_eval setup.py](https://github.com/TUT-ARG/sed_eval/blob/0cb1b6d11ceec4fe500cc9b31079c9d8666ed6eb/setup.py)，blob `5efa4320e9b92bfdf64071145d8a5b502654f294`；[requirements.txt](https://github.com/TUT-ARG/sed_eval/blob/0cb1b6d11ceec4fe500cc9b31079c9d8666ed6eb/requirements.txt)，blob `8155fdb36963a65e260c6204bb7520fc05e6a772`，本轮均已实际读取。它们声明版本0.2.1，依赖numpy≥1.7.0、dcase_util≥0.2.4；未声明本计划Python版本的兼容保证。

因此T1是可失败的真实兼容门槛：项目局部Python3.11.14、独立venv，最多两次明确约束尝试；成功后锁住全部解析依赖及哈希并从锁重建。约束值是验证起点，不是已证明可用的环境。源码包从固定提交获取并记录归档/每文件哈希，下载来源与许可单独留存；reference.lock只用于开发验证。对照运行时直接核验原版源码与固定提交，任何patch都不能继续称原版。

本轮也核查了 [Python 3.11.14发布页](https://www.python.org/downloads/release/python-31114/)、[dcase_util 0.2.20的PyPI元数据](https://pypi.org/pypi/dcase_util/0.2.20/json)、[NumPy 1.23.5元数据](https://pypi.org/project/numpy/1.23.5/)。这些固定版本确实有发布记录；Python并非最新版，NumPy元数据列出Python3.11支持，但这不能证明整组依赖组合可运行。uv管理的解释器是单独来源，T1须记录实际下载来源/hash，而不称为Python官网的二进制安装器。

## 当前官方技术资料与适用边界

- [MoonBit package配置](https://docs.moonbitlang.com/en/latest/toolchain/moon/package.html)：native stub/目标设置。
- [MoonBit FFI](https://docs.moonbitlang.com/en/latest/language/ffi.html)：extern C与借用生命周期。
- [MoonBit module配置](https://docs.moonbitlang.com/en/latest/toolchain/moon/module.html)：本地path依赖、包内容过滤与目标元数据。
- [moon CLI命令](https://docs.moonbitlang.com/en/latest/toolchain/moon/commands.html)：命令语义。

这些在线页面是当前nightly文档，本轮已读取相关内容，不能自动当作固定0.10.14版本已支持。T1先用目标工具链确认manifest/解析/测试命令；若语法版本不同，只调整manifest/调用语法，不改变PRD业务语义，记录实际可运行形式后才继续。

赛事日期、换题计次和现行强制条款本轮没有重新调查；沿用 [PRD来源记录](2026-10-20-source-check.json) 的证据及缺口，不以技术资料补证赛事许可。
