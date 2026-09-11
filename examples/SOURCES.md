# 示例来源与使用范围

**本包保留 3 段已核验的外部来源示例。** “已核验”只针对下面登记的片段，不表示整个模板、当前技术行为或本次运行结果已验证。未核验的模板样本正文已移除。

模板结构与类型验证仍执行。真实来源、源码改编和构造示意按各自登记用途使用，不作为目标项目事实；外部原文不覆盖本包规则。未附样本的模板通过结构、模块与类型验证标准使用。

## 材料与使用范围

| 材料 | 状态 | 使用边界 |
|---|---|---|
| [Changelog 默认变体](../templates/changelog.md)的 Requests 2.31.0 条目 | 已核验，非官方翻译＋格式改编 | 只示范 Security 条目的影响范围与用户行动；历史版本，不是当前升级建议 |
| [Nygard ADR 变体](../templates/adr.md)的 Backstage ADR003 片段 | 已核验，非官方节译 | 只示范理由摘要与决策句，不是完整 Nygard ADR 合格样本 |
| [How-to 任务食谱](../templates/how-to.md)的 Django CSV 片段 | 已核验，非官方节译＋格式转换 | 只示范任务前提与完整实现；未运行，不是完整接入或验收清单 |
| [技术设计](../templates/tech-design.md)备忘/长片段、[How-to](../templates/how-to.md)扫描操作 | 本仓库源码改编，已对照实现；原创内容采用 MIT | 只示范深度与操作组织，非历史决策或本次运行记录 |
| [5.8](../docs/modules/5.8-structured-expression.md)动作/图树、[Reference](../templates/reference.md)JSON | 构造示意；原创内容采用 MIT | 只教排版与语法，不登记为真实来源已核验 |
| 自动测试夹具 | 构造测试输入 | 只验证测试所覆盖的行为，不是真实来源示例或项目事实 |

## 本仓库改编与构造示意

源码改编依据本包当前的 [doc-lint.py](../runtime/doc-lint.py)，已对照 `blank`、`mask_markdown`、`scan_text`、`main`。短设计说明保留行号的选择，长设计仅含方案与取舍；未测量内存。操作样本扫描本包 [README.md](../README.md)，依赖 Python 3.9 或更高版本、扫描脚本及其读取的 [design-spec.md](../docs/design-spec.md) 词源；需从包根目录执行并具备文件读取权限。样本未执行，输出说明来自源码，不是运行记录。

构造示意无外部来源；图未渲染，JSON 不对应实际应用。本包原创内容（包括源码改编说明和构造示意）采用 [MIT 许可证](../LICENSE)。下列第三方片段及其翻译、改编仍保留各自的署名、许可与使用范围，不因本包采用 MIT 而取消原许可条件。

## Requests 2.31.0

