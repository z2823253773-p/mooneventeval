# T7-package 任务卡

状态：用户“继续”授权本地T7；机器实现/初轮复验通过，准备唯一独立评审。先读AGENTS.md、docs/PROJECT_STATE.md、docs/contracts.md，再读本卡；必要时读PRD相关章节。

包内容/许可/包外消费者保留为最终交付检查，先让核心和demo可用，不声称评委看不到就无需检查。

## Task 7: 包外调用、可发布候选与可运行文档

**Files:** 创建/完善 T7 地图文件、`docs/PROJECT_STATE.md`、`docs/ACCEPTANCE.md`；证据 `evidence/T7/`。

**Interfaces:**
- Consumes：稳定public API、T6证据及可运行CLI。
- Produces：`scripts/check_consumer.py --source <module-root> --output <dir>`；`scripts/package_candidate.py --output <dir>`；README命令及API示例实际运行记录。脚本返回0只表示本地消费/候选检查成功，不表示注册表发布。

- [x] **1. 先写会失败的外部消费者。** 临时目录内独立moon.mod，path依赖指向待测模块；仅 import `local/mooneventeval/eventeval`，通过public工厂与evaluate构造A1并断言tp=1/fp=1/fn=0及报告可解析；缺API/字段或路径指回测试源码即失败。消费者自身不复制匹配/指标逻辑。

```moonbit
test "consumer_duplicate" {
  let r = @eventeval.event("r1", "alarm", "10", "12").unwrap()
  let p1 = @eventeval.event("p1", "alarm", "10", "12").unwrap()
  let p2 = @eventeval.event("p2", "alarm", "10.05", "12.05").unwrap()
  let rec = @eventeval.recording("clip-01", [r], [p1, p2]).unwrap()
  let input = @eventeval.task(["alarm"], [rec], @eventeval.default_config()).unwrap()
  let m = @eventeval.evaluate(input).unwrap().metrics()
  inspect((m.counts.tp, m.counts.fp, m.counts.fn_count), content="(1, 1, 0)")
}
```
- [x] **2. 实现候选打包及消费脚本。** 使用 `moon package --list --frozen` 和实际归档；解包到新的临时目录再运行包外消费者，避免只测工作树。`.moonignore` 明确保留core/cli/native stub、README、LICENSE、NOTICE和必要API/案例；排除探针、虚拟环境、工具链、构建产物、原始日志、内部咨询/计划。逐项核对归档实际文件及README链接；下载/发包不在此步骤。
- [x] **3. 补齐文档与许可。** 自有实现建议MIT，新增LICENSE/署名以确认的仓库作者信息为准；引入代码/数据逐项保留许可。README写实际工具链、安装/编译/两命令/空值/限制，EXAMPLES写三项任务的完整输入-操作-输出-解释；VALIDATION说明projection/浮点/空集边界及复现命令。未有真实反馈就只写开发者复现，未测后端不宣称支持。
- [x] **4. 核对待公开身份。** 本地 `local/mooneventeval` 是开发名。无远端/namespace授权时，记录正式仓库URL和包名未完成，候选标为本地；不填虚构URL。收到具体授权后才替换namespace/URL，并重跑包外消费/包内容/链接检查；不能把原namespace候选当新包实测结果。
- [x] **5. 运行 GREEN。** `python3 scripts/check_consumer.py --source . --output evidence/T7/consumer`；`python3 scripts/package_candidate.py --output evidence/T7/package`；实际运行README三案例及explain命令。归档清单、SHA-256、API快照、消费者输入输出/退出码分开保存。
- [ ] **6. 保存并提交。** 提交 `docs: document runnable event evaluation and package contracts`；打包策略/消费者可单独成实质提交。更新ACCEPTANCE每项A1–A12的证据链接，未满足项明确列出，不以本地打包替代Mooncakes发布。

兼容性裁定：现代moon.mod以import声明模块，临时moon.work的两个本地成员替代旧JSON path-deps；锁定工具实跑。完整初轮结果见docs/reviews/2026-10-22-t7-results.md（仓库根相对路径）。步骤勾选仅本地候选范围，无发布/正式namespace声明。
