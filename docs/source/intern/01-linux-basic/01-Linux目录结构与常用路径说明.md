# Linux 目录结构与常用路径说明

## 文档目标

本文档用于帮助实习生理解 Linux 系统中的目录结构和常用路径。

完成本文档学习后，应能够：

1. 理解 Linux 文件系统从根目录 `/` 开始组织；
2. 说清楚 `/bin`、`/sbin`、`/etc`、`/usr`、`/var`、`/proc`、`/sys`、`/dev`、`/boot` 等目录的基本作用；
3. 区分真实磁盘文件系统和虚拟文件系统；
4. 理解 `/proc`、`/sys`、`/dev` 在内核、设备、驱动调试中的作用；
5. 知道开发板调试时常用的关键路径；
6. 能够根据问题类型快速判断应该查看哪些目录和文件。

本文档不是要求背诵所有 Linux 目录，而是要求建立基本判断能力：  
**遇到系统、启动、设备、驱动、网络、日志问题时，知道应该去哪里看。**

## Linux 文件系统的基本特点

Linux 的文件系统是一棵从根目录 `/` 开始的目录树。

可以使用以下命令查看根目录内容：

```bash
ls -lh /
```

典型输出中会看到类似目录：

```text
bin
boot
dev
etc
home
lib
lib64
mnt
opt
proc
root
run
sbin
sys
tmp
usr
var
```

Linux 中没有 Windows 里的 `C:`、`D:` 这种盘符概念。

在 Linux 中，不同磁盘、分区、设备、虚拟文件系统都可以通过 `mount` 挂载到某个目录下，统一表现为目录树的一部分。

例如：

```text
/dev/nvme0n1p2  挂载到 /
/dev/nvme0n1p1  挂载到 /boot
proc            挂载到 /proc
sysfs           挂载到 /sys
devtmpfs        挂载到 /dev
```

可以使用以下命令查看当前挂载情况：

```bash
mount
```

或者：

```bash
cat /proc/mounts
```

也可以查看磁盘和分区：

```bash
lsblk
df -h
```

## 根目录 /

根目录 `/` 是整个 Linux 文件系统的起点。

所有文件和目录都位于 `/` 下面，例如：

```text
/etc/passwd
/boot/Image
/dev/nvme0n1p2
/proc/cpuinfo
/sys/class/net
/home/user
```

查看根目录：

```bash
ls -lh /
```

根目录本身非常重要，不要在根目录下随意执行删除命令。

危险示例：

```bash
rm -rf /*
```

这类命令可能直接破坏整个系统。

在执行删除、移动、覆盖操作前，建议先确认当前目录：

```bash
pwd
ls -lh
```

## /bin 目录

`/bin` 用于存放基础用户命令。

常见命令包括：

```text
ls
cp
mv
rm
cat
mkdir
echo
sh
```

查看：

```bash
ls -lh /bin
```

在很多现代 Linux 发行版中，`/bin` 可能是指向 `/usr/bin` 的符号链接。

可以用以下命令查看：

```bash
ls -ld /bin
```

示例：

```text
/bin -> usr/bin
```

这表示 `/bin` 实际上链接到了 `/usr/bin`。

## /sbin 目录

`/sbin` 用于存放系统管理命令。

常见命令包括：

```text
ip
mount
reboot
shutdown
fsck
mkfs
```

查看：

```bash
ls -lh /sbin
```

和 `/bin` 类似，在现代发行版中，`/sbin` 可能是指向 `/usr/sbin` 的符号链接。

```bash
ls -ld /sbin
```

`/sbin` 中的命令通常用于系统管理，很多操作需要 root 权限。

例如：

```bash
sudo reboot
sudo mount /dev/nvme0n1p1 /mnt
```

## /usr 目录

`/usr` 用于存放大部分用户程序、库文件、头文件、文档等内容。

常见子目录：

```text
/usr/bin        普通用户程序
/usr/sbin       系统管理程序
/usr/lib        库文件
/usr/include    头文件
/usr/local      本地安装的软件
/usr/share      架构无关的数据和文档
```

查看：

```bash
ls -lh /usr
```

常见路径：

