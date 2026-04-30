# 01-journalctl与dmesg日志查看方法

## 1 文档目标

本文用于帮助实习生掌握 Linux 中常见日志查看方法，重点学习 `journalctl` 和 `dmesg` 的基本使用。

学习完本文后，应能完成以下任务：

1. 使用 `journalctl` 查看系统和服务日志
2. 使用 `dmesg` 查看内核日志
3. 按时间、服务、关键字过滤日志
4. 查看最近日志和实时日志
5. 根据日志进行简单问题排查

## 2 Linux 日志基础

## 2.1 为什么要看日志

日志用于记录系统、内核、服务和应用程序的运行情况。

常见用途包括：

1. 排查服务启动失败
2. 查看驱动加载情况
3. 查看设备识别情况
4. 分析网络异常
5. 分析系统启动过程

遇到问题时，不要只看现象，要先学会查日志。

## 2.2 journalctl 和 dmesg 的区别

| 工具           | 主要用途                      |
|--------------|---------------------------|
| `journalctl` | 查看 systemd 管理的系统日志、服务日志   |
| `dmesg`      | 查看内核环形缓冲区日志，常用于内核、驱动、硬件问题 |

简单理解：

```text
服务问题优先看 journalctl
内核和硬件问题优先看 dmesg
```

## 3 journalctl 基础

## 3.1 查看全部系统日志

```bash
journalctl
```

日志内容较多时，可以使用方向键、`PageUp`、`PageDown` 翻页。

退出查看界面：

```text
q
```

## 3.2 查看最近日志

查看最近 50 行日志：

```bash
journalctl -n 50
```

查看最近 100 行日志：

```bash
journalctl -n 100
```

## 3.3 实时查看日志

```bash
journalctl -f
```

该命令会持续输出新日志，适合一边操作一边观察系统反应。

退出实时查看：

```text
Ctrl + c
```

## 4 查看服务日志

## 4.1 查看指定服务日志

基本格式：

```bash
journalctl -u 服务名
```

示例：

```bash
journalctl -u sshd
```

查看 NetworkManager 日志：

```bash
journalctl -u NetworkManager
```

## 4.2 查看服务最近日志

```bash
journalctl -u 服务名 -n 50
```

示例：

```bash
journalctl -u sshd -n 50
```

## 4.3 实时查看服务日志

```bash
journalctl -u 服务名 -f
```

示例：

```bash
journalctl -u NetworkManager -f
```

适合观察服务重启、网络连接变化等过程。

## 5 按时间查看日志

## 5.1 查看本次启动以来的日志

```bash
journalctl -b
```

查看本次启动以来某个服务的日志：

```bash
journalctl -b -u 服务名
```

示例：

```bash
journalctl -b -u sshd
```

## 5.2 查看上一次启动的日志

```bash
journalctl -b -1
```

如果系统刚刚异常重启，可以用该命令查看上一次启动期间的日志。

## 5.3 查看指定时间范围日志

```bash
journalctl --since "2026-04-29 09:00:00"
```

查看某个时间段：

```bash
journalctl --since "2026-04-29 09:00:00" --until "2026-04-29 10:00:00"
```

也可以使用相对时间：

```bash
journalctl --since "10 minutes ago"
```

## 6 按关键字过滤日志

## 6.1 使用 grep 过滤

```bash
journalctl | grep 关键字
```

示例：

```bash
journalctl | grep error
```

查看某个服务日志中的错误：

```bash
journalctl -u sshd | grep failed
```

## 6.2 忽略大小写过滤

```bash
journalctl | grep -i error
```

`-i` 表示忽略大小写。

## 6.3 同时查看上下文

查看匹配行前后 3 行：

```bash
journalctl | grep -i -C 3 error
```

## 7 dmesg 基础

## 7.1 查看内核日志

```bash
dmesg
```

`dmesg` 常用于查看：

1. 内核启动日志
2. 驱动加载日志
3. 硬件识别日志
4. USB、PCIe、网卡、磁盘等设备日志

## 7.2 分页查看 dmesg

```bash
dmesg | less
```

退出：

```text
q
```

## 7.3 查看最近内核日志

```bash
dmesg | tail -n 50
```

查看最近 100 行：

```bash
dmesg | tail -n 100
```

## 7.4 实时查看内核日志

```bash
dmesg -w
```

退出：

```text
Ctrl + c
```

该命令适合观察插拔设备、加载驱动、网络状态变化等情况。

## 8 dmesg 常用过滤

## 8.1 查看错误日志

```bash
dmesg | grep -i error
```

也可以查找：

```bash
dmesg | grep -i fail
dmesg | grep -i warning
```

