# 04-Linux内核源码目录结构说明

## 1. 文档目标

Linux 内核源码非常庞大，第一次阅读时很容易迷失方向。本篇文档的目标不是记住每一个目录，而是建立一个基本的“源码地图”：知道主要目录大概负责什么内容，遇到问题时应该从哪里开始查。

学习本篇后，应能做到：

1. 知道 Linux 内核源码顶层目录的基本作用。
2. 能够区分架构相关代码、驱动代码、文件系统代码、网络协议栈代码和通用内核代码。
3. 在调试驱动、设备树、启动流程、系统调用等问题时，知道大致应该进入哪些目录。

## 2. Linux 内核源码的整体结构

Linux 内核源码顶层目录通常包含如下内容：

```text
linux/
├── arch/
├── block/
├── certs/
├── crypto/
├── Documentation/
├── drivers/
├── fs/
├── include/
├── init/
├── ipc/
├── kernel/
├── lib/
├── mm/
├── net/
├── samples/
├── scripts/
├── security/
├── sound/
├── tools/
├── usr/
├── virt/
├── Kconfig
└── Makefile
```

可以先把源码树理解成几大类：

| 类别    | 典型目录                                 | 作用                               |
|-------|--------------------------------------|----------------------------------|
| 架构相关  | `arch/`                              | CPU 架构相关代码，例如 ARM64、x86、RISC-V   |
| 驱动相关  | `drivers/`                           | 设备驱动，例如网卡、PCIe、串口、I2C、SPI、DMA    |
| 内核核心  | `kernel/`、`mm/`、`ipc/`               | 调度、进程、内存管理、进程间通信等                |
| 文件系统  | `fs/`                                | ext4、procfs、sysfs、devtmpfs 等文件系统 |
| 网络协议栈 | `net/`                               | TCP/IP、路由、Socket、Netfilter 等     |
| 头文件   | `include/`                           | 内核通用头文件和 UAPI 头文件                |
| 构建系统  | `Makefile`、`Kconfig`、`scripts/`      | 编译、配置、脚本工具                       |
| 文档与工具 | `Documentation/`、`tools/`、`samples/` | 内核文档、调试工具、示例代码                   |

## 3. `arch/`：体系结构相关代码

`arch/` 目录存放不同 CPU 架构相关的代码。例如：

```text
arch/
├── arm/
├── arm64/
├── x86/
├── riscv/
└── ...
```

在 ARM64 平台上，重点关注：

```text
arch/arm64/
├── boot/
├── configs/
├── include/
├── kernel/
├── mm/
└── ...
```

常见子目录说明：

| 路径                     | 作用                         |
|------------------------|----------------------------|
| `arch/arm64/boot/`     | 内核镜像、设备树相关构建位置             |
| `arch/arm64/boot/dts/` | ARM64 平台设备树源码              |
| `arch/arm64/configs/`  | ARM64 默认配置文件，例如 defconfig  |
| `arch/arm64/kernel/`   | ARM64 架构下的异常、中断、启动、系统调用等代码 |
| `arch/arm64/mm/`       | ARM64 架构相关内存管理代码           |
| `arch/arm64/include/`  | ARM64 架构相关头文件              |

如果调试 ARM64 启动、异常向量、中断入口、设备树、页表初始化等问题，通常会进入 `arch/arm64/` 目录。

## 4. `drivers/`：设备驱动代码

`drivers/` 是内核源码中非常重要的目录，绝大多数硬件驱动都在这里。

常见子目录如下：

```text
drivers/
├── base/
├── block/
├── char/
├── clk/
├── dma/
├── gpio/
├── gpu/
├── i2c/
├── input/
├── irqchip/
├── md/
├── misc/
├── mmc/
├── mtd/
├── net/
├── nvme/
├── pci/
├── phy/
├── pinctrl/
├── platform/
├── regulator/
├── rtc/
├── scsi/
├── spi/
├── tty/
├── usb/
└── video/
```

常见目录说明：

