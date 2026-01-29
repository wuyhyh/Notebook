# openeuler 22.03 (aarch64) 从编译内核到生成 rootfs.ext4 的一体化流程

目标：在 **ARM 虚拟机/ARM 服务器** 上原生编译内核（Image / modules / dtbs），把 **modules + Image + dtb** 统一收集进
rootfs，并最终打包成 `rootfs.ext4` 供 U-Boot 开发板启动。

> 关键原则
> - `modules_install` 只负责 `/lib/modules/<KREL>/`，不会把 Image/dtb 放进 rootfs。Image/dtb 必须显式拷贝或
    `dtbs_install`。
> - 构建 rootfs 打镜像时必须排除 `/proc /sys /dev /run`，否则会把 `kcore` 之类“无限大文件”写爆镜像。

---

## 0. 变量与目录（整篇只用这些变量，前后必须统一）

把下面这段复制到你的 shell（或写进 `~/.bashrc` / 一个 `env.sh`）：

```bash
# 内核源码、编译输出（build 在源码外）
export SRCDIR=$HOME/src/openeuler-5.10.0-136-src-master
export BUILDDIR=$HOME/build/oe-kernel-5.10.0-136

# rootfs staging 与最终镜像输出
export ROOTFS=/mnt/rootfs
export STGDIR=$HOME/staging
export IMG=$STGDIR/rootfs.ext4
export IMG_SIZE=8G

# 你的内核配置文件（来自 openeuler 的 config 或你维护的基线 config）
export KCONF=$HOME/config-5.10.0-136.12.0.86.aarch64

# 内核版本后缀（可选，建议固定，便于模块配套）
export LOCALVERSION=-baseline_2026Q1-Alpha
```

目录结构建议：

```
~/src/     # 放源码
~/build/   # 放 O= 输出（不污染源码树）
~/staging/ # 放最终产物（rootfs.ext4、可选的 Image/dtb 备份）
/mnt/rootfs # dnf --installroot 的 rootfs staging（临时目录）
```

---

## 1. 依赖包（一次装齐，后面自动化不踩坑）

在编译机（ARM 虚拟机/ARM 服务器）上安装常用依赖：

```bash
sudo dnf -y install   gcc gcc-c++ make bc bison flex perl   elfutils-libelf-devel openssl-devel   rsync e2fsprogs util-linux findutils coreutils   tar xz gzip
```

如果你启用了 BTF（CONFIG_DEBUG_INFO_BTF），可能还需要 `pahole`（包名常见为 `dwarves`）：

```bash
sudo dnf -y install dwarves || true
```

---

## 2. 准备内核源码与 build 输出目录（build 在源码外）

### 2.1 解压源码

```bash
mkdir -p "$(dirname "$SRCDIR")"
cd "$(dirname "$SRCDIR")"
tar -xf "$HOME/openeuler-5.10.0-136-src-master.tar.gz"
```

### 2.2 创建 build 目录并放置 `.config`

```bash
mkdir -p "$BUILDDIR"
cp -f "$KCONF" "$BUILDDIR/.config"
```

### 2.3 生成最终配置（只在 build 目录里生成）

```bash
make -C "$SRCDIR" O="$BUILDDIR" ARCH=arm64 olddefconfig
```

可选：交互修改配置（只影响 `$BUILDDIR/.config`）

```bash
make -C "$SRCDIR" O="$BUILDDIR" ARCH=arm64 menuconfig
```

```bash
cd $SRCDIR
CONF=$BUILDDIR/.config

chmod +x scripts/config

# 关 hotplug 相关
scripts/config --file "$CONF" --disable HOTPLUG_PCI
scripts/config --file "$CONF" --disable HOTPLUG_PCI_PCIE
scripts/config --file "$CONF" --disable HOTPLUG_PCI_SHPC
scripts/config --file "$CONF" --disable HOTPLUG_PCI_ACPI

# 关 PCIe DPC/ECRC
scripts/config --file "$CONF" --disable PCIE_DPC
scripts/config --file "$CONF" --disable PCIE_ECRC

# 关 IOMMU/SMMU + ATS/PRI/PASID
scripts/config --file "$CONF" --disable IOMMU_SUPPORT
scripts/config --file "$CONF" --disable ARM_SMMU
scripts/config --file "$CONF" --disable ARM_SMMU_V3
scripts/config --file "$CONF" --disable PCI_ATS
scripts/config --file "$CONF" --disable PCI_PRI
scripts/config --file "$CONF" --disable PCI_PASID

# 让 Kconfig 补齐依赖/默认值（关键！）
make -C "$SRCDIR" O="$BUILDDIR" ARCH=arm64 olddefconfig
```