```bash
ls -lh /usr/bin
ls -lh /usr/sbin
ls -lh /usr/lib
ls -lh /usr/include
```

在开发环境中，很多工具位于 `/usr/bin`，例如：

```text
gcc
make
git
python
vim
```

可以使用 `which` 查看命令路径：

```bash
which gcc
which make
which git
```

示例输出：

```text
/usr/bin/gcc
/usr/bin/make
/usr/bin/git
```

## /usr/local 目录

`/usr/local` 通常用于存放本机手动安装的软件。

常见子目录：

```text
/usr/local/bin
/usr/local/sbin
/usr/local/lib
/usr/local/include
```

如果某些软件不是通过系统包管理器安装，而是手动编译安装，可能会安装到 `/usr/local` 下。

例如：

```bash
ls -lh /usr/local
ls -lh /usr/local/bin
```

在项目中，如果安装交叉编译工具链，也可能放在类似路径：

```text
/usr/local/gcc-arm64
/opt/toolchains
```

具体以项目规范为准。

## /opt 目录

`/opt` 通常用于存放第三方软件或手动部署的大型工具。

例如：

```text
/opt/toolchains
/opt/qemu
/opt/gcc-arm
/opt/project-tools
```

查看：

```bash
ls -lh /opt
```

对于项目开发机，常见用途包括：

1. 存放交叉编译工具链；
2. 存放厂商 SDK；
3. 存放临时验证工具；
4. 存放不适合放进系统目录的软件。

使用 `/opt` 时应注意保持目录命名清晰，避免随意堆放文件。

## /etc 目录

`/etc` 用于存放系统配置文件。

这是 Linux 系统中非常重要的目录。

常见文件和目录：

```text
/etc/os-release              系统发行版信息
/etc/fstab                   文件系统挂载配置
/etc/passwd                  用户信息
/etc/group                   用户组信息
/etc/shadow                  用户密码哈希
/etc/hostname                主机名
/etc/hosts                   本地域名解析
/etc/resolv.conf             DNS 配置
/etc/ssh/                    SSH 服务配置
/etc/systemd/                systemd 配置
/etc/NetworkManager/         NetworkManager 配置
```

常用查看命令：

```bash
cat /etc/os-release
cat /etc/hostname
cat /etc/hosts
cat /etc/resolv.conf
cat /etc/fstab
```

修改 `/etc` 下配置文件前必须备份。

例如：

```bash
sudo cp /etc/fstab /etc/fstab.bak
sudo vim /etc/fstab
```

不要随意修改：

```text
/etc/fstab
/etc/passwd
/etc/shadow
/etc/sudoers
/etc/systemd/
```

这些文件修改错误可能导致系统无法启动、无法登录或服务异常。

## /home 目录

`/home` 是普通用户的家目录。

例如用户 `user` 的 home 目录通常是：

```text
/home/user
```

查看：

```bash
ls -lh /home
```

进入当前用户 home 目录：

```bash
cd ~
```

或者：

```bash
cd
```

查看当前 home 路径：

```bash
echo $HOME
```

普通用户的代码、文档、实验记录通常可以放在 home 目录下，例如：

```text
/home/user/workspace
/home/user/project
/home/user/logs
/home/user/board-report
```

建议实习生在自己的 home 目录下做练习，不要直接在系统目录中操作。

## /root 目录

`/root` 是 root 用户的家目录。

注意：`/root` 不是根目录。  
根目录是 `/`，root 用户家目录是 `/root`。

查看：

```bash
sudo ls -lh /root
```

普通用户通常没有权限直接访问 `/root`。

不要把普通项目文件随意放在 `/root` 下，除非项目规范明确要求。

## /tmp 目录

`/tmp` 用于存放临时文件。

查看：

```bash
ls -lh /tmp
```

特点：

1. 适合放临时测试文件；
2. 系统重启后文件可能被清理；
3. 不适合保存重要日志和长期数据。

示例：

```bash
mkdir -p /tmp/test
echo "hello" > /tmp/test/hello.txt
cat /tmp/test/hello.txt
```

实验完成后可以删除：

```bash
rm -rf /tmp/test
```

