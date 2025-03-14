你可以通过两种方式修改 Fedora Server 的 IP 地址：

- 方法一：临时修改（立即生效，但重启失效）
- 方法二：永久修改（重启后依然有效）

下面分别讲解：

---

## 一、临时修改 IP 地址（立即生效，重启失效）

1. 查看当前网络接口名：

```bash
ip addr
```

通常接口名类似于：`ens33` 或 `enp3s0`。

2. 临时修改 IP 地址（示例）：

假如接口名为 `enp3s0`，目标 IP 为 `192.168.1.100`：

```bash
sudo ip addr flush dev enp3s0
sudo ip addr add 192.168.1.100/24 dev enp3s0
sudo ip link set enp3s0 up
```

3. 设置默认网关（如需）：

假设网关为 `192.168.1.1`：

```bash
sudo ip route add default via 192.168.1.1
```

但**重启后以上配置将失效**。

---

## 二、永久修改 IP 地址（推荐）

Fedora Server 默认使用 `NetworkManager` 进行网络管理：

### 操作步骤：

1. 查看网络连接名称：

```bash
nmcli connection show
```

输出示例：

```
NAME    UUID                                  TYPE      DEVICE
enp3s0  c3b8f98e-xxxx-xxxx-xxxx-xxxxxxxxxxxx  ethernet  enp3s0
```

记住连接名（比如 `enp3s0`）。

2. 修改 IP 地址（举例）：

假如：

- IP 地址改为：`192.168.1.100`
- 子网掩码：`255.255.255.0` (即 `/24`)
- 网关：`192.168.1.1`
- DNS：`8.8.8.8` 和 `1.1.1.1`

执行命令：

```bash
sudo nmcli connection modify enp3s0 ipv4.addresses 192.168.1.100/24
sudo nmcli connection modify enp3s0 ipv4.gateway 192.168.1.1
sudo nmcli connection modify enp3s0 ipv4.dns "8.8.8.8 1.1.1.1"
sudo nmcli connection modify enp3s0 ipv4.method manual
```

3. 应用配置：

```bash
sudo nmcli connection down enp3s0
sudo nmcli connection up enp3s0
```

此时新的 IP 就生效了，且永久有效。

---

## 三、检查新的 IP 是否生效

执行：

```bash
ip addr
ping -c 3 www.baidu.com
```

确认 IP 正确且网络正常。

---

以上即可完成 Fedora Server IP 地址修改。
