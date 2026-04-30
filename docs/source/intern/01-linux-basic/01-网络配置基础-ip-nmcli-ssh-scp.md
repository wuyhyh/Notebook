# 01-网络配置基础-ip-nmcli-ssh-scp

## 1 文档目标

本文用于帮助实习生掌握 Linux 中最基础的网络查看、网络配置、远程登录和文件传输方法。

学习完本文后，应能完成以下任务：

1. 使用 `ip` 查看网卡、IP 地址和路由
2. 使用 `ping` 测试网络连通性
3. 使用 `nmcli` 查看和配置网络连接
4. 使用 `ssh` 远程登录 Linux 主机
5. 使用 `scp` 在本机和远程主机之间传输文件
6. 完成开发板和 PC 之间的基础网络调试

## 2 网络基础概念

## 2.1 网卡是什么

网卡是系统连接网络的设备。

在 Linux 中，网卡通常有类似下面的名字：

| 网卡名 | 常见含义 |
|---|---|
| `eth0` | 传统以太网接口名 |
| `end0` | 某些系统中的以太网接口名 |
| `ens33` | 虚拟机或服务器中常见接口名 |
| `wlan0` | 无线网卡接口名 |
| `lo` | 本地回环接口 |

`lo` 是本机回环接口，一般不需要手动配置。

## 2.2 IP 地址是什么

IP 地址用于标识网络中的一台主机。

常见 IPv4 地址示例：

```text
192.168.1.100
10.0.0.5
172.16.0.10
```

同一个局域网内的设备，通常需要处于同一个网段。

例如：

```text
PC：    192.168.1.10
开发板：192.168.1.20
```

二者通常可以直接通信。

## 2.3 网关和 DNS 是什么

| 概念 | 作用 |
|---|---|
| 网关 | 访问其他网段或互联网时经过的出口 |
| DNS | 将域名解析为 IP 地址 |

如果只是 PC 和开发板直连测试，可以暂时不配置网关和 DNS。

如果需要访问互联网，通常需要配置网关和 DNS。

## 3 使用 ip 查看网络状态

## 3.1 查看网卡列表

```bash
ip link
```

常见输出中会看到：

```text
1: lo: ...
2: end0: ...
3: end1: ...
```

其中 `end0`、`end1` 这类接口通常是以太网网卡。

## 3.2 查看 IP 地址

```bash
ip addr
```

简写：

```bash
ip a
```

只查看某个网卡：

```bash
ip addr show end0
```

如果看到类似：

```text
inet 192.168.1.100/24
```

表示该网卡已经配置了 IPv4 地址。

## 3.3 查看路由

```bash
ip route
```

常见默认路由：

```text
default via 192.168.1.1 dev end0
```

表示访问外部网络时，通过 `192.168.1.1` 这个网关出去。

## 3.4 临时配置 IP 地址

临时给网卡配置 IP：

```bash
sudo ip addr add 192.168.1.100/24 dev end0
```

启用网卡：

```bash
sudo ip link set end0 up
```

删除临时 IP：

```bash
sudo ip addr del 192.168.1.100/24 dev end0
```

注意：使用 `ip` 命令配置的地址通常是临时的，重启后可能失效。

## 4 使用 ping 测试连通性

## 4.1 测试本机网络栈

```bash
ping 127.0.0.1
```

如果能通，说明本机网络协议栈基本正常。

## 4.2 测试局域网主机

```bash
ping 192.168.1.20
```

如果 PC 和开发板互相 ping 通，说明基础网络连通。

## 4.3 测试互联网

```bash
ping 8.8.8.8
```

如果能 ping 通 IP，但不能访问域名，可能是 DNS 问题。

测试域名：

```bash
ping www.baidu.com
```

## 5 nmcli 基础

## 5.1 nmcli 是什么

`nmcli` 是 NetworkManager 的命令行工具，用于查看和配置网络连接。

常见用途：

1. 查看网卡状态
2. 查看网络连接配置
3. 配置静态 IP
4. 启用或关闭网络连接
5. 配置网关和 DNS

## 5.2 查看设备状态

```bash
nmcli device status
```

常见字段：

| 字段 | 含义 |
|---|---|
| `DEVICE` | 网卡名称 |
| `TYPE` | 设备类型 |
| `STATE` | 当前状态 |
| `CONNECTION` | 使用的连接配置名称 |

## 5.3 查看连接配置

