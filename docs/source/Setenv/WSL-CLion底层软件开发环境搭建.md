# WSL CLion 底层软件开发环境搭建

## 约定与快速起步

* 平台：Windows 11 + WSL2（Ubuntu 24.04）
* 目标：在 WSL 内完成 U‑Boot、Linux 内核的交叉编译与 QEMU 启动/调试。
* 目录建议：将源码与构建目录放在 WSL 的 ext4 文件系统（`/home/$USER/...`），避免在 `/mnt/c` 下构建（性能差、权限坑多）。
* 默认 shell：bash。

```text
$WORK      # 你的工作根目录，例如  ~/work
$KSRC      # Linux 内核源码目录，例如  $WORK/linux
$UBOOT     # U‑Boot 源码目录，例如      $WORK/u-boot
```

---

## 1. 安装 WSL（Windows 11）

### 1.1 一条命令安装（含 Ubuntu 与 WSL2）

在 **管理员权限的 PowerShell** 中执行：

```powershell
wsl --install -d Ubuntu
```

首次启动 Ubuntu 会提示创建用户名/密码。之后在 Windows 终端中用 `wsl` 或在开始菜单启动 “Ubuntu”。

### 1.2 常用 WSL 管理命令

```powershell
wsl --list --online              # 可用发行版
wsl --list --verbose             # 已安装发行版/版本
wsl --update                     # 更新 WSL 内核
wsl --shutdown                   # 关闭全部 WSL 实例
```

### 1.3 性能/资源建议（可选）

在 `%UserProfile%/.wslconfig` 写入（调整为你机器所需）：

```ini
[wsl2]
memory = 8GB        # 限制内存
processors = 8      # 限制 vCPU 数
localhostForwarding = true
```

写入后 `wsl --shutdown` 再重启 WSL 生效。

---

## 2. 安装基础开发工具

进入 WSL Ubuntu：

切换镜像源

```text
sudo sed -i 's@/archive.ubuntu.com/@/mirrors.ustc.edu.cn/@g' /etc/apt/sources.list  # 可选：切换镜像
```

安装开发工具

```bash
sudo apt update
sudo apt -y install \
  build-essential git cmake ninja-build pkg-config \
  bc flex bison libelf-dev libssl-dev dwarves \
  ccache gperf libncurses-dev rsync cpio \
  device-tree-compiler python3 python3-pip \
  unzip curl wget file ripgrep jq tree
```

Git 基本设置

```text 
git config --global user.name  "Your Name"
git config --global user.email "you@example.com"
```

> 说明：`libelf-dev`、`libssl-dev`、`bc`、`flex`、`bison`、`dwarves` 是内核常见依赖；`device-tree-compiler` 用于编译 DTB；
`ccache` 可显著加速二次构建。

---

## 3. 安装 ARM 交叉编译工具

### 3.1 常用交叉工具链（基于 apt）

```bash
sudo apt -y install \
  gcc-aarch64-linux-gnu g++-aarch64-linux-gnu \
  binutils-aarch64-linux-gnu \
  gcc-arm-none-eabi binutils-arm-none-eabi \
  gdb-multiarch

# 验证
aarch64-linux-gnu-gcc --version
arm-none-eabi-gcc --version
```

* **aarch64-linux-gnu-**\*：面向 AArch64 Linux 用户态/内核（glibc）环境（用于编译内核、U‑Boot 运行于 Linux 平台）
* **arm-none-eabi-**\*：面向 ARM 裸机/RTOS 环境（无操作系统，常用于 MCU/早期引导）

> 变量约定：
>
> * `ARCH=arm64`（AArch64 架构）
> * `CROSS_COMPILE=aarch64-linux-gnu-`

### 3.2 可选：Clang/LLVM 交叉（了解即可）

```bash
sudo apt -y install clang lld llvm
# 内核可用：make LLVM=1 LLVM_IAS=1 ARCH=arm64 ...
```

---

## 4. 安装 QEMU（AArch64/ARM 平台）

```bash
sudo apt -y install qemu-system-arm qemu-system-misc qemu-utils

# 快速自检（不加载镜像，仅看是否能启动到 QEMU 控制台）
qemu-system-aarch64 \
  -machine virt -cpu cortex-a72 -m 1024 \
  -nographic -monitor none -serial mon:stdio -S -s & sleep 1; kill %1
```

> `-machine virt` 是 QEMU 提供的通用 ARMv8 虚拟平台；串口为 `ttyAMA0`。

---

## 5. U‑Boot：获取、编译与在 QEMU 上运行

### 5.1 获取源码

```bash
mkdir -p "$WORK" && cd "$WORK"
git clone https://source.denx.de/u-boot/u-boot.git
cd u-boot
```

