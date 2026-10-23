# 统一验证与证据边界

T8新增入口：从已提交、干净的项目根运行：

```sh
python3 scripts/verify.py --mode local --evidence evidence/T8/recheck
```

必须使用新目录；缺少项目、锁定工具链下载档/安装文件、原版参考环境均失败，不安装、不跳过、不把历史绿色日志当当前通过。实际构建后核对binary存在且可执行；每个子进程保存命令/cwd/退出/原始stdout和stderr及hash，完整17步骤和产物都通过才总通过。

工具链：下载档与锁/sidecar对照，已安装1384个常规文件逐一与档内bytes对照，不只看版本字符串。core仍是历史摘要，非发布者认证。参考：Python3.11.14、44个版本锁+固定sed_eval原始12文件校验，选中.pyc必须与已hash源码新编译代码相同且在导入前检查，身份探针使用同一门；Mac额外锁解释器hash；Linux解释器hash实际记录，不把Mac二进制hash当Linux认证。

测试协议要求非空Moon/unittest实际成功，拒绝跳过；源文件在interface生成前后/全程hash不变。全局报告绑定当前HEAD、完整源码hash、实际binary/候选zip、工具与参考身份。T6/T7冻结仅核验历史SHA，不能把它们说成当前代码重测。T6超时部分输出取证M1仍延期。

CI文件.github/workflows/ci.yml采用JSON形式的YAML子集以便标准库解析，手动workflow_dispatch、contents:read、checkout不保留凭据、第三方Actions固定完整40位SHA；Mac arm64/Linux x64矩阵先断言实际架构，使用同一verify，不发包、不改表单。官方来源锁在ci-actions.lock.json。当前只保存配置，远端/其他OS/新安装在执行前均未认证。

最终实测8aa37c5总17/17、Moon58/Python22/validation42/CLI15。整分支唯一评审候选df214268的缓存Important已作者RED→GREEN修复并通过总门，未第二次独立复审。收尾内部文档HEAD与被测SHA分别记账，见[T8结果](reviews/2026-10-22-t8-results.md)。PRD M2最小核心已完成；用户取消自行复测，由Codex负责技术验收。个人讲解、外部反馈和赛事资格不能由自动日志代替。

R1新增实际远端证据（2026-10-23）：私有仓库run39914869650的macOS14 arm64与Ubuntu24.04 x86_64各完整17步骤成功，新安装/构建/运行已完成。实际被测c1e74f58对应原始代码69f544fd，两个OS各58/28/42/15及1620调用、38文件包通过，产物下载hash复验。历史T8“未运行”仅限其阶段；当前见[REMOTE_CI](delivery/REMOTE_CI.md)。不把私有CI成功当公开、注册表发布或赛事接受。
