---
author: pldz1
category: ai-sharing
csdn: ''
date: '2026-08-21'
gitee: ''
github: ''
juejin: ''
serialNo: 3
status: publish
summary: 做了一个小工具, 按住快捷键录音，松开任意一个按键就停止，最后识别出来的文字插入到录音前的输入位置.
tags:
  - AI
  - Codex
  - Windows PowerShell
thumbnail: /api/v1/website/image/ai-sharing/qwem-asr-input-1-thumbnail.jpg
title: 用 Qwen ASR 给 Linux 加一个按住说话的语音输入工具
---

# 用 Qwen ASR 给 Linux 加一个按住说话的语音输入工具

平时在 Linux 下写代码、写命令或者回复消息时，很多内容其实直接说出来会更快一点。这里做了一个小工具 `qwen-asr-input`：按住 `Ctrl+Win` 开始录音，松开任意一个按键就停止，最后把 Qwen ASR 识别出来的文字插入到录音前的输入位置。

录音时屏幕底部会出现一个 Qt 麦克风浮层，服务端产生 `result-generated` 事件后，浮层会实时更新识别文本。最终结果显示一会儿之后，浮层自动关闭。


## 😎 快速看一下效果

这个工具的使用过程比较简单：

1. 在 VS Code、终端或者其他输入框里放好光标。
2. 按住 `Ctrl+Win`。
3. 看到底部的麦克风浮层后开始说话。
4. 松开 `Ctrl` 或 `Win`，录音立即停止。
5. 等待最终识别结果，文字会插入刚才保存的输入位置。

项目目前只在 Ubuntu X11 会话中测试过，Wayland 还不支持，其他 Linux 发行版也没有测试。可以先检查当前会话类型：

```bash
echo "$XDG_SESSION_TYPE"  # 预期输出：x11
```

| 平台 | 测试状态 |
| --- | --- |
| Ubuntu X11 | ✅ Pass |

项目里的预览图如下：

![v0.0.1 preview](/api/v1/website/image/ai-sharing/qwem-asr-1-preview.png)

## 🔧 安装依赖

在 Ubuntu 上安装系统依赖：

```bash
sudo apt update
sudo apt install python3 python3-venv alsa-utils xclip python3-pyqt5 libx11-6 libxtst6
```

程序需要读取 `/dev/input/event*` 下的键盘设备。如果当前用户不在 `input` 组里，可以执行：

```bash
sudo usermod -aG input "$USER"
```

重新登录后，新的用户组权限才会生效。这里不要把整个应用直接用 root 运行。

项目使用 `python3-venv` 创建 Python 虚拟环境，`alsa-utils` 提供录音相关命令，`xclip` 用来配合 X11 剪贴板完成文本插入，`python3-pyqt5` 用来显示录音状态浮层。

## 🚀 第一次运行

以下命令都在项目根目录执行。

先复制配置文件：

```bash
cp config.example.toml config.toml
```

然后检查本地环境：

```bash
./qwen-asr-input check
```

工具使用 DashScope API，需要把 API Key 放在环境变量里：

```bash
export ALIYUN_ASR_API_KEY='your DashScope API key'
```

启动前台进程：

```bash
./qwen-asr-input run
```

第一次建议先用 `run`，因为日志会直接显示在当前终端里。看到下面这类提示后，就可以切换到输入框测试：

```text
ready — hold Ctrl+Win to record
```

测试完成后按 `Ctrl+C` 退出。

程序默认从项目根目录读取 `config.toml`，所以从其他目录调用脚本时也能找到配置文件。如果需要指定其他配置文件，可以这样运行：

```bash
./qwen-asr-input run --config /absolute/path/to/config.toml --debug
```

其中 `/absolute/path/to/config.toml` 需要替换成实际配置文件路径。

## 🧪 先测试文字插入

如果暂时不想录音，也不想连接 Qwen，可以只测试文字注入功能：

```bash
./qwen-asr-input run --inject-test 'Qwen input test succeeded'
```

执行命令后，在三秒内切换到目标输入框。这个测试不会录音，也不会访问 Qwen，主要用来看文本能不能插入当前的输入位置。

## ⚙️ 后台运行

前台模式确认没有问题后，可以启动后台服务：

```bash
export ALIYUN_ASR_API_KEY='your DashScope API key'
./qwen-asr-input start
./qwen-asr-input status
```

其他管理命令如下：

```bash
./qwen-asr-input logs       # 查看日志，Ctrl+C 只退出日志查看器
./qwen-asr-input restart    # 重启服务
./qwen-asr-input stop       # 停止服务
```

