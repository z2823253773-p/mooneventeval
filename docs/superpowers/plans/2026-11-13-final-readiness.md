# P9 最终验收准备

用户2026-11-13确认初审通过，要求自主完善至可提交最终验收；没有另发清单/截止/视频要求。继续使用现有隔离工作树spike/t0-feasibility，主实施串行，最终一次独立只读评审。已授权的普通推送与CI继续适用；不提交赛事表单、不发外部消息。

## 设计与范围

保留正式Mooncakes z2823253773-p/mooneventeval@0.1.0、已发布43成员ZIP和产品评分/API/CLI语义。本轮新增仓库级公开数据流程、自动快速CI和当前验收入口。选择补齐真实接入与维护能力；不扩大评分模式，不加入未申报的Web/Windows或模型训练，不靠堆测试数代替可用性。旧P3–P8冻结证据原样保留。

公开数据使用turpaultn/DESED固定提交0686178dd218b431ef1606e5a2139df7c543b07b的data/real/metadata/eval/public.tsv，归属DESED_public_eval，DOI10.5281/zenodo.3588172。Zenodo API标注cc-by-4.0，保留作者、原始数据hash、固定URL、许可与修改说明；代码MIT不替代数据许可。不下载音频。压缩保存完整小型元数据，以无损前两录制抽样复现参考TSV；预测是受控构造，不能用作模型性能或外部采用证明。先下载核字节/边界，再固定预期。

现有baseline11参考/11预测均匹配。变体：第二条Speech起点+0.201秒（超过0.2），删除最后一条Dishes，再复制另一条Dishes。预期11/11事件、TP9/FP2/FN2；人工期望9/11 F1。分别解释时间越界和合格但未选中的重复事件。Python只作编排/抽样/核对，评分由现有MoonBit CLI执行。

快速CI独立工作流：push main、pull_request、workflow_dispatch，contents:read、固定SHA动作、Ubuntu24.04、无参考环境/历史证据还原，实际运行格式/编译/65 MoonBit/发布示例/公开数据/包外API消费者。现有手动双平台17步完整CI保留，追加公开数据回放，不缩减原门槛。初审状态写为用户提供的事实，不等同最终通过。

## 文件地图

- demo/public-data/{SOURCE.json,NOTICE.md,reference.tsv,prediction-baseline.tsv,prediction-regressed.tsv,source/public-eval.tsv.gz,reproduce.py,README.md,output/*}：来源、抽样、运行、实际成品与错误定位。
- tests/test_public_workflow.py：真实端到端工作流，以及输入/输出被篡改必须非零；先RED后实现。
- scripts/smoke.py、.github/workflows/smoke.yml：独立快速CI执行器与受限触发。完整ci.yml只追加公开数据回放。
- docs/FINAL_ACCEPTANCE.md、docs/ACCEPTANCE.md、docs/PROJECT_STATE.md、README、demo/workflows/README、THIRD_PARTY_NOTICES、BACKLOG：当前入口与旧状态纠正，避免历史文档成为当前事实。
- docs/demo.md：三分钟命令演示、匹配图和技术取舍，代理编写的准备材料，不冒称本人答辩实录。
- evidence/P9：本轮本地/评审/远端证据及冻结核对器，不改旧阶段档案。

## 执行与验收

1. [x] 下载原始元数据，保存许可/作者/固定版本，建立无损抽样与受控预测；对新流程写RED实际测试。
2. [x] 实现公开数据6命令回放、固定成品和错误分析；正例、输入篡改和快照篡改均实跑。
3. [ ] 增加快速CI和现有完整CI中的公开数据回放；本地快速门通过。
4. [ ] 当前验收矩阵、安装/示例入口、来源说明、讲解材料补齐；记录初审已过但最终未验收。
5. [ ] 源码提交后完整本地17步与回放通过；唯一独立评审并处理Critical/Important。
6. [ ] 等价导出、推送、自动快速CI与手动双平台完整CI成功；下载产物绑定被测SHA、数据来源和输出。
7. [ ] 冻结可离线核对证据、当前验收状态及交接；不将收尾文档HEAD冒称重新跑完整CI。

## 记录

- 基线原始226688abf / 公开738e462fa；工作树均干净，P8冻结校验通过。现有产品未发现新故障。
- 官网源码9d9c17a92d0b7e285f7ebb61df68f5c1849d732f为十一月赛，日期以官方通知为准；本项目用户未收到附加要求。只据已读官方公开基线做工程核对，不套用其他赛事的100提交要求。
- Ruling: 用户既有“全程交给你、不自行验证”与本次直接开发请求覆盖例行方案选择和可逆实施，不另重复请求设计批准。费用/外发/报名仍不扩权。

预检记录：实际公开流程6命令11/0/0→9/2/2通过；测试输入/快照篡改被拒绝。发现新编排器只在成功时更新command-count，导致失败回执把已执行4次记成0；新增断言RED后修为逐命令持久化计数/收据。此缺陷限开发编排器，未改产品。快速门预检8步/65MoonBit/2workflow通过；完整最终SHA门仍待提交后执行。
