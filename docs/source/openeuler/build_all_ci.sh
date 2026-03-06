#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# 0) CI-safe 路径（全部基于当前仓库目录）
# ============================================================
WORKDIR="${WORKDIR:-$PWD}"

SRCDIR="${SRCDIR:-$WORKDIR}"          # 源码 = GitLab 拉下来的仓库
BUILDDIR="${BUILDDIR:-$WORKDIR/build}"
STGDIR="${STGDIR:-$WORKDIR/output}"
ROOTFS="${ROOTFS:-$WORKDIR/rootfs}"
IMG="${IMG:-$STGDIR/rootfs.ext4}"
IMG_SIZE="${IMG_SIZE:-8G}"

KCONF="${KCONF:-$WORKDIR/configs/phytium_defconfig}"
DTB_REL="${DTB_REL:-phytium/pd2008-devboard-dsk.dtb}"

MENUCONFIG="${MENUCONFIG:-0}"
KCONFIG_FRAGMENTS="${KCONFIG_FRAGMENTS:-}"
LOCALVERSION="${LOCALVERSION:-}"

ROOT_PASSWORD="${ROOT_PASSWORD:-wuyh12#\$}"

PKGS=(
  basesystem systemd passwd shadow-utils util-linux
  bash bash-completion coreutils findutils grep sed gawk diffutils file which sudo tzdata
  tar gzip xz bzip2 zstd
  vim-minimal less procps-ng iproute iputils strace lsof psmisc
  NetworkManager openssh-server openssh-clients curl wget ethtool tcpdump bind-utils
  dnf python3 python3-libs python3-dnf libdnf librepo rpm rpm-libs
  kmod kmod-libs parted e2fsprogs resize2fs nvme-cli pciutils
  ca-certificates gnupg2
)

MNT="$WORKDIR/rootfs_img"

# ============================================================
# 1) 工具函数
# ============================================================
die() { echo "ERROR: $*" >&2; exit 1; }
need_cmd() { command -v "$1" >/dev/null 2>&1 || die "missing command: $1"; }
log() { echo "[+] $*"; }

# ============================================================
# 2) 前置检查
# ============================================================
for c in make rsync mkfs.ext4 e2fsck dnf depmod truncate install mount umount openssl; do
  need_cmd "$c"
done

[[ -f "$KCONF" ]] || die "KCONF not found: $KCONF"

mkdir -p "$BUILDDIR" "$STGDIR"

log "WORKDIR=$WORKDIR"
log "SRCDIR=$SRCDIR"
log "BUILDDIR=$BUILDDIR"
log "ROOTFS=$ROOTFS"
log "IMG=$IMG"

# ============================================================
# 3) 内核配置（严格只在 BUILDDIR）
# ============================================================
log "prepare kernel config"
cp -f "$KCONF" "$BUILDDIR/.config"

[[ -n "$LOCALVERSION" ]] && export LOCALVERSION

make -C "$SRCDIR" O="$BUILDDIR" ARCH=arm64 olddefconfig

if [[ -n "$KCONFIG_FRAGMENTS" ]]; then
  MERGE_SH="$SRCDIR/scripts/kconfig/merge_config.sh"
  [[ -x "$MERGE_SH" ]] || die "merge_config.sh not found"

  IFS=':' read -r -a frags <<< "$KCONFIG_FRAGMENTS"
  "$MERGE_SH" -m -O "$BUILDDIR" "$BUILDDIR/.config" "${frags[@]}"
  make -C "$SRCDIR" O="$BUILDDIR" ARCH=arm64 olddefconfig
fi

[[ "$MENUCONFIG" == "1" ]] && die "MENUCONFIG is not allowed in CI"

KREL="$(make -s -C "$SRCDIR" O="$BUILDDIR" ARCH=arm64 kernelrelease)"
log "KREL=$KREL"

