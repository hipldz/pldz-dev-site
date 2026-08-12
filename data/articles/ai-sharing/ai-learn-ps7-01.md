---
author: pldz1
category: ai-sharing
csdn: ''
date: '2026-08-11'
gitee: ''
github: ''
juejin: ''
serialNo: 2
status: publish
summary: 之前给大家分享了Codex这样的AI Agent, 那这些AI Agent跑起来用到的PS语法，是不是也可以一起学习学习呢? 哈哈, 接下来和大家一起了解一下常用的PS语法.
tags:
  - AI
  - Codex
  - Windows PowerShell
thumbnail: /api/v1/website/image/ai-sharing/ai-learn-ps-01-thumbnail.webp
title: 跟着AI Agent学powershell
---


# 跟着AI Agent学powershell

之前，让codex配置了Windows的powershell版本到7之后，这里分享一些实用的ps的用法给大家

前排提示, powershell在windows上和 Windows terminal搭配起来 复用效果更好.

> 下面的内容包含了 AI的扩展，但是推荐大家阅读的已经打了 ⭐ 号标记

---

希望大家阅读完重点内容能回答这5个问题 哈哈哈

1. 共享配置：$PROFILE 里用什么语法加载 shared-profile.ps1？

2. 切换终端：在 PowerShell 里输入什么进入 CMD？

3. 特有配置：关闭 PSReadLine 命令预测用什么命令？

4. Linux 类似命令：PowerShell 7 里查看当前路径，可以直接输入什么？

5. 特有指令：查询本机 8080 端口用什么 PowerShell 命令？


---


## ⭐ 1. 共享配置

让 Windows PowerShell 5.1 和 PowerShell 7 共用同一套配置。

### `$PROFILE`

PowerShell 启动时会自动执行 `$PROFILE`。

可以查看当前 Profile 路径：

```powershell
$PROFILE
```

不同 PowerShell 版本的 `$PROFILE` 路径可能不同，因此不建议把所有配置分别复制到每个 Profile。

更适合的方式是：

```text
PS5 Profile ──┐
              ├── shared-profile.ps1
PS7 Profile ──┘
```

### Profile 内容

在 PowerShell 5.1 和 PowerShell 7 的 `$PROFILE` 中都写：

```powershell
. "$HOME\Documents\PowerShell\shared-profile.ps1"
```

`.` 是 PowerShell 的 dot-sourcing。

作用是：

```text
读取 shared-profile.ps1
并把其中定义的 function / alias / 设置
加载到当前 PowerShell 会话
```

这样以后只需要修改：

```text
shared-profile.ps1
```

PS5 和 PS7 都会使用新的配置。

---

# ⭐ 2. 在不同终端 / Shell 之间切换


![demo-gif](/api/v1/website/image/ai-sharing/ai-learn-ps-switch-tm-01.gif)

Windows Terminal 只是终端窗口。

里面可以运行不同 Shell：

```text
cmd
Windows PowerShell 5.1
PowerShell 7
Git Bash
WSL2 Ubuntu
```

很多时候不需要重新开窗口，直接在当前 Shell 中启动另一个 Shell 即可。

## PowerShell → Git Bash

自定义一个函数：

```powershell
function git-bash {
    & "D:\Git\bin\bash.exe" --login -i
}
```

因此可以直接：

```powershell
git-bash
```

进入 Git Bash。


## Shell 切换关系

可以把它理解成：

```text
Windows Terminal
       │
       ├── cmd
       │
       ├── powershell
       │      └── Windows PowerShell 5.1
       │
       ├── pwsh
       │      └── PowerShell 7
       │
       ├── git-bash
       │      └── Git Bash
       │
       └── wsl
              └── WSL2 Ubuntu
```

常用：

