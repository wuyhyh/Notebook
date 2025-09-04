# LFS 进入 Chroot 并构建其他临时工具

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

首先创建这些文件系统的挂载点：

```text
mkdir -pv $LFS/{dev,proc,sys,run}
```

运行以下命令进行绑定挂载：

```text
mount -v --bind /dev $LFS/dev
```

挂载其余的虚拟内核文件系统：

```text
mount -vt devpts devpts -o gid=5,mode=0620 $LFS/dev/pts
mount -vt proc proc $LFS/proc
mount -vt sysfs sysfs $LFS/sys
mount -vt tmpfs tmpfs $LFS/run
```

显式挂载一个 tmpfs：

```text
if [ -h $LFS/dev/shm ]; then
install -v -d -m 1777 $LFS$(realpath /dev/shm)
else
mount -vt tmpfs -o nosuid,nodev tmpfs $LFS/dev/shm
fi
```

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
