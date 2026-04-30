# 04-procfs-sysfs-debugfs基础

## 1. 文档目标

本文用于说明 Linux 内核中常见的三个虚拟文件系统：

1. `procfs`
2. `sysfs`
3. `debugfs`

学习完成后，应能够回答以下问题：

1. `/proc`、`/sys`、`/sys/kernel/debug` 分别是什么？
2. 为什么这些目录里的文件很多不是普通磁盘文件？
3. 开发和调试驱动时，应该优先看哪些路径？
4. `procfs`、`sysfs`、`debugfs` 的使用边界是什么？
5. 为什么不应该把正式功能接口随便放到 `debugfs`？

## 2. 三者的基本区别

`procfs`、`sysfs`、`debugfs` 都可以通过文件路径暴露内核信息，但它们的定位不同。

| 文件系统 | 常见挂载点 | 主要用途 |
| --- | --- | --- |
| `procfs` | `/proc` | 查看进程信息和部分内核运行状态 |
| `sysfs` | `/sys` | 查看和管理设备、驱动、总线、类等内核对象 |
| `debugfs` | `/sys/kernel/debug` | 提供调试用接口，辅助内核和驱动开发 |

简单理解：

1. `/proc` 更偏向进程和系统运行状态
2. `/sys` 更偏向设备模型和硬件资源
3. `/sys/kernel/debug` 更偏向开发调试

## 3. 虚拟文件系统的含义

这些目录中的很多文件并不是磁盘上真实存在的普通文件，而是内核动态生成的接口。

例如：

```bash
cat /proc/cpuinfo
cat /proc/meminfo
cat /sys/class/net
cat /sys/kernel/debug/gpio
```

这些文件的内容通常来自内核中的数据结构。

当用户执行 `cat`、`echo`、`ls` 等命令时，实际上是在通过文件系统接口和内核交互。

这也是 Linux 常说的思想之一：

```text
Everything is a file.
```

但是要注意：

这些“文件”不一定真的占用磁盘空间，它们更多是内核暴露出来的访问入口。

## 4. procfs 基础

`procfs` 通常挂载在：

```text
/proc
```

它最初主要用于暴露进程信息，所以叫 process filesystem。

现在 `/proc` 中也包含不少系统级信息。

## 5. /proc 中常见内容

常见路径如下：

| 路径 | 说明 |
| --- | --- |
| `/proc/cpuinfo` | CPU 信息 |
| `/proc/meminfo` | 内存信息 |
| `/proc/cmdline` | 内核启动参数 |
| `/proc/interrupts` | 中断统计 |
| `/proc/iomem` | 物理内存和 MMIO 资源分布 |
| `/proc/ioports` | I/O 端口资源，常见于 x86 |
| `/proc/modules` | 已加载模块 |
| `/proc/devices` | 已注册的字符设备和块设备主设备号 |
| `/proc/filesystems` | 当前支持的文件系统 |
| `/proc/mounts` | 当前挂载信息 |
| `/proc/version` | 内核版本信息 |

开发板调试中经常使用：

```bash
cat /proc/cmdline
cat /proc/interrupts
cat /proc/iomem
cat /proc/modules
cat /proc/devices
```

## 6. /proc/<pid> 进程目录

`/proc` 中有很多数字目录，例如：

```text
/proc/1
/proc/1234
```

这些数字表示进程 PID。

常见文件如下：

| 路径 | 说明 |
| --- | --- |
| `/proc/<pid>/cmdline` | 进程启动命令 |
| `/proc/<pid>/status` | 进程状态 |
| `/proc/<pid>/maps` | 进程虚拟地址空间映射 |
| `/proc/<pid>/fd/` | 进程打开的文件描述符 |
| `/proc/<pid>/exe` | 进程可执行文件链接 |
| `/proc/<pid>/cwd` | 进程当前工作目录 |

示例：

```bash
cat /proc/1/status
ls -l /proc/1/fd
cat /proc/1/maps
```

这些信息在分析进程资源占用、文件句柄、内存映射时很有用。

## 7. /proc/cmdline

`/proc/cmdline` 用于查看当前系统实际使用的内核启动参数。

命令：

```bash
cat /proc/cmdline
```

常见内容可能包括：

