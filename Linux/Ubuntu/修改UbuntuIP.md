在 Ubuntu 中修改 IP 地址，推荐使用 Netplan 工具。

## 步骤如下：

---

### 一、确认网卡名和配置文件：

1\. 首先查看你的网络接口名：

```bash
ip addr
```

通常接口名类似于 `ens33`、`enp3s0` 等。

---

### 二、编辑 Netplan 配置文件：

Ubuntu 默认使用 Netplan，配置文件位于：

```bash
/etc/netplan/
```

通常是：

- Ubuntu Server 一般为：`/etc/netplan/00-installer-config.yaml` 或 `50-cloud-init.yaml`
- Ubuntu Desktop 一般为：`01-network-manager-all.yaml`

例如编辑：

```bash
sudo vim /etc/netplan/00-installer-config.yaml
```

---

### 三、示例配置文件内容：

假设：

- 网卡名：`enp3s0`
- IP 地址：`192.168.1.200`
- 子网掩码：`255.255.255.0` (即 `/24`)
- 网关：`192.168.1.1`
- DNS：`8.8.8.8`、`1.1.1.1`

配置示例：

```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    enp3s0:
      addresses:
        - 192.168.1.200/24
      routes:
        - to: default
          via: 192.168.1.1
      nameservers:
        addresses: [ 8.8.8.8, 1.1.1.1 ]
```

**注意：** YAML格式对缩进敏感，建议复制后按原格式修改。

---

### 四、使配置生效：

```bash
sudo netplan apply
```

- 如果没有报错，说明配置生效成功。
- 可通过以下方式确认：

```bash
ip addr show enp3s0
ping -c 3 www.baidu.com
```

---

### 五、临时修改IP（仅临时生效，重启后失效）：

如果只是临时更改 IP：

```bash
sudo ip addr flush dev enp3s0
sudo ip addr add 192.168.1.200/24 dev enp3s0
sudo ip route add default via 192.168.1.1
```

重启后将失效。

---

以上方法适用于 Ubuntu 18.04 及更新版本（包括 20.04、22.04 和 24.02）。

