#!/usr/bin/env bash
set -euo pipefail

# -----------------------------
# 0) 用户可改的默认变量
# -----------------------------
: "${SRCDIR:=$HOME/src/openeuler-5.10.0-136-src-master}"
: "${BUILDDIR:=$HOME/build/oe-kernel-5.10.0-136}"
: "${STGDIR:=$HOME/staging}"
: "${ROOTFS:=/mnt/rootfs}"
: "${IMG:=$STGDIR/rootfs.ext4}"
: "${IMG_SIZE:=8G}"

: "${KCONF:=$HOME/config-5.10.0-136.12.0.86.aarch64}"

# 可选：版本后缀（不设置就用源码默认）
: "${LOCALVERSION:=}"

# 关键：默认只拷你这块板子的 dtb
# 它是相对 arch/arm64/boot/dts/ 的路径
: "${DTB_REL:=phytium/pd2008-devboard-dsk.dtb}"

# 可选：配置修改入口
# 1) MENUCONFIG=1 交互修改
: "${MENUCONFIG:=0}"
# 2) KCONFIG_FRAGMENTS=frag1:frag2 以冒号分隔的 fragment 列表（可复现）
: "${KCONFIG_FRAGMENTS:=}"

PKGS=(
  basesystem
  systemd
  passwd
  shadow-utils
  util-linux

  # 基础调试
  vim-minimal
  less
  procps-ng
  iproute
  iputils

  # 网络
  NetworkManager
  openssh-server
  openssh-clients
  curl

  # RPM / DNF 栈（关键）
  dnf
  python3
  python3-libs
  python3-dnf
  libdnf
  librepo
  rpm
  rpm-libs

  # 安全 / 证书
  ca-certificates
  gnupg2
)

# -----------------------------
# 1) 小工具函数
# -----------------------------
die() { echo "ERROR: $*" >&2; exit 1; }
need_cmd() { command -v "$1" >/dev/null 2>&1 || die "missing command: $1"; }
log() { echo "[+] $*"; }

# -----------------------------
# 2) 前置检查
# -----------------------------
need_cmd make
need_cmd rsync
need_cmd mkfs.ext4
need_cmd e2fsck
need_cmd dnf
need_cmd depmod
need_cmd truncate
need_cmd install

[[ -d "$SRCDIR" ]] || die "SRCDIR not found: $SRCDIR"
[[ -f "$KCONF"  ]] || die "KCONF not found: $KCONF"

mkdir -p "$BUILDDIR" "$STGDIR"

# -----------------------------
# 3) 准备内核配置（只在 BUILDDIR）
# -----------------------------
log "prepare kernel config in BUILDDIR"
cp -f "$KCONF" "$BUILDDIR/.config"

if [[ -n "$LOCALVERSION" ]]; then
  export LOCALVERSION
  log "LOCALVERSION=$LOCALVERSION"
fi

log "olddefconfig (base)"
make -C "$SRCDIR" O="$BUILDDIR" ARCH=arm64 olddefconfig

# 3.1 可选：合并 fragments（可复现）
if [[ -n "$KCONFIG_FRAGMENTS" ]]; then
  log "merge kconfig fragments: $KCONFIG_FRAGMENTS"
  # merge_config.sh 需要在源码树里
  MERGE_SH="$SRCDIR/scripts/kconfig/merge_config.sh"
  [[ -x "$MERGE_SH" ]] || die "merge_config.sh not found/executable: $MERGE_SH"

  IFS=':' read -r -a frags <<< "$KCONFIG_FRAGMENTS"
  for f in "${frags[@]}"; do
    [[ -f "$f" ]] || die "fragment not found: $f"
  done

  # 先确保 .config 在 BUILDDIR
  # -O 指向输出目录，合并结果会写到该目录的 .config
  "$MERGE_SH" -m -O "$BUILDDIR" "$BUILDDIR/.config" "${frags[@]}"
  make -C "$SRCDIR" O="$BUILDDIR" ARCH=arm64 olddefconfig
fi

# 3.2 可选：交互式 menuconfig
if [[ "$MENUCONFIG" == "1" ]]; then
  log "run menuconfig (interactive)"
  make -C "$SRCDIR" O="$BUILDDIR" ARCH=arm64 menuconfig
  make -C "$SRCDIR" O="$BUILDDIR" ARCH=arm64 olddefconfig
fi

# 取干净的 KREL（关键：-s）
KREL="$(make -s -C "$SRCDIR" O="$BUILDDIR" ARCH=arm64 kernelrelease)"
log "KREL=$KREL"

# -----------------------------
# 4) 编译 Image/modules/dtbs
# -----------------------------
log "build Image/modules/dtbs"
time make -C "$SRCDIR" O="$BUILDDIR" ARCH=arm64 -j"$(nproc)" Image modules dtbs