---

## 3. 编译内核（Image / modules / dtbs）

### 3.1 固化版本号（建议）

```bash
export LOCALVERSION="$LOCALVERSION"
make -C "$SRCDIR" O="$BUILDDIR" ARCH=arm64 olddefconfig

# 取干净的 kernelrelease：必须用 -s 抑制 Entering/Leaving directory
KREL=$(make -s -C "$SRCDIR" O="$BUILDDIR" ARCH=arm64 kernelrelease)
echo "KREL=$KREL"
```

### 3.2 正式编译

```bash
time make -C "$SRCDIR" O="$BUILDDIR" ARCH=arm64 -j"$(nproc)"   Image modules dtbs
```

产物位置（都在 build 树里）：

- Image：`$BUILDDIR/arch/arm64/boot/Image`
- dtb：`$BUILDDIR/arch/arm64/boot/dts/**/*.dtb`
- modules：`$BUILDDIR/lib/modules/<KREL>/`（编译树里会出现，真正安装到 rootfs 要靠下一步）

---

## 4. 生成 rootfs（dnf --installroot）并装入 modules + Image + dtb

### 4.1 创建/清空 rootfs staging 目录

```bash
sudo rm -rf "$ROOTFS"
sudo mkdir -p "$ROOTFS"
```

### 4.2 使用 dnf 安装最小可启动用户态（含 NM + sshd）

> 你要在板子上远程登录，必须装 `openssh-server`，否则 `systemctl enable sshd` 会提示 unit 不存在。

```bash
sudo dnf -y --installroot="$ROOTFS" --releasever=22.03 install   basesystem systemd passwd shadow-utils util-linux vim-minimal   NetworkManager   openssh-server openssh-clients
```

```shell
sudo dnf -y   --installroot="$ROOTFS"   --disablerepo='*' --enablerepo='oe-local'   --nogpgcheck   install basesystem \
         systemd passwd shadow-utils util-linux vim-minimal   NetworkManager   openssh-server openssh-clients \
         less procps-ng iproute iputils curl dnf python3 python3-libs python3-dnf libdnf librepo \
         rpm rpm-libs ca-certificates gnupg2 \
         tar gzip xz bzip2 zstd \
         coreutils findutils grep sed gawk diffutils file which \
         bash bash-completion sudo tzdata \
         kmod kmod-libs \
         parted e2fsprogs nvme-cli resize2fs\
         pciutils ethtool tcpdump strace lsof psmisc bind-utils wget
```

连外网安装：

```shell
sudo dnf -y   --installroot="$ROOTFS"   --nogpgcheck   install basesystem \
         systemd passwd shadow-utils util-linux vim-minimal   NetworkManager   openssh-server openssh-clients \
         less procps-ng iproute iputils curl dnf python3 python3-libs python3-dnf libdnf librepo \
         rpm rpm-libs ca-certificates gnupg2 \
         tar gzip xz bzip2 zstd \
         coreutils findutils grep sed gawk diffutils file which \
         bash bash-completion sudo tzdata \
         kmod kmod-libs \
         parted e2fsprogs nvme-cli resize2fs\
         pciutils ethtool tcpdump strace lsof psmisc bind-utils wget
```

### 4.3 安装内核模块到 rootfs + depmod

```bash
sudo make -C "$SRCDIR" O="$BUILDDIR" ARCH=arm64   modules_install INSTALL_MOD_PATH="$ROOTFS"

KREL=$(make -s -C "$SRCDIR" O="$BUILDDIR" ARCH=arm64 kernelrelease)
sudo depmod -b "$ROOTFS" "$KREL"
```