```text
console=ttyAMA1,115200 root=/dev/nvme0n1p2 rootfstype=ext4 rw rootwait loglevel=8
```

调试启动问题时，必须确认：

1. 当前 rootfs 是哪个分区
2. 当前 console 参数是否正确
3. 是否启用了调试参数
4. 是否设置了 `nr_cpus`、`maxcpus`、`nosmp` 等限制参数

不要只看 U-Boot 里以为设置了什么，要进入 Linux 后用 `/proc/cmdline` 确认实际生效的启动参数。

## 8. /proc/interrupts

`/proc/interrupts` 用于查看中断统计。

命令：

```bash
cat /proc/interrupts
```

它可以帮助判断：

1. 某个设备是否产生中断
2. 中断是否被绑定到某些 CPU
3. 中断计数是否持续增长
4. 驱动是否成功申请 IRQ

例如调试网卡、串口、NVMe、PCIe 设备时，经常需要观察中断计数是否变化。

常用方法：

```bash
watch -n 1 cat /proc/interrupts
```

如果设备工作时中断计数完全不变，可能需要检查：

1. 设备树中的 interrupt 配置
2. 驱动是否 request_irq 成功
3. 中断控制器配置
4. 硬件连线或 PCIe MSI/MSI-X 配置

## 9. /proc/iomem

`/proc/iomem` 用于查看系统物理地址资源分布。

命令：

```bash
cat /proc/iomem
```

它常用于确认：

1. DRAM 地址范围
2. MMIO 设备地址范围
3. PCIe BAR 映射范围
4. reserved memory 区域
5. 内核代码、数据所在物理区域

在调试设备树和 MMIO 时，`/proc/iomem` 非常重要。

例如，如果设备树里写了某个设备的寄存器基地址，可以通过 `/proc/iomem` 观察该地址范围是否被内核识别和保留。

## 10. sysfs 基础

`sysfs` 通常挂载在：

```text
/sys
```

它主要用于把 Linux 内核中的设备模型导出到用户空间。

Linux 设备模型中有几个核心概念：

1. device
2. driver
3. bus
4. class
5. subsystem

`sysfs` 可以帮助我们从用户空间观察这些对象之间的关系。

## 11. /sys 中常见目录

常见路径如下：

| 路径 | 说明 |
| --- | --- |
| `/sys/devices/` | 按设备拓扑组织的设备树 |
| `/sys/bus/` | 按总线类型组织的设备和驱动 |
| `/sys/class/` | 按设备类别组织的接口 |
| `/sys/module/` | 内核模块信息 |
| `/sys/firmware/` | 固件相关信息，例如设备树、ACPI |
| `/sys/kernel/` | 内核子系统相关接口 |
| `/sys/block/` | 块设备 |
| `/sys/fs/` | 文件系统相关接口 |

简单理解：

1. `/sys/devices` 更接近设备真实层级
2. `/sys/bus` 更适合看设备挂在哪种总线上
3. `/sys/class` 更适合按功能类别查设备
4. `/sys/module` 更适合查模块参数和模块状态

## 12. /sys/class 示例

`/sys/class` 按设备类别组织。

例如查看网卡：

```bash
ls /sys/class/net
```

可能看到：

```text
eth0
end0
end1
lo
```

查看网卡状态：

```bash
cat /sys/class/net/end0/operstate
cat /sys/class/net/end0/address
cat /sys/class/net/end0/mtu
```

常见类别：

| 路径 | 说明 |
| --- | --- |
| `/sys/class/net` | 网络设备 |
| `/sys/class/gpio` | GPIO 旧接口 |
| `/sys/class/tty` | 串口和终端设备 |
| `/sys/class/block` | 块设备 |
| `/sys/class/leds` | LED 设备 |
| `/sys/class/hwmon` | 硬件监控设备 |
| `/sys/class/input` | 输入设备 |

## 13. /sys/bus 示例

`/sys/bus` 按总线类型组织设备和驱动。

常见路径：

```bash
ls /sys/bus
```

可能包括：

```text
pci
platform
usb
i2c
spi
mdio_bus
```

以 platform 设备为例：

```bash
ls /sys/bus/platform/devices
ls /sys/bus/platform/drivers
```

