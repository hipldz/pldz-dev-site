---
author: "hipldz"
category: "agent-architecture"
csdn: ""
date: "2026-11-10"
gitee: ""
github: ""
juejin: ""
serialNo: 2
status: publish
summary: "回顾 2022 至 2026 年的 Agent 产品形态，梳理 AI IDE、Coding Agent、通用工作 Agent、Workflow 平台与 Harness 的不同定位。"
tags:
  - "AI Agent"
  - "Coding Agent"
  - "Workflow"
  - "Harness"
thumbnail: "/api/v1/website/image/agent-architecture/agent-product-landscape-2026-cover.webp"
title: "回头看到2026年的Agent产品"
---

> 写在 2026 年 11 月 9 日。个人和GPT\-6一起梳理的，不是完整行业年鉴。产品时间按首次公开、正式上线或关键形态转型来记；有些产品会持续改名、合并、迁移，后面也可能继续变。
>
>

![2026 年 Agent 产品主题插图](/api/v1/website/image/agent-architecture/agent-product-landscape-2026-figure-01.webp@original)

最近看到扣子（Coze）企业版下线的消息，还是蛮感慨的。以前大家热衷于拖节点、接插件、调 Prompt、搭 Bot，现在讨论得最多的，已经变成了 Claude Code、Codex、OpenClaw、各种 Work Agent，还有 Harness。感觉软件行业又换了一轮玩法。