```text
当前 Shell              输入

PowerShell → CMD         cmd
CMD → PS5                powershell
CMD → PS7                pwsh
PS5 → PS7                pwsh
PS7 → PS5                powershell
PS → Git Bash            git-bash
PS / CMD → WSL           wsl
PS / CMD → Ubuntu        wsl -d Ubuntu
返回上一层                exit
```

---

# 3. PowerShell  特有配置与历史清理

## ⭐ 3.1 PS 7 关闭命令预测

PowerShell 的 PSReadLine 默认可能显示命令预测。


![auto-i](/api/v1/website/image/ai-sharing/ai-learn-ps7-autoi.webp)

例如输入：

```text
git
```

后面可能出现灰色预测内容。

如果不需要，而且觉得妨碍输入，可以关闭：

```powershell
Set-PSReadLineOption -PredictionSource None
```

已经放入：

```text
shared-profile.ps1
```

所以每次启动 PS5 / PS7 都会自动关闭。

---

## 3.2 PowerShell 的历史记录和 CMD 不完全一样

PowerShell 的历史至少要区分两个部分：

```text
PowerShell Session History
+
PSReadLine Persistent History
```

因此：

```powershell
Clear-History
```

并不一定等于：

```text
彻底删除以前输入过的所有命令
```

---

## 3.3 清理当前 PowerShell History

```powershell
Clear-History
```

查看：

```powershell
Get-History
```

---

## 3.4 PSReadLine 的磁盘历史

PSReadLine 会把历史保存到文件。

查看这个文件在哪里：

```powershell
(Get-PSReadLineOption).HistorySavePath
```

删除：

```powershell
(Get-PSReadLineOption).HistorySavePath |
    Remove-Item
```

为了避免文件不存在时报错：

```powershell
(Get-PSReadLineOption).HistorySavePath |
    Remove-Item -ErrorAction SilentlyContinue
```

---

## 3.5 清屏

```powershell
Clear-Host
```

也可以直接：

```powershell
cls
```

或者：

```powershell
clear
```

---

## 3.6 一次全部清理

定义：

```powershell
function Clear-All {
    Clear-Host
    Clear-History
    (Get-PSReadLineOption).HistorySavePath |
        Remove-Item -ErrorAction SilentlyContinue
}
```

再定义：

```powershell
Set-Alias cla Clear-All
```

以后：

```powershell
cla
```

相当于：

```text
清屏
+
清当前 PowerShell History
+
删除 PSReadLine 持久化历史
```

注意这里主要清理的是：

```text
命令历史
```

严格来说并不是传统意义上的系统 cache。

---

# 4. ⭐ 和 Linux / Bash 类似的常用命令

PowerShell 可以直接使用很多和 Bash 类似的名字。

## 当前路径

Bash：

```bash
pwd
```

PowerShell：

```powershell
pwd
```

本体：

```powershell
Get-Location
```

---

## 查看目录

```powershell
ls
```

PowerShell：

```powershell
Get-ChildItem
```

自定义：

```powershell
ll
```

也是：

```powershell
Get-ChildItem
```

查看隐藏文件：

```powershell
Get-ChildItem -Force
```

递归：

```powershell
Get-ChildItem -Recurse
```

---

## 切换目录

```powershell
cd D:\work
```

本体：

```powershell
Set-Location D:\work
```

---

## 查看文件

```powershell
cat file.txt
```

本体：

```powershell
Get-Content file.txt
```

前 20 行：

```powershell
Get-Content file.txt -Head 20
```

后 20 行：

```powershell
Get-Content file.txt -Tail 20
```

实时查看日志：

```powershell
Get-Content app.log -Tail 50 -Wait
```

类似：

```bash
tail -f app.log
```

---

## 复制

```powershell
cp file1 file2
```

本体：

```powershell
Copy-Item
```

---

## 移动 / 重命名

```powershell
mv old.txt new.txt
```

本体：

```powershell
Move-Item
```

---

## 删除

```powershell
rm file.txt
```

本体：

```powershell
Remove-Item
```

