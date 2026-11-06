# P7 TSV接入记录

基线原始e9165492c / 公开afcd62ec7。用户授权继续优化，先实现严格四列表头双文件导入，完整规则见docs/TSV.md；沿用隔离工作树和公开导出副本。

- 基线native62通过，旧CLI实际拒绝import-tsv，RED保留red.log（旧默认文本诊断导致部分JSON解析错误，另两项预期成功测试直接断言失败）。
- 实现MoonBit import_tsv、CLI新操作/可选prediction输入、只读双文件I/O；API共享既有精确工厂、排序、错误与JSON序列化。
- 修复测试发现的显式--format text未覆盖导入默认JSON的问题；native测试FailureKind改为模式匹配，修正测试8MiB构造的一字节计算，未改变产品限额。
- 当前native65、rootPython29、validation42、CLI19；42成员源码包、解包导入→评测和原13/4演示均通过本地完整门。
- 初候选500b44a52，独立评审0 Critical / 0 Important / 1 Minor，帮助尾段仍称全局默认text。作者修正文案并实际运行--help；无二次独立复审。评审另独立运行40随机双侧/Unicode输入、旧CLI10调用对照、8MiB制表符边界、42成员解包重建等。
- 最终原始实测c851db67c / 公开099bed0b5；双平台CI42175638875已触发，待产物核对。阶段发布仅GitHub普通提交，不发Mooncakes、不改报名表。

- GitHub退役macos14导致原run42175638875的Mac任务在分配runner前取消；重跑同标签仍取消，annotation为configuration unsupported。保留retired-run/jobs/annotations。迁移macos15，权限/action/toolchain固定项不变。
- 一次本地验证跨越了提交切换，保护检查正确因commit不一致拒绝通过（accepted-current）；作者在固定c05cb1652重跑accepted-migrated，完整17步成功，不将该失败记为产品缺陷或成功。
- 最终当前源码原始c05cb1652 / 公开5874d6514；新CI42176209407正在完整执行。

- 最终CI42176209407的Mac15arm64/Linux各完整17步成功，251源码hash与各8262基础产物已下载逐项复核，13/4演示输出不变。README链接更新后42成员包复验通过；后续元数据不冒称完整重跑。
