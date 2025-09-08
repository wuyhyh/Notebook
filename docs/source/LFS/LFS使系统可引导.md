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






