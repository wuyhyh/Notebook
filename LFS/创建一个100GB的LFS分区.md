很好，你打算给 LFS 分配 **100GB** 空间，这是完全足够的，而且在你已经确认第二块 SSD（`/dev/nvme1n1`）上有空闲空间的情况下，可以安全进行分区和挂载操作。

下面我会提供 **逐步详细的命令流程**，不需要你先读第2章，也不会破坏已有的 Fedora 系统。

---

## ✅ 目标

我们将在 `/dev/nvme1n1` 空闲空间中创建一个新的 100GB 分区，挂载到 `/mnt/lfs`，并设置环境变量 `LFS=/mnt/lfs`。

---

## 🧭 操作步骤

### 步骤 1：使用 `fdisk` 创建新分区（100GB）

```bash
sudo fdisk /dev/nvme1n1
```

在交互提示中输入：

```text
n       ← 创建新分区
<Enter> ← 默认选择分区号（比如是4）
<Enter> ← 默认起始扇区
+100G   ← 设置大小为100GB
w       ← 写入分区表并退出
```

**说明**：

* 如果提示你要创建 `nvme1n1p4`，那就是你新建的 LFS 分区；
* 操作不会影响已有 Fedora 分区，因为只使用空闲空间。

### 步骤 2：格式化分区为 ext4 文件系统

假设刚刚创建的分区是 `/dev/nvme1n1p4`，执行：

```bash
sudo mkfs.ext4 /dev/nvme1n1p4
```

等待格式化完成。

### 步骤 3：挂载到 `/mnt/lfs`

```bash
sudo mkdir -pv /mnt/lfs
sudo mount /dev/nvme1n1p4 /mnt/lfs
```

你现在已经有了构建 LFS 所需的挂载点。

### 步骤 4：设置环境变量 `LFS`

```bash
export LFS=/mnt/lfs
```

你可以将它添加到当前 shell 的配置中：

```bash
echo 'export LFS=/mnt/lfs' >> ~/.bashrc
source ~/.bashrc
```

这样每次登录终端都会自动生效。

---

## ✅ 完成后状态

你现在已经拥有：

* 一块新的 100GB 分区 `/dev/nvme1n1p4`；
* 挂载点 `/mnt/lfs`；
* 环境变量 `$LFS=/mnt/lfs`；

你可以在这个挂载点里开始后续 LFS 第2章的构建工作（比如创建目录结构、下载源码等）。

---

## ⏭️ 下一步建议

如果你想继续体验，可以开始阅读 **LFS 第2章**（Preparing a New Partition），内容包括：

* 创建 LFS 目录结构；
* 设置权限；
* 准备源码包和补丁等。

需要我帮你提前总结第2章的要点，带你一步步完成吗？

