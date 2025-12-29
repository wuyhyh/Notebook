# openEuler稳定用户态配置手册

## 0. 环境概述

* 内核：`5.10.0-openeuler`（oebuild 工程里原始 BSP 内核）
* 根文件系统：openEuler 22.03 LTS SP4 Server 版本

    * 已安装到 `nvme0n1p2`（ext4）
    * U-Boot 启动参数使用：`root=/dev/nvme0n1p2 rw rootwait ...`
* 启动方式：从 `nvme0n1p2` 启动 BSP 内核 + Server 根文件系统

后面所有操作都默认在这套系统上进行。

---

## 1. root 密码同步（从 p1 系统复制）

在仍然可以正常启动的旧系统（p1 上的 embedded）里：

1. 挂载 p2 根分区：

```bash
mkdir -p /mnt/p2
mount /dev/nvme0n1p2 /mnt/p2
```

2. 从 p1 的 `/etc/shadow` 把 root 的哈希复制到 p2：

```bash
ROOT_LINE=$(grep '^root:' /etc/shadow)
echo "$ROOT_LINE"      # 确认一下内容正常

# 可选：备份 p2 的原来的 shadow
cp -a /mnt/p2/etc/shadow /mnt/p2/etc/shadow.bak

# 重建 p2 的 shadow，只保留这行 root
printf '%s\n' "$ROOT_LINE" > /mnt/p2/etc/shadow

chown root:root /mnt/p2/etc/shadow
chmod 0000 /mnt/p2/etc/shadow
```

3. 卸载：

```bash
umount /mnt/p2
```

之后从 `nvme0n1p2` 启动时，root 密码与 p1 系统一致，可以直接登录。

---

## 2. 网络配置：静态 IP + NetworkManager

### 2.1 临时拉起网络（首次使用）

第一次进新系统时，为了能用 dnf 装包，先手动起网（示例：PC/WSL IP 为 `192.168.11.100`，板子 eth1 为 `192.168.11.106`）：

```bash
ip addr flush dev eth1
ip link set eth1 up
ip addr add 192.168.11.106/24 dev eth1

ip route add default via 192.168.11.100 dev eth1

printf 'nameserver 223.5.5.5\nnameserver 114.114.114.114\n' > /etc/resolv.conf
```

确认：

```bash
ping -c 3 192.168.11.100
```

### 2.2 安装 NetworkManager

利用本地 ISO 仓库（下一节会讲怎么建 `oeiso-http`）：

```bash
dnf --disablerepo='*' --enablerepo='oeiso-http' install NetworkManager
systemctl enable NetworkManager
systemctl start NetworkManager
```

### 2.3 配置静态 IP（eth0=105, eth1=106）

手动创建配置目录：

```bash
mkdir -p /etc/sysconfig/network-scripts
```

`/etc/sysconfig/network-scripts/ifcfg-eth0`（备用口，不做默认路由）：

```ini
TYPE = Ethernet
NAME = eth0
DEVICE = eth0
ONBOOT = yes

BOOTPROTO = static
IPADDR = 192.168.11.105
PREFIX = 24

DEFROUTE = no
IPV4_FAILURE_FATAL = no
IPV6INIT = no
```

`/etc/sysconfig/network-scripts/ifcfg-eth1`（主口，有默认路由）：

```ini
TYPE = Ethernet
NAME = eth1
DEVICE = eth1
ONBOOT = yes

BOOTPROTO = static
IPADDR = 192.168.11.106
PREFIX = 24
GATEWAY = 192.168.11.100      # 这里按实际网关写，当前是接 PC/WSL

DNS1 = 223.5.5.5
DNS2 = 114.114.114.114

DEFROUTE = yes
IPV4_FAILURE_FATAL = no
IPV6INIT = no
```

重启 NetworkManager 使配置生效：

```bash
systemctl restart NetworkManager

ip a
ip route
```

检查：

* `eth0` 地址为 `192.168.11.105`，`eth1` 为 `192.168.11.106`
* 有默认路由：`default via 192.168.11.100 dev eth1`

重启整机验证网络能自动起来：

```bash
reboot
# 启动后
ip a
ip route
ping -c 3 192.168.11.100
```

---

## 3. 基于 PC ISO 的本地 dnf 仓库（oeiso-http）

