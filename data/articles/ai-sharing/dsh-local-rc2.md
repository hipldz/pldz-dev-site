---
author: pldz1
category: ai-sharing
csdn: ''
date: '2026-09-01'
gitee: ''
github: ''
juejin: ''
serialNo: 4
status: publish
summary: 记录 DeepSeek Harness 本地安装方式，包括本地 pnpm、DSH 安装、build scripts 放行，以及 Node.js 在特殊网络环境下的系统 CA、代理配置和 HTTPS 证书问题排查.
tags:
  - AI
  - DeepSeek
  - Node
thumbnail: /api/v1/website/image/ai-sharing/dsh-local-rc2-thumbnail.webp
title: DeepSeek Harness 本地安装和对话过程的网络问题
---


# DeepSeek Harness 本地安装和对话过程的网络问题

最近简单体验了一下 DeepSeek Harness，官方直接给的方式是：

```powershell
npx @deepseek-ai/dsh web
```

不过我这里不太想把 `pnpm` 或者 `dsh` 往全局环境里面装，尤其是在临时环境或者一台比较干净的 Windows 电脑上，个人还是更喜欢东西都放在当前文件夹，后面不用了直接删目录就行。

所以这里记录一下这次在 Windows PowerShell 里的安装过程：`pnpm` 本身也是 local 的，`@deepseek-ai/dsh` 也是 local 的，没有用 `-g`。

本次实际安装到的 DSH 版本是：

```text
@deepseek-ai/dsh 0.1.1-rc.2
```

而且还需要解决一些特殊网络环境下大家无法和它进行对话的问题。

![highlight问题](/api/v1/website/image/ai-sharing/dsh-local-rc2-highlight-network-issue.webp)


DeepSeek Harness 目前还是 Developer Preview，版本变化比较快，后面如果命令有变化还是以官方 README 为准。

## 0. 环境和目录

我这里是在一个临时目录下面操作：

```text
dsh-local/
```

机器已经有 `Node.js` 和 `npm`，但是没有 `pnpm`。

可以先看一下：

```powershell
node -v
```

```powershell
npm -v
```

后面的命令都是 PowerShell，一条命令一行，没有用多行续写。

## 1. 先把 pnpm 装到当前目录

首先创建一个 `.tools` 目录：

```powershell
mkdir -p .tools
```

然后使用已经存在的 `npm`，把 `pnpm` 安装到 `.tools` 下面：

```powershell
npm install --prefix "$PWD\.tools" pnpm@11.7.0
```

验证一下：

```powershell
.\.tools\node_modules\.bin\pnpm.cmd --version
```

我这里输出：

```text
11.7.0
```

这样 `pnpm` 就没有安装到全局，实际执行文件在：

```text
.tools\node_modules\.bin\pnpm.cmd
```

后面的 pnpm 指令直接用这个路径。

## 2. 本地安装 DeepSeek Harness

这里也不是 clone DeepSeek Harness 的源码，而是直接安装 npm 上面的 `@deepseek-ai/dsh` 包：

```powershell
.\.tools\node_modules\.bin\pnpm.cmd add @deepseek-ai/dsh
```

这次安装完成以后可以看到：

```text
dependencies:
+ @deepseek-ai/dsh 0.1.1-rc.2
```

不过 pnpm 还给了一个比较重要的提示：

```text
[ERR_PNPM_IGNORED_BUILDS] Ignored build scripts:
@deepseek-ai/dsh-subprocess-local@0.1.1-rc.2,
@google/genai@1.52.0,
koffi@3.1.6,
node-pty@1.2.0-beta.15,
protobufjs@7.6.6
```

安装时的实际情况如下：

![使用本地 pnpm 安装 DeepSeek Harness](/api/v1/website/image/ai-sharing/dsh-local-rc2-pnpm-build-dsh.webp)

## 3. pnpm 的 build scripts 需要放行

新版 pnpm 会对依赖安装期间执行的 build scripts 做限制。

