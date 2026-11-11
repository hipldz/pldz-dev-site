---
author: "hipldz"
category: "agent-architecture"
csdn: ""
date: "2026-11-10"
gitee: ""
github: ""
juejin: ""
serialNo: 1
status: publish
summary: "从 ChatGPT、工具调用和 Workflow 的演化出发，结合基因组质量评估示例，理解 AI Agent 的核心组成、执行循环与运行时决策。"
tags:
  - "AI Agent"
  - "ChatGPT"
  - "Tool Calling"
  - "Workflow"
thumbnail: "/api/v1/website/image/agent-architecture/chatgpt-to-agent-cover.webp"
title: "Agent-2026程序员都得掌握的一个技能"
---

## Coze散场了？回顾一下从2022的ChatGPT到2026的Agent


<iframe
  src="https://player.bilibili.com/player.html?isOutside=true&aid=117594879166372&bvid=BV1gUWV6nE3k&cid=43501093884&p=1"
  title="B站视频"
  style="display: block; width: 100%; aspect-ratio: 16 / 9; border: 0;"
  scrolling="no"
  allowfullscreen
></iframe>


最近字节跳动的Coze宣布要下线了\(2026\-10\-27\)

![Coze 下线相关公告截图](/api/v1/website/image/agent-architecture/chatgpt-to-agent-figure-01.webp@original)

乍一看还是蛮感慨的，从2022年11月的GPT3\.5炸裂出世，到现在26年11月无人不谈的AI Agent, 整个软件行业都在被AI不断的洗牌，X上有个Coze的内部工程师的帖子也很值得一读

![Coze 工程师关于产品演化的帖子](/api/v1/website/image/agent-architecture/chatgpt-to-agent-figure-02.webp@original)

也就是随着模型能力的不断进步提升, 现在AI Agent可能才是个趋势。

倒不如借着这个机会，聊一聊ChatGPT到AI Agent的我的个人了解。

毕竟学习AI Agent, 才能用好 AI Agent\(呜呜呜 别淘汰我，我学还不行吗 😭🥲\)

## 二、产品演化速览：2022 → 2026

![ChatGPT、Tool Use、Workflow 与 Agent 的能力演化](/api/v1/website/image/agent-architecture/chatgpt-to-agent-figure-03.webp@original)

*图 1｜关键能力的叠加：ChatGPT → Tool Use → Workflow → Agent。图中年份是产品演化分段，并不意味着技术被替代。*

|时间|代表性变化|用户体验的变化|背后的关键能力|
|---|---|---|---|
|**2022 年末**|ChatGPT（GPT\-3\.5）走向大众|从「搜索信息」变成「与模型讨论问题」|指令跟随、对话上下文、自然语言生成|
|**2023**|ChatGPT Plugins、Code Interpreter、Function Calling；早期 Agent 实验|模型开始能查询数据、运行代码、调用外部服务|**Tool Use / Function Calling**|
|**2023—2024**|以 Dify、Coze 等为代表的 LLM 应用构建平台；n8n 等自动化平台积极引入 AI|用户可以把模型、知识库、条件判断、API 连接成可复用应用|**Workflow Orchestration**|
|**2025—2026**|Deep Research、Codex、ChatGPT agent 等更成熟的任务型产品|用户交代一个目标，系统可能连续执行多个步骤后交付成果|**Agent Loop \+ Runtime \+ 安全约束**|

**注意：这不是严格的行业年代表。GPT说** Workflow 远早于大模型；早期自主 Agent 也已在 2023 年出现。今天，Chatbot、Workflow 与 Agent 都是并存的，这一点 还是必须知道的好 👀。

### 产品的三个感觉

- **Chatbot：**「你问我答。」

- **Workflow：**「我把一套流程搭好，让系统自动执行。」

- **Agent：**「我说清目标与约束，由系统根据进展选择行动。」

---

## 三、起点：2022 年的 ChatGPT，本质上是什么？

ChatGPT 的旧版本（web端的那种， 我怎么感觉看着都像是上个时代的东西了，AI发展真是太快了，恍如隔世） 是把强大的语言模型包装成普通用户可以持续交互的**对话产品，所以取名字就是Chat\-GPT\.**

