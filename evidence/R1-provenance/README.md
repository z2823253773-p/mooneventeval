# R1 原始作者对象

冻结的 R1 验证器用原始作者代码 `69f544fd` 查询 Git blobs。远端原生提交图使用映射后的 `c1e74f58`；CI 的原始历史包只到 `4d5d3fbb`，不能单独提供后来新增的原始对象。

本目录的自包含 bundle 保留原始历史至 `69f544fd`，大小与 SHA256 记录在 lock.json。运行 `python3 evidence/R1-provenance/restore.py` 离线校验、导入独立证据 ref，再运行冻结的 R1 验证器。恢复不切换 HEAD、不使用 Git replace、不修改已冻结证据或产品代码。

这补充后续离线证据复核的运输能力，不改变已成功的双平台 CI 被测提交。bundle 含内部原始历史，仅随已授权私有仓库存放。
