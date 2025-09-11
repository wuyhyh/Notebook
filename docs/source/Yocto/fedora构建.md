好，按你现在的目标（VMware 里的 **Fedora Server** 上从零构建，产出 **qemuarm64** 镜像，用 **20 GB NVMe**，根分区小、首启后在线扩容），我把整套流程重新梳理成一份能直接照做的手册。**千万不要用 root 跑 bitbake**——这是之前最常见的坑。

---

# 0) VMware 虚机参数（建议）

* vCPU：6–8
* 内存：24–32 GB（16 GB 也可，但构建会吃紧）
* 系统盘：**120 GB 推荐**（80 GB 也能跑，见“省盘”提示）
* 网络：NAT 即可
* 注：x86\_64 宿主上跑 aarch64 QEMU 只能 TCG（纯软件），用 `-accel tcg,thread=multi`。

空间大致消耗（首次构建）：downloads 10–20 GB + sstate 15–40 GB + tmp 10–25 GB。给 120 GB 最省心；80 GB 需开省盘。

---

# 1) Fedora 基础准备（**非 root 普通用户**）

以下假设你用普通用户（例如 `builder`）。若当前是 root，请先创建用户并 `su - builder`。

```bash
# 开发工具与依赖（Fedora 39/40/41 通用）
sudo dnf -y groupinstall "Development Tools"
sudo dnf -y install \
  gawk wget git diffstat unzip texinfo chrpath socat cpio which bc \
  python3 python3-pip python3-pexpect python3-jinja2 python3-GitPython \
  xz zstd lz4 tar \
  qemu-system-aarch64 qemu-img bmap-tools parted dosfstools e2fsprogs gdisk

# 常规环境（Fedora 通常已是 UTF-8）
echo 'export LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8' >> ~/.bashrc && source ~/.bashrc
```

> `gdisk` 包里自带 `sgdisk`（扩分区时会用到）。

---

# 2) 拉代码 & 固定构建目录

```bash
mkdir -p ~/yocto && cd ~/yocto
git clone git://git.yoctoproject.org/poky -b kirkstone
cd poky
git clone https://github.com/openembedded/meta-openembedded -b kirkstone

# 固定构建目录到 poky 外面（避免 build/build 嵌套）
source oe-init-build-env ~/yocto/build
```

> 以后每次开新终端，都在 `~/yocto/poky` 执行：
> `source oe-init-build-env ~/yocto/build`（仍然用普通用户！）

---

# 3) 配置 `local.conf`

```bash
cat >> conf/local.conf <<'EOF'
MACHINE ??= "qemuarm64"

BB_NUMBER_THREADS ?= "24"
PARALLEL_MAKE ?= "-j24"

IMAGE_FSTYPES += "wic wic.bmap"
EXTRA_IMAGE_FEATURES += "ssh-server-dropbear debug-tweaks"
WKS_FILE ?= "nvme-gpt.wks"

# 统一缓存（注意：用 ${HOME}，不要用 $USER）
DL_DIR     = "${HOME}/yocto-cache/downloads"
SSTATE_DIR = "${HOME}/yocto-cache/sstate-cache"

# 可选：更省盘，但重编译更慢
# INHERIT += "rm_work"
EOF

mkdir -p ~/yocto-cache/{downloads,sstate-cache}
```

---

# 4) 创建自定义层 & 必要文件

```bash
bitbake-layers create-layer ~/yocto/poky/meta-virtarm64
bitbake-layers add-layer    ~/yocto/poky/meta-openembedded/meta-oe
bitbake-layers add-layer    ~/yocto/poky/meta-virtarm64
bitbake-layers show-layers  # 确认两层已加入
```

## 4.1 让 wic 能找到自定义 `.wks`

```bash
echo 'WKS_SEARCH_PATH:prepend = "${LAYERDIR}/wic:"' \
  >> ~/yocto/poky/meta-virtarm64/conf/layer.conf
mkdir -p ~/yocto/poky/meta-virtarm64/{wic,recipes-core/images}
```

## 4.2 `wic/nvme-gpt.wks`（小根分区，不带 --grow）

```bash
cat > ~/yocto/poky/meta-virtarm64/wic/nvme-gpt.wks <<'EOF'
part /boot --source bootimg-partition --ondisk sda --fstype=ext4 --label boot --size 200
part /     --source rootfs           --ondisk sda --fstype=ext4 --label root --size 2048
bootloader --ptable gpt
EOF
```

## 4.3 自定义镜像（把扩容工具打进系统）

> kirkstone 没有 `growpart` 配方；我们用 `parted + resize2fs + sgdisk`。

