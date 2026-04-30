# Linux 常用命令入门

## 文档目标

本文档用于帮助实习生掌握 Linux 下最基础、最高频的命令操作。

完成本文档学习后，应能够：

1. 在 Linux 系统中查看、切换、创建、复制、移动和删除文件；
2. 查看文本文件内容并搜索关键字；
3. 理解常见目录的基本用途；
4. 查看系统、磁盘、内存、CPU、进程等基础信息；
5. 使用基础网络命令判断网络状态；
6. 使用命令完成简单的问题排查和信息采集；
7. 按要求保存命令输出，形成可追溯的实验记录。

本文档不要求一次性记住所有命令，但要求能够理解命令的用途，并能在实际工作中正确使用。

## 学习要求

学习本文档时，不允许只阅读不操作。每个命令都应该在 Linux 开发机或开发板上实际执行。

执行命令时要注意：

1. 看清当前所在目录；
2. 看清操作对象；
3. 删除、覆盖、移动文件前必须确认路径；
4. 不要随意使用 `rm -rf /`、`chmod -R 777 /` 等危险命令；
5. 不理解命令含义时，不要在开发板或服务器上直接执行。

建议学习方式：

```bash
命令学习 → 实际执行 → 观察输出 → 记录现象 → 总结用途
```

## Linux 命令的基本格式

Linux 命令通常由三部分组成：

```bash
命令 选项 参数
```

例如：

```bash
ls -l /etc
```

含义是：

```text
ls      命令，表示列出目录内容
-l      选项，表示使用长格式显示
/etc    参数，表示要查看的目录
```

再例如：

```bash
cp -r dir1 dir2
```

含义是：

```text
cp      复制命令
-r      递归复制目录
dir1    源目录
dir2    目标目录
```

有些命令可以不带选项和参数，例如：

```bash
pwd
```

表示显示当前所在目录。

## 获取命令帮助

当不知道命令如何使用时，可以使用帮助命令。

查看简短帮助：

```bash
ls --help
cp --help
grep --help
```

查看手册：

```bash
man ls
man cp
man grep
```

在 `man` 页面中：

```text
方向键       上下滚动
/关键字      搜索关键字
n            跳到下一个搜索结果
q            退出
```

例如：

```bash
man ls
```

如果系统没有安装 `man`，可以先使用：

```bash
命令 --help
```

## 查看当前目录

查看当前所在目录：

```bash
pwd
```

示例输出：

```text
/home/user/project
```

含义是当前位于 `/home/user/project` 目录下。

这个命令非常重要。执行复制、删除、移动文件前，建议先执行：

```bash
pwd
```

确认自己当前在哪个目录。

## 列出目录内容

查看当前目录内容：

```bash
ls
```

以长格式显示：

```bash
ls -l
```

显示隐藏文件：

```bash
ls -a
```

以长格式显示所有文件，包括隐藏文件：

```bash
ls -la
```

显示文件大小并使用更容易阅读的单位：

```bash
ls -lh
```

查看指定目录：

```bash
ls -lh /boot
ls -lh /etc
ls -lh /lib/modules
```

常见输出示例：

```text
-rw-r--r-- 1 root root  1.2K Apr 28 10:00 config.txt
drwxr-xr-x 2 root root  4.0K Apr 28 10:00 test-dir
```

第一列含义：

```text
-       普通文件
d       目录
l       符号链接
```

权限含义：

```text
r       read，可读
w       write，可写
x       execute，可执行
```

## 切换目录

进入目录：

```bash
cd /etc
```

返回上一级目录：

```bash
cd ..
```

返回用户 home 目录：

```bash
cd ~
```

或者：

```bash
cd
```

返回上一次所在目录：

```bash
cd -
```

示例：

```bash
pwd
cd /boot
pwd
cd -
pwd
```

## Linux 常见目录说明

Linux 文件系统是从根目录 `/` 开始的一棵目录树。

常见目录如下：