## 8.2 查看网卡相关日志

```bash
dmesg | grep -i eth
```

也可以根据驱动名查找：

```bash
dmesg | grep -i stmmac
```

## 8.3 查看 PCIe 相关日志

```bash
dmesg | grep -i pci
```

如果要查看 PCIe 错误，也可以使用：

```bash
dmesg | grep -i aer
```

## 8.4 查看磁盘和 NVMe 相关日志

```bash
dmesg | grep -i nvme
```

查看块设备相关日志：

```bash
dmesg | grep -i block
```

## 9 常见排查流程

## 9.1 服务启动失败

先查看服务状态：

```bash
systemctl status 服务名
```

再查看服务日志：

```bash
journalctl -u 服务名 -n 100
```

如果刚刚重启过服务，可以实时观察：

```bash
journalctl -u 服务名 -f
```

## 9.2 网络异常

查看网络服务状态：

```bash
systemctl status NetworkManager
```

查看网络服务日志：

```bash
journalctl -u NetworkManager -n 100
```

查看内核网卡日志：

```bash
dmesg | grep -i eth
```

或者根据驱动名称过滤：

```bash
dmesg | grep -i stmmac
```

## 9.3 设备没有识别

查看内核日志：

```bash
dmesg | tail -n 100
```

根据设备类型过滤：

```bash
dmesg | grep -i usb
dmesg | grep -i pci
dmesg | grep -i nvme
```

## 9.4 系统刚刚异常重启

查看本次启动日志：

```bash
journalctl -b
```

查看上一次启动日志：

```bash
journalctl -b -1
```

查看内核错误：

```bash
dmesg | grep -i -E "error|fail|panic|oops"
```

## 10 常见问题

## 10.1 journalctl 输出太多怎么办

可以限制输出行数：

```bash
journalctl -n 50
```

也可以指定服务：

```bash
journalctl -u 服务名 -n 50
```

## 10.2 dmesg 提示权限不足

部分系统上普通用户不能直接查看 `dmesg`。

可以使用：

```bash
sudo dmesg
```

如果要过滤：

```bash
sudo dmesg | grep -i error
```

## 10.3 日志中看到 failed 是否一定有问题

不一定。

需要结合上下文判断：

1. 是否影响当前功能
2. 是否反复出现
3. 是否和故障时间一致
4. 是否对应正在排查的设备或服务

不要只看到 `failed` 就认为系统一定坏了。

## 11 必须掌握的命令总结

| 命令                         | 作用               |
|----------------------------|------------------|
| `journalctl`               | 查看系统日志           |
| `journalctl -n 50`         | 查看最近 50 行系统日志    |
| `journalctl -f`            | 实时查看系统日志         |
| `journalctl -u 服务名`        | 查看指定服务日志         |
| `journalctl -u 服务名 -n 100` | 查看指定服务最近 100 行日志 |
| `journalctl -b`            | 查看本次启动日志         |
| `journalctl -b -1`         | 查看上一次启动日志        |
| `dmesg`                    | 查看内核日志           |
| `dmesg \| less`            | 分页查看内核日志         |
| `dmesg \| tail -n 100`     | 查看最近 100 行内核日志   |
| `dmesg -w`                 | 实时查看内核日志         |
| `dmesg \| grep -i pci`     | 查看 PCIe 相关内核日志   |

## 12 练习任务

## 12.1 查看系统最近日志

```bash
journalctl -n 50
```

观察最近系统日志中是否有错误或警告。

## 12.2 查看 SSH 服务日志

```bash
journalctl -u sshd -n 50
```

如果系统没有 `sshd` 服务，可以换成其他服务，例如：

```bash
journalctl -u NetworkManager -n 50
```

## 12.3 查看本次启动日志

```bash
journalctl -b -n 100
```

观察系统启动阶段是否有明显错误。

## 12.4 查看内核日志

```bash
dmesg | tail -n 100
```

查找错误信息：

```bash
dmesg | grep -i -E "error|fail|warning"
```

## 13 小结

日志排查的基本思路是：

```text
先看现象 → 找对应服务或设备 → 查 journalctl 或 dmesg → 按时间和关键字缩小范围
```

简单判断规则：

```text
服务问题：优先 journalctl -u 服务名
内核/驱动/硬件问题：优先 dmesg
刚刚发生的问题：看最近日志或实时日志
启动阶段的问题：看 journalctl -b 和 dmesg
```

实习生需要熟练掌握 `journalctl -u`、`journalctl -n`、`journalctl -f`、`dmesg | grep`、`dmesg -w` 这些常用命令。