```bash
nmcli connection show
```

简写：

```bash
nmcli con show
```

每一条 connection 是 NetworkManager 保存的一份网络配置。

## 6 使用 nmcli 配置静态 IP

## 6.1 查看当前连接名称

```bash
nmcli con show
```

假设连接名称是 `end0`，网卡也是 `end0`。

## 6.2 配置静态 IP

```bash
sudo nmcli con mod end0 ipv4.addresses 192.168.1.100/24
```

配置网关：

```bash
sudo nmcli con mod end0 ipv4.gateway 192.168.1.1
```

配置 DNS：

```bash
sudo nmcli con mod end0 ipv4.dns "114.114.114.114 8.8.8.8"
```

设置为手动配置模式：

```bash
sudo nmcli con mod end0 ipv4.method manual
```

重新启用连接：

```bash
sudo nmcli con down end0
sudo nmcli con up end0
```

## 6.3 只配置直连 IP

如果只是 PC 和开发板网线直连，可以不配置网关和 DNS。

例如开发板配置：

```bash
sudo nmcli con mod end0 ipv4.addresses 192.168.10.20/24
sudo nmcli con mod end0 ipv4.method manual
sudo nmcli con down end0
sudo nmcli con up end0
```

PC 配置为：

```text
192.168.10.10/24
```

然后在 PC 上测试：

```bash
ping 192.168.10.20
```

## 6.4 改回 DHCP 自动获取 IP

```bash
sudo nmcli con mod end0 ipv4.method auto
sudo nmcli con mod end0 ipv4.addresses ""
sudo nmcli con mod end0 ipv4.gateway ""
sudo nmcli con mod end0 ipv4.dns ""
sudo nmcli con down end0
sudo nmcli con up end0
```

DHCP 适合连接到路由器，由路由器自动分配 IP。

## 7 ssh 远程登录

## 7.1 ssh 是什么

`ssh` 用于远程登录 Linux 主机。

常见场景：

1. PC 登录开发板
2. PC 登录服务器
3. 在远程主机上执行命令
4. 远程查看日志和修改配置

## 7.2 基本登录命令

```bash
ssh 用户名@IP地址
```

示例：

```bash
ssh root@192.168.1.100
```

或者：

```bash
ssh user@192.168.1.100
```

首次连接时可能提示是否信任主机，输入：

```text
yes
```

然后输入远程用户密码。

## 7.3 指定端口登录

默认 SSH 端口是 `22`。

如果远程主机使用其他端口，例如 `2222`：

```bash
ssh -p 2222 user@192.168.1.100
```

## 7.4 退出 SSH 登录

在远程终端中输入：

```bash
exit
```

或者按：

```text
Ctrl + d
```

## 8 scp 文件传输

## 8.1 scp 是什么

`scp` 用于通过 SSH 在本机和远程主机之间复制文件。

基本格式：

```bash
scp 源路径 目标路径
```

远程路径格式：

```text
用户名@IP地址:远程路径
```

## 8.2 从本机复制文件到远程主机

```bash
scp local.txt user@192.168.1.100:/home/user/
```

表示将本机 `local.txt` 复制到远程主机 `/home/user/` 目录。

## 8.3 从远程主机复制文件到本机

```bash
scp user@192.168.1.100:/home/user/remote.txt ./
```

表示将远程主机上的 `remote.txt` 复制到当前目录。

## 8.4 复制目录

复制目录需要加 `-r`：

```bash
scp -r testdir user@192.168.1.100:/home/user/
```

从远程复制目录到本机：

```bash
scp -r user@192.168.1.100:/home/user/testdir ./
```

## 8.5 指定 SSH 端口传输

如果 SSH 端口不是 22，例如 2222：

```bash
scp -P 2222 local.txt user@192.168.1.100:/home/user/
```

注意：`ssh` 指定端口使用小写 `-p`，`scp` 指定端口使用大写 `-P`。

## 9 常见排查流程

## 9.1 ping 不通怎么办

建议按顺序检查：

1. 网线是否连接
2. 网卡是否启用
3. IP 是否配置正确
4. 双方是否在同一网段
5. 防火墙是否阻挡
6. 目标主机是否在线

常用命令：

```bash
ip link
ip addr
ip route
ping 目标IP
```

## 9.2 ssh 登录不上怎么办

先确认网络是否通：

```bash
ping 目标IP
```

再确认 SSH 服务是否运行：