### 5.2 针对 QEMU ARM64 的最小构建

```bash
export ARCH=arm64
export CROSS_COMPILE=aarch64-linux-gnu-

make qemu_arm64_defconfig
make -j$(nproc)
```

产物：`u-boot.bin`、`u-boot`（ELF）。

### 5.3 在 QEMU 启动 U‑Boot（作为固件）

```bash
qemu-system-aarch64 \
  -machine virt -cpu cortex-a72 -m 1024 \
  -nographic -serial mon:stdio \
  -bios u-boot.bin
```

看到 U‑Boot 提示符即可。

> 若你将来要面向实体板卡（如 Phytium/D2000），需使用对应的 defconfig 与设备树，并准备合适的打包/启动介质（FIP、SPI
> NOR、eMMC、NVMe 等）。上面仅为 QEMU 通用流程。

---

## 6. Linux 内核：获取、配置与编译（ARM64）

### 6.1 获取内核源码

```bash
mkdir -p "$WORK" && cd "$WORK"
git clone https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
cd linux
```

### 6.2 最小可用配置（面向 QEMU virt 平台）

```bash
export ARCH=arm64
export CROSS_COMPILE=aarch64-linux-gnu-

make defconfig
# 可选：若需要内核自带 initramfs，可开启：
#   General setup → Initial RAM filesystem and RAM disk (initramfs/initrd) support
#   也可用外部 BusyBox rootfs（见 §7）

make -j$(nproc) \
  Image vmlinux modules
```

产物：

* `arch/arm64/boot/Image`（内核镜像）
* `vmlinux`（带符号，供 gdb 调试）
* `modules`（可选）

> 若需要特定驱动（例如 PL011 串口、virtio、NVMe），可执行 `make menuconfig` 勾选：
>
> * `CONFIG_SERIAL_AMBA_PL011=y`
> * `CONFIG_VIRTIO_PCI=y`、`CONFIG_VIRTIO_MMIO=y`
> * `CONFIG_BLK_DEV_NVME=y`

---

## 7. 准备最小 initramfs（BusyBox）并在 QEMU 启动

### 7.1 构建 BusyBox 静态根文件系统

```bash
cd "$WORK"
wget https://busybox.net/downloads/busybox-1.36.1.tar.bz2
 tar xf busybox-1.36.1.tar.bz2 && cd busybox-1.36.1
make defconfig
# 打开静态链接：
sed -i 's/^# CONFIG_STATIC is not set/CONFIG_STATIC=y/' .config
make -j$(nproc)
make CONFIG_PREFIX=$PWD/_rootfs install

# 基础目录与 init
cd _rootfs
mkdir -p proc sys dev etc mnt tmp root
cat > init <<'EOF'
#!/bin/sh
mount -t proc none /proc
mount -t sysfs none /sys
mount -t devtmpfs none /dev || mdev -s
exec /bin/sh
EOF
chmod +x init

# 打包 cpio.gz
find . -print0 | cpio --null -ov --format=newc | gzip -9 > ../rootfs.cpio.gz
```

### 7.2 在 QEMU 启动内核 + initramfs

```bash
cd "$KSRC"   # 你的内核目录
qemu-system-aarch64 \
  -machine virt -cpu cortex-a72 -m 1024 \
  -nographic -serial mon:stdio \
  -kernel arch/arm64/boot/Image \
  -initrd "$WORK"/busybox-1.36.1/rootfs.cpio.gz \
  -append "console=ttyAMA0 earlycon=pl011,0x9000000 rdinit=/init"
```

进入 BusyBox shell 即表示启动成功。

> 若你要挂载虚拟磁盘（ext4、NVMe、virtio-blk）：
>
> ```bash
> qemu-img create -f qcow2 $WORK/disk.qcow2 4G
> mkfs.ext4 $WORK/disk.qcow2   # 或用 loop 格式化后再作为 -drive 使用
> qemu-system-aarch64 \
>   -machine virt -cpu cortex-a72 -m 1024 -nographic -serial mon:stdio \
>   -kernel arch/arm64/boot/Image -initrd $WORK/busybox-1.36.1/rootfs.cpio.gz \
>   -append "console=ttyAMA0 rdinit=/init" \
>   -drive if=none,file=$WORK/disk.qcow2,format=qcow2,id=d0 \
>   -device virtio-blk-pci,drive=d0
> ```

---

## 8. 调试内核（QEMU + GDB）

### 8.1 以 GDB 可附加的方式启动 QEMU

