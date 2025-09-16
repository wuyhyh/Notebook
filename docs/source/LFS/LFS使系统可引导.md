# LFS 使系统可引导

现在我们创建 /etc/fstab 文件，为新的 LFS 系统构建内核，以及安装 GRUB 引导加载器，使得系统引导时可以选择进入 LFS 系统。

## 1. 创建 /etc/fstab 文件

### 1.1 什么是 fstab

`/etc/fstab` (filesystem table) 文件用于告诉系统：

* 哪些文件系统需要挂载；
* 挂载到什么位置；
* 使用哪种文件系统类型；
* 挂载时的选项；
* 是否需要在启动时检查。

在 LFS 中，`fstab` 是系统 **启动过程中自动挂载根分区和虚拟文件系统** 的关键配置。

---

### 1.2 fstab 文件格式

每一行的格式：

```
<文件系统>   <挂载点>   <类型>   <选项>   <dump>   <fsck顺序>
```

* **文件系统**：设备路径（如 `/dev/sda2`）、UUID（推荐）或 LABEL。
* **挂载点**：挂载到的目录，比如 `/`、`/boot`、`/home`。
* **类型**：文件系统类型，如 `ext4`、`vfat`、`xfs`、`swap`。
* **选项**：挂载选项，如 `defaults`、`noexec`、`ro`。
* **dump**：是否启用 `dump` 备份，一般填 `0`。
* **fsck顺序**：

    * `1` 表示根分区
    * `2` 表示其他需要 fsck 的分区
    * `0` 表示不检查

---

### 1.3 推荐使用 UUID

相比 `/dev/sdaX` 这种写法，UUID 更稳定，因为设备顺序可能会改变。
获取方式：

```bash
blkid
```

输出示例：

```
/dev/nvme0n1p4: UUID="0fe88e43-bb07-4b30-9211-4b4f34828f16" TYPE="ext4" PARTLABEL="LFS"
```

---

### 1.4 LFS 必需的挂载项

即使只有一个根分区，仍然要在 fstab 中配置内核需要的虚拟文件系统：

```text
UUID=0fe88e43-bb07-4b30-9211-4b4f34828f16   /        ext4    defaults        1 1

proc         /proc    proc    nosuid,noexec,nodev    0 0
sysfs        /sys     sysfs   nosuid,noexec,nodev    0 0
devpts       /dev/pts devpts  gid=5,mode=620         0 0
tmpfs        /run     tmpfs   defaults               0 0
devtmpfs     /dev     devtmpfs mode=0755,nosuid      0 0
```

---

### 1.5 可选的挂载项

* **EFI 分区（UEFI 启动时必须）**

  ```text
  UUID=xxxx-xxxx   /boot   vfat   defaults,umask=0077   0 2
  ```
* **Swap 分区**

  ```text
  UUID=xxxx-xxxx   swap    swap   pri=1   0 0
  ```

---

### 1.6 验证

重启进入 LFS 后，执行：

```bash
mount
```

或

```bash
findmnt -a
```

确认所有分区都正确挂载。

---

### 1.7 适合当前机器的 fstab 配置

根据你的 `lsblk` 和 `blkid` 输出：

* LFS 根分区 → `/dev/nvme0n1p4`，UUID=**0fe88e43-bb07-4b30-9211-4b4f34828f16**，类型 ext4。
* 没有单独的 swap 分区（仅有 Fedora 的 zram swap，不影响 LFS）。
* EFI 分区由 Fedora 使用（xfs 格式），LFS 暂时不需要独立挂载。

因此，你的 `/etc/fstab` 应写成：

```text
# Begin /etc/fstab

# LFS root partion
UUID=0fe88e43-bb07-4b30-9211-4b4f34828f16   /        ext4    defaults        1 1

# kernel virtual file system
proc         /proc    proc    nosuid,noexec,nodev    0 0
sysfs        /sys     sysfs   nosuid,noexec,nodev    0 0
devpts       /dev/pts devpts  gid=5,mode=620         0 0
tmpfs        /run     tmpfs   defaults               0 0
devtmpfs     /dev     devtmpfs mode=0755,nosuid      0 0

# End /etc/fstab
```

这样配置后，LFS 会在启动时自动挂载根分区和必需的内核伪文件系统。

## 2. 编译 Linux-6.13.4 内核

```text
cd /sources;tar -xf linux-6.13.4.tar.xz;cd linux-6.13.4
```

### 2.1 编译配置

运行以下命令，准备编译内核：

```text
make mrproper
```

该命令确保内核源代码树绝对干净，内核开发组建议在每次编译内核前运行该命令。

```text
make menuconfig
```

这会启动 ncurses 目录驱动的界面

一定要按照[列表](https://lfs.xry111.site/zh_CN/12.3-systemd/chapter10/kernel.html)
启用/禁用/设定其中列出的内核特性，否则系统可能不能正常工作，甚至根本无法引导：

### 2.2 编译内核

```text
make
```

如果内核配置使用了模块，安装它们：

```text
make modules_install
```

### 2.3 设置启动项

指向内核映像的路径可能随机器平台的不同而变化。下面使用的文件名可以依照您的需要改变，但文件名的开头应该保持为
vmlinuz，以保证和下一节描述的引导过程自动设定相兼容。下面的命令假定机器是 x86 体系结构：

```text
cp -iv arch/x86/boot/bzImage /boot/vmlinuz-6.13.4-lfs-12.3-systemd
```

System.map 是内核符号文件，它将内核 API 的每个函数入口点和运行时数据结构映射到它们的地址。它被用于调查分析内核可能出现的问题。执行以下命令安装该文件：

```text
cp -iv System.map /boot/System.map-6.13.4
```

内核配置文件 .config 由上述的 make menuconfig 步骤生成，包含编译好的内核的所有配置选项。最好能将它保留下来以供日后参考：

```text
cp -iv .config /boot/config-6.13.4
```

安装 Linux 内核文档：

```text
cp -r Documentation -T /usr/share/doc/linux-6.13.4
```

### 2.4 配置 Linux 内核模块加载顺序

执行以下命令创建文件 /etc/modprobe.d/usb.conf：

```text
install -v -m755 -d /etc/modprobe.d
cat > /etc/modprobe.d/usb.conf << "EOF"
# Begin /etc/modprobe.d/usb.conf

install ohci_hcd /sbin/modprobe ehci_hcd ; /sbin/modprobe -i ohci_hcd ; true
install uhci_hcd /sbin/modprobe ehci_hcd ; /sbin/modprobe -i uhci_hcd ; true

# End /etc/modprobe.d/usb.conf
EOF
```

## 3. 使用 GRUB 设定引导过程

### 3.1 设定 GRUB 配置

GRUB 的工作方式是，将数据写入硬盘的第一个物理磁道。这里不属于任何文件系统，在启动时，第一个物理磁道中的程序从引导分区加载
GRUB 模块，默认在 /boot/grub 中查找模块。

将 GRUB 文件安装到 /boot/grub 并设定引导磁道：

```text
grub-install /dev/nvme0n1
```

### 3.2 创建 GRUB 配置文件

生成 /boot/grub/grub.cfg：

```text
cat > /boot/grub/grub.cfg << "EOF"
# Begin /boot/grub/grub.cfg
set default=0
set timeout=5

insmod part_gpt
insmod ext2
set root=(hd0,4)
set gfxpayload=1024x768x32

menuentry "GNU/Linux, Linux 6.13.4-lfs-12.3-systemd" {
linux   /boot/vmlinuz-6.13.4-lfs-12.3-systemd root=/dev/nvme0n1p4 ro
}
EOF
```
