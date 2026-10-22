# T5-cli-demo 任务卡

状态：本机CLI/自动demo完成；最终被测2c0a06d，唯一Important作者单轮修复，无二次评审。步骤7本人讲解仍未完成，不能称整个个人验收通过。先读AGENTS.md、docs/PROJECT_STATE.md、docs/contracts.md，再读本卡；必要时读PRD相关章节。

demo在CLI任务中交付；当前输入仍JSON。安全边界不删除，较重故障注入可后移但不能称已通过。

## Task 5: 最薄native CLI、真实失败与三分钟演示

**Files:** 创建 T5 地图文件与 `cli/args_test.mbt`、`tests/cli/test_cli.py`、`docs/demo.md`；证据 `evidence/T5/`。

**Interfaces:**
- Consumes：T3/T4 全部 public API 和 EvalError。
- Produces（cli public）：`parse_args(args: Array[String]) -> Result[CliRequest, ArgFailure]`；`run(request: CliRequest, input: Result[Bytes, EvalError]) -> CliOutput`；`render_arg_failure(error: ArgFailure) -> CliOutput`。
- `CliRequest`：`operation: Operation`（Evaluate(path)/ExplainPair(path,recording,reference,prediction)/Help/Version）、`format: OutputFormat`（Text/Json）。`ArgFailure` 携带输出格式与 EvalError。`CliOutput`：`stdout/stderr: Bytes`、`exit_code: Int`。
- Produces（入口包内）：`read_file_bounded(path: String) -> Result[Bytes, EvalError]`；`write_all(fd: Int, bytes: Bytes) -> Result[Unit, EvalError]`。C `mee_open_readonly(path)->Int32`、`mee_read(fd,buffer,count)->Int32`、`mee_close(fd)->Int32`、`mee_write(fd,buffer,count)->Int32`；Bytes以#borrow传递，包装函数明确 ssize_t→Int32 范围，不存借用指针，不包含业务规则。

- [x] **1. 写参数失败测试并运行 RED。** 评测与 explain-pair 的精确命令、默认text、--format json、缺文件/缺ID/未知及重复选项、未知命令；Help/Version只允许单独调用且不读文件。合法 `--format json` 出现时即使其他参数错误也返回JSON；format本身非法或重复时返回text诊断。命令在首位、文件在第二位、选项在其后，不引入未定义的环境默认值。运行 `scripts/with-toolchain.sh moon test cli --target native`。
- [x] **2. 写真实进程失败测试。** Python `unittest` 用 `MEE_BIN` 指向 release exe；A1结果与退出0；零分/不合格解释仍退出0；坏schema/未知ID/不可读文件=2；8 MiB等号（合法JSON加空白）成功，超1=3；深度17=3；JSON错误仅failed，无summary/matches/NaN。测试调用exe而非把moon run的状态当产品退出码。

```python
def test_duplicate_real_process(self):
    run = subprocess.run([os.environ["MEE_BIN"], "evaluate", "examples/duplicate.json", "--format", "json"], capture_output=True, text=True)
    self.assertEqual(run.returncode, 0, run.stderr)
    counts = json.loads(run.stdout)["summary"]["counts"]
    self.assertEqual((counts["tp"], counts["fp"], counts["fn"]), (1, 1, 0))
```
- [x] **3. 实现参数/调度和有界 native I/O。** CLI库决定输出/退出码；入口读取 argv、只读 open、每次最多65536字节且全程最多8 MiB+1，关闭所有已开描述符。拒绝NUL路径及非普通文件；open先用非阻塞方式避免FIFO挂起，fstat后拒绝设备/目录/FIFO；允许读取普通文件符号链接。C包装处理EINTR/短读，MoonBit驱动聚合；输出预检后写入，底层短写循环或明确内部/IO失败。日志不污染stdout，输入绝不覆盖。
- [x] **4. 验证 R5 和内部错误路径。** 第一轮保留NUL/不可读/大小限制/关闭文件/短写处理；完整EINTR/故障注入列入硬化验收，未测就明列缺口，不增加用户开关；真实缺文件/目录/FIFO/NUL（NUL用入口函数测试，OS argv无法携带）及断开输出管道有界终止。输出设备失败可能已写出前缀，不能承诺撤回；必须非零且不能记录completed证据。错误4仅用于非预期故障，不把普通文件错误改成4。
- [x] **5. 运行 GREEN。** `scripts/with-toolchain.sh moon test cli --target native --deny-warn`；`scripts/with-toolchain.sh moon build cmd/mooneventeval --target native --release --deny-warn`；`MEE_BIN=_build/native/release/build/cmd/mooneventeval/mooneventeval.exe python3 -m unittest discover -s tests/cli -v`。记录实际exe路径/哈希/命令，三份examples在text/json都能跑，explain-pair单独运行。
- [x] **6. 保存并提交。** 归档真实输入/输出/退出码与所有限额/失败记录；提交 `feat: expose event evaluation through a bounded native CLI`。CLI目标先声明已验证的本机OS，Linux支持等CI/实机证明后再写。


- [ ] **7. 录制可复现demo与讲解证据。** 按docs/demo.md跑duplicate、trap、boundary；解释为何sed_eval optimal预期也是TP2，以及优势针对朴素贪心而不是虚构超越成熟工具。保留实际命令/退出码/输出。本人讲解尚未发生时保持未完成；薄TSV仍在BACKLOG待批准，不偷加CSV。

机器实现与自动演示结果：docs/reviews/2026-10-22-t5-results.md。步骤7的可复跑脚本、图示与10次真实命令已交付；本人纸笔/口头讲解未发生，因此该框保持未选。重故障注入留T6但必须最终补证。
