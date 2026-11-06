# P8 Mooncakes正式发布与注册表消费证据

发布版本z2823253773-p/mooneventeval@0.1.0，公开v0.1.0源码304d590574d7ca54fd5a8c9d2781d7823f8802c9（原作者affd168393780a9e8fc2fb757d156e0a6c6af938）。CI42241701394两OS成功，实际publish exit0/200OK。43/43下载文件与reviewed ZIP及公开Git逐字节一致；仓库外注册表消费7条命令成功。此证据不是组委会复审回执或外部采用。

离线复核（Python>=3.12、Git，完整公开克隆）：

```sh
python3 evidence/P8/verify.py
```

不编译、不联网、不发布、不需要凭据。绑定固定SHA与冻结哈希，不把后续README/状态收尾HEAD当成完整CI被测提交。

- release-0.1.0.zip是实际发布归档（43文件），服务器上传后与预审SHA相同；不能用后续文档打包覆盖它。
- local.zip保留真实RED安装失败、本地预检/完整17门、源码包/解包消费、13+4演示、文档生成和演练。moon doc --target native最初因命令不支持该参数失败，按help改用moon doc --frozen成功，原日志保留。演练实际exit255/服务端202（无变更）与正式exit0/200分开。
- remote.zip保留两个完整CI下载产物，包括各8262基础文件与35演示文件；流和索引逐项核对。
- registry.zip保留未登录客户端网络安装、3条API报告、TSV/重名键断言、下载包native CLI构建和3案例的实际日志/收据/构建产物；另附正式发布原始stdout/stderr、版本页HTML及客户端登录状态。发布凭据没有归档。
- REVIEW.md为唯一独立评审，0C/0I/1M；作者已把authenticated=False改为login_performed=False并实际跑通最终注册表门。没有第二次独立评审。验证程序自身哈希记录在registry报告中；该修订不是产品评分变更。
- archives.json记录ZIP哈希/大小/成员数，bindings.json明确原/公开SHA与计数，SHA256SUMS.json锁定外层文件。run/jobs/artifacts/repository及publish/registry-page为实际回执。

在线复验见根scripts/check_registry.py，需要网络和锁定工具链；使用新输出目录。当前主分支README可能含发布后的新链接，正式包对应v0.1.0，不以当前HEAD文档字节替代已发布版本。

metadata.zip另保留发布后README/链接更新的43成员打包/解包复验；这是后续文档候选，不覆盖已发布release-0.1.0.zip。registry.zip另保存实际消费检查器源码并绑定其自身SHA。归档核对器首次存在一条旧accepted-migrated路径，按实际ZIP的accepted路径修正后重跑；不修改产品与原始日志。

candidate.json保留发布前快照，actual_published=false只描述该捕获时刻；当前实际发布状态以publish.json、registry日志和verified.json为准。release-tag.txt来自匿名远端查询，精确标签解引用绑定304d59057。