### 4.4 把 Image / dtb 收集进 rootfs 的 /boot（关键新增）

你的 U-Boot 若用 `ext4load ... /boot/Image-*`，就把它们放在 rootfs 的 `/boot` 最直接：

```bash
sudo mkdir -p "$ROOTFS/boot/dtb"
sudo install -m 0644 "$BUILDDIR/arch/arm64/boot/Image" "$ROOTFS/boot/Image-$KREL"
sudo install -m 0644 "$BUILDDIR/arch/arm64/boot/dts/phytium/pd2008-devboard-dsk.dtb" "$ROOTFS/boot/dtb/"
```

### 4.5 machine-id（首次启动自动生成）

```bash
sudo truncate -s 0 "$ROOTFS/etc/machine-id"
sudo rm -f "$ROOTFS/var/lib/dbus/machine-id"
sudo mkdir -p "$ROOTFS/var/lib/dbus"
sudo ln -sf /etc/machine-id "$ROOTFS/var/lib/dbus/machine-id"
```

### 4.6 NetworkManager 配置（目录不存在就先建）

```bash
sudo mkdir -p "$ROOTFS/etc/NetworkManager"
cat <<'EOF' | sudo tee "$ROOTFS/etc/NetworkManager/NetworkManager.conf" >/dev/null
[main]
plugins=keyfile

[device]
wifi.scan-rand-mac-address=no
EOF
```

### 4.7 启用服务（写入 rootfs，不需要 chroot）

```bash
sudo systemctl --root="$ROOTFS" enable NetworkManager
sudo systemctl --root="$ROOTFS" enable sshd
```

### 4.8 root 密码（可选：离线写 shadow）

如果你要离线设定 root 密码，建议用 hash 写入（避免 chroot 里 PAM/伪文件系统问题）：

```bash
PW='wuyh12#$'   # 你要的密码，注意引号
HASH=$(openssl passwd -6 "$PW")

sudo chmod 600 "$ROOTFS/etc/shadow"
sudo sed -i "s#^root:[^:]*:#root:${HASH}:#" "$ROOTFS/etc/shadow"
```

---

## 5. 打包 rootfs.ext4 镜像（排除伪文件系统）

### 5.1 生成空镜像 + 格式化

```bash
mkdir -p "$(dirname "$IMG")"
rm -f "$IMG"
truncate -s "$IMG_SIZE" "$IMG"
mkfs.ext4 -F -L rootfs "$IMG"
```

### 5.2 rsync 写入镜像（务必排除 /proc /sys /dev /run）

```bash
sudo mkdir -p /mnt/rootfs_img
sudo mount -o loop "$IMG" /mnt/rootfs_img

sudo rsync -aHAX --numeric-ids   --exclude='/proc/*' --exclude='/sys/*' --exclude='/dev/*' --exclude='/run/*'   --exclude='/tmp/*' --exclude='/mnt/*' --exclude='/media/*' --exclude='/lost+found'   "$ROOTFS"/ /mnt/rootfs_img/

sudo sync
sudo umount /mnt/rootfs_img
sudo e2fsck -f "$IMG"
```

`rootfs.etx4` 产品在 `/root/staging/rootfs.ext4` 目录

---

## 6. 部署到开发板（示例：NVMe 分区）

在 PC 上:

```shell
python3 -m http.server 8000 --bind 0.0.0.0
```

在开发板上:

```shell
date -s "2026-7-11 13:00:00"
```

```shell
curl -fL http://192.168.11.100:8000/rootfs.ext4 -o ./rootfs.ext4
sync
```

假设开发板 rootfs 分区是 `/dev/nvme0n1p2`：

```bash
IMG=rootfs.ext4
dd if="$IMG" of=/dev/nvme0n1p2 bs=16M status=progress conv=fsync
fsck.ext4 -f /dev/nvme0n1p2
```

U-Boot 示例（按你实际分区和 dtb 路径改）：

