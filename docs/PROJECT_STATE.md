# MoonEventEval 当前状态

更新2026-10-22（America/Phoenix）。**T0–T8本地工程任务完成；PRD M2最小核心机器条件已完成；用户取消自行复测，技术验收由Codex负责。本人讲解无实际证据，外部理解要求另列。T8整分支唯一有效独立评审的1项Important已作者单轮RED→GREEN修复并通过最终总门，无第二次独立复审；1项新Minor和1项继承Minor延期。远端CI/Linux、新安装、正式发布与赛事资格未完成。**

## 当前入口与身份

[契约](contracts.md) → [有效计划v2](superpowers/plans/2026-10-20-mooneventeval-plan-v2.md) → [验收地图](ACCEPTANCE.md) → [T8结果](reviews/2026-10-22-t8-results.md) / [评审处置](reviews/2026-10-22-t8-review.md) → [最终交接](DELIVERY_HANDOFF.md) / [已实现选题事实](PROJECT_POSITIONING.md)。v1已作废。自动演示与外部本人部分见[T5卡](superpowers/plans/tasks/T5-cli-demo.md)与[demo稿](demo.md)。

- 工作树`/Users/henryz/Desktop/比赛/mooneventeval-t0`；分支`spike/t0-feasibility`，保留待用户后续决定。原main基线8a3075521312c9bf9ad196309422adaa0c67fbd2；无remote/merge/push/CI触发/发布/报名变更，无临床数据访问。
- T8最终代码/被测 **8aa37c5aa55821d40a527e42ee9bc47ffc32371f**；独立评审候选df2142688e991c244cae0a94623ccf8acf55f257。之后内部文档/证据提交与代码被测SHA分开，当前HEAD用git查询。
- 最终实际17/17：Moon58、Python22、validation42、CLI15，324bases+1296变形共1620产品调用；38文件真实源候选包、解包后consumer/native CLI及README六命令通过。源码193hash测试前后不变；后续文档按Git历史绑定。[总表](../evidence/T8/final-local/report.json) / [manifest](../evidence/T8/manifest.json)。
- 生产binary SHA256 `7a65bacefef1c3b70d4b851dc4fae1b337ce9114eea4addefddcf3be92f1940d`。T8历史候选archive SHA256 `9ac08e51914ef39a9ecafc51b1b9daabd1b47397701a33d65b67330235d43b31`，只限定本机Darwin arm64。local/mooneventeval@0.1.0不是注册表发布身份。

## 已完成及证据范围

T0工具链/版本语法实编译；T1精确十进制/Unicode/资格；T1b原版参考hash锁；T2显式栈first-free+DFS、753小图；T3封装输入/评测；T4同源解释/稳定报告/16MiB字节门；T5真实文件CLI与agent自动demo；T6限定对照/变形/预算/I/O注入/mutation；T7公开API包外消费及解包；T8当前cwd统一检查器、真实失败控制、未触发手动CI、整分支复核和交接。

T6参考324基础任务：155网格/160安全十进制/9边界。315共有口径一致；边界6一致/1具体binary64差异/2零collar原版域限制，未解释0。保留raw substitutions并显式projection；合成/固定seed范围，不认证任意真实数据普遍兼容。每base原版全局/逐录制/类实跑，四变形由独立有理数/图oracle核验；1620不是1620次原版对照。

[T6结果](reviews/2026-10-22-t6-results.md) / [评审](reviews/2026-10-22-t6-review.md)：代码/被测7b8a453f58307e4118eeae7ad78d79859af6eeed，2 Important作者修复；真实限额/9类I/O注入/6可编译mutation杀死，本机性能样本，无全部图/OS/竞态保证。[T7结果](reviews/2026-10-22-t7-results.md) / [评审](reviews/2026-10-22-t7-review.md)：代码/被测bb24ce33962ebf6276265075edb3df10e16e6601，1 Important作者修复。各历史manifest只对其历史SHA；不可按旧源码hash检验新文档。