VMLINUX="$BUILDDIR/arch/arm64/boot/Image"
DTB_SRC="$BUILDDIR/arch/arm64/boot/dts/$DTB_REL"

[[ -f "$VMLINUX" ]] || die "Image not found: $VMLINUX"
[[ -f "$DTB_SRC" ]] || die "dtb not found: $DTB_SRC (DTB_REL=$DTB_REL)"

# -----------------------------
# 5) 构建 rootfs（dnf --installroot）
# -----------------------------
log "build rootfs into $ROOTFS"
sudo rm -rf "$ROOTFS"
sudo mkdir -p "$ROOTFS"

log "dnf installroot packages"
sudo dnf -y --installroot="$ROOTFS" --releasever=22.03 install "${PKGS[@]}"

# -----------------------------
# 6) 安装模块 + depmod
# -----------------------------
log "modules_install to rootfs"
sudo make -C "$SRCDIR" O="$BUILDDIR" ARCH=arm64 \
  modules_install INSTALL_MOD_PATH="$ROOTFS"

log "depmod in rootfs"
sudo depmod -b "$ROOTFS" "$KREL"

# -----------------------------
# 7) 把 Image + 目标 dtb 放进 rootfs /boot
# -----------------------------
log "install Image + dtb into rootfs /boot"
sudo mkdir -p "$ROOTFS/boot/dtb"
sudo install -m 0644 "$VMLINUX" "$ROOTFS/boot/Image-$KREL"
sudo install -m 0644 "$DTB_SRC" "$ROOTFS/boot/dtb/$(basename "$DTB_SRC")"

# 固定名 symlink，方便 U-Boot 路径不变
sudo ln -sfn "Image-$KREL" "$ROOTFS/boot/Image"
sudo ln -sfn "dtb/$(basename "$DTB_SRC")" "$ROOTFS/boot/devicetree.dtb"

# -----------------------------
# 8) machine-id + NM 配置 + 启用服务
# -----------------------------
log "machine-id setup"
sudo truncate -s 0 "$ROOTFS/etc/machine-id"
sudo rm -f "$ROOTFS/var/lib/dbus/machine-id"
sudo mkdir -p "$ROOTFS/var/lib/dbus"
sudo ln -sf /etc/machine-id "$ROOTFS/var/lib/dbus/machine-id"

log "NetworkManager.conf"
sudo mkdir -p "$ROOTFS/etc/NetworkManager"
cat <<'EOF' | sudo tee "$ROOTFS/etc/NetworkManager/NetworkManager.conf" >/dev/null
[main]
plugins=keyfile

[device]
wifi.scan-rand-mac-address=no
EOF

log "enable services"
sudo systemctl --root="$ROOTFS" enable NetworkManager
sudo systemctl --root="$ROOTFS" enable sshd

# -----------------------------
# 9) 打包 rootfs.ext4 镜像
# -----------------------------
log "make ext4 image: $IMG (size=$IMG_SIZE)"
sudo mkdir -p "$(dirname "$IMG")"
rm -f "$IMG"
truncate -s "$IMG_SIZE" "$IMG"
mkfs.ext4 -F -L rootfs "$IMG"

MNT=/mnt/rootfs_img
sudo mkdir -p "$MNT"
sudo mount -o loop "$IMG" "$MNT"

log "rsync rootfs -> image (exclude pseudo fs)"
sudo rsync -aHAX --numeric-ids \
  --exclude='/proc/*' --exclude='/sys/*' --exclude='/dev/*' --exclude='/run/*' \
  --exclude='/tmp/*' --exclude='/mnt/*' --exclude='/media/*' --exclude='/lost+found' \
  "$ROOTFS"/ "$MNT"/

sudo sync
sudo umount "$MNT"

log "fsck image"
sudo e2fsck -f "$IMG"

# -----------------------------
# 10) 一致性检查（防止内核/模块不匹配）
# -----------------------------
log "sanity check: modules directory exists"
test -d "$ROOTFS/lib/modules/$KREL" || die "missing modules dir: $ROOTFS/lib/modules/$KREL"
test -f "$ROOTFS/lib/modules/$KREL/modules.dep" || die "missing modules.dep: $ROOTFS/lib/modules/$KREL/modules.dep"

log "sanity check: Image/dtb exists in rootfs"
test -f "$ROOTFS/boot/Image-$KREL" || die "missing Image in rootfs"
test -f "$ROOTFS/boot/dtb/$(basename "$DTB_SRC")" || die "missing dtb in rootfs"

log "DONE"
echo "KREL=$KREL"
echo "IMG=$IMG"
echo "U-Boot load paths (suggested): /boot/Image and /boot/devicetree.dtb"