```bash
setenv bootargs 'console=ttyAMA1,115200 root=/dev/nvme0n1p2 rootfstype=ext4 rw rootwait loglevel=7'
ext4load nvme 0:2 ${kernel_addr_r} /boot/Image-5.10.0-baseline_2026Q1-2
ext4load nvme 0:2 ${fdt_addr_r} /boot/dtb/pd2008-devboard-dsk.dtb
booti ${kernel_addr_r} - ${fdt_addr_r}
```

能正常启动进入系统

```shell
setenv bootargs 'console=ttyAMA1,115200 console=ttyAMA0,115200 \
earlycon=pl011,0x28001000 loglevel=8 ignore_loglevel \
root=/dev/nvme0n1p2 rootfstype=ext4 rw rootwait \
maxcpus=1 nmi_watchdog=0 panic=-1 init=/bin/sh'
ext4load nvme 0:2 ${kernel_addr_r} /boot/Image-5.10.0-baseline_2026Q1-2
ext4load nvme 0:2 ${fdt_addr_r} /boot/dtb/pd2008-devboard-dsk.dtb
booti ${kernel_addr_r} - ${fdt_addr_r}
```

然后手动执行：

```shell
mount -t proc  proc  /proc
mount -t sysfs sys   /sys
mount -t devtmpfs dev /dev
mount -t tmpfs tmp /run

exec /lib/systemd/systemd
```

直接执行会在 root 密码输入时处理器 reset

```shell
setenv bootargs 'console=ttyAMA1,115200 console=ttyAMA0,115200 \
earlycon=pl011,0x28001000 loglevel=8 ignore_loglevel \
root=/dev/nvme0n1p2 rootfstype=ext4 rw rootwait \
maxcpus=1 nmi_watchdog=0 panic=-1 init=/lib/systemd/systemd'
ext4load nvme 0:2 ${kernel_addr_r} /boot/Image-5.10.0-baseline_2026Q1-2
ext4load nvme 0:2 ${fdt_addr_r} /boot/dtb/pd2008-devboard-dsk.dtb
booti ${kernel_addr_r} - ${fdt_addr_r}
```

试试指定单核启动，启动了20次都没有出现问题。

```shell
setenv bootargs 'console=ttyAMA1,115200 console=ttyAMA0,115200 \
earlycon=pl011,0x28001000 loglevel=8 ignore_loglevel \
root=/dev/nvme0n1p2 rootfstype=ext4 rw rootwait \
nr_cpus=1 nosmp nmi_watchdog=0 panic=-1 init=/lib/systemd/systemd'
ext4load nvme 0:2 ${kernel_addr_r} /boot/Image-5.10.0-baseline_2026Q1-2
ext4load nvme 0:2 ${fdt_addr_r} /boot/dtb/pd2008-devboard-dsk.dtb
booti ${kernel_addr_r} - ${fdt_addr_r}
```

扩 ext4 文件系统到分区最大

如果 / 就是 ext4：

```shell
sudo resize2fs /dev/nvme0n1p2
```

---

## 7. 启动后自检（确认“内核+模块”配套）

```bash
uname -r
ls /lib/modules/$(uname -r) | head
modprobe -v <你关心的模块名>
systemctl is-enabled NetworkManager sshd
```

## 8. 自动化脚本

```shell
#!/usr/bin/env bash
set -euo pipefail

# -----------------------------
# 0) 用户可改的默认变量
# -----------------------------
: "${SRCDIR:=$HOME/src/openEuler-5.10.0-136-src-master}"
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
  vim-minimal
  NetworkManager
  openssh-server
  openssh-clients
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
  "$MERGE_SH" -O "$BUILDDIR" "$BUILDDIR/.config" "${frags[@]}"
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
```

用法

```shell
chmod +x build_all.sh
LOCALVERSION=-baseline_2026Q1-2 ./build_all.sh
```

交互式改内核选项：

```shell
MENUCONFIG=1 ./build_all.sh
```

自动化改内核选项（可复现，推荐）：

```shell
KCONFIG_FRAGMENTS=$HOME/kcfg/feat-a.cfg:$HOME/kcfg/feat-b.cfg ./build_all.sh
```