以 PCI 设备为例：

```bash
ls /sys/bus/pci/devices
ls /sys/bus/pci/drivers
```

这些目录可以帮助判断：

1. 设备是否被内核枚举出来
2. 设备是否绑定到了正确驱动
3. 当前有哪些驱动注册到了某个总线
4. 某个设备的资源和属性是什么

## 14. /sys/bus/pci/devices

PCIe 设备通常可以在这里查看：

```bash
ls /sys/bus/pci/devices
```

设备名通常类似：

```text
0000:01:00.0
```

其中包含 domain、bus、device、function 信息。

查看某个 PCIe 设备：

```bash
cd /sys/bus/pci/devices/0000:01:00.0
ls
```

常见文件：

| 文件 | 说明 |
| --- | --- |
| `vendor` | Vendor ID |
| `device` | Device ID |
| `class` | 设备类别 |
| `resource` | BAR 等资源信息 |
| `driver` | 当前绑定的驱动链接 |
| `irq` | 使用的中断号 |
| `enable` | 设备使能状态 |

示例：

```bash
cat vendor
cat device
cat class
cat resource
cat irq
```

调试 PCIe 设备时，`/sys/bus/pci/devices` 是非常关键的入口。

## 15. /sys/firmware/devicetree

如果系统通过 Device Tree 启动，通常可以在这里看到运行时设备树：

```bash
ls /sys/firmware/devicetree/base
```

常用命令：

```bash
find /sys/firmware/devicetree/base -name compatible
find /sys/firmware/devicetree/base -name status
```

查看某个节点的 compatible：

```bash
cat /sys/firmware/devicetree/base/soc/xxx/compatible
```

注意：

有些属性是二进制数据，直接 `cat` 可能显示不友好。

可以使用：

```bash
hexdump -C <file>
```

或：

```bash
xxd <file>
```

这个目录可以帮助确认：

1. Linux 实际拿到的设备树是什么
2. 某个节点是否存在
3. 某个节点的 `status` 是否为 `okay`
4. `compatible` 是否和驱动匹配
5. `reg`、`interrupts` 等属性是否符合预期

## 16. /sys/module

`/sys/module` 用于查看内核模块和部分内建模块的信息。

命令：

```bash
ls /sys/module
```

查看某个模块：

```bash
ls /sys/module/<module_name>
```

常见内容：

| 路径 | 说明 |
| --- | --- |
| `/sys/module/<name>/parameters` | 模块参数 |
| `/sys/module/<name>/holders` | 依赖该模块的其他模块 |
| `/sys/module/<name>/drivers` | 相关驱动 |
| `/sys/module/<name>/refcnt` | 模块引用计数 |

如果模块提供了参数，可以这样查看：

```bash
ls /sys/module/<module_name>/parameters
cat /sys/module/<module_name>/parameters/<param>
```

有些参数也可以通过 `echo` 修改，但是否允许修改取决于模块参数权限。

## 17. sysfs 中的读写操作

`sysfs` 中很多文件可以读，有些文件可以写。

读取示例：

```bash
cat /sys/class/net/end0/operstate
```

写入示例：

```bash
echo 1 | sudo tee /sys/bus/pci/devices/0000:01:00.0/enable
```

注意：

1. 不是所有 sysfs 文件都能写
2. 能写也不代表可以随便写
3. 写错可能导致设备状态异常
4. 对硬件控制类接口写入前必须理解含义

对于初学者，建议先以读取和观察为主。

## 18. debugfs 基础

`debugfs` 通常挂载在：

```text
/sys/kernel/debug
```

它主要用于内核调试，不保证接口稳定，不适合作为正式用户空间 ABI。

查看是否已经挂载：

```bash
mount | grep debugfs
```

如果没有挂载，可以执行：

```bash
sudo mount -t debugfs none /sys/kernel/debug
```

有些系统默认已经挂载，有些嵌入式系统需要手动挂载。

## 19. debugfs 常见用途

`debugfs` 常用于：

1. 查看内核调试信息
2. 查看驱动内部状态
3. 暴露临时调试开关
4. 调试 GPIO、时钟、中断、regmap 等子系统
5. 辅助驱动开发阶段定位问题

常见路径可能包括：

