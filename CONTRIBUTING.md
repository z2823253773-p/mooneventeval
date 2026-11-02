# 参与开发

MoonEventEval 的目标是 MoonBit 内可调用、可解释的事件级评测。产品数学规则、时间计算、匹配和报告在 `eventeval/`；`cli/` 与 `cmd/mooneventeval/` 提供原生文件命令；Python 仅作开发验证。先看 [README](README.md)、[公开 API](docs/API.md) 和 [参考范围](THIRD_PARTY_NOTICES.md)。

## 本地开始

使用分支或隔离工作树；不要直接覆盖他人的未提交改动。按 README 安装项目锁定工具链，不以全局最新版替换。完整仓库可先运行：

```sh
scripts/with-toolchain.sh moon test --target native --deny-warn
scripts/with-toolchain.sh moon -C examples/moonbit-consumer run main --target native --release --deny-warn
python3 -m unittest discover -s tests -p test_library_example.py -v
```

第二条是独立 MoonBit 模块的接入演示，三条 JSON 的含义见[示例说明](examples/moonbit-consumer/README.md)。快速命令不替代完整交付验收。

完整验收需要锁定的原版参考环境；安装和哈希校验步骤见 [validation/README](validation/README.md) 与 CI 配置。先提交本轮源码/文档，再从仓库根目录运行：

```sh
python3 scripts/verify.py --mode local --evidence evidence/dev-local-001
python3 demo/reproduce.py --check --reference-python .venv-reference/bin/python --output evidence/dev-demo-001
```

输出目录必须全新；再次运行请换名，不能覆盖旧结果。统一验收拒绝未提交的源码/配置/文档，记录真实 Git SHA、工具链、退出码、报告和源码哈希。发布演示回放单独核对 13 条产品命令及 4 条锁定原版对照。CI 在维护者手动触发后运行 macOS arm64 / Linux x86_64；本地通过不代表 CI 已运行。

## 改动与记录

- 一个提交描述一项有意义的工作；说明问题、行为变化和已运行的验证。不要拆分空提交或机械改动凑数，不改写已公开历史。
- 数学/输入/错误/排序语义变化先明确修改 [contracts](docs/contracts.md)，说明兼容性影响；不能只更新 README。复现缺陷后增加能抓到它的行为测试，再修复。
- 同步 README、API、示例与 [CHANGELOG](CHANGELOG.md)。工作交接更新 [PROJECT_STATE](docs/PROJECT_STATE.md)，分清代码 SHA、实测 SHA、证据收尾 SHA；没有执行的检查不标通过。
- 测试日志放在证据目录。历史冻结证据不改写；新阶段另建目录。原始大日志不要直接加入提交，应保存可复核归档与哈希，并遵守 GitHub 文件大小限制。
- 评分改变需重跑对应独立 oracle、原版共同口径和变形验证；不能只比较快照。解释的 eligible 不等于选中，原版 raw 指标不等于共同投影，均需保留。

## 来源和许可

本仓库自有源码、文档与合成示例采用 [MIT](LICENSE)，分发时保留许可与版权。MoonBit core 的 Apache-2.0 许可/NOTICE 单独保留，不将依赖重标为 MIT。参考 sed_eval 的规则和开发对照范围见 [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES.md)。

引入第三方代码、数据或依赖前，核对来源、版本、许可和分发义务，并更新第三方说明；不提交凭证、个人联系方式、原始音视频或临床资料。不要将开发源码包、GitHub 提交、包外消费测试描述为已发布 Mooncakes 包。正式发布、报名表更改或对外联络由维护者另行决定。