PID 文件和日志放在项目内的 `.runtime/` 目录。项目没有配置登录后自动启动，如果自己增加自动启动配置，需要保证登录环境里能拿到以下变量：

```text
ALIYUN_ASR_API_KEY
DISPLAY
XAUTHORITY
```

所有操作都通过 `./qwen-asr-input COMMAND` 进入，支持的命令是：

```text
start
run
status
logs
stop
restart
check
```

Python 选项放在 `run` 或 `start` 后面。

## 🎙️ 配置说明

配置文件默认是项目根目录下的 `config.toml`，也可以通过参数指定：

```bash
./qwen-asr-input run --config /path/to/config.toml --debug
```

区域配置需要根据使用位置选择：

```toml
region = "beijing"
```

在中国大陆使用 `beijing`，其他地区使用 `singapore`。

API Key 只从 `ALIYUN_ASR_API_KEY` 读取，不会保存到配置文件里。即使开启 `--debug`，WebSocket 授权请求头也不会写入日志。

浮层相关配置在 `[overlay]` 区域：

- `bottom_margin`：浮层距离屏幕工作区底部的像素数，默认值是 `72`。
- `width`：浮层宽度，默认值是 `620`。

## 🧩 里面是怎么串起来的

整个流程可以简化成下面这样：

```text
EvdevPushToTalk
       │ START / STOP / RELEASED
       ▼
PushToTalkApp ── capture ──> InputTarget（实际 X11 输入焦点窗口）
       │
       ├── ArecordAudioSource ── PCM 16k/mono/S16_LE ──┐
       │                                                ▼
       └──────────────────────── QwenStreamingAsrClient
                                                        │ final text
                                                        ▼
                              X11XTestPasteInjector（xclip + Shift+Insert）
```

核心接口定义在 `contracts.py`：

- `AudioSource`：产生 PCM 音频块。
- `AsrClient`：消费音频流并返回最终文本。
- `FocusTracker`：在录音开始前记录准确的输入目标。
- `TextInjector`：把完整的 Unicode 文本插入目标窗口。
- `Overlay`：显示监听、流式识别、完成和错误状态。

这里的录音格式是 `PCM 16k/mono/S16_LE`。识别过程中间结果只显示在浮层里，输入框只接收最终句子，不会随着流式结果不断覆盖输入内容。

## 📋 为什么文本插入不是逐字模拟按键

这个工具没有把识别出的内容一个字符一个字符地模拟成键盘输入，也不依赖目标程序当前选择的输入法。

它的处理方式是：

1. 先把识别到的完整文本写入 X11 的 `CLIPBOARD`。
2. 再通过 XTEST 发送 `Shift+Insert`。
3. 由当前输入窗口完成粘贴。

这种方式目前在 VS Code 和常见终端里可以使用。

还有一个输入焦点的问题。录音开始时，程序通过 `XGetInputFocus` 保存实际的子窗口，而不是只保存 `_NET_ACTIVE_WINDOW` 对应的顶层窗口。这样在录音和识别完成后，文字还能回到开始录音前的编辑位置。

## 📁 项目目录

项目采用发行名和 Python 包名分开的方式：

```text
qwen-asr-input/                 # 项目名和命令名，使用连字符
├── qwen-asr-input              # 环境设置、启动和进程管理
├── config.example.toml
└── qwen_asr_input/             # 可导入的 Python 包，使用下划线
    ├── assets/mic.svg          # Python 包内的资源文件
    └── *.py
```

Python 标识符不能使用 `-`，所以发行名和命令是 `qwen-asr-input`，import 时使用 `qwen_asr_input`。

这是一个 flat package layout，没有额外的 `src` 目录。麦克风资源放在 Python 包里，并作为 package data 一起打包，安装后仍然可以找到。

## 目前的限制

当前版本有几个需要提前知道的地方：

- 只支持 X11，Wayland 还没有对应的 `TextInjector` 实现。
- 流式中间结果只显示在浮层里，输入框只接收最终句子。
- 上一次录音没有结束前，新的录音请求会被拒绝，避免识别结果插入错误的窗口。
- 目前只在 Ubuntu X11 下测试，其他 Linux 发行版没有测试。
- 项目没有设置登录后自动启动。

如果你正好在 Ubuntu X11 下，需要一个按住说话、松开后直接输入的工具，可以先从 `./qwen-asr-input check` 和前台 `run` 模式开始试。确认文字注入、API Key 和浮层都正常后，再切换成后台服务。

