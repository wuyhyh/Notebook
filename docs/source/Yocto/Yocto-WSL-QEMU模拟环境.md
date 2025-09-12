# Yocto WSL QEMU 模拟环境

在 WSL 中使用 Ubuntu 24.04，编译一个 yocto 功能，从 qemu 启动进行模拟

## 0. 准备环境（WSL2 / Ubuntu 24.04）

- 基础包

```bash
sudo apt update
sudo apt install -y \
  rpcgen gawk wget git diffstat unzip texinfo gcc-multilib build-essential chrpath socat \
  cpio python3 python3-pip python3-pexpect xz-utils debianutils iputils-ping \
  python3-git python3-jinja2 zstd liblz4-tool file locales \
  qemu-system-arm qemu-system-misc qemu-utils bmap-tools parted dosfstools e2fsprogs
```

- 修复 locale（BitBake 必须是 UTF-8）

```text
sudo locale-gen en_US.UTF-8 zh_CN.UTF-8
sudo update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 LANGUAGE=en_US:en
export LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 LANGUAGE=en_US:en
```

注意：WSL2 无 KVM，加 `-accel tcg` 即可。把工程放在 WSL 的 ext4（如 `~/Yocto`），不要放 `/mnt/c`。

---

## 1. 获取 Yocto 源码并初始化

```bash
mkdir -p ~/Yocto && cd ~/Yocto
git clone git://git.yoctoproject.org/poky -b kirkstone
cd poky
git clone https://github.com/openembedded/meta-openembedded -b kirkstone
```

- 初始化构建目录（生成并进入 build/）

```text
source oe-init-build-env
```

---

## 2.配置 `build/conf/local.conf`

用下面的内容覆盖或追加关键项（保持其他行不动）：

```bash
cat >> conf/local.conf <<'EOF'

# ---- QEMU ARM64 目标与镜像设置 ----
MACHINE ??= "qemuarm64"

BB_NUMBER_THREADS ?= "12"
PARALLEL_MAKE ?= "-j12"

# 生成 .wic 方便当作整盘镜像
IMAGE_FSTYPES += "wic wic.bmap"

# 打开 SSH 和调试
EXTRA_IMAGE_FEATURES += "ssh-server-dropbear debug-tweaks"

# 使用自定义的 wic 脚本名
WKS_FILE ?= "nvme-gpt.wks"

# 建议把下载与 sstate 放到工程目录下，便于复用
DL_DIR ?= "${TOPDIR}/downloads"
SSTATE_DIR ?= "${TOPDIR}/sstate-cache"
EOF
```

---

## 3. 创建并加入自定义层 meta-virtarm64

**不要手改 `bblayers.conf`，用命令追加最安全。**

- 仍然在 poky/build 下

```bash
bitbake-layers create-layer ../meta-virtarm64
bitbake-layers add-layer ../meta-openembedded/meta-oe
bitbake-layers add-layer ../meta-virtarm64
bitbake-layers show-layers
```

看到 meta-virtarm64 和 meta-oe 即成功
---

## 4. 在 meta-virtarm64 放好必须文件

### 4.1 layer 搜索路径与目录骨架

```bash
cd ../meta-virtarm64
mkdir -p recipes-core/images \
         recipes-kernel/linux/files \
         recipes-bsp/u-boot/files \
         wic
```

- 让 wic 能在本层找到自定义 .wks

```text
echo 'WKS_SEARCH_PATH:prepend = "${LAYERDIR}/wic:"' >> conf/layer.conf
```

### 4.2 自定义镜像（也可先用 core-image-minimal）

`recipes-core/images/my-image.bb`：

```bash
cat >> recipes-core/images/my-image.bb <<'EOF'
SUMMARY = "Minimal image for QEMU ARM64 with NVMe + SSH"
LICENSE = "MIT"
require recipes-core/images/core-image-minimal.bb

IMAGE_INSTALL:append = " kernel-modules iproute2 ethtool pciutils nvme-cli bash "
EOF
```

### 4.3 自定义 WIC（与 `local.conf` 里的 `WKS_FILE` 对应）

`wic/nvme-gpt.wks`：

```text
cat >> wic/nvme-gpt.wks <<'EOF'
part /boot --source bootimg-partition --ondisk sda --fstype=ext4 --label boot --size 200
part /     --source rootfs           --ondisk sda --fstype=ext4 --label root --size 2048
bootloader --ptable gpt
EOF
```

### 4.4（可选，推荐）内核与 U-Boot 配置片段

让内核与 U-Boot 自带 NVMe/PCI/网络等支持。没有也能启动，遇到功能缺再补。

`recipes-kernel/linux/linux-yocto_%.bbappend`：

```text
cat >> recipes-kernel/linux/linux-yocto_%.bbappend <<'EOF'
FILESEXTRAPATHS:prepend := "${THISDIR}/files:"
SRC_URI:append = " file://my-kernel.cfg"
EOF
```

`recipes-kernel/linux/files/my-kernel.cfg`：

```text
cat >> recipes-kernel/linux/files/my-kernel.cfg <<'EOF'
CONFIG_PCI=y
CONFIG_PCI_HOST_GENERIC=y
CONFIG_PCIEPORTBUS=y
CONFIG_BLK_DEV_NVME=y
CONFIG_NVME_MULTIPATH=y
CONFIG_VIRTIO_PCI=y
CONFIG_VIRTIO_NET=y
CONFIG_VIRTIO_BLK=y
CONFIG_VIRTIO_MMIO=y
CONFIG_DEVTMPFS=y
CONFIG_DEVTMPFS_MOUNT=y
EOF
```

