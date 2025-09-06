# LFS 进入 chroot 并构建其他临时工具

现在已经解决了所有循环依赖问题，现在即可使用“chroot”环境进行构建，它与宿主系统 (除正在运行的内核外) 完全隔离。

为了隔离环境的正常工作，必须它与正在运行的内核之间建立一些通信机制。
这些通信机制通过所谓的虚拟内核文件系统实现，我们将在进入 chroot 环境前挂载它们。

## 1. 将 $LFS/* 目录的所有者改变为 root：

退出 lfs，重新作为 root 用户

```text
exit
```

```text
chown --from lfs -R root:root $LFS/{usr,lib,var,etc,bin,sbin,tools}
case $(uname -m) in
  x86_64) chown --from lfs -R root:root $LFS/lib64 ;;
esac
```

## 2. 准备虚拟内核文件系统

用户态程序使用内核创建的一些文件系统和内核通信。这些文件系统是虚拟的：它们并不占用磁盘空间。它们的内容保留在内存中。必须将它们被挂载到 $
LFS 目录树中，这样 chroot 环境中的程序才能找到它们

### 2.1 首先创建这些文件系统的挂载点：

```text
mkdir -pv $LFS/{dev,proc,sys,run}
```

### 2.2 运行以下命令进行绑定挂载：

```text
mount -v --bind /dev $LFS/dev
```

### 2.3 挂载其余的虚拟内核文件系统：

```text
mount -vt devpts devpts -o gid=5,mode=0620 $LFS/dev/pts
mount -vt proc proc $LFS/proc
mount -vt sysfs sysfs $LFS/sys
mount -vt tmpfs tmpfs $LFS/run
```

### 2.4 显式挂载一个 tmpfs：

```text
if [ -h $LFS/dev/shm ]; then
install -v -d -m 1777 $LFS$(realpath /dev/shm)
else
mount -vt tmpfs -o nosuid,nodev tmpfs $LFS/dev/shm
fi
```

## 3. 进入 chroot 环境

以 root 用户身份，运行以下命令以进入当前只包含临时工具的 chroot 环境：

```text
chroot "$LFS" /usr/bin/env -i   \
    HOME=/root                  \
    TERM="$TERM"                \
    PS1='(lfs chroot) \u:\w\$ ' \
    PATH=/usr/bin:/usr/sbin     \
    MAKEFLAGS="-j$(nproc)"      \
    TESTSUITEFLAGS="-j$(nproc)" \
/bin/bash --login
```

> 注意 bash 的提示符会包含 I have no name!。这是正常的，因为现在还没有创建 /etc/passwd 文件。

## 4. 创建目录

创建一些位于根目录中的目录，它们不属于之前章节需要的有限目录结构：

```text
mkdir -pv /{boot,home,mnt,opt,srv}
```

执行以下命令，为这些直接位于根目录中的目录创建次级目录结构：

```text
mkdir -pv /etc/{opt,sysconfig}
mkdir -pv /lib/firmware
mkdir -pv /media/{floppy,cdrom}
mkdir -pv /usr/{,local/}{include,src}
mkdir -pv /usr/lib/locale
mkdir -pv /usr/local/{bin,lib,sbin}
mkdir -pv /usr/{,local/}share/{color,dict,doc,info,locale,man}
mkdir -pv /usr/{,local/}share/{misc,terminfo,zoneinfo}
mkdir -pv /usr/{,local/}share/man/man{1..8}
mkdir -pv /var/{cache,local,log,mail,opt,spool}
mkdir -pv /var/lib/{color,misc,locate}

ln -sfv /run /var/run
ln -sfv /run/lock /var/lock

install -dv -m 0750 /root
install -dv -m 1777 /tmp /var/tmp
```

## 5. 创建必要的文件和符号链接

### 5.1 创建符号链接

为了满足一些仍然使用 /etc/mtab 的工具，执行以下命令，创建符号链接：

```text
ln -sv /proc/self/mounts /etc/mtab
```

### 5.2 创建 /etc/hosts 文件

创建一个基本的 /etc/hosts 文件，一些测试套件，以及 Perl 的一个配置文件将会使用它：

```text
cat > /etc/hosts << EOF
127.0.0.1  localhost $(hostname)
::1        localhost
EOF
```

### 5.3 创建 /etc/passwd 文件

为了使得 root 能正常登录，而且用户名 “root” 能被正常识别，必须在文件 /etc/passwd 和 /etc/groups 中写入相关的条目。

执行以下命令创建 /etc/passwd 文件：

