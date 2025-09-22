# Yocto 编译框架

## 1. 在 WSL/Ubuntu 24.04 的推荐安装清单（无图形，够用）

### 1.1 适配 24.04，且适合我们用串口/无窗口跑 QEMU：

```bash
sudo apt install -y \
  gawk wget git diffstat unzip texinfo gcc-multilib build-essential chrpath socat \
  cpio python3 python3-pip python3-pexpect xz-utils debianutils iputils-ping \
  python3-git python3-jinja2 zstd liblz4-tool file locales \
  qemu-system-arm qemu-system-misc qemu-utils bmap-tools parted dosfstools e2fsprogs
```

### 1.2 快速自检

```bash
qemu-system-aarch64 --version        # 能输出版本就对了
bitbake --version                    # 还没装 Yocto 不会有；后面会有
python3 -c "import jinja2,pexpect; print('ok')"  # 正常则无报错
```

### 1.3 WSL 使用小提示

* WSL2 里 **不能用 KVM**，QEMU 会走 TCG 纯软件虚拟化，正常但慢一点；脚本里不要加 `-accel kvm`。
* 如果 `-m 32G` 报错，先减到 `-m 8G` 试跑；需要的话再在 `~/.wslconfig` 调大内存上限。
* Yocto 构建对文件句柄很多，建议：

  ```bash
  ulimit -n 4096
  git config --global core.autocrlf false
  ```

下面给你一套**可直接照做**的流程：用 Yocto 在 QEMU 上搭建一台“ARMv8 嵌入式平台”，具备串口、以太网、PCIe（挂 NVMe SSD
128G）、“NOR 存放 bootloader 的味道”（用 pflash 近似）、32 GB DRAM。目标是产出：U-Boot、内核、设备树与根文件系统镜像，并在 QEMU 上从
NVMe 启动系统。

> 说明
>
> * 机器模型：QEMU `-M virt`（aarch64）。
> * 网络：virtio-net（含主机端口转发，便于 SSH）。
> * NVMe：QEMU 的 `-device nvme`。
> * “SPI NOR”：用 QEMU pflash 近似（可把 U-Boot 放进去，相当于板上 NOR/固件区）。
> * 设备树：QEMU 会提供一份“virt”DT，Linux 也会构建对应 dtb；U-Boot 采用 QEMU 传入的 DT 或 extlinux 指定 dtb 均可。
> * 用 Yocto LTS 分支（如 kirkstone）更稳。

---

## 2. 获取 Yocto 代码并初始化

```bash
# 获取 poky（Yocto 参考发行版），示例使用 LTS 分支
git clone git://git.yoctoproject.org/poky -b kirkstone
cd poky

# 可选：常用社区层（这次不强依赖，但以后可能用到）
git clone https://github.com/openembedded/meta-openembedded -b kirkstone

# 初始化构建目录（进入 build/）
source oe-init-build-env
```

编辑 `build/conf/bblayers.conf`，加入 meta-openembedded（若 clone 了）：

```text
BBLAYERS ?= " \
  ${TOPDIR}/../poky/meta \
  ${TOPDIR}/../poky/meta-poky \
  ${TOPDIR}/../poky/meta-yocto-bsp \
  ${TOPDIR}/../meta-openembedded/meta-oe \
"
```

编辑 `build/conf/local.conf`（要点如下）：

```text
MACHINE ??= "qemuarm64"                 # 目标 QEMU aarch64
BB_NUMBER_THREADS ?= "8"
PARALLEL_MAKE ?= "-j8"

# 镜像类型：生成 .wic 方便当作 NVMe 整盘镜像
IMAGE_FSTYPES += "wic wic.bmap"

# 开启 SSH server、调试特性
EXTRA_IMAGE_FEATURES += "ssh-server-dropbear debug-tweaks"

# 后面我们会自定义一个 WKS 分区脚本
WKS_FILE ?= "nvme-gpt.wks"

# 把下载与 sstate 放到大磁盘（可选但强烈建议）
DL_DIR ?= "${TOPDIR}/downloads"
SSTATE_DIR ?= "${TOPDIR}/sstate-cache"
```

---

## 3. 创建自定义层，放内核/U-Boot 配置与镜像定义

BitBake 服务器因系统 locale 不是 UTF-8（或缺少 en_US.UTF-8）而起不来

