# 制作完整 rootfs.ext4 镜像（openeuler-fusion：out-of-tree + 版本号规则）

目标：在 **ARM 虚拟机/ARM 服务器** 上使用 **openeuler-fusion** 源码 **原生编译内核（Image / modules / dtbs）**，把 *
*modules + Image + dtb** 统一收集进 rootfs，并最终打包成 `rootfs.ext4` 供 U-Boot 开发板启动。

---

## 关键原则（务必先读）

1. **out-of-tree 构建**：所有 `.config/.o/.cmd` 产物落到 `O=`，源码目录保持干净；切分支不会互相污染。
2. `modules_install` **只安装** `/lib/modules/<KREL>/`，不会把 `Image/dtb` 放进 rootfs；`Image/dtb` 必须显式复制/安装。
3. 打 `rootfs.ext4` 时 rsync 必须排除 `/proc /sys /dev /run` 等伪文件系统，否则会把 `kcore` 之类“无限大文件”写爆镜像。
4. **KREL 一致性** 是一切的核心：`LOCALVERSION` → `KREL` → `/lib/modules/$KREL` → `/boot/Image-$KREL` 必须同源。

---

## 0. 环境说明

* 平台：ARM64 物理机（openEuler 22.03 SP4 server）
* 目的：在 ARM 侧验证构建/出 release 版本（你 Windows 侧做交叉编译，ARM 侧主要做验证 + release）。

---

## 1. 一次性依赖（后面自动化不踩坑）

```bash
sudo dnf -y install \
  gcc gcc-c++ make bc bison flex perl \
  elfutils-libelf-devel openssl-devel \
  rsync e2fsprogs util-linux findutils coreutils \
  tar xz gzip
```

如果启用了 BTF（CONFIG_DEBUG_INFO_BTF），可能还需要：

```bash
sudo dnf -y install dwarves || true
```

---

## 2. 获取 openeuler-fusion 源码 + 建立 out-of-tree 构建目录

### 2.1 clone 源码并切分支

```bash
mkdir -p ~/src && cd ~/src
git clone git@rocky-server.lab:618_projects/openeuler-fusion.git
cd openeuler-fusion

# 按需切分支（示例）
# git checkout release
```

### 2.2 每分支一个 O= 目录（强烈推荐）

```bash
BR=$(git rev-parse --abbrev-ref HEAD)
O=$HOME/build/openeuler-fusion/${BR}
mkdir -p "$O"
echo "BR=$BR"
echo "O=$O"
```

这样你的工作流会非常稳定：切分支不会被残留的 .o/tmp 文件污染。

---

## 3. 版本号规则（新）：LOCALVERSION 规范化 → KREL 自带 fusion 标识

> 你现在的 rootfs 构建链路是靠 `LOCALVERSION` 固化，然后用 `make -s ... kernelrelease` 得到 `KREL`。
> 所以“版本号规则”只要写进文档，整个链路就自动一致。

### 3.1 推荐格式

统一约定 `LOCALVERSION` 为：

* `-oe2203sp4-fusion.<SERIES>.<REV>[-g<GIT>][.<FLAVOR>]`

字段说明：

* `oe2203sp4`：发行版标识（openEuler 22.03 SP4）
* `fusion.<SERIES>.<REV>`：你的融合线版本

    * `SERIES`：建议季度/里程碑，例如 `2026Q1`
    * `REV`：从 1 递增，例如 `1/2/3`
* `-g<GIT>`：可选，建议加 12 位短 commit id（便于定位）
* `.FLAVOR`：可选，区分构建风味（例如 `.test/.dbg`）

示例：

* `LOCALVERSION=-oe2203sp4-fusion.2026Q1.1`
* `LOCALVERSION=-oe2203sp4-fusion.2026Q1.2-g1a2b3c4d5e6f`
* `LOCALVERSION=-oe2203sp4-fusion.2026Q1.2-g1a2b3c4d5e6f.test`

> 注意：**不要 export 空的 LOCALVERSION**，否则你以为“用了版本号”，实际没生效。

---

## 4. 配置：.config 的来源、复制、更新（全部发生在 $O）

out-of-tree 的关键规则：

* `.config` 永远在：`$O/.config`
* `make menuconfig/olddefconfig/make` 都读写 `$O/.config`（命令仍在源码根目录执行，只是加 `O="$O"`）。