| 路径                      | 作用                            |
|-------------------------|-------------------------------|
| `drivers/base/`         | Linux 设备模型核心代码                |
| `drivers/pci/`          | PCI/PCIe 总线、枚举、资源分配等代码        |
| `drivers/net/`          | 网卡驱动和网络设备相关驱动                 |
| `drivers/net/ethernet/` | 以太网控制器驱动                      |
| `drivers/nvme/`         | NVMe 设备驱动                     |
| `drivers/tty/`          | 串口、终端相关驱动                     |
| `drivers/clk/`          | 时钟框架和时钟驱动                     |
| `drivers/irqchip/`      | 中断控制器驱动                       |
| `drivers/gpio/`         | GPIO 控制器驱动                    |
| `drivers/i2c/`          | I2C 总线和控制器驱动                  |
| `drivers/spi/`          | SPI 总线和控制器驱动                  |
| `drivers/dma/`          | DMA 控制器驱动                     |
| `drivers/mmc/`          | SD/eMMC 相关驱动                  |
| `drivers/mtd/`          | SPI NOR、NAND Flash 等 MTD 设备驱动 |
| `drivers/usb/`          | USB 控制器和 USB 设备驱动             |
| `drivers/firmware/`     | 固件接口相关代码，例如 EFI、SCMI 等        |

对嵌入式 Linux 和板级适配来说，`drivers/` 是最常进入的目录之一。

例如：

1. 网口不通：先看 `drivers/net/ethernet/` 和 PHY 驱动。
2. PCIe 设备识别异常：先看 `drivers/pci/`。
3. 串口无输出：先看 `drivers/tty/serial/`。
4. NVMe 无法识别：先看 `drivers/nvme/` 和 `drivers/pci/`。
5. 中断异常：先看 `drivers/irqchip/` 和 `arch/arm64/kernel/irq.c` 等相关代码。

## 5. `fs/`：文件系统代码

`fs/` 目录存放 Linux 文件系统相关代码，包括真实磁盘文件系统和虚拟文件系统。

常见子目录如下：

```text
fs/
├── ext4/
├── proc/
├── sysfs/
├── devpts/
├── ramfs/
├── tmpfs/
├── nfs/
├── overlayfs/
└── ...
```

常见目录说明：

| 路径              | 作用             |
|-----------------|----------------|
| `fs/ext4/`      | ext4 文件系统代码    |
| `fs/proc/`      | `/proc` 虚拟文件系统 |
| `fs/sysfs/`     | `/sys` 虚拟文件系统  |
| `fs/devpts/`    | 伪终端设备文件系统      |
| `fs/ramfs/`     | 基于内存的简单文件系统    |
| `fs/tmpfs/`     | 临时内存文件系统       |
| `fs/nfs/`       | NFS 网络文件系统     |
| `fs/overlayfs/` | OverlayFS 文件系统 |

需要注意的是，`/proc`、`/sys`、`/dev` 这类目录虽然在用户空间看起来像普通目录，但很多内容是内核动态生成的，不一定对应磁盘上的真实文件。

## 6. `mm/`：内存管理代码

`mm/` 目录存放 Linux 内存管理的通用代码，例如页分配、虚拟内存、内存映射、缺页异常处理、slab 分配器等。

常见文件和子目录：

| 路径                      | 作用               |
|-------------------------|------------------|
| `mm/page_alloc.c`       | 物理页分配相关代码        |
| `mm/vmalloc.c`          | `vmalloc` 相关代码   |
| `mm/mmap.c`             | 用户空间内存映射相关代码     |
| `mm/memory.c`           | 页表、缺页处理等核心逻辑     |
| `mm/slab.c`、`mm/slub.c` | slab/slub 小对象分配器 |
| `mm/readahead.c`        | 文件预读机制           |
| `mm/swap*.c`            | swap 相关代码        |

如果问题涉及内存申请失败、页表、用户态 mmap、DMA 内存、内存泄漏、OOM 等，往往需要结合 `mm/`、`arch/<arch>/mm/` 和具体驱动一起分析。