```bash
systemctl status sshd
```

如果没有运行：

```bash
sudo systemctl start sshd
```

查看 SSH 日志：

```bash
journalctl -u sshd -n 50
```

## 9.3 scp 失败怎么办

先确认 SSH 是否能登录：

```bash
ssh user@目标IP
```

再检查路径是否存在：

```bash
ls
pwd
```

如果复制到系统目录，可能需要权限：

```bash
scp file user@目标IP:/tmp/
```

先复制到 `/tmp/`，再登录远程主机后使用 `sudo mv` 移动。

## 10 常见问题

## 10.1 ip addr 看不到 IP 地址

可能原因：

1. 网线未连接
2. 网卡没有启用
3. DHCP 没有获取到地址
4. NetworkManager 没有管理该网卡
5. 静态 IP 配置错误

可以先尝试启用连接：

```bash
sudo nmcli con up 连接名
```

## 10.2 配置静态 IP 后无法上网

需要检查：

1. 是否配置了网关
2. 是否配置了 DNS
3. 默认路由是否正确
4. 网线是否连接到可上网的路由器或交换机

查看默认路由：

```bash
ip route
```

测试网关：

```bash
ping 192.168.1.1
```

测试 DNS：

```bash
ping www.baidu.com
```

## 10.3 可以 ping IP 但不能 ping 域名

通常是 DNS 问题。

可以通过 `nmcli` 配置 DNS：

```bash
sudo nmcli con mod end0 ipv4.dns "114.114.114.114 8.8.8.8"
sudo nmcli con down end0
sudo nmcli con up end0
```

## 11 必须掌握的命令总结

| 命令 | 作用 |
|---|---|
| `ip link` | 查看网卡状态 |
| `ip addr` | 查看 IP 地址 |
| `ip route` | 查看路由 |
| `sudo ip link set end0 up` | 启用网卡 |
| `ping 目标IP` | 测试网络连通性 |
| `nmcli device status` | 查看 NetworkManager 设备状态 |
| `nmcli con show` | 查看连接配置 |
| `sudo nmcli con mod end0 ipv4.addresses 192.168.1.100/24` | 配置静态 IP |
| `sudo nmcli con mod end0 ipv4.method manual` | 设置手动 IP 模式 |
| `sudo nmcli con up end0` | 启用连接 |
| `ssh user@192.168.1.100` | 远程登录 |
| `ssh -p 2222 user@192.168.1.100` | 指定端口远程登录 |
| `scp file user@192.168.1.100:/home/user/` | 上传文件 |
| `scp user@192.168.1.100:/home/user/file ./` | 下载文件 |
| `scp -r dir user@192.168.1.100:/home/user/` | 上传目录 |

## 12 练习任务

## 12.1 查看本机网络状态

```bash
ip link
ip addr
ip route
```

记录当前网卡名称、IP 地址和默认路由。

## 12.2 测试网络连通性

测试本机：

```bash
ping 127.0.0.1
```

测试局域网主机：

```bash
ping 目标IP
```

测试域名：

```bash
ping www.baidu.com
```

## 12.3 使用 nmcli 查看连接

```bash
nmcli device status
nmcli con show
```

记录当前连接名称和网卡名称。

## 12.4 配置直连静态 IP

在开发板上配置：

```bash
sudo nmcli con mod end0 ipv4.addresses 192.168.10.20/24
sudo nmcli con mod end0 ipv4.method manual
sudo nmcli con down end0
sudo nmcli con up end0
```

在 PC 上配置同网段 IP，例如：

```text
192.168.10.10/24
```

然后测试：

```bash
ping 192.168.10.20
```

## 12.5 使用 ssh 和 scp

远程登录：

```bash
ssh user@192.168.10.20
```

上传文件：

```bash
scp test.txt user@192.168.10.20:/home/user/
```

下载文件：

```bash
scp user@192.168.10.20:/home/user/test.txt ./
```

## 13 小结

Linux 网络排查的基本顺序是：

```text
看网卡 → 看 IP → 看路由 → ping 测试 → 查服务 → 查日志
```

常用命令可以分为四类：

```text
查看网络：ip link、ip addr、ip route
配置网络：nmcli
远程登录：ssh
文件传输：scp
```

实习生需要优先掌握 `ip addr`、`ip route`、`ping`、`nmcli con show`、`nmcli con mod`、`ssh`、`scp` 这些命令。
