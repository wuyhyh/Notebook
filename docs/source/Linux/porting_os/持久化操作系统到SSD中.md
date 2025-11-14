# 持久化操作系统到 SSD 中

在 wsl Ubuntu 24.04 中操作。

## 1. 复制文件

创建软链接

```text
cd;
ln -s /mnt/c/Users/wuyuhang/Downloads/ downloads
ln -s /mnt/c/Users/wuyuhang/Music/ music
ln -s /home/wuyuhang/openeuler/workdir/build/phytium/tmp/deploy/images/phytium/ images_openeuler
```

> 如果已经创建了就不用再创建

复制文件到 `nvme_images`

```text
cd;mkdir -pv downloads/nvme_images;cd images_openeuler;
cp -v openeuler-image-phytium.tar.bz2 ~/downloads/nvme_images
cp -v pd2008-devboard-dsk.dtb ~/downloads/nvme_images
cp -v Image ~/downloads/nvme_images
```

## 2. 启动 initramdisk 系统

假设你已经有一份“能稳定起”的内核 `Image` 与配套 `pd2008-devboard-dsk.dtb`

建议的安全地址（按你的板子内存可适当调整，三者别重叠）

```bash
setenv kernel_addr_r    0x80200000
setenv fdt_addr_r       0x8F000000
setenv ramdisk_addr_r   0x90000000
setenv fdt_high         0xffffffffffffffff
setenv initrd_high      0xffffffffffffffff
```

```text
tftpboot $kernel_addr_r Image;tftpboot $ramdisk_addr_r rootfs.cpio.gz;setexpr rdsize $filesize;tftpboot $fdt_addr_r pd2008-devboard-dsk.dtb
```

使用自定义初始化脚本，感觉并不能正确运行，末尾还是要调用 `/sbin/init`

```text
setenv bootargs 'console=ttyAMA1,115200 earlycon=pl011,0x28001000 rdinit=/init'
booti $kernel_addr_r $ramdisk_addr_r:$rdsize $fdt_addr_r
```

使用系统初始化脚本

```text
setenv bootargs 'console=ttyAMA1,115200 earlycon=pl011,0x28001000 rdinit=/sbin/init'
booti $kernel_addr_r $ramdisk_addr_r:$rdsize $fdt_addr_r
```

> 注意：
> 如果启动失败进入 kernel panic，**重新启动**。
> 如果启动后命令提示符为 `$` ，不是 `#`，**重新启动**。

启动进入 bash 之后，查看块设备是否挂载成功。可能回出现找不到动态链接库 libnurse的问题，**重新启动**。

```text
lsblk
```

启动之后需要配置 **IP**，才能使用后面的网络工具下载文件到开发板。

```text
ip a
```

**CPU0**

```text
ifconfig eth0 192.168.11.105 up
ifconfig eth1 192.168.11.106 up
```

**CPU1**

```text
ifconfig eth0 192.168.11.107 up
ifconfig eth1 192.168.11.108 up
```

验证网络，ping 3次。
> 如果不指定次数或超时时间可能**无法中断 ping 命令**，失去对串口终端的操作。

```text
ping -c 3 192.168.11.100
```

扫描设备节点

初始化脚本和 systemd 中没有指定自动挂载设备的服务，需要手动扫描，这样才能操作 `/dev/nvme` 设备。

```text
echo /sbin/mdev > /proc/sys/kernel/hotplug 2>/dev/null || true
mdev -s
```

## 3. 写入 ssd

- 创建挂载点并挂载分区

创建两个分区 60G 59.2G

```text
fdisk /dev/nvme0n1
```

创建完：

```text
Command (m for help): p

Disk /dev/nvme0n1: 119.24 GiB, 128035676160 bytes, 250069680 sectors
Disk model: SC6912011-SB128BGJ
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: dos
Disk identifier: 0x00000000

Device         Boot     Start       End   Sectors  Size Id Type
/dev/nvme0n1p1           2048 125831167 125829120   60G 83 Linux
/dev/nvme0n1p2      125831168 250069679 124238512 59.2G 83 Linux

Filesystem/RAID signature on partition 1 will be wiped.
Filesystem/RAID signature on partition 2 will be wiped.
```