```text
# 1) 安装并生成 UTF-8 本地化
sudo apt update
sudo apt install -y locales
sudo locale-gen en_US.UTF-8 zh_CN.UTF-8

# 2) 设为默认（写入 /etc/default/locale）
sudo update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 LANGUAGE=en_US:en

# 3) 在当前 shell 生效
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
export LANGUAGE=en_US:en

# 4) 验证
locale -a | grep -i en_US     # 应看到 en_US.utf8
locale                         # 各项应为 en_US.UTF-8
```

清理并重试

```text
# 重新进入 Yocto 环境
cd ~/Yocto/poky
source oe-init-build-env

# 可清一下上次残留的 cooker 进程/日志（可选）
rm -rf build/bitbake-cookerdaemon.*

# 再次创建并加入 layer
bitbake-layers create-layer ../meta-virtarm64
bitbake-layers add-layer ../meta-virtarm64
bitbake-layers show-layers
```

### 查看结果

```text
bitbake-layers show-layers
```

目录结构（建议）：

```
meta-virtarm64/
  conf/layer.conf
  recipes-kernel/linux/
    linux-yocto_%.bbappend
    files/my-kernel.cfg
  recipes-bsp/u-boot/
    u-boot_%.bbappend
    files/u-boot.cfg
  recipes-core/images/
    my-image.bb
  wic/
    nvme-gpt.wks
```

## 3.1 Kernel 配置（启用 PCIe/NVMe/virtio 等）

`recipes-kernel/linux/linux-yocto_%.bbappend`：

```text
FILESEXTRAPATHS:prepend := "${THISDIR}/files:"
SRC_URI:append = " file://my-kernel.cfg"
```

`recipes-kernel/linux/files/my-kernel.cfg`（关键开关，尽量内建/模块均可）：

```text
CONFIG_PCI=y
CONFIG_PCI_HOST_GENERIC=y
CONFIG_PCIEPORTBUS=y

CONFIG_BLK_DEV_NVME=y
CONFIG_NVME_HWMON=y
CONFIG_NVME_MULTIPATH=y

CONFIG_VIRTIO_PCI=y
CONFIG_VIRTIO_NET=y
CONFIG_VIRTIO_BLK=y
CONFIG_VIRTIO_MMIO=y
CONFIG_NET=y
CONFIG_PACKET=y
CONFIG_UNIX=y
CONFIG_INET=y

CONFIG_DEVTMPFS=y
CONFIG_DEVTMPFS_MOUNT=y
CONFIG_FHANDLE=y

# 如果希望在 Linux 中看到“NOR MTD”，需要平台 DT 暴露映射的 NOR。
# QEMU virt 上使用 pflash 主要给固件用，Linux 不一定默认映射出来。
# 如需在 Linux 内访问，请自备 DT 节点（进阶玩法，先跳过）。
# CONFIG_MTD=y
# CONFIG_MTD_BLOCK=y
# CONFIG_MTD_CFI=y
# CONFIG_MTD_CFI_AMDSTD=y
# CONFIG_MTD_SPI_NOR=y
# CONFIG_SPI=y
```

> 说明：qemuarm64 默认内核配置已经能跑 virtio；上面 fragment 主要确保 NVMe/PCIe 等开启。如果后续发现某驱动缺失，可再补。

## 3.2 U-Boot 配置（支持 NVMe 扫描、distro 启动）

`recipes-bsp/u-boot/u-boot_%.bbappend`：

```text
FILESEXTRAPATHS:prepend := "${THISDIR}/files:"
SRC_URI:append = " file://u-boot.cfg"
UBOOT_CONFIG_FRAGMENT:append = " file://u-boot.cfg"
```

`recipes-bsp/u-boot/files/u-boot.cfg`：

```text
CONFIG_PCI=y
CONFIG_DM_PCI=y
CONFIG_NVME=y
CONFIG_CMD_NVME=y
CONFIG_CMD_PCI=y
CONFIG_CMD_PART=y
CONFIG_CMD_EXT4=y
CONFIG_CMD_FAT=y
CONFIG_DISTRO_DEFAULTS=y
CONFIG_BOOTSTD_DEFAULTS=y
CONFIG_REGEX=y
CONFIG_CMD_DHCP=y
CONFIG_CMD_PING=y
```

> 这让 U-Boot 具备 `pci`、`nvme`、`extlinux`（distro 启动）能力，它会自动在 NVMe 分区的 `/boot/extlinux/extlinux.conf` 查找启动项。

