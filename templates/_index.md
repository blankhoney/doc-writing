# 文档类型模板索引

> L1 层模板文件。准备阶段确定类型后完整读取对应模板，包含变体、条件、类型验证与适用分支，不裁成阶段片段。
> 选型及固定/定制边界见[准备入口](../runtime/prepare.md)；维护模板时见[模板规范](../docs/modules/5.2-document-templates.md) §5.2.8。

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

技术设计在同一类型内选架构方案／程序详细设计任务分支，再选原有变体；分支入口见该模板，不增加类型。

## 知识传递文档（Diátaxis）

项目介绍与现有架构说明按理解任务选 Explanation，不因读者负责验收就选变更或测试报告。Quickstart 指最快用上真实主要功能：已有会话或工具基础、只想完成一次任务时选 How-to 任务食谱；需要引导学习才选 Tutorial 最短路径，不另建类型。

| 类型 | 文件 | 默认变体 | 变体数 |
|------|------|---------|--------|
| Tutorial | [tutorial.md](tutorial.md) | 最短路径 | 3 |
| How-to Guide | [how-to.md](how-to.md) | 任务食谱 | 3 |
| Reference | [reference.md](reference.md) | 键卡片 | 4 |
| Explanation | [explanation.md](explanation.md) | 概念解释 | 3 |

## 扩展

新增文档类型按[模板指导](../docs/modules/5.2-document-templates.md) §5.2.10 执行。