格式化为 ext4 文件系统：

```text
mkfs.ext4 /dev/nvme0n1p1
mkfs.ext4 /dev/nvme0n1p2
```

创建完：

```text
# blkid
/dev/nvme0n1p1: UUID="acf1fe2f-13fd-4b82-9d1b-ae6a6fec63ec" BLOCK_SIZE="4096" TYPE="ext4"
/dev/nvme0n1p2: UUID="9c5fa5ac-4851-4031-ac19-c68b30893248" BLOCK_SIZE="4096" TYPE="ext4"
```

挂载：

```text
mkdir -p /mnt/p1 /mnt/p2
mount /dev/nvme0n1p1 /mnt/p1
mount /dev/nvme0n1p2 /mnt/p2
```

- 复制要写入的文件到分区，这个目录是最终系统启动后的/

```text
cd /mnt/p1
```

```text
scp -P 2223 wuyuhang@192.168.11.100:/home/wuyuhang/downloads/nvme_images/* /mnt/p1
```

- 写入到文件系统目录

用这几个变量表示重要的文件和目录

```text
ROOT_TAR=openeuler-image-phytium.tar.bz2
KERNEL=Image
DTB=pd2008-devboard-dsk.dtb
```

**p1**

```text
ROOT_DEV=/dev/nvme0n1p1
ROOT_MNT=/mnt/p1
cd $ROOT_MNT;pwd
```

**p2**

```text
ROOT_DEV=/dev/nvme0n1p2
ROOT_MNT=/mnt/p2
cd $ROOT_MNT;pwd
```

- 在根目录解包

解包保留权限/属主/扩展属性

```text
busybox bunzip2 -c "$ROOT_TAR" | tar -xpf - -C "$ROOT_MNT" --numeric-owner
```

- 移动设备树和内核到 `/boot`，创建分区表

```text
mkdir -p $ROOT_MNT/boot/dtbs
cp -v $KERNEL $ROOT_MNT/boot/Image
cp -v $DTB    $ROOT_MNT/boot/dtbs/

UUID=$(blkid -s UUID -o value $ROOT_DEV)
printf "UUID=%s / ext4 defaults,noatime 0 1\n" "$UUID" > $ROOT_MNT/etc/fstab
cd ..
sync && umount $ROOT_MNT
```

> 最终版操作系统中，可以删除`/`下的这几个文件节省空间

## 4. 使用设备名(/dev/nvme0n1p1)手动启动系统

```text
# 基本地址（确保不和其他映像重叠）
setenv kernel_addr_r    0x80200000
setenv fdt_addr_r       0x8F000000

# 控制台与启动参数
setenv console 'console=ttyAMA1,115200'
setenv bootargs "${console} root=/dev/nvme0n1p1 rw rootwait earlycon ignore_loglevel loglevel=8 audit=0"

# NVMe 读文件并启动
setenv bootcmd_nvme 'pci init; nvme scan; \
ext4load nvme 0:1 ${kernel_addr_r} /boot/Image; \
ext4load nvme 0:1 ${fdt_addr_r}    /boot/dtbs/pd2008-devboard-dsk.dtb; \
booti ${kernel_addr_r} - ${fdt_addr_r}'

setenv bootnvme_p2 'pci init; nvme scan; \
ext4load nvme 0:2 ${kernel_addr_r} /boot/Image; \
ext4load nvme 0:2 ${fdt_addr_r}   /boot/dtbs/pd2008-devboard-dsk.dtb; \
setenv bootargs "${console} root=/dev/nvme0n1p2 rw rootwait earlycon ignore_loglevel loglevel=8 audit=0" \
booti ${kernel_addr_r} - ${fdt_addr_r}'

saveenv
```

> 如果环境变量已经设置，直接输入启动命令

默认从 nvme0n1p1 分区启动：

```text
run bootcmd_nvme
```

从 nvme0n1p2 分区启动：

```text
run bootcmdp2
```

### 4.2 U-Boot 启动参数的进一步修改

