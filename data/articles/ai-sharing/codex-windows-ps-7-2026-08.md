---
author: pldz1
category: ai-sharing
csdn: ''
date: '2026-08-07'
gitee: ''
github: ''
juejin: ''
serialNo: 1
status: publish
summary: Codex 在 Windows 上的乱码、命令异常未必是模型问题。升级 PowerShell 7，并优先使用 pwsh.exe，通常更稳，也更适合中文开发。
tags:
  - AI
  - Codex
thumbnail: /api/v1/website/image/ai-sharing/codex-ps-7-26-08-thumbnail.webp
title: Windows 上的 Codex，问题不一定都在 Codex
---


# Windows 上的 Codex，问题不一定都在 Codex


最近 Coding Agent 确实越来越火，Codex 这种工具也从“看看它能不能写两段代码”，慢慢变成真的有人拿它读项目、改文件、跑测试、执行 Git、调用 Python。

但如果主要在 **Windows** 上用，可能会有一种很微妙的感觉：

- 怎么有些命令就是慢半拍？
- 中文文件、日志、注释偶尔会乱码？
- 同样一个命令，在终端里能跑，到了 Agent 里面行为又有点怪？
- 路径、引号、编码这些小问题，怎么总在 Windows 上冒出来？

于是很自然就会怀疑：**是不是 Codex 没吹得那么好？**

Codex 本身的能力到底应该打几分，这个话题太大，这篇先不展开。

但 Windows 上很多“不舒服”的体验，真的不一定来自模型本身。

有一层特别容易被忽略：

> **PowerShell。**

![很多时候先别急着怪 Codex，先看 PowerShell](/api/v1/website/image/ai-sharing/codex-ps-7-concept-intro.webp)

## Codex 和 PowerShell 到底是什么关系？

Codex 当然不是 PowerShell。

但 Codex 在 Windows 上真正开始“干活”以后，经常要经过 shell 去完成任务，比如：

```text
Codex
  ↓
shell / PowerShell
  ↓
git / rg / python / npm / dotnet / 各种脚本
```

例如它想做这些事：

```text
读文件
跑 git diff
搜索代码
执行测试
调用 Python
运行 npm
执行项目脚本
```

模型负责判断“要做什么”，真正把命令交给 Windows 执行的那一层，很多时候就是 shell。

而 Windows 上偏偏同时存在两个非常容易混淆的东西：

```text
powershell.exe  → Windows PowerShell 5.1
pwsh.exe        → PowerShell 7.x
```

这两个不是同一个版本换了个名字。

**Windows PowerShell 5.1 是老运行时；`pwsh.exe` 才是现在的 PowerShell 7。**

![Codex → PowerShell → CLI 工具的执行关系](/api/v1/website/image/ai-sharing/codex-ps-7-concept-relationship.webp)

这也是为什么我觉得，Windows 上经常用 Coding Agent 的人，PowerShell 7 是一个很值得顺手装上的基础环境升级。

---

## 第一个最实际的问题：UTF-8 和中文

这个不是玄学，微软自己的文档已经写得很清楚。

PowerShell 6 以及更高版本，文本输出默认使用 **UTF-8 without BOM**；而 Windows PowerShell 5.1 的编码行为要老得多。

尤其是在**没有 BOM** 的文件上，Windows PowerShell 的 `Get-Content` 等读取行为可能会使用系统默认 ANSI code page。

这对纯英文项目未必特别明显，但放到中文 Windows 环境里就比较烦了。

现在很多源码本来就是：

```text
UTF-8
UTF-8 No BOM
```

项目里再出现：

```text
中文注释
中文 README
中文日志
中文 CSV
中文路径 / 文件名
```

Windows PowerShell 5.1 就更容易出现历史编码问题。

更麻烦的是，Coding Agent 会**高频、自动地读取和写入文件**。

手工操作时偶尔一个乱码可能马上能看到；Agent 自动处理时，甚至可能出现这种情况：

```text
文件原文是正确的
        ↓
PowerShell 读取时解码错了
        ↓
Codex 收到了一份“合法但错误”的乱码文本
        ↓
模型继续基于这个错误文本做修改
```

这就比普通终端乱码更讨厌了。

微软参考：