## 3.3 自定义镜像（带基础工具）

`recipes-core/images/my-image.bb`：

```text
SUMMARY = "Minimal image for QEMU ARM64 with NVMe + SSH"
LICENSE = "MIT"
require recipes-core/images/core-image-minimal.bb

IMAGE_INSTALL:append = " \
    kernel-modules \
    iproute2 ethtool pciutils nvme-cli \
    bash \
"
```

## 3.4 WIC 分区脚本（NVMe GPT，两分区）

`wic/nvme-gpt.wks`：

```text
# GPT 分区表，/boot + / 根分区；根分区 --grow 以便后续扩容
part /boot --source bootimg-partition --ondisk sda --fstype=ext4 --label boot --size 200
part /     --source rootfs           --ondisk sda --fstype=ext4 --label root --size 2048 --grow
bootloader --ptable gpt
```

> 这里的 `ondisk sda` 只是生成镜像时的占位符，最终作为整盘 .wic 供 QEMU 以 NVMe 呈现即可。`--grow` 允许后续在线扩容（用
`growpart`/`resize2fs`）。

---

# 4. 构建

```bash
bitbake my-image
# 构建完成的产物在：
# build/tmp/deploy/images/qemuarm64/
#   Image、*.dtb、u-boot.bin、my-image-qemuarm64.wic 等
```

---

# 5. 准备“128G NVMe 硬盘镜像”与“pflash(U-Boot)”

## 5.1 生成 128G 的 NVMe raw 文件，并写入 .wic

```bash
cd tmp/deploy/images/qemuarm64

# 1) 先做一个 128G 的空 raw 文件（NVMe 硬盘）
truncate -s 128G nvme.img

# 2) 把 Yocto 生成的 .wic 覆盖到开头（保留后面空白空间以备将来扩容）
#   注意把 my-image-*.wic 替换成你的实际文件名
dd if=my-image-qemuarm64.wic of=nvme.img bs=4M conv=notrunc status=progress
sync
```

> 现在 `nvme.img` 就是一块 128G 的“硬盘”，前部已经写入了可启动的 GPT/boot/rootfs。

## 5.2 准备 pflash 放 U-Boot（近似“SPI NOR 存放 bootloader”）

```bash
# 做一个 64MB 的 pflash 映像（常见容量，足够放 U-Boot）
dd if=/dev/zero of=flash0.img bs=1M count=64

# 把 u-boot.bin 写进去（从起始位置）
dd if=u-boot.bin of=flash0.img conv=notrunc

sync
```

> 备注：QEMU 的 pflash 是内存映射 NOR 的近似，主要模拟“固件区”。在 `-M virt` 上，这更符合“板上 NOR 放
> bootloader/固件”的使用场景。Linux 里不一定把它当 MTD 暴露出来，**这不影响从 NVMe 启动操作系统**。

---

# 6. 启动 QEMU（串口 + 以太网 + PCIe + NVMe + 32G 内存）

写个脚本 `run-qemu.sh`（放在 `tmp/deploy/images/qemuarm64/` 里）：

```bash
#!/usr/bin/env bash
set -e

QEMU=qemu-system-aarch64
NVME_IMG=nvme.img
PFLASH_IMG=flash0.img

${QEMU} \
  -M virt,gic-version=3,virtualization=true \
  -cpu cortex-a57 \
  -smp 4 \
  -m 32G \
  -nographic \
  \
  # 以 pflash 近似 SPI NOR，放 U-Boot
  -drive if=pflash,format=raw,file=${PFLASH_IMG} \
  \
  # NVMe 硬盘（作为 PCIe 设备）
  -blockdev driver=file,filename=${NVME_IMG},node-name=nvmefile,auto-read-only=off,discard=unmap \
  -device pcie-root-port,id=rp1 \
  -device nvme,drive=nvmefile,serial=nvme-1,bus=rp1 \
  \
  # 以太网（用户态虚拟网络，转发主机 2222 -> 来宾 22）
  -netdev user,id=net0,hostfwd=tcp::2222-:22 \
  -device virtio-net-pci,netdev=net0 \
  \
  # 可选：随机数设备，避免熵不足
  -device virtio-rng-pci
```

```bash
chmod +x run-qemu.sh
./run-qemu.sh
```

