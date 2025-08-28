# U-boot 到 Ubuntu 自动启动：命令说明与完整流程（d2000/arm64）

本文覆盖：U‑Boot 环境准备 → 临时 RAMDISK 启动 → Linux 下分区与写入根文件系统 → 从 NVMe 启动 → 配置自动启动。

> 适用对象：ARM64 平台（示例为 D2000 开发板），U‑Boot 可用，网络可达，TFTP 服务器 IP 为 `192.168.11.100`。

配置完成后可以实现：

1. 可从 RAMDISK 临时进入 Linux 的环境（便于制作 NVMe 根文件系统）；
2. 可从 **NVMe 根文件系统**稳定启动的系统；
3. U‑Boot `bootcmd` 已配置自动化，后续**上电即启动 Ubuntu**。

---

## 0. 名词与前置条件

* **U‑Boot 环境变量存储**：使用 `saveenv` 前，请确认板上环境介质（如 NOR/NAND/EMMC）的偏移与大小配置正确，否则 `saveenv`
  可能失败。
* **TFTP 服务器**：示例中服务器 IP 是 `192.168.11.100`，确保同网段、能互通，并在服务器的 TFTP 根目录放好 `Image`/
  `Image_ramdisk`、`*.dtb`、根文件系统压缩包等文件。
* **内存地址**：示例把内核放在 `0x9010_0000`，DTB 放在 `0x9000_0000`，确保与你的内存布局不冲突（留出足够空闲，不要覆盖 U‑Boot
  自身、栈与其他映像）。

---

## 1. 上电进入 U‑Boot

### 打印环境变量

```bash
pri
```

* **作用**：打印当前 U‑Boot 的环境变量。`pri` 是 `printenv` 的缩写（U‑Boot 支持命令前缀匹配）。

---

## 2. 配置基础网络参数

```bash
setenv ipaddr 192.168.11.102
setenv serverip 192.168.11.100
saveenv
```

* **`setenv ipaddr`**：设置本机（开发板）IP 地址。
* **`setenv serverip`**：设置 TFTP 服务器 IP（U‑Boot 的 `tftpboot` 会用到）。
* **`saveenv`**：把当前环境变量持久化到环境介质（掉电不丢）。

> 可选：临时调试阶段你也可以不 `saveenv`，但每次断电后需要手动重新设置。

---

## 3. 配置 PHY 工作模式（定义一个复用命令）

```bash
setenv enableNet "mii write 0x7 0x1e 0xa003; mii write 0x7 0x1f 0x8007;mii write 0x7 0x1e 0xa004; mii write 0x7 0x1f 0x00b0;mii write 0x7 0x1e 0xa001; mii write 0x7 0x1f 0x0164;mii read  0x7 0x11;"
saveenv
```

* **目的**：把一串 PHY 配置命令封装为一个环境变量 `enableNet`，后续用 `run enableNet` 一次性执行。
* **`mii write <phy-addr> <reg> <val>`**：通过 MDIO/MII 向 PHY 的寄存器写入。

    * 这里的 PHY 地址为 `0x7`（请按你的硬件实际填写）。
    * 多次对 `0x1e/0x1f` 的写入通常是**页选择/扩展寄存器访问**的厂商机制；`0x11` 的读用于查看状态或确认配置是否生效（具体语义依
      PHY 型号而定）。
* **`saveenv`**：持久化该复用命令，后续上电即可直接 `run enableNet`。

> 说明：不同厂商 PHY（如 Marvell 88E 系列）有自定义分页与寄存器布局，上述序列一般用于设置 RGMII 延时、速率/双工等。若更换
> PHY，请参考对应数据手册调整寄存器。

---

## 4. 临时 RAMDISK 启动（内核内置 initramfs）

```bash
run enableNet

# 通过 TFTP 下载“内置了 initramfs 的内核镜像”与 DTB
tftpboot 0x90100000 Image_ramdisk;tftpboot 0x90000000 u-boot-d2000-devboard-dsk.dtb

# 传递内核参数：串口与 earlycon；指定 initramfs 的初始进程为 /bin/sh
setenv bootargs "console=ttyAMA1,115200 earlycon=pl011,0x28001000 rdinit=/bin/sh"

# 启动（booti <kernel> <initrd|-> <fdt>）。这里内核自带 initramfs，所以 initrd 用 '-'
booti 0x90100000 - 0x90000000
```

* **`run enableNet`**：执行第 3 步封装的 PHY 初始化，确保网卡链路正常。
* **`tftpboot`**：从 `serverip` 下载镜像到内存指定地址。
* **`bootargs`**：

    * `console=ttyAMA1,115200`：设置控制台串口与波特率（示例为 PL011 的 ttyAMA1）。
    * `earlycon=pl011,0x28001000`：早期控制台，便于内核早期阶段输出日志。
    * `rdinit=/bin/sh`：initramfs 启动后直接进入一个最小 shell，便于后续手工分区等操作。