```text
cat > /etc/passwd << "EOF"
root:x:0:0:root:/root:/bin/bash
bin:x:1:1:bin:/dev/null:/usr/bin/false
daemon:x:6:6:Daemon User:/dev/null:/usr/bin/false
messagebus:x:18:18:D-Bus Message Daemon User:/run/dbus:/usr/bin/false
systemd-journal-gateway:x:73:73:systemd Journal Gateway:/:/usr/bin/false
systemd-journal-remote:x:74:74:systemd Journal Remote:/:/usr/bin/false
systemd-journal-upload:x:75:75:systemd Journal Upload:/:/usr/bin/false
systemd-network:x:76:76:systemd Network Management:/:/usr/bin/false
systemd-resolve:x:77:77:systemd Resolver:/:/usr/bin/false
systemd-timesync:x:78:78:systemd Time Synchronization:/:/usr/bin/false
systemd-coredump:x:79:79:systemd Core Dumper:/:/usr/bin/false
uuidd:x:80:80:UUID Generation Daemon User:/dev/null:/usr/bin/false
systemd-oom:x:81:81:systemd Out Of Memory Daemon:/:/usr/bin/false
nobody:x:65534:65534:Unprivileged User:/dev/null:/usr/bin/false
EOF
```

我们以后再设置 root 用户的实际密码。

### 5.4 创建 /etc/group 文件

执行以下命令，创建 /etc/group 文件：

```text
cat > /etc/group << "EOF"
root:x:0:
bin:x:1:daemon
sys:x:2:
kmem:x:3:
tape:x:4:
tty:x:5:
daemon:x:6:
floppy:x:7:
disk:x:8:
lp:x:9:
dialout:x:10:
audio:x:11:
video:x:12:
utmp:x:13:
cdrom:x:15:
adm:x:16:
messagebus:x:18:
systemd-journal:x:23:
input:x:24:
mail:x:34:
kvm:x:61:
systemd-journal-gateway:x:73:
systemd-journal-remote:x:74:
systemd-journal-upload:x:75:
systemd-network:x:76:
systemd-resolve:x:77:
systemd-timesync:x:78:
systemd-coredump:x:79:
uuidd:x:80:
systemd-oom:x:81:
wheel:x:97:
users:x:999:
nogroup:x:65534:
EOF
```

### 5.5 创建一个非特权用户

一些测试需要使用一个非特权用户。我们这里创建一个用户，在那一章的末尾再删除该用户。

```text
echo "tester:x:101:101::/home/tester:/bin/bash" >> /etc/passwd
echo "tester:x:101:" >> /etc/group
install -o tester -d /home/tester
```

### 5.6 打开新的 shell

为了移除 “I have no name!” 提示符，需要打开一个新 shell。由于已经创建了文件 /etc/passwd 和 /etc/group，用户名和组名现在就可以正常解析了：

```text
exec /usr/bin/bash --login
```

### 5.7 创建日志文件

login、agetty 和 init 等程序使用一些日志文件，以记录登录系统的用户和登录时间等信息。然而，这些程序不会创建不存在的日志文件。初始化日志文件，并为它们设置合适的访问权限：

```text
touch /var/log/{btmp,lastlog,faillog,wtmp}
chgrp -v utmp /var/log/lastlog
chmod -v 664  /var/log/lastlog
chmod -v 600  /var/log/btmp
```

## 6. 构建其他临时工具

### 6.1 安装 Gettext

Gettext 软件包包含国际化和本地化工具，它们允许程序在编译时加入 NLS (本地语言支持) 功能，使它们能够以用户的本地语言输出消息。

对于我们的临时工具，只要安装 Gettext 中的三个程序即可。

```text
cd $LFS/sources;tar -xf gettext-0.24.tar.xz;cd gettext-0.24
```

准备编译 Gettext：

```text
./configure --disable-shared
```

编译该软件包：

```text
time make
```

安装 msgfmt，msgmerge，以及 xgettext 这三个程序：

```text
cp -v gettext-tools/src/{msgfmt,msgmerge,xgettext} /usr/bin
```

### 6.2 安装 Bison

```text
cd $LFS/sources;tar -xf bison-3.8.2.tar.xz;cd bison-3.8.2
```

准备编译 Bison：

```text
./configure --prefix=/usr \
            --docdir=/usr/share/doc/bison-3.8.2
```

编译该软件包

```text
time make
```

```text
time make install
```

### 6.3 安装 Perl

```text
cd $LFS/sources;tar -xf perl-5.40.1.tar.xz;cd perl-5.40.1
```

