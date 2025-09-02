# LFS 环境创建根分区与环境配置

在 Fedora Server 42（VMware 虚拟机）环境下上编译 [LFS](https://lfs.xry111.site/zh_CN/12.3-systemd/)

## 0. 虚拟机参数

- 虚拟机创建：Fedora Server 42 Disk 80G，安装完操作系统后关机，然后选择扩展为 160G，这样会有 80G 新的空闲空间分配给 LFS
- 调整 CPU 和内存为至少 4U8G

## 1. 安装编译工具

```text
sudo dnf install ncurses-devel bison flex elfutils-libelf-devel openssl-devel \
  dwarves perl git gcc make bc zstd xz wget patch texinfo -y
```

## 2. yacc is not Bison 的问题

> 构建包装器: 放一个 wrapper 到 /usr/bin

- 确保 bison 已安装

```text
dnf install -y bison
```

- 写一个兼容的 yacc 包装脚本

```text
install -d /usr/bin
cat > /usr/bin/yacc <<'EOF'
#!/bin/sh
exec bison -y "$@"
EOF
chmod +x /usr/bin/yacc
```

- 验证 PATH 与版本，应显示 bison 的版本

```text
yacc --version
```

## 3. 工具版本检测脚本

[version-check.sh](./version-check.sh)

## 4. 在磁盘上创建并格式化独立的 LFS 根分区

> 本文以 **新建独立分区** 作为 LFS 根分区为例（推荐做法，后续可直接引导 LFS）。

* 目标磁盘：`/dev/nvme0n1`（示例；若不同请替换）
* 目标容量：约 80GiB 空闲空间

### 4.1 识别磁盘与空闲空间

- 确认磁盘末尾存在约 **80GiB** 的 *Free Space*

```bash
parted -s /dev/nvme0n1 unit GiB print free
```

```text
[root@localhost ~]# parted -s /dev/nvme0n1 unit GiB print free
Model: VMware Virtual NVMe Disk (nvme)
Disk /dev/nvme0n1: 160GiB
Sector size (logical/physical): 512B/512B
Partition Table: gpt
Disk Flags: pmbr_boot

Number  Start    End      Size     File system  Name  Flags
        0.00GiB  0.00GiB  0.00GiB  Free Space
 1      0.00GiB  0.00GiB  0.00GiB                     bios_grub
 2      0.00GiB  1.00GiB  1.00GiB  xfs                bls_boot
 3      1.00GiB  80.0GiB  79.0GiB                     lvm
        80.0GiB  160GiB   80.0GiB  Free Space
```

---

### 4.2 创建 LFS 根分区（ext4）

> 若你与示例环境一致，空闲区从 \~80GiB 开始直至磁盘末尾，可直接使用下列命令。

- 在空闲区新建主分区 p4（名字 LFS，类型 ext4）

```bash
parted /dev/nvme0n1 --script mkpart LFS ext4 80GiB 100%
```

- 让内核刷新分区表

```bash
partprobe /dev/nvme0n1
```

- 检查分区情况

```bash
lsblk -o NAME,TYPE,SIZE,FSTYPE,MOUNTPOINT
```

```text
[root@localhost ~]# lsblk -o NAME,TYPE,SIZE,FSTYPE,MOUNTPOINT
NAME            TYPE  SIZE FSTYPE      MOUNTPOINT
sr0             rom   2.7G iso9660
zram0           disk  1.9G swap        [SWAP]
nvme0n1         disk  160G
├─nvme0n1p1     part    1M
├─nvme0n1p2     part    1G xfs         /boot
├─nvme0n1p3     part   79G LVM2_member
│ └─fedora-root lvm    79G xfs         /
└─nvme0n1p4     part   80G
```

---

### 4.3 在新分区上创建文件系统

- 给文件系统打上标签 `LFS`，便于后续通过 `LABEL`/`UUID` 挂载。

```bash
mkfs.ext4 -L LFS /dev/nvme0n1p4
```

- 挂载到 LFS 规范位置

LFS 约定根挂载点为 **`/mnt/lfs`**。

```bash
export LFS=/mnt/lfs
mkdir -pv $LFS
mount -v /dev/nvme0n1p4 $LFS
```

- 验证

```bash
lsblk -f /dev/nvme0n1p4
```

应显示类型 `ext4`、挂载点 `/mnt/lfs`、标签 `LFS`。

---

### 4.4 开机自动挂载

- 使用 `UUID` 方式最稳妥：记下 UUID=xxxxxxxx-xxxx-....

```bash
sudo blkid /dev/nvme0n1p4
```

- 追加到 /etc/fstab（将 <UUID> 替换为上一行输出的实际值）

```text
echo 'UUID=<UUID>  /mnt/lfs  ext4  defaults  0  1' | sudo tee -a /etc/fstab
```

> 验证：`sudo mount -a` 应无报错，`df -hT /mnt/lfs` 正常。

---

## 5. 设置环境变量 `LFS`

LFS 全书要求使用变量 `LFS` 指向挂载点。为当前用户持久化：

```bash
# 一次性生效（当前 shell）
export LFS=/mnt/lfs

# 写入登录 shell 配置，持久化
if ! grep -q '^export LFS=' ~/.bashrc; then
  echo 'export LFS=/mnt/lfs' >> ~/.bashrc
fi
# 让其立即生效
source ~/.bashrc
```

- 验证: 应输出 /mnt/lfs
```text
echo $LFS        # 
```
