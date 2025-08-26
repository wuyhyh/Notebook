# LFS 根分区与环境变量准备

> 目标：从“创建 LFS 根分区”到“设置环境变量 `LFS`”，在 Fedora Server（VMware 虚拟机）环境下完成。

---

## 适用前提

* 宿主系统：Fedora Server 42
* 启动方式：BIOS 或 UEFI 皆可
* 目标磁盘：`/dev/nvme0n1`（示例；若不同请替换）
* 目标容量：约 100GiB 空闲空间

> 本文以 **新建独立分区** 作为 LFS 根分区为例（推荐做法，后续可直接引导 LFS）。

---

## 1. 识别磁盘与空闲空间

```bash
lsblk -o NAME,TYPE,SIZE,FSTYPE,MOUNTPOINT
sudo parted -s /dev/nvme0n1 unit GiB print free
```

确认磁盘末尾存在约 **100GiB** 的 *Free Space*。

---

## 2. 创建 LFS 根分区（ext4）

> 若你与示例环境一致，空闲区从 \~100GiB 开始直至磁盘末尾，可直接使用下列命令。

```bash
# 在空闲区新建主分区 p4（名字 LFS，类型 ext4）
sudo parted /dev/nvme0n1 --script mkpart LFS ext4 100GiB 100%

# 让内核刷新分区表
sudo partprobe /dev/nvme0n1

# 也可以用交互式工具：
# sudo cfdisk /dev/nvme0n1  # 选择 Free space → New → 指定大小 → Type=Linux filesystem → Write
```

> **检查**：

```bash
lsblk -o NAME,SIZE,TYPE /dev/nvme0n1
```

应能看到新分区，例如 `nvme0n1p4`。

---

## 3. 在新分区上创建文件系统

```bash
sudo mkfs.ext4 -L LFS /dev/nvme0n1p4
```

> 给文件系统打上标签 `LFS`，便于后续通过 `LABEL`/`UUID` 挂载。

---

## 4. 挂载到 LFS 规范位置

LFS 约定根挂载点为 **`/mnt/lfs`**。

```bash
export LFS=/mnt/lfs
sudo mkdir -pv $LFS
sudo mount -v /dev/nvme0n1p4 $LFS
```

**验证：**

```bash
df -hT $LFS
lsblk -f /dev/nvme0n1p4
```

应显示类型 `ext4`、挂载点 `/mnt/lfs`、标签 `LFS`。

---

## 5. 开机自动挂载

使用 `UUID` 方式最稳妥：

```bash
sudo blkid /dev/nvme0n1p4   # 记下 UUID=xxxxxxxx-xxxx-....

# 追加到 /etc/fstab（将 <UUID> 替换为上一行输出的实际值）
echo 'UUID=<UUID>  /mnt/lfs  ext4  defaults  0  1' | sudo tee -a /etc/fstab
```

> 验证：`sudo mount -a` 应无报错，`df -hT /mnt/lfs` 正常。

---

## 6. 设置环境变量 `LFS`

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

# 验证
echo $LFS        # 应输出 /mnt/lfs
```

> 注意：后续在第 4 章还会创建 `lfs` 专用用户，**该用户的 `~/.bashrc` 也要设置同样的 `export LFS=/mnt/lfs`**。

---

## 7.（可选）为后续章节准备基础目录

虽不在本节硬性要求，但建议现在创建：

```bash
sudo mkdir -pv $LFS/{sources,tools}
sudo chmod -v a+wt $LFS/sources
# 按 LFS 习惯在根目录放一个 /tools 链接
if [ ! -e /tools ]; then sudo ln -sv $LFS/tools /; fi
```

---

完成以上步骤，你已经：

1. 在磁盘上创建并格式化了独立的 **LFS 根分区**；
2. 将其挂载至 LFS 规范路径 **`/mnt/lfs`** 并配置自动挂载；
3. 正确设置了环境变量 **`LFS`**，为后续章节做了准备。
