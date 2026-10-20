# T0 可行性探针（已执行并验收PASS）

问题：固定 `moonc v0.10.14+7d59c7ec9` 能否实际支撑本计划使用的字段、清单、断言、JSON深度、native借用I/O与打包命令？哪些需要改写，是否存在阻断核心的兼容问题？

范围：一次性探针，不是可保留产品代码。总墙钟预算2小时；单次网络请求设超时，安装重试累计最多30分钟；到点给出PASS/PARTIAL/BLOCKED及原始证据，不悄悄延长。用户于2026-10-20明确“开始执行”，本轮授权范围为T0。

**Inputs:** docs/contracts.md、docs/research/2026-10-20-plan-environment.md、实际git状态。现有默认0.10.4结果不得记成0.10.14结果。

**Files:** 执行后在隔离工作树创建 `spikes/T0/`（一次性输入）、`scripts/install_toolchain.py`、`scripts/with-toolchain.sh`、`docs/toolchain.lock.json`，证据 `evidence/T0/`。安装脚本若保留进入产品仓库，后续按工具脚本单独审阅；探针业务不直接转成产品。

## 步骤和成功/失败判据

- [x] 1. 核对基线/工作树；按适用技能创建隔离worktree，从固定历史发行路径校验并安装项目局部工具链。无法核实目标工具链则BLOCKED，保留网络/哈希/版本失败，不用默认版替代。
- [x] 2. 编译最小Counts：分别尝试旧 `fn` 字段与新 `fn_count`，同时验证JSON能保留键"fn"。记录真实诊断，不从文档关键字列表假造编译器输出。
- [x] 3. 同一个最小测试分别尝试 `inspect` 和 `inspect!`，启用deny-warn；记录目标版本实际接受的形式。计划卡片现用inspect，但在该步前不称已编译。
- [x] 4. 分别验证清单格式；产品和包外消费者统一用目标版通过的格式。优先moon.mod/moon.pkg，若目标版不支持则统一切换JSON清单并更新contracts/任务卡，不混用未经验证形式。无需为了格式单独写产品功能。
- [x] 5. 真正调用JSON parse深度参数；合法深度16成功、17资源错误；确认后值覆盖、严格UTF-8及代理项处理。普通JSON语法错误与资源错误分开。确认关键字参数实际语法后写回契约。
- [x] 6. 编译最小#borrow C stub，只做一次短文件读写及显式退出码，核对借用生命周期、Int32/ssize_t边界和输出；不实现完整文件库，不读取科研或临床目录。
- [x] 7. 实跑 `moon package --list --frozen` 与普通打包，核对实际产物路径。只产生本地测试包，不publish、不登录、不推送。把可运行命令与工具帮助说明分开记录。
- [x] 8. 形成不超过20行结论：每个probe的命令/退出码/日志、目标版本、通过/失败/未测、需要改的契约。技术事实与猜测分栏；结束更新STATE。
- [x] 9. 执行获批后安排一次fresh只读评审，只给契约、diff、探针实际输出，不给实施推理。清单/JSON/borrow有阻断或证据不足则不能标T0通过；可修正的语法差异先改文档再交接T1。

运行日志使用项目capture工具保存，不把整段编译器输出塞回主chat。技术结果与失败记录见docs/reviews/2026-10-20-t0-results.md及evidence/T0；第9步fresh评审发现1项Important，修复后回归和完整探针通过；详见docs/reviews/2026-10-20-t0-independent-review.md。