* **`booti`**：ARM64 内核启动命令；`-` 表示不提供外部 initrd（此处使用**内置**的 initramfs）。

> 结果：进入一个临时的 RAM 根文件系统（内存盘），不会改动 NVMe 上的持久存储，方便准备磁盘与拷贝根文件系统。

---

## 5. 启动后的 Linux 环境内：分区、格式化、配置网络、下载根文件系统

> 以下命令在临时 RAM 环境（initramfs）中执行。

### 5.1（可选）执行初始化脚本

```bash
/bin/sh /root/run.sh
```

* 若你有自定义脚本（比如加载驱动、配置路由等），可在 RAM 环境下执行。

### 5.2 NVMe 分区与格式化

```bash
fdisk /dev/nvme0n1          # 交互式创建分区（示例稍后使用 p1）
mkfs.ext4 /dev/nvme0n1p1    # 把第 1 分区格式化为 ext4
```

### 5.3 配置网络（Linux 侧）

```bash
ifconfig eth0 192.168.11.102 up
```

* 在 RAM 环境中给 `eth0` 设置 IP 并拉起接口（与 U‑Boot 的 `ipaddr` 是两回事）。

### 5.4 挂载目标分区，下载并展开根文件系统

```bash
mkdir -p /root/nvme
mount /dev/nvme0n1p1 /root/nvme
cd /root/nvme

# 从 TFTP 服务器下载内核、设备树和根文件系统压缩包（Linux 里的 tftp 客户端用法略有不同）
tftp -g -r Image 192.168.11.100

tftp -g -r u-boot-d2000-devboard-dsk.dtb 192.168.11.100

tftp -g -r ubuntu_rootfs.tar.gz 192.168.11.100

# 解包根文件系统
gunzip ubuntu_rootfs.tar.gz
	# 得到 ubuntu_rootfs.tar

tar -xvf ubuntu_rootfs.tar
cd ubuntu_rootfs/ ; mv * ../.
```

* **`tftp -g -r <file> <server>`**：Linux 用户态的 TFTP 客户端（与 U‑Boot 的 `tftpboot` 不同）。
* 解包后把根文件系统内容**移动到分区根目录**（`/root/nvme`）。

> 到此，`/dev/nvme0n1p1` 已写入完整 rootfs，后续可作为 `root=` 设备从 NVMe 启动。

---

## 6. 网络加载内核 + NVMe 根文件系统启动（一次性手动启动）

```bash
run enableNet

tftpboot 0x90100000 Image;tftpboot 0x90000000 u-boot-d2000-devboard-dsk.dtb

setenv bootargs "console=ttyAMA1,115200 audit=0 earlycon=pl011,0x28001000 noinitrd root=/dev/nvme0n1p1 rootwait rw"

booti 0x90100000 - 0x90000000
```

* **思路**：内核与 DTB 仍从 TFTP 获取（便于快速迭代内核），但**根文件系统挂载 NVMe**。
* **关键参数**：

    * `noinitrd`：不再使用 initramfs。
    * `root=/dev/nvme0n1p1`：指定根分区。
    * `rootwait`：等待块设备出现（NVMe 初始化需要时间）。
    * `rw`：以可写方式挂载根分区。

> 结果：系统从 NVMe 的根文件系统启动，便于持久化变更。

---

## 7. 配置自动加载（完全脱离 TFTP，直接从 NVMe 启动）

```bash
# 1) 固化通用内核参数（无需 initrd，根在 NVMe）
setenv bootargs "console=ttyAMA1,115200 audit=0 earlycon=pl011,0x28001000 noinitrd root=/dev/nvme0n1p1 rootwait rw"

# 2) 定义 bootcmd：
#    - 先做 PHY 初始化（保证链路稳定，某些平台网卡与时钟/复位相关）。
#    - 从 NVMe 分区 0:1 读取内核与 DTB 到内存。
#    - 以 booti 启动。
setenv bootcmd "run enableNet;ext4load nvme 0:1 0x90100000 Image;ext4load nvme 0:1 0x90000000 u-boot-d2000-devboard-dsk.dtb;booti 0x90100000 - 0x90000000"

saveenv     # 持久化

# 3) 立即试跑一次
run bootcmd
```

* **`ext4load nvme 0:1 <addr> <file>`**：从 NVMe 控制器 0、分区 1 的 ext4 文件系统读取文件到内存。
* **`bootcmd`**：上电倒计时结束后 U‑Boot 自动执行的命令；保存后下次上电会自动启动 Ubuntu。
