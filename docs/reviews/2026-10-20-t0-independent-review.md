# T0 fresh只读独立评审与处置

评审代理：gpt-6-astra，未继承主会话；只读候选`74dcbe0e7d56817de6cbf54074147112b90faadc`相对基线`8a3075521312c9bf9ad196309422adaa0c67fbd2`的diff、契约和真实证据。没有写入本工作树。

- 原始结论：PARTIAL。Critical无、Important一项、Minor无。技术探针成立，但保留wrapper在本地moon缺失而moonc存在时会执行全局moon。
- 独立核对：源码/日志SHA、真实ZIP CRC及成员内容均一致；在独立临时目录复跑已记录native二进制，退出7、stdout精确T0换行。兼容性结论与实际源代码/诊断相符。
- Important处置：先加真实shell回归，原wrapper执行全局标记而失败；修正为检查局部moon/moonc/moonrun/moonfmt完整，常用工具用绝对局部路径exec。修复提交`c491a4d28ce842b53a56657edd966632d61172d3`。
- RED：[回归失败](../../evidence/T0/20261020T163003162921Z-wrapper-fallback-red.log)；GREEN：[4/4完整Python测试](../../evidence/T0/20261020T163034050911Z-wrapper-fallback-green.log)；[真实局部版本](../../evidence/T0/20261020T163034944759Z-wrapper-real-version.log)；[修复后完整探针](../../evidence/T0/20261020T163251Z/results.json)。修复由主实施者验收，没有伪称第二轮独立PASS。
- Declined：core发布者真实性。裁决保留来源缺口，T0只声明与历史hash一致；成本是缺少发布者独立认证，不能升级来源声明。
- Declined：下载完整时序及全部网络退出码的独立观测。裁决回执仅是主实施者记录，保留首轮/续传超时日志与最终固定SHA；成本是不能声称独立网络时序审计。
- Declined：全量重新编译。裁决独立评审核对源码/日志并复跑native，主实施者已实际编译/测试；成本是评审证据不等于第二次完整构建。
- Declined：产品数学、完整I/O异常/部分写、Linux、sed_eval、包外消费、CI、发布。裁决归后续任务，本轮不作相应验收声明；成本是这些可行性/交付状态仍未知。
- 原始编译器日志自带尾随空格，完整范围git diff --check会报这些原始行；保留原始字节以维护哈希，源码/文档排除evidence后的空白检查通过。成本是查看原始日志diff时仍有空白提示。

主实施者结论：Important已修复并验证，T0整体PASS；后续任务与未测项保持未完成，不扩大授权范围。