| 路径 | 说明 |
| --- | --- |
| `/sys/kernel/debug/gpio` | GPIO 状态 |
| `/sys/kernel/debug/clk/` | 时钟树信息 |
| `/sys/kernel/debug/pinctrl/` | pinctrl 状态 |
| `/sys/kernel/debug/regmap/` | regmap 设备寄存器访问情况 |
| `/sys/kernel/debug/tracing/` | ftrace 跟踪接口 |
| `/sys/kernel/debug/dynamic_debug/` | dynamic debug 控制 |

不同内核配置和平台下，debugfs 中的内容会有差异。

## 20. 查看 GPIO 调试信息

如果内核启用了相关配置，可以查看：

```bash
cat /sys/kernel/debug/gpio
```

它可以帮助判断：

1. 当前有哪些 GPIO controller
2. 某个 GPIO 是否被占用
3. GPIO 方向是 input 还是 output
4. GPIO 当前电平状态
5. GPIO 被哪个驱动申请

调试外设上电、复位脚、中断脚时，这个文件经常很有用。

## 21. 查看时钟树

如果平台支持，可以查看：

```bash
ls /sys/kernel/debug/clk
cat /sys/kernel/debug/clk/clk_summary
```

`clk_summary` 可以帮助判断：

1. 某个时钟是否存在
2. 某个时钟是否被使能
3. 当前时钟频率是多少
4. 时钟父子关系是否符合预期

调试串口、网卡、I2C、SPI、显示等设备时，时钟问题很常见。

## 22. ftrace 简单入口

`ftrace` 的接口通常也在 debugfs 下：

```bash
/sys/kernel/debug/tracing
```

常见文件：

| 文件 | 说明 |
| --- | --- |
| `available_tracers` | 可用 tracer |
| `current_tracer` | 当前 tracer |
| `trace` | 跟踪结果 |
| `trace_pipe` | 实时跟踪输出 |
| `set_ftrace_filter` | 函数过滤 |
| `tracing_on` | 开关跟踪 |

示例：

```bash
cd /sys/kernel/debug/tracing
cat available_tracers
cat current_tracer
```

ftrace 是更高级的内核调试工具，入门阶段先知道入口即可，后续可以单独学习。

## 23. dynamic debug 简单入口

dynamic debug 可以动态控制某些 `pr_debug()`、`dev_dbg()` 日志是否输出。

入口通常是：

```bash
/sys/kernel/debug/dynamic_debug/control
```

查看：

```bash
cat /sys/kernel/debug/dynamic_debug/control | head
```

按文件打开调试日志的示例：

```bash
echo 'file drivers/net/ethernet/xxx/yyy.c +p' | sudo tee /sys/kernel/debug/dynamic_debug/control
```

说明：

1. `+p` 表示打开打印
2. `-p` 表示关闭打印
3. 具体是否可用取决于内核配置和代码写法

初学阶段不要求熟练掌握，但需要知道：有些 `dev_dbg()` 日志不是改代码才能打开，可以通过 dynamic debug 动态开启。

## 24. 三者使用边界

三者虽然都表现为文件接口，但使用边界不同。

| 文件系统 | 适合做什么 | 不适合做什么 |
| --- | --- | --- |
| `procfs` | 进程信息、系统运行状态 | 新驱动的设备属性接口 |
| `sysfs` | 设备、驱动、总线、类的稳定属性 | 大块数据传输、复杂协议 |
| `debugfs` | 临时调试信息、开发阶段排查 | 稳定产品接口、正式用户 ABI |

简单建议：

1. 查看进程和内核状态，先看 `/proc`
2. 查看设备和驱动关系，先看 `/sys`
3. 调试驱动内部状态，再看 `/sys/kernel/debug`
4. 不要把正式业务接口设计在 `debugfs`
5. 不要随便依赖 debugfs 文件作为长期稳定接口

## 25. 开发板调试常用组合

调试开发板时，可以按以下顺序收集信息。

### 25.1 基本系统信息

```bash
uname -a
cat /proc/cmdline
cat /proc/meminfo
cat /proc/cpuinfo
```

### 25.2 中断和内存资源

```bash
cat /proc/interrupts
cat /proc/iomem
```