```text
/               根目录
/bin            基础用户命令
/sbin           系统管理命令
/etc            系统配置文件
/home           普通用户家目录
/root           root 用户家目录
/lib            系统库文件
/usr            用户程序和库
/var            日志、缓存、运行时数据
/tmp            临时文件
/dev            设备节点
/proc           内核运行状态虚拟文件系统
/sys            设备和驱动信息虚拟文件系统
/boot           内核、dtb、initramfs 等启动文件
/mnt            临时挂载目录
/opt            第三方软件目录
```

在开发板和内核调试中，以下目录尤其重要：

```text
/boot           查看和替换内核 Image、dtb 等文件
/lib/modules    查看当前内核对应的模块目录
/proc           查看进程、CPU、内存、中断等运行状态
/sys            查看设备、驱动、总线、网卡等信息
/dev            查看磁盘、串口、字符设备等设备节点
/etc            修改系统配置文件
/var/log        查看部分系统日志
```

## 创建目录

创建一个目录：

```bash
mkdir test
```

创建多级目录：

```bash
mkdir -p logs/boot/20260428
```

查看结果：

```bash
ls -l
tree logs
```

如果系统没有 `tree` 命令，可以使用：

```bash
find logs
```

## 创建空文件

创建空文件：

```bash
touch test.txt
```

创建多个文件：

```bash
touch a.txt b.txt c.txt
```

更新文件修改时间：

```bash
touch test.txt
```

`touch` 常用于快速创建测试文件。

## 复制文件和目录

复制文件：

```bash
cp a.txt b.txt
```

复制文件到目录：

```bash
cp a.txt logs/
```

复制目录：

```bash
cp -r dir1 dir2
```

保留文件属性复制：

```bash
cp -a dir1 dir2
```

常用场景：

```bash
cp Image /boot/Image-test
cp pd2008-devboard-dsk.dtb /boot/dtb/pd2008-devboard-dsk-test.dtb
```

复制系统关键文件前，建议先备份：

```bash
cp /boot/Image /boot/Image.bak
```

## 移动和重命名文件

重命名文件：

```bash
mv old.txt new.txt
```

移动文件到目录：

```bash
mv test.txt logs/
```

移动目录：

```bash
mv dir1 dir2
```

`mv` 既可以移动，也可以重命名。

危险点：

```bash
mv new.dtb /boot/dtb/pd2008-devboard-dsk.dtb
```

这个命令会覆盖原来的 dtb 文件。执行前应先备份：

```bash
cp /boot/dtb/pd2008-devboard-dsk.dtb /boot/dtb/pd2008-devboard-dsk.dtb.bak
```

## 删除文件和目录

删除文件：

```bash
rm test.txt
```

删除空目录：

```bash
rmdir empty-dir
```

删除目录及其内容：

```bash
rm -r test-dir
```

强制删除：

```bash
rm -f test.txt
```

强制递归删除目录：

```bash
rm -rf test-dir
```

必须特别小心 `rm -rf`。

不要执行类似命令：

```bash
rm -rf /
rm -rf /*
rm -rf /boot/*
rm -rf /lib/modules/*
```

删除前建议先查看：

```bash
ls -lh test-dir
```

确认目录无误后再删除：

```bash
rm -r test-dir
```

## 查看文本文件内容

直接查看完整文件：

```bash
cat file.txt
```

分页查看文件：

```bash
less file.txt
```

查看前 10 行：

```bash
head file.txt
```

查看前 50 行：

```bash
head -n 50 file.txt
```

查看最后 10 行：

```bash
tail file.txt
```

查看最后 50 行：

```bash
tail -n 50 file.txt
```

实时查看文件新增内容：

```bash
tail -f file.txt
```

常用示例：

```bash
cat /etc/os-release
cat /proc/cpuinfo
cat /proc/meminfo
tail -n 100 /var/log/messages
```

## 使用 less 查看大文件

`less` 适合查看大日志文件。

打开文件：

```bash
less dmesg.txt
```

常用按键：