### 4.1 第一次建立配置（3 选 1）

#### 方案 A：从 defconfig 开始

```bash
make O="$O" phytium_defconfig
# 或者
make O="$O" defconfig
```

#### 方案 B：复制“已知可用”的 config（你最常用）

```bash
cp -f /path/to/config-5.10.0-136.12.0.86.aarch64 "$O/.config"
make O="$O" olddefconfig
```

#### 方案 C：同一分支复用已有 $O/.config

如果 `$O` 里已经有 `.config`，无需重复生成。

### 4.2 交互式修改配置（menuconfig）

```bash
make O="$O" menuconfig
make O="$O" olddefconfig
```

只要改过 `.config`，就建议立刻 `olddefconfig`，避免配置与源码不匹配。

### 4.3 可追溯：保存一份“分支基线 config”（推荐）

```bash
mkdir -p configs
cp -f "$O/.config" configs/fusion_arm64.config
```

恢复：

```bash
cp -f configs/fusion_arm64.config "$O/.config"
make O="$O" olddefconfig
```

---

## 5. 编译内核（Image / modules / dtbs）+ 获取 KREL（关键）

### 5.1 固化版本号 + olddefconfig + 取 KREL

```bash
cd ~/src/openeuler-fusion

# 例：按新规则设置版本号（建议你发布/测试时都显式写）
export LOCALVERSION=-oe2203sp4-fusion.2026Q1.1

# 任何 config 变动后，都做一次 olddefconfig
make -C . O="$O" ARCH=arm64 olddefconfig

# 取干净的 kernelrelease：必须用 -s 抑制 Entering/Leaving directory
KREL=$(make -s -C . O="$O" ARCH=arm64 kernelrelease)
echo "KREL=$KREL"
```

`-s` 这一点是硬要求，否则你后面 `depmod`/脚本解析会被噪声干扰。

### 5.2 正式编译（out-of-tree）

```bash
time make -C . O="$O" ARCH=arm64 -j"$(nproc)" Image modules dtbs
```

产物位置（都在 build 树里）：

* Image：`$O/arch/arm64/boot/Image`
* dtb：`$O/arch/arm64/boot/dts/**/*.dtb`
* modules（编译树会出现，安装到 rootfs 要靠下一步）：`$O/lib/modules/<KREL>/`

---

## 6. 构建 rootfs staging（dnf --installroot）

> 这里使用 **dnf installroot** 生成最小可启动用户态（含 NM + sshd），再把模块/内核产物灌进去。

### 6.1 变量与目录（建议你一次性复制到 shell）

```bash
# 源码与 out-of-tree build
export SRCDIR=$HOME/src/openeuler-fusion
export BUILDDIR=$O

# rootfs staging 与最终镜像输出
export ROOTFS=/mnt/rootfs
export STGDIR=$HOME/staging
export IMG=$STGDIR/rootfs.ext4
export IMG_SIZE=8G

# dtb 选择：按你板子实际 dtb 相对路径填写（相对 arch/arm64/boot/dts/）
# 例：export DTB_REL=phytium/your-board.dtb
# 例：export DTB_REL=phytium/pd2008-devboard.dtb
export DTB_REL=phytium/pd2008-devboard-dsk.dtb
```

### 6.2 创建/清空 rootfs staging 目录

```bash
sudo rm -rf "$ROOTFS"
sudo mkdir -p "$ROOTFS"
```

### 6.3 dnf 安装最小可启动用户态（含 NM + sshd）

> 你要在板子上远程登录，必须装 `openssh-server`，否则 `systemctl enable sshd` 会提示 unit 不存在。

最小集（够用）：

```bash
sudo dnf -y --installroot="$ROOTFS" --nogpgcheck install \
  basesystem systemd passwd shadow-utils util-linux vim-minimal \
  NetworkManager \
  openssh-server openssh-clients
```

（可选）更完整工具集：你原文里也给了“离线本地 repo / 连外网安装”的大包清单，可继续沿用。

```shell
sudo dnf -y   --installroot="$ROOTFS"   --nogpgcheck   install basesystem \
         systemd passwd shadow-utils util-linux vim-minimal   NetworkManager   openssh-server openssh-clients \
         less procps-ng iproute iputils curl dnf python3 python3-libs python3-dnf libdnf librepo \
         rpm rpm-libs ca-certificates gnupg2 \
         tar gzip xz bzip2 zstd \
         coreutils findutils grep sed gawk diffutils file which \
         bash bash-completion sudo tzdata \
         kmod kmod-libs \
         parted e2fsprogs\
         pciutils ethtool tcpdump strace lsof psmisc bind-utils wget chrony
```

