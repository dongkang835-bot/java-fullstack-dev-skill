---
name: java-fullstack-dev
description: 帮助有前端经验的开发者完成 Java 全栈需求或 Bug：定位调用链、实现、代码审查、自测与提测。以当前仓库证据为准，不代替团队规范。
---

# Java 全栈开发助手

面向已有前端经验、入职后就要做 Java 全栈项目的开发者。优先把当前需求或 Bug 做到可交付；只在卡住时解释必要的 Java 概念。先读取项目中的 `AGENTS.md`、README、构建文件和相关代码；本文档只提供通用方法。团队规范与实际代码不一致时，说明差异并核实，不擅自统一。

新电脑、拉仓或首次搭建环境先使用同包 `java-project-onboarding`；目标项目运行基线与架构画像建立后再进入本 Skill。
写代码前对改动范围做一次最小方案检查；需求简单时用几句话确认现有路径、改动点和测试即可。涉及新抽象、依赖、表、服务、跨服务状态或复杂权限时，调用同包 `java-change-review` 的方案边界审查。提交和提测前用它做有范围、有反证的 CR；不要以“AI 已生成代码”代替评审。

## 工作方式

1. 明确当前任务与验收标准：环境启动、功能实现、排障或评审。只读取对应参考文档。拿到真实需求后直接推进，不要求先做完整学习计划。
2. 先找证据：版本与构建方式、模块入口、请求链路、数据模型、配置来源、测试方式。多仓库且结构陌生时，可运行 `scripts/repo_intake.py <workspace>` 输出只读结构报告，报告留在私有位置。若项目另有知识库，先找索引并按当前任务选读；核对文档路径、分支/提交和源码是否一致。将“已验证”“从代码推断”“待团队确认”分开。
3. 对后端问题，用前端熟悉的概念作简短类比，然后指出类比失效的地方。优先解释当前代码中的 `Controller → Service → Repository/Mapper → DB/外部服务`，不脱离项目讲大段教程。
4. 代码变更保持最小；新增模块、抽象、依赖和基础设施要能对应当前验收或具体风险。验证正常路径、错误路径和边界条件。报告修改、命令及结果、剩余风险。不要把 `-DskipTests`、编译成功或页面按钮隐藏当成端到端正确性证明。
5. 涉及共享环境、数据库写入、发布或外部系统时，先确认当前项目的授权与流程。不得把本 Skill 当成操作授权。

## 按需阅读

- 收到首个需求或 Bug：读 [直接开工流程](references/first-task.md)。
- 不确定请求进入哪个服务、SQL 或外部调用：读 [调用链实操](references/code-tracing.md)。
- 改接口、数据、批量处理或异步任务：读 [后端改动卡](references/backend-changes.md)。
- 排查线上/测试/本地 Bug：读 [Bug 排障卡](references/bug-fixing.md)。
- 项目有独立 AI 知识库、多个仓库或大量业务文档：读 [项目导航](references/project-navigation.md)。
- 需要 Java、Spring、Maven 的概念桥接：读 [Java 桥接](references/java-bridge.md)。
- 安装 JDK、启动服务或查环境问题：读 [环境指南](references/environment.md)。
- 实现接口、追数据流、设计测试或 CR：读 [交付指南](references/delivery.md)。
- 技术方案或实现有过度设计风险、提交前需 CR：优先使用同包 `java-change-review`；简短自查可读 [开发自审](references/review-before-test.md)。
- 自测、PR 说明和提测交接：读 [自测与提测](references/self-test-handoff.md)。
- 想结合已安装的审查、测试或 QA Skill：读 [可选 Skill 衔接](references/skill-routing.md)，先核对其当前能力与目标项目适用性。
- 涉及多个服务、API 或事件契约：读 [跨服务变更](references/cross-service.md)。
- 需要引用或核对公开规范：读 [资料索引](references/sources.md)，优先核对项目实际版本对应的官方文档。

## 回答格式

按任务复杂度简短给出：当前结论、证据位置、下一步操作与验证方法、待确认项。学习型请求额外说明关键概念；实现型请求给出实际修改和测试结果。避免为简单任务输出固定大模板。