`recipes-bsp/u-boot/u-boot_%.bbappend`：

```text
cat >> recipes-bsp/u-boot/u-boot_%.bbappend <<'EOF'
FILESEXTRAPATHS:prepend := "${THISDIR}/files:"
SRC_URI:append = " file://u-boot.cfg"
EOF
```

`recipes-bsp/u-boot/files/u-boot.cfg`：

```text
cat >> recipes-bsp/u-boot/files/u-boot.cfg <<'EOF'
CONFIG_PCI=y
CONFIG_DM_PCI=y
CONFIG_NVME=y
CONFIG_CMD_NVME=y
CONFIG_CMD_PCI=y
CONFIG_CMD_PART=y
CONFIG_CMD_EXT4=y
CONFIG_CMD_FAT=y
CONFIG_DISTRO_DEFAULTS=y
CONFIG_CMD_DHCP=y
CONFIG_CMD_PING=y
EOF
```

---

## 5. 开始构建

```bash
cd ~/Yocto/poky
source oe-init-build-env           # 每次新开终端都要执行
bitbake-layers show-layers         # 再确认一遍层
```

- 构建镜像（二选一）

```text
bitbake my-image
```

> 或
> ```text
> bitbake core-image-minimal
> ```

产物位置：`build/tmp/deploy/images/qemuarm64/`（`Image`、`*.dtb`、`u-boot.bin`、`*.wic` 等）。

---

# 6）准备 NVMe “硬盘”与 pflash “NOR”

```bash
cd build/tmp/deploy/images/qemuarm64

# 128G NVMe 原始镜像，并把 .wic 写到开头
truncate -s 128G nvme.img
dd if=my-image-qemuarm64.wic of=nvme.img bs=4M conv=notrunc status=progress
sync

# pflash 给 U-Boot（64MB 足够）
dd if=/dev/zero of=flash0.img bs=1M count=64
dd if=u-boot.bin of=flash0.img conv=notrunc
sync
```

---

# 7）启动 QEMU（串口、网络端口转发、NVMe）

`run-qemu.sh`（存放在同一目录）：

```bash
#!/usr/bin/env bash
set -e
QEMU=qemu-system-aarch64

${QEMU} \
  -M virt,gic-version=3,virtualization=true \
  -cpu cortex-a57 \
  -smp 4 \
  -m 8192 \               # WSL2 内存有限，先 8G；够用再调大
  -nographic \
  -accel tcg,thread=multi \
  \
  -drive if=pflash,format=raw,file=flash0.img \
  \
  -blockdev driver=file,filename=nvme.img,node-name=nvmefile,auto-read-only=off,discard=unmap \
  -device pcie-root-port,id=rp1 \
  -device nvme,drive=nvmefile,serial=nvme-1,bus=rp1 \
  \
  -netdev user,id=net0,hostfwd=tcp::2222-:22 \
  -device virtio-net-pci,netdev=net0 \
  -device virtio-rng-pci
```

```bash
chmod +x run-qemu.sh
./run-qemu.sh
```

---

# 8）在 U-Boot/系统里验证与启动

进入 U-Boot：

```
=> pci enum
=> nvme scan
=> nvme info
=> sysboot nvme 0:1 any /boot/extlinux/extlinux.conf
```

进入系统后：

```bash
nvme list
lsblk
lspci -nn
ip addr
ssh -p 2222 root@127.0.0.1   # 默认 root 无密码（debug-tweaks）
```

---

# 9）两处关键自检（出问题先看它们）

```bash
# WIC 是否被识别到
bitbake -e core-image-minimal | sed -n 's/^WKS_FILE.*/&/p'
bitbake -e core-image-minimal | sed -n 's/^WKS_SEARCH_PATH.*/&/p'
# 应该分别看到 nvme-gpt.wks 与包含 meta-virtarm64/wic 的搜索路径

# 层是否都已启用
bitbake-layers show-layers
```

---

# 10）常见错误对照

* `locale 'en_US.UTF-8' is not available` → 按第 0）步生成并 `export`。
* 解析 `bblayers.conf` 失败 → 不要手改；用 `bitbake-layers add-layer` 管理。
* 找不到 `nvme-gpt.wks` → 确认文件名、路径 `meta-virtarm64/wic/`，以及 `layer.conf` 里有 `WKS_SEARCH_PATH`。
* QEMU 内存报错 → 把 `-m` 调小，或在 `~/.wslconfig` 提高内存上限后重启 WSL。

---

照上述顺序做，你需要手动编辑/新增的文件只有这几个：

1. `build/conf/local.conf`（追加几行配置）
2. `meta-virtarm64/conf/layer.conf`（追加一行 `WKS_SEARCH_PATH`）
3. `meta-virtarm64/wic/nvme-gpt.wks`
4. `meta-virtarm64/recipes-core/images/my-image.bb`
5. （可选）`meta-virtarm64/recipes-kernel/linux/linux-yocto_%.bbappend` 与 `files/my-kernel.cfg`
6. （可选）`meta-virtarm64/recipes-bsp/u-boot/u-boot_%.bbappend` 与 `files/u-boot.cfg`
7. `run-qemu.sh`

如果你把当前目录树发我一张 `tree` 截图，我可以对照帮你逐项勾掉。