```text
setenv bootargs_debug 'console=ttyAMA1,115200 root=/dev/nvme0n1p1 rootwait rw earlycon ignore_loglevel loglevel=8'
setenv bootargs_release 'console=ttyAMA1,115200 root=/dev/nvme0n1p1 rootwait rw loglevel=4'
```

## 5. 在 nvme0n1p2 中写入备份系统

进入 U-Boot 命令行后，先使用 nvme0n1p1 启动：

```text
run bootcmd_nvme
```

启动之后需要配置 **IP**，才能使用后面的网络工具下载文件到开发板。

```text
ip a
```

**CPU0**

```text
ifconfig eth0 192.168.11.105 up
ifconfig eth1 192.168.11.106 up
```

**CPU1**

```text
ifconfig eth0 192.168.11.107 up
ifconfig eth1 192.168.11.108 up
```

```text
mkdir -pv /mnt/p1 /mnt/p2
mount /dev/nvme0n1p2 /mnt/p2
cd /mnt/p2
```

复制最新的版本到开发板 ssd 中

```text
scp -P 2223 wuyuhang@192.168.11.100:~/downloads/hulin_images/* ./
```

```text
scp -P 2223 wuyuhang@192.168.11.100:~/phytium_build/images/Image ./
```

```text
scp -P 2223 wuyuhang@192.168.11.100:~/phytium_build/images/pd2008-devboard-dsk.dtb ./
```

```text
scp -P 2223 wuyuhang@192.168.11.100:~/phytium_build/images/openeuler-image-phytium.tar.bz2 ./
```

设置时间

手工设置一个接近当前的时间

```text
date -s "2025-11-06 12:00:00"
```

```text
有 RTC 的话把系统时钟写回硬件
hwclock --systohc 2>/dev/null || true
```

安装内核和设备树

```text
cd /mnt/p2
mkdir -pv boot/dtbs
cp -v Image boot/
cp -v pd2008-devboard-dsk.dtb boot/dtbs/
```

解包根文件系统

```text
cd /mnt/p2
bzip2 -dc openeuler-image-phytium.tar.bz2 | tar -xpf - -C ./ --numeric-owner
```

```text
sync;cd
```

```text
umount /dev/nvme0n1p2
```

下一次 U-Boot 上电后，使用 nvme0n1p2 启动

## 6. 启动阶段系统配置

### 6.1 精简 sshd（只保留客户端能力）

**目标**

* 启动阶段不再自动启动 SSH 服务器 `sshd`，减少启动耗时和无谓的后台进程。
* 仍然保留 `ssh/scp` 客户端功能，方便开发板主动连接 PC/服务器。

**现象**

* 启动时出现：

  ```text
  Starting OpenBSD Secure Shell server: sshd
    generating ssh RSA host key...
    generating ssh ECDSA host key...
    generating ssh ED25519 host key...
  ```

* 第一次启动会因为生成主机密钥明显拖慢启动；后续每次也会多一个常驻的 `sshd` 进程。

**分析**

* 系统使用 SysV init：

    * 服务脚本：`/etc/init.d/sshd`
    * 自启链接：`/etc/rc2.d/S09sshd`、`/etc/rc3.d/S09sshd`、`/etc/rc4.d/S09sshd`、`/etc/rc5.d/S09sshd`
* 你的实际需求：开发板作为 **客户端** 去 `ssh/scp` 到 PC，并不需要从外部登录开发板。

**配置步骤**

1. 停用 2/3/4/5 级别的 `sshd` 自启动：

   ```sh
   for rl in 2 3 4 5; do
       rm -f /etc/rc${rl}.d/S*sshd
   done
   ```

2. 保留 `/etc/init.d/sshd`，需要时可以手动启动：

   ```sh
   /etc/init.d/sshd start   # 或 service sshd start
   ```

3. 不卸载 `openssh-clients`，继续保留：

   ```sh
   ssh user@pc
   scp user@pc:/path/file /path/on/board
   ```

**结果 / 原因总结**

