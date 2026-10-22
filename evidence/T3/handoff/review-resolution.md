# T3 独立评审与作者修复记录

原候选范围`9c78a20aaa34514e218afd7ce26cae1e0ce03046..e9c7f317bcd141aa34dbcc3e1ee6728415be3824`；fresh只读评审者`/root/t3_independent_review`（gpt-6-astra/high）。评审因工具额度中断，后来恢复并完成同一次评审，没有另派席位。

**原评审结论：不可验收；Critical0 / Important2 / Minor0。** 完整原报告/脚本/命令/逐例stdout等107份收据已校验hash并保存到[evidence](../../evidence/T3/independent-review/review.md)，没有修改原始评审结论。

| 发现 | 原因/影响 | 作者修复及证据 |
| --- | --- | --- |
| P1 Important：非法JSON | String.escape生成MoonBit的\u{xx}；合法控制字符ID/label/错误path导致成功或失败报告无法JSON解析 | 全控制字符Moon/Python行为RED→统一JSON string encoder→GREEN，最终64进程往返与全套38项通过 |
| P2 Important：比较器漏检协议 | 被测数字时间被规范化为字符串；Python true==1等宽松相等；未校验嵌套键 | 四组回归RED→严格实际输出schema/类型/规范字符串/顺序→GREEN；比较器10项、全validation29项通过 |

两项按实际影响保持Important，不降级；单轮作者修复提交及被测SHA **508d5cf6cc5ef637f0931bbdaae36b1729256b03**。提交后Moon38/38、Python4/4、validation29/29、56进程输入/失败检查、64控制字符往返、46原型对照均通过。作者还重放评审原脚本（副本在review-replay-fixed，未覆盖原收据）；零非法成功/失败JSON，7项协议篡改拒绝。没有二次独立复审，不声称评审者复审通过修复。

## 独立评审确实做过的验证

临时git archive源码重新native37/37、release probe构建、32控制字符成功路径、1个控制字符错误路径及8个比较器篡改。评审未重新跑全部sed_eval46例、全部Python/资格mutation套件；这些仅审阅作者证据。检查了复制、规范分组、微平均/共享预算、精确时间、具体binary64见证；未发现这几项额外阻断。原工作树/index/HEAD未改动。

## Declined to judge及作者裁定

- file CLI/explain/demo与广泛非边界对照/最终A11：保留T4/T5/T6门槛；将原型外推会虚报产品验收。
- 用户本人复算/M2与Linux/远端CI/消费者/发布/参赛资格：仍无实证；代理材料/本地命令不能代替人或外部状态。
- 已冻结的重名键后值覆盖、原版零collar不支持：维持披露/分类，不新增预扫描、不改参考或epsilon；误改会更换数据/评测语义。
- 全部合法图均在预算内或宿主内存/时间保证：不作此承诺；独立比较器只验搜索步类型/范围及图工作计数，具体消费由白盒/共享预算测，不复制matcher为计步oracle。过度宣称会误导资源保证。
- STATE/manifest的收尾顺序：现在按计划更新并提交，不把写文档等同运行验证。

无延期Minor。作者确认两项修复及本地机器实现可交接，个人M2/最终A11仍未完成。
