# P7 TSV导入验收

2026-11-05。用户授权继续优化，本阶段完成MoonBit四列TSV转换、native import-tsv命令、行/侧/列错误、文档与42文件源码包。规范见[TSV](../../docs/TSV.md)。合成输入不作为真实数据采用证明，四列子集不代表DCASE完整协议。

原始初候选500b44a52，独立审查0 Critical / 0 Important / 1 Minor，见[原报告](independent-review/REVIEW.md)。唯一Minor为帮助仍把所有默认输出称为text，作者修正文案并实际运行。独立检查包括40随机双侧Unicode任务、10旧CLI对照、8MiB制表符与实际42成员包解包构建；无第二次独立复审。

最终实测原始c05cb165281777a86356fe86f4079f9ed72e6de5 / 公开5874d6514d4ef3c34292ecced56446ea02c764a8。[实际CI42176209407](https://github.com/z2823253773-p/mooneventeval/actions/runs/42176209407)的Mac15 arm64/Linux x86_64各17步通过：65 MoonBit、29根Python、42验证、19 CLI，1620资格验证调用、42成员打包/解包导入→评测、13产品+4原版回放。251源码hash相同并绑定公开Git，各8262基础产物及35演示文件保存核对。

原run42175638875的Mac14在分配runner前取消，annotation为configuration unsupported，原样保存在retired文件中。[官方退役说明](https://github.com/actions/runner-images/issues/13518)确认原镜像停止支持；作者迁移macos15，保持权限、action/toolchain锁及完整门。一项本地验证跨提交切换被commit一致性保护拒绝；最终固定提交重跑成功。均不把失败回执当通过。

CI后的README链接/当前状态/契约整理不是新一次全CI，42成员源码包另复验。

## 离线复核

完整Git克隆、Python>=3.12与Git，无需编译器/原版环境或网络：

```sh
python3 evidence/P7/verify.py
```

检查冻结文件和ZIP SHA/大小/路径/CRC、真实run/jobs、完整门/流/所有基础产物、13+4输出与二进制绑定、两平台源码库存及公开Git内容。显式失败检查不依赖assert。

- local.zip：初候选、帮助修订、迁移期间失败及最终固定提交的实际本地门；RED/GREEN/帮助/独立原报告与脚本/当时ledger。最终使用accepted-migrated；demo指最终帮助修订后回放，initial-demo为早期回放。
- remote.zip：成功新run的两平台原始下载产物。
- metadata.zip：README链接更新后的42成员源码包独立复验。

大小、成员与hash见archives.json；最终文件由SHA256SUMS.json冻结。日志保留生成路径，旧冻结阶段不修改。独立原脚本依赖其隔离源码/产物布局，不是用户命令。无包注册表发布、报名变更或真实用户采用声明。
