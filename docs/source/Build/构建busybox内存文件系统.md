# 构建busybox内存文件系统

```text
sudo dnf install -y git gcc gcc-c++ make ncurses-devel bc bison flex cpio gzip file wget tar xz
sudo dnf install -y gcc-aarch64-linux-gnu binutils-aarch64-linux-gnu

```

```text
export ARCH=arm64
export CROSS_COMPILE=aarch64-linux-gnu-
mkdir -p $HOME/work/initramfs
cd $HOME/work/initramfs
```

```text
git clone https://git.busybox.net/busybox
cd busybox
make defconfig
make menuconfig
```

```text
sudo dnf install -y aarch64-linux-gnu-gcc glibc-aarch64-linux-gnu glibc-aarch64-linux-gnu-devel
sudo dnf install sysroot-aarch64-fc42-glibc
```

```text
export SYSROOT=/usr/aarch64-redhat-linux/sys-root/fc42
make -j"$(nproc)"  CFLAGS="--sysroot=$SYSROOT"  LDFLAGS="--sysroot=$SYSROOT"
```

```text
cd /tmp/
wget https://cdn.kernel.org/pub/linux/kernel/v5.x/linux-5.10.tar.xz
tar -xf linux-5.10.tar.xz
cd linux-5.10/
make ARCH=arm64 headers_install INSTALL_HDR_PATH=/tmp/aarch64-kheaders
```

```text
sudo rsync -av /tmp/aarch64-kheaders/include/   /usr/aarch64-redhat-linux/sys-root/fc42/usr/include/
cd ~/work/initramfs/busybox
make distclean
export ARCH=arm64
export CROSS_COMPILE=aarch64-linux-gnu-
export SYSROOT=/usr/aarch64-redhat-linux/sys-root/fc42
make defconfig
make menuconfig
make -j"$(nproc)" CFLAGS="--sysroot=$SYSROOT" LDFLAGS="--sysroot=$SYSROOT"
```

```text
cd ~/work/initramfs/busybox
# 安装到上一层的 rootfs/
mkdir -p ../rootfs
make CONFIG_PREFIX=../rootfs install
cd rootfs/
```




