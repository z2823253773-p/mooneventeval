# P9 最终验收技术证据

2026-11-13，用户确认初审通过、未收到附加清单。正式核心0.1.0不变，本轮交付公开标注接入、自动快速CI和集中验收/讲解入口；没有代交最终表单或声称官方通过。

最终作者173864bb285abad4a1e7bd3ee63d09a557a43f3f，实际公开被测de2c8e200cbb2e392f3368f262fda3e07ba70c53。手动完整run43410461615两OS成功，自动快速run43410412628成功。每OS17门/65MoonBit/33Python/42验证/19CLI，1620资格验证调用、43文件包/解包，另13产品/4原版/6公开数据回放。快速门8步/65MoonBit/4workflow，不冒充参考或注册表验证。

```sh
python3 evidence/P9/verify.py
```

Python>=3.12、Git、完整克隆，无联网、编译或凭据需要。核对冻结hash、Git源码275成员、GitHub原始ZIP摘要、双平台/快速门、公开数据出处/许可与实际输出、本日真实注册表43文件/7命令安装。P8发布档案/已发布ZIP不修改。

- local.zip：首次候选、本地最终17门及全部回放、RED/GREEN、篡改拒绝、独立评审及原始实验、稀疏检出预检与本日注册表消费。预检/初候选和最终173源严格分开，不能拿旧候选结果代替最终SHA。
- ci-macos.zip/ci-linux.zip/ci-smoke.zip：由GitHub连接器取回的原始artifactZIP，逐项匹配API中的sha256 digest。GitHub artifact原有名称及ID记录在artifacts.json；不是重新压缩后假称原SHA。
- metadata.zip：CI后README/状态链接收尾的43文件源码包/解包复验，仅为文档候选，不覆盖已发布版本，不称新的完整CI。
- source-record.json：本实施者实际读取Zenodo API的CC BY4.0许可/作者/原始文件记录；公开Git中的SOURCE.json及gzip数据独立绑定。数据与衍生TSV/含标注输出保留CC BY4.0；代码MIT。预测是受控构造，不是真实模型输出，无音频。
- REVIEW.md：唯一独立评审632候选，0C/1I/1M；作者增加来源篡改与真实超时反例并修复，最终SHA本地/远端全门通过，无第二次独立复审。原评审SOURCE反例在最终代码下也被拒绝。
- bindings、run/jobs、repository、archives及SHA256SUMS明确身份与冻结边界。GitHub临时下载签名URL、发布凭据和个人联系方式不归档。

local包含真实非零RED和被篡改数据，包含旧候选可错误通过来源字段的评审反例；这些仅描述修复前，不是当前通过的交付结果。超时探针是开发编排器的真实睡眠进程测试，不冒充MoonBit评分测试。源表是公开数据接入证明，不是外部用户采用或完整DCASE成绩。

归档核对器首次假设连接器job对象含head_sha而失败；实际连接器给run_id。已按job.run_id绑定已确认head_sha的真实run，再同时核对原artifact digest、artifact workflow_run.head_sha及内部源清单，不用缺失字段猜测HEAD；原数据未改。

首次注册表安装日志显示Using cached，未当作冷下载证据。之后仅将本模块缓存保留并临时隔离，真实冷下载显示Downloading且43/43文件及7条命令通过，原缓存在finally恢复，见cache-isolation.json。local.zip逻辑registry前缀对应实际registry-cold运行，原始收据路径不改；第一次缓存安装保留在registry-cached中。
