# 在 WSL 中打包 openEuler 根文件系统并部署到 NVMe 的完整流程

目标：
在 WSL Ubuntu 环境中，把已经编译好的 `5.10.0-phytium-embedded-v2.3` 内核 + 模块 + 设备树，和 `~/euler/oe-root` 里的 openEuler 根文件系统组装成一个 `oe-rootfs-5.10.0-phytium-embedded-v2.3.tar`（约 3.7G），再部署到开发板的 `nvme0n1p2` 上，由 U-Boot 引导启动。

目录结构约定：

* 内核源码树：`~/tmp-2/openEuler-5.10.0-216-src`
* 根文件系统（chroot 环境）：`~/euler/oe-root`
* ISO 解包：`~/oeiso`（本流程只用到其中的用户态包）

内核版本号（后文用 `KREL` 表示）：

```bash
cd ~/tmp-2/openEuler-5.10.0-216-src
make kernelrelease
# 输出：
# 5.10.0-phytium-embedded-v2.3
```

---

## 1. 在内核源码树中准备内核、模块和设备树

如果已经完成，可略读。

1. 编译内核、dtb、模块：

   ```bash
   cd ~/tmp-2/openEuler-5.10.0-216-src

   make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- \
       Image dtbs modules -j$(nproc)
   ```

2. 确认内核版本字符串：

   ```bash
   make kernelrelease
   # 记住输出，例如：
   # 5.10.0-phytium-embedded-v2.3
   ```

3. 安装内核模块到根文件系统目录：

   ```bash
   KREL=5.10.0-phytium-embedded-v2.3

   sudo make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- \
       modules_install \
       INSTALL_MOD_PATH=~/euler/oe-root
   ```

   安装完成后，`~/euler/oe-root/lib/modules/${KREL}/` 应该存在。

4. 拷贝内核镜像和设备树到 `oe-root/boot`：

   ```bash
   sudo mkdir -p ~/euler/oe-root/boot

   sudo cp arch/arm64/boot/Image \
       ~/euler/oe-root/boot/Image-${KREL}

   sudo cp arch/arm64/boot/dts/phytium/pd2008-devboard-dsk.dtb \
       ~/euler/oe-root/boot/pd2008-devboard-dsk.dtb
   ```

---

## 2. 在 chroot 中生成 initramfs 和编辑 fstab

1. 进入 chroot：

   ```bash
   cd ~/euler
   sudo ./bin/oe-chroot.sh
   ```

2. 在 chroot 内安装并使用 dracut 生成 initramfs（如未安装）：

   ```bash
   # chroot 内
   dnf install -y dracut

   KREL=5.10.0-phytium-embedded-v2.3
   dracut --kver "${KREL}" --force \
       /boot/initramfs-${KREL}.img
   ```

3. 在 chroot 内编辑根文件系统的 `/etc/fstab`，给将来的根分区留一个占位 UUID：

   ```bash
   vim /etc/fstab
   ```

   示例内容（只保留最基本的根挂载，真实 UUID 之后在板子上再改）：

   ```text
   UUID=ROOTUUID   /   ext4   defaults  0 1
   ```

4. 退出 chroot：

   ```bash
   exit
   ```

---

## 3. 清理挂载并在 WSL 中打包 rootfs

### 3.1 清理 chroot 绑定挂载（必要时重启 WSL）

如果之前多次进入 chroot，`oe-root` 下的 `/proc`、`/sys`、`/dev`、`run` 可能还保持绑定挂载。
简单稳定的做法是在 Windows 端重启 WSL：

```powershell
# 在 Windows PowerShell / CMD 中执行
wsl --shutdown
```

然后重新打开 WSL Ubuntu，回到 `~/euler`。

### 3.2 设置 KREL 变量

```bash
cd ~/euler
KREL=5.10.0-phytium-embedded-v2.3
```

### 3.3 使用 tar 打包根文件系统（排除伪文件系统）

第一次直接 `tar -cpf` 会把 `./sys`、`./proc`、`./run` 等 WSL 自己的伪文件也打进去，产生大量 `socket ignored` 和 `file changed as we read it` 的警告，并且生成了一个逻辑大小高达数百 G 的坏 tar 文件。

最终采用的正确打包方式如下：

```bash
cd ~/euler

sudo tar --numeric-owner --xattrs --acls \
  --exclude='./proc/*' \
  --exclude='./sys/*' \
  --exclude='./dev/*' \
  --exclude='./run/*' \
  -cpf oe-rootfs-${KREL}.tar \
  -C oe-root .
```

打包完成后检查大小：

```bash
ls -lh oe-rootfs-${KREL}.tar
# 期望约 3.7G
```

这就是最终生成的 rootfs 包。

---

## 4. 将 rootfs 部署到开发板的 nvme0n1p2

下面步骤在开发板上执行（从原来的系统，例如 `nvme0n1p1` 启动）。

### 4.1 拷贝 rootfs tar 到板子

在 WSL 中：

```bash
cd ~/euler
scp oe-rootfs-${KREL}.tar openeuler@BOARD_IP:~
```

### 4.2 准备并挂载 `nvme0n1p2`

在开发板上：