递归删除：

```powershell
Remove-Item folder -Recurse
```

---

## 创建目录

```powershell
mkdir test
```

也可以：

```powershell
New-Item -ItemType Directory test
```

---

## 进程 ps

可以：

```powershell
ps
```

PowerShell 本体：

```powershell
Get-Process
```

例如：

```powershell
ps
```

直接查看当前进程。

查询 Python：

```powershell
Get-Process python
```

---

## Kill

PowerShell：

```powershell
Stop-Process -Id 1234
```

或者：

```powershell
Stop-Process -Name python
```

强制：

```powershell
Stop-Process -Id 1234 -Force
```

---

## grep

PowerShell：

```powershell
Select-String "error" file.log
```

例如：

```powershell
Select-String "error" *.log
```

递归：

```powershell
Get-ChildItem -Recurse -File |
    Select-String "error"
```

---

## find

类似：

```bash
find . -name "*.txt"
```

PowerShell：

```powershell
Get-ChildItem -Recurse -Filter "*.txt"
```

---

## which

Bash：

```bash
which python
```

PowerShell 更推荐：

```powershell
Get-Command python
```

只看路径：

```powershell
(Get-Command python).Source
```

如果存在多个 Python：

```powershell
Get-Command python -All
```

Windows 自带命令也可以：

```powershell
where.exe python
```

---

## 查 Git / Python / Bash 在哪里

```powershell
Get-Command python
Get-Command pip
Get-Command git
Get-Command bash
Get-Command java
```

例如：

```powershell
(Get-Command python).Source
```

可以直接得到 Python executable 路径。

---

## 环境变量

类似 Bash：

```bash
echo $PATH
```

PowerShell：

```powershell
$env:PATH
```

查看全部：

```powershell
Get-ChildItem Env:
```

---

## 常见对应

```text
Linux / Bash        PowerShell

pwd                 pwd / Get-Location
ls                  ls / Get-ChildItem
cat                 cat / Get-Content
cd                  cd / Set-Location
cp                  cp / Copy-Item
mv                  mv / Move-Item
rm                  rm / Remove-Item
mkdir               mkdir / New-Item

ps                  ps / Get-Process
kill                Stop-Process

grep                Select-String
find                Get-ChildItem -Recurse
which               Get-Command
which -a            Get-Command -All

head                Get-Content -Head
tail                Get-Content -Tail
tail -f             Get-Content -Tail -Wait

sort                Sort-Object
uniq                Sort-Object -Unique
wc                  Measure-Object

ping                Test-Connection
dig                 Resolve-DnsName
traceroute          Test-NetConnection -TraceRoute
```

---

# 5. PowerShell 常用特有命令

这部分是 PowerShell 比单纯模仿 Linux 命令更有价值的地方。

---

## 5.1 查询程序在哪里

```powershell
Get-Command python
```

例如：

```powershell
Get-Command python
Get-Command pip
Get-Command git
Get-Command pwsh
Get-Command powershell
Get-Command bash
```

只取 executable 路径：

```powershell
(Get-Command python).Source
```

查看所有匹配项：

```powershell
Get-Command python -All
```

---

## 5.2 查询程序类型

例如：

```powershell
Get-Command python
```

可能显示：

```text
CommandType    Name          Source
-----------    ----          ------
Application    python.exe    ...
```

而：

```powershell
Get-Command ll
```

可能显示：

```text
Alias
```

```powershell
Get-Command git-bash
```

会显示：

```text
Function
```

因此 `Get-Command` 不只是 `which`，还能判断它究竟是：

```text
Application
Cmdlet
Function
Alias
Script
```

---

## 5.3 查询进程

```powershell
Get-Process
```

查 Python：

```powershell
Get-Process python
```

查 Chrome：

```powershell
Get-Process *chrome*
```

按照 CPU 时间排序：