---

## 7. 安装内核模块到 rootfs + depmod（必须带 KREL）

### 7.1 modules_install

```bash
sudo make -C "$SRCDIR" O="$BUILDDIR" ARCH=arm64 \
  modules_install INSTALL_MOD_PATH="$ROOTFS"
```

### 7.2 depmod（强制写 modules.dep 等索引）

```bash
sudo depmod -b "$ROOTFS" "$KREL"
```

> 你在脚本里就是这么做的：先 `modules_install`，再 `depmod -b rootfs KREL`。

---

## 8. 把 Image + dtb 放进 rootfs /boot（与 KREL 绑定）

```bash
VMLINUX="$BUILDDIR/arch/arm64/boot/Image"
DTB_SRC="$BUILDDIR/arch/arm64/boot/dts/$DTB_REL"

sudo mkdir -p "$ROOTFS/boot/dtb"
sudo install -m 0644 "$VMLINUX" "$ROOTFS/boot/Image-$KREL"
sudo install -m 0644 "$DTB_SRC" "$ROOTFS/boot/dtb/$(basename "$DTB_SRC")"

# 固定名 symlink，方便 U-Boot 路径不变
sudo ln -sfn "Image-$KREL" "$ROOTFS/boot/Image"
```

这一段与你原脚本一致：`Image-$KREL` 能保证“镜像里的内核”与“镜像里的模块目录”绝不串。

---

## 9. machine-id、NetworkManager、sshd、root 密码

你原脚本的做法很对：不 chroot，直接离线写入必要内容。

### 9.1 machine-id（避免启动时卡顿/重复）

```bash
sudo truncate -s 0 "$ROOTFS/etc/machine-id"
sudo rm -f "$ROOTFS/var/lib/dbus/machine-id"
sudo mkdir -p "$ROOTFS/var/lib/dbus"
sudo ln -sf /etc/machine-id "$ROOTFS/var/lib/dbus/machine-id"
```

### 9.2 NetworkManager.conf（禁用随机 MAC 扫描等）

```bash
sudo mkdir -p "$ROOTFS/etc/NetworkManager"
cat <<'EOF' | sudo tee "$ROOTFS/etc/NetworkManager/NetworkManager.conf" >/dev/null
[main]
plugins=keyfile

[device]
wifi.scan-rand-mac-address=no
EOF
```

### 9.3 启用服务（在 rootfs 里 enable）

```bash
sudo systemctl --root="$ROOTFS" enable NetworkManager
sudo systemctl --root="$ROOTFS" enable sshd
```

### 9.4 设置 root 密码（离线写 shadow）

> 你原脚本用 `openssl passwd -6` 写入 shadow，这招很好用。

```bash
: "${ROOT_PASSWORD:=wuyh12#\$}"   # 可通过环境变量覆盖
HASH="$(openssl passwd -6 "$ROOT_PASSWORD")"

sudo chmod 600 "$ROOTFS/etc/shadow"
sudo sed -i "s#^root:[^:]*:#root:${HASH}:#" "$ROOTFS/etc/shadow"
```

### 9.5 时区（固化 Asia/Shanghai）

> 不依赖 chroot，直接写 `/etc/localtime` 软链 + timezone 文本。

```bash
sudo ln -sf ../usr/share/zoneinfo/Asia/Shanghai "$ROOTFS/etc/localtime"
echo "Asia/Shanghai" | sudo tee "$ROOTFS/etc/timezone" >/dev/null
```

---

### 9.6 安装并启用 chrony（NTP 校时）

> 你的板子 RTC 可能是 `n/a`，启动会回到 1970。chrony + NTP 是根本解法。

（如果你在更早的 dnf --installroot 阶段装包，也可以把 `chrony` 加进基础包清单；这里给的是补装写法）

```bash
sudo dnf --installroot="$ROOTFS" install -y chrony
sudo systemctl --root="$ROOTFS" enable chronyd
```

---

### 9.7 开机强制快速校时（从 1970 秒跳到当前时间）

你有两种方案，**建议 A+B 都配**（A 简单，B 更保险）：