```text
root@Fedora:~/LFS# parted -l
Model: Colorful CN700 1TB (nvme)
Disk /dev/nvme0n1: 1024GB
Sector size (logical/physical): 512B/512B
Partition Table: gpt
Disk Flags: 

Number  Start   End     Size    File system  Name                          Flags
 1      1049kB  106MB   105MB   fat32        Basic data partition          boot, esp, no_automount
 2      106MB   123MB   16.8MB               Microsoft reserved partition  msftres, no_automount
 3      123MB   1023GB  1023GB  ntfs         Basic data partition          msftdata, no_automount
 4      1023GB  1024GB  739MB   ntfs                                       hidden, diag, no_automount


Model: CT1000P3SSD8 (nvme)
Disk /dev/nvme1n1: 1000GB
Sector size (logical/physical): 512B/512B
Partition Table: gpt
Disk Flags: 

Number  Start   End     Size    File system  Name                  Flags
 1      1049kB  630MB   629MB   fat32        EFI System Partition  boot, esp
 2      630MB   1704MB  1074MB  xfs                                bls_boot
 3      1704MB  277GB   275GB                                      lvm


Model: Unknown (unknown)
Disk /dev/zram0: 8590MB
Sector size (logical/physical): 4096B/4096B
Partition Table: loop
Disk Flags: 

Number  Start  End     Size    File system     Flags
 1      0.00B  8590MB  8590MB  linux-swap(v1)


root@Fedora:~/LFS# fdisk /dev/nvme1n1

Welcome to fdisk (util-linux 2.40.4).
Changes will remain in memory only, until you decide to write them.
Be careful before using the write command.

This disk is currently in use - repartitioning is probably a bad idea.
It's recommended to umount all file systems, and swapoff all swap
partitions on this disk.


Command (m for help): n
Partition number (4-128, default 4): 4
First sector (540209152-1953525134, default 540209152): 
Last sector, +/-sectors or +/-size{K,M,G,T,P} (540209152-1953525134, default 1953523711): +100G

Created a new partition 4 of type 'Linux filesystem' and of size 100 GiB.

Command (m for help): w

The partition table has been altered.
Syncing disks.

root@Fedora:~/LFS# lsblk 
NAME                MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
zram0               251:0    0     8G  0 disk [SWAP]
nvme0n1             259:0    0 953.9G  0 disk 
├─nvme0n1p1         259:9    0   100M  0 part 
├─nvme0n1p2         259:10   0    16M  0 part 
├─nvme0n1p3         259:11   0 953.1G  0 part 
└─nvme0n1p4         259:12   0   705M  0 part 
nvme1n1             259:5    0 931.5G  0 disk 
├─nvme1n1p4         259:1    0   100G  0 part 
├─nvme1n1p1         259:6    0   600M  0 part /boot/efi
├─nvme1n1p2         259:7    0     1G  0 part /boot
└─nvme1n1p3         259:8    0   256G  0 part 
  └─fedora_192-root 252:0    0   256G  0 lvm  /
root@Fedora:~/LFS# sudo mkfs.ext4 /dev/nvme1n1p4
mke2fs 1.47.2 (1-Jan-2025)
Discarding device blocks: done                            
Creating filesystem with 26214400 4k blocks and 6553600 inodes
Filesystem UUID: ae5810bc-a0fc-4f96-8108-4dbe48b4736f
Superblock backups stored on blocks: 
        32768, 98304, 163840, 229376, 294912, 819200, 884736, 1605632, 2654208, 
        4096000, 7962624, 11239424, 20480000, 23887872

Allocating group tables: done                            
Writing inode tables: done                            
Creating journal (131072 blocks): done
Writing superblocks and filesystem accounting information: done   

root@Fedora:~/LFS# mkdir -pv /mnt/lfs
mkdir: created directory '/mnt/lfs'
root@Fedora:~/LFS# mount /dev/nvme1n1p4 /mnt/lfs/
root@Fedora:~/LFS# export LFS=/mnt/lfs
root@Fedora:~/LFS# echo 'export LFS=/mnt/lfs' >> ~/.bashrc 
root@Fedora:~/LFS# source ~/.bashrc 
root@Fedora:~/LFS# 
root@Fedora:~/LFS# 
root@Fedora:~/LFS# df -h
Filesystem                   Size  Used Avail Use% Mounted on
/dev/mapper/fedora_192-root  256G  9.8G  247G   4% /
devtmpfs                     4.0M     0  4.0M   0% /dev
tmpfs                         32G     0   32G   0% /dev/shm
efivarfs                     256K  125K  127K  50% /sys/firmware/efi/efivars
tmpfs                         13G  1.9M   13G   1% /run
tmpfs                        1.0M     0  1.0M   0% /run/credentials/systemd-journald.service
tmpfs                         32G     0   32G   0% /tmp
/dev/nvme1n1p2               893M  310M  583M  35% /boot
/dev/nvme1n1p1               599M  7.5M  592M   2% /boot/efi
tmpfs                        1.0M     0  1.0M   0% /run/credentials/systemd-resolved.service
tmpfs                        1.0M     0  1.0M   0% /run/credentials/getty@tty1.service
tmpfs                        6.3G  4.0K  6.3G   1% /run/user/0
/dev/nvme1n1p4                98G  2.1M   93G   1% /mnt/lfs
root@Fedora:~/LFS# df -h | grep /mnt/lfs/
root@Fedora:~/LFS# lsblk 
NAME                MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
zram0               251:0    0     8G  0 disk [SWAP]
nvme0n1             259:0    0 953.9G  0 disk 
├─nvme0n1p1         259:9    0   100M  0 part 
├─nvme0n1p2         259:10   0    16M  0 part 
├─nvme0n1p3         259:11   0 953.1G  0 part 
└─nvme0n1p4         259:12   0   705M  0 part 
nvme1n1             259:5    0 931.5G  0 disk 
├─nvme1n1p4         259:1    0   100G  0 part /mnt/lfs
├─nvme1n1p1         259:6    0   600M  0 part /boot/efi
├─nvme1n1p2         259:7    0     1G  0 part /boot
└─nvme1n1p3         259:8    0   256G  0 part 
  └─fedora_192-root 252:0    0   256G  0 lvm  /
root@Fedora:~/LFS# 
```