```powershell
Get-Process |
    Sort-Object CPU -Descending |
    Select-Object -First 10 Name, Id, CPU
```

按照内存排序：

```powershell
Get-Process |
    Sort-Object WorkingSet -Descending |
    Select-Object -First 10 ProcessName,
        @{N='MemoryMB';E={[math]::Round($_.WorkingSet / 1MB, 1)}}
```

---

## 5.4 查询线程

指定 PID：

```powershell
(Get-Process -Id 1234).Threads
```

统计每个进程线程数量：

```powershell
Get-Process |
    Select-Object Id, ProcessName,
        @{N='Threads';E={$_.Threads.Count}} |
    Sort-Object Threads -Descending
```

---

## 5.5 查询 TCP 连接

```powershell
Get-NetTCPConnection
```

相当于 Linux 常用：

```bash
ss
```

或者：

```text
netstat
```

---

## 5.6 查询正在监听的端口

```powershell
Get-NetTCPConnection -State Listen
```

例如查 8080：

```powershell
Get-NetTCPConnection -LocalPort 8080
```

重要字段：

```text
LocalAddress
LocalPort
RemoteAddress
RemotePort
State
OwningProcess
```

---

## 5.7 查询哪个程序占用了端口

例如查 8080：

```powershell
Get-NetTCPConnection -LocalPort 8080
```

假设：

```text
OwningProcess = 1234
```

然后：

```powershell
Get-Process -Id 1234
```

也可以直接：

```powershell
Get-NetTCPConnection -LocalPort 8080 |
    ForEach-Object {
        Get-Process -Id $_.OwningProcess
    }
```

---

## 5.8 UDP

```powershell
Get-NetUDPEndpoint
```

---

## 5.9 测试端口能不能连接

例如：

```powershell
Test-NetConnection github.com -Port 443
```

数据库：

```powershell
Test-NetConnection localhost -Port 5432
```

Web 服务：

```powershell
Test-NetConnection localhost -Port 8080
```

这是排查：

```text
服务有没有开
端口有没有监听
防火墙有没有拦
网络能不能连通
```

时非常实用的命令。

---

## 5.10 Ping

```powershell
Test-Connection google.com
```

例如：

```powershell
Test-Connection google.com -Count 2
```

---

## 5.11 DNS

```powershell
Resolve-DnsName github.com
```

---

## 5.12 路由

```powershell
Test-NetConnection github.com -TraceRoute
```

---

## 5.13 Windows 服务

查看：

```powershell
Get-Service
```

查某类服务：

```powershell
Get-Service *docker*
```

启动：

```powershell
Start-Service sshd
```

停止：

```powershell
Stop-Service sshd
```

重启：

```powershell
Restart-Service sshd
```

---

## 5.14 查询对象有哪些属性

PowerShell 很重要的命令：

```powershell
Get-Member
```

例如：

```powershell
Get-Process | Get-Member
```

可以查看 `Get-Process` 输出对象拥有哪些：

```text
Property
Method
Member
```

如果不知道：

```text
“这个结果还能查什么？”
```

就可以：

```powershell
... | Get-Member
```

例如：

```powershell
Get-NetTCPConnection | Get-Member
```

---

## 5.15 对结果进行筛选

例如只看 CPU 大于 10 的进程：

```powershell
Get-Process |
    Where-Object CPU -gt 10
```

完整写法：

```powershell
Get-Process |
    Where-Object { $_.CPU -gt 10 }
```

---

## 5.16 选择字段

```powershell
Get-Process |
    Select-Object Id, ProcessName, CPU
```

---

## 5.17 排序

```powershell
Get-Process |
    Sort-Object CPU -Descending
```

---

## 5.18 只取前几个

```powershell
Get-Process |
    Select-Object -First 10
```

组合：

```powershell
Get-Process |
    Sort-Object CPU -Descending |
    Select-Object -First 10 Id, ProcessName, CPU
```

---