这次 DSH 的依赖里面有 `node-pty`、`koffi` 以及 DSH 自己的 subprocess 包，所以不能只是看到 package 下载完成就直接当成安装结束。

我这个目录就是单独用来运行 DSH 的，所以这里直接批准当前 pending builds：

```powershell
.\.tools\node_modules\.bin\pnpm.cmd approve-builds --all
```

执行后可以看到类似：

```text
node-pty: Running install script
koffi: Running install script
protobufjs: Running postinstall script
@deepseek-ai/dsh-subprocess-local: Running postinstall script
```

如果不想直接 `--all`，也可以运行交互式的：

```powershell
.\.tools\node_modules\.bin\pnpm.cmd approve-builds
```

然后自己确认需要允许执行脚本的依赖。

pnpm 官方对 `approve-builds` 的定义就是批准依赖在安装过程中运行 scripts，所以这里不要简单用关闭安全检查之类的方式绕过去。

## 4. 启动 DSH

安装完成以后，本地的 `dsh` 在：

```text
node_modules\.bin\dsh.cmd
```

普通启动：

```powershell
.\node_modules\.bin\dsh.cmd web
```

默认 Web UI 地址是：

```text
http://127.0.0.1:3080
```

如果和我一样不希望启动时自动打开浏览器，可以加 `--no-open`：

```powershell
.\node_modules\.bin\dsh.cmd web --no-open
```

这样服务正常启动，只是不自动拉起浏览器，需要的时候自己打开 `http://127.0.0.1:3080`。

## 5. 特殊网络环境下的 Node HTTPS 问题

这里还有一个我实际遇到的问题。

DSH 页面虽然能起来，但是调用 DeepSeek API 的时候网络报错：

![DeepSeek Harness 网络错误](/api/v1/website/image/ai-sharing/dsh-local-rc2-network-error.webp)

一开始先分别用 `curl` 和 Node 自己的 `fetch` 测试：

```powershell
curl -v https://api.deepseek.com
```

`curl` 可以正常建立 HTTPS 连接，最后服务端返回：

```text
HTTP/1.1 401 Authorization Required
Authentication Fails
```

这里的 `401` 没啥问题，因为这个测试请求本来就没有带 API Key。至少它说明 `curl` 已经通过 TLS 连到了 `api.deepseek.com`，并且拿到了服务端的 HTTP 响应。

然后再测试 Node：

```powershell
node -e "fetch('https://api.deepseek.com').then(r=>console.log(r.status)).catch(e=>console.error(e))"
```

我这里 Node 反而直接失败：

```text
TypeError: fetch failed

[cause]: Error: unable to get local issuer certificate

code: 'UNABLE_TO_GET_ISSUER_CERT_LOCALLY'
```

实际测试截图：

![curl 可以访问但 Node fetch 证书失败](/api/v1/website/image/ai-sharing/dsh-local-rc2-test-network-curl-fetch.webp)

这种现象在一些公司网络、HTTPS 检查或者特殊代理环境里比较容易碰到：系统里面已经信任了对应证书，所以 Windows 的 curl 可以正常访问，但是 Node 默认使用的 CA 信任链不一定完全一样。

### 5.1 让 Node 使用系统 CA

Node 新版本支持直接使用系统证书库。

PowerShell 当前会话设置：

```powershell
$env:NODE_USE_SYSTEM_CA="1"
```

然后重新测试：

```powershell
node -e "fetch('https://api.deepseek.com').then(r=>console.log(r.status)).catch(e=>console.error(e))"
```

如果这时候输出：

```text
401
```

就对了。

还是前面那个原因：测试没有提供 API Key，所以 `401` 是预期的；关键是已经不再出现 `UNABLE_TO_GET_ISSUER_CERT_LOCALLY`。

然后在同一个 PowerShell 会话里面启动 DSH：

```powershell
.\node_modules\.bin\dsh.cmd web --no-open
```

## 6. 如果网络还要求代理

有些环境除了系统 CA，还必须经过 HTTP/HTTPS 代理。