## 7. `kernel/`：内核核心通用代码

`kernel/` 目录存放与体系结构无关或相对通用的内核核心代码。

常见文件和子目录：

| 路径                 | 作用              |
|--------------------|-----------------|
| `kernel/sched/`    | 进程调度器           |
| `kernel/fork.c`    | 进程创建相关代码        |
| `kernel/exit.c`    | 进程退出相关代码        |
| `kernel/irq/`      | 通用中断处理框架        |
| `kernel/time/`     | 时间、定时器相关代码      |
| `kernel/printk/`   | `printk` 日志系统   |
| `kernel/module.c`  | 内核模块加载和卸载       |
| `kernel/kthread.c` | 内核线程相关代码        |
| `kernel/panic.c`   | panic、oops 相关处理 |
| `kernel/sys.c`     | 部分系统调用实现        |

如果调试进程、调度、中断、定时器、内核线程、模块加载、panic 等问题，通常会进入 `kernel/` 目录。

## 8. `net/`：网络协议栈代码

`net/` 目录存放 Linux 网络协议栈代码。

常见子目录：

```text
net/
├── core/
├── ethernet/
├── ipv4/
├── ipv6/
├── netfilter/
├── packet/
├── sched/
├── socket.c
└── ...
```

常见目录说明：

| 路径               | 作用                                |
|------------------|-----------------------------------|
| `net/core/`      | 网络协议栈核心框架，例如 sk_buff、net_device 等 |
| `net/ipv4/`      | IPv4 协议实现                         |
| `net/ipv6/`      | IPv6 协议实现                         |
| `net/netfilter/` | 防火墙、NAT、包过滤相关代码                   |
| `net/sched/`     | 流量控制、队列调度相关代码                     |
| `net/packet/`    | packet socket 相关代码                |
| `net/socket.c`   | socket 系统调用相关入口                   |

网卡驱动通常在 `drivers/net/`，而网络协议栈通常在 `net/`。调试网络问题时，需要区分问题发生在驱动层、协议栈层还是用户空间配置层。

## 9. `include/`：头文件目录

`include/` 目录存放内核通用头文件。

常见子目录：

```text
include/
├── linux/
├── uapi/
├── asm-generic/
├── trace/
└── ...
```

常见目录说明：

| 路径                     | 作用               |
|------------------------|------------------|
| `include/linux/`       | 内核内部通用头文件        |
| `include/uapi/`        | 用户空间可见的内核接口头文件   |
| `include/asm-generic/` | 通用架构抽象头文件        |
| `include/trace/`       | tracepoint 相关头文件 |

需要特别注意 `include/linux/` 和 `include/uapi/` 的区别：

1. `include/linux/` 主要给内核内部代码使用。
2. `include/uapi/` 是 User API，表示用户空间程序也可能依赖这些接口。

架构相关头文件通常在：

```text
arch/arm64/include/
```

实际编译时，内核会把通用头文件和架构相关头文件组合起来使用。

## 10. `init/`：内核初始化代码

`init/` 目录存放内核启动早期的初始化代码。

常见文件：

| 路径                 | 作用                          |
|--------------------|-----------------------------|
| `init/main.c`      | 内核启动主流程，包含 `start_kernel()` |
| `init/do_mounts.c` | 根文件系统挂载相关逻辑                 |
| `init/initramfs.c` | initramfs 相关处理              |
| `init/Kconfig`     | 初始化相关配置项                    |

`start_kernel()` 是理解 Linux 内核启动流程的关键函数之一。它会初始化调度、内存、中断、定时器、控制台、VFS
等一系列核心子系统，最后进入用户空间的第一个进程。

如果要学习 Linux 启动流程，可以从 `init/main.c` 开始阅读。

## 11. `block/`：块设备层代码

`block/` 目录存放 Linux 块设备层相关代码。

块设备包括硬盘、SSD、NVMe、SD 卡、eMMC 等。块设备层位于文件系统和具体存储设备驱动之间。

常见内容：

