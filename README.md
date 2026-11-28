# Java 全栈开发助手

给没有开发基础的纯小白使用。目标是让使用者借助 AI，在真实任务中写出资深前后端工程师水准的代码：定位准确、设计有边界、实现完整、验证有业务断言、审查能找到反例。仓库包含三个可安装的 Codex Skill：`java-project-onboarding` 负责新电脑、拉仓、环境与架构盘点；`java-fullstack-dev` 负责需求、Bug、实现、自测和提测；`java-change-review` 负责技术方案边界、控制过度设计和代码审查。它们不预设新公司的技术栈。

一次任务是否达到可评审质量，看四件事：验收与业务不变量有独立来源；代码放在正确的调用、权限与数据边界；有针对实际风险的执行证据；交付说明能讲清未验证项。具体执行见[资深质量闭环](java-fullstack-dev/references/senior-delivery.md)；可直接使用的[分阶段 Prompt](java-fullstack-dev/references/prompt-playbook.md)提炼自实际项目的技术方案、前后端编码与 CR 提示词；通用方法见[方法沉淀](docs/2026-11-27-methodology.md)。

## 提示词入口：直接复制

**系统提示词（工具支持自定义时使用）：**

```text
你是一名资深全栈工程师，具备资深 Java 后端、前端开发和代码审查能力。先从目标仓库核实技术栈、项目规范与业务边界，再完成技术方案、最小实现和验证。你的协作者是纯小白；请用实际代码位置、业务断言和运行结果解释关键决策。
```

**用户提示词：**

```text
请使用 java-fullstack-dev 完成 <需求或 Bug>。我没有开发基础，请你先核对项目规则、知识库和代码版本，从用户入口追到前端、后端、数据与下游，找相邻实现并验证其正确性。把验收转成业务不变量、最小方案和测试断言；信息足够就实施。运行相关验证后审查本次 diff，报告代码位置、命令、业务结果与未覆盖风险，并解释我需要理解的关键决策。
```