> 说明
>
> * `-nographic`：串口在当前终端（`ttyAMA0`），符合“串口启动”。
> * `-m 32G`：32 GB DRAM。
> * PCIe x8 的“宽度”QEMU 并不做物理带宽精确建模；但设备挂在 PCIe 总线上，功能路径与驱动栈等价。
> * 如果你不想用 pflash，也可以直接 `-bios u-boot.bin`（更简单），本文为了贴近“NOR 放 bootloader”的设定才使用 pflash。

---

# 7. 在 U-Boot 中从 NVMe 启动

启动后进入 U-Boot 提示符，验证 PCIe/NVMe：

```text
=> pci enum
=> nvme scan
=> nvme info
```

若 Yocto 自动生成了 `/boot/extlinux/extlinux.conf`（qemuarm64 一般会有），可直接：

```text
=> sysboot nvme 0:1 any /boot/extlinux/extlinux.conf
```

想让它**下次自动**走 NVMe 的 distro 启动：

```text
=> env set boot_targets nvme0
=> saveenv   # 需 U-Boot 有环境保存介质；若没有，这步就省略，每次手动 sysboot
=> boot
```

> 小技巧：若想无交互，给 QEMU 加 `-device virtio-serial-pci` 并设置 `U-BOOT` 环境为 `bootcmd=...` 也行。最简做法是每次
`sysboot`。

---

# 8. 进入系统后的验证

系统启动后（串口登录或从宿主机 SSH：`ssh -p 2222 root@127.0.0.1`，默认 root 无密码若启用 `debug-tweaks`）：

```bash
# 看到 NVMe
nvme list
lsblk
lspci -nn
# 网络
ip addr
ping -c 3 8.8.8.8
# 查看内核/设备树信息
dmesg | grep -i -e nvme -e pcie -e virtio
uname -a
```

如果你要把根分区扩到 128G：

```bash
# 示例（安装 growpart & 扩容根分区；不同发行可换包）
# growpart /dev/nvme0n1 2
# resize2fs /dev/nvme0n1p2
```

---

# 9. 常见问题与排查

1. **U-Boot 找不到 extlinux.conf**

* 确认 `my-image` 产出的 `/boot/extlinux/extlinux.conf` 存在（Yocto 对 qemuarm64 通常会生成）。
* 若没有，可自己打包一个很小的 bootfiles 包把 `extlinux.conf` 安装到 `/boot/extlinux/`，或改用手写 `boot.cmd/boot.scr`。

2. **NVMe 未出现**

* 确认内核已启用 `CONFIG_BLK_DEV_NVME`（见 fragment）。
* QEMU 命令行里 `-device nvme,...` 是否正确；`pci enum`、`nvme scan` 在 U-Boot 是否能看到设备。

3. **网络不通/SSH 不通**

* `-netdev user,id=net0,hostfwd=tcp::2222-:22` 要求镜像内有 SSH server（`dropbear` 已包含）。
* 来宾里 `ip addr` 看是否获取到 10.0.2.x 之类地址；`systemctl status dropbear`。

4. **想用 `-bios u-boot.bin` 代替 pflash**

* 可以，把脚本里的 pflash 两行删掉，改为 `-bios u-boot.bin`，其他不变。

5. **设备树定制**

* 默认用 QEMU 的“virt”DT。若你要显式指定 Linux dtb：

    * 在 extlinux 条目里设置 `FDT` 或 `FDTDIR` 指向 Yocto 生成的 `virt.dtb`；
    * 或者在 U-Boot 里 `load` dtb 后 `booti`/`bootm`。
* 真要在 Linux 中映射并访问“板上 NOR”，需要在 DT 里加相应 `flash@...` 节点（QEMU virt 默认不做），这属于进阶话题。

---

# 10. 复用与加速建议

* 固定 `DL_DIR` 与 `SSTATE_DIR` 到共享目录，团队多人构建会快很多。
* `bitbake -c cleansstate <pkg>` 清理某个包、`bitbake -c listtasks virtual/kernel` 查看可用任务、`bitbake -e <pkg>` 查最终变量。
* 需要 SDK 交叉编译环境：`bitbake my-image -c populate_sdk`。

---

如果你愿意，我可以把上述**自定义层（meta-virtarm64）完整骨架**、`extlinux.conf`（显式指定 Image 与 dtb 的版本无关写法）、以及一键
`run-qemu.sh` 打包成可下载的压缩包，直接放进你的工程里就能编译运行。

 

