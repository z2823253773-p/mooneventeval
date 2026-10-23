# MoonEventEval 本地交付包

直接打开 DEMO.html 查看三个案例、增广路径和本轮真实输出。不需要安装网页依赖，也不连接网络。它是代理执行的离线实录，不是用户本人演示。

本机运行（仅已验证 macOS arm64）：

```sh
bin/mooneventeval evaluate examples/duplicate.json --format json
bin/mooneventeval evaluate examples/greedy-trap.json --format text
bin/mooneventeval explain-pair examples/boundary.json --recording clip-01 --reference r1 --prediction p1 --format text
```

若解压工具未保留权限，执行 chmod +x bin/mooneventeval。不要绕过系统安全警告；其他Mac或其他平台并未实测。source/内为已验收38文件源候选；源码归档带有README、安装工具链说明和完整许可。

用户已取消自行复测，工程验收由Codex完成；这不表示参赛者已亲自讲解或已通过官方审核。公开仓库、Linux/远端CI、正式namespace/URL和发布未完成。

源与binary身份、当前五次复制binary调用在demo-data.json，原样输出在transcripts/；每个交付文件摘要在SHA256SUMS.json。当前输入只支持JSON字符串时间，重名键last-wins，NUL ID不能由literal CLI参数选中，超时部分输出取证有历史缺口。

本机原生binary包含编译时路径；本包仅作为本地候选，未完成公开脱敏。源候选zip与演示文本未发现本机绝对路径。不要将该本地候选误称正式公开发布。