```bash
cat > ~/yocto/poky/meta-virtarm64/recipes-core/images/my-image.bb <<'EOF'
SUMMARY = "Minimal image for QEMU ARM64 with NVMe + SSH"
LICENSE = "MIT"
require recipes-core/images/core-image-minimal.bb

IMAGE_INSTALL:append = " \
  kernel-modules iproute2 ethtool pciutils nvme-cli bash \
  parted e2fsprogs-resize2fs gptfdisk \
"
EOF
```

---

# 5) 自检 & 构建

```bash
bitbake-layers show-recipes | grep -E '^my-image\b' || echo "my-image 未被识别"
bitbake -e my-image | sed -n 's/^WKS_FILE.*/&/p'
bitbake -e my-image | sed -n 's/^WKS_SEARCH_PATH.*/&/p'
# 能看到 WKS_FILE="nvme-gpt.wks"，且搜索路径包含 meta-virtarm64/wic 即可

bitbake my-image
```

产物：`~/yocto/build/tmp/deploy/images/qemuarm64/`（`my-image-qemuarm64.wic`、`u-boot*.bin`、`Image`、`*.dtb`）。

---

# 6) 准备 20 GB NVMe“硬盘” & pflash“NOR”

```bash
cd ~/yocto/build/tmp/deploy/images/qemuarm64

# 20G 稀疏磁盘
truncate -s 20G nvme.img
# 把 .wic 写到开头（其余空间留给扩容）
dd if=my-image-qemuarm64.wic of=nvme.img bs=4M conv=notrunc status=progress
sync

# pflash 容纳 U-Boot（更贴近“SPI NOR”）
dd if=/dev/zero of=flash0.img bs=1M count=64
# 目录里可能有 u-boot.bin 或 u-boot-qemuarm64.bin，选其一：
dd if=u-boot.bin of=flash0.img conv=notrunc
sync
```

> 想更简单也可直接 `-bios u-boot.bin` 跳过 pflash；但为了贴近“NOR 放 bootloader”，这里用 pflash。

---

# 7) 启动 QEMU

创建 `run-qemu.sh`：

```bash
cat > run-qemu.sh <<'EOF'
#!/usr/bin/env bash
set -e
qemu-system-aarch64 \
  -M virt,gic-version=3,virtualization=true \
  -cpu cortex-a57 -smp 4 -m 16384 -nographic \
  -accel tcg,thread=multi \
  -drive if=pflash,format=raw,file=flash0.img \
  -blockdev driver=file,filename=nvme.img,node-name=nvmefile,auto-read-only=off,discard=unmap \
  -device pcie-root-port,id=rp1 \
  -device nvme,drive=nvmefile,serial=nvme-1,bus=rp1 \
  -netdev user,id=net0,hostfwd=tcp::2222-:22 \
  -device virtio-net-pci,netdev=net0 \
  -device virtio-rng-pci
EOF
chmod +x run-qemu.sh
./run-qemu.sh
```

U-Boot 里启动：

```
=> pci enum
=> nvme scan
=> sysboot nvme 0:1 any /boot/extlinux/extlinux.conf
```

---

# 8) 首启在线扩容到 20 GB（无需 growpart）

登陆系统后：

```bash
sgdisk -e /dev/nvme0n1              # 把备份 GPT 移到磁盘末尾（关键）
parted -s /dev/nvme0n1 unit % resizepart 2 100%   # 扩大第2分区到磁盘末尾
partprobe /dev/nvme0n1 || true      # 让内核重读分区表；若无效可重启一次
resize2fs -p /dev/nvme0n1p2         # 扩展 ext4 文件系统
lsblk
df -h /
```

---

## 常见坑与快速排查

* **不要用 root 跑**：看到 `#` 提示符或路径在 `/root/...` 就错了。用普通用户。
* **`Nothing PROVIDES 'my-image'`**：`my-image.bb` 没被层收录或层未 add。`bitbake-layers show-layers`/`show-recipes` 自检，必要时 `bitbake-layers add-layer ~/yocto/poky/meta-virtarm64`。
* **找不到 `nvme-gpt.wks`**：确认文件在 `meta-virtarm64/wic/` 且 `layer.conf` 已加
  `WKS_SEARCH_PATH:prepend = "${LAYERDIR}/wic:"`。
* **sanity 报权限**：`DL_DIR`/`SSTATE_DIR` 必须是**你用户可写**的真实路径（本文用 `${HOME}/yocto-cache/...`）。
* **磁盘空间不足**：启用 `INHERIT += "rm_work"`；定期 `du -sh ~/yocto/build/tmp` & `~/yocto-cache`；把 downloads/sstate 缓存放在更大的卷。
* **QEMU 很慢**：跨架构无 KVM；确保 `-accel tcg,thread=multi`，并减少镜像内容。

---

按这份“Fedora Server on VMware”指南，从 0 到运行 QEMU 和在线扩容都能一次走通。中途任何一步报错，把**命令与完整报错段**贴出来，我据此快速定位修正。

