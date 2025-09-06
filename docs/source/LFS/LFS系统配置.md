# LFS 系统配置

我们现在讨论配置文件和 systemd 服务

## 1. 一般网络配置

systemd 提供一个名为 systemd-networkd 的网络配置守护进程，它能够用于基础网络配置。

Udev 一般根据系统物理特征为网卡分配接口名，例如 enp2s1

### 1.1 创建 networkd 配置目录

```bash
mkdir -pv /etc/systemd/network
```

### 1.2 写入 DHCP 配置文件

```bash
cat > /etc/systemd/network/10-eth0.network << "EOF"
[Match]
Name=ens160

[Network]
DHCP=yes
EOF
```

> 注意：接口名 `ens160` 要和 `ifconfig` 里看到的一样。如果你的接口名是别的，就替换。

### 1.3 设置主机名

```bash
echo "lfs" > /etc/hostname
```

### 1.4 配置 hosts 文件

```bash
cat > /etc/hosts << "EOF"
127.0.0.1   localhost
127.0.1.1   lfs.localdomain lfs
EOF
```

### 1.5 启用服务（开机生效）

```bash
systemctl enable systemd-networkd
systemctl enable systemd-resolved
```

### 1.6建立 resolv.conf 链接

```bash
ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf
```

## 2. 配置系统时钟

在 LFS 系统中，需要配置 **系统时钟** 与 **硬件时钟** 的关系，以及系统时区。LFS 使用 `systemd-timedated` 来统一管理时钟。

---

### 2.1 检查当前时间

```bash
date
hwclock --localtime --show
```

* `date` 显示的是 **系统时钟**（软件层，受时区影响）。
* `hwclock` 显示的是 **硬件时钟（RTC）**。

如果 `hwclock` 输出的时间与手表时间一致，说明 RTC 是以 **本地时间** 保存的；如果有差异，可能是以 **UTC** 保存的。

---

### 2.2 推荐方案：使用 UTC 保存硬件时钟

Linux 推荐将硬件时钟设置为 UTC，避免跨系统（特别是 Linux ↔ Linux）时区切换时出现时间错乱。

- 设置硬件时钟为 UTC

```bash
timedatectl set-local-rtc 0
```

- 设置时区（例如中国上海）

```bash
timedatectl set-timezone Asia/Shanghai
```

- 检查状态

```bash
timedatectl status
```

输出中应看到：

* `RTC in local TZ: no` → 表示硬件时钟为 UTC。
* `Time zone: Asia/Shanghai (CST, +0800)` → 表示时区已设置。

---

### 2.3 手动设置系统时间（如需要）

如果系统时间不正确，可以手动设置：

```bash
timedatectl set-time "YYYY-MM-DD HH:MM:SS"
```

同时硬件时钟也会被更新。

---

### 2.4 时区列表查询

如果需要设置其他时区，可以先列出可用时区：

```bash
timedatectl list-timezones
```

然后选择合适的时区，例如：

```bash
timedatectl set-timezone Europe/Berlin
```

## 3. 配置系统 Locale

* Locale 决定了 **程序输出的语言、字符集、货币格式、日期/时间显示** 等。
* 如果不设置，很多程序（包括 `ls`, `man`, `vim` 等）可能会出现乱码，或者提示找不到 locale。
* Glibc 在编译时已经安装了 locale 数据库，你现在需要选择一个默认的 locale。

### 3.1 查看支持的 locale

```bash
locale -a
```

你会看到一大串，比如：

```
C
C.UTF-8
POSIX
en_US.utf8
zh_CN.utf8
```

### 3.2 选择一个默认的 locale

* 如果你习惯英文界面，推荐：

```bash
echo "LANG=en_US.UTF-8" > /etc/locale.conf
```

* 如果你希望系统尽量显示中文，可以用：

```bash
echo "LANG=zh_CN.UTF-8" > /etc/locale.conf
```

> 注意：LFS 默认的 man-pages 和部分程序对中文支持不完整，用中文 locale 可能出现奇怪显示，所以新手推荐 **en\_US.UTF-8**。

## 4. 创建 /etc/inputrc 文件

inputrc 文件是 Readline 库的配置文件，该库在用户从终端输入命令行时提供编辑功能。

```text
cat > /etc/inputrc << "EOF"
# Begin /etc/inputrc
# Modified by Chris Lynn <roryo@roryo.dynup.net>

# Allow the command prompt to wrap to the next line
set horizontal-scroll-mode Off

# Enable 8-bit input
set meta-flag On
set input-meta On

# Turns off 8th bit stripping
set convert-meta Off

# Keep the 8th bit for display
set output-meta On

# none, visible or audible
set bell-style none

# All of the following map the escape sequence of the value
# contained in the 1st argument to the readline specific functions
"\eOd": backward-word
"\eOc": forward-word

# for linux console
"\e[1~": beginning-of-line
"\e[4~": end-of-line
"\e[5~": beginning-of-history
"\e[6~": end-of-history
"\e[3~": delete-char
"\e[2~": quoted-insert

# for xterm
"\eOH": beginning-of-line
"\eOF": end-of-line

# for Konsole
"\e[H": beginning-of-line
"\e[F": end-of-line

# End /etc/inputrc
EOF
```

## 5. 创建 /etc/shells 文件

shells 文件包含系统登录 shell 的列表，应用程序使用该文件判断 shell 是否合法。

该文件中每行指定一个 shell，包含该 shell 相对于目录树根 (/) 的路径。

```text
cat > /etc/shells << "EOF"
# Begin /etc/shells

/bin/sh
/bin/bash

# End /etc/shells
EOF
```

## 6. Systemd 使用和配置

### 6.1 禁用引导时自动清屏

默认情况下，systemd 会在内核消息打印完毕后清屏。

如果你希望 保留启动日志 在屏幕上，可以执行：

```text
mkdir -pv /etc/systemd/system/getty@tty1.service.d
cat > /etc/systemd/system/getty@tty1.service.d/noclear.conf << "EOF"
[Service]
TTYVTDisallocate=no
EOF
```

这样重启时不会清屏，可以看到内核和启动过程的完整输出。

### 6.2 处理核心转储

为了限制核心转储使用的最大磁盘空间，可以在 /etc/systemd/coredump.conf.d 中创建一个配置文件。例如：

```text
mkdir -pv /etc/systemd/coredump.conf.d

cat > /etc/systemd/coredump.conf.d/maxuse.conf << EOF
[Coredump]
MaxUse=5G
EOF
```
