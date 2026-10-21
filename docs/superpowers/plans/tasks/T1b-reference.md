# T1b 原版参考环境（独立任务卡，已授权并验收PASS）

**Goal:** 在项目局部Python环境运行固定sed_eval，保留真实raw/class_wise/projected/definition_flags，不修改参考算法。

**Files:** `validation/bootstrap_reference.py`、`reference-requirements.in`、`reference-constraints.txt`、`reference.lock`、`sed_reference.py`、`validation/tests/test_reference.py`；证据 `evidence/T1b/`。

**Interfaces:** `sed_reference.evaluate_document(document: dict) -> dict`；T3/T6消费raw、class_wise、projected、metric_definition_flags。输入是同一合成任务；不从产品输出生成参考期望。

预算：从开始安装/排障计总墙钟3小时。一个Codex实施者可先做T1，或在安装等待时做不冲突的只读工作；不要求额外模型或Claude长期在线。T1b未完成不抹去纯核心证据，也不能自动解除最终A11要求。

- [x] 1. 使用项目局部uv Python3.11.14及独立venv，从提交0cb1b6d11ceec4fe500cc9b31079c9d8666ed6eb取得sed_eval，记录来源、归档与源码hash；不向agent-reach环境安装。
- [x] 2. 写reference self-check：重复预测raw Ntp=1/Nsys=2/Nref=1；A2 optimal预期TP=2；跨标签例记录raw substitution与共同口径差异。先跑失败，不能只导入成功就说对照成功。
- [x] 3. 首轮约束numpy<2、dcase_util==0.2.20；若实际是旧别名兼容问题，第二个全新环境试numpy==1.23.5并保留第一轮失败。三小时内可定位其他问题但不得patch参考算法制造通过。
- [x] 4. 成功后从固定归档URL和依赖生成含hash的完整lock，再从lock重建并重复self-check；保留原始数据，NaN等原始值用明确标记序列化，不改成0。投影不冒充原始全局FP/FN。
- [x] 5. 运行 `.venv-reference/bin/python -m unittest discover -s validation/tests -p test_reference.py -v`；保存命令/退出码/版本与raw结果，再交T3。
- [x] 6. 到3小时未通即停止排障并登记A11未完成，输出已排除原因/最小失败/下一步。固定手工或公开样例可辅助核心验证，但不是sed_eval实跑替代品；完整交付降级或延期需明确决定。

本卡把环境工作从时间核心中拆开，并建议允许T3核心门槛先独立成立；该阶段顺序修订随v2计划待用户确认，最终验收项目没有被静默删除。

执行结果：docs/reviews/2026-10-20-t1b-results.md，证据evidence/T1b/manifest.json。备用NumPy1.23.5轮未触发；三小时失败止损未触发。原版拒绝零collar，产品零collar仍有效，详见contracts。
