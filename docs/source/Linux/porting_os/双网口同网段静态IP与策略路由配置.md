# 双口同网段（eth0/eth1）静态双 IP + 策略路由配置

本文总结整套配置流程、关键参数与设计理由，适用于你的嵌入式平台：同一 SoC 上有两张网卡（eth0 与 eth1），都接入同一二层网段
`192.168.11.0/24`，要求：

* eth1 为主用链路（优先级高）；
* eth0 为备用链路（主链路失效时接管）；
* 两个接口各自拥有不同的 IP，并可作为服务端各自对外提供服务；
* 启动阶段不再因 DHCP 超时而卡顿。

---

## 1. 背景与问题

* **双口同网段的固有问题**：如果按“普通静态路由”配置两口在同一子网，常出现“从 eth1 发出带着 eth0
  的源地址”或“回包从不期望的接口进入”，触发内核的反向路径检查（rp_filter）与 ARP-flux，表现为 `martian source`
  日志泛滥、邻居表混乱、偶发丢包。
* **目标**：既要并存两张网卡的两个不同 IP，又要保证**路径对称**（哪个源地址从哪张网卡出去、回包从同一口回来），并实现**主备优先级
  **与**故障切换**。

对应的解决思路是：

1. **停用 DHCP，改为静态地址**，消除启动时的 DHCP 超时等待；
2. **基于源地址的策略路由（Policy Routing）**，绑定“源→出口”关系；
3. **主路由表设置双默认路由 + metric 区分优先级**；
4. 适当的 **sysctl** 调整（rp_filter、ARP 行为）以避免误判与 ARP-flux。

---

## 2. 配置总览

### 2.1 停用 DHCP，使用静态 IP

* 不再在 `/etc/network/interfaces` 中出现 `iface ... inet dhcp`；
* 使用静态地址与固定 DNS；
* 作用：启动时不会再拉起 DHCP 客户端、不会等待超时，网络在引导过程内快速就绪。

### 2.2 基于源地址的策略路由（关键）

* 为每个源地址建立一张**独立路由表**，例如：

    * CPU0：`table 106` 仅服务源 `192.168.11.106`（eth1），`table 105` 仅服务源 `192.168.11.105`（eth0）
    * CPU1：`table 108` 仅服务源 `192.168.11.108`（eth1），`table 107` 仅服务源 `192.168.11.107`（eth0）
* 通过 `ip rule add from <源IP>/32 table <表号>` 把“从该源发起的流量”**强制**查对应表，再由该表指向正确的出口（子网路由 +
  默认路由）。
* 结果：**哪个源，就从对应接口出去**，回程也会沿着对应接口返回，解决“martian source/ARP-flux”。

### 2.3 主路由表的默认路由优先级（metric）

* 在**主路由表**保留两条默认路由：

    * `default via 192.168.11.1 dev eth1 metric 100`（主用）
    * `default via 192.168.11.1 dev eth0 metric 200`（备用）
* 作用：

    * 对于系统自身未显式指定源的流量（DNS/NTP/更新器等），优先走 eth1；
    * 当 eth1 down 时，eth1 的默认路由自动消失，主机仍能通过 eth0（metric 更大）对外连通，实现**主备切换**。

### 2.4 sysctl 参数（rp_filter 与 ARP 行为）

* `rp_filter=0`：放宽反向路径检查，避免双口同网段下被误判为可疑来源；
* `arp_ignore=1`、`arp_announce=2`：降低 ARP-flux，避免“eth0 帮 eth1 的 IP 回答 ARP”等异常。

---

## 3. 最终配置文件（示例）

> 说明：以下为**模板**与**实例**。接口名若与你系统不同（如 enpXsY），请替换成实际名称。
> DNS 可按现场环境调整。注释为英文、精简，便于后续协作阅读。

### 3.1 CPU1（已落地并通过测试）

`/etc/network/interfaces`