准备编译 Perl：

```text
sh Configure -des                            \
-D prefix=/usr                               \
-D vendorprefix=/usr                         \
-D useshrplib                                \
-D privlib=/usr/lib/perl5/5.40/core_perl     \
-D archlib=/usr/lib/perl5/5.40/core_perl     \
-D sitelib=/usr/lib/perl5/5.40/site_perl     \
-D sitearch=/usr/lib/perl5/5.40/site_perl    \
-D vendorlib=/usr/lib/perl5/5.40/vendor_perl \
-D vendorarch=/usr/lib/perl5/5.40/vendor_perl
```

编译该软件包

```text
time make
```

```text
time make install
```

### 6.4 安装 Python

```text
cd $LFS/sources;tar -xf Python-3.13.2.tar.xz;cd Python-3.13.2
```

准备编译 Python：

```text
./configure --prefix=/usr   \
            --enable-shared \
            --without-ensurepip
```

编译该软件包

```text
time make
```

```text
time make install
```

### 6.5 安装 Texinfo

```text
cd $LFS/sources;tar -xf texinfo-7.2.tar.xz;cd texinfo-7.2
```

准备编译 Texinfo：

```text
./configure --prefix=/usr
```

编译该软件包

```text
time make
```

```text
time make install
```

### 6.6 安装 Util-linux

```text
cd $LFS/sources;tar -xf util-linux-2.40.4.tar.xz;cd util-linux-2.40.4
```

FHS 建议使用 /var/lib/hwclock 目录，而非一般的 /etc 目录作为 adjtime 文件的位置。首先创建该目录：

```text
mkdir -pv /var/lib/hwclock
```

准备编译 Util-linux：

```text
./configure --libdir=/usr/lib     \
            --runstatedir=/run    \
            --disable-chfn-chsh   \
            --disable-login       \
            --disable-nologin     \
            --disable-su          \
            --disable-setpriv     \
            --disable-runuser     \
            --disable-pylibmount  \
            --disable-static      \
            --disable-liblastlog2 \
            --without-python      \
            ADJTIME_PATH=/var/lib/hwclock/adjtime \
            --docdir=/usr/share/doc/util-linux-2.40.4
```

编译该软件包

```text
time make
```

```text
time make install
```

## 7. 清理和备份临时系统

进入根目录

```text
cd /
```

### 7.1 清理

首先，删除已经安装的临时工具文档文件，以防止它们进入最终构建的系统，并节省大约 35 MB：

```text
rm -rf /usr/share/{info,man,doc}/*
```

其次，在现代 Linux 系统中，libtool 的 .la 文件仅用于 libltdl。LFS 中没有库通过 libltdl 加载，而且已知一些 .la 文件会导致
BLFS 软件包出现异常。现在删除这些文件：

```text
find /usr/{lib,libexec} -name \*.la -delete
```

当前临时系统使用约 3 GB 空间，但是我们已经不需要其中的 /tools 目录了。该目录使用约 1 GB 存储空间。现在删除它：

```text
rm -rf /tools
```

### 7.2 备份

现在，已经为系统安装了所有必要的程序和库，且 LFS 系统的当前状态良好。
可以将系统备份起来，以便以后重新使用。

备份档案不应存放在 $LFS 目录树中。
现在，如果您决定进行备份，离开 chroot 环境：

```text
exit
```

> 以下给出的所有步骤都在宿主系统中以 root 身份执行
>
> 无论何时，只要准备以 root 身份执行命令，一定要确认 LFS 变量已经正确设定。

在进行备份之前，解除内核虚拟文件系统的挂载：

```text
mountpoint -q $LFS/dev/shm && umount $LFS/dev/shm
umount $LFS/dev/pts
umount $LFS/{sys,proc,run,dev}
```

由于备份档案需要进行压缩，即使您的系统运行速度较快，该命令也会消耗较长的时间 (可能超过 10 分钟)

```text
cd $LFS;time tar -cJpf $HOME/lfs-temp-tools-12.3-systemd.tar.xz .
```

### 7.3 还原

如果您犯下了一些错误，并不得不重新开始构建，您可以使用备份档案还原临时系统，节约一些工作时间。

> 下面的命令非常危险。
>
> 如果您在没有切换到 $LFS 目录或 LFS 环境变量没有为 root 用户正确设定的情况下运行了 rm -rf ./* 命令，它会完全摧毁宿主系统。

```text
cd $LFS
rm -rf ./*
tar -xpf $HOME/lfs-temp-tools-12.3-systemd.tar.xz
```