| 路径                          | 作用          |
|-----------------------------|-------------|
| `block/blk-core.c`          | 块设备层核心代码    |
| `block/blk-mq.c`            | 多队列块层框架     |
| `block/elevator.c`          | I/O 调度器相关代码 |
| `block/partition-generic.c` | 分区识别相关代码    |

调试 NVMe、磁盘 I/O、分区识别、文件系统读写性能时，可能需要关注 `block/`、`drivers/nvme/` 和 `fs/`。

## 12. `ipc/`：进程间通信代码

`ipc/` 目录存放 System V IPC 相关代码，包括消息队列、信号量、共享内存等。

常见文件：

| 路径             | 作用         |
|----------------|------------|
| `ipc/msg.c`    | 消息队列       |
| `ipc/sem.c`    | 信号量        |
| `ipc/shm.c`    | 共享内存       |
| `ipc/mqueue.c` | POSIX 消息队列 |

普通驱动开发中较少直接阅读该目录，但学习进程间通信机制时可以关注。

## 13. `lib/`：通用库函数

`lib/` 目录存放内核内部使用的通用库函数。

常见内容：

| 路径                | 作用           |
|-------------------|--------------|
| `lib/string.c`    | 字符串处理函数      |
| `lib/vsprintf.c`  | 格式化输出相关代码    |
| `lib/rbtree.c`    | 红黑树实现        |
| `lib/list_sort.c` | 链表排序         |
| `lib/crc*`        | CRC 校验相关代码   |
| `lib/kobject.c`   | kobject 相关逻辑 |

内核不能直接使用 glibc，因此很多基础函数由内核自己实现。

## 14. `Documentation/`：内核文档

`Documentation/` 目录存放 Linux 内核官方文档，是非常重要的学习资料来源。

常见内容：

| 路径                           | 作用            |
|------------------------------|---------------|
| `Documentation/admin-guide/` | 系统管理员相关文档     |
| `Documentation/devicetree/`  | 设备树绑定文档       |
| `Documentation/driver-api/`  | 驱动开发 API 文档   |
| `Documentation/filesystems/` | 文件系统文档        |
| `Documentation/networking/`  | 网络相关文档        |
| `Documentation/PCI/`         | PCI/PCIe 相关文档 |
| `Documentation/core-api/`    | 内核核心 API 文档   |

阅读驱动时，建议同步查阅对应的 `Documentation/` 文档，尤其是设备树 binding 文档和 driver-api 文档。

## 15. `scripts/`：构建和辅助脚本

`scripts/` 目录存放内核构建系统和辅助工具脚本。

常见内容：

| 路径                      | 作用                  |
|-------------------------|---------------------|
| `scripts/kconfig/`      | Kconfig 配置系统实现      |
| `scripts/Makefile.*`    | 编译系统相关 Makefile 片段  |
| `scripts/dtc/`          | 设备树编译器相关代码          |
| `scripts/mod/`          | 内核模块处理工具            |
| `scripts/checkpatch.pl` | 内核代码风格检查脚本          |
| `scripts/config`        | 命令行修改 `.config` 的工具 |

常用命令示例：

```bash
# 检查补丁风格
./scripts/checkpatch.pl xxx.patch

# 命令行打开某个配置项
./scripts/config --enable CONFIG_EXAMPLE

# 命令行关闭某个配置项
./scripts/config --disable CONFIG_EXAMPLE
```

## 16. `tools/`、`samples/` 和 `usr/`

这几个目录在驱动开发中也会遇到。

| 路径         | 作用                                    |
|------------|---------------------------------------|
| `tools/`   | 内核相关用户态工具，例如 perf、bpftool、testing 工具等 |
| `samples/` | 内核示例代码，例如 kobject、tracepoint、bpf 示例   |
| `usr/`     | initramfs 相关构建逻辑                      |

其中 `tools/perf/` 是性能分析工具 perf 的源码位置。`samples/` 适合在学习某些内核机制时参考。

## 17. `Kconfig` 和 `Makefile`

