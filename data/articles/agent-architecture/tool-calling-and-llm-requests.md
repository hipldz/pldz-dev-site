---
author: hipldz
category: agent-architecture
csdn: ""
date: "2026-11-07"
gitee: ""
github: ""
juejin: ""
serialNo: 1
status: publish
summary: 从 Codex WebUI 的工具活动折叠出发，区分 Tool Call、模型 Response、API Request 与 Agent Turn，并结合 OpenAI 文档梳理 Agent Runtime 的分组和追踪方式。
tags:
  - AI Agent
  - Tool Calling
  - OpenAI
  - Agent Runtime
thumbnail: /api/v1/website/image/agent-architecture/tool-calling-response-lifecycle.webp
title: Tool Calling 和 LLM Request 是一对一的吗？
---

## 从 Codex WebUI 的工具调用折叠说起

最近给 Codex 做了 WebUI Lite 这个项目。我自己用的时候发现，工具调用记录很长，而且有些重复；再看 Codex Web 的界面，它会把工具活动折叠起来，像下面这样：

![Codex WebUI 折叠展示的工具活动摘要](/api/v1/website/image/agent-architecture/tool-calling-codex-activity-summary.webp@original)

*图：Codex WebUI 中的工具活动摘要*

这倒让我产生了一个猜想：**难道 Codex 是把大模型一次 Request 产生的 Tool Calls 放到同一个折叠容器里了？**

如果真是这样，这个折叠就不只是 UI 交互，而是把模型的执行边界暴露给了用户。后来经过多方求证（其实就是和 GPT 对线），发现事情并没有这么简单。原生 WebUI 的工具活动归纳，并不能直接理解成按照一次模型 Request 进行分组。这个 UI 细节可以留到后面单独讨论。

不过，它倒是引出了一个更值得研究的问题：**Tool Calling 和 LLM Request 到底是一对一的吗？**

## 一、先给结论：不是一对一

时间宝贵，先给结论：

- 一次模型 Response 可以包含多个 Tool Calls。
- 一次 Agent Turn 可以包含多次模型 Responses。
- 工具执行完成后，Agent 可能再次请求模型，产生下一次 Response。

简单来说：**Tool Call 是工具调用单元，Response / Generation 是模型响应单元，Turn 则是一次完整的 Agent 任务。**

先用一张图看它们的关系：

![一次 Agent Turn 中模型响应、工具调用和后续请求的关系](/api/v1/website/image/agent-architecture/tool-calling-response-lifecycle.webp@original)

*图：一次 Agent Turn 中，模型响应、工具调用和下一轮模型请求的关系*

举个例子：

用户让 Agent 分析一个项目：第一次模型调用，模型决定读取三个文件，于是在同一个 Response 中返回三个 Tool Calls，Agent 执行这三个调用，将结果交给模型，模型拿到结果后，发现还需要搜索代码，于是再次请求模型，并返回两个 Tool Calls，最后，模型再次推理，生成最终回答，整个过程可以是：

| 类型 | 次数 |
| --- | --- |
| Agent Turn | 1 |
| 模型 API 调用 / Response | 3 |
| Tool Calls | 5 |

这就是典型的 Agent Loop。

这里先约定一下术语：

- **Turn**：一次完整的用户任务周期。
- **API Request**：应用向模型服务发起的一次顶层 HTTP/API 请求。
- **Response / Generation**：模型对一次调用产生的响应。OpenAI Agents Tracing 将 Generation Span 定义为记录一次模型响应的 Span。
- **Tool Call**：模型输出中要求执行的一次工具调用。

严格说，HTTP Request 和 Response 是请求与响应两端；本文讨论分组时，会用 Response / Generation 指代模型这一轮输出。

## 二、OpenAI API：一次 Response 如何产生多个 Tool Calls？

这里以 OpenAI Responses API 为例，OpenAI 官方的 Function Calling 文档给出了一个五步流程：

![OpenAI Function Calling 的五步交互流程](/api/v1/website/image/agent-architecture/tool-calling-function-calling-flow.webp@original)

