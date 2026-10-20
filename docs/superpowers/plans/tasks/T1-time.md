# T1-time 任务卡

状态：已获用户授权并完成；fresh评审问题修复后主验收PASS。先读AGENTS.md、docs/PROJECT_STATE.md、docs/contracts.md，再读本卡；必要时读PRD相关章节。

T0必须先完成。T1只实现时间/候选；Python环境归T1b。

## Task 1: 纯MoonBit精确时间与候选判断

**Files:** 创建 `eventeval/model.mbt`、`errors.mbt`、`time.mbt`、`eligibility.mbt`、`moon.pkg`；测试 `eventeval/time_wbtest.mbt`、`eventeval/eligibility_wbtest.mbt`；证据 `evidence/T1/`。工具链和起步manifest来自T0实际通过的配置，参考环境文件归T1b。

**Interfaces:**
- Consumes：PRD 的十进制语法、范围、容差公式及固定 sed_eval 源码。
- Produces（public）：`event(id: String, label: String, onset_s: String, offset_s: String) -> Result[Event, EvalError]`；`config(collar_s: String, offset_ratio: String) -> Result[Config, EvalError]`；`default_config() -> Config`。
- Produces（包内）：`parse_time_us(text: String, path: String) -> Result[Int64, EvalError]`、`parse_ratio_ppm(text: String, path: String) -> Result[Int64, EvalError]`、`eligibility(reference: Event, prediction: Event, config: Config) -> PairBasis`、`compare_codepoints(a: String, b: String) -> Int`。
- Python参考接口不属于本任务；T1b独立提供，不能把其环境工作重新塞回时间核心。

- [x] **1. 核对T0证据。** 只复用实际通过探针的工具链和manifest，不在本任务重复安装。若版本/环境变化先重跑相关T0探针。
- [x] **2. 写失败测试。** `decimal_exact`：`"10.05" -> 10050000`、`"0.000001" -> 1`、`"2592000" -> 2592000000000`；`decimal_reject` 拒绝 `"01"`、`"1e-6"`、`" 1"`、`"-0"`、七位小数和超界；`ratio_bounds` 检查 0/1/超界及零 collar。

```moonbit
test "decimal_exact" {
  inspect(parse_time_us("10.05", "onset_s").unwrap() == 10_050_000L, content="true")
  inspect(parse_time_us("0.000001", "onset_s").unwrap() == 1L, content="true")
  inspect(parse_time_us("2592000", "offset_s").unwrap() == 2_592_000_000_000L, content="true")
}
```
- [x] **3. 写候选/字符失败测试。** A3、A4 等号及超 1 微秒；参考时长主导与固定 collar 主导；不相交短事件可合格；R1 比较 U+E000 与 U+10000（前者排前）；R3 用 r=[10,10.000003]、c=0、q=0.5，期望 scaled=1500000，终点偏差 1 微秒合格、2 微秒不合格。
- [x] **4. 运行 RED。** `scripts/with-toolchain.sh moon test eventeval --target native --filter '*decimal*'`，再运行候选/字符测试；期望因缺目标API或目标行为而失败，不能把工具链损坏、错误导入或缺依赖当作行为 RED。初始化 manifest 与测试导入属于本任务必需搭建，保留实际诊断。
- [x] **5. 实现上面签名及错误常量。** 有界逐字符十进制积累，范围验证先于乘法；比例与时间共用精确扫描而保留不同上限；不调用 Double.parse。所有事件/config 有效性由同一函数定义，标签条件不代替录制分组。码点比较不依赖未经证明的 String 默认比较。
- [x] **6. 将参考环境交给独立T1b。** 不在时间核心里安装Python依赖；T1b未完成不把本任务时间/候选测试说成原版对照。
- [x] **7. 验证 GREEN 与解析前提。** `scripts/with-toolchain.sh moon test eventeval --target native --deny-warn`。参考self-check属于T1b，不是本任务的GREEN条件。原型测试实际确认 core JSON 重名键后值覆盖、16 层深度参数生效、UTF-8 严格解码和孤立代理项行为；若标准解析器会保留孤立代理项，在业务字符串校验中拒绝，不换契约。
- [x] **8. 保存并提交。** `evidence/T1/manifest.json` 记录命令、退出码、版本、下载/源码哈希及失败；日志分开保留。提交 `feat: define exact event time and collar eligibility`；参考锁及其 self-check 可作为独立实质提交，不凑次数。本任务不宣称M2完成；核心/参考/外部审核各自记账。

实际结果：docs/reviews/2026-10-20-t1-results.md；独立评审及修复：docs/reviews/2026-10-20-t1-review.md。T1b仍未执行，本任务不宣称M2完成。