- **来源与位置**：Requests 项目的 [HISTORY.md 第 9–33 行](https://github.com/psf/requests/blob/147c8511ddbfa5e8f71bbf5c18ede0c4ceb3bba4/HISTORY.md#L9-L33)，`v2.31.0`，发布日期 `2023-05-22`。[附注 tag 对象](https://api.github.com/repos/psf/requests/git/tags/0106aced5faa299e6ede89d1230bd6784f2c3660)指向提交 `147c8511ddbfa5e8f71bbf5c18ede0c4ceb3bba4`；tag 对象自身的 SHA 不是提交 SHA。
- **内容性质**：2026-09-06 核验并翻译。版本标题改成 `## [版本] - 日期`，分类改为 `### Security`，调整换行并给示例 URL 加行内代码标记。保留原版本范围、触发条件、不受影响的情况、升级及轮换凭据顺序；没有新增迁移建议。Requests 原文不因此被宣称遵循 Keep a Changelog。
- **许可依据**：[该提交根 LICENSE](https://github.com/psf/requests/blob/147c8511ddbfa5e8f71bbf5c18ede0c4ceb3bba4/LICENSE)为 Apache-2.0；[NOTICE](https://github.com/psf/requests/blob/147c8511ddbfa5e8f71bbf5c18ede0c4ceb3bba4/NOTICE)载明 Requests / Copyright 2019 Kenneth Reitz。[项目文档直接包含 HISTORY.md](https://github.com/psf/requests/blob/147c8511ddbfa5e8f71bbf5c18ede0c4ceb3bba4/docs/community/updates.rst#L18)。结合文件归属、根许可与无覆盖例外，按 Apache-2.0 收录；不是维护者另行给予的专项授权。
- **范围与义务**：已检查目标文件、根目录及完整目录树。`docs/_themes/LICENSE` 只覆盖主题，`ext/LICENSE` 保留该目录素材权利，均不套用于本条目，也不收录这些资源。随包原样附[许可证全文](licenses/requests-LICENSE.txt)及[NOTICE](licenses/requests-NOTICE.txt)，在模板旁标记翻译与改编；不暗示官方背书，不复制所链接安全公告的正文。
- **校验**：原始 HISTORY.md 的 SHA-256 为 `b22101904f27e7fe5f7855dac688d6497ad43847e991441246f2dae28f29061d`。它证明取样版本，不证明该历史版本今天仍安全；本次没有复现或测试漏洞。

## Backstage ADR003

- **来源与位置**：The Backstage Authors 的 [ADR003: Avoid Default Exports and Prefer Named Exports，第 28–51 行](https://github.com/backstage/backstage/blob/1134d4b38c40583cdcd00637a7c29de02351f9d8/docs/architecture-decisions/adr003-avoid-default-exports.md#L28-L51)，固定提交 `1134d4b38c40583cdcd00637a7c29de02351f9d8`。[ADR 索引](https://github.com/backstage/backstage/blob/1134d4b38c40583cdcd00637a7c29de02351f9d8/docs/architecture-decisions/index.md#L8-L13)说明该目录记录项目已作出的决策，不是空白模板集合。
- **内容性质**：2026-09-06 核验并节译。翻译标题、理由摘要、具名导出的收益及停止默认导出的决策句，增加“节选”标记。省略前段历史背景、后段替代代码与迁移动作；保留 React.lazy 必要例外。原文理由是对已有讨论的摘要，不写成该项目的性能实测；不转载外链文章。
- **许可依据**：[该提交根 LICENSE](https://github.com/backstage/backstage/blob/1134d4b38c40583cdcd00637a7c29de02351f9d8/LICENSE)为 Apache-2.0；[CONTRIBUTING](https://github.com/backstage/backstage/blob/1134d4b38c40583cdcd00637a7c29de02351f9d8/CONTRIBUTING.md#L7-L9)明确仓库原创贡献使用相同许可，[文档贡献章节](https://github.com/backstage/backstage/blob/1134d4b38c40583cdcd00637a7c29de02351f9d8/CONTRIBUTING.md#L163-L175)明确包含 docs。目标文件头、docs 与 architecture-decisions 目录未发现更具体的覆盖许可。
- **范围与义务**：Copyright 2020 The Backstage Authors。随包原样附[许可证全文](licenses/backstage-LICENSE.txt)和[完整 NOTICE](licenses/backstage-NOTICE.txt)，不把其中对其他插件的归属写成本 ADR 的作者。翻译/删节已醒目标记，不暗示原作者背书。
- **校验与缺口**：原文 SHA-256 为 `8d67c3e0c57461829bcacf5424d08f2288f098fde029facd4ad96cc9671b2a3c`。原文没有 Accepted 或决策日期，后果也未区分正负；不使用仓库提交时间补成决策日期，不宣称它通过本包完整 ADR 类型验证。已核验范围仅为理由摘要与决策句写法。

## Django CSV

- **来源与位置**：Django Software Foundation and individual contributors 的 [How to create CSV output，第 9–33 行](https://github.com/django/django/blob/9e7cc2b628fe8fd3895986af9b7fc9525034c1b0/docs/howto/outputting-csv.txt#L9-L33)，Django `5.2` tag，固定提交 `9e7cc2b628fe8fd3895986af9b7fc9525034c1b0`。
- **内容性质**：2026-09-06 核验并节译。说明段落译为中文，reStructuredText 转为 Markdown；Python 函数、英文注释及示例行数据不改，仅移除代码块的外层缩进。未添加路由、业务数据、下载成功截图或本次运行结论。
- **许可依据**：[根 LICENSE](https://github.com/django/django/blob/9e7cc2b628fe8fd3895986af9b7fc9525034c1b0/LICENSE)为 BSD-3-Clause；[发行元数据](https://github.com/django/django/blob/9e7cc2b628fe8fd3895986af9b7fc9525034c1b0/pyproject.toml#L14-L25)声明相同许可，[MANIFEST.in](https://github.com/django/django/blob/9e7cc2b628fe8fd3895986af9b7fc9525034c1b0/MANIFEST.in#L4-L11)把 docs 与 LICENSE 纳入同一发行物，[FAQ](https://github.com/django/django/blob/9e7cc2b628fe8fd3895986af9b7fc9525034c1b0/docs/faq/general.txt#L74-L86)说明 BSD 许可及 Python 借用代码的独立许可。目标文件、docs/howto 与 docs 目录未发现另行覆盖许可。结论来自固定发行物的组合证据，不声称存在独立的 `docs/LICENSE` 或维护者专项授权。
- **范围与义务**：随包保留[许可证全文](licenses/django-LICENSE.txt)，包括版权、三项条件和免责；不得用 Django 或贡献者名称作背书。标明翻译是本包来源规范，也便于辨认改编范围；不将 Apache-2.0 的修改通知条款误称为 BSD 原文要求。不复制 Python 标准库实现，也不把官网页面的 CC 许可套到此文档。
- **校验与缺口**：原文 SHA-256 为 `f9c9969b63b174469f13a634bdf3e954d58a0402c26684dc7e4ba211509a17b3`。函数已逐行对照原文；本次未运行 Django。片段不是完整任务食谱，实际任务的环境、接入位置和验证信号仍需由目标项目证据补齐。

## 第三方许可核验是什么

确认外部材料允许我们做什么，以及带入本包时需要保留什么。公开可读不等于允许复制；根目录的代码许可证也不必然覆盖文档、图片或主题资源。

1. **核对对象**：定位原始文件与固定版本，查看文件头、文档目录的专门许可和项目许可声明，确认哪份许可适用。
2. **核对用途**：本包可能摘录、翻译、改编并再分发，逐项确认许可是否允许；有用途限制或条款不清楚时，保留为候选，不作已核验样本。
3. **履行条件**：按原许可保留版权、许可证全文、NOTICE（若要求），标明翻译或修改；不能把原作者写成对本项目的背书。
4. **区分范围**：第三方片段继续受其原许可约束；本包原创内容采用 MIT，不能用本项目 LICENSE 覆盖第三方材料的条件。

核验结果只针对登记的材料和使用方式，不是整个项目的法律合规保证。

## 后续每段示例的登记内容

| 字段 | 要求 |
|---|---|
| 来源与位置 | 原文标题、作者或组织、固定 URL、具体章节/片段位置及版本或获取日期 |
| 再分发依据 | 实际核对的许可文本及适用范围，所需署名与限制；不从仓库名字猜测许可 |
| 内容性质 | 原文摘录、翻译或改编；记录改变的事实、范围和符号，不以改编补造缺失字段 |
| 适用与验证 | 对应类型/变体、值得模仿的写法、已核对技术版本、未执行项与未决问题 |
| 状态 | 待核验或已核验；来源、许可与内容核验缺一项，都不能升级为正向 few-shot |

测试任务与来源示例是不同的验收项：跑通 `/doc-writing` 不能证明示例来源可靠，找到真实示例也不能证明技能按预期执行。