*图：OpenAI 官方 Function Calling 流程图。来源：[OpenAI Function Calling 文档](https://developers.openai.com/api/docs/guides/function-calling)。*

这个图很直观：

1. 应用向模型发送请求，并提供工具定义。
2. 模型返回 Tool Call。
3. 应用执行工具。
4. 应用将工具结果交还给模型。
5. 模型生成最终回答，或者继续提出新的工具调用。

但这里还有一个问题：一次模型响应能不能返回多个 Tool Calls？答案是**可以**。

例如，Responses API 的一个 Response 可以包含这样的输出：

```json
{
  "id": "resp_123",
  "output": [
    {
      "type": "function_call",
      "call_id": "call_001",
      "name": "read_file",
      "arguments": "{\"path\":\"a.ts\"}"
    },
    {
      "type": "function_call",
      "call_id": "call_002",
      "name": "read_file",
      "arguments": "{\"path\":\"b.ts\"}"
    }
  ]
}
```

这里不需要研究整个 JSON，就看这三个变量得了：

- `response.id`：标识整个 Response。
- `output`：模型返回的输出 Item 列表。
- `call_id`：标识具体的工具调用，后续提交工具结果时用它关联。

两个 Function Calls 的 `call_id` 不同，但它们属于同一个 `response.id`。

所以，如果我们希望知道哪些 Tool Calls 来自同一次 Responses API 响应，就可以把它们关联到同一个 Response ID。

OpenAI 官方文档还直接给出了一个包含多个 `function_call` Item 的示例，并明确说明一次模型响应可能返回零个、一个或多个函数调用。

参考：[OpenAI Function Calling — Handling function calls](https://developers.openai.com/api/docs/guides/function-calling)

## 三、不能把顶层 API Request 和模型内部执行过程混为一谈啊

上面的例子讲的是应用自己执行的 Custom Function Tools：

```text
应用发起 API Request #1
        │
        ▼
模型返回 Response #1
        ├── Tool Call A
        ├── Tool Call B
        └── Tool Call C
        │
        ▼
应用执行 A / B / C
        │
        ▼
应用发起 API Request #2，提交工具结果
        │
        ▼
模型返回 Response #2
```

但 Responses API 还支持 OpenAI 托管工具，例如 Web Search、File Search 和 Code Interpreter。

这类工具可以由平台负责执行和编排。此时，应用看到的顶层 API 调用、Response 中的输出 Item，以及平台内部发生的工具步骤，不一定是同一个统计口径。

> - 应用发起了几次顶层 HTTP/API 请求？
>
> - API 返回了几个 Response 对象？
>
> - 模型实际产生了几次 Generation？
>
> - 工具一共执行了多少次？
>
> 这些数字可能相关，但不能不加区分地互相替代。

## 四、OpenAI 官方 Tracing：直接看真实执行记录

前面主要是从 API 返回结构推导。有没有更直接的证据？有。OpenAI 的 Agents Tracing 文档就把执行过程拆成了不同的 Span：

- **Agent Span**：某个 Agent 执行的一段工作。
- **Generation Span**：一次模型响应，记录模型输入和输出。
- **Tool Span**：一次具体工具调用及其结果。

官方文档明确写到：一个 Turn 可以包含多个模型响应和工具调用；工具返回后，模型可以在新的 Generation 中继续响应。

[OpenAI Agents API 的 Tracing 文档](https://developers.openai.com/api/docs/guides/agents-api/tracing)还给出了一个具体 Trace 的例子：

**一个 Turn 中有 11 个 Generation Spans 和 10 个 Tool Spans。**

这里要注意，这 11 个 Generation Spans 分布在 root agent 和两个 subagents 之间，并不是说 root agent 自己调用了 11 次模型。

下面两张截图来自另一份 OpenAI Cookbook 示例，用于展示 Trace 时间线和 Span 详情的组织方式，与上面的计数示例不是同一份记录。

![OpenAI Cookbook 多 Agent 工作流的 Trace 时间线](/api/v1/website/image/agent-architecture/tool-calling-multi-agent-trace.webp@original)

*图：OpenAI Cookbook 展示的多 Agent Trace 时间线。来源：[Building Consistent Workflows with Codex CLI & Agents SDK](https://developers.openai.com/cookbook/examples/codex/codex_mcp_agents_sdk/building_consistent_workflows_codex_cli_agents_sdk)。这是一个归档示例，截图用于展示 Trace 的组织方式。*

再看 Span 详情：

![Trace 中单个 Span 的输入、输出与工具参数](/api/v1/website/image/agent-architecture/tool-calling-trace-span-details.webp@original)

*图：选中一个 Span 后，可以查看输入、输出和工具参数。来源同上。*

这两张图比单纯看 API JSON 更直观：同一个 Trace 里，可以有多次 `POST /v1/responses`、工具执行、Agent Handoff 等活动。它们属于同一个更大的工作流程，但不是同一个模型响应。官方 Tracing 文档也明确区分 Generation 和 Tool：Generation 记录模型输入输出，Tool Span 记录具体工具调用及结果。

参考：[OpenAI Agents API — Tracing](https://developers.openai.com/api/docs/guides/agents-api/tracing)

## 五、自己开发 Agent 时，应该怎么建模？

如果自己开发 Agent Runtime，我建议至少区分三个核心实体：

```text
Turn
  └── Generation
        └── ToolCall
```

在内部数据模型中，可以这样设计：

| 内部 ID | 职责 |
| --- | --- |
| `turn_id` | 标识一次用户任务 |
| `generation_id` | 标识一次模型响应 / 推理记录 |
| `tool_execution_id` | 标识一次工具执行记录 |

同时保留 Provider 返回的 ID：

| Provider ID | 用途 |
| --- | --- |
| `response.id` | 关联 Responses API 的 Response |
| `call_id` | 关联具体 Function Call 和 Function Call Output |
| `x-request-id` | HTTP 请求诊断和排错 |

![Agent Runtime 内部 ID 与 OpenAI Provider ID 的关联](/api/v1/website/image/agent-architecture/tool-calling-runtime-provider-ids.webp@original)

*图：内部 ID 与 OpenAI Provider ID 的关系*

这里特别提醒：`response.id` 和 HTTP Header 中的 `x-request-id` 不是一回事。前者是 Response 对象 ID，后者用于定位 HTTP 请求。

还有几个实际开发中容易踩坑的地方：

**1. 不要默认所有 Tool Calls 都必须串行执行。**

同一次模型响应中的多个独立调用，可以由 Agent Runtime 并发调度。但是否并发，最终应该由 Runtime 根据工具依赖关系和安全策略决定。

**2. Tool Result 必须关联回原始 Tool Call。**

不要依赖工具名称、数组下标或完成顺序。并发执行时，工具完成顺序可能和发起顺序不同。应使用 Provider 的 `call_id`，并在内部维护自己的执行 ID。

**3. 重试一定要考虑幂等性。**

特别是发送邮件、创建订单、付款等具有副作用的工具，不能因为 Agent 恢复执行，就把已经成功的调用再执行一遍。

**4. 把模型调用重试和工具执行重试分开记录。**

一次 SDK 调用可能发生网络重试；一次工具执行也可能有自己的重试。若要精确统计成本和执行次数，需要分别记录 attempt，而不是只记一个总数。

## 六、总结

回到最开始的问题：

**Tool Calling 和 LLM Request 是一对一的吗？**答案是：不是。

一次模型 Response 可以包含多个 Tool Calls；一次 Agent Turn 可以包含多个 Generation；而 Responses API 的托管工具还可能在一次顶层 API 调用中完成多步工具编排。

所以，如果我们要在自己的 Agent WebUI 中实现真正按照模型响应分组的 Tool Call 折叠，最直接的方式就是：

在模型调用层创建 `generation_id`，在收到响应时将 Tool Calls 关联到对应的 Generation，再由 UI 根据 `generation_id` 进行分组。

这里描述的是按模型响应分组的数据模型。Codex 原生 WebUI 中的 `Read files, ran commands` 则是可见的活动摘要；仅凭界面，不能确认它内部是否使用同样的分组边界。

把这两个概念分开，后续无论做工具调用展示、并发调度、执行追踪还是状态恢复，都会清晰很多。

---

## 参考资料

以下资料核对于 2026-11-07。

1. [OpenAI Function Calling](https://developers.openai.com/api/docs/guides/function-calling)
2. [OpenAI Agents API — Tracing](https://developers.openai.com/api/docs/guides/agents-api/tracing)
3. [OpenAI Cookbook — Building Consistent Workflows with Codex CLI & Agents SDK](https://developers.openai.com/cookbook/examples/codex/codex_mcp_agents_sdk/building_consistent_workflows_codex_cli_agents_sdk)
4. [OpenAI API Overview — Request IDs](https://developers.openai.com/api/reference/overview)