```text
方向键       上下移动
空格         向下翻页
b            向上翻页
/关键字      搜索关键字
n            下一个搜索结果
N            上一个搜索结果
g            跳到文件开头
G            跳到文件结尾
q            退出
```

例如，在日志中搜索 `error`：

```text
/error
```

搜索 `stmmac`：

```text
/stmmac
```

## 搜索文件内容

使用 `grep` 搜索文本内容。

在文件中搜索关键字：

```bash
grep "error" dmesg.txt
```

忽略大小写：

```bash
grep -i "error" dmesg.txt
```

显示行号：

```bash
grep -n "error" dmesg.txt
```

递归搜索目录：

```bash
grep -rn "CONFIG_DWMAC" .
```

忽略大小写并递归搜索：

```bash
grep -rni "stmmac" .
```

常用示例：

```bash
dmesg | grep -i eth
dmesg | grep -i phy
dmesg | grep -i error
dmesg | grep -i fail
journalctl -b | grep -i network
grep -rn "compatible" arch/arm64/boot/dts/
```

## 使用管道

管道符号 `|` 可以把前一个命令的输出交给后一个命令处理。

例如：

```bash
dmesg | grep -i error
```

含义是：

```text
先执行 dmesg 输出内核日志
再把输出交给 grep 搜索 error
```

常用示例：

```bash
ps aux | grep ssh
ip addr | grep inet
cat /proc/interrupts | grep eth
dmesg | grep -i stmmac
```

管道是 Linux 命令行中非常重要的用法。

## 输出重定向

把命令输出保存到文件：

```bash
dmesg > dmesg.txt
```

追加到文件末尾：

```bash
dmesg >> log.txt
```

保存错误输出：

```bash
make > build.log 2>&1
```

常用示例：

```bash
uname -a > uname.txt
cat /etc/os-release > os-release.txt
ip addr > ip-addr.txt
dmesg > dmesg.txt
journalctl -b > journalctl-b.txt
```

注意：

```bash
>
```

会覆盖原文件。

```bash
>>
```

会追加到原文件末尾。

## 查找文件

按文件名查找：

```bash
find . -name "test.txt"
```

在当前目录下查找所有 `.c` 文件：

```bash
find . -name "*.c"
```

查找所有 `.dts` 文件：

```bash
find . -name "*.dts"
```

查找所有 `.dtb` 文件：

```bash
find . -name "*.dtb"
```

查找最近修改过的文件：

```bash
find . -mtime -1
```

含义是查找最近 1 天内修改过的文件。

常用示例：

```bash
find arch/arm64/boot/dts/ -name "*pd2008*"
find . -name "Makefile"
find . -name "Kconfig"
find . -name "*.ko"
```

## 查看文件和目录大小

查看磁盘空间：

```bash
df -h
```

查看当前目录下每个文件和目录大小：

```bash
du -sh *
```

查看某个目录总大小：

```bash
du -sh /lib/modules
du -sh /boot
```

查看目录下各项大小并排序：

```bash
du -sh * | sort -h
```

常用场景：

```bash
df -h
du -sh /var/log
du -sh ~/project
```

如果磁盘空间不足，首先检查：

```bash
df -h
du -sh * | sort -h
```

## 查看系统基本信息

查看内核版本：

```bash
uname -a
```

只查看内核 release：

```bash
uname -r
```

查看系统发行版信息：

```bash
cat /etc/os-release
```

查看主机名：

```bash
hostname
```

查看当前时间：

```bash
date
```

查看系统运行时间：

```bash
uptime
```

常用记录命令：

```bash
uname -a > uname.txt
uname -r > kernel-release.txt
cat /etc/os-release > os-release.txt
date > date.txt
uptime > uptime.txt
```

## 查看 CPU 信息

查看 CPU 信息：

```bash
cat /proc/cpuinfo
```

更清晰地查看 CPU 架构信息：

```bash
lscpu
```

常用记录命令：

```bash
lscpu > lscpu.txt
cat /proc/cpuinfo > cpuinfo.txt
```

在 ARM64 开发板上，需要关注：