### 25.3 模块和设备

```bash
lsmod
cat /proc/modules
ls /sys/bus/platform/devices
ls /sys/bus/pci/devices
ls /sys/class/net
```

### 25.4 设备树

```bash
ls /sys/firmware/devicetree/base
find /sys/firmware/devicetree/base -name compatible
```

### 25.5 调试接口

```bash
mount | grep debugfs
ls /sys/kernel/debug
cat /sys/kernel/debug/gpio
```

## 26. 网卡调试示例

如果网卡不工作，可以按以下步骤观察。

### 26.1 看网卡是否出现

```bash
ip link
ls /sys/class/net
```

### 26.2 看内核日志

```bash
dmesg | grep -i "eth\|phy\|stmmac\|link"
```

### 26.3 看设备是否在总线上

platform 网卡：

```bash
ls /sys/bus/platform/devices
```

PCIe 网卡：

```bash
ls /sys/bus/pci/devices
```

### 26.4 看中断是否变化

```bash
watch -n 1 cat /proc/interrupts
```

### 26.5 看设备树实际内容

```bash
find /sys/firmware/devicetree/base -iname '*eth*'
find /sys/firmware/devicetree/base -iname '*ethernet*'
```

这个过程体现了 `/proc`、`/sys`、`debugfs` 的组合使用。

## 27. PCIe 调试示例

如果 PCIe 设备没有正常工作，可以先查看：

```bash
lspci
ls /sys/bus/pci/devices
dmesg | grep -i pci
cat /proc/iomem
cat /proc/interrupts
```

如果某个设备已经出现，例如：

```text
0000:01:00.0
```

可以进一步查看：

```bash
cd /sys/bus/pci/devices/0000:01:00.0
cat vendor
cat device
cat class
cat resource
cat irq
ls -l driver
```

这些信息可以帮助判断：

1. 设备是否被枚举
2. BAR 是否分配资源
3. 中断是否分配
4. 驱动是否绑定
5. 设备类型是否识别正确

## 28. 注意事项

使用这些接口时需要注意：

1. `/proc`、`/sys`、`debugfs` 很多文件不是普通磁盘文件
2. 不要随便向不了解的节点写入数据
3. `debugfs` 不保证接口稳定
4. 不同内核版本下路径和内容可能有差异
5. 是否存在某个 debugfs 节点取决于内核配置
6. 有些文件内容是二进制，不能直接按字符串理解
7. 调试时要同时结合 `dmesg` 和源码分析

## 29. 推荐练习

建议完成以下练习：

1. 查看 `/proc/cmdline`，确认当前系统启动参数
2. 查看 `/proc/interrupts`，观察中断计数变化
3. 查看 `/proc/iomem`，找出系统 DRAM 和 MMIO 范围
4. 查看 `/sys/class/net`，找到当前网卡设备
5. 查看 `/sys/bus/platform/devices`，理解 platform 设备列表
6. 查看 `/sys/bus/pci/devices`，理解 PCIe 设备命名
7. 查看 `/sys/module`，找到一个已加载模块的信息
8. 挂载 debugfs，并查看 `/sys/kernel/debug`
9. 如果平台支持，查看 `/sys/kernel/debug/gpio`
10. 如果平台支持，查看 `/sys/kernel/debug/clk/clk_summary`

## 30. 小结

本文介绍了 `procfs`、`sysfs`、`debugfs` 的基础概念和常见用法。

需要重点掌握：

1. `/proc` 主要用于查看进程和内核运行状态
2. `/sys` 主要用于查看设备、驱动、总线和类
3. `/sys/kernel/debug` 主要用于内核和驱动调试
4. `/proc/cmdline` 可以确认实际启动参数
5. `/proc/interrupts` 可以观察中断情况
6. `/proc/iomem` 可以查看物理地址资源分布
7. `/sys/bus` 可以观察设备和驱动绑定关系
8. `/sys/class` 可以按设备类别查找接口
9. `debugfs` 适合调试，但不适合做稳定用户接口

对 Linux 驱动开发来说，源码分析很重要，但现场排查时更应该先学会看系统暴露出来的运行状态。`procfs`、`sysfs`、`debugfs` 就是观察内核运行状态的三扇窗口。
