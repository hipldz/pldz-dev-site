---
author: "hipldz"
category: "agent-architecture"
csdn: ""
date: "2026-11-10"
gitee: ""
github: ""
juejin: ""
serialNo: 3
status: publish
summary: "结合 Anthropic、OpenAI 的原文及基因组 QC 示例，比较 Workflow 与 Agent 的决策边界、适用场景和混合架构。"
tags:
  - "AI Agent"
  - "Workflow"
  - "Agent Architecture"
  - "Hybrid"
thumbnail: "/api/v1/website/image/agent-architecture/workflow-vs-agent-cover.webp"
title: "Workflow 和 Agent"
---

## Workflow vs Agent：到底是谁在决定下一步？

![Workflow 与 Agent 主题插图](/api/v1/website/image/agent-architecture/workflow-vs-agent-figure-01.webp@original)

## 我个人现在的理解的总结哈

- **Workflow：** 主要执行路径和控制结构，通常由开发者在设计时规定好。

- **Agent：** 模型在运行时，根据目标、当前状态和工具返回结果，动态决定接下来做什么。

> Workflow 和 Agent 不是老和新的技术的关系，也不是一个有 LLM、一个没有 LLM。
>
>
>
> 一个 Workflow 完全可以有 LLM 节点、条件判断、循环、重试、并行分支；一个 Agent 也可以被放进 Workflow 里，替其中某一步做判断和执行。
>
>
>
> 不是说 Agent 想干什么就干什么。工具范围、权限、最大迭代次数、审批点、停止条件，仍然需要工程系统来约束。
>
>

## 1\. 两篇原文

### Anthropic：Building effective agents（2024\-12\-19）

这是我认为讲 Workflow vs Agent 最直接的一篇。Anthropic 在文章里先承认 Agent 这个词有不同用法：有的人说的是长时间自主运行的系统，有的人把遵循预定义流程的实现也叫 Agent。然后它给了一个架构层面的区分：

> “Workflows are systems where LLMs and tools are orchestrated through predefined code paths\.”
>
>

Anthropic 不是说 Workflow 里不能有模型，而是说模型和工具主要沿着预先编排好的代码路径运行。它甚至把 Workflow 和 Agent 都放在更大的 agentic systems（Agentic 系统）范围里，只是在架构层面把两者区分开。

它对 Agent 的描述则是：**模型会动态地控制自己的过程和工具使用**，并保留对任务完成方式的控制权。

原文还给了一个很实用的建议：不要一开始就上复杂 Agent。对于步骤明确的任务，Workflow 往往更可预测；当任务需要灵活性和模型驱动的决策时，再考虑 Agent。Agentic 系统通常要拿延迟和成本换任务表现，而且错误可能逐步累积。