T8复核原样9134文件；独立17步骤、额外48输入/281产品调用/7拒绝控制通过。I1缓存字节码绕过源码核验，作者已修复：身份与评分导入前都比较选中缓存与已hash源码新编译代码，两个入口真实RED→GREEN和原fixture作者重放均拒绝，最终总门GREEN。没有第二次独立复审。最强review席位额度失败后由可用gpt-6.1-sol xhigh替补，原失败未计为有效评审。

## 固定决定、延期与未完成

- 输入仅UTF8 JSON/字符串时间；重名及转义等价键last-wins。TSV/CSV、数字时间、sed_eval dict、stdin、新评分仍[BACKLOG](../BACKLOG.md)，未获范围修订。
- T8 M1延期：含NUL的合法ID可评测/API解释，CLI literal argv无法选中。T6 M1延期：超时正确非零，但部分stdout/stderr/process收据缺口。不称两者已修复。
- 机器输出单LF；I/O错误2、资源3、内部4；可能已输出前缀不等于完成。预算/large collar/等价匹配身份语义仍按契约，不保证所有合法图总能完成。
- [八例](validation/T3-worked-examples.md)和demo稿是agent材料，无本人讲解/外部反馈证据。历史“本人M2”混用作废：PRD M2是最小核心，已完成。用户于2026-10-22取消自行复测，不再列为工程阻塞。
- 手动CI保存Mac ARM/Linux x64矩阵及完整SHA action pins，调用同一verify；无远端执行或Linux资格化。正式作者/namespace/仓库URL/赛事资格仍待确认，不能编造。无自动发布、远端创建或报名授权。

## 复验与下一步

```sh
python3 evidence/T8/freeze.py
python3 scripts/verify.py --mode local --evidence evidence/local-delivery-recheck
```

总门须干净已提交根目录、新证据目录、现有锁定工具/档和参考venv，不自动下载/跳过。新复验认证当时HEAD，不改冻结T8。P1本地交付准备已完成，见[交付准备与下一阶段](delivery/READINESS.md)：19文件本地候选包、离线实录、复制/ZIP解出binary再运行通过；页面视觉核验受浏览器file协议限制未认证。下一步是授权后接入私有GitHub并实跑双平台CI；不要求用户自行复测。新输入格式仍需明确范围。后续Codex/Claude Code先读本文件、AGENTS、contracts与对应任务，核实际git状态，不重做已完成阶段。

## P1 代理交付准备完成

用户已取消自行复测。当前19文件交付ZIP见[交付准备](delivery/READINESS.md)；38文件源zip在f24e7e68重新打包/解包消费/native CLI及六示例验收通过，修正公开说明中M2的混用。完整17步仍绑定8aa37c5，当前新源包SHA256为`44c002bf3aecd3b8de6b7e4f7c65a7484fb3a14445c1b3adf68f77fec2e1a255`；程序binary/API与其一致未变。最终ZIP再解出运行三案例通过。页面结构/实际JSON检查通过，file协议内容观察被浏览器安全策略拒绝，视觉核验未完成，临时本机预览服务已关闭，不要求用户补测。

下一步可审阅的远端范围：账号z2823253773-p，拟私有仓库mooneventeval，推送代码/测试证据/真实Git历史并手动跑双平台CI；用户现已明确授权创建私有仓库、推送及运行CI；仓库已创建并确认私有，尚待推送/dispatch/实测结果。不自动改为公开、发包、改报名或发消息。

## R1 私有远端CI实施中

用户“授权”已覆盖目标z2823253773-p/mooneventeval的私有创建、代码/证据/历史推送及双平台CI；CLI账号与目标一致，API已确认仓库private=true。Git历史有150195290字节T7日志，超过GitHub普通Git单blob限制，采用独立导出图+完整原始历史bundle，按hash恢复原始对象和大日志再跑同一总门，本地原始历史不改写。见[远端验收记录](delivery/REMOTE_CI.md)。本地恢复器5项反例RED→GREEN及原始T7冻结复核；远端结果尚待发生。
