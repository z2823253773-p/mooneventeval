# MoonEventEval 0.1.0 正式发布验收

2026-11-06（America/Phoenix）。本次整改针对“local/mooneventeval尚未正式发布，未满足公开发布及可安装使用要求”。这项技术缺口已用正式发布与注册表消费实测补齐；不代表组委会已经重新验收。

## 正式交付

- 模块：[`z2823253773-p/mooneventeval@0.1.0`](https://mooncakes.io/docs/z2823253773-p/mooneventeval@0.1.0)。公开API包：`z2823253773-p/mooneventeval/eventeval`；旧local身份仅是历史源码候选。
- 源码：[`v0.1.0`](https://github.com/z2823253773-p/mooneventeval/tree/v0.1.0)，精确提交 `304d590574d7ca54fd5a8c9d2781d7823f8802c9`，对应作者提交 `affd168393780a9e8fc2fb757d156e0a6c6af938`。后续证据/README/状态提交不重写这个标签或正式版本。
- 许可MIT，随包包含LICENSE、THIRD_PARTY_NOTICES及MoonBit core许可/NOTICE。43成员闭合白名单，无开发凭据、临床原始数据或个人联系方式。
- 正式发布 `moon publish --frozen` **exit 0 / Server status: 200 OK**；上传前后43成员与审核归档一致。归档SHA-256：`e34d6bd987e5f341c03b70a281ce29f93dc67c84302352dcf7de14c6e285784b`。临时发布凭据链接已移除，不写入版本控制。
- 精确版本页独立HTTP请求200，页面包含正式模块身份和版本。

## 安装和实际消费

```sh
moon add z2823253773-p/mooneventeval@0.1.0
```

配置、完整代码与预期输出见[安装指南](../INSTALL.md)。支持native的macOS arm64 / Linux x86_64，锁定编译器 `v0.10.14+7d59c7ec9`。调用库无需Python或sed_eval。moon add安装依赖源码，不向PATH安装可执行命令；CLI构建方式见安装指南。

在仓库外新建临时项目、无moon.work、无本地源码路径依赖，使用未登录的锁定客户端，真实输出 `Registry index updated successfully` 和 `Downloading z2823253773-p/mooneventeval@0.1.0`，exit0。下载所得 **43/43文件**与审核发布ZIP逐字节一致，ZIP成员又逐项绑定v0.1.0源码。

随后7条真实命令全部exit0：

1. 注册表精确版本安装。
2. 公开API评测/解释/Result处理：TP1/FP1/FN0、p1选中、p2为重复预测；p2资格解释为true，非法数字时间返回INVALID_TYPE，无部分评分。
3. TSV精确时间导入→公开API评测，TP1/FP1/FN0；同程序断言JSON重名键返回DUPLICATE_KEY。
4. 在实际下载的源码中构建native CLI，未从仓库复制产品实现。
5. 下载包内duplicate案例CLI，TP1/FP1/FN0。
6. 下载包内greedy-trap案例CLI，TP2/FP0/FN0。
7. 下载包内boundary案例CLI，TP1/FP0/FN0。

这些是开发者建立的注册表消费者验证，不是外部用户采用。可重新运行（需要网络和锁定工具链；使用新输出目录）：

```sh
python3 scripts/check_registry.py --archive evidence/P8/release-0.1.0.zip --output /tmp/mooneventeval-registry-recheck
```

## 发布前验证与评审

[CI42241701394](https://github.com/z2823253773-p/mooneventeval/actions/runs/42241701394)绑定正式源码提交304d59057，macOS15 arm64和Ubuntu24.04 x86_64均success。每平台完整17步：65 MoonBit / 29根Python / 42验证 / 19 CLI测试、1620资格验证产品调用、43文件打包/解包消费，以及13产品/4锁定原版演示回放。本地完整门同样通过。255源码哈希一致；远端原始产物下载后另作哈希核验。

发布前唯一独立评审0 Critical / 0 Important / 1 Minor；独立解包检查43成员和两段接入程序，均编译运行成功。Minor为验证工具硬编码authenticated=False，作者改为明确的login_performed=False并记录工具自身SHA；修订后真实注册表7命令全部通过，没有第二次独立评审。这个回执字段修订不在43文件产品包内，不改变已发布ZIP；后续收尾HEAD不冒称重新跑完整双平台CI。

发布演练保留了实际非零：客户端exit255，但服务端明确返回202 Accepted与“Dry run completed successfully. No changes were made.”；正式发布另一次exit0/200OK，不能混同。旧P6/P7及其他冻结证据不修改。

离线证据复核：`python3 evidence/P8/verify.py`。它核对归档哈希、双平台全门/输出、Git源码绑定、实际发布回执与注册表安装/文件/API/CLI结果；它不发包、不联网、不替代组委会复验。