```text
auto lo
iface lo inet loopback

# Primary uplink: eth1 (preferred path, IP 192.168.11.108)
auto eth1
iface eth1 inet static
address 192.168.11.108
netmask 255.255.255.0
gateway 192.168.11.1
metric 100
# Source-based routing for 192.168.11.108
post-up ip rule add from 192.168.11.108/32 table 108 priority 1000 2>/dev/null || true
post-up ip route replace 192.168.11.0/24 dev eth1 proto static table 108
post-up ip route replace default via 192.168.11.1 dev eth1 table 108
# Main table prefers eth1
post-up ip route replace default via 192.168.11.1 dev eth1 metric 100
pre-down ip rule del from 192.168.11.108/32 table 108 2>/dev/null || true
pre-down ip route flush table 108 2>/dev/null || true

# Secondary uplink: eth0 (backup path, IP 192.168.11.107)
auto eth0
iface eth0 inet static
address 192.168.11.107
netmask 255.255.255.0
metric 200
# Source-based routing for 192.168.11.107
post-up ip rule add from 192.168.11.107/32 table 107 priority 1001 2>/dev/null || true
post-up ip route replace 192.168.11.0/24 dev eth0 proto static table 107
post-up ip route replace default via 192.168.11.1 dev eth0 table 107
# Backup default route in main table
post-up ip route replace default via 192.168.11.1 dev eth0 metric 200
pre-down ip rule del from 192.168.11.107/32 table 107 2>/dev/null || true
pre-down ip route flush table 107 2>/dev/null || true
```

`/etc/sysctl.conf`

```text
# Relax reverse path filtering for dual-NIC same-subnet policy routing
net.ipv4.conf.all.rp_filter=0
net.ipv4.conf.eth0.rp_filter=0
net.ipv4.conf.eth1.rp_filter=0

# Reduce ARP flux across multiple NICs in the same subnet
net.ipv4.conf.all.arp_ignore=1
net.ipv4.conf.default.arp_ignore=1
net.ipv4.conf.all.arp_announce=2
net.ipv4.conf.default.arp_announce=2
```

`/etc/resolv.conf`

```
nameserver 223.5.5.5
nameserver 8.8.8.8
```

### 3.2 CPU0（对等配置）

`/etc/network/interfaces`

```text
auto lo
iface lo inet loopback

# Primary uplink: eth1 (preferred path, IP 192.168.11.106)
auto eth1
iface eth1 inet static
address 192.168.11.106
netmask 255.255.255.0
gateway 192.168.11.1
metric 100
# Source-based routing for 192.168.11.106
post-up ip rule add from 192.168.11.106/32 table 106 priority 1000 2>/dev/null || true
post-up ip route replace 192.168.11.0/24 dev eth1 proto static table 106
post-up ip route replace default via 192.168.11.1 dev eth1 table 106
# Main table prefers eth1
post-up ip route replace default via 192.168.11.1 dev eth1 metric 100
pre-down ip rule del from 192.168.11.106/32 table 106 2>/dev/null || true
pre-down ip route flush table 106 2>/dev/null || true

# Secondary uplink: eth0 (backup path, IP 192.168.11.105)
auto eth0
iface eth0 inet static
address 192.168.11.105
netmask 255.255.255.0
metric 200
# Source-based routing for 192.168.11.105
post-up ip rule add from 192.168.11.105/32 table 105 priority 1001 2>/dev/null || true
post-up ip route replace 192.168.11.0/24 dev eth0 proto static table 105
post-up ip route replace default via 192.168.11.1 dev eth0 table 105
# Backup default route in main table
post-up ip route replace default via 192.168.11.1 dev eth0 metric 200
pre-down ip rule del from 192.168.11.105/32 table 105 2>/dev/null || true
pre-down ip route flush table 105 2>/dev/null || true
```

`/etc/sysctl.conf` 与 `resolv.conf` 与 CPU1 保持一致。

---

## 4. 生效步骤与自检

### 4.1 一次性生效

```bash
# 写完 /etc/sysctl.conf 后
sysctl -p

# 停 DHCP 客户端（如存在）
pkill dhclient 2>/dev/null || true

# 重新加载网络
ifdown eth1 eth0 2>/dev/null || true
ifup eth1
ifup eth0
```

### 4.2 自检命令（任一 CPU 上）

```bash
# IP 与链路
ip -4 addr show dev eth1
ip -4 addr show dev eth0

# 规则与路由表
ip rule
ip route show              # 主表：应有两条 default（eth1 metric 100，eth0 metric 200）
ip route show table 106    # 或 108/107/105：应含 192.168.11.0/24 与 default via 对应接口
ip route show table 105

# 路径对称性测试（把 192.168.11.100 换成对端主机）
ping -c2 -I 192.168.11.106 192.168.11.100
ping -c2 -I 192.168.11.105 192.168.11.100
```