- [about_Character_Encoding](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_character_encoding?view=powershell-7.6)

---

## 这不是只存在于理论里，Codex 自己真踩过

Codex 官方 GitHub 仓库里有一个很有代表性的 Windows 编码问题：**Issue #7290**。

用户报告，即使 Windows、VS Code、PowerShell 7 都已经在 UTF-8 环境下，Codex 拉起 PowerShell 后，依然可能出现编码退回系统代码页、最终把非拉丁字符写坏的问题。

更有意思的是后续。

OpenAI 的维护者后来真的合并了一个 Windows PowerShell UTF-8 启动修复，并让用户通过 `powershell_utf8` feature 测试。

所以至少可以确认一件事：

> **PowerShell 编码并不是网友为了给 Codex 找借口硬凑出来的问题，而是确实进入过 Codex 上游工程修复流程的问题。**

相关资料：

- [openai/codex Issue #7290](https://github.com/openai/codex/issues/7290)

---

## 不只是编码，5.1 本身也可能成为兼容性变量

还有一个比较有意思的 Windows sandbox 案例：Codex **Issue #14057**。

在这个案例中，Windows PowerShell 5.1 在 Codex sandbox 内启动出现错误，而其他 shell 可以正常工作。

这类 issue 不能推导成：

> “PowerShell 5.1 在 Codex 里一定会坏。”

当然不是。

但它至少说明：

> **当 Agent 的执行环境已经够复杂时，一个老的 Windows PowerShell 运行时，本身就可能成为额外的兼容性变量。**

所以装 PS7 的价值，不只是“新版本看起来比较新”。

它是在主动拿掉一部分历史包袱。

相关资料：

- [openai/codex Issue #14057](https://github.com/openai/codex/issues/14057)

---

## 还有一个容易被低估的问题：调用现代 CLI

Coding Agent 在 shell 里真正调用最多的，往往不是 PowerShell cmdlet，而是：

```text
git
rg
python
node
npm
dotnet
cargo
```

这种 native CLI。

而 PowerShell 7.3 之后对 native command 参数传递也做过专门调整，并提供 `$PSNativeCommandArgumentPassing` 来处理现代命令行参数行为。

Agent 自动生成命令时，经常会碰到：

```text
空格路径
双引号
反斜杠
Unicode 参数
复杂 argv
```

所以一个行为更现代、更接近现在 CLI 工具链的 shell，本身就是加分项。

微软参考：

- [about_Preference_Variables / PSNativeCommandArgumentPassing](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_preference_variables?view=powershell-7.6)

---

# 那怎么升级？这反而是最简单的部分

如果已经在用 Codex 这种 Agent，我甚至觉得没必要手把手写一堆安装步骤。

直接让 Agent 帮忙就行。

可以把下面这段直接丢给 Codex：

```text
帮我在 Windows 上安装当前稳定版 PowerShell 7。

优先使用 winget 安装。
安装完成后：
1. 检查 pwsh --version
2. 找到实际的 pwsh.exe 路径
3. 检查当前 Codex 版本支持的 Windows shell 配置方式
4. 如果支持，把默认 PowerShell shell 指向 pwsh.exe
5. 如果当前版本不能直接配置默认 shell，就让后续 PowerShell 命令优先显式调用 pwsh
6. 最后验证实际运行的 PowerShell 版本和进程路径

如果 Microsoft / WinGet 软件源当前无法访问，先告诉我网络问题，不要无限重试。
```

微软推荐的安装命令本质上也就是：

```powershell
winget install --id Microsoft.PowerShell --source winget
```

微软官方同时明确说明：

> PowerShell 7 **不会替换** Windows PowerShell 5.1。

它们会并存。

所以升级不是：

```text
删掉 5.1 → 换成 7
```

而是：

```text
powershell.exe → 5.1 继续留着
pwsh.exe       → 另外安装 PowerShell 7
```

这也是为什么这件事的试错成本很低。

微软安装文档：

- [Installing PowerShell on Windows](https://learn.microsoft.com/en-us/powershell/scripting/install/install-powershell-on-windows?view=powershell-7.6)

---

# 最容易漏掉的一步：装了 PS7，不等于 Codex 已经在用 PS7

这一点很重要。

很多人执行完：

```powershell
winget install --id Microsoft.PowerShell --source winget
```

看到安装成功，就认为问题结束了。

其实不是。

Windows 上：

```text
powershell.exe ≠ pwsh.exe
```

PS7 是 side-by-side 安装。

所以即使机器里已经有 `pwsh.exe`，某些 Codex 版本、某些终端上下文或者某些内部执行路径，仍然可能继续调用：

```text
powershell.exe
```

Codex 仓库里甚至有人专门提出过 enhancement：

> Windows 上如果能找到 `pwsh`，Codex 应该优先使用 PowerShell 7，而不是 legacy `powershell.exe`。

参考：

- [openai/codex Issue #27390](https://github.com/openai/codex/issues/27390)

因此我更建议：**不要死记某个可能随 Codex 版本变化的配置项。**

让 Agent 自己先检查当前版本支持什么 shell 配置，再修改。

最终只认实际结果。

---

# 怎么确认 Codex 真的用上 PowerShell 7？

这一步非常简单。

让 Codex 在当前执行环境里跑：

```powershell
$PSVersionTable.PSVersion
(Get-Process -Id $PID).Path
```

或者直接显式测试：

```powershell
pwsh -NoLogo -NoProfile -Command '$PSVersionTable.PSVersion; (Get-Process -Id $PID).Path'
```

真正想看到的是类似：

```text
7.x
C:\Program Files\PowerShell\7\pwsh.exe
```

而不是：

```text
5.1
C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
```

![Codex 成功调用 PowerShell 7 的验证示意图](/api/v1/website/image/ai-sharing/codex-ps-7-concept-verify.webp)

判断其实就两个点：

```text
✓ PowerShell 版本是 7.x
✓ 实际进程是 pwsh.exe
```

两个都满足，这条执行链才算真的切过去。

---

# PS7 能解决什么，又不能解决什么？

这里也别把 PowerShell 7 神化。

它比较明确能改善的是：

- UTF-8 / 非 ASCII 文本环境
- Windows PowerShell 5.1 的历史编码行为
- 更现代的 native CLI 参数处理
- 一部分旧 PowerShell 运行时兼容问题
- Windows Coding Agent 的 shell 基础环境一致性

但如果 Codex 慢是因为：

```text
模型响应慢
网络访问慢
代理慢
Git 仓库本身巨大
杀毒软件扫描
sandbox 开销
npm / pip 下载慢
磁盘 I/O 慢
```

那装 PowerShell 7 当然不会突然让这些东西全部消失。

所以我的理解不是：

> **Windows 上 Codex 慢，全怪 PowerShell。**

而是：

> **Windows 上使用 Codex 时，PowerShell 5.1 是一个很便宜就能排除掉的老变量。**

先把它处理掉，再判断剩下的问题到底来自哪里，排查会干净很多。

---

# 最后

如果平时就在 Windows 上用 Codex，我现在会直接做三件事：

```text
安装 PowerShell 7
        ↓
让 PowerShell 命令优先走 pwsh.exe
        ↓
让 Codex 自己验证版本 + 进程路径
```

成本非常低，5.1 又不会被删。

对于中文项目尤其如此。

它不是什么“让 Codex 能力暴涨”的神奇优化，但属于那种：

> **装完以后，少背一点 Windows 的历史包袱。**

这就已经挺值了。

---

## 参考资料

1. Microsoft Learn — Character Encoding in PowerShell  
   https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_character_encoding?view=powershell-7.6

2. Microsoft Learn — Installing PowerShell on Windows  
   https://learn.microsoft.com/en-us/powershell/scripting/install/install-powershell-on-windows?view=powershell-7.6

3. Microsoft Learn — PSNativeCommandArgumentPassing  
   https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_preference_variables?view=powershell-7.6

4. openai/codex Issue #7290 — Windows UTF-8 / non-Latin character issue  
   https://github.com/openai/codex/issues/7290

5. openai/codex Issue #14057 — Windows sandbox / powershell.exe issue  
   https://github.com/openai/codex/issues/14057

6. openai/codex Issue #27390 — Prefer pwsh on Windows proposal  
   https://github.com/openai/codex/issues/27390
