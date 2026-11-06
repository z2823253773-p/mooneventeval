# P8 正式注册表发布与安装验收

用户2026-11-06明确要求修复“local/mooneventeval尚未正式发布，无法安装”的验收退回项。本阶段包含正式公开发布；不代交表单、不声称组委会通过。

设计：首次正式版本 z2823253773-p/mooneventeval@0.1.0；保留现有评分/报告版本与native范围。替换当前源码、接口和消费者的模块导入；旧冻结证据和历史计划保留。Mooncakes账号先核为z2823253773-p。包沿用闭合白名单策略，MIT及第三方声明完整。发布前全门、双平台CI和独立审查；发布后无moon.work/源码路径的仓库外消费者执行moon add、公开API调用、CLI，并比对注册表文件与已审归档。发布凭据不提交。

文件：moon.mod、当前moon.pkg/mbti、tests/consumer及examples/moonbit-consumer、scripts/verify.py/check_consumer.py/package_candidate.py、README/API/CHANGELOG、docs/INSTALL.md、docs/PROJECT_STATE.md/contracts.md；本阶段证据evidence/P8。INSTALL文档进入源码包，包成员改为43。

1. [x] RED：独立临时模块安装精确正式版本应失败；保存真实输出。
2. [x] 正式身份与安装说明：所有当前导入迁移、生成接口；包审计脚本使用正式归档名；完整本地门通过。
3. [x] 独立审查并处置，推送公开仓库；完整macOS15/Linux CI通过并记录被测SHA。
4. [x] 只发布经验证的0.1.0归档；确认服务端成功，注册表外部消费者从网络安装，调用评测/解释/TSV/错误处理及native CLI；比对每个已安装文件。
5. [x] 更新实际发布回执、README安装入口和状态；公开标签绑定实际发布源码，保存可核对证据与复验脚本。

验收：不是改名或本地workspace消费；必须注册表真实安装成功。不用旧证据假装新版本；发布后版本不可覆盖，若修复需递增版本。源码包中README/API/INSTALL不虚报发布成功；发布事实以独立回执文档为准。

阶段记录：预检65 MoonBit / 29 Python及43成员解包消费通过；补充注册表程序先以本地依赖实编译通过。此本地预检不冒称注册表消费。下一步固定Git提交跑完整门。

完成记录：正式源码affd16839/公开304d59057，完整本地与CI42241701394双平台门通过；0C/0I/1M独立评审后，作者修正记录字段并实际跑通7条注册表命令。正式发布exit0/200OK，43/43文件安装匹配，v0.1.0绑定实际发布源码。收尾HEAD不冒称重跑CI，实际回执见delivery/MOONCAKES_RELEASE.md和evidence/P8。
