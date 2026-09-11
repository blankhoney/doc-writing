# 文档类型模板索引

> L1 层模板文件。Phase 1（准备阶段）根据文档类型加载对应模板。
> 模板规范见 `docs/modules/5.2-document-templates.md` §5.2.8。

## 工程生命周期文档

| 类型 | 文件 | 默认变体 | 变体数 |
|------|------|---------|--------|
| PRD | [prd.md](prd.md) | Lean | 4 |
| 技术设计 | [tech-design.md](tech-design.md) | Lean | 4 |
| API 文档 | [api-doc.md](api-doc.md) | 端点参考 | 3 |
| Changelog | [changelog.md](changelog.md) | Keep a Changelog | 3 |
| 测试报告 | [test-report.md](test-report.md) | CI 报告 | 3 |
| 部署/Runbook | [deploy-runbook.md](deploy-runbook.md) | Deploy Guide | 4 |
| ADR | [adr.md](adr.md) | Nygard | 5 |

## 知识传递文档（Diátaxis）

项目介绍与现有架构说明按理解任务选 Explanation，不因读者负责验收就选变更或测试报告。Quickstart 指最快用上真实主要功能：已有会话或工具基础、只想完成一次任务时选 How-to 任务食谱；需要引导学习才选 Tutorial 最短路径，不另建类型。

| 类型 | 文件 | 默认变体 | 变体数 |
|------|------|---------|--------|
| Tutorial | [tutorial.md](tutorial.md) | 最短路径 | 3 |
| How-to Guide | [how-to.md](how-to.md) | 任务食谱 | 3 |
| Reference | [reference.md](reference.md) | 键卡片 | 4 |
| Explanation | [explanation.md](explanation.md) | 概念解释 | 3 |

## 扩展

新增文档类型时：
1. 在此目录创建 `{type}.md`，遵循 5.2.8 规范
2. 在本文件添加索引行
3. 如有类型专用子规则，编号为 D{N}（D1 为架构文档质量清单）