不要把长期需要保留的实验记录只放在 `/tmp` 下。

## /var 目录

`/var` 用于存放经常变化的数据。

常见子目录：

```text
/var/log        日志文件
/var/cache      缓存
/var/lib        程序运行数据
/var/tmp        临时数据
/var/run        运行时数据，很多系统中链接到 /run
```

查看：

```bash
ls -lh /var
```

常见日志路径：

```bash
ls -lh /var/log
```

根据发行版不同，日志文件可能包括：

```text
/var/log/messages
/var/log/syslog
/var/log/dmesg
/var/log/boot.log
```

如果系统使用 systemd，很多日志由 journal 管理，不一定直接写在普通文本文件中。

查看 systemd 日志：

```bash
journalctl -b
```

查看内核日志：

```bash
dmesg
```

查看 `/var/log` 大小：

```bash
du -sh /var/log
```

如果磁盘空间不足，`/var/log` 是需要重点检查的目录之一。

## /run 目录

`/run` 用于存放系统运行时数据。

常见内容包括：

```text
/run/systemd
/run/NetworkManager
/run/lock
/run/user
```

查看：

```bash
ls -lh /run
```

`/run` 中的数据通常由系统服务在运行时创建，重启后会重新生成。

一般不建议实习生手动修改 `/run` 下的内容。

## /boot 目录

`/boot` 用于存放系统启动相关文件。

在 ARM64 开发板或服务器系统中，常见内容包括：

```text
Image
vmlinuz-xxx
initramfs-xxx.img
dtb
dtbs
grub
efi
System.map
config-xxx
```

查看：

```bash
ls -lh /boot
```

对于 ARM64 开发板，尤其需要关注：

```text
/boot/Image
/boot/dtb/
/boot/dtb/xxx.dtb
```

有些系统可能使用：

```text
/boot/dtbs/
/boot/efi/
```

具体以实际系统为准。

开发板启动时，U-Boot 可能会从某个分区读取：

```text
Image
DTB
initramfs
```

这几个概念需要区分：

```text
Image       Linux 内核镜像
dtb         设备树二进制文件
rootfs      根文件系统
initramfs   早期用户态临时根文件系统
```

修改 `/boot` 下文件前必须备份。

示例：

```bash
sudo cp /boot/Image /boot/Image.bak
sudo cp /boot/dtb/pd2008-devboard-dsk.dtb /boot/dtb/pd2008-devboard-dsk.dtb.bak
```

不要在不确认启动方式的情况下随意覆盖：

```bash
sudo cp Image /boot/Image
sudo cp test.dtb /boot/dtb/pd2008-devboard-dsk.dtb
```

否则可能导致系统无法启动。

## /lib 目录

`/lib` 用于存放系统运行需要的库文件和内核模块。

常见内容：

```text
/lib/modules
/lib/firmware
```

查看：

```bash
ls -lh /lib
```

在很多现代发行版中，`/lib` 可能是指向 `/usr/lib` 的符号链接：

```bash
ls -ld /lib
```

## /lib/modules 目录

`/lib/modules` 用于存放不同内核版本对应的内核模块。

查看：

```bash
ls -lh /lib/modules
```

当前运行内核版本：

```bash
uname -r
```

模块目录应该与当前运行内核版本匹配。

例如：

```bash
uname -r
```

输出：

```text
5.10.0-custom
```

则对应模块目录应该存在：

```text
/lib/modules/5.10.0-custom
```

查看：

```bash
ls -lh /lib/modules/$(uname -r)
```

如果当前内核版本和 `/lib/modules` 不匹配，可能导致模块无法加载。

典型错误包括：

```text
module not found
invalid module format
```

开发板替换内核时，需要同时关注：

```text
/boot/Image
/boot/dtb/xxx.dtb
/lib/modules/<kernel-release>
```

## /lib/firmware 目录

`/lib/firmware` 用于存放设备固件文件。

查看：

```bash
ls -lh /lib/firmware
```

某些设备驱动加载时，会请求 firmware 文件。

如果 firmware 缺失，`dmesg` 中可能出现类似信息：

```text
failed to load firmware
Direct firmware load failed
```

可以搜索：