预期：

* 不再出现 `martian source` 日志；
* `-I .106` 的流量经 eth1，`-I .105` 的流量经 eth0；
* 拔掉 eth1 后，主表中 eth1 的默认路由消失，仍可通过 eth0 对外联通。

---

### 4.3 固化到 SSD

```text
scp -P 2223 wuyuhang@192.168.11.100:~/downloads/board_network_conf/cpu0/sysctl.conf ./
```

```text
scp -P 2223 wuyuhang@192.168.11.100:~/downloads/board_network_conf/cpu0/resolv.conf ./
```

```text
scp -P 2223 wuyuhang@192.168.11.100:~/downloads/board_network_conf/cpu0/interfaces ./
```

## 5. 参数解释（为什么这样配置）

| 项                       | 配置                                                          | 作用/理由                                               |
|-------------------------|-------------------------------------------------------------|-----------------------------------------------------|
| 静态 IP                   | `iface ethX inet static`                                    | 取消 DHCP，消除引导期超时等待；稳定可控。                             |
| 源地址策略路由                 | `ip rule add from <IP>/32 table <T>`                        | 把“源→表”绑定，保证出/回路径对称，解决双口同网段的非对称路由与 `martian source`。 |
| 子网/默认路由（分表）             | `ip route ... table <T>`                                    | 在各自表里声明同网段直连与各自的默认路由，明确出口接口。                        |
| 主路由表双默认                 | `default via ... dev eth1 metric 100`；`dev eth0 metric 200` | 为系统“未显式绑定源”的流量提供路径选择，eth1 优先，eth1 down 自动切 eth0。    |
| rp_filter               | `=0`                                                        | 放宽反向路径检查，避免双口同网段的合法报文被误判。                           |
| arp_ignore/arp_announce | `1/2`                                                       | 降低 ARP-flux，避免错误的 ARP 回答与地址宣告导致邻居表混乱。               |
| resolv.conf             | 固定 DNS                                                      | 停用 DHCP 后由系统自己管理 DNS，避免运行时被覆盖。                      |

---

## 6. 常见问题与扩展

* **为什么不直接用 bonding？**
  你需要“两口两个不同 IP 并行对外提供服务”以及“主备切换”。bonding 的 active-backup 虽然能做单 IP 失效切换，但天然只会使用*
  *一条口**接收/发送，不适合“两 IP 并行对外”。策略路由更匹配你的需求。

* **同网段一定要关 rp_filter 吗？**
  在同网段多口的拓扑里，不放宽 rp_filter 往往会遇到 “martian source” 告警甚至丢包。若后续将两个接口放入**不同网段或不同
  VLAN**，可以重新打开严格的 rp_filter。

* **如果未来切换到不同网段/VLAN？**
  只需把各接口的 `address/netmask` 分到不同子网，并相应调整各自表内的子网路由；这样可以不再改 `rp_filter`/ARP 参数，配置更简洁。

* **应用层注意事项**
  若服务需要同时在两个 IP 上对外提供（如同一个端口绑定两个地址），应用需分别 `bind(192.168.11.10x)`；客户端应访问对应的
  IP，从而自然命中对应接口与策略表。

---

## 7. 回滚与排错

* 回滚：将 `/etc/network/interfaces` 恢复为备份，或临时手动清表再测试：

  ```bash
  ip rule del from 192.168.11.106/32 table 106 2>/dev/null || true
  ip rule del from 192.168.11.105/32 table 105 2>/dev/null || true
  ip route flush table 106 2>/dev/null || true
  ip route flush table 105 2>/dev/null || true
  ```
* 若仍见 `martian source`：确认 `sysctl -a | egrep 'rp_filter|arp_ignore|arp_announce'` 为预期值；确认 `ip rule`
  生效且无重复/冲突；确认接口名与配置一致。
* 若 DNS 异常：检查 `/etc/resolv.conf` 是否被指向 `/run/*` 的动态文件；在静态模式下应当是文件本身。

---

## 8. 小结

* 关键是**策略路由**保证“源→出口”绑定、**metric** 落实主备优先级、**sysctl** 消除同网段多口的误判与 ARP 纷争；
* 该方案在不依赖外部交换机配合（如 LACP）的前提下，实现了**双 IP 并行 + 主备切换**，并且**启动无 DHCP 阻塞**、行为可预测、易于排查与维护。