# ============================================================
# 4) 编译 Image / modules / dtbs
# ============================================================
log "build kernel"
make -C "$SRCDIR" O="$BUILDDIR" ARCH=arm64 -j"$(nproc)" Image modules dtbs

VMLINUX="$BUILDDIR/arch/arm64/boot/Image"
DTB_SRC="$BUILDDIR/arch/arm64/boot/dts/$DTB_REL"

[[ -f "$VMLINUX" ]] || die "Image missing"
[[ -f "$DTB_SRC" ]] || die "dtb missing: $DTB_REL"

# ============================================================
# 5) 构建 rootfs
# ============================================================
log "build rootfs"
log "build rootfs into $ROOTFS"
rm -rf "$ROOTFS"
mkdir -p "$ROOTFS"

log "dnf installroot packages"
dnf -y \
  --installroot="$ROOTFS" \
  --releasever=22.03 \
  --setopt=install_weak_deps=False \
  --nodocs \
  install "${PKGS[@]}"

# ============================================================
# 6) 安装 modules + depmod
# ============================================================
log "modules_install to rootfs"
make -C "$SRCDIR" O="$BUILDDIR" ARCH=arm64 \
  modules_install INSTALL_MOD_PATH="$ROOTFS"

log "depmod in rootfs"
depmod -b "$ROOTFS" "$KREL"
# ============================================================
# 7) 安装 Image / dtb 到 rootfs
# ============================================================
log "install Image + dtb into rootfs /boot"
mkdir -p "$ROOTFS/boot/dtb"

install -m 0644 "$VMLINUX" "$ROOTFS/boot/Image-$KREL"
install -m 0644 "$DTB_SRC" "$ROOTFS/boot/dtb/$(basename "$DTB_SRC")"

ln -sfn "Image-$KREL" "$ROOTFS/boot/Image"
ln -sfn "dtb/$(basename "$DTB_SRC")" "$ROOTFS/boot/devicetree.dtb"

# ============================================================
# 8) 系统配置
# ============================================================
log "machine-id setup"
truncate -s 0 "$ROOTFS/etc/machine-id"
rm -f "$ROOTFS/var/lib/dbus/machine-id"
mkdir -p "$ROOTFS/var/lib/dbus"
ln -sf /etc/machine-id "$ROOTFS/var/lib/dbus/machine-id"

log "NetworkManager.conf"
mkdir -p "$ROOTFS/etc/NetworkManager"
cat >"$ROOTFS/etc/NetworkManager/NetworkManager.conf" <<EOF
[main]
plugins=keyfile
[device]
wifi.scan-rand-mac-address=no
EOF

systemctl --root="$ROOTFS" enable NetworkManager
systemctl --root="$ROOTFS" enable sshd

log "set root password (offline shadow edit)"
HASH="$(openssl passwd -6 "$ROOT_PASSWORD")"
sed -i "s#^root:[^:]*:#root:${HASH}:#" "$ROOTFS/etc/shadow"

# ============================================================
# 9) 打包 ext4 镜像（最终产物）
# ============================================================
log "make ext4 image: $IMG (size=$IMG_SIZE)"
rm -f "$IMG"
truncate -s "$IMG_SIZE" "$IMG"
mkfs.ext4 -F -L rootfs "$IMG"

mkdir -p "$MNT"
mount -o loop "$IMG" "$MNT"

log "rsync rootfs -> image (exclude pseudo fs)"
rsync -aHAX --numeric-ids \
  --exclude='/proc/*' --exclude='/sys/*' --exclude='/dev/*' \
  --exclude='/run/*' --exclude='/tmp/*' \
  "$ROOTFS"/ "$MNT"/

sync
umount "$MNT"
log "fsck image"
e2fsck -fy "$IMG"

# ============================================================
# 10) CI 产物信息
# ============================================================
echo "KREL=$KREL" | tee "$STGDIR/build-info.txt"
echo "IMG=$IMG"   | tee -a "$STGDIR/build-info.txt"

log "DONE"
