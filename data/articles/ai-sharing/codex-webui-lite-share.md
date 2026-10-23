---
author: pldz1
category: ai-sharing
csdn: ""
date: "2026-10-13"
gitee: https://gitee.com/pldz/codex-webui-lite
github: https://github.com/hipldz/codex-webui-lite
juejin: ""
serialNo: 5
status: publish
summary: 给自己的 2H2G 小服务器做了一个 Codex Web UI，提供在线静态预览。分享会话恢复、计划交互、附件上传和生成文件下载的用法，以及安装和部署步骤。
tags:
  - AI
  - Codex
  - 工具分享
  - 自部署
thumbnail: /api/v1/website/image/ai-sharing/codex-webui-lite-cover.webp
title: 自制 Codex Web UI
---

**先看效果：[打开静态预览](https://hipldz.com/io/codex-webui-lite/?demo=chat)**

不用安装或登录，打开就能看界面，顶部可以切换聊天、提问和计划三个场景。预览使用演示数据，不连接真实 Codex；文件下载、持久保存和真实任务执行需要部署后端。

源码：[GitHub](https://github.com/hipldz/codex-webui-lite) · [Gitee](https://gitee.com/pldz/codex-webui-lite)

## 为什么做这个工具

前面 DeepSeek Harness 很火，我也跟着折腾了一下。后来又发现了 Codex Harness 和 `codex app-server`，就想着能不能在浏览器里用 Codex。

刚好我手上有一台 **2 核 2 GB 的小服务器**，想把这套东西放上去用，感觉就差一个顺手的 Web UI。官方那套界面不太适合我这里自定义 `endpoint` 的用法，也找了几个 GitHub 上的项目，或多或少在 UI 和文件操作上不太合适。

那么干脆让 **GPT-6** 写一个，就是这里的 `codex-webui-lite`，项目里的名字是 **Codex Web Harness**。在浏览器里选项目、继续之前的会话、看执行记录，也能直接查看和编辑文件。

自己已经用了不少日子，目前没遇到太大的问题。期间也把上传附件、生成文件放在哪里、怎么在页面里找到和下载这些文件等几个典型的使用问题处理了一下，这里就把这个小工具分享给大家。

登录状态、配置和 session 还是由 Codex 自己管理，Web UI 不读取或保存 Codex 凭据。已经在终端或者 VS Code 里用 Codex 的话，可以接着原来的会话工作。

## 😎 先看一下界面

先放一段之前录的操作演示，界面是当时的版本：

![Codex Web UI 早期版本操作录屏](/api/v1/website/image/ai-sharing/codex-webui-lite-demo.gif@original)

左边是 workspace 和会话列表，中间是对话。上面可以打开 **Changes** 看修改，或者打开 **Files** 查看文件；下面的输入框可以选模型、reasoning effort、Code / Plan 模式和权限。

![Codex Web UI 内置演示：左侧会话列表，中间活动时间线和命令审批卡片，下方为输入工具栏](/api/v1/website/image/ai-sharing/codex-webui-lite-overview.webp@original)

文中的三张静态界面图来自项目内置的 `demo`，命令、修改和模型名称都是演示数据。实际使用时，模型列表从你自己的 app-server 读取。

执行过程不会只显示最后一段回答。读了哪些文件、跑了什么命令、改了哪些地方，会收在这一轮的活动时间线里，可以展开看详情。需要审批时，会显示类似图里的命令卡片。

## 📁 文件和修改直接在页面里看

这里是我比较在意的一部分：上传的附件不要混进项目源码，生成出来的文件也要能在页面里找到、下载。

**Changes** 按文件展示 Diff。**Files** 里分了两个入口：

| 入口          | 放什么                           | 位置                                |
| ------------- | -------------------------------- | ----------------------------------- |
| Project files | 项目源码、项目资源               | 当前会话的 workspace                |
| Session files | 这次会话的附件和默认独立交付文件 | `${CODEX_HOME}/web-ui/<thread.id>/` |

没设置 `CODEX_HOME` 时，会话文件默认在 `~/.codex/web-ui/<thread.id>/`。让 Codex 改项目源码，文件还是在项目里；让它整理一份独立文档，默认交付位置是会话目录，明确指定其他位置时按你的要求保存。

比如把资料作为附件放进输入框，再发一句：

```text
根据上传的资料整理一份 Markdown 说明，保存到当前会话文件目录，完成后给我文件链接。
```

任务完成后，可以从回复里的文件链接打开，也可以在 **Files → Session files** 里找到文件并下载。要看改过的项目源码，就切到 **Project files**；要核对修改内容，就打开 **Changes**。

Files 可以浏览目录、新建文本文件、编辑、删除和下载。Markdown、JSON、Python、TypeScript 这类文本可以预览和编辑；图片可以直接预览。PDF、Word、Excel 和压缩包可以上传、下载，当前 Files 面板不解析这些文件。

输入框也能直接选择文件，或者粘贴附件。这里两种上传入口的限制不一样：

| 上传位置   | 数量上限      | 大小限制                               |
| ---------- | ------------- | -------------------------------------- |
| 对话输入框 | 每条消息 4 个 | 单个和全部附件合计都不超过 10 MB       |
| Files 面板 | 每批 10 个    | 单个不超过 10 MB，每批合计不超过 25 MB |

删除会话时不会顺手删除会话目录里的交付文件。确认不需要了，再手动清理对应目录。

## 💬 接着已有会话工作

页面会从 app-server 分页读取本机的会话，包括 CLI、VS Code、exec、app-server 和 sub-agent sessions。可以搜索、恢复、归档，也可以分支。

点进一个已有会话后，会恢复它原来的 workspace。地址栏会带上 `?session=<id>`，刷新后会继续恢复这个会话。

这里有个容易混的地方：**默认 workspace 只管新对话。** 已有会话用自己的目录，点击 **New thread** 才重新取 `CODEX_WEB_DEFAULT_WORKSPACE`。如果改了默认目录，却刷新了一个旧会话的链接，看到的仍然是旧项目。

每条已完成的 Codex 文本回复下面还有复制和分支入口。分支从这条回复的位置创建新会话，不会把后面的对话带过去，原会话保留。

模型和 reasoning effort 列表来自 app-server 实际返回的 `model/list`。新对话会读取对应 workspace 的有效配置；没有指定模型时，再使用模型目录里的默认值。

## 📝 先出计划，再执行

输入框下面可以切换 **Code / Plan**。要先梳理方案，就选 Plan；计划完成后，页面会单独显示一张计划卡片。

![内置 Plan 演示：计划正文下方提供 Revise plan 和 Implement this plan 两个操作](/api/v1/website/image/ai-sharing/codex-webui-lite-plan.webp@original)

比如准备调整一个页面，可以先发：

```text
先给一个改造计划：把首页的文章列表增加分类筛选，说明要改哪些文件，先不要执行。
```

看完计划后，点击 **Implement this plan** 会切到 Code，并开始新一轮执行。还要调整就点 **Revise plan**，补充要求后继续规划。

任务中途需要你回答问题时，也有单独的问题卡片。能选选项、填自己的答案，多问题可以逐个切换，填完统一提交，支持 `Ctrl / ⌘ + Enter`。

![内置提问演示：问题卡片显示选项、问题进度和提交入口](/api/v1/website/image/ai-sharing/codex-webui-lite-questions.webp@original)

阻塞问题需要回答后任务才能继续；非阻塞问题可以暂时不答，或者 dismiss。普通答案草稿会保留在当前浏览器标签页，敏感答案不保存草稿。

这些交互依赖 Codex 的 experimental app-server API。项目 README 记录的实现依据是本机 `codex-cli 0.162.1` 导出的协议；旧版如果不支持 `collaborationMode`，会明确报错，需要检查 CLI 兼容性。

## 🚀 先跑起来

需要准备：

- Node.js `^20.19.0` 或 `>=22.12.0`。
- 已安装 `codex` CLI，并且运行 Web 服务的同一个用户已经完成登录或认证配置。
- 一个实际存在、当前用户可以访问的项目目录。

先确认命令能找到：

```bash
node --version
codex --version
```

下面用 Linux shell 举例。先获取项目，然后在项目根目录安装依赖和构建：

```bash
git clone https://gitee.com/pldz/codex-webui-lite.git
cd codex-webui-lite
npm ci
npm run build
```

接着设置默认工作目录。`/absolute/path/to/your-project` 换成你自己的项目绝对路径，需要提前存在：

```bash
export CODEX_WEB_DEFAULT_WORKSPACE=/absolute/path/to/your-project
npm start
```

浏览器打开：

```text
http://127.0.0.1:8765/
```

这个地址是运行服务的那台机器的本机地址。默认只监听 `127.0.0.1`；部署在服务器上、需要从另一台电脑访问的话，后面再说反向代理。

启动时页面会等待 Codex app-server、模型列表和首屏会话加载。进入界面后，先看左边的 workspace 是否是刚才设置的项目，再新建一个对话。

比如先发一句：

```text
先看一下这个项目的目录结构，告诉我入口文件在哪里，暂时不要修改代码。
```

检查回答和活动记录是不是对应自己的项目。没有配置默认目录时，也可以在页面上手动选择 workspace；新对话没选目录，是不能直接发送的。

## ⚙️ 后台运行和几个配置

前台确认能用后，可以按项目提供的脚本管理后台进程。先停掉前台的 `npm start`，避免占用同一个端口。

Linux/macOS 在项目根目录执行：

```bash
./scripts/codex-web.sh start
./scripts/codex-web.sh status
./scripts/codex-web.sh logs
```

重启和停止：

```bash
./scripts/codex-web.sh restart
./scripts/codex-web.sh stop
```

Windows PowerShell 对应的是：

```powershell
.\scripts\codex-web.ps1 start
.\scripts\codex-web.ps1 status
.\scripts\codex-web.ps1 logs
.\scripts\codex-web.ps1 restart
.\scripts\codex-web.ps1 stop
```

日志和 PID 放在项目的 `.run/`。这些脚本不会自动加载 `.env`，也不会保存当前环境变量；换一个终端重启时，需要重新设置所需变量。关闭终端后服务会继续运行，机器重启后自动启动则需要另外配置 systemd，项目 README 里有示例。

常用的几个变量如下：

| 变量                          | 默认值      | 用途                                   |
| ----------------------------- | ----------- | -------------------------------------- |
| `CODEX_WEB_HOST`              | `127.0.0.1` | 监听地址                               |
| `CODEX_WEB_PORT`              | `8765`      | 监听端口                               |
| `CODEX_WEB_BASE_PATH`         | `/`         | 页面和 API 的统一子路径                |
| `CODEX_WEB_DEFAULT_WORKSPACE` | 未设置      | 新对话默认工作目录                     |
| `CODEX_WEB_AUTH`              | 未启用      | Basic Auth，格式为 `username:password` |

要挂在现有站点的 `/codex/` 下，可以在启动或重启前设置：

```bash
export CODEX_WEB_BASE_PATH=/codex
export CODEX_WEB_AUTH='your-user:replace-with-a-strong-password'
./scripts/codex-web.sh restart
```

上面的账号和密码换成自己的。Nginx 的 HTTPS 站点里增加：

```nginx
location /codex/ {
    proxy_pass http://127.0.0.1:8765/codex/;
    proxy_set_header Host $http_host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

后端保持监听本机回环地址，从自己的 HTTPS 域名访问 `/codex/`。Basic Auth 本身不加密连接，不要直接把这个 HTTP 服务暴露到公网。

浏览器和 Node 之间使用 HTTP API 与增量轮询，不需要额外配置 WebSocket 反代。Node 再用 stdio JSON-RPC 和常驻的 `codex app-server` 通信。

## 🔧 用之前再看几个地方

权限菜单提供 **Ask when needed**、**Full access**、**Read-only** 和 **Use config.toml**。要只读看代码，可以选 Read-only；有自己的权限配置，就选 Use config.toml。Full access 对应无 sandbox、无审批，只在自己信任的环境和任务里使用。

生产模式的 `npm start` 不会自动构建。更新源码后，需要重新执行 `npm run build`，再重启服务；只改环境变量则不需要重新构建。

小机器上，当前 Web UI 默认同时执行 1 个 turn，最多再排队 8 个。启动脚本给 Node 设置了 `--max-old-space-size=256`，这是 V8 堆上限，Codex app-server 和它启动的工具仍会单独占内存。不要把它理解成整套工具只用 256 MB，更不能保证项目构建或浏览器任务都能在 2 GB 内跑完。

新对话发不出去时，先检查 workspace 是否选好。account usage 显示 `Unavailable`，可能是当前认证方式没有提供对应接口，不影响对话和文件功能。

第一次使用建议先以前台方式确认登录、项目目录和第一轮对话，再转后台运行。完整配置和 systemd 示例放在[项目 README](https://gitee.com/pldz/codex-webui-lite)里。
