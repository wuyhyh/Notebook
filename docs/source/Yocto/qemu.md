下面给你一套“可落地”的做法：用 QEMU 的通用 AArch64 `virt` 机型去近似你的 D2000 核心板。要说明的是：QEMU 暂不模拟飞腾 D2000 的专用外设与精确微架构，但用 `virt` 可以一次性搞定你关心的几乎所有部件：16 GB 内存、PCIe-NVMe 磁盘、串口控制台、千兆网口，以及用于固件的 NOR（通常用 pflash 来等效/替代 SPI-NOR）。

---

# 你要准备的文件（最小集合）

1. U-Boot（可选，但推荐）

* 目标：`qemu_arm64` 板级，得到 `u-boot.bin`（作为固件/BIOS 启动）
* 作用：用 U-Boot 的 distro boot/EXTLINUX 从 NVMe 分区启动内核

2. Linux 内核

* 目标：`Image`（arm64 内核镜像）与 `virt.dtb`（可选；QEMU 会自动提供 DTB，不指定也能启动）
* 必要配置：

    * `CONFIG_PCI=y`, `CONFIG_PCI_HOST_GENERIC=y`（virt 上的 PCIe Host）
    * `CONFIG_BLK_DEV_NVME=y`（NVMe 驱动）
    * `CONFIG_SERIAL_AMBA_PL011=y`（`ttyAMA0` 串口）
    * `CONFIG_VIRTIO_NET=y` 或 `CONFIG_VIRTIO_NET_PCI=y`（网卡）
    * `CONFIG_EXT4_FS=y`（如用 ext4 根分区）

3. RootFS

* 两条路：
  A. **initramfs**（`rootfs.cpio.gz`，最快能看到 shell）
  B. **NVMe 上的 ext4 根分区**（更贴近真实部署；/ 分区 + /boot 放内核与 extlinux 配置）

4. NVMe 磁盘镜像

* 一个 128 GB 的镜像文件（qcow2 或 raw），里面建 GPT 分区（建议 /boot + / 分区）

> 可选：NOR/“SPI-NOR”
>
> * 在 `virt` 机型上最简单的是 **pflash** 作为固件存储（非 SPI 总线，但功能等效，能承载 U-Boot/UEFI）。
> * `virt` 原生不带 SPI 控制器；若一定要在内核里以 spi-nor 驱动方式访问，需要给 `virt` 外挂 SPI 控制器（复杂）或改用带 SPI 控制器的其他 SoC 机型。绝大多数开发场景，pflash 足够。

---

# 一、构建 U-Boot（推荐）

```bash
git clone https://source.denx.de/u-boot/u-boot.git
cd u-boot
make CROSS_COMPILE=aarch64-linux-gnu- qemu_arm64_defconfig

# 开 NVMe + distro boot（若默认没开）
# make menuconfig:
#   -> Device Drivers -> NVMe support (y)
#   -> Command line interface -> NVMe command (y)
#   -> Boot options -> "Use distro boot" (y)

make -j$(nproc) CROSS_COMPILE=aarch64-linux-gnu-
# 生成 u-boot.bin
```

---

# 二、构建 Linux 内核

```bash
git clone https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
cd linux
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- defconfig
make ARCH=arm64 menuconfig
# 勾选/确认：
#   PCIe host (generic)、NVMe、PL011 串口、virtio-net、EXT4、initramfs（若走A路线）
make -j$(nproc) ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- Image dtbs
# 产物：arch/arm64/boot/Image
# （可选）virt DTB：arch/arm64/boot/dts/arm/virt.dtb
```

---

# 三、制作 128 GB NVMe 镜像并准备根文件系统

```bash
qemu-img create -f qcow2 nvme-128g.qcow2 128G

# 用 nbd 方式分区/格式化
sudo modprobe nbd
sudo qemu-nbd -c /dev/nbd0 nvme-128g.qcow2
sudo parted -s /dev/nbd0 mklabel gpt
sudo parted -s /dev/nbd0 mkpart boot ext4 1MiB 512MiB
sudo parted -s /dev/nbd0 mkpart root ext4 512MiB 100%
sudo mkfs.ext4 /dev/nbd0p1
sudo mkfs.ext4 /dev/nbd0p2
sudo mount /dev/nbd0p2 /mnt/root
sudo mkdir -p /mnt/root/boot
sudo mount /dev/nbd0p1 /mnt/root/boot
```

* **A. 先用 initramfs 验证启动**（最快起一个 shell）

    * 把 `rootfs.cpio.gz` 放到宿主机某路径，启动 QEMU 时用 `-initrd` 指定即可。
    * 内核参数指向 initramfs（无需 root=/dev/...）。

* **B. 用 NVMe 作为根**（更接近实物板）
  准备一个最小根文件系统（busybox/自制 rootfs 或 debootstrap/自建发行版根），把它拷进 `/mnt/root`。然后把内核与（可选的）DTB 放到 `/mnt/root/boot`：

  ```bash
  sudo cp /path/to/linux/arch/arm64/boot/Image /mnt/root/boot/
  sudo mkdir -p /mnt/root/boot/extlinux
  sudo tee /mnt/root/boot/extlinux/extlinux.conf >/dev/null <<'EOF'
  DEFAULT linux
  TIMEOUT 1
  LABEL linux
    KERNEL /boot/Image
    # FDT /boot/virt.dtb   # 通常可省略，QEMU 会传 DTB
    APPEND root=/dev/nvme0n1p2 rw console=ttyAMA0 earlycon=pl011,0x09000000
  EOF
  ```

  完成后卸载：

  ```bash
  sync
  sudo umount /mnt/root/boot /mnt/root
  sudo qemu-nbd -d /dev/nbd0
  ```