**原文链接：** [Building effective agents — Anthropic](https://www.anthropic.com/research/building-effective-agents)

补一句：Anthropic 在这篇文章顶部专门提示，2024 年底的工具生态已经变化，今天要看它们当前的托管式方案，应继续读 [Claude Managed Agents](https://www.anthropic.com/research/managed-agents) 和 [Managed Agents 文档](https://platform.claude.com/docs/en/managed-agents/overview)。所以这篇主要拿来理解架构概念，不把里面当年的 SDK 选型当成今天的最新推荐。

建议重点读：

- `What are agents?`

- `When (and when not) to use agents`

- `Building blocks, workflows, and agents`

- `Combining and customizing these patterns`

### OpenAI：A practical guide to building agents（2026\-01\-15）

OpenAI 这篇从产品和工程团队的角度讲得更直接。它把 Workflow 说成完成目标所需的一系列步骤，而 Agent 是能够代表用户独立完成任务的系统。

原文里有一句很短、但很适合拿来做定义的话：

> “Agents are systems that independently accomplish tasks on your behalf\.”
>
>

OpenAI 进一步给了两个判断条件：

1. LLM 要负责管理 Workflow 的执行并作出决策；它需要判断何时完成、必要时修正动作，失败时也能停止并把控制权交还给用户。

2. Agent 能使用外部工具获取上下文或采取行动，并根据 Workflow 当前状态动态选择工具，同时遵守明确的 guardrails。

所以 OpenAI 的说法不是「Workflow 不重要」。恰恰相反，它把 Agent 描述成能够代表用户执行 Workflow 的系统。这里的重点是：**LLM 是否参与控制 Workflow 的执行过程。**

**它还提醒：如果一个确定性的方案已经够用，就没必要为了追 Agent 热点硬上 Agent。**

**原文链接：** [A practical guide to building agents — OpenAI](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/)

建议重点读：

- `What is an agent?`

- `When should you build an agent?`

- `Orchestration`

- `Guardrails`

---

## 2\. 把两家的说法放在一起

|问题|Anthropic 的表达|OpenAI 的表达|
|---|---|---|
|Workflow 是什么？|LLM 和工具沿预定义代码路径编排|为达成目标而执行的一系列步骤|
|Agent 是什么？|LLM 动态控制自己的过程和工具使用|LLM 管理 Workflow 执行、作决策、动态选工具|
|什么时候用 Workflow？|任务容易拆成固定步骤，需要可预测性和一致性|规则明确、确定性方案足够时|
|什么时候用 Agent？|步骤数量难预估，路径无法提前写死|复杂判断、规则难维护、大量非结构化数据|
|代价是什么？|延迟、成本、错误累积和安全风险|复杂度、可靠性、成本、延迟与安全约束|

两篇文章的表述角度不完全一样：Anthropic 更像是在比较两种系统架构；OpenAI 更像是在解释 Agent 如何替用户执行 Workflow。但它们的交集很清楚：**Agent 的关键不是“用了 LLM”，而是 LLM 是否拿到了运行时的决策权。**

![Anthropic 与 OpenAI 对 Workflow 和 Agent 的定义对比](/api/v1/website/image/agent-architecture/workflow-vs-agent-figure-02.webp@original)

## 3\. Workflow 也可以很聪明

如果把 Workflow 理解成一条从头走到尾、完全不能分支的直线，就太简单了。

Anthropic 在《Building effective agents》里列了五种常见的 Workflow 组织模式。这张图我按原文整理了一下：

![五种常见 Workflow 组织模式](/api/v1/website/image/agent-architecture/workflow-vs-agent-figure-03.webp@original)

### 3\.1 Prompt chaining：把任务拆成几段

比如：先生成提纲，再检查提纲，最后根据提纲写正文。每一步的输出交给下一步，也可以在中间加程序化检查。

![Prompt chaining 提示链模式](/api/v1/website/image/agent-architecture/workflow-vs-agent-figure-04.webp@original)

[Prompt chaining 原图](https://www-cdn.anthropic.com/images/4zrzovbb/website/7418719e3dab222dccb379b8879e1dc08ad34c78-2401x1000.png)

适合能清楚拆成固定子任务的工作。

### 3\.2 Routing：先分类，再分流

![Routing 分类与分流模式](/api/v1/website/image/agent-architecture/workflow-vs-agent-figure-05.webp@original)

[Routing 原图](https://www-cdn.anthropic.com/images/4zrzovbb/website/5c0c0e9fe4def0b584c04d37849941da55e5e71c-2401x1000.png)

例如客服问题先分类，再进入退款、技术支持、普通咨询等不同流程。

分类器可以是传统分类模型，也可以是 LLM。重点是后续分支在设计时已经准备好了。

### 3\.3 Parallelization：并行处理，再汇总

![Parallelization 并行处理与汇总模式](/api/v1/website/image/agent-architecture/workflow-vs-agent-figure-06.webp@original)

[Parallelization 原图](https://www-cdn.anthropic.com/images/4zrzovbb/website/406bb032ca007fd1624f261af717d70e6ca86286-2401x1000.png)

Anthropic 把它分成两种：

- Sectioning：把一个任务拆成多个互相独立的子任务并行跑。

- Voting：让多个模型或多个 Prompt 独立完成同一件事，再汇总或投票。

### 3\.4 Orchestrator\-workers：编排者动态拆任务

![Orchestrator-workers 编排者与工作者模式](/api/v1/website/image/agent-architecture/workflow-vs-agent-figure-07.webp@original)

[Orchestrator\-workers 原图](https://www-cdn.anthropic.com/images/4zrzovbb/website/8985fc683fae4780fb34eab1365ab78c7e51bc8e-2401x1000.png)

这个模式最容易让人困惑。一个中心 LLM 先分析任务，再动态拆出子任务，交给 Worker，最后把结果综合起来。

注意：Anthropic 仍然把它放在 Workflow patterns 这一节里。也就是说，**“子任务是动态生成的”并不自动意味着整个系统就一定要被归为 Agent。** 还要看系统的外层控制结构是什么、模型在多大范围内控制执行。

### 3\.5 Evaluator\-optimizer：生成、评估、再修改

![Evaluator-optimizer 评估与优化模式](/api/v1/website/image/agent-architecture/workflow-vs-agent-figure-08.webp@original)

[Evaluator\-optimizer 原图](https://www-cdn.anthropic.com/images/4zrzovbb/website/14f51e6406ccb29e695da48b17017e899a6119c7-2401x1000.png)

一个 LLM 先生成结果，另一个 LLM 按照标准评估并给反馈，再回到生成环节迭代。

如果有比较清晰的评价标准，而且迭代确实能改善结果，这个模式就很有用。

**Anthropic 原文里的五种模式不是“Workflow 的完整定义”，而是常见的组织方式。** 实际系统可以组合它们，也可以在某个节点里嵌入 Agent。

---

## 4\. 什么时候 Workflow 更合适，什么时候考虑 Agent？

我会先问几个很实际的问题，而不是先问“这个应用要不要做成 Agent”。

![Workflow 与 Agent 的适用场景对比](/api/v1/website/image/agent-architecture/workflow-vs-agent-figure-09.webp@original)

### Workflow 通常更合适的情况

- 输入、处理步骤、输出都比较明确。

- 规则和阈值需要固定，且必须可追溯。

- 任务重复率高，流程要稳定运行。

- 操作成本、时延和合规要求比较严格。

- 出错时希望走明确的 fallback，而不是让模型自由探索。

### Agent 更值得考虑的情况

- 任务目标清楚，但具体步骤和数量事先难以确定。

- 需要从非结构化信息里判断下一步。

- 可能遇到各种例外，规则表越写越复杂。

- 执行中需要根据新发现调整搜索方向或工具。

- 任务价值足够高，能覆盖额外的模型调用、时间和验证成本。

Anthropic 特别提醒 Agent 会带来更高的成本和错误累积风险；OpenAI 也建议先验证用例是否真的需要模型来管理执行，否则确定性方案可能就够了。

换句话说：**Agent 不是 Workflow 的升级版，Agent 是在某些任务里值得付出成本的一种执行方式。**

## 5\.举个工程的例子🌰：基因组 QC

假设现在有 30 个细菌基因组组装文件，要跑 QC 并输出报告。

### 纯 Workflow

```text
输入 FASTA
  → 格式与完整性检查
  → QUAST / BUSCO
  → 解析指标
  → 按预设阈值判断
  → 输出 QC 表格和报告
```

这个流程很适合 Workflow。因为工具、指标、阈值和报告格式通常应该固定。N50 计算、contig 数量统计、总长度这些也不应该交给 LLM 凭感觉判断。

### Agent 负责全部 QC？我觉得不一定

如果让 Agent 自己决定跑什么工具、怎么判断质量、哪些样本合格，反而可能引入不可重复性。科研分析尤其需要方法透明、参数固定、结果可复现。

但如果任务改成：

> 先按标准流程跑完 QC。对于失败样本，结合日志和指标异常，判断可能原因，并决定需要补充哪些诊断信息。
>
>

这时 Agent 就有用武之地了。

### Hybrid：固定主干 \+ Agent 处理例外

![固定 QC 流程与 Agent 异常诊断的混合架构](/api/v1/website/image/agent-architecture/workflow-vs-agent-figure-10.webp@original)

我觉得这是很多真实系统更可能采用的方案：

1. Workflow 负责固定、可复现的标准 QC 主流程。

2. 规则节点找出失败或异常样本。

3. Agent 读取日志和已有指标，选择合适的补充检查，提出可能原因。

4. 如果涉及安装软件、覆盖文件、提交任务等有风险的操作，再让人确认。

5. 最后把确定性指标、Agent 的诊断过程和证据一起放进报告。

这就不是“Workflow 还是 Agent”的二选一了。

---

## 6\.  Hybrid的产品例子

我特意看了 Dify 和 n8n 的官方文档，发现这一类的产品层面也没有把两者做成互斥关系。

### Dify：Agent 可以直接作为 Workflow 的一个节点

Dify 的 Agent 节点文档写得很直白：可以在 Workflow 中运行一个 Agent，让它在该步骤内推理、使用工具，再把结果交还给后续节点。Agent 可以根据自己的结论选择输出路线；如果只是判断一个明确数值阈值，文档仍建议用 IF/ELSE。当前文档还区分 Classic Agent 和 New Agent；New Agent 节点处于 Beta，所以看产品功能时要留意版本状态。

这其实是很好的产品例子：**固定流程负责大结构，Agent 负责局部需要动态判断的工作。**

![Dify Workflow 中添加 Agent 节点](/api/v1/website/image/agent-architecture/workflow-vs-agent-figure-11.webp@original)

图: 在dify里添加agent节点

- [Dify Agent Node 官方文档](https://docs.dify.ai/en/use-dify/nodes/agent)

- [Dify Workflow Studio](https://www.dify.ai/workflows)

### n8n：AI Agent Node 本身就是放在 Workflow 里的

n8n 的 AI Agent 节点要求连接 Chat Model 和至少一个 Tool；Agent 根据任务决定调用哪些工具。它不是把 n8n Workflow 整个替换掉，而是在自动化流程里提供一个可以动态选工具的节点。当前文档还注明，较早版本的 Agent type 设置已弃用，现在的节点统一按 Tools Agent 工作。

![n8n Workflow 中的 AI Agent 节点](/api/v1/website/image/agent-architecture/workflow-vs-agent-figure-12.webp@original)

- [n8n AI Agent 官方文档](https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-langchain.agent/)

### Coze：Workflow 也可以服务 Agent

Coze 的 Workflow 文档把 Workflow 描述为一组可执行的业务逻辑步骤，用于应用或 Agent 的数据流和任务处理。它同时区分 Workflow 与 Chatflow：前者偏功能型任务的节点执行，后者偏对话场景。

- [Coze Workflow 官方文档](https://docs.coze.com/guides/workflow)

这些产品文档不是理论定义，但能说明一个事实：在实际产品里，Agent 和 Workflow 往往是嵌套、组合的关系。

---

## 7\. Anthropic 和 OpenAI 的真实 Agent 系统

前面两篇是概念与工程指南。下面几篇更像真实系统的拆解，我觉得值得接着读。

### Anthropic：How we built our multi\-agent research system（2025\-06\-13）

这篇很值得看，原因是它不是只画一个 Agent Loop，而是讲 Claude Research 背后的多 Agent 架构。

它采用 orchestrator\-workers：一个 Lead Agent 先理解问题、制定研究策略，再创建多个 Subagent 并行搜索。子 Agent 返回结果后，Lead Agent 会判断是否还需要继续研究；最后还会交给 Citation Agent 处理引用定位。

Anthropic 还披露了一些很有意思的工程数据：在他们自己的内部 research eval 上，Opus 4 Lead \+ Sonnet 4 Subagents 的多 Agent 系统比单个 Opus 4 高 90\.2%。但不要把这个数字理解成“多 Agent 普遍提升 90%”，它是特定任务、特定内部评测和特定架构下的结果。

成本也很实在：文章说他们的 Agent 通常比普通 Chat 交互多用约 4 倍 Token，多 Agent 系统约 15 倍。适合高度并行、信息量超出单个上下文、工具复杂且任务价值较高的研究工作；并不是所有任务都应该多 Agent 化。

原文还提到，多 Agent 评估不能只检查是否走过一条固定路径，因为不同 Agent 可能用不同的有效路径抵达目标。评估需要更多看结果是否正确、完整、来源是否可靠，以及过程是否合理。

**原文链接：** [How we built our multi\-agent research system — Anthropic](https://www.anthropic.com/research/multi-agent-research-system)

建议重点读：

- `Benefits of a multi-agent system`

- `Architecture overview for Research`

- `Prompt engineering and evaluations for research agents`

- `Production reliability and engineering challenges`

### OpenAI：Deep research System Card（2025\-02\-25）

这份 System Card 不是 Workflow vs Agent 的定义文章，但它给了一个具体 Agent 产品的能力和风险边界。

Deep Research 会多步搜索、阅读网页和 PDF、解释信息、根据新发现调整方向，也可以读取用户文件并运行 Python 做数据分析。OpenAI 同时专门评估了 Prompt Injection、隐私、代码执行、幻觉等风险。

我觉得这份材料的重要性在于：一旦 Agent 能读取外部内容并且采取行动，安全问题就不是一个可有可无的附加项了。网页里的恶意指令可能试图改变 Agent 行为；用户文件和工具权限也需要隔离与限制。

**原文链接：** [Deep research System Card — OpenAI](https://openai.com/index/deep-research-system-card/)

也可以直接读 PDF：[Deep Research System Card PDF](https://cdn.openai.com/deep-research-system-card.pdf)

### OpenAI：New tools for building agents（2025\-03\-11）

这篇讲的是 OpenAI 为什么推出 Responses API、内置 Web Search / File Search / Computer Use，以及 Agents SDK。

它点出了一个实际开发痛点：模型已经能推理、能调用工具，但把它变成生产可用的 Agent，仍需要大量 Prompt 迭代、自定义编排逻辑，而且缺少可观察性。

Responses API 把多次模型调用、工具使用和 item\-based 输出放到一个更统一的接口里；Agents SDK 则负责单 Agent 和多 Agent 的编排，并提供 tracing / observability。

**原文链接：** [New tools for building agents — OpenAI](https://openai.com/index/new-tools-for-building-agents/)

### OpenAI：ChatGPT agent System Card（2025\-07\-17）

它把 Deep Research 的多步研究能力、Operator 的远程视觉浏览器操作、Terminal 里的代码执行与数据分析，以及 Connectors 连接外部应用整合到一个 Agent 产品中。

这可以用来理解产品形态的变化：Agent 不只是搜索，也不只是一个聊天窗口，而是开始在不同工具和执行环境之间完成任务。

**原文链接：** [ChatGPT agent System Card — OpenAI](https://openai.com/index/chatgpt-agent-system-card/)

---

## 8\. 我觉得最容易被忽略的结论

Workflow 和 Agent 的分界，不是有没有循环、有没有条件节点、有没有 LLM，更不是看画布上有多少个 Node。

一个 Workflow 可以有循环、动态路由、并行 Worker、Evaluator；一个 Agent 也会被放进一个更大的 Workflow 里。

如果要判断一个系统的核心执行方式，我会问：

1. 主执行路径是不是由开发者预先规定？

2. 模型能否根据当前状态选择下一步工具或行动？

3. 模型的决策范围有多大？是只选一个分支，还是能规划并反复调整任务？

4. 执行边界、权限、终止条件和人工审批由谁控制？

所以更准确的说法可能是：

**Workflow 关注如何组织一组步骤；Agent 关注谁在执行过程中决定下一步。**

而实际生产系统通常是两者一起用：确定性部分交给 Workflow，开放式判断和例外处理交给 Agent。

这篇先停在这里。下一篇再往下拆：如果 Agent 能在运行时决定下一步，那它到底怎么运行？一次完整执行怎么被组织成 Turn、Step、Item、Event？这些东西就是 Agent Runtime 要解决的问题了。

---

## 原始资料清单

### Workflow vs Agent 的定义与取舍

1. **Anthropic — Building effective agents**（2024\-12\-19）

https://www\.anthropic\.com/research/building\-effective\-agents

最直接的架构定义；五种 Workflow 模式；何时不该使用 Agent。

2. **OpenAI — A practical guide to building agents**（2026\-01\-15）

https://openai\.com/business/guides\-and\-resources/a\-practical\-guide\-to\-building\-ai\-agents/

从工程实践解释 Agent 如何管理 Workflow 执行、动态选工具、单 Agent / 多 Agent 编排和 Guardrails。

### 真实 Agent 系统拆解

3. **Anthropic — How we built our multi\-agent research system**（2025\-06\-13）

https://www\.anthropic\.com/research/multi\-agent\-research\-system

Lead Agent、Subagents、并行搜索、评估、成本和生产可靠性。

4. **OpenAI — Deep research System Card**（2025\-02\-25）

https://openai\.com/index/deep\-research\-system\-card/

一个研究型 Agent 如何搜索、分析、调整方向，以及它的安全风险。

5. **OpenAI — ChatGPT agent System Card**（2025\-07\-17）

https://openai\.com/index/chatgpt\-agent\-system\-card/

Deep Research、浏览器操作、Terminal 和 Connectors 的组合。

### 工程实现与下一篇 Runtime 的桥梁

6. **OpenAI — New tools for building agents**（2025\-03\-11）

https://openai\.com/index/new\-tools\-for\-building\-agents/

Responses API、Agents SDK、内置工具、Tracing 和可观察性。

7. **Anthropic — Effective harnesses for long\-running agents**（2025\-11\-26）

https://www\.anthropic\.com/research/effective\-harnesses\-for\-long\-running\-agents

多个 Context Window 之间如何交接，Initializer Agent、Coding Agent、进度文件、Git 和测试。

8. **OpenAI — Harness engineering: leveraging Codex in an agent\-first world**（2026\-02\-11）

https://openai\.com/index/harness\-engineering/

当人类从写代码转向设计环境、规范意图、搭反馈回路时，工程团队的工作会怎样变化。

9. **Anthropic — Harness design for long\-running application development**（2026\-03\-24）

https://www\.anthropic\.com/research/harness\-design\-long\-running\-apps

Planner / Generator / Evaluator 三 Agent 结构，长任务的上下文重置、评估器和迭代反馈。

10. **Anthropic — Scaling Managed Agents: Decoupling the brain from the hands**（2026\-04\-08）

https://www\.anthropic\.com/research/managed\-agents

Managed Agents 如何把 Agent（brain/harness）、Session（事件日志）和 Environment / Sandbox（hands）拆开；很适合作为下一篇 Agent Runtime 的预习。

### 看 Workflow 和 Agent 如何组合

10. **Dify — Agent Node**

https://docs\.dify\.ai/en/use\-dify/nodes/agent

11. **Dify — Workflow Studio**

https://www\.dify\.ai/workflows

12. **n8n — AI Agent node**

https://docs\.n8n\.io/integrations/builtin/cluster\-nodes/root\-nodes/n8n\-nodes\-langchain\.agent/

13. **Coze — Workflow overview**

https://docs\.coze\.com/guides/workflow