```bash
dmesg | grep -i firmware
```

对于网卡、无线网卡、GPU、NPU、DPU 等设备，firmware 文件可能很重要。

## /dev 目录

`/dev` 用于存放设备节点。

Linux 中很多设备会表现为文件，例如：

```text
/dev/nvme0n1
/dev/nvme0n1p1
/dev/ttyAMA0
/dev/null
/dev/zero
/dev/random
```

查看：

```bash
ls -lh /dev
```

常见设备节点：

```text
/dev/nvme0n1        NVMe 磁盘
/dev/nvme0n1p1      NVMe 第 1 个分区
/dev/nvme0n1p2      NVMe 第 2 个分区
/dev/sda            SATA/SCSI/USB 磁盘
/dev/sda1           第 1 个分区
/dev/ttyAMA0        ARM PL011 串口
/dev/ttyS0          传统串口
/dev/null           丢弃写入数据
/dev/zero           读取时返回 0
/dev/random         随机数设备
```

查看磁盘设备：

```bash
lsblk
ls -lh /dev/nvme*
```

查看串口设备：

```bash
ls -lh /dev/tty*
```

注意：

```bash
sudo dd if=image.img of=/dev/nvme0n1
```

这种命令会直接写磁盘，风险极高。  
没有明确要求时，不能执行。

## /proc 目录

`/proc` 是 procfs 虚拟文件系统，用于导出内核运行状态和进程信息。

它不是普通磁盘目录，里面的内容大部分由内核动态生成。

查看：

```bash
ls -lh /proc
```

常用文件：

```text
/proc/cpuinfo        CPU 信息
/proc/meminfo        内存信息
/proc/interrupts     中断信息
/proc/cmdline        当前内核启动参数
/proc/mounts         当前挂载信息
/proc/version        内核版本信息
/proc/modules        已加载模块
/proc/devices        已注册设备号
/proc/iomem          系统物理内存和 MMIO 资源分布
/proc/ioports        IO 端口资源，主要用于 x86 等平台
```

常用命令：

```bash
cat /proc/cpuinfo
cat /proc/meminfo
cat /proc/interrupts
cat /proc/cmdline
cat /proc/mounts
cat /proc/version
cat /proc/modules
cat /proc/iomem
```

查看进程信息：

```bash
ls /proc/1
cat /proc/1/status
```

其中 `/proc/1` 表示 PID 为 1 的进程。

查看当前 shell 进程：

```bash
echo $$
cat /proc/$$/status
```

在开发板调试中，`/proc/cmdline` 非常重要，因为它可以确认当前内核实际收到的启动参数。

```bash
cat /proc/cmdline
```

例如：

```text
console=ttyAMA1,115200 root=/dev/nvme0n1p2 rw rootwait
```

这可以帮助判断：

1. 根文件系统是不是预期分区；
2. console 参数是否正确；
3. 是否带了 `nr_cpus=`、`maxcpus=`、`init=` 等调试参数。

## /sys 目录

`/sys` 是 sysfs 虚拟文件系统，用于导出 Linux 设备模型、总线、驱动、设备、class 等信息。

它不是普通磁盘目录，而是内核动态生成的接口。

查看：

```bash
ls -lh /sys
```

常见目录：

```text
/sys/bus             总线
/sys/class           按类别组织的设备
/sys/devices         设备树状结构
/sys/block           块设备
/sys/module          已加载模块信息
/sys/firmware        固件相关信息
/sys/kernel          内核相关信息
```

查看总线：

```bash
ls /sys/bus
```

常见总线：

```text
platform
pci
usb
i2c
spi
mdio_bus
```

查看 platform 设备：

```bash
ls /sys/bus/platform/devices
```

查看 PCI 设备：

```bash
ls /sys/bus/pci/devices
```

查看网卡：

```bash
ls /sys/class/net
```

查看块设备：

```bash
ls /sys/block
```

查看模块：

```bash
ls /sys/module
```

通过 sysfs 可以判断很多设备和驱动问题。

例如查看网卡 `end0` 对应设备路径：

```bash
readlink -f /sys/class/net/end0
```

查看某个 PCI 设备：

```bash
ls -lh /sys/bus/pci/devices/
```