分阶段可复制：[技术方案](java-fullstack-dev/references/prompt-playbook.md#1-从需求到技术方案) · [前端方案与评审回写](java-fullstack-dev/references/prompt-playbook.md#前端技术方案与评审回写) · [后端编码](java-fullstack-dev/references/prompt-playbook.md#2-按方案实现后端) · [前端编码](java-fullstack-dev/references/prompt-playbook.md#3-按契约实现前端) · [代码 CR](java-fullstack-dev/references/prompt-playbook.md#4-代码-cr) · [前端专项 CR](java-fullstack-dev/references/prompt-playbook.md#前端专项-cr-与修复循环) · [知识库 CR](java-fullstack-dev/references/prompt-playbook.md#5-知识库-cr) · [代码自测](java-fullstack-dev/references/prompt-playbook.md#6-代码自测)。文中的 `{{变量}}` 和双引号中的 "业务领域"、"项目知识库" 都是需要按当前项目填写的占位符。

## 开始使用

1. 第一天拿到电脑和项目时，使用 [入职环境 Skill](java-project-onboarding/SKILL.md)、[首日顺序](java-project-onboarding/references/day-one.md)与 [安装操作页](java-project-onboarding/references/install-recipes.md)。
2. 将 `java-project-onboarding/`、`java-fullstack-dev/`、`java-change-review/` 分别复制到 `~/.codex/skills/` 下的同名目录，重启 Codex；也可直接让 AI 阅读各自的 `SKILL.md`。
3. 在新项目中复制 [项目画像模板](java-project-onboarding/assets/PROJECT_CONTEXT.template.md) 到**该项目的私有文档位置**，只填已经核实的信息。模板可能包含内部信息，填写后不要回传到这个公开仓库。
4. 在新项目对 AI 说：`请使用 java-project-onboarding，先检查电脑和当前仓库，按实际版本给我安装与启动步骤，再生成私有架构画像；先完成只读检查。`
5. 拿到需求或 Bug 后，按 [首个任务操作页](java-fullstack-dev/references/first-task.md) 使用 `java-fullstack-dev` 开工。

多仓库项目可先运行只读盘点：

```sh
python3 java-fullstack-dev/scripts/repo_intake.py /path/to/new-workspace > /path/to/private/repo-intake.md
```

报告只列结构、数量和候选版本；它仍可能包含内部目录名，**只放私有位置**。脚本不运行项目、不读取凭据值、不连接网络。

新电脑可先运行环境诊断；拉仓后再带项目目录运行一次：

```sh
python3 java-project-onboarding/scripts/workstation_doctor.py
python3 java-project-onboarding/scripts/workstation_doctor.py --project /path/to/new-workspace > /path/to/private/workstation.md
```

诊断只读，不会自动安装、连接公司系统或读取配置值。版本和缺项出来后，AI 再按目标项目和团队渠道执行实际安装。

完成导览后，可以直接这样提需求：

```text
请使用 java-fullstack-dev，帮我实现这个接口。先找相邻模块的实现，说明权限、事务、SQL 和前端契约；然后做最小修改，运行相关测试，并列出未验证的风险。
```

收到具体任务时，可复制[单次任务工作单](java-fullstack-dev/assets/TASK_BRIEF.template.md)到项目私有位置。它把验收标准、调用链、预期改动和验证证据放在同一页，方便与后端同事或评审人对齐。

## 入职后怎么实际用

**刚拿到仓库，还没有需求：**在新仓库中让 AI 使用 Skill 做一次只读导览，输出服务/模块、构建版本、启动依赖、测试命令和未知项。先核对仓库自带的 `AGENTS.md` 与团队文档，项目画像只写已经证实的内容。多仓库时可用上面的只读脚本生成私有盘点。

**刚拿到需求：**把需求和验收标准交给 AI，要求先按 [调用链实操](java-fullstack-dev/references/code-tracing.md) 从页面/API 追到后端与数据层，再按 [后端改动卡](java-fullstack-dev/references/backend-changes.md)检查权限、事务、兼容与验证。信息足够时直接实施，不需先学完 Java。

```text
请使用 java-fullstack-dev 完成下面的任务：<需求与验收标准>。
先读取当前仓库规则，确认分支和构建版本；从用户操作追到前端 API、Controller、Service、Mapper/外部服务和测试。
给出有文件行号的现状、预计改动与待确认的业务问题。然后实施最小改动、运行相关验证，并说明未覆盖项。
Java 概念只解释本次改动需要的部分；不要把别的项目规范套进来。
```

**刚拿到 Bug：**附上环境、复现步骤、期望/实际、请求 ID 和日志，使用 [Bug 排障卡](java-fullstack-dev/references/bug-fixing.md)固定失败证据、定位根因、写回归验证。根因暂时无法证实时，要求 AI 说明下一条最能区分原因的证据。

**准备发 PR：**让 AI 以当前 diff 和需求验收为依据做一次评审，重点检查后端数据权限、事务、并发、跨服务契约和测试缺口；只报告有源码证据的问题。

**AI 方案看起来太复杂：**使用 [方案边界审查](java-change-review/references/design-gate.md)核对现有能力、必要改动与新增复杂度的证据。公开包内的 [代码审查 Skill](java-change-review/SKILL.md)可独立使用，并带只读 [Git 范围脚本](java-change-review/scripts/review_scope.py)。若目标环境另有适用的 "测试视角审查 Skill"，按其自身规则衔接。

## 内容导航

| 场景 | 文档 |
| --- | --- |
| 收到需求或 Bug 后直接开工 | [first-task.md](java-fullstack-dev/references/first-task.md) |
| 按阶段填写技术方案、开发与 CR Prompt | [prompt-playbook.md](java-fullstack-dev/references/prompt-playbook.md) |
| 新手交付可评审的资深工程质量 | [senior-delivery.md](java-fullstack-dev/references/senior-delivery.md) |
| 新电脑、克隆、JDK/Node/构建工具安装 | [day-one.md](java-project-onboarding/references/day-one.md) |
| 确认项目版本后的 macOS/Windows 安装步骤 | [install-recipes.md](java-project-onboarding/references/install-recipes.md) |
| 仓库架构、数据库与中间件盘点 | [architecture-intake.md](java-project-onboarding/references/architecture-intake.md) |
| 从页面或请求定位到 Java、SQL 和下游服务 | [code-tracing.md](java-fullstack-dev/references/code-tracing.md) |
| 改接口、字段、批量处理与异步任务 | [backend-changes.md](java-fullstack-dev/references/backend-changes.md) |
| 用请求和日志排查 Bug | [bug-fixing.md](java-fullstack-dev/references/bug-fixing.md) |
| 导航大型项目或独立 AI 知识库 | [project-navigation.md](java-fullstack-dev/references/project-navigation.md) |
| 技术方案与过度设计审查 | [design-gate.md](java-change-review/references/design-gate.md) |
| 有范围、有反证的代码 CR | [java-change-review](java-change-review/SKILL.md) |
| 碰到不熟的 Java / Spring 代码时查阅 | [java-bridge.md](java-fullstack-dev/references/java-bridge.md) |
| 本地环境与启动排障 | [environment.md](java-fullstack-dev/references/environment.md) |
| 功能开发、测试和代码评审 | [delivery.md](java-fullstack-dev/references/delivery.md) |
| 开发自审与可选测试视角审查 Skill 衔接 | [review-before-test.md](java-fullstack-dev/references/review-before-test.md) |
| 自测、PR、提测说明 | [self-test-handoff.md](java-fullstack-dev/references/self-test-handoff.md) |
| 与已安装的 CR、用例、API/UI 测试 Skill 衔接 | [skill-routing.md](java-fullstack-dev/references/skill-routing.md) |
| 多服务接口与事件联动 | [cross-service.md](java-fullstack-dev/references/cross-service.md) |
| 公开权威资料与取舍 | [sources.md](java-fullstack-dev/references/sources.md) |

## 使用边界

现有项目的 `AGENTS.md`、团队约定、代码和真实配置优先。这三个 Skill 不会把某个旧项目的 Java 8、Spring Boot 2、MyBatis-Plus、字段注入、表命名或审批流程当成普遍标准。阿里巴巴《Java 开发手册》作为检查清单和学习资料使用，不复制手册正文，也不凌驾于新团队规范之上。

本仓库只收录从不同项目的**核心入口、索引和工作流中定向归纳**的通用做法，以及公开资料链接；源码盘点与代表性调用链用于校对方法，不等于逐文件理解全部业务实现。私有资料仅用于核对“需求输入 → 开发自测 → PR/提测 → 测试”的交接方式；没有复制内部文档原文、代码、地址、账户或业务规则。公开包自带独立的方案与代码审查 Skill；可选的外部扩展按实际安装版本和目标项目规则使用。公开上传前仍应检查自己的新增内容。