```bash
qemu-system-aarch64 \
  -machine virt -cpu cortex-a72 -m 1024 \
  -nographic -serial mon:stdio \
  -kernel arch/arm64/boot/Image \
  -initrd "$WORK"/busybox-1.36.1/rootfs.cpio.gz \
  -append "console=ttyAMA0 rdinit=/init" \
  -s -S
```

* `-S`：上电即暂停 CPU
* `-s`：等价于 `-gdb tcp::1234`

### 8.2 使用 gdb 连接并下断点

```bash
# 在另一个终端
cd "$KSRC"
AARCH64_GDB=$(command -v aarch64-linux-gnu-gdb || echo gdb-multiarch)
"$AARCH64_GDB" vmlinux -ex 'target remote :1234' -ex 'hbreak start_kernel' -ex c
```

常用操作：

```gdb
bt                 # 查看调用栈
info registers     # 寄存器
x/16i $pc          # 反汇编
b do_fork          # 下断点
c                  # 继续运行
```

> 若需调试模块：加载模块后使用 `add-symbol-file` 指定模块符号基址。

---

## 9. 常见坑与经验

1. **避免在 `/mnt/c` 构建**：WSL 与 Windows 文件系统的差异会导致权限、符号链接与 I/O 性能问题。在 `/home/$USER` 下构建更快更稳。
2. **ccache**：在 `make` 前导出 `CC='ccache aarch64-linux-gnu-gcc'` 可显著加速重复构建。
3. **内核配置缺失**：QEMU `virt` 平台至少确保 `PL011` 串口与 `virtio` 基础驱动开启，否则看不到串口输出或无法挂盘。
4. **GDB 符号**：务必用 `vmlinux`（ELF 带符号）而非 `Image` 进行调试。
5. **WSL 资源不足**：大编译时可提升 `.wslconfig` 的 `memory` 与 `processors`；或在构建前 `make -j$(nproc)` 适度降低并发。
6. **时间/地区**：`sudo dpkg-reconfigure tzdata` 设置时区；`hwclock` 在 WSL 上不可用属正常。
7. **代理/镜像**：国内建议配置 APT/Git 代理与镜像源以提高下载速度。

---

## 10. 附：U‑Boot 与内核常用构建命令速查

```bash
# U‑Boot（QEMU ARM64）
export ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu-
make qemu_arm64_defconfig
make -j$(nproc)
qemu-system-aarch64 -machine virt -cpu cortex-a72 -m 1024 -nographic -serial mon:stdio -bios u-boot.bin

# Linux 内核（ARM64 + QEMU virt）
export ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu-
make defconfig
make -j$(nproc) Image vmlinux modules

# BusyBox 静态 rootfs（最小化）
make defconfig && sed -i 's/^# CONFIG_STATIC is not set/CONFIG_STATIC=y/' .config
make -j$(nproc) && make CONFIG_PREFIX=$PWD/_rootfs install
cd _rootfs && mkdir -p proc sys dev && echo '#!/bin/sh\nmount -t proc none /proc\nmount -t sysfs none /sys\nmount -t devtmpfs none /dev || mdev -s\nexec /bin/sh' > init && chmod +x init
find . -print0 | cpio --null -ov --format=newc | gzip -9 > ../rootfs.cpio.gz

# QEMU 启动（带 GDB 调试）
qemu-system-aarch64 -machine virt -cpu cortex-a72 -m 1024 -nographic -serial mon:stdio \
  -kernel arch/arm64/boot/Image -initrd $WORK/busybox-1.36.1/rootfs.cpio.gz \
  -append 'console=ttyAMA0 rdinit=/init' -s -S

# GDB 连接
(aarch64-linux-gnu-gdb|gdb-multiarch) vmlinux
(gdb) target remote :1234
(gdb) hbreak start_kernel
(gdb) c
```

---

## 11. 进一步延伸（可按需添加）

* 将 `initramfs` 集成进内核（`CONFIG_INITRAMFS_SOURCE`）。
* 使用 `virtio-net` + `-net user,hostfwd=tcp::2222-:22` 做 SSH 进 initramfs 环境。
* 在 QEMU 中添加 NVMe/PCIe 设备，构造更贴近真实板卡的拓扑。
* 使用 `kgdboc=ttyAMA0,115200` 进行串口 KGDB；结合 `earlycon` 排查早期启动问题。
* 使用 `ftrace`、`perf`、`bpf` 做性能/路径分析。

> 将来面向真实硬件（如 D2000/Phytium）时，需切换为相应的 defconfig/设备树/打包链（FIP/TF‑A/U‑Boot/内核/根文件系统），并对接真实外设驱动与
> Boot 流程。上述文档提供的是在 PC 上快速闭环验证的最小可行链路。


