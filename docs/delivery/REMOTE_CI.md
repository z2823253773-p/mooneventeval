# 授权后的私有远端验收

用户“授权”确认：在z2823253773-p/mooneventeval创建私有仓库、推送代码/测试证据/真实历史并运行双平台CI及处理失败。仓库已创建，API确认private=true；未改为公开、发包、改报名或联系他人。

原工作树/分支不改写。GitHub普通Git拒绝超过100MiB的blob；原T7评审原始diff日志为150195290字节，直接推送不可行。使用独立GitHub导出副本，只从其原生提交树移除该大日志并保留提交作者/日期/说明，记录原始→导出SHA映射。原始完整Git历史作为约23MiB的bundle原样附带；原始SHA和150MiB级日志在CI前按hash恢复。这个载体变化不等于原始GitHub提交图字节不变，不降低历史证据核验。

[恢复说明](../../.ci/README.md) / [原始历史锁](../../.ci/history.json)。新的恢复器五个真实Git fixture用例先RED再GREEN；原始目录本地恢复和T7 freeze复核结果另存evidence/R1。CI仍调用完整verify.py；源码SHA记录实际导出/dispatch提交，而历史freeze仍验证原始被测SHA。

此页创建时远端尚未push/dispatch/通过。后续须保存repo/private/default-branch、源/导出SHA映射、实际run URL、每个OS/架构的日志和结论；失败修复后重新运行，不能把创建配置或本机通过写成远端通过。

推送副本首轮总门在15步之后被历史T7核验正确阻断：两份原始评审binary被.gitignore排除，只有本机文件，未进入Git。按原始独立评审manifest验证两文件共1054216字节的hash后明确加入当前证据提交，旧manifest和原始历史不改写。未采用新增supplemental-ref机制，探索反例日志保留但不作最终通过证据。

唯一独立R1复核候选07906089发现1 Important：已有文件只与可变metadata比hash，未与bundle内原始Git blob比较。真实反例RED后，作者补上existing-file的Git对象一致检查；当前6项恢复器/总28项Python通过。没有第二次独立复审；历史图映射、完整门、远端及后续修复仍须作者实际验证。
