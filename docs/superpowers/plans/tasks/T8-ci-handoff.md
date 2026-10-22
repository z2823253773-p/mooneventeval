# T8-ci-handoff 任务卡

状态：用户“继续”授权实施本地T8；统一验证器/手动CI已创建、初轮失败测试GREEN，完整本地总验证及整分支唯一评审待执行。先读AGENTS.md、docs/PROJECT_STATE.md、docs/contracts.md，再读本卡；必要时读PRD相关章节。

没有远端授权时只有配置及本地结果，Linux/远端CI明确未运行；不要把不可取得的运行列为本机已完成。

## Task 8: 统一检查、CI配置与最终可审阅交接

**Files:** 创建 `scripts/verify.py`、`tests/test_verify.py`、`.github/workflows/ci.yml`；完善 `docs/PROJECT_STATE.md`、`docs/ACCEPTANCE.md`、`docs/VALIDATION.md`；证据 `evidence/T8/`。

**Interfaces:**
- Consumes：T1–T7所有已通过阶段、工具链锁与reference.lock。
- Produces：`python3 scripts/verify.py --mode local --evidence <dir>`（本地真实检查）；CI调用同一脚本，OS/arch必须实测；最终交接包含当前分支/SHA、证据范围、未完成事项。
- verify.py以当前工作目录为项目根，首先要求该目录有本项目manifest；不因脚本路径位于另一份仓库就静默改测另一份代码。

- [ ] **1. 写检查器失败测试/故障注入。** 在tests/test_verify.py验证缺少实际binary、子命令非0、缺参考环境、改动工具链哈希、归档缺LICENSE任一情况必须非0，不能生成总通过；运行 `python3 -m unittest discover -s tests -p test_verify.py -v` 确认RED再实现检查器。可在临时复制品注入，不改已验证基线；证据解析不能把“未运行/跳过”当成功。

```python
def test_missing_project_never_passes(self):
    repo = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory() as directory:
        run = subprocess.run([sys.executable, str(repo / "scripts/verify.py"), "--mode", "local", "--evidence", str(Path(directory) / "proof")], cwd=directory, capture_output=True)
        self.assertNotEqual(run.returncode, 0)
```
- [ ] **2. 实现统一检查。** 记录 `moon version --all`；检查格式和生成接口不产生未提交diff；native check/test及release build；真实CLI测试、独立对照、消费者和包内容检查；各子进程保留退出码和日志，全部通过才完成本地总表。先按最终代码SHA验证，后续文档提交与被测SHA分别记账。
- [ ] **3. 写固定版本CI。** 保存macOS arm64与Linux x86_64矩阵配置，安装校验同一固定工具链/core，Python参考环境从同一哈希锁同步；CI调用verify而非另写缩减测试。第三方Actions固定提交SHA后使用，权限contents:read；没有远端授权时仅保存配置和本地检查，状态为“远端未运行”。绝不配置自动发包、自动改报名或密钥输出。
- [ ] **4. 完成分支级独立复核。** 按用户选择的执行方式进行：Native由当前实施者顺序完成后请一名fresh reviewer在可用的最强模型上审整条分支；Subagent-driven按任务独立审阅后仍做整分支审阅。复核重点为最大匹配完备性、预算传播、输入精度/Unicode、解释与全局projection、native借用生命周期、包外契约；有问题修复并重跑受影响检查，不能把审阅意见当测试结果。
- [ ] **5. 运行最终验证并交接。** 先提交已完成的产品/检查器/CI配置为 `ci: verify the event evaluation delivery candidate`，核对代码工作树干净并记录被测SHA；再运行 `python3 scripts/verify.py --mode local --evidence evidence/T8/local`，核对归档hash及每个A项证据。本轮新增证据文档可随后提交，但不能因此把后来HEAD说成已经实测的代码SHA。授权后如有远端CI，再记录确切run URL/被测SHA/OS结果；未授权则明列远端CI、正式包、报名未完成。
- [ ] **6. 保存并提交交付证据。** 提交 `docs: record event evaluation candidate acceptance evidence`，最终核对干净工作树，区分被测代码SHA与此文档HEAD；交付本地可运行结果及事实清单。公开选题差异说明须更新为真实已实现范围；正式申报由用户本人基于确认事实撰写。按finishing-a-development-branch流程处理分支，不自动推送、合并或发布。