```text
Architecture
CPU(s)
Model name
Thread(s) per core
Core(s) per socket
```

## 查看内存信息

查看内存使用情况：

```bash
free -h
```

查看详细内存信息：

```bash
cat /proc/meminfo
```

常用记录命令：

```bash
free -h > free.txt
cat /proc/meminfo > meminfo.txt
```

## 查看磁盘和分区

查看块设备：

```bash
lsblk
```

查看文件系统 UUID：

```bash
blkid
```

查看挂载情况：

```bash
mount
```

查看当前系统挂载表：

```bash
cat /proc/mounts
```

查看磁盘使用情况：

```bash
df -h
```

常用记录命令：

```bash
lsblk > lsblk.txt
blkid > blkid.txt
mount > mount.txt
cat /proc/mounts > proc-mounts.txt
df -h > df-h.txt
```

在开发板上需要重点关注：

```text
系统是否从 NVMe 启动
根文件系统挂载在哪个分区
/boot 是否单独挂载
磁盘空间是否充足
```

## 查看进程

查看当前用户进程：

```bash
ps
```

查看所有进程：

```bash
ps aux
```

搜索指定进程：

```bash
ps aux | grep ssh
```

实时查看系统进程状态：

```bash
top
```

如果安装了 `htop`，也可以使用：

```bash
htop
```

查看某个进程状态：

```bash
cat /proc/<PID>/status
```

例如查看 1 号进程：

```bash
cat /proc/1/status
```

1 号进程通常是系统初始化进程，例如 `systemd`。

## 查看服务状态

现代 Linux 系统通常使用 systemd 管理服务。

查看服务状态：

```bash
systemctl status NetworkManager
```

查看 ssh 服务状态：

```bash
systemctl status sshd
```

启动服务：

```bash
sudo systemctl start NetworkManager
```

停止服务：

```bash
sudo systemctl stop NetworkManager
```

重启服务：

```bash
sudo systemctl restart NetworkManager
```

设置开机自启动：

```bash
sudo systemctl enable NetworkManager
```

取消开机自启动：

```bash
sudo systemctl disable NetworkManager
```

查看所有正在运行的服务：

```bash
systemctl list-units --type=service --state=running
```

注意：在项目开发板上，不要随意停止关键服务。

## 查看日志

查看本次启动日志：

```bash
journalctl -b
```

查看本次启动日志并分页：

```bash
journalctl -b | less
```

查看某个服务日志：

```bash
journalctl -u NetworkManager
```

查看本次启动中某个服务日志：

```bash
journalctl -b -u NetworkManager
```

实时查看日志：

```bash
journalctl -f
```

查看内核日志：

```bash
dmesg
```

查看内核日志并分页：

```bash
dmesg | less
```

搜索内核日志：

```bash
dmesg | grep -i error
dmesg | grep -i eth
dmesg | grep -i phy
dmesg | grep -i pci
```

保存日志：

```bash
dmesg > dmesg.txt
journalctl -b > journalctl-b.txt
```

## 查看网络接口

查看网卡地址：

```bash
ip addr
```

简写：

```bash
ip a
```

查看网络接口状态：

```bash
ip link
```

查看路由：

```bash
ip route
```

查看 DNS 配置：

```bash
cat /etc/resolv.conf
```

测试网络连通性：

```bash
ping 192.168.1.1
ping www.baidu.com
```

常用记录命令：

```bash
ip addr > ip-addr.txt
ip link > ip-link.txt
ip route > ip-route.txt
cat /etc/resolv.conf > resolv.conf.txt
```

如果无法联网，应按顺序检查：

```text
1. 网线是否连接
2. 网卡是否存在
3. 网卡是否 link up
4. 是否有 IP 地址
5. 路由是否正确
6. DNS 是否正确
7. 网关是否能 ping 通
8. 外网 IP 是否能 ping 通
9. 域名是否能解析
```

## 使用 SSH 登录远程机器

登录远程机器：

```bash
ssh user@192.168.1.100
```

指定端口：

