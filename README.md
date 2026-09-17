<p>
  <img src="assets/doc-writing-logo.png" alt="doc-writing 黑白笔记本与笔标志" width="64" height="64">
</p>

# doc-writing

面向 Claude Code 的中文技术文档写作 skill。给出材料和目标，助手按文档类型组织内容、核对事实、编写正文，并完成表达与结构检查。

适合编写项目需求、技术方案、API 文档、部署手册、使用指南和架构说明，也可以检查或更新已有文档。

## 快速开始

已安装后，在目标项目会话中输入：

```text
/doc-writing 根据以下材料，写一份给项目贡献者的代码提交流程指南，只在对话中输出：开发者创建功能分支并提交合并请求；合并请求需要说明改动目的；自动化测试通过且一名维护者审核通过后，由维护者合并。
```

你会得到一份围绕创建分支、提交请求、测试和审核组织的操作指南。将示例材料换成实际项目材料，就可以开始自己的写作任务；模板和变体由助手根据目标选择。

需要保存时，直接指定位置，例如：

```text
/doc-writing 根据当前项目的 README.md，为新加入项目的工程师编写快速开始，保存到 docs/quickstart.md。
```

此请求以已有 `README.md` 为材料，并授权写入指定路径。只想先审阅正文时，改为“只在对话中输出”。

## 安装

需要支持 skills 的 Claude Code。先进入准备使用该 skill 的项目根目录；目标安装目录尚不存在时，执行：

```bash
mkdir -p .claude/skills
git clone https://github.com/blankhoney/doc-writing.git .claude/skills/doc-writing
```

在项目会话中用 `/skills` 确认 `doc-writing` 已被发现，然后手动调用 `/doc-writing`。若当前会话未发现新目录，重新打开会话后再检查。

如果需要在个人所有项目中使用，可将仓库克隆到 `~/.claude/skills/doc-writing/`。安装目录已存在时，先比较版本再更新，保留已有定制。

完整包中的 `SKILL.md`、`runtime/`、`templates/`、`docs/design-spec.md`、`docs/modules/` 和 `examples/` 应保持相对位置。候选扫描功能使用 Python 3.9 或更高版本，仅依赖标准库；不需要 pip 安装。Python 不可用时，助手仍可编写并完成模型检查，另行说明扫描未执行。

详细安装结构见[使用文档入口](docs/guide/README.md)。

## 能用它完成什么

| 任务 | 文档类型 | 主要产出 |
|---|---|---|
| 明确功能目标与验收 | PRD | 问题、目标与非目标、验收条件 |
| 设计方案并解释取舍 | 技术设计 | 方案、依据、组件职责与代价 |
| 说明接口调用方式 | API 文档 | 鉴权、端点、参数及错误处理 |
| 说明版本影响 | Changelog | 变更、影响及必要迁移步骤 |
| 汇报测试或安排测试 | 测试报告 | 范围、结果、证据或测试计划 |
| 编写部署和值班操作 | 部署／Runbook | 前提、步骤、验证与恢复方式 |
| 记录已有决策 | ADR | 决策、理由与后果 |
| 引导学习或完成任务 | Tutorial、How-to | 教程或可执行操作指南 |
| 查询契约或理解机制 | Reference、Explanation | 参数参考或原理、架构说明 |

用自然语言说明任务即可，也可以显式指定类型。完整类型和变体见[模板索引](templates/_index.md)。

检查已有文档而不改写：

```text
/doc-writing 检查 docs/architecture.md 的结构、术语和实现描述，列出具体位置及修改建议，不修改文件。
```

## 写作方法

- **从读者任务确定结构**：选择文档类型、变体和必要模块，保留必需章节，按任务决定深度。
- **用项目材料提供事实**：代码、配置、已有决策与运行记录分别支撑对应描述。
- **按信息关系组织表达**：动作使用步骤，参数使用字段表，组件依赖使用关系图，推理保留必要论证。
- **由模型完成判断**：模型检查范围、证据、术语和可操作性，脚本补充用词与格式候选的位置。
- **按反馈修正**：核对版本、去除阅读单元内的重复，重要文档再检查独立读者的理解与使用障碍。

完整机制与两幅关系图见[架构与优化方法](docs/guide/architecture.md)。

## 文档导航

| 文档 | 阅读目标 |
|---|---|
| [使用文档入口](docs/guide/README.md) | 安装、首次使用和后续导航 |
| [使用指南](docs/guide/usage.md) | 提供材料、保存文档、修改原文、只检查不改写 |
| [架构与优化方法](docs/guide/architecture.md) | 理解规则、模板、模型和扫描器的分工及完整流程 |
| [模板扩展](docs/guide/templates.md) | 添加类型、变体或模块，登记示例并验证扩展结果 |
| [贡献指南](CONTRIBUTING.md) | 修改规则、维护测试和提交改动 |

## 候选扫描器

需要独立查看用词和格式候选时，在本仓库根目录执行：

```bash
python3 runtime/doc-lint.py -- README.md
```

扫描器读取文件并返回候选位置，正文修改由使用者或助手决定。

| 项目 | 行为 |
|---|---|
| 输入 | 一个或多个 UTF-8 文件，支持 BOM、CRLF 和含空格路径 |
| 词源 | 直接读取 `docs/design-spec.md` 中的 G1 禁用模式清单 |
| 格式检查 | 中文标点、间距和括号；默认输出警告 |
| 输出 | `文件:行号:warning/类别:命中文本`，附完成统计 |
| 退出码 | `0`：扫描完成；`2`：参数、输入或规则读取发生错误 |
| 文件操作 | 只读，不联网，不执行文档中的代码或命令 |

`--skip-format` 可重复选择 `punctuation`、`spacing`、`parentheses`。例如，项目自行约定中英文间距时：

```bash
python3 runtime/doc-lint.py --skip-format spacing -- README.md
```

从其他目录调用时使用实际脚本绝对路径；待扫描文档的相对路径按终端当前目录解析。脚本按自身位置查找包内规则，`${CLAUDE_SKILL_DIR}` 是 skill 入口的路径变量，不是普通 shell 预设变量。

候选需要结合上下文判断。例如，引用中的词语可能应当保留；扫描完成状态只表示命令执行结果，全文质量由模型检查。

### 局部豁免

需要保留引用原文时，可在前一物理行注明原因：

```markdown
<!-- doc-lint: ignore-next-line 保留引用原文 -->
> 此处是需要原样保留的引用。
```

注释只抑制下一物理行的脚本候选，空行也会消耗这次豁免。输出会记录原因和数量；引用的真实性及其他写作要求仍由模型核对。

## 维护与测试

在仓库根目录运行：

```bash
python3 -B -m unittest discover -s tests -v
```

测试覆盖候选扫描、命令行接口、包结构和已登记示例的内容保护。真实写作任务的检查方法见[手动调用验收](tests/SMOKE.md)，新增类型的完整操作见[模板扩展](docs/guide/templates.md)。

## 许可证

项目原创代码、规则和文档采用 [MIT License](LICENSE)。Requests、Backstage、Django 的示例片段分别保留原项目的许可证和署名，详见[来源记录](examples/SOURCES.md)及 [examples/licenses/](examples/licenses/)。