* 启动日志中不再出现 `Starting OpenBSD Secure Shell server: sshd` 和生成 host key 的耗时步骤。
* 系统少一个长期驻留的守护进程，资源更干净。
* 开发板仍然可以主动发起 `ssh/scp` 连接，完全满足当前使用场景。
* 真有需要时仍然可以手工开启 `sshd`，不会丢失能力，只是从“默认开启”改成“按需开启”。

---

### 6.2 关闭 audit / 清理 audit.log 相关报错

**目标**

* 关闭 Linux 审计子系统和 `auditd` 服务，删掉与 `/var/log/audit/audit.log` 相关的无意义报错。
* 避免在 tmpfs 的 `/var/log` 上频繁创建/修改不需要的审计日志文件，减少启动噪音和逻辑复杂度。

**初始现象**

* 启动时反复输出：

  ```text
  chown: cannot access '/var/log/audit/audit.log': No such file or directory
  Failed to set owner -root- for -/var/log/audit/audit.log-.
  chmod: cannot access '/var/log/audit/audit.log': No such file or directory
  Failed to set mode -0600- for -/var/log/audit/audit.log-.
  ```

* `df -h` 显示根分区为 NVMe 上的 ext4，而 `/var/log` 实际为：

  ```sh
  readlink /var/log  # -> /var/volatile/log（tmpfs）
  ```

  说明日志放在 tmpfs 中，每次上电 `/var/log/audit/*` 都是空的。

**需求判断**

* audit 的作用主要是安全审计 / 合规（记录谁访问了哪些关键资源）。
* 当前场景：单板/小集群，主要目标是跑容器和 HPC 应用，没有合规要求，也没有多租户/多人运维。
* 结论：**完全可以关闭审计功能**，避免无意义的开销和报错。

**技术分析**

1. 内核审计：

    * 通过 `audit=0` 内核参数可以关闭内核 audit 子系统。

2. 用户空间 `auditd` 守护进程：

    * 服务脚本：`/etc/init.d/auditd`
    * 自启链接：`/etc/rc2.d/S20auditd` 等。

3. openEuler 的 `volatile` 脚本：

    * `/etc/openeuler-volatile.cache` 中有关于 `/var/log/audit` 的规则；
    * 启动时会根据这些规则去 `mkdir/chown/chmod`，在失败时输出 `"Failed to set owner ..."` 等错误；
    * 这些错误来自 **volatile 初始化脚本**，和 `auditd` 本身无关。

**配置步骤**

1. **关闭内核审计**

   在 U-Boot 环境中，为启动参数增加：

   ```sh
   ... loglevel=8 audit=0
   ```

   通过 `printenv` / `setenv` 确保 `bootargs` 中包含 `audit=0`。

2. **禁用 auditd 服务**

    * 去掉 runlevel 中的自启链接：

      ```sh
      for rl in 2 3 4 5; do
          rm -f /etc/rc${rl}.d/S*auditd
      done
      ```

    * 将 `/etc/init.d/auditd` 改为“空脚本”：

      ```sh
      #!/bin/sh
      exit 0
      ```

      这样任何 `service auditd start` 都会立刻返回，不会真正启动守护进程。

3. **删除 volatile 中对 /var/log/audit 的处理**

   在 `/etc/openeuler-volatile.cache` 中找到所有关于 `/var/log/audit` 和 `/var/log/audit/audit.log` 的规则与命令，整段*
   *直接删除**，避免留半截 shell 语句导致语法错误。

   同时在 `/etc/default/openeuler-volatiles/00_core` 中注释掉对应条目，防止将来重新生成 cache 时又被加回来：

   ```text
   # d root root 0750 /var/log/audit/ none
   # f root root 0600 /var/log/audit/audit.log none
   ```

**结果 / 原因总结**

* 内核不会再启用审计子系统（`audit=0`）。
* 用户态不会再启动 `auditd`，也不会在 tmpfs 上创建/修改审计日志。
* `/etc/openeuler-volatile.cache` 不再尝试访问 `/var/log/audit*`，启动日志中关于 `audit.log` 的报错彻底消失。
* 对当前“容器 + HPC”场景没有任何功能损失，但启动更快、日志更干净、系统行为更符合实际需求。

### 6.3 网络配置

关闭 dhcp，将网络工作模式配置为 static

