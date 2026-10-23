# P2 公开交付记录

2026-10-23，用户明确授权公开 z2823253773-p/mooneventeval，同时要求补充项目说明的通用性和三个完整预期使用场景。仓库现已公开；以下分开记录公开前检查与实际执行结果。

## 公开内容检查

对导出 main 0b9ae9216 及两个 SHA256 锁定原始历史根执行只读扫描：31,635 个 Git blob（313,799,607 字节），另扫描 306 个 ZIP 成员和 8,027 个 TAR 成员。选定私钥、GitHub/API token、AWS access ID、带凭证 URL 格式及参赛者手机号/邮箱均未命中。10 个非法 TAR/GZIP 是安装器负例素材；已扫描其原始字节，不冒称能解包。含“临床”的抽查上下文均为不访问临床数据/不作临床判断等边界说明。

这不是完整凭证检测认证；真实 Git 作者身份、Mac/runner 构建路径及内部开发/评审记录保留，以维持可追溯开发历史。原始 150MB 日志仍按既有 bundle 运输，不改写原始本地历史。扫描工具和结果见 evidence/P2/audit_public.py 与 public-git-audit.json。申报书及个人手机号/邮箱仅留在仓库外本地申报目录。

## 本轮变更与复核

更新 README、VALIDATION 的过时 macOS-only/未运行CI表述，指向实际 R1 成功双平台 run39914869650。产品评分、公开API、运行源码、CLI、工作流、参考锁未变。文档变更后的包和完整门仍按实际新被测SHA记录，不把旧CI结果冒称新HEAD测试。

新版申报材料的三个预期流程是声音事件评测、视频动作片段核对、外部脚本的模型回归定位；均使用现有JSON/API和评分规则，不增加音视频识别、TSV导入、IoU/mAP或内置双版本比较功能。它是AI辅助材料；未声明由参赛者独立撰写，也不以公开完成替代表单中“不要使用AI编写”的要求。

## 当前执行状态

GitHub API回执private=false、visibility=public；未携带Git认证头、禁用凭证助手/提示的ls-remote成功，返回f406084d7。首次匿名curl API请求网络接收超时（exit56），保留失败记录，不把它当匿名API成功证明。

原始候选23af827f / 导出被测f406084d7：本地完整17步成功；[公开后run39925966715](https://github.com/z2823253773-p/mooneventeval/actions/runs/39925966715)的macOS arm64、Ubuntu x86_64均成功。每OS58 Moon、28 Python、42验证、15 CLI、1620产品进程、38成员源包/解包消费均通过；各8144产物逐一hash复核，两OS205非证据源码hash一致并绑定公开Git提交f406084d7。后续文档收尾HEAD不冒称重新CI。

三个工作流用合成数据实际运行4次evaluate和1次explain，分别覆盖声音多录制/多类别、视频候选竞争和两个模型版本的边界回归；不是外部用户采用证据。新版申报书约900汉字，使用10.5pt正文在A4渲染为一页并检查无溢出；Markdown排版取决于接收方渲染。申报文件和联系方式没有加入Git。个人理解/独立撰写要求及正式报名未由此完成；未报名、未Mooncakes发布。

复核命令：`python3 evidence/P2-checks/freeze.py`；`python3 evidence/P2-checks/verify_public_ci.py --check-only`。独立克隆所需公开候选f406084d7在原生Git提交图中，可直接查询；旧R1原始对象仍按其provenance恢复工具获取，不重写冻结清单。