不过先别急着说 Coze 整个平台没了。这里有个细节得说清楚：**2026 年 10 月 29 日公布的是扣子企业版的分阶段下线安排，不是 Coze 全站立即关停。** 企业标准版、企业旗舰版从 2026 年 11 月 30 日起停止新售；旧版套餐计划在 2026 年 12 月 31 日下线；新版企业套餐的下线时间是 2027 年 12 月 31 日。个人版和其他产品资源的后续安排，官方还说会再通知。公告原文：[扣子企业版下线公告](https://docs.coze.cn/enterprise-plan-discontinuation-notice)。

这件事让我想回头看一下：从 2022 年 11 月 ChatGPT（GPT\-3\.5）出来，到 2026 年大家几乎天天在聊 Agent，中间这几年产品到底怎么变的？

我之前也会把它们顺手排成一条线：GitHub Copilot → Cursor → Trae → Claude Code → Codex → Harness → OpenClaw → WorkBuddy / 百度搭子 / 豆包工作……看起来很顺，但仔细想想其实不太对。Cursor 是 IDE，Claude Code 是 CLI Coding Agent，Codex App 是多 Agent 工作台，OpenClaw 是偏个人自托管助手，DeepSeek Harness 又是运行底座。它们压根不是同一层的东西。

这篇不打算写成严格的产品年鉴，我想按产品形态把这几年捋一遍。尽可能的覆盖平时讨论 Agent 时绕不开的主流产品，差不多是一个“常见产品地图”，不是统计学意义的市场覆盖👀。中间有些产品上线时间会有预览版、正式版、改名等不同口径，我会尽量标明。

毕竟学习 AI Agent，才能用好 AI Agent（我学还不行吗 😭🥲）。

---

## 一、2022 到 2026，Agent产品不是一条线

![Agent 产品发展的四条路线](/api/v1/website/image/agent-architecture/agent-product-landscape-2026-figure-02.webp@original)

这张图我想表达的不是“xxx上一代被xxx下一代淘汰”，而是四条路线在发展：

1. **开发者工具**：代码补全、AI IDE、CLI Coding Agent、云端 Coding Agent、多 Agent 工作台。

2. **通用工作 Agent**：从聊天和搜索，走到研究、浏览器操作、桌面操作和跨应用办公。

3. **Workflow / Builder**：n8n、Dify、Coze 这类平台继续存在，也在吸收 Agent 能力。

4. **Runtime / Harness**：让 Agent 能持续执行、使用工具、管理上下文和权限的底层系统，越来越被单独拿出来讨论。

还有一个容易搞错的时间点：**GitHub Copilot 比 ChatGPT 还早。** Copilot 在 2021 年就做过技术预览，2022 年 6 月正式开放；ChatGPT 是 2022 年 11 月 30 日发布。所以如果我们要讲这段历史，不能简单写成“ChatGPT 出现后，才有 Copilot”。

另一个容易搞混的是 Codex：2021 年 OpenAI 就有过 Codex 代码模型；我们这里说的 2025 年 Codex CLI、Codex Cloud 和 2026 年 Codex App，是后来那套 Coding Agent 产品，不是同一个产品形态。

---

## 二、2022：ChatGPT 出圈，但 AI 还主要待在聊天框里

2022 年 11 月 30 日，ChatGPT 发布。最直观的变化是：原本要写代码、调 API、装软件才能用起来的模型能力，被包装成了一个普通人也能直接打开的聊天界面。

![早期 ChatGPT 历史界面](/api/v1/website/image/agent-architecture/agent-product-landscape-2026-figure-03.webp@original)

*图：早期 ChatGPT 经典界面。图源：*[*Japan Powered*](https://www.japanpowered.com/writing/chatgpt-and-bloggings-future)*。这张是历史界面参考，不是当前 ChatGPT 截图。*

那时候的产品直觉很简单：我问，它答。它能解释概念、写邮件、写代码、总结论文，甚至陪你讨论一个研究方案。

另一条更早的线是 GitHub Copilot。它不是通用聊天机器人，而是嵌在 IDE 里的代码助手：你写一半，它补下一段；你写函数名，它猜实现。它的价值不在于“跟你聊”，而在于把 AI 放进一个已有工作流里。

![VS Code 中的 Copilot 代码建议](/api/v1/website/image/agent-architecture/agent-product-landscape-2026-figure-04.webp@original)

*图：VS Code / Copilot 的代码建议交互。图源：*[*VS Code 官方文档*](https://code.visualstudio.com/docs/agents/agent-troubleshooting/faq)*。*

所以 2022 年其实有两种挺不一样的产品入口：

- ChatGPT：一个通用的自然语言入口。

- GitHub Copilot：一个嵌在开发工具里的 AI 辅助功能。

它们都很有用，但核心还是“帮人做当前这一步”。下一步要干什么，大多数时候还是人来决定。

---

## 三、2023：AI 开始进 IDE，也开始学会调用工具

2023 年我觉得有两个很重要的变化。

一个是 ChatGPT Plugins、Code Interpreter 和 Function Calling 这些能力开始让大家看到：模型不一定只能回一段文字，它也可以请求外部工具做事。比如运行 Python、查询外部 API、搜索信息，或者调用你自己写的函数。

另一个变化是 AI 原生 IDE 开始出现。Cursor 在 2023 年进入开发者视野，它的思路不是单纯在 VS Code 旁边放个聊天框，而是把代码库上下文、编辑器、对话和代码修改放在一起。

![Cursor 模式选择界面](/api/v1/website/image/agent-architecture/agent-product-landscape-2026-figure-05.webp@original)

*图：Cursor 的模式选择界面。图源：*[*AIDD Cursor 指南*](https://aidd.jp/blog/knowledge/cursor-ai-complete-guide/)*，第三方产品截图。*

这一步挺关键。以前的 Copilot 更像“你写代码，它帮你补”；Cursor 这类 AI IDE 开始变成“你告诉它想改什么，它理解项目，再帮你跨文件修改”。

与此同时，Aider 这样的终端 AI pair programming 工具也在发展。也就是说，AI 编程并没有只往 IDE 里走，Terminal 这条路线也在长。

![Aider 官网界面](/api/v1/website/image/agent-architecture/agent-product-landscape-2026-figure-06.webp@original)

*图：aider\.chat。图源：aider\.chat官网截图*

这一年还发生了 Function Calling。它的重点不是模型突然会执行 Python 了，而是模型可以返回结构化的工具调用请求；真正执行函数的还是外部程序。这个区别后面理解 Agent Runtime 时非常重要。

---

## 四、2024：Agent 开始离开聊天框，Workflow 平台也开始热闹

2024 年，产品形态明显多了起来。尤其是编码领域，大家开始尝试把任务直接交给 AI，而不是只让 AI 补一段代码。

### 4\.1 Devin：把软件工程任务交给一个远程 Agent

2024 年 3 月，Cognition 发布 Devin，把“AI 软件工程师”这个概念推到了大众面前。它不是只在编辑器里给你建议，而是给 Agent 一个自己的工作环境：能看代码、运行命令、浏览网页、改文件，再把结果交回来。

![Devin 任务执行界面](/api/v1/website/image/agent-architecture/agent-product-landscape-2026-figure-07.webp@original)

*图：Devin 任务执行界面。图源：*[*Toksta 产品页面*](https://www.toksta.com/products/devin-ai)*，第三方截图。*

当然，早期 Devin 的演示和实际可用性之间也有距离，但它把一个方向摆到了台面上：**AI 不只是写代码，而是尝试接手一项完整的软件工程任务。**

### 4\.2 Replit Agent、Bolt\.new：从“写代码”扩展到“做出一个应用”

2024 年下半年，Replit Agent、Bolt\.new 这一类产品开始火起来。它们面向的不只是传统开发者，而是“我想做一个网页 / 小应用，但我不想从零开始写代码”的用户。

用户描述需求，Agent 生成代码、预览页面、继续修改，有些产品还能直接部署。

这条路线后来常被叫作 AI App Builder 或 Vibe Coding。它和传统 Coding Agent 有交集，但产品目标不完全一样：前者更关心“快速做出一个能跑的应用”，后者通常更关心“在一个已有代码库里完成工程任务”。

### 4\.3 Windsurf、Cline：IDE 里的 Agent 味道越来越浓

2024 年 11 月，Codeium 推出 Windsurf Editor，核心体验是 Cascade：AI 不只是回答问题，而是理解上下文、编辑代码、运行工具，和开发者在同一个工作区里协作。

![Windsurf Cascade 界面](/api/v1/website/image/agent-architecture/agent-product-landscape-2026-figure-08.webp@original)

*图：Windsurf Cascade 界面。图源：*[*DataCamp*](https://www.datacamp.com/tutorial/windsurf-ai-agentic-code-editor)*，第三方截图。*

Cline（最初叫 Claude Dev）则是 VS Code 里的开源 Coding Agent。它会请求读取文件、执行命令、访问浏览器等操作，并在需要时让用户批准。它把“Agent 的权限边界”也做成了产品交互的一部分。

![Cline 官网界面](/api/v1/website/image/agent-architecture/agent-product-landscape-2026-figure-09.webp@original)

*图：cline\.bot官网截图*

### 4\.4 Workflow 平台：n8n、Dify、Coze

这几年还有一条并行路线：把 LLM 和工具编排成可以重复运行的应用。

这里我想特别说一下：**Workflow 不是大模型时代才出现的。** n8n 这样的自动化平台早就存在，传统业务系统也早就有流程引擎。LLM 只是后来变成了 Workflow 里很常见的一个节点。

![n8n 节点式流程画布](/api/v1/website/image/agent-architecture/agent-product-landscape-2026-figure-10.webp@original)

*图：n8n 的节点式流程画布。图源：*[*BetaZeta*](https://betazeta.dev/blog/automatization-n8n-nodes/)*，第三方截图。*

![Dify Workflow Studio](/api/v1/website/image/agent-architecture/agent-product-landscape-2026-figure-11.webp@original)

*图：Dify Workflow Studio。图源：*[*Dify 官方页面*](https://dify.ai/zh/workflows)*。*

![Coze 工作流节点配置示例](/api/v1/website/image/agent-architecture/agent-product-landscape-2026-figure-12.webp@original)

*图：Coze 工作流节点配置示例。图源：*[*CSDN 社区文章*](https://blog.csdn.net/xianyu120/article/details/137353856)*，第三方截图。*

这三个产品不是同一种东西的三个皮肤：

- n8n：本来就是通用自动化平台，后来积极加入 AI 节点、Agent 节点。

- Dify：更偏 LLM 应用开发，Prompt、RAG、Workflow、工具、Agent 都是它的组成部分。

- Coze：更偏低代码 AI Bot / Agent 应用搭建，插件、知识库、工作流和发布渠道都放在一个平台里。

它们解决的问题是：开发者不必从零把模型、API、知识库、数据流和运行逻辑全写一遍。

但 Workflow 的路径通常是开发者提前设计好的。即使里面有 LLM 节点，也不代表整个系统就变成了 Agent。这个区别下一篇再认真聊。

---

## 五、2025：Coding Agent 真正成了一个产品类别

如果让我选一个变化最明显的年份，我会选 2025。

因为这一年，Coding Agent 从“看起来很酷的实验”变成了很多开发者日常会用的工具。产品不再只问“能不能补代码”，而是开始问“能不能接一个 issue，自己改完、跑测试、给我一个 PR”。

### 5\.1 2025 年初：IDE、CLI、Browser Agent 同时往前走

- **TRAE**：字节跳动在 2025 年 1 月推出 AI IDE，后续持续加强 Builder / Agent 能力。

- **OpenAI Operator**：2025 年 1 月发布，重点是让 Agent 通过浏览器界面完成任务。

- **Deep Research**：2025 年 2 月发布，把多步骤研究任务变成一个可以委托的产品形态。

- **GitHub Copilot Agent Mode**：2025 年 2 月进入预览，让 Copilot 在 IDE 中更主动地规划、编辑和运行代码。

- **Claude Code**：2025 年 2 月 24 日随 Claude 3\.7 Sonnet 一起发布研究预览，主打 Terminal 里的 Coding Agent。

![TRAE IDE Builder 模式](/api/v1/website/image/agent-architecture/agent-product-landscape-2026-figure-13.webp@original)

*图：TRAE IDE Builder 模式。图源：*[*Clubic*](https://www.clubic.com/actualite-551492-bytedance-tiktok-lance-son-concurrent-a-vs-code-et-cursor-ai-et-il-est-totalement-gratuit-pour-l-instant.html)*，媒体截图。*

![Claude Code 在终端中运行子 Agent](/api/v1/website/image/agent-architecture/agent-product-landscape-2026-figure-14.webp@original)

*图：Claude Code 在终端中运行子 Agent。图源：*[*Anthropic Claude Code Academy*](https://anthropic.skilljar.com/claude-code-101)*。*

这几个产品的入口完全不同：TRAE 在 IDE 里，Claude Code 在 Terminal 里，Operator 在浏览器里，Deep Research 则更像一个研究任务工作台。但它们都在尝试让用户从“问一个问题”转向“交代一个目标”。

### 5\.2 Codex：本地 CLI 和云端 Agent 是两种不同形态

2025 年 4 月 16 日，OpenAI 发布 Codex CLI，一个在本地 Terminal 里运行的开源 Coding Agent。

2025 年 5 月 16 日，OpenAI 又发布云端 Codex Agent。它在独立的云端沙箱里运行任务，可以并行处理多个工程任务，最后把改动和测试结果交给开发者审查。

这两个产品虽然都叫 Codex，但使用场景不一样：

- Codex CLI：在本地项目目录里工作，适合开发者边看边改。

- Codex Cloud：把任务派到云端环境异步执行，适合把一项工作交出去，稍后回来验收。

![Codex 网页界面](/api/v1/website/image/agent-architecture/agent-product-landscape-2026-figure-15.webp@original)

*图：Codex 网页截图*

![Codex 多 Agent 工作区示意截图](/api/v1/website/image/agent-architecture/agent-product-landscape-2026-figure-16.webp@original)

*图：Codex 多 Agent 工作区示意截图。图源：*[*OpenAI Developer Community*](https://community.openai.com/t/hierarchical-multi-agent-workflow-visual-tree-based-agent-orchestration-in-codex-app/1401395)*，社区帖子截图。*

### 5\.3 2025 年中后段：云端 Coding Agent 开始变多

这一年还有几个值得放进时间线的节点：

- Cursor Background Agent：2025 年 5 月开始预览，6 月向更多用户开放。Agent 可以在独立远程环境里运行，开发者可以并行启动多个任务。

- GitHub Copilot Coding Agent：2025 年 5 月推出，让 Copilot 能从 GitHub Issue 接任务，在云端环境中改代码并提交 PR。

- Google Jules：2025 年 5 月进入公开 Beta，定位也是云端异步 Coding Agent。

- Gemini CLI：2025 年 6 月发布，把 Gemini 的 Agent 能力带进 Terminal。

- Kiro：2025 年 7 月进入预览，主打 Spec\-driven development，把需求规格、设计和实现串起来。

- Qoder：2025 年 8 月 21 日发布首个版本，属于阿里系 AI IDE / Coding Agent 产品线。

- CodeBuddy：腾讯的编程产品线，包含 IDE 和 CLI 等不同入口。你之前提到的“coder”，我不确定是不是指 CodeBuddy，也可能是阿里的 Qoder；这两个名字最好分开。

![CodeBuddy IDE 界面](/api/v1/website/image/agent-architecture/agent-product-landscape-2026-figure-17.webp@original)

*图：CodeBuddy IDE。图源：*[*CodeBuddy 官方产品页*](https://www.codebuddy.ai/ide)*。*

### 5\.4 不只是 Coding：Manus 和 ChatGPT Agent

2025 年 3 月，Manus 引起了很大关注。它想做的不是一个专门写代码的 Agent，而是一个通用任务 Agent：研究、整理信息、运行代码、生成文件，最后交付一个结果。

![Manus 研究任务执行界面](/api/v1/website/image/agent-architecture/agent-product-landscape-2026-figure-18.webp@original)

*图：Manus 执行研究任务的界面。图源：*[*WorkOS*](https://workos.com/blog/introducing-manus-the-general-ai-agent)*。*

2025 年 7 月，OpenAI 发布 ChatGPT Agent，把 Operator 的浏览器操作能力和 Deep Research 的研究能力进一步结合起来，让 ChatGPT 可以使用自己的计算机环境执行多步骤任务。

这一年我觉得最重要的变化是：**Agent 开始从 Coding 场景向通用工作场景扩散。**

---

## 六、2026：Agent 开始像一个“同事”，而不只是一个工具

到了 2026 年，产品形态又往前走了一步。很多产品不再把自己定位成“一个更聪明的聊天框”，而是一个可以常驻、接入工作资料、管理任务、操作桌面，甚至协调多个 Agent 的工作台。

### 6\.1 Claude Cowork：把 Claude Code 的做事方式带到办公任务

2026 年 1 月 12 日，Anthropic 推出 Claude Cowork 研究预览。它和 Claude Code 有亲缘关系，但目标不是只处理代码，而是处理文件、文档、资料整理和更广泛的知识工作。

![Claude Cowork 界面](/api/v1/website/image/agent-architecture/agent-product-landscape-2026-figure-19.webp@original)

*图：Claude Cowork 界面。图源：*[*Claude Academy*](https://academy.claude.com/tutorials/get-started-in-claude-cowork-in-three-steps)*。*

### 6\.2 OpenClaw：个人 Agent / 自托管助手这条路线

OpenClaw 这条路线又不一样。它不是单纯的云端 SaaS，也不是一个 IDE 插件，而是一个可以部署在自己机器或服务器上的个人 AI 助手。它可以接入 Telegram、WhatsApp、Discord 等消息渠道，也能通过 Gateway、Skills、工具和本地环境去执行任务。

OpenClaw 项目起步于 2025 年 11 月，之后在 2026 年初迅速出圈。它的意义不只是“又一个聊天机器人”，而是让 Agent 变成一个可以常驻、连接个人工具和消息入口的东西。

![OpenClaw Dashboard 界面参考](/api/v1/website/image/agent-architecture/agent-product-landscape-2026-figure-20.webp@original)

*图：OpenClaw Dashboard 界面参考。图源：*[*Skywork OpenClaw 介绍*](https://skywork.ai/skypage/en/openclaw-agent-framework-ai/2049089901959643136)，第三方截图；产品功能以 [*OpenClaw 官方文档*](https://docs.openclaw.ai/)* 为准。*

### 6\.3 Codex App、Antigravity：从一个 Agent，变成管理多个 Agent 的指挥台

2026 年 2 月 2 日，OpenAI 发布 Codex App。它不是简单地把 CLI 搬到桌面，而是让开发者可以同时管理多个 Agent：不同任务放在不同 Thread / Project 里，多个 Agent 可以并行工作，用户负责分配、监督、Review 和合并结果。

Google Antigravity 也在往这个方向走。它在 2025 年 11 月以 agent\-first IDE 的形态推出，产品里比较显眼的是 Agent Manager：不只是写代码的编辑器，还要让用户能看 Agent 在做什么、管理不同任务。它和 Cursor、Windsurf 的区别，不是简单的“有没有编辑器”，而是产品开始把 Agent 管理本身放到更靠前的位置。

这个变化挺值得注意：当 Agent 已经可以自己工作几个小时，人的瓶颈就不再是“怎么告诉它写代码”，而是“怎么同时管理十个正在工作的 Agent”。

### 6\.4 国内的桌面工作 Agent：WorkBuddy、DuMate、QoderWork、豆包工作

2026 年国内也出现了一批很有代表性的桌面 Agent 产品。

**腾讯 WorkBuddy**：2026 年 3 月 9 日正式上线，定位是职场 AI 原生智能体桌面工作台（[腾讯云产品页](https://cloud.tencent.com/product/workbuddy)）。它可以处理文档、数据分析、文件管理、办公流程，也在不断打通腾讯生态和企业工具。

![WorkBuddy 任务交付界面](/api/v1/website/image/agent-architecture/agent-product-landscape-2026-figure-21.webp@original)

*图：WorkBuddy 的任务交付界面。图源：*[*腾讯云 WorkBuddy 官方页面*](https://cloud.tencent.com/act/pro/workbuddy)*。*

**百度 DuMate（百度搭子）**：2026 年 3 月 17 日发布，3 月 22 日正式上线（[百度搭子产品文档](https://aca.bce.baidu.com/doc/Dumate/index.html)）。它更像一个桌面 Agent，可以操作本地文件、做多源数据分析、生成文档和表格，并通过安全沙箱、权限审批等机制控制本地执行风险。

![百度 DuMate 发布文章配图](/api/v1/website/image/agent-architecture/agent-product-landscape-2026-figure-22.webp@original)

*图：DuMate 官方发布文章配图。图源：*[*百度智能云千帆社区*](https://qianfan.cloud.baidu.com/qianfandev/topic/687919)*。*

**阿里 QoderWork**：这里要和 Qoder 分开。Qoder 是偏 Coding 的产品线；QoderWork 则是 2026 年 1 月推出的桌面工作 Agent，面向文档、数据分析、文件整理等日常任务。它后来持续增加写作、幻灯片、设计和专家套件等工作台能力。

![QoderWork 桌面任务与权限确认界面](/api/v1/website/image/agent-architecture/agent-product-landscape-2026-figure-23.webp@original)

*图：QoderWork 的桌面任务和权限确认界面。图源：*[*云栈社区*](https://yunpan.plus/t/11911-1-1)*，第三方截图。*

有个后续也值得记下来：阿里云在 2026 年 9 月发布公告，QoderWork 将于 2027 年 9 月 5 日停止运营，并建议办公场景迁移到千问办公；Qoder 家族的其他产品不受影响。这又是一个产品整合的例子。

**豆包工作**：2026 年 8 月 25 日正式发布，面向生产力场景。它可以围绕目标拆任务、调用工具、生成文档表格 PPT，也与飞书打通，使用用户授权范围内的企业上下文。

这里顺便补一个 Coze 的时间点：扣子并不是一路从 Workflow 原地走到下线。2026 年 1 月它还发布过扣子 2\.0，继续强化 Agent Skills 和任务交付方向；到 8 月，团队和部分工作场景能力被并入豆包体系；10 月底公布的则是企业版分阶段下线。把这几件事放在一起看，更像是产品线在整合，而不是“Agent Builder 这个品类突然没用了”。[扣子 2\.0 相关报道](https://www.aitntnews.com/newDetail.html?newId=21756) · [企业版下线公告报道](https://www.thepaper.cn/newsDetail_forward_34431810)。

![豆包工作桌面界面](/api/v1/website/image/agent-architecture/agent-product-landscape-2026-figure-24.webp@original)

*图：豆包工作桌面界面。图源：*[*中国商业新闻网*](https://www.cbinews.com/AI/g0qxu)*，媒体截图。*

这里还有一个产品组织层面的变化：2026 年 8 月，媒体报道字节将 TRAE、Coze 团队并入豆包体系；其中 TRAE Work 和 Coze 的工作场景能力与豆包工作整合，TRAE IDE 和 CLI 则继续作为编程产品线发展。也就是说，不是“TRAE 和 Coze 一夜之间都没了”，而是产品线和团队开始重组。

阿里这边也有类似的整合动作：QoderWork、悟空（2026 年 3 月 17 日发布的企业级工作平台）和 MuleRun 曾被报道计划整合；随后阿里云又公告，QoderWork 将于 2027 年 9 月 5 日停止运营，办公场景建议迁移到千问办公。这里能看到一个趋势：企业 Agent 产品还在快速试错，产品品牌、团队和入口并不稳定。

### 6\.5 DeepSeek Harness：名字里已经把 Harness 摆出来了

2026 年 8 月 13 日，DeepSeek Harness v0\.1 开发者预览版开放，并同步开源（[官方项目主页](https://www.deepseek.com/harness/en/) · [GitHub 仓库](https://github.com/deepseek-ai/deepseek-harness)）。它的定位和 WorkBuddy、DuMate 不完全一样：它不只是一个给普通用户使用的工作 Agent，更强调可组合插件、Agent 执行环境和可扩展的 Harness 架构，同时提供桌面应用和 Web UI。

![DeepSeek Harness 桌面界面](/api/v1/website/image/agent-architecture/agent-product-landscape-2026-figure-25.webp@original)

*图：DeepSeek Harness 桌面界面。图源：*[*Tenten 实测文章*](https://tenten.co/learning/deepseek-harness-desktop-app-walkthrough/)，第三方截图；产品定位以 [*DeepSeek 官方页面*](https://www.deepseek.com/en/harness/) 和 [*官方 GitHub 仓库*](https://github.com/deepseek-ai/deepseek-harness)* 为准。*

还有一个我觉得很有意思的信号：2026 年 5 月 13 日，Cline 推出 Cline SDK，官方文章直接把它称为 upgraded agent runtime（[Cline 官方文章](https://cline.bot/blog/introducing-cline-sdk-the-upgraded-agent-runtime)）。也就是说，早期很多产品是先把 Agent Loop 写在 IDE 插件里，后来功能越来越多，才发现需要把 Runtime 从 IDE 界面里拆出来，变成可以复用的独立底座。

---

## 七、把这些产品重新归类：它们其实不在同一层

我把前面这些名字重新放一遍。这样看会清楚很多。

![Agent 产品形态分类图](/api/v1/website/image/agent-architecture/agent-product-landscape-2026-figure-26.webp@original)

|产品形态|代表产品|它主要解决什么问题|
|---|---|---|
|代码补全 / IDE 插件|GitHub Copilot、Codeium、通义灵码早期形态|在当前编辑位置帮人更快写代码|
|AI 原生 IDE|Cursor、Windsurf、TRAE IDE、Qoder IDE、CodeBuddy IDE|理解项目上下文，在 IDE 里完成多文件修改|
|本地 CLI Coding Agent|Claude Code、Codex CLI、Gemini CLI、Cline、CodeBuddy Code|直接在仓库和终端环境里执行开发任务|
|云端 / 异步 Coding Agent|Devin、Jules、GitHub Copilot Coding Agent、Cursor Background Agent、Codex Cloud|把任务派出去，在远程环境执行，完成后再 Review|
|通用工作 Agent|Manus、Claude Cowork、OpenClaw、WorkBuddy、DuMate、豆包工作、ChatGPT Work、QoderWork|从写代码扩展到研究、文件、办公和跨应用任务|
|多 Agent 工作台|Codex App、Qoder 1\.0 等|管理多个 Agent 并行工作、分配任务、验收结果|
|Workflow / Agent Builder|n8n、Dify、Coze|把模型、工具和业务逻辑组织成可复用应用|
|Runtime / Harness|DeepSeek Harness、Cline SDK，以及 Codex / Claude Code 内部的执行底座|管理模型调用、工具、上下文、权限、状态、恢复和追踪|

这里最容易混淆的就是最后两行：

- **Codex App 是一个用户工作台**，让人方便地管理多个 Agent。

- **Harness / Runtime 是执行底座**，负责 Agent 实际怎样跑起来。

它们不是一个层次。一个桌面工作台可以管理多个 Agent，而每个 Agent 背后还需要 Runtime。

还有几个名字也容易串：**CodeBuddy 和 Qoder 不是一个产品**，前者是腾讯的编程产品线，后者是阿里的编程产品线；**Qoder 和 QoderWork 也不是一个产品形态**，前者偏 Coding，后者是桌面办公 Agent。你前面提到的“coder”，我这里按腾讯 CodeBuddy 一并放进来。

再说 OpenClaw。它不是 Claude Code 的下一代，也不是 Codex 的竞品替代品。它更像一个可自托管、可接入消息渠道和本地工具的个人 Agent 项目。它的项目在 2025 年 11 月以 Clawdbot 起步，2026 年 1 月经历 Clawd / Moltbot 的改名，1 月 30 日才定名 OpenClaw（[OpenClaw 官方起源说明](https://docs.openclaw.ai/zh-CN/start/lore)）。把它和 IDE 或 CLI Coding Agent 放在一条直线上比较，容易把产品入口和底层执行能力混在一起。

---

## 八、所以，2026 年的 Agent 产品到底发展到什么状态了？

我现在的理解是：不是大家都在做同一种 Agent，而是 Agent 能力开始出现在不同的产品入口里。

**1\. IDE 没有消失，只是从“写代码的地方”变成了“监督代码 Agent 的地方”。**

Cursor、Windsurf、TRAE、Qoder 仍然很重要。只不过用户不再只盯着补全建议，而是会给它一个任务，让它改一组文件、跑测试，再检查 Diff。

**2\. Terminal 也没有消失，反而成了 Coding Agent 很自然的入口。**

Claude Code、Codex CLI、Gemini CLI、Cline 这类产品说明：对开发者来说，文件、Git、Shell、测试工具本来就在 Terminal 附近。Agent 能直接使用这些工具，反而少了一层抽象。

**3\. 云端异步 Agent 开始承担“派活”的角色。**

Devin、Jules、Copilot Coding Agent、Codex Cloud、Cursor Background Agent 这类产品，让人可以同时派出多个任务，不必一直守在 IDE 旁边。

**4\. 通用工作 Agent 开始争夺办公入口。**

Manus、Claude Cowork、OpenClaw、WorkBuddy、DuMate、豆包工作、ChatGPT Work 等产品，关注的不再是“帮我写一段代码”，而是“帮我把这件事做完”。文件、浏览器、桌面、日历、邮件、知识库、企业 IM 都可能变成 Agent 的工作环境。

**5\. 多 Agent 和 Harness 开始变成新的工程问题。**

当一个人可以同时派出多个 Agent，问题就变成：谁负责拆任务？Agent 之间怎么协作？上下文怎么共享？工具权限怎么控制？失败了怎么恢复？结果怎么验收？

所以我觉得 2026 年最值得关注的变化，不是又多了十个 Agent 产品，而是大家开始意识到：**Agent 不只是一个模型加几个工具，它背后需要一套真正能运行、能管理、能恢复的系统。**

这也解释了为什么 Harness 这个词开始变得重要。这里也要分清楚：Harness 是一类工程架构 / 执行底座的概念；DeepSeek Harness 是一个具体开源项目；Cline SDK 是把 Cline 的 Agent Runtime 拆出来做成可复用 SDK；Codex App 则是用户管理任务和多个 Agent 的桌面工作台。名字里都带着 Agent 味道，但它们解决的问题不一样。

---

## 附：主流产品时间点速查（不完全，但基本把常见名字放进来了）

|时间|产品 / 事件|大致属于哪条路线|
|---|---|---|
|2021\.06|GitHub Copilot 技术预览|代码补全 / 插件（前史）|
|2022\.06|GitHub Copilot 正式开放|代码补全 / 插件|
|2022\.11\.30|ChatGPT（GPT\-3\.5）发布|通用 Chatbot|
|2023|Cursor 进入开发者视野；Aider 等终端工具发展|AI IDE / CLI 助手|
|2023\.06|OpenAI Function Calling|Tool Use 能力|
|2023\.12|Coze 海外版推出|Bot / Agent Builder|
|2024\.02|扣子国内版上线|Bot / Workflow Builder|
|2024\.03|Devin 发布|自主 Coding Agent|
|2024\.04|GitHub Copilot Workspace 技术预览|Issue → Plan → Code 的任务式开发|
|2024\.09|Replit Agent|Prompt\-to\-App / Coding Agent|
|2024\.10|Bolt\.new|Prompt\-to\-App / Vibe Coding|
|2024\.11|Windsurf Editor；Cline（原 Claude Dev）开始走红|AI IDE / IDE 内 Agent|
|2025\.01|TRAE；OpenAI Operator|AI IDE / Browser Agent|
|2025\.02|Deep Research；Copilot Agent Mode；Claude Code|研究 Agent / IDE Agent / CLI Agent|
|2025\.03|Manus|通用任务 Agent|
|2025\.04|OpenAI Codex CLI|本地 CLI Coding Agent|
|2025\.05|Codex Cloud；GitHub Copilot Coding Agent；Jules；Cursor Background Agent|云端 / 异步 Coding Agent|
|2025\.06|Gemini CLI|开源 CLI Agent|
|2025\.07|ChatGPT Agent；Kiro 预览；CodeBuddy IDE|通用 Agent / Spec\-driven IDE / AI IDE|
|2025\.08|Qoder 首版；Jules 正式公开|AI IDE / 云端 Coding Agent|
|2025\.09|CodeBuddy Code CLI|CLI Coding Agent|
|2025\.10|Codex 正式 GA|Coding Agent 产品化|
|2025\.11|Google Antigravity；OpenClaw 的 Clawd 项目开始|Agent\-first IDE / 个人 Agent|
|2026\.01|Claude Cowork（1\.12）；QoderWork|通用工作 Agent / 桌面 Agent|
|2026\.01\.30|OpenClaw 定名（从 Clawd、Moltbot 演化而来）|自托管个人 Agent|
|2026\.02\.02|Codex App|多 Agent 工作台|
|2026\.03|WorkBuddy（3\.9）；阿里悟空（3\.17）；DuMate（3\.22）；Accio Work|办公 / 企业 Agent|
|2026\.05\.13|Cline SDK|Agent Runtime / Harness SDK|
|2026\.05\.15|Qoder 1\.0|从 AI IDE 转向自主开发工作台|
|2026\.07\.09|ChatGPT Work 发布|通用工作 Agent|
|2026\.08\.13|DeepSeek Harness 开发者预览并开源；8\.25 豆包工作发布|Harness / 通用工作 Agent|
|2026\.08|TRAE、Coze 团队并入豆包体系的消息|产品线整合|
|2026\.09\.08|QoderWork 下线通知|产品整合 / 迁移安排|
|2026\.10\.29|扣子企业版下线公告（不是全站关停）|Workflow / Builder 产品线调整|

---

## 参考资料（我用来核对时间线的链接）

### 早期 ChatGPT 与开发者工具

- [Introducing ChatGPT — OpenAI](https://openai.com/index/chatgpt/)

- [GitHub Copilot GA — GitHub Blog](https://github.blog/news-insights/product-news/github-copilot-now-generally-available/)

- [Introducing Function Calling — OpenAI](https://openai.com/index/function-calling-and-other-api-updates/)

- [GitHub Copilot is generally available — GitHub Blog](https://github.blog/news-insights/product-news/github-copilot-general-availability/)

- [Function calling and other API updates — OpenAI](https://openai.com/index/function-calling-and-other-api-updates/)

- [Aider 项目历史 — GitHub](https://github.com/Aider-AI/aider/blob/main/HISTORY.md)

### AI IDE、Coding Agent 与 Workflow

- [Cursor 官网](https://cursor.com/)

- [Introducing Devin — Cognition](https://www.cognition.ai/blog/introducing-devin)

- [Replit Agent — Replit Blog](https://blog.replit.com/agent)

- [Windsurf 官网](https://windsurf.com/)

- [TRAE 2025 Yearly Review](https://www.trae.ai/blog/trae_2025_yearly_review)

- [CodeBuddy Code CLI 发布 — 腾讯云开发者社区](https://developer.cloud.tencent.com/article/2566993)

- [Introducing Google Antigravity — Google](https://antigravity.google/blog/introducing-google-antigravity)

- [Claude Code / Claude 3\.7 Sonnet — Anthropic](https://www.anthropic.com/news/claude-3-7-sonnet)

- [Introducing Codex CLI — OpenAI API Changelog](https://developers.openai.com/api/docs/changelog)

- [Introducing Codex Cloud — OpenAI](https://openai.com/index/introducing-codex/)

- [Codex is now generally available — OpenAI](https://openai.com/index/codex-now-generally-available/)

- [Introducing Deep Research — OpenAI](https://openai.com/index/introducing-deep-research/)

- [Introducing ChatGPT Agent — OpenAI](https://openai.com/index/introducing-chatgpt-agent/)

- [Introducing ChatGPT Work — OpenAI](https://openai.com/index/chatgpt-for-your-most-ambitious-work/)

- [Dify Workflow Studio](https://dify.ai/zh/workflows)

- [Coze 国内版上线公告 — 火山引擎](https://developer.volcengine.com/articles/7330248590764703798)

- [n8n 官方文档](https://docs.n8n.io/)

### 2026 通用工作 Agent 与 Harness

- [Introducing the Codex app — OpenAI](https://openai.com/index/introducing-the-codex-app/)

- [Claude Cowork 官方教程](https://academy.claude.com/tutorials/get-started-in-claude-cowork-in-three-steps)

- [OpenClaw 起源说明 — 官方文档](https://docs.openclaw.ai/zh-CN/start/lore)

- [OpenClaw 官方文档](https://docs.openclaw.ai/)

- [WorkBuddy 官方产品页 — 腾讯云](https://cloud.tencent.com/act/pro/workbuddy)

- [WorkBuddy 2026 年 3 月上线相关报道](https://stock.stockstar.com/SS2026090700013763.shtml)

- [DuMate 官方产品文档](https://aca.bce.baidu.com/doc/Dumate/index.html)

- [DuMate 正式上线 — 百度智能云千帆社区](https://qianfan.cloud.baidu.com/qianfandev/topic/687919)

- [豆包工作正式发布 — 新华网](https://www3.xinhuanet.com/tech/20260825/1c13b806a0a946a9981e95f0c238e98c/c.html)

- [豆包工作正式发布 — 北京日报](https://xinwen.bjd.com.cn/content/s6a8d7d41e4b03fa51a835e97.html)

- [Qoder 1\.0 官方发布说明](https://qoder.com/zh/blog/qoder-1.0)

- [QoderWork 下线通知 — Alibaba Cloud](https://www.alibabacloud.com/zh/notice/product_change_feature_discontinuation_announcement_for_qoderwork_86e?_p_lc=1)

- [QoderWork / 悟空 / MuleRun 整合报道 — IT之家](https://www.ithome.com/0/971/554.htm)

- [DeepSeek Harness 官方页面](https://www.deepseek.com/en/harness/)

- [DeepSeek Harness GitHub](https://github.com/deepseek-ai/deepseek-harness)

- [DeepSeek Harness 官方主页](https://www.deepseek.com/harness/en/)

- [Introducing Cline SDK — Cline](https://cline.bot/blog/introducing-cline-sdk-the-upgraded-agent-runtime)

- [扣子产品动态 — 官方文档](https://docs.coze.cn/guides_release_note)

- [扣子企业版下线公告报道 — 澎湃新闻](https://www.thepaper.cn/newsDetail_forward_34431810)

- [扣子 2\.0 相关报道](https://www.aitntnews.com/newDetail.html?newId=21756)