```bash
ssh -p 22 user@192.168.1.100
```

退出 SSH：

```bash
exit
```

或者按：

```text
Ctrl + D
```

首次登录时可能出现：

```text
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```

输入：

```bash
yes
```

## 使用 scp 复制文件

从本机复制文件到远程机器：

```bash
scp test.txt user@192.168.1.100:/home/user/
```

从远程机器复制文件到本机：

```bash
scp user@192.168.1.100:/home/user/test.txt .
```

复制目录：

```bash
scp -r logs user@192.168.1.100:/home/user/
```

常用示例：

```bash
scp Image root@192.168.1.100:/boot/
scp pd2008-devboard-dsk.dtb root@192.168.1.100:/boot/dtb/
scp root@192.168.1.100:/tmp/dmesg.txt .
```

注意：复制内核、dtb 等关键文件前，必须确认目标路径。

## 使用 rsync 复制目录

`rsync` 适合复制目录，并且支持增量同步。

复制目录到远程机器：

```bash
rsync -av logs/ user@192.168.1.100:/home/user/logs/
```

从远程机器复制目录到本机：

```bash
rsync -av user@192.168.1.100:/home/user/logs/ ./logs/
```

常用选项：

```text
-a      归档模式，保留权限、时间等信息
-v      显示详细过程
-h      使用可读性更好的大小单位
--delete 删除目标中源目录不存在的文件
```

谨慎使用：

```bash
rsync -av --delete source/ target/
```

因为 `--delete` 会删除目标目录中多余文件。

## 查看命令历史

查看历史命令：

```bash
history
```

搜索历史命令：

```bash
history | grep dmesg
```

重新执行上一条命令：

```bash
!!
```

重新执行最近一条以 `systemctl` 开头的命令：

```bash
!systemctl
```

历史命令可以帮助回顾自己做过什么操作。

做实验时，可以保存历史命令：

```bash
history > history.txt
```

## 查看当前用户和权限

查看当前用户：

```bash
whoami
```

查看当前用户 ID 和所属组：

```bash
id
```

查看当前登录用户：

```bash
who
```

或者：

```bash
w
```

切换到 root 用户：

```bash
su -
```

使用 sudo 执行命令：

```bash
sudo command
```

例如：

```bash
sudo systemctl restart NetworkManager
```

注意：使用 root 权限前必须确认命令没有危险。

## 修改文件权限

查看权限：

```bash
ls -l file.txt
```

增加执行权限：

```bash
chmod +x script.sh
```

设置文件权限为 644：

```bash
chmod 644 file.txt
```

设置脚本权限为 755：

```bash
chmod 755 script.sh
```

修改文件所有者：

```bash
sudo chown user:user file.txt
```

权限数字含义：

```text
r = 4
w = 2
x = 1
```

常见权限：

```text
644     普通文本文件常用权限，所有者可读写，其他人只读
755     可执行脚本或目录常用权限，所有者可读写执行，其他人可读执行
```

不要随意执行：

```bash
chmod -R 777 /
chmod -R 777 /etc
chmod -R 777 /boot
```

## 压缩和解压文件

创建 tar 包：

```bash
tar -cvf logs.tar logs/
```

解开 tar 包：

```bash
tar -xvf logs.tar
```

创建 gzip 压缩包：

```bash
tar -czvf logs.tar.gz logs/
```

解开 gzip 压缩包：

```bash
tar -xzvf logs.tar.gz
```

创建 xz 压缩包：

```bash
tar -cJvf logs.tar.xz logs/
```

解开 xz 压缩包：

```bash
tar -xJvf logs.tar.xz
```

常用示例：

```bash
tar -czvf board-report-20260428.tar.gz board-report-20260428/
```

## 编辑文本文件

常见编辑器包括：

```text
vim
nano
vi
```

如果不熟悉 vim，可以先使用 nano：

```bash
nano file.txt
```

nano 常用按键：

```text
Ctrl + O     保存
Enter        确认文件名
Ctrl + X     退出
```

vim 打开文件：

```bash
vim file.txt
```