由于板子内核不支持 iso9660，ISO 在 PC/WSL 上挂载，通过 HTTP 提供给板子使用。

### 3.1 在 PC/WSL 上挂载 ISO + 起 HTTP

假设 ISO 在 PC 的 `~/openEuler-22.03-LTS-SP4-everything-aarch64-dvd.iso`：

```bash
mkdir -p ~/oeiso
sudo mount -o loop ~/openEuler-22.03-LTS-SP4-everything-aarch64-dvd.iso ~/oeiso
ls ~/oeiso     # 确认有 repodata/ 和 Packages/
```

在 `~/oeiso` 目录下起 HTTP 服务（端口 8090）：

```bash
cd ~/oeiso
python3 -m http.server 8090
```

保持这个终端不关。

### 3.2 在开发板上配置本地仓库

确认开发板能访问 PC：

```bash
ping -c 3 192.168.11.100
curl http://192.168.11.100:8090/ | head
```

新建 `oeiso-http` 仓库文件 `/etc/yum.repos.d/oeiso-http.repo`：

```ini
[oeiso-http]
name = openEuler-everything-from-PC
baseurl = http://192.168.11.100:8090
enabled = 1
gpgcheck = 0
```

（如果 `repodata` 在 `OS/aarch64/` 下，则改成 `baseurl=http://192.168.11.100:8090/OS/aarch64`。）

之后所有安装包的命令统一使用：

```bash
dnf --disablerepo='*' --enablerepo='oeiso-http' install <packages...>
```

---

## 4. 安装开发/调试工具（当前这套 rootfs 已装过）

在开发板上利用 `oeiso-http` 仓库安装：

### 4.1 开发工具组

```bash
dnf --disablerepo='*' --enablerepo='oeiso-http' groupinstall "Development Tools"
```

### 4.2 内核/系统开发常用依赖

```bash
dnf --disablerepo='*' --enablerepo='oeiso-http' install \
    ncurses-devel \
    openssl-devel \
    elfutils-libelf-devel elfutils-libelf-devel-static \
    flex bison \
    bc \
    dwarves \
    perl \
    git \
    rsync \
    ccache \
    htop iotop \
    sysstat \
    iproute iputils \
    net-tools \
    tcpdump \
    wget curl
```

这些包保证你可以在板子上直接：

* 编译 Linux 内核 / 模块；
* 写/编译 C 程序、运行简单性能测试；
* 排查网络问题、查看系统负载。

---

## 5. SSH 登录加速配置

为解决 ssh 登录缓慢的问题，在开发板上修改 sshd 配置。

### 5.1 关闭 DNS / GSSAPI

编辑 `/etc/ssh/sshd_config`，增加或修改：

```text
UseDNS no
GSSAPIAuthentication no
```

保存后：

```bash
systemctl restart sshd
```

### 5.2 固定 /etc/hosts

避免本机名解析走外部 DNS，编辑 `/etc/hosts`，写上：

```text
127.0.0.1   localhost localhost.localdomain
192.168.11.106   localhost.localdomain localhost
::1         localhost localhost.localdomain
```

（第二行 IP 按你实际登录用的那个口填，这里假设用 eth1 的 `192.168.11.106`。）

---

## 6. 日常启动后的自检流程

以后每次开机可以按这个顺序快速检查系统是否“稳定就绪”：

1. 看内核版本：

   ```bash
   uname -a   # 确认是 5.10.0-openeuler
   ```

2. 网络：

   ```bash
   ip a
   ip route
   ping -c 3 192.168.11.100        # 到 PC/WSL
   curl http://192.168.11.100:8090/ | head   # 仓库可达
   ```

3. SSH：在 PC 上：

   ```bash
   ssh root@192.168.11.106
   ```

   应该很快就出现密码提示 + shell。

4. dnf 测试：

   ```bash
   dnf --disablerepo='*' --enablerepo='oeiso-http' list cmake
   ```

   能正常列出包说明本地仓库配置 OK。

---

后面你要做“稳定版本”的时候，可以把这份文档略微改造成 README/手册，给实习生按步骤操作：

* 先按“0+1”准备根文件系统和 root 密码；
* 再按“2+3”配置网络 + 本地仓库；
* 再按“4+5”把开发工具和 ssh 环境配好。

只要内核不换，这套用户态配置基本就是你现在这块板子“可用开发环境”的全部要素。

