# 创建 initramfs

用 Buildroot 产出一个“极简但功能足够”的 initramfs

## 1. 环境与目录

在 Fedora 42 上:

```text
sudo dnf install -y git rsync cpio gzip xz lz4 zstd file \
  gcc-aarch64-linux-gnu binutils-aarch64-linux-gnu \
  ncurses-devel bc bison flex openssl-devel elfutils-libelf-devel dwarves \
  perl-IPC-Cmd perl-FindBin perl-File-Compare perl-File-Copy \
  dtc patch
```

下载代码压缩包到 `~`

[20250207 LTS](https://buildroot.org/download.html) 版本

创建目录

```text
mkdir -p ~/arm64-ramdisk/{src,overlay,output}
cd ~/arm64-ramdisk/src
cp ~/buildroot-2025.02.7.tar.xz ./;tar -xf buildroot-2025.02.7.tar.xz
```

---

## 2. 编译配置

### 2.1 进入 Buildroot 并创建基础配置

```bash
cd ~/arm64-ramdisk/src/buildroot
make qemu_aarch64_virt_defconfig
make menuconfig
```

在 `menuconfig` 里勾选/修改：

* Target options

    * `Target Architecture` → **AArch64 (little endian)**
    * `Target ABI` → **lp64**

* Toolchain

    * `Toolchain type` → **Buildroot toolchain**
    * `C library` → **musl**（更小也够用；如你坚持 glibc 也行）
    * `[*] Enable static`（**静态链接**，最适合独立 initramfs）

* System configuration

    * `Init system` → **none/BusyBox init**（默认）
    * `Root filesystem overlay` → **填你的 overlay 目录**（例如：`/home/你/arm64-ramdisk/overlay`）

* Package selection

    * BusyBox（默认启用；等会儿单独进 busybox-menuconfig 开 applets）
    * util-linux：勾选子项

        * `sfdisk`、`blkid`、`lsblk`、`partprobe`
    * e2fsprogs：勾选子项

        * `mke2fs`、`e2fsck`、`resize2fs`
    * （可选）`iproute2`（不装也行，busybox 自带 ifconfig/route 足够）

* Filesystem images

    * `[ * ] cpio the root filesystem (for use as an initramfs)`
    * `Compression method` → **gzip**

保存退出。

### 2.2 打开 BusyBox 所需 applets

```bash
make busybox-menuconfig
```

勾选（若默认未开）：

* Networking Utilities：`tftp`、`wget`（建议都开）、`udhcpc`、`ifconfig`、`route`、`ping`
* Coreutils/Archival：`tar`、`gzip`、`sha256sum`

保存退出。

---

## 3. Overlay 放一个自启动的 `/init`

把下面脚本保存为 `~/arm64-ramdisk/overlay/init` 并赋权；Buildroot 会自动把它打进 `rootfs.cpio.gz`。

```text
vim ~/arm64-ramdisk/overlay/init
```

```sh
#!/bin/sh
set -eux

mount -t proc none /proc
mount -t sysfs none /sys
mount -t devtmpfs none /dev || true
mkdir -p /run /tmp
```

赋权：

```bash
chmod +x ~/arm64-ramdisk/overlay/init
```

---

## 4. 编译并收取产物

在根目录创建交叉编译的环境脚本

```text
echo 'unset ARCH CROSS_COMPILE' >> set-arm64.sh
echo 'export ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu-' >> set-arm64.sh
```

```bash
sh ~/set-arm64.sh;cd ~/arm64-ramdisk/src/buildroot
make -j$(nproc)
```

产物：

```text
ls -lh ~/arm64-ramdisk/src/buildroot/output/images/*
```

```text
cp output/images/rootfs.cpio.gz ~/arm64-ramdisk/output/
cp output/images/Image ~/arm64-ramdisk/output/
```

至此，你的 **initramfs** 就准备好了。

---

## 5. U-Boot 启动（外部 cpio.gz）

假设你已经有一份“能稳定起”的内核 `Image` 与配套 `pd2008.dtb`

```bash
# 建议的安全地址（按你的板子内存可适当调整，三者别重叠）
setenv kernel_addr_r    0x80200000
setenv fdt_addr_r       0x8F000000
setenv ramdisk_addr_r   0x90000000
setenv fdt_high         0xffffffffffffffff
setenv initrd_high      0xffffffffffffffff
```

```
tftpboot $kernel_addr_r Image;tftpboot $fdt_addr_r pd2008.dtb;tftpboot $ramdisk_addr_r rootfs.cpio.gz;
```

```text
setenv bootargs 'console=ttyAMA1,115200 earlycon=pl011,0x28001000 rdinit=/sbin/init'
setexpr rdsize $filesize          # 注意：必须在加载 cpio.gz 之后
booti $kernel_addr_r $ramdisk_addr_r:$rdsize $fdt_addr_r
```

---

## 6. 服务器文件摆放建议

TFTP/HTTP 根目录放：

```
Image
pd2008.dtb
rootfs.cpio.gz
```