vim 基础操作：

```text
i            进入插入模式
Esc          退出插入模式
:w           保存
:q           退出
:wq          保存并退出
:q!          不保存强制退出
/关键字      搜索
n            下一个搜索结果
```

修改配置文件前建议备份：

```bash
cp config.txt config.txt.bak
vim config.txt
```

## 查看设备节点

查看 `/dev` 目录：

```bash
ls /dev
```

查看磁盘设备：

```bash
ls /dev/nvme*
ls /dev/sd*
```

查看串口设备：

```bash
ls /dev/tty*
```

常见设备示例：

```text
/dev/nvme0n1        NVMe 磁盘
/dev/nvme0n1p1      NVMe 第 1 个分区
/dev/nvme0n1p2      NVMe 第 2 个分区
/dev/ttyAMA0        ARM PL011 串口
/dev/null           空设备
/dev/zero           零数据设备
```

不要随意向磁盘设备写数据，例如：

```bash
dd if=image.img of=/dev/nvme0n1
```

这类命令可能破坏系统。

## 查看 procfs 信息

`/proc` 是内核导出的虚拟文件系统，不是真实磁盘文件。

常用命令：

```bash
cat /proc/cpuinfo
cat /proc/meminfo
cat /proc/interrupts
cat /proc/cmdline
cat /proc/mounts
cat /proc/version
```

特别重要：

```bash
cat /proc/cmdline
```

用于查看当前内核启动参数。

例如可以看到：

```text
console=ttyAMA1,115200 root=/dev/nvme0n1p2 rw rootwait
```

查看中断：

```bash
cat /proc/interrupts
```

保存信息：

```bash
cat /proc/cmdline > cmdline.txt
cat /proc/interrupts > interrupts.txt
```

## 查看 sysfs 信息

`/sys` 也是内核导出的虚拟文件系统，常用于查看设备、驱动、总线信息。

查看总线：

```bash
ls /sys/bus
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

常用示例：

```bash
ls /sys/class/net
ls /sys/bus/platform/devices
ls /sys/bus/pci/devices
```

如果想知道某个网卡对应的设备路径，可以使用：

```bash
readlink -f /sys/class/net/end0
```

## 常用开发板信息采集命令

在开发板上排查问题时，建议先采集以下信息：

```bash
mkdir -p board-report

uname -a > board-report/uname.txt
uname -r > board-report/kernel-release.txt
cat /etc/os-release > board-report/os-release.txt
date > board-report/date.txt
uptime > board-report/uptime.txt

lscpu > board-report/lscpu.txt
cat /proc/cpuinfo > board-report/cpuinfo.txt
free -h > board-report/free.txt
cat /proc/meminfo > board-report/meminfo.txt

lsblk > board-report/lsblk.txt
blkid > board-report/blkid.txt
df -h > board-report/df-h.txt
mount > board-report/mount.txt
cat /proc/mounts > board-report/proc-mounts.txt

ip addr > board-report/ip-addr.txt
ip link > board-report/ip-link.txt
ip route > board-report/ip-route.txt
cat /etc/resolv.conf > board-report/resolv.conf.txt

dmesg > board-report/dmesg.txt
journalctl -b > board-report/journalctl-b.txt
cat /proc/cmdline > board-report/cmdline.txt
cat /proc/interrupts > board-report/interrupts.txt