---

# 四、启动方式与 QEMU 命令行

## 方式 1：通过 U-Boot（distro boot，从 NVMe 启动）

```bash
qemu-system-aarch64 \
  -machine virt,virtualization=on,gic-version=3,highmem=on \
  -cpu cortex-a72 -smp 4 -m 16G \
  -nographic \
  -bios /path/to/u-boot.bin \
  -device virtio-net-pci,netdev=n0 \
  -netdev user,id=n0,hostfwd=tcp::2222-:22 \
  -drive if=none,id=nvme0,file=nvme-128g.qcow2,format=qcow2 \
  -device nvme,drive=nvme0,serial=nvme-1
```

* 串口：`-nographic` 将 **RS-232 控制台**绑到当前终端（`ttyAMA0`）。
* 网卡：`virtio-net-pci`；上面用了 user-mode 网络并转发宿主 `2222->guest:22`，方便 SSH。
* NVMe：以 PCIe 设备形式挂在 `virt` 的 RC 下（QEMU 不模拟 x8 车道/速率细节，但功能上等效）。
* U-Boot 会自动扫描 NVMe 并解析 `/boot/extlinux/extlinux.conf` 启动内核。

> 如需把固件放进“NOR”，可用 pflash（等效 NOR 存储）：
>
> ```bash
> # 准备两个 128MiB 的 pflash 文件（读写分离更稳）
> dd if=/dev/zero of=flash0.bin bs=1M count=128
> dd if=/dev/zero of=flash1.bin bs=1M count=128
> # 将 u-boot.bin 写入 flash0.bin 开头（按需要的偏移/布局处理）
> dd if=u-boot.bin of=flash0.bin conv=notrunc
>
> qemu-system-aarch64 \
>   -machine virt,gic-version=3 \
>   -cpu cortex-a72 -smp 4 -m 16G -nographic \
>   -drive if=pflash,format=raw,file=flash0.bin,unit=0 \
>   -drive if=pflash,format=raw,file=flash1.bin,unit=1 \
>   ...（网卡/NVMe 同上）
> ```
>
> 说明：这是 **并行 NOR（pflash）**，在 `virt` 上最容易用来承载固件；并非 SPI 总线，但功能上满足“启动固件存储”的需求。

## 方式 2：直接用内核（跳过 U-Boot）

```bash
qemu-system-aarch64 \
  -machine virt,virtualization=on,gic-version=3,highmem=on \
  -cpu cortex-a72 -smp 4 -m 16G \
  -nographic \
  -kernel /path/to/arch/arm64/boot/Image \
  -append "console=ttyAMA0 root=/dev/nvme0n1p2 rw earlycon=pl011,0x09000000" \
  -device virtio-net-pci,netdev=n0 \
  -netdev user,id=n0,hostfwd=tcp::2222-:22 \
  -drive if=none,id=nvme0,file=nvme-128g.qcow2,format=qcow2 \
  -device nvme,drive=nvme0,serial=nvme-1
  # 若走 initramfs 路线，再加：
  # -initrd /path/to/rootfs.cpio.gz
  # （可选）-dtb /path/to/arch/arm64/boot/dts/arm/virt.dtb
```

---

# 关于每个外设与“贴近度”的说明

* **CPU**：`-cpu cortex-a72`/`max` 都是 ARMv8-A，能覆盖指令集与异常级；不是 D2000 的定制微架构，但对内核/驱动开发足够。
* **内存 16 GB**：`-m 16G` 即可（QEMU 支持高内存，`highmem=on` 更稳）。
* **PCIe 3.0 x8（RC 模式）**：`virt` 提供 PCIe Root Complex；NVMe 作为端点挂上即可。车道数/速率在 QEMU 中不做精细仿真，不影响功能测试与驱动堆栈验证。
* **RS-232 串口**：`virt` 内置 PL011（`ttyAMA0`），`-nographic`/`-serial` 即可把控制台映射到宿主终端或 PTY。
* **千兆以太网**：`virtio-net-pci` 性能更高且简单；如一定要“看到 1000M 速率”可在来宾系统里用 ethtool/网卡驱动参数限制（功能上不影响）。
* **128 MB SPI-NOR**：

    * 最简单：用 **pflash** 承载固件（上文示例）。
    * 若必须 SPI-NOR 语义（M25P80/W25Q…）：需要在 `virt` 上加 SPI 控制器并在 DTS/内核中建联，步骤较长且对 `virt` 不是开箱即用。多数开发者在 `virt` 上用 pflash 代替。

---

# 常见坑与检查清单

* **串口名**：控制台务必用 `console=ttyAMA0`（PL011）。
* **NVMe 根分区名**：`root=/dev/nvme0n1p2`（按你的实际分区号改）。
* **U-Boot 没找到 NVMe**：确认 U-Boot 里 `CONFIG_NVME*`、`CONFIG_BLK`、`CONFIG_PARTITIONS`、`CONFIG_DISTRO_DEFAULTS` 已开启；U-Boot 命令行里可 `nvme scan`/`ls nvme 0:1` 排查。
* **网络**：先用 user-mode 网络最省事；需要和宿主同网段再换 TAP/bridge（`-netdev tap,...` + `-device virtio-net-pci,netdev=...`）。
* **DTB**：`virt` 机型 QEMU 会自动传 DTB 给固件/内核；通常无需 `-dtb`。

---

如果你希望我按你的实际源码树（U-Boot/Kconfig、内核 .config、rootfs 布局）定制一份“一键启动脚本”和最小 BusyBox 根文件系统清单，我可以直接给出完整脚本与目录结构。你现在手头已有哪几样（u-boot、内核、rootfs）？我就按你的现状组织最短路径的启动方案。