在驱动调试中，`/sys` 非常重要，因为设备、驱动、总线匹配关系通常可以在这里观察到。

## /mnt 目录

`/mnt` 通常用于临时挂载文件系统。

例如挂载某个分区：

```bash
sudo mount /dev/nvme0n1p1 /mnt
```

查看：

```bash
ls -lh /mnt
```

卸载：

```bash
sudo umount /mnt
```

在开发板调试中，可能会用 `/mnt` 临时挂载其他分区：

```bash
sudo mount /dev/nvme0n1p2 /mnt
ls -lh /mnt
```

注意：卸载前应确认没有进程正在使用该目录。

如果提示 busy，可以查看：

```bash
pwd
lsof +f -- /mnt
```

如果系统没有 `lsof`，可以先确认自己是否还在 `/mnt` 目录内：

```bash
pwd
cd /
sudo umount /mnt
```

## /media 目录

`/media` 常用于自动挂载 U 盘、移动硬盘等外部设备。

查看：

```bash
ls -lh /media
```

桌面 Linux 系统中，插入 U 盘后可能自动挂载到：

```text
/media/<user>/<disk-name>
```

服务器或开发板环境中，不一定使用 `/media`。

## /srv 目录

`/srv` 用于存放服务对外提供的数据。

例如：

```text
/srv/http
/srv/ftp
/srv/nfs
```

在普通开发板调试中使用较少。

如果项目搭建了 NFS、HTTP 文件服务器，可能会用到该目录。

## /lost+found 目录

`lost+found` 通常出现在 ext 文件系统的根目录下。

例如：

```text
/lost+found
```

或者某个挂载分区下：

```text
/mnt/lost+found
```

它用于文件系统检查修复时存放找回的文件片段。

不要随意删除。

## 真实文件系统和虚拟文件系统

Linux 中有些目录对应真实磁盘数据，有些目录是内核动态生成的虚拟文件系统。

常见真实文件系统目录：

```text
/etc
/home
/usr
/var
/boot
/opt
```

这些目录中的文件通常实际存储在磁盘分区上。

常见虚拟文件系统目录：

```text
/proc
/sys
/dev
/run
```

它们大多不是普通磁盘文件，而是内核或系统运行时生成的接口。

可以使用 `mount` 查看文件系统类型：

```bash
mount | grep " /proc "
mount | grep " /sys "
mount | grep " /dev "
```

典型结果：

```text
proc on /proc type proc
sysfs on /sys type sysfs
devtmpfs on /dev type devtmpfs
```

理解这一点非常重要。

例如：

```bash
cat /proc/cpuinfo
```

不是读取磁盘上的普通文本文件，而是通过 procfs 向内核查询 CPU 信息。

再例如：

```bash
ls /sys/class/net
```

不是查看磁盘里保存的网卡文件，而是查看当前内核识别到的网络设备。

## 开发板调试常用路径

在开发板上排查问题时，经常查看以下路径。

系统版本：

```bash
cat /etc/os-release
uname -a
```

启动参数：

```bash
cat /proc/cmdline
```

内核日志：

```bash
dmesg
journalctl -b
```

CPU 信息：

```bash
cat /proc/cpuinfo
lscpu
```

内存信息：

```bash
cat /proc/meminfo
free -h
```

中断信息：

```bash
cat /proc/interrupts
```

磁盘分区：

```bash
lsblk
blkid
df -h
cat /proc/mounts
```

启动文件：

```bash
ls -lh /boot
ls -lh /boot/dtb
```

内核模块：

```bash
uname -r
ls -lh /lib/modules/$(uname -r)
cat /proc/modules
```

网卡设备：

```bash
ls /sys/class/net
ip addr
ip link
```

PCI 设备：

```bash
ls /sys/bus/pci/devices
lspci
```

platform 设备：

```bash
ls /sys/bus/platform/devices
```

设备节点：

```bash
ls -lh /dev
lsblk
```

## 和启动流程相关的重要路径

开发板启动排查时，需要重点关注：

```text
/boot
/boot/dtb
/proc/cmdline
/lib/modules/$(uname -r)
/etc/fstab
```