history > board-report/history.txt
```

打包：

```bash
tar -czvf board-report.tar.gz board-report/
```

这个压缩包可以用于提交问题记录。

## 常见错误和注意事项

不要在不确认路径的情况下执行删除命令：

```bash
rm -rf *
```

不要在根目录下随意执行：

```bash
rm -rf *
```

不要随意覆盖 `/boot` 下的内核和 dtb：

```bash
cp Image /boot/Image
cp test.dtb /boot/dtb/xxx.dtb
```

覆盖前必须备份。

不要随意修改 `/etc/fstab`、网络配置、启动脚本等系统关键文件。

修改配置文件前，先备份：

```bash
cp file file.bak
```

执行危险命令前，先确认：

```bash
pwd
ls -lh
```

如果不确定命令作用，应先在测试目录中操作，不要直接在系统目录中执行。

## 建议必须熟练掌握的命令清单

文件和目录：

```bash
pwd
ls
cd
mkdir
touch
cp
mv
rm
find
du
df
```

文本查看和搜索：

```bash
cat
less
head
tail
grep
```

系统信息：

```bash
uname
hostname
date
uptime
lscpu
free
lsblk
blkid
mount
```

进程和服务：

```bash
ps
top
systemctl
journalctl
dmesg
```

网络：

```bash
ip addr
ip link
ip route
ping
ssh
scp
rsync
```

权限和用户：

```bash
whoami
id
sudo
su
chmod
chown
```

压缩打包：

```bash
tar
```

## 实验任务

请在 Linux 开发机或开发板上完成以下实验。

第一部分：目录和文件操作。

```bash
mkdir -p ~/linux-command-test/logs
cd ~/linux-command-test
pwd
touch a.txt b.txt c.txt
ls -lah
cp a.txt a.bak
mv b.txt logs/
find . -name "*.txt"
```

第二部分：文本查看和搜索。

```bash
echo "hello linux" > test.log
echo "error: test message" >> test.log
cat test.log
grep -i "error" test.log
less test.log
```

第三部分：系统信息查看。

```bash
uname -a
cat /etc/os-release
lscpu
free -h
lsblk
df -h
```

第四部分：日志查看。

```bash
dmesg | tail -n 50
journalctl -b | tail -n 50
```

第五部分：网络信息查看。

```bash
ip addr
ip link
ip route
ping -c 4 127.0.0.1
```

第六部分：信息采集。

```bash
mkdir -p ~/linux-command-test/report

uname -a > ~/linux-command-test/report/uname.txt
cat /etc/os-release > ~/linux-command-test/report/os-release.txt
lscpu > ~/linux-command-test/report/lscpu.txt
free -h > ~/linux-command-test/report/free.txt
lsblk > ~/linux-command-test/report/lsblk.txt
df -h > ~/linux-command-test/report/df-h.txt
ip addr > ~/linux-command-test/report/ip-addr.txt
ip route > ~/linux-command-test/report/ip-route.txt
dmesg > ~/linux-command-test/report/dmesg.txt
journalctl -b > ~/linux-command-test/report/journalctl-b.txt

tar -czvf ~/linux-command-test/report.tar.gz -C ~/linux-command-test report
```

## 提交要求

提交以下内容：

```text
linux-command-test/
├── report/
│   ├── uname.txt
│   ├── os-release.txt
│   ├── lscpu.txt
│   ├── free.txt
│   ├── lsblk.txt
│   ├── df-h.txt
│   ├── ip-addr.txt
│   ├── ip-route.txt
│   ├── dmesg.txt
│   └── journalctl-b.txt
├── report.tar.gz
└── summary.md
```

`summary.md` 需要包含：

```text
1. 当前系统版本
2. 当前内核版本
3. 当前 CPU 核心数量
4. 当前内存大小
5. 当前磁盘分区情况
6. 当前网络接口名称
7. 本次实验遇到的问题
8. 不理解的命令或概念
```

## 验收标准

验收时重点检查以下内容：

1. 是否能独立完成目录创建、文件复制、移动、删除；
2. 是否能正确使用 `cat`、`less`、`tail`、`grep` 查看和搜索文本；
3. 是否能查看系统版本、内核版本、CPU、内存、磁盘、网络信息；
4. 是否能保存命令输出到文件；
5. 是否能使用 `tar` 打包提交结果；
6. `summary.md` 是否能说明系统基本状态；
7. 是否没有使用截图代替原始文本日志；
8. 是否没有误删或覆盖系统关键文件。

通过本文档学习后，实习生应具备最基础的 Linux 命令行操作能力，可以继续学习日志查看、网络配置、GCC 编译、Makefile 和内核模块等后续内容。
