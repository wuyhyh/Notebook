# ARM64 initramfs 配置流程

利用 U-Boot 的网络功能和 tftp 协议传输 Image dtb initramfs 到内存中，从内存启动一个轻量级 Linux 系统，完成 nvme
ssd的分区创建并建立文件系统，然后固话操作系统到 nvme ssd 中。

---

## 0. 目标与约束

**目标：**

* U-Boot 通过 TFTP 下载：`Image + dtb + initramfs.cpio`，启动后进入 bash
* initramfs 里具备：`lsblk blkid fdisk mkfs tree file scp wget curl tar unzip` 等工具
* 网络固定静态：

    * `eth0 = 192.168.11.101/24`（默认路由走 eth0）
    * `eth1 = 192.168.11.102/24`
    * gateway：`192.168.11.1`（按你实际网关调整）
    * DNS：`223.5.5.5, 114.114.114.114`
* 后续用于把完整 OS 写入 `nvme0n1p1` `nvme0n1p2` `nvme0n1p3` 等分区

---

## 1. 在构建机上准备 initramfs 根目录

假设你在 openEuler server（aarch64）上构建：

```bash
export IR=/root/initramfs-aarch64
rm -rf "$IR"
mkdir -p "$IR"
```

---

## 2. 用 dnf 把“可用工具集”装进 installroot

这是关键：用 `--installroot` 构建一个完整的最小用户态，自动带齐 so 依赖。

```bash
dnf -y --installroot="$IR" --releasever=/ \
  --setopt=install_weak_deps=False \
  --setopt=tsflags=nodocs \
  install \
  bash coreutils findutils grep gawk sed \
  util-linux e2fsprogs dosfstools \
  iproute iputils \
  openssh-clients \
  wget curl ca-certificates \
  tar gzip bzip2 xz unzip \
  file tree \
  procps-ng which less
```

命令覆盖关系：

* `lsblk blkid fdisk` → `util-linux`
* `mkfs.ext4` → `e2fsprogs`
* `mkfs.vfat` → `dosfstools`
* `scp` → `openssh-clients`
* `wget/curl` → `wget/curl + ca-certificates`
* `tar/unzip/file/tree` → 对应包

---

## 3. 补齐 initramfs 必备目录结构

```bash
mkdir -p "$IR"/{dev,proc,sys,run,tmp,mnt,root,etc,var,usr,bin,sbin,lib,lib64}
```

---

## 4. 写入可靠的 /init（静态 IP + 必要挂载 + 进 bash）

把 `$IR/init` 写成下面这样：

```bash
cat >"$IR/init" <<'EOF'
#!/bin/bash
set -e
export PATH=/usr/sbin:/usr/bin:/sbin:/bin

exec </dev/console >/dev/console 2>&1
echo "[initramfs] /init start"

# basic mounts
mount -t proc  proc  /proc
mount -t sysfs sysfs /sys
mount -t devtmpfs devtmpfs /dev || true
mkdir -p /run /tmp /mnt /etc

# bring up loopback + nics
ip link set lo up || true
ip link set eth0 up || true
ip link set eth1 up || true

# static IPs
ip addr flush dev eth0 || true
ip addr flush dev eth1 || true
ip addr add 192.168.11.101/24 dev eth0
ip addr add 192.168.11.102/24 dev eth1

# default route via eth0 (adjust gateway if needed)
ip route replace default via 192.168.11.1 dev eth0

# DNS
cat >/etc/resolv.conf <<EOF2
nameserver 223.5.5.5
nameserver 114.114.114.114
EOF2

echo "[initramfs] net status:"
ip -br a || true
ip route || true

echo "[initramfs] ready. drop to shell"
exec /bin/bash
EOF

chmod +x "$IR/init"
```

---

## 5. 做“安全瘦身”（只删不会影响运行的）

这里按保守方案，只删文档和缓存：

```bash
rm -rf "$IR/usr/share/man" "$IR/usr/share/doc" "$IR/usr/share/info"
rm -rf "$IR/var/cache/dnf" "$IR/var/cache/yum" "$IR/var/lib/dnf" "$IR/var/lib/rpm"
rm -rf "$IR/var/log"/*
mkdir -p "$IR/var/lib" "$IR/var/cache" "$IR/var/log"
```

可选：strip（通常安全，但你可以先不做）

```bash
find "$IR" -type f \( -perm -111 -o -name "*.so*" \) -exec strip --strip-unneeded {} + 2>/dev/null || true
```

---

## 6. 打包成未压缩 initramfs.cpio

**强烈建议你用未压缩版**，因为你验证它每次都能启动。

```bash
cd "$IR"
LC_ALL=C find . -mindepth 1 -print0 | sort -z | cpio --null -ov --format=newc > /root/initramfs.cpio
ls -lh /root/initramfs.cpio
```

---

## 7. 本地自检

### 7.1 确认 magic 和 /init 存在

```bash
head -c 6 /root/initramfs.cpio; echo
# 期望开头是 070701（newc）

cpio -it < /root/initramfs.cpio | grep -x init
```

### 7.2 确认你的工具都在

```bash
mkdir -p /tmp/irchk && cd /tmp/irchk
cpio -id < /root/initramfs.cpio >/dev/null 2>&1
for x in lsblk blkid fdisk mkfs.ext4 tree file scp wget curl tar unzip ip; do
  echo -n "$x: "; command -v "./usr/bin/$x" "./usr/sbin/$x" "./bin/$x" "./sbin/$x" 2>/dev/null | head -n1 || echo "MISSING"
done
```