```bash
lsblk   # 确认 nvme0n1p2 存在

# 如果需要重新格式化 p2（会清空数据）
sudo mkfs.ext4 /dev/nvme0n1p2

sudo mkdir -p /mnt/newroot
sudo mount /dev/nvme0n1p2 /mnt/newroot
```

确认 `/mnt/newroot` 为空或只有 `lost+found`。

### 4.3 在 p2 上解包 rootfs

```bash
cd /mnt/newroot
sudo tar --numeric-owner --xattrs --acls \
    -xpf ~/oe-rootfs-${KREL}.tar
```

解包后 `/mnt/newroot` 下应包含完整的 Linux 根目录结构：`bin/`、`etc/`、`lib/`、`usr/`、`boot/` 等。

### 4.4 修改 fstab 使用 p2 的真实 UUID

1. 查询 p2 的 UUID：

   ```bash
   sudo blkid /dev/nvme0n1p2
   # 例：
   # /dev/nvme0n1p2: UUID="12345678-90ab-cdef-1234-567890abcdef" TYPE="ext4"
   ```

2. 编辑新系统的 fstab：

   ```bash
   sudo vim /mnt/newroot/etc/fstab
   ```

   把之前的占位行改成：

   ```text
   UUID=12345678-90ab-cdef-1234-567890abcdef  /  ext4  defaults  0 1
   ```

3. 可选收尾：

   ```bash
   sudo systemd-machine-id-setup --root=/mnt/newroot

   # 如果暂时不想被 SELinux 干扰：
   sudo sed -i 's/^SELINUX=.*/SELINUX=permissive/' \
       /mnt/newroot/etc/selinux/config
   ```

确认 `/mnt/newroot/boot` 下至少有：

* `Image-5.10.0-phytium-embedded-v2.3`
* `initramfs-5.10.0-phytium-embedded-v2.3.img`
* `pd2008-devboard-dsk.dtb`

---

## 5. 配置 U-Boot 从 nvme0n1p2 启动

在串口进入 U-Boot 命令行。

### 5.1 设置内核加载地址（如之前未设置）

```bash
setenv kernel_addr_r 0x50000000
setenv fdt_addr_r    0x48000000
setenv ramdisk_addr_r 0x52000000
```

保持与现有可用配置一致即可。

### 5.2 设置 root UUID 和 bootargs

把上面查到的 UUID 填进来：

```bash
setenv rootuuid 12345678-90ab-cdef-1234-567890abcdef

setenv bootargs_nvme2 'console=ttyAMA0,115200 \
root=UUID=${rootuuid} rootfstype=ext4 rw rootwait'
```

必要时可以在后面追加 `loglevel=7`、`earlycon` 等调试参数。

### 5.3 定义从 nvme0n1p2 加载镜像的命令

```bash
nvme scan   # 确认控制器/盘可见

setenv loadimage_nvme2 'ext4load nvme 0:2 ${kernel_addr_r} /boot/Image-5.10.0-phytium-embedded-v2.3'
setenv loaddtb_nvme2   'ext4load nvme 0:2 ${fdt_addr_r} /boot/pd2008-devboard-dsk.dtb'
setenv loadinit_nvme2  'ext4load nvme 0:2 ${ramdisk_addr_r} /boot/initramfs-5.10.0-phytium-embedded-v2.3.img'
```

> 说明：`0:2` 表示第 0 块 NVMe 盘的第 2 个分区，即 `nvme0n1p2`。

### 5.4 组合 bootcmd 并测试启动

```bash
setenv bootcmd_nvme2 'run loadimage_nvme2 loaddtb_nvme2 loadinit_nvme2; \
setenv bootargs ${bootargs_nvme2}; \
booti ${kernel_addr_r} ${ramdisk_addr_r} ${fdt_addr_r}'
```

先不要 `saveenv`，直接测试：

```bash
run bootcmd_nvme2
```

如果一切正常，系统会从 `nvme0n1p2` 启动，根挂载为 `UUID=1234...` 对应的分区。

### 5.5 设为默认启动并保留回滚路径

确认从 p2 启动稳定后：

```bash
setenv bootcmd 'run bootcmd_nvme2'
saveenv
```

同时建议保留原来从 p1 启动的命令，例如：

```bash
setenv bootcmd_nvme1 '...原来那套启动命令...'
saveenv
```

出现问题时可在 U-Boot 提示符下：

```bash
run bootcmd_nvme1
```

回滚到旧系统。

---

## 6. 实习生复现要点

1. 保证目录结构与本文一致，特别是 `~/euler/oe-root` 和 `~/tmp-2/openEuler-5.10.0-216-src`。
2. 内核版本字符串 `KREL` 必须贯穿全流程一致（内核、模块路径、initramfs 文件名、U-Boot 加载路径）。
3. 打包 rootfs 时务必排除 `/proc`、`/sys`、`/dev`、`/run` 等伪文件系统，否则 tar 包会异常巨大且无效。
4. 在板子上修改 `fstab` 为真实 UUID，否则内核找不到根文件系统。
5. U-Boot 的 `ext4load` 分区号要对应 `nvme0n1p2`，不要写错成 `0:1` 或其他。

实习生只要严格按本文的顺序执行，就可以从零复现整个“3.7G rootfs 打包 + nvme0n1p2 部署 + U-Boot 引导”的完整过程。