假设本地代理监听：

```text
127.0.0.1:7890
```

PowerShell 可以设置：

```powershell
$env:HTTP_PROXY="http://127.0.0.1:7890"
```

```powershell
$env:HTTPS_PROXY="http://127.0.0.1:7890"
```

然后让 Node 使用这些环境变量：

```powershell
$env:NODE_USE_ENV_PROXY="1"
```

如果系统 CA 也需要，一起设置：

```powershell
$env:NODE_USE_SYSTEM_CA="1"
```

最后启动：

```powershell
.\node_modules\.bin\dsh.cmd web --no-open
```

喜欢一次粘贴的话也可以直接一行：

```powershell
$env:NODE_USE_SYSTEM_CA="1"; $env:HTTP_PROXY="http://127.0.0.1:7890"; $env:HTTPS_PROXY="http://127.0.0.1:7890"; $env:NODE_USE_ENV_PROXY="1"; .\node_modules\.bin\dsh.cmd web --no-open
```

这里的 `127.0.0.1:7890` 只是示例，需要换成自己的代理地址。

Node 官方现在提供了 built-in proxy support，打开 `NODE_USE_ENV_PROXY=1` 后会读取 `HTTP_PROXY`、`HTTPS_PROXY` 和 `NO_PROXY`。

## 7. 不要直接关闭 TLS 校验

网上排查 Node HTTPS 证书问题时经常能搜到这个：

```powershell
$env:NODE_TLS_REJECT_UNAUTHORIZED="0"
```

这个确实可能让报错暂时消失，但是它是直接关闭 TLS 证书校验。

这里不建议这样处理。

如果问题是公司网络证书链，优先：

```powershell
$env:NODE_USE_SYSTEM_CA="1"
```

![NODE继承CA](/api/v1/website/image/ai-sharing/dsh-local-rc2-node-ca.webp)

如果还需要代理，再配置：

```powershell
$env:HTTP_PROXY="http://127.0.0.1:7890"
```

```powershell
$env:HTTPS_PROXY="http://127.0.0.1:7890"
```

```powershell
$env:NODE_USE_ENV_PROXY="1"
```

![NODE继承PROXY](/api/v1/website/image/ai-sharing/dsh-local-rc2-node-proxy.webp)

这样至少还是正常走证书信任和代理配置。

## 8. 最后的目录结构

最后大概就是：

```text
dsh-local/
├── .tools/
│   └── node_modules/
│       └── pnpm/
├── node_modules/
│   └── @deepseek-ai/
│       └── dsh/
├── docs/
│   ├── network-error.jpg
│   ├── pnpm-build-dsh..jpg
│   ├── test-network-curl-fetch.jpg
│   └── deepseek-harness-local-pnpm.md
├── package.json
└── pnpm-lock.yaml
```

`pnpm` 在 `.tools`，DSH 在当前项目的 `node_modules`，没有任何 `pnpm add -g` 或者 `npm install -g`。

平时启动就是：

```powershell
.\node_modules\.bin\dsh.cmd web --no-open
```

特殊网络环境下先设置对应的 Node 环境变量，再启动即可。

另外 DSH 现在还是 Developer Preview，我这里记录的是 `0.1.1-rc.2` 这次实际安装和排错的过程，后续版本如果 CLI、依赖或者启动参数变化，直接看一下官方 README 和 `dsh web --help`。

## 参考内容

- DeepSeek Harness: https://github.com/deepseek-ai/deepseek-harness
- DeepSeek Harness CLI: https://github.com/deepseek-ai/deepseek-harness/tree/master/apps/cli
- pnpm `approve-builds`: https://pnpm.io/cli/approve-builds
- pnpm `ignored-builds`: https://pnpm.io/cli/ignored-builds
- Node.js CLI / `NODE_USE_SYSTEM_CA` / `NODE_USE_ENV_PROXY`: https://nodejs.org/api/cli.html
- Node.js Built-in Proxy Support: https://nodejs.org/api/http.html#built-in-proxy-support
