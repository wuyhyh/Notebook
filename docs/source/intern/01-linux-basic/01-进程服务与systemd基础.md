# 01-进程服务与systemd基础

## 1 文档目标

本文用于帮助实习生理解 Linux 中的进程、服务和 `systemd` 基础用法，能够完成常见的进程查看、服务状态检查、服务启动停止、开机自启配置等操作。

学习完本文后，应能完成以下任务：

1. 查看系统中的进程
2. 理解进程和服务的区别
3. 使用 `systemctl` 查看服务状态
4. 启动、停止、重启服务
5. 设置服务开机自启
6. 查看服务日志

## 2 进程基础

## 2.1 什么是进程

进程是正在运行的程序。

例如执行：

```bash
vim test.txt
```

此时 `vim` 就是一个正在运行的进程。

一个程序文件本身只是磁盘上的文件，只有运行起来之后，才会变成进程。

## 2.2 查看当前终端进程

```bash
ps
```

常见输出：

```text
PID TTY          TIME CMD
1234 pts/0    00:00:00 bash
1250 pts/0    00:00:00 ps
```

其中：

| 字段 | 含义 |
|---|---|
| `PID` | 进程 ID |
| `TTY` | 所属终端 |
| `TIME` | 占用 CPU 时间 |
| `CMD` | 启动命令 |

## 2.3 查看系统所有进程

```bash
ps aux
```

常用过滤方式：

```bash
ps aux | grep ssh
```

用于查找和 `ssh` 相关的进程。

## 2.4 动态查看进程

```bash
top
```

`top` 可以动态查看 CPU、内存和进程状态。

退出 `top`：

```text
q
```

## 3 进程常用操作

## 3.1 查找进程 PID

```bash
ps aux | grep 进程名
```

示例：

```bash
ps aux | grep nginx
```

也可以使用：

```bash
pgrep nginx
```

## 3.2 结束进程

使用 PID 结束进程：

```bash
kill PID
```

如果进程无法正常退出，可以使用：

```bash
kill -9 PID
```

注意：`kill -9` 是强制结束进程，不建议作为首选方式。

## 3.3 查看进程树

```bash
pstree
```

如果系统没有该命令，可以安装：

```bash
sudo dnf install psmisc
```

## 4 服务基础

## 4.1 什么是服务

服务通常是长期在后台运行的程序。

例如：

| 服务 | 作用 |
|---|---|
| `sshd` | 提供 SSH 远程登录 |
| `NetworkManager` | 管理网络连接 |
| `chronyd` | 时间同步 |
| `docker` | 容器服务 |

服务本质上也是进程，只是通常由系统统一管理。

## 4.2 进程和服务的区别

| 项目 | 进程 | 服务 |
|---|---|---|
| 含义 | 正在运行的程序 | 后台长期运行的系统程序 |
| 管理方式 | `ps`、`kill` | `systemctl` |
| 是否开机自启 | 不一定 | 可以设置 |
| 示例 | `vim`、`bash` | `sshd`、`NetworkManager` |

## 5 systemd 基础

## 5.1 systemd 是什么

`systemd` 是 Linux 系统中常见的系统和服务管理器。

它负责：

1. 启动系统
2. 管理系统服务
3. 管理开机自启
4. 收集服务日志
5. 处理服务依赖关系

在 openEuler、CentOS、Fedora、Ubuntu 等发行版中，通常都使用 `systemd`。

## 5.2 systemctl 是什么

`systemctl` 是操作 `systemd` 的常用命令。

基本格式：

```bash
systemctl 操作 服务名
```

示例：

```bash
systemctl status sshd
```

表示查看 `sshd` 服务状态。

## 6 查看服务状态

## 6.1 查看单个服务状态

```bash
systemctl status 服务名
```

示例：

```bash
systemctl status sshd
```

常见状态：

| 状态 | 含义 |
|---|---|
| `active (running)` | 正在运行 |
| `inactive` | 未运行 |
| `failed` | 启动失败 |
| `enabled` | 已设置开机自启 |
| `disabled` | 未设置开机自启 |

## 6.2 查看所有正在运行的服务

```bash
systemctl list-units --type=service --state=running
```

## 6.3 查看所有服务文件

```bash
systemctl list-unit-files --type=service
```

## 7 启动、停止和重启服务

## 7.1 启动服务

```bash
sudo systemctl start 服务名
```

示例：

```bash
sudo systemctl start sshd
```

## 7.2 停止服务

```bash
sudo systemctl stop 服务名
```