![早期 ChatGPT 经典界面](/api/v1/website/image/agent-architecture/chatgpt-to-agent-figure-04.webp@original)

*图 2｜早期 ChatGPT 经典界面（2023 年 1 月的历史截图）：Examples、Capabilities、Limitations。图源：*[*SUPERJUMP*](https://www.superjumpmagazine.com/i-tried-creating-a-game-using-openai/)*。*

### 3\.1 最小交互模型

**用户消息 → 模型推理与生成 → 助手回复**

从技术上说，模型接收当前输入和可用的对话上下文，逐 token 预测并生成输出。经过指令微调和人类反馈等训练后，它可以较好地遵循用户要求、解释概念、分析文本、写代码。

但是，小伙伴们，生成「正确的执行方案」与「真的把方案执行完」是两回事。

### 3\.2 一个具体例子：微生物基因组质量评估

你问早期 ChatGPT：

> 「我有一批细菌基因组组装结果，请完成质量评估，找出异常样本并生成报告。」
>
>

它通常可以提供：

- 推荐的指标：总长度、contig 数量、N50、完整度、污染度等；

- 工具建议：QUAST、BUSCO 或其他适合的质量评估工具；

- Shell/Python 脚本与报告模板。

但在没有文件访问和执行工具的情况下，它**没有真正读取 FASTA、运行命令、检查错误日志、生成结果文件**。

这就暴露了 Chatbot 的核心边界：**它可以告诉你如何完成任务，但外部操作依然依赖人。**

> **关键区分：**「模型能推理出下一步」不等于「系统能执行下一步」。
>
>

---

## 四、第一次关键跨越：从生成文本到调用工具 \(function calling出来了\)

2023 年，Plugins、Code Interpreter 和 Function Calling 等能力让大众更直观地看到：模型不仅能输出自然语言，还可以参与外部工具调用。

![模型请求、工具执行与反馈闭环](/api/v1/website/image/agent-architecture/chatgpt-to-agent-figure-05.webp@original)

*图 3｜变化不只是回答更准确，还多了个小闭环:  “模型请求 → 执行环境 → 工具结果 → 模型继续”。*

### 4\.1 Function Calling 改变了什么？

模型可以在适当时机生成一个**结构化工具调用请求**，例如：

```json
{
  "tool": "run_quast",
  "arguments": {
    "assembly_path": "samples/S01.fasta"
  }
}
```

这还不是运行命令本身。实际过程是：

1. 应用向模型描述可用工具及其参数格式。

2. 模型根据上下文决定是否请求某个工具。

3. **外部执行环境**校验参数、权限并调用工具。

4. 工具返回结果或错误。

5. 模型读取结果，继续回答，或决定进一步操作。

**模型负责提出调用意图；执行系统负责真正调用工具。** 这是理解后续  AI Agent 的第一块地基。

### 4\.2 「会调用工具」还不等于「完整的 Agent」？

一次工具调用可能只解决一个局部问题。真正的复杂任务往往需要：

- 多个步骤之间的依赖关系；

- 中间状态和历史结果；

- 失败重试与异常处理；

- 对下一步动作的选择；

- 权限、成本、次数与终止条件。

于是问题从「模型能不能用工具」升级为：**谁来组织整个执行过程？**

---

## 五、Workflow：把 LLM 变成可复用的业务流程

Workflow（工作流）并不是大模型时代发明的。传统自动化系统早就可以在预先定义的流程中连接 API、数据库、定时任务和条件判断。LLM 的出现，让「调用模型」成为工作流里的一个常见节点。

### 5\.1 Workflow 的技术直觉

**Workflow = 节点（Node） \+ 连线（Edge） \+ 条件与状态 \+ 执行引擎**

![基因组 QC Workflow 流程](/api/v1/website/image/agent-architecture/chatgpt-to-agent-figure-06.webp@original)

*图 4｜一条可复用的基因组 QC Workflow：不同节点按预先设计的关系运行。*

以「对一批基因组组装结果生成 QC 报告」为例，可以设计一个流程：

**接收 FASTA → 运行 QC 工具 → 解析指标 → 判断阈值 → LLM 生成解释 → 输出报告**

流程设计者提前规定主要步骤与连接关系。执行时可以存在 `if/else`、循环、重试，甚至让某个 LLM 节点决定局部分支，但整体框架通常是可视化或代码预先声明的。

### 5\.2 代表性产品（不是互斥的类别）

**n8n：通用自动化平台中的节点式编排**

![n8n 工作流编辑器](/api/v1/website/image/agent-architecture/chatgpt-to-agent-figure-07.webp@original)

*图 5｜n8n 工作流编辑器真实界面。图源：*[*n8n Community*](https://community.n8n.io/t/how-to-create-a-staging-copy-of-an-n8n-workflow-before-going-live/293744)*。*

**Dify：为 LLM 应用编排模型节点和数据流**

![Dify 模型节点编排示例](/api/v1/website/image/agent-architecture/chatgpt-to-agent-figure-08.webp@original)

*图 6｜Dify 官方示例：Start → LLM → LLM 2 的视觉流程。图源：*[*Dify 官方文档*](https://docs.dify.ai/ja/cloud/use-dify/nodes/llm)*。*

**Coze：AI 应用工作流中的节点与插件选择**

![Coze 节点与插件选择界面](/api/v1/website/image/agent-architecture/chatgpt-to-agent-figure-09.webp@original)

*图 7｜Coze 官方节点编辑界面，展示可选择的插件与工作流组件。图源：*[*Coze 官方文档*](https://www.coze.cn/open/docs/guides/delete_conversation)*。*

|产品|它让什么事变得容易？|与 AI Agent 的关系|
|---|---|---|
|**n8n**|用节点连接各类应用、API、数据库和自动化任务|在成熟的自动化基础上集成 AI 与 Agent 节点|
|**Dify**|构建 LLM 应用，组合 Prompt、RAG、Workflow / Chatflow 与工具|同时支持 Agent 能力，并可将 Agent 纳入更大的流程|
|**Coze（扣子）**|用可视化方式组织 AI 应用、插件、知识和工作流等能力|属于 Agent 应用构建生态的一部分，不应仅理解为静态 Workflow 工具|

这些产品就是踩在: **降低从「一个会聊天的模型」到「一个能用于真实业务的 AI 应用」的工程门槛发力的**。

> 但要 保护保护保护：n8n、Dify、Coze 并非同一技术范式的三个同义词；它们的定位、功能及产品形态也持续变化。
>
>

### 5\.3 Workflow 解决了什么，又留下了什么？

Workflow 非常适合：

- 业务步骤相对明确、可重复；

- 合规、审计和可预测性重要；

- 数据流向及失败分支需要清楚说明；

- 希望通过可视化或明确的程序逻辑维护执行过程。

它留下的一个开放问题是：**当用户只给出目标、事先无法枚举所有步骤时，能不能让模型根据执行结果动态决定下一步？**

这个问题把我们引向 Agent。

---

## 六、Agent：从「执行一张流程图」到「围绕目标持续行动」

![ChatGPT Deep Research 任务入口](/api/v1/website/image/agent-architecture/chatgpt-to-agent-figure-10.webp@original)

*图 8｜2025 年 ChatGPT 中的 Deep Research 入口：从一次提问转向多步骤研究任务。图源：*[*Neowin*](https://www.neowin.net/news/openai-introduces-deep-research-a-new-ai-agent-that-can-complete-multi-step-research-tasks/)*。*

### 6\.1 一个实用定义

**AI Agent 是一种以模型为决策核心、能够在给定目标和约束下使用工具、观察结果，并迭代选择后续动作的系统。**

它通常包含四类元素：

1. **Goal（目标）：** 用户希望完成什么；

2. **Model（模型）：** 理解任务、判断下一步的核心决策者；

3. **Tools / Environment（工具与环境）：** 文件、浏览器、代码执行器、API 等；

4. **Loop / Runtime（执行循环与运行环境）：** 维护上下文、调度工具、接收反馈、控制终止与权限。

### 6\.2 最小的 Agent Loop

![最小 Agent Loop 执行循环](/api/v1/website/image/agent-architecture/chatgpt-to-agent-figure-11.webp@original)

*图 9｜最小 Agent Loop：目标 → 模型判断 → 工具执行 → 观察结果 → 回到模型；满足终止条件时交付。*

图中的关键不是「会循环」，而是**模型可以根据新的观察结果，动态选择工具、参数或下一步操作**。执行环境仍应对工具权限、迭代次数、敏感操作审批和失败处理设限。

### 6\.3 仍以基因组 QC 为例

![Agent 执行基因组 QC 任务的示意图](/api/v1/website/image/agent-architecture/chatgpt-to-agent-figure-12.webp@original)

如果你说：

> 「检查这 30 个样本的组装质量。遇到失败样本先排查，最后给我异常清单和可复现的分析报告。」
>
>

在有合适授权、工具和运行环境的情况下，一个 Agent 可以：

1. 检查输入目录和样本清单；

2. 选择并执行相应 QC 工具；

3. 读取输出，识别异常与失败；

4. 根据错误日志决定是否调整参数或重新运行；

5. 汇总指标、生成表格和报告；

6. 标注未解决问题及其证据。

这些操作**不是模型凭空完成的**，它们依赖真实工具、外部环境及持续的执行协调。Agent 也可能犯错，因此结果需要验证，特别是在涉及科学结论时。

---

## 七、Chatbot、Workflow、Agent 做个比较矩阵

> 注意: Workflow 也能包含 LLM、动态条件、循环、检索和 Agent 节点， Agent 可以是 Workflow 中的一个节点；Agent 内部也可以调用确定性的子流程。
>
>

|对比维度|Chatbot|Workflow|Agent|
|---|---|---|---|
|**典型输入**|一个问题或指令|触发事件与流程参数|目标、上下文与约束|
|**核心输出**|文本、代码、建议|预设流程的执行结果|完成目标所需的动作与交付物|
|**主要谁决定下一步？**|用户继续提问|流程开发者设计的节点和规则|模型在运行时进行动态决策|
|**工具使用方式**|可以没有工具；也可有工具|工具通常封装在节点中|模型可按观察结果选择工具和调用顺序|
|**处理未知分支**|依赖用户追问|依赖已配置的分支或子流程|可以尝试规划、探索与调整；仍受边界限制|
|**典型强项**|交流、解释、创作|稳定、重复、易审计|开放式、多步骤、难以预先穷举的任务|

---

## 八、最重要的技术转折：控制权发生了什么变化？

![Workflow 与 Agent 的控制权对比](/api/v1/website/image/agent-architecture/chatgpt-to-agent-figure-13.webp@original)

*图 11｜控制权差异：Workflow 的关键路径主要在设计时规定；Agent 的下一步更多在运行时根据观察动态决定。*

把上面的发展浓缩成三次变化：

|技术转折|被增加的能力|新的问题|
|---|---|---|
|**ChatGPT → Tool Use**|从「生成答案」到「请求外部操作」|谁真正执行、校验和授权？|
|**Tool Use → Workflow**|从「单次调用」到「组织多个步骤」|流程的结构由谁定义？|
|**Workflow → Agent**|从「预先编排」到「在执行中动态决策」|如何让动态决策可靠、可控、可追踪？|

这也解释了为什么 Agent 不等于「更会聊天的 Chatbot」，也不只是「节点更多的 Workflow」。

Agent 的工程难点逐步转向**如何让一连串模型决策和工具操作持续、可恢复、可观察且足够安全地运行**。这就是后续 Agent Runtime 话题的入口。

## 参考资料

- [OpenAI：Introducing ChatGPT（2022）](https://openai.com/index/chatgpt/)

- [OpenAI：Function calling and other API updates（2023）](https://openai.com/index/function-calling-and-other-api-updates/)

- [OpenAI Developers：Responses API / Building agents](https://developers.openai.com/blog/responses-api)

- [OpenAI Developers：Running agents](https://developers.openai.com/api/docs/guides/agents/running-agents)

- [n8n 官方文档](https://docs.n8n.io/)

- [Dify 官方：Agent or Workflow — How to choose](https://www.dify.ai/blog/ai-agent-or-workflow-how-to-choose-the-right-approach)

- [Coze 官方文档](https://docs.coze.cn/about-low-code-project)
