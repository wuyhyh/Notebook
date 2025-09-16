# LFS 系统启动前的最后准备

## 1. 创建系统版本文件

创建一个 /etc/lfs-release 文件能够容易地找出当前安装的 LFS 系统版本。

```text
echo 12.3-systemd > /etc/lfs-release
```

需要两个描述当前安装的系统的文件，这些软件包可能是二进制包，也可能是需要构建的源代码包。

第一个文件根据 Linux Standards Base (LSB) 的规则描述系统状态。运行命令创建该文件：

```text
cat > /etc/lsb-release << "EOF"
DISTRIB_ID="Linux From Scratch"
DISTRIB_RELEASE="12.3-systemd"
DISTRIB_CODENAME="LanYe"
DISTRIB_DESCRIPTION="Linux From Scratch"
EOF
```

第二个文件基本上包含相同的信息，systemd 和一些图形桌面环境会使用它。运行命令创建该文件：

```text
cat > /etc/os-release << "EOF"
NAME="Linux From Scratch"
VERSION="12.3-systemd"
ID=lfs
PRETTY_NAME="Linux From Scratch 12.3-systemd"
VERSION_CODENAME="<LanYe-25.09>"
HOME_URL="https://www.linuxfromscratch.org/lfs/"
RELEASE_TYPE="stable"
EOF
```

你可以修改 'DISTRIB_CODENAME' 和 'VERSION_CODENAME' 域，体现你的系统的独特性。

## 2. 重启系统

现在所有软件包已经安装完成，可以重新启动计算机了。

首先退出 chroot 环境：

```text
logout
```

解除虚拟文件系统的挂载：

```text
umount -v $LFS/dev/pts
mountpoint -q $LFS/dev/shm && umount -v $LFS/dev/shm
umount -v $LFS/dev
umount -v $LFS/run
umount -v $LFS/proc
umount -v $LFS/sys
```

如果为 LFS 创建了其他的分区，需要在解除挂载 LFS 分区之前，先解除挂载它们，例如：

```text
umount -v $LFS/home
umount -v $LFS
```

解除 LFS 文件系统的挂载：

```text
umount -v $LFS
```

现在重新启动系统。

```text
reboot
```