示例：

```bash
sudo systemctl stop sshd
```

## 7.3 重启服务

```bash
sudo systemctl restart 服务名
```

示例：

```bash
sudo systemctl restart NetworkManager
```

## 7.4 重新加载配置

有些服务支持不停止进程而重新加载配置：

```bash
sudo systemctl reload 服务名
```

如果不确定是否支持，可以使用：

```bash
sudo systemctl restart 服务名
```

## 8 开机自启管理

## 8.1 设置开机自启

```bash
sudo systemctl enable 服务名
```

示例：

```bash
sudo systemctl enable sshd
```

## 8.2 取消开机自启

```bash
sudo systemctl disable 服务名
```

示例：

```bash
sudo systemctl disable sshd
```

## 8.3 立即启动并设置自启

```bash
sudo systemctl enable --now 服务名
```

示例：

```bash
sudo systemctl enable --now sshd
```

表示立即启动 `sshd`，并设置开机自启。

## 9 查看服务日志

## 9.1 查看某个服务日志

```bash
journalctl -u 服务名
```

示例：

```bash
journalctl -u sshd
```

## 9.2 查看最近日志

```bash
journalctl -u 服务名 -n 50
```

表示查看最近 50 行日志。

## 9.3 实时查看日志

```bash
journalctl -u 服务名 -f
```

类似于：

```bash
tail -f
```

用于观察服务运行过程中的实时输出。

## 10 常见服务检查示例

## 10.1 检查 SSH 服务

```bash
systemctl status sshd
```

如果没有运行：

```bash
sudo systemctl start sshd
```

设置开机自启：

```bash
sudo systemctl enable sshd
```

## 10.2 检查网络服务

```bash
systemctl status NetworkManager
```

重启网络服务：

```bash
sudo systemctl restart NetworkManager
```

查看日志：

```bash
journalctl -u NetworkManager -n 50
```

## 11 常见问题

## 11.1 systemctl 提示权限不足

普通用户查看服务状态通常可以直接执行：

```bash
systemctl status 服务名
```

但启动、停止、重启服务通常需要管理员权限：

```bash
sudo systemctl restart 服务名
```

## 11.2 服务启动失败怎么办

建议按照以下顺序排查：

1. 查看服务状态
2. 查看服务日志
3. 检查配置文件是否写错
4. 修改配置后重启服务

常用命令：

```bash
systemctl status 服务名
journalctl -u 服务名 -n 100
```

## 11.3 start 和 enable 有什么区别

| 命令 | 作用 |
|---|---|
| `start` | 立即启动服务 |
| `enable` | 设置开机自启 |
| `enable --now` | 立即启动并设置开机自启 |

`start` 只影响当前运行状态，不代表下次开机会自动启动。

## 12 必须掌握的命令总结

| 命令                           | 作用 |
|------------------------------|---|
| `ps`                         | 查看当前终端进程 |
| `ps aux`                     | 查看系统所有进程 |
| `ps aux \| grep name`        | 查找进程 |
| `top`                        | 动态查看进程 |
| `kill PID`                   | 结束进程 |
| `systemctl status 服务名`       | 查看服务状态 |
| `sudo systemctl start 服务名`   | 启动服务 |
| `sudo systemctl stop 服务名`    | 停止服务 |
| `sudo systemctl restart 服务名` | 重启服务 |
| `sudo systemctl enable 服务名`  | 设置开机自启 |
| `sudo systemctl disable 服务名` | 取消开机自启 |
| `journalctl -u 服务名`          | 查看服务日志 |

## 13 练习任务

## 13.1 查看进程

```bash
ps
ps aux | head
top
```

进入 `top` 后按 `q` 退出。

## 13.2 查找 sshd 进程

```bash
ps aux | grep sshd
```

观察是否存在 `sshd` 相关进程。

## 13.3 查看 SSH 服务状态

```bash
systemctl status sshd
```

记录服务是否处于 `active (running)` 状态。

## 13.4 查看 NetworkManager 日志

```bash
journalctl -u NetworkManager -n 50
```

观察最近的网络服务日志。

## 14 小结

进程和服务的关系可以简单理解为：

```text
进程：正在运行的程序
服务：由 systemd 管理的后台进程
```

日常排查问题时，常用流程是：

```text
查看服务状态 → 查看服务日志 → 修改配置 → 重启服务 → 再次确认状态
```

实习生需要优先掌握 `ps`、`top`、`kill`、`systemctl`、`journalctl` 这几类命令。