Linux 内核的配置和编译离不开 `Kconfig` 和 `Makefile`。

### `Kconfig`

`Kconfig` 用于描述内核配置选项。例如：

```text
config EXAMPLE_DRIVER
    tristate "Example driver"
    depends on PCI
    help
      This is an example driver.
```

常见配置值：

| 值   | 含义      |
|-----|---------|
| `y` | 编译进内核镜像 |
| `m` | 编译成内核模块 |
| `n` | 不编译     |

### `Makefile`

`Makefile` 用于描述源码如何参与编译。例如：

```makefile
obj-$(CONFIG_EXAMPLE_DRIVER) += example.o
```

这表示：如果 `CONFIG_EXAMPLE_DRIVER=y`，则编译进内核；如果为 `m`，则编译成模块；如果为 `n`，则不编译。

阅读驱动时，经常需要同时看源码文件、`Kconfig` 和 `Makefile`，否则不容易搞清楚一个驱动为什么没有被编译出来。

## 18. 常见问题应该从哪里查

下面给出一些常见问题和对应的源码入口。

| 问题类型       | 优先查看目录                                                |
|------------|-------------------------------------------------------|
| ARM64 启动流程 | `arch/arm64/kernel/`、`init/main.c`                    |
| 设备树问题      | `arch/arm64/boot/dts/`、`Documentation/devicetree/`    |
| PCIe 设备枚举  | `drivers/pci/`                                        |
| 网卡驱动问题     | `drivers/net/ethernet/`、`net/core/`                   |
| PHY 识别问题   | `drivers/net/phy/`                                    |
| NVMe 识别问题  | `drivers/nvme/`、`drivers/pci/`、`block/`               |
| 串口输出问题     | `drivers/tty/serial/`                                 |
| 中断问题       | `drivers/irqchip/`、`kernel/irq/`、`arch/arm64/kernel/` |
| 内存管理问题     | `mm/`、`arch/arm64/mm/`                                |
| 文件系统问题     | `fs/`、`block/`                                        |
| 网络协议栈问题    | `net/`、`drivers/net/`                                 |
| 内核模块问题     | `kernel/module.c`、相关驱动目录                              |
| 编译配置问题     | `Kconfig`、`Makefile`、`scripts/`                       |

## 19. 推荐的源码阅读方法

阅读 Linux 内核源码时，不建议从头到尾顺序阅读。更实际的方法是围绕问题阅读。

建议步骤：

1. 先明确问题属于哪个子系统。
2. 根据日志、函数名、驱动名搜索相关源码。
3. 同时查看源码文件、`Kconfig`、`Makefile`。
4. 查阅对应的 `Documentation/` 文档。
5. 使用 `git grep`、`cscope`、`clangd`、`ctags` 等工具辅助跳转。
6. 结合实际运行日志验证理解。

常用搜索命令：

```bash
# 搜索函数或字符串
git grep "start_kernel"

# 搜索配置项
git grep "CONFIG_DWMAC_PHYTIUM"

# 搜索设备树 compatible
git grep "phytium"

# 搜索某个驱动注册入口
git grep "module_platform_driver"
```

## 20. 小结

Linux 内核源码目录虽然庞大，但可以先建立几个核心概念：

1. `arch/` 负责架构相关代码。
2. `drivers/` 负责设备驱动，是嵌入式 Linux 最常看的目录。
3. `fs/` 负责文件系统，`net/` 负责网络协议栈，`mm/` 负责内存管理。
4. `kernel/` 存放调度、中断、进程、模块等核心通用代码。
5. `include/` 存放头文件，其中 `include/uapi/` 是用户空间可见接口。
6. `Kconfig` 决定配置项，`Makefile` 决定编译规则。
7. 阅读内核源码时，应围绕具体问题和日志进行定位，不建议漫无目的地从头读。

对实习生来说，第一阶段不要求记住所有目录，而是要能根据问题快速判断“我应该去哪里找代码”。这就是学习内核源码目录结构的核心目的。