这些路径分别用于回答不同问题。

当前使用的启动文件在哪里：

```bash
ls -lh /boot
ls -lh /boot/dtb
```

当前内核实际启动参数是什么：

```bash
cat /proc/cmdline
```

当前内核版本是什么：

```bash
uname -r
```

当前内核模块目录是否存在：

```bash
ls -lh /lib/modules/$(uname -r)
```

根文件系统挂载是否正确：

```bash
cat /proc/mounts
df -h
lsblk
```

开机挂载配置是否正确：

```bash
cat /etc/fstab
```

注意：`/boot` 中存在某个 Image 或 dtb，不代表当前启动一定使用了它。  
必须结合 U-Boot 环境变量、启动命令、`/proc/cmdline` 和实际启动日志判断。

## 和设备驱动相关的重要路径

驱动调试时，需要重点关注：

```text
/dev
/proc
/sys
/lib/modules
/lib/firmware
```

设备节点：

```bash
ls -lh /dev
```

设备是否被内核识别：

```bash
ls /sys/bus/platform/devices
ls /sys/bus/pci/devices
ls /sys/class/net
```

驱动模块是否加载：

```bash
cat /proc/modules
lsmod
```

如果系统没有 `lsmod`，可以使用：

```bash
cat /proc/modules
```

当前内核模块目录：

```bash
ls -lh /lib/modules/$(uname -r)
```

是否缺少 firmware：

```bash
dmesg | grep -i firmware
```

查看设备和驱动相关日志：

```bash
dmesg | grep -i error
dmesg | grep -i fail
dmesg | grep -i probe
```

网络驱动相关：

```bash
dmesg | grep -i eth
dmesg | grep -i phy
dmesg | grep -i stmmac
ls /sys/class/net
```

PCIe 相关：

```bash
dmesg | grep -i pci
ls /sys/bus/pci/devices
lspci
```

## 和网络调试相关的重要路径

网络调试时，需要关注：

```text
/sys/class/net
/etc/NetworkManager
/etc/resolv.conf
/proc/net
/run/NetworkManager
```

查看网卡：

```bash
ls /sys/class/net
ip link
ip addr
```

查看 DNS：

```bash
cat /etc/resolv.conf
```

查看 NetworkManager 配置：

```bash
ls -lh /etc/NetworkManager
```

查看 NetworkManager 状态：

```bash
systemctl status NetworkManager
journalctl -b -u NetworkManager
```

查看网络相关内核信息：

```bash
ls /proc/net
```

常见命令：

```bash
ip addr
ip route
ping -c 4 127.0.0.1
ping -c 4 <网关IP>
ping -c 4 8.8.8.8
ping -c 4 www.baidu.com
```

判断网络问题时，不要只说“网络不通”，应该说明：

1. 网卡是否存在；
2. link 是否 up；
3. 是否有 IP；
4. 是否有默认路由；
5. 是否能 ping 通网关；
6. 是否能 ping 通外部 IP；
7. 是否能解析域名。

## 和磁盘挂载相关的重要路径

磁盘和文件系统排查时，需要关注：

```text
/dev
/proc/mounts
/etc/fstab
/mnt
/boot
```

查看块设备：

```bash
lsblk
```

查看 UUID：

```bash
blkid
```

查看当前挂载：

```bash
mount
cat /proc/mounts
df -h
```

查看开机挂载配置：

```bash
cat /etc/fstab
```

临时挂载：

```bash
sudo mount /dev/nvme0n1p1 /mnt
ls -lh /mnt
```

卸载：

```bash
sudo umount /mnt
```

注意：不要随意格式化分区。

危险命令示例：

```bash
mkfs.ext4 /dev/nvme0n1p2
dd if=image.img of=/dev/nvme0n1
```

这类命令可能直接破坏系统。

## 常见路径速查表

