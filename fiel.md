

## 题目要求：

**设计一个网络规划，使虚拟机和物理机在一个比 C 类更小的子网中，能互相 ping 通。**

---

## 设计思路：

* 选择 `192.168.50.0/28` 小子网（比 C 类 `/24` 更小）
* 使用 **VMware Host-only 网络（VMnet1）** 直连物理机与虚拟机
* 手动设置静态 IP，避免 DHCP 干扰
* 开启 Windows 防火墙 ICMP 入站规则，允许被 ping

---

## 操作步骤简要：

| 主机      | 网络接口   | IP 地址        | 子网掩码                  |
| ------- | ------ | ------------ | --------------------- |
| Windows | VMnet1 | 192.168.50.1 | 255.255.255.240 (/28) |
| Fedora  | ens160 | 192.168.50.2 | 255.255.255.240 (/28) |

**Fedora 命令：**

```bash
nmcli con modify ens160 ipv4.addresses 192.168.50.2/28
nmcli con modify ens160 ipv4.method manual
nmcli con up ens160
```

**Windows 命令（管理员 PowerShell）：**

```powershell
netsh advfirewall firewall add rule name="允许Ping" protocol=icmpv4:8,any dir=in action=allow
```

---

## 操作结果：

* Windows 可 ping Fedora：`ping 192.168.50.2` ✅
* Fedora 可 ping Windows：`ping 192.168.50.1` ✅
* **符合题目要求的小子网互通设计**

---