#### A）chrony.conf 允许 step（推荐）

```bash
# 允许在启动初期直接 step（比如从 1970 跳到 2026）
sudo grep -q '^makestep ' "$ROOTFS/etc/chrony.conf" || \
  echo 'makestep 1.0 3' | sudo tee -a "$ROOTFS/etc/chrony.conf" >/dev/null
```

#### B）systemd one-shot：网络就绪后执行一次 makestep（更确定）

```bash
cat <<'EOF' | sudo tee "$ROOTFS/etc/systemd/system/time-sync-makestep.service" >/dev/null
[Unit]
Description=Force chrony to step time at boot
Wants=network-online.target chronyd.service
After=network-online.target chronyd.service

[Service]
Type=oneshot
ExecStart=/usr/bin/chronyc -a makestep

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl --root="$ROOTFS" enable time-sync-makestep.service
```

#### 同时建议：启用 NetworkManager 的 wait-online（确保“网络就绪”是真的就绪）

否则 `network-online.target` 可能过早达成，导致 makestep 执行时还没 DNS/路由。

```bash
sudo systemctl --root="$ROOTFS" enable NetworkManager-wait-online.service
```

---

## 10. 打包 rootfs.ext4 镜像（rsync 排除伪文件系统）

```bash
sudo mkdir -p "$(dirname "$IMG")"
rm -f "$IMG"
truncate -s "$IMG_SIZE" "$IMG"
mkfs.ext4 -F -L rootfs "$IMG"

MNT=/mnt/rootfs_img
sudo mkdir -p "$MNT"
sudo mount -o loop "$IMG" "$MNT"

sudo rsync -aHAX --numeric-ids \
  --exclude='/proc/*' --exclude='/sys/*' --exclude='/dev/*' --exclude='/run/*' \
  --exclude='/tmp/*' --exclude='/mnt/*' --exclude='/media/*' --exclude='/lost+found' \
  "$ROOTFS"/ "$MNT"/

sudo sync
sudo umount "$MNT"

sudo e2fsck -f "$IMG"
```

排除项与顺序完全沿用你原脚本的关键段落。

`rootfs.etx4` 产品在 `/root/staging/rootfs.ext4` 目录

---

## 11. 一致性检查（防止内核/模块不匹配）

```bash
test -d "$ROOTFS/lib/modules/$KREL" || { echo "missing modules dir"; exit 1; }
test -f "$ROOTFS/lib/modules/$KREL/modules.dep" || { echo "missing modules.dep"; exit 1; }

test -f "$ROOTFS/boot/Image-$KREL" || { echo "missing Image-$KREL"; exit 1; }
test -f "$ROOTFS/boot/dtb/$(basename "$DTB_SRC")" || { echo "missing dtb"; exit 1; }

echo "KREL=$KREL"
echo "IMG=$IMG"
```

你原脚本也把这些 sanity check 写得很到位。

---

## 12. 用法（推荐你就按这三种跑）

### 12.1 一条命令：构建当前分支的 rootfs.ext4（最常用）

```bash
# 进入仓库
cd ~/src/openeuler-fusion

# 自动生成 O=（每分支一个）
BR=$(git rev-parse --abbrev-ref HEAD)
O=$HOME/build/openeuler-fusion/${BR}
mkdir -p "$O"

# 设置版本号（按新规则）
export LOCALVERSION=-oe2203sp4-fusion.2026Q1.1

# （按你的板子填写）
export DTB_REL=phytium/your-board.dtb

# 然后按本文从第 5 章一路执行到第 11 章
```

### 12.2 交互式改配置（menuconfig）

```bash
make O="$O" menuconfig
make O="$O" olddefconfig
```

### 12.3 可复现：固定 config + 固定 LOCALVERSION + 固定 dtb

你可以把：

* `configs/fusion_arm64.config`
* `LOCALVERSION=-oe2203sp4-fusion.2026Q1.2-g<sha>`
* `DTB_REL=...`

三者一起固定，然后每次构建都能 100% 复现同一套 KREL 与 rootfs 内容。

---

如果你希望我再进一步，把这份“手动分步文档”压缩成一个**可直接放仓库的 build_all.sh 流程说明**
（只改文档，不改仓库代码），我也可以把“变量→步骤→产物→检查”做成更像你的项目 README 那种风格。