| 路径 | 作用 | 常用命令 |
| --- | --- | --- |
| `/` | 根目录 | `ls -lh /` |
| `/bin` | 基础命令 | `ls -lh /bin` |
| `/sbin` | 系统管理命令 | `ls -lh /sbin` |
| `/usr` | 用户程序、库、头文件 | `ls -lh /usr` |
| `/usr/bin` | 常用程序 | `which gcc` |
| `/etc` | 系统配置 | `cat /etc/os-release` |
| `/home` | 普通用户家目录 | `cd ~` |
| `/root` | root 用户家目录 | `sudo ls /root` |
| `/tmp` | 临时文件 | `ls -lh /tmp` |
| `/var` | 可变数据 | `ls -lh /var` |
| `/var/log` | 日志文件 | `ls -lh /var/log` |
| `/run` | 运行时数据 | `ls -lh /run` |
| `/boot` | 启动文件 | `ls -lh /boot` |
| `/lib/modules` | 内核模块 | `ls /lib/modules/$(uname -r)` |
| `/lib/firmware` | 固件文件 | `ls /lib/firmware` |
| `/dev` | 设备节点 | `ls -lh /dev` |
| `/proc` | 内核运行状态 | `cat /proc/cpuinfo` |
| `/sys` | 设备模型 | `ls /sys/class/net` |
| `/mnt` | 临时挂载点 | `sudo mount ... /mnt` |
| `/opt` | 第三方软件 | `ls -lh /opt` |

## 常见问题排查时应该看哪里

系统版本不清楚：

```bash
cat /etc/os-release
uname -a
```

启动参数不清楚：

```bash
cat /proc/cmdline
```

不知道当前从哪个分区启动：

```bash
lsblk
df -h
cat /proc/mounts
```

不知道内核模块是否匹配：

```bash
uname -r
ls /lib/modules/$(uname -r)
```

不知道网卡是否识别：

```bash
ls /sys/class/net
ip link
dmesg | grep -i eth
```

不知道 PCIe 设备是否识别：

```bash
ls /sys/bus/pci/devices
lspci
dmesg | grep -i pci
```

不知道设备节点是否存在：

```bash
ls -lh /dev
```

不知道中断是否存在：

```bash
cat /proc/interrupts
```

不知道磁盘空间是否足够：

```bash
df -h
du -sh * | sort -h
```

不知道日志在哪里：

```bash
dmesg
journalctl -b
ls -lh /var/log
```

## 容易混淆的概念

根目录 `/` 和 root 用户家目录 `/root` 不是一回事。

```text
/       整个文件系统的根
/root   root 用户的 home 目录
```

`/bin` 和 `/usr/bin` 在现代系统中可能存在合并关系。

```bash
ls -ld /bin
ls -ld /usr/bin
```

`/proc` 和 `/sys` 不是普通磁盘目录，而是内核导出的虚拟文件系统。

`/dev/nvme0n1p2` 是设备节点，不是普通文件。  
对它写入数据可能直接修改磁盘分区。

`/boot` 中存在文件，不代表当前一定使用了该文件启动。  
实际启动文件需要结合 U-Boot 环境变量和启动日志判断。

`/lib/modules/<版本>` 必须和当前运行内核版本匹配。  
当前运行内核版本用以下命令查看：

```bash
uname -r
```

## 建议实习生必须熟悉的路径

第一阶段必须熟悉：

```text
/
/home
/etc
/var/log
/boot
/dev
/proc
/sys
/lib/modules
/mnt
/tmp
```

第二阶段需要逐步熟悉：

```text
/usr
/usr/bin
/usr/include
/usr/lib
/opt
/lib/firmware
/sys/bus
/sys/class
/sys/devices
/proc/interrupts
/proc/iomem
```

第三阶段结合驱动开发进一步学习：

```text
/sys/bus/platform/devices
/sys/bus/pci/devices
/sys/class/net
/sys/module
/lib/modules/$(uname -r)/build
/lib/modules/$(uname -r)/kernel
```

## 实验任务

请在 Linux 开发机或开发板上完成以下实验。

第一部分：查看根目录和常见目录。

```bash
pwd
ls -lh /
ls -lh /etc
ls -lh /usr
ls -lh /var
ls -lh /boot
ls -lh /dev
ls -lh /proc
ls -lh /sys
```

第二部分：判断真实文件系统和虚拟文件系统。

```bash
mount | grep " /proc "
mount | grep " /sys "
mount | grep " /dev "
cat /proc/mounts | head -n 30
```

第三部分：查看系统和启动信息。

```bash
cat /etc/os-release
uname -a
cat /proc/cmdline
ls -lh /boot
ls -lh /lib/modules
ls -lh /lib/modules/$(uname -r)
```

第四部分：查看设备和驱动相关路径。

```bash
ls /sys/bus
ls /sys/class/net
ls /sys/bus/platform/devices | head
ls /sys/bus/pci/devices
cat /proc/interrupts
cat /proc/modules
```

第五部分：查看磁盘和挂载信息。

```bash
lsblk
blkid
df -h
mount
cat /proc/mounts
```

第六部分：整理路径观察记录。

创建实验目录：

```bash
mkdir -p ~/linux-path-test/report
```

保存命令输出：

```bash
ls -lh / > ~/linux-path-test/report/root-ls.txt
ls -lh /etc > ~/linux-path-test/report/etc-ls.txt
ls -lh /boot > ~/linux-path-test/report/boot-ls.txt
ls -lh /dev > ~/linux-path-test/report/dev-ls.txt
ls -lh /proc > ~/linux-path-test/report/proc-ls.txt
ls -lh /sys > ~/linux-path-test/report/sys-ls.txt

mount > ~/linux-path-test/report/mount.txt
cat /proc/mounts > ~/linux-path-test/report/proc-mounts.txt
cat /etc/os-release > ~/linux-path-test/report/os-release.txt
uname -a > ~/linux-path-test/report/uname.txt
cat /proc/cmdline > ~/linux-path-test/report/cmdline.txt
lsblk > ~/linux-path-test/report/lsblk.txt
df -h > ~/linux-path-test/report/df-h.txt
cat /proc/interrupts > ~/linux-path-test/report/interrupts.txt
cat /proc/modules > ~/linux-path-test/report/modules.txt
```

打包：

```bash
tar -czvf ~/linux-path-test/report.tar.gz -C ~/linux-path-test report
```

## 提交要求

提交以下内容：

```text
linux-path-test/
├── report/
│   ├── root-ls.txt
│   ├── etc-ls.txt
│   ├── boot-ls.txt
│   ├── dev-ls.txt
│   ├── proc-ls.txt
│   ├── sys-ls.txt
│   ├── mount.txt
│   ├── proc-mounts.txt
│   ├── os-release.txt
│   ├── uname.txt
│   ├── cmdline.txt
│   ├── lsblk.txt
│   ├── df-h.txt
│   ├── interrupts.txt
│   └── modules.txt
├── report.tar.gz
└── summary.md
```

`summary.md` 需要包含：

```text
1. 当前系统版本是什么？
2. 当前内核版本是什么？
3. 当前根文件系统挂载在哪个分区？
4. 当前系统是否存在 /boot 目录？里面主要有哪些文件？
5. 当前系统是否存在 /lib/modules/$(uname -r) 目录？
6. 当前系统有哪些网络接口？
7. /proc 和 /sys 分别是什么类型的文件系统？
8. 你认为 /dev、/proc、/sys 三个目录有什么区别？
9. 本次实验中不理解的路径或概念有哪些？
```

## 验收标准

验收时重点检查以下内容：

1. 是否理解 Linux 文件系统从 `/` 开始组织；
2. 是否能说清楚 `/etc`、`/boot`、`/dev`、`/proc`、`/sys`、`/lib/modules` 的基本作用；
3. 是否能区分真实磁盘文件系统和虚拟文件系统；
4. 是否能通过 `/proc/cmdline` 查看当前启动参数；
5. 是否能通过 `/lib/modules/$(uname -r)` 判断内核模块目录是否匹配；
6. 是否能通过 `/sys/class/net` 查看当前网络接口；
7. 是否能通过 `lsblk`、`df -h`、`cat /proc/mounts` 查看磁盘和挂载状态；
8. 是否能按要求保存命令输出，而不是只截图；
9. `summary.md` 是否能用自己的话说明关键路径的作用。

通过本文档学习后，实习生应能够对 Linux 目录结构建立基本认识，并能够在系统调试、开发板启动排查、驱动问题分析中找到常用路径。
