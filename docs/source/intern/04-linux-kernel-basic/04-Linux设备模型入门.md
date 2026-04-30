# 04-Linux设备模型入门

## 1. 文档目标

本文用于说明 Linux 设备模型的基础概念，帮助初学者理解 Linux 内核如何组织设备、驱动、总线和设备类别。

学习完成后，应能够回答以下问题：

1. Linux 内核为什么需要设备模型？
2. `device`、`driver`、`bus`、`class` 分别是什么？
3. 设备和驱动是如何匹配的？
4. `platform_device` 和 `platform_driver` 是什么？
5. `/sys` 目录为什么能反映设备、驱动和总线关系？
6. 后续学习设备树和驱动开发时，设备模型有什么作用？

## 2. 为什么需要 Linux 设备模型

Linux 内核需要管理大量硬件设备，例如：

1. 串口
2. 网卡
3. I2C 控制器
4. SPI 控制器
5. GPIO 控制器
6. PCIe 设备
7. USB 设备
8. NVMe 磁盘
9. 显示设备
10. 音频设备

如果每个驱动都用自己的方式管理设备，内核会非常混乱。

所以 Linux 内核抽象出一套统一的设备模型，用来描述：

1. 系统中有哪些设备
2. 系统中有哪些驱动
3. 设备挂在哪种总线上
4. 哪个驱动负责哪个设备
5. 设备之间有什么父子关系
6. 用户空间如何查看设备信息

简单理解：

Linux 设备模型就是内核管理硬件设备和驱动关系的一套统一框架。

## 3. 设备模型中的几个核心对象

Linux 设备模型中最核心的几个概念是：

| 概念 | 含义 |
| --- | --- |
| `device` | 表示一个具体设备 |
| `driver` | 表示一个驱动程序 |
| `bus` | 表示设备和驱动匹配的通道 |
| `class` | 表示按功能分类后的设备类别 |
| `subsystem` | 表示某一类内核子系统 |

简单理解：

1. `device` 是“硬件对象”
2. `driver` 是“控制硬件的软件”
3. `bus` 负责把 device 和 driver 匹配起来
4. `class` 负责把设备按功能暴露给用户空间

## 4. device：设备对象

`device` 用来表示内核中的一个具体设备。

例如：

1. 一个 UART 控制器
2. 一个 I2C 控制器
3. 一个 SPI flash
4. 一个 PCIe 网卡
5. 一个 USB 鼠标
6. 一个 GPIO 控制器

在内核中，很多设备结构体内部都会包含一个通用的 `struct device`。

例如：

```c
struct platform_device {
    const char *name;
    int id;
    struct device dev;
    u32 num_resources;
    struct resource *resource;
};
```

其中的 `dev` 字段就是通用设备模型的一部分。

这说明：不同类型的设备可以有自己的专用结构体，但最终会嵌入统一的 `struct device`，从而接入 Linux 设备模型。

## 5. driver：驱动对象

`driver` 用来表示一个驱动程序。

驱动的职责通常包括：

1. 识别自己支持的设备
2. 初始化硬件
3. 申请内存、中断、时钟、GPIO 等资源
4. 注册字符设备、网卡、块设备等接口
5. 提供读写、控制、收发等操作
6. 在设备移除时释放资源

在 platform 驱动中，常见结构体是：

```c
struct platform_driver {
    int (*probe)(struct platform_device *);
    int (*remove)(struct platform_device *);
    struct device_driver driver;
    const struct platform_device_id *id_table;
};
```

其中：

| 成员 | 说明 |
| --- | --- |
| `probe` | 设备和驱动匹配成功后调用 |
| `remove` | 设备移除或驱动卸载时调用 |
| `driver` | 通用驱动模型对象 |
| `id_table` | 用于匹配 platform 设备 |

对于初学者来说，最重要的是记住：

驱动不是自己随便运行的，而是注册到内核后，等待内核设备模型把合适的设备匹配给它。

## 6. bus：总线对象

`bus` 是设备和驱动之间的匹配通道。

常见总线包括：

| 总线 | 说明 |
| --- | --- |
| `platform` | 片上 SoC 设备常用的虚拟总线 |
| `pci` | PCI/PCIe 设备 |
| `usb` | USB 设备 |
| `i2c` | I2C 设备 |
| `spi` | SPI 设备 |
| `mdio_bus` | 以太网 PHY 常用 |
| `serio` | 输入设备相关 |
| `amba` | ARM AMBA 总线设备 |

每种总线通常都有自己的匹配规则。

例如：

1. PCIe 设备根据 Vendor ID、Device ID 等信息匹配驱动
2. USB 设备根据 Vendor ID、Product ID、Class 等信息匹配驱动
3. Device Tree 描述的 platform 设备常根据 `compatible` 字符串匹配驱动
4. I2C 设备可以根据设备名或 `compatible` 匹配驱动
5. SPI 设备也可以根据设备名或 `compatible` 匹配驱动

简单理解：

总线负责回答一个问题：

```text
这个设备应该交给哪个驱动？
```

## 7. class：设备类别

`class` 用来按功能类别组织设备。

例如：

| class 路径 | 说明 |
| --- | --- |
| `/sys/class/net` | 网络设备 |
| `/sys/class/block` | 块设备 |
| `/sys/class/tty` | 串口和终端设备 |
| `/sys/class/input` | 输入设备 |
| `/sys/class/gpio` | GPIO 旧接口 |
| `/sys/class/leds` | LED 设备 |
| `/sys/class/hwmon` | 硬件监控设备 |

`class` 更接近用户空间看到的功能接口。

例如一个网卡设备，从总线角度看，它可能是 PCIe 设备，也可能是 platform 设备；但从用户空间角度看，它最终通常都会出现在：

```bash
/sys/class/net
```

并且可以通过：

```bash
ip link
```

看到对应网络接口。

所以：

1. `bus` 更关注设备从哪里来、如何匹配驱动
2. `class` 更关注设备对用户空间表现为什么功能

## 8. device、driver、bus、class 的关系

可以用下面的关系理解：

```text
device  ----挂在某个 bus 上---->  bus  <----注册到某个 bus----  driver

device  ----按功能分类后---->  class
```

更直观地说：

1. 设备先被内核发现或创建
2. 设备挂到某一种 bus 上
3. 驱动也注册到同一种 bus 上
4. bus 使用自己的匹配规则寻找合适的 driver
5. 匹配成功后调用 driver 的 `probe()`
6. 驱动初始化成功后，可能向某个 class 注册用户可见接口

例如网卡：

```text
PCIe 网卡设备
    -> 挂到 pci bus
    -> pci bus 匹配网卡驱动
    -> 驱动 probe
    -> 注册 net_device
    -> 用户在 /sys/class/net 和 ip link 中看到网卡
```

## 9. probe 函数的意义

`probe()` 是驱动开发中非常重要的函数。

它表示：

```text
设备和驱动匹配成功，现在驱动开始初始化这个设备。
```

`probe()` 中通常会做：

1. 获取设备资源
2. 映射寄存器
3. 申请中断
4. 获取时钟
5. 获取 reset 控制
6. 获取 GPIO
7. 初始化硬件
8. 注册子系统接口
9. 打印设备初始化日志

以 platform 驱动为例：

```c
static int sample_probe(struct platform_device *pdev)
{
    pr_info("sample device probed\n");
    return 0;
}
```

如果 `probe()` 没有被调用，通常说明：

1. 设备没有被创建出来
2. 驱动没有注册成功
3. 设备和驱动匹配失败
4. 设备树 `compatible` 不匹配
5. 设备节点 `status` 不是 `okay`
6. 相关总线或子系统没有启用

## 10. remove 函数的意义

`remove()` 表示设备移除或驱动卸载时的清理函数。

常见工作包括：

1. 释放中断
2. 注销字符设备、网卡或其他接口
3. 释放 DMA buffer
4. 关闭时钟
5. 释放 GPIO
6. 解除资源映射
7. 清理驱动私有数据

示例：

```c
static int sample_remove(struct platform_device *pdev)
{
    pr_info("sample device removed\n");
    return 0;
}
```

简单理解：

`probe()` 负责申请资源和初始化设备。

`remove()` 负责释放资源和清理现场。

## 11. platform 总线的意义

`platform` 总线是一种虚拟总线，经常用于 SoC 内部设备。

很多片上设备并不是通过 PCIe、USB 这类可以自动枚举的总线发现的，而是由固件或设备树描述出来。

例如：

1. UART 控制器
2. GPIO 控制器
3. I2C 控制器
4. SPI 控制器
5. Ethernet MAC
6. DMA 控制器
7. Watchdog
8. Timer

这些设备通常会注册为 `platform_device`，对应驱动注册为 `platform_driver`。

简单理解：

platform 总线主要用于管理那些不能自动枚举、需要固件描述的片上设备。

## 12. platform_device

`platform_device` 表示 platform 总线上的一个设备。

它通常包含：

1. 设备名称
2. 设备资源
3. MMIO 寄存器范围
4. IRQ 中断号
5. DMA 信息
6. 设备私有数据
7. 通用 `struct device`

简化理解：

```text
platform_device = 一个被内核知道的片上设备对象
```

设备可能来自：

1. 板级 C 代码注册
2. Device Tree 创建
3. ACPI 描述
4. MFD 等其他子系统创建

在现代 ARM64 嵌入式系统中，很多 platform 设备来自 Device Tree。

## 13. platform_driver

`platform_driver` 表示 platform 总线上的驱动。

典型写法：

```c
static const struct of_device_id sample_of_match[] = {
    { .compatible = "vendor,sample-device" },
    { }
};
MODULE_DEVICE_TABLE(of, sample_of_match);

static struct platform_driver sample_driver = {
    .probe = sample_probe,
    .remove = sample_remove,
    .driver = {
        .name = "sample-driver",
        .of_match_table = sample_of_match,
    },
};

module_platform_driver(sample_driver);
```

这段代码表达的意思是：

1. 驱动支持 `compatible = "vendor,sample-device"` 的设备
2. 驱动注册到 platform 总线
3. 如果系统中有匹配的 platform 设备，就调用 `sample_probe()`
4. 模块卸载或设备移除时调用 `sample_remove()`

## 14. Device Tree 与设备模型的关系

在 ARM64 开发板中，Device Tree 常用于描述硬件。

例如设备树中有一个节点：

```dts
sample@10000000 {
    compatible = "vendor,sample-device";
    reg = <0x0 0x10000000 0x0 0x1000>;
    interrupts = <0 32 4>;
    status = "okay";
};
```

内核启动时会解析设备树，并为这个节点创建对应的设备对象。

如果驱动中有：

```c
static const struct of_device_id sample_of_match[] = {
    { .compatible = "vendor,sample-device" },
    { }
};
```

那么 platform 总线会发现：

```text
设备树节点 compatible 和驱动 of_match_table 匹配
```

于是调用驱动的 `probe()` 函数。

这就是设备树和驱动匹配的基本过程。

## 15. 设备和驱动匹配的常见方式

不同总线有不同匹配方式。

| 总线 | 常见匹配依据 |
| --- | --- |
| `platform` | 设备名、`compatible` |
| `pci` | Vendor ID、Device ID、Class |
| `usb` | Vendor ID、Product ID、Class |
| `i2c` | 设备名、`compatible` |
| `spi` | 设备名、`compatible` |
| `mdio_bus` | PHY ID、compatible |

例如 PCIe 设备驱动中常见：

```c
static const struct pci_device_id sample_pci_ids[] = {
    { PCI_DEVICE(0x1234, 0x5678) },
    { }
};
```

例如 USB 设备驱动中常见：

```c
static const struct usb_device_id sample_usb_ids[] = {
    { USB_DEVICE(0x1234, 0x5678) },
    { }
};
```

例如 platform 设备驱动中常见：

```c
static const struct of_device_id sample_of_match[] = {
    { .compatible = "vendor,sample-device" },
    { }
};
```

所以阅读驱动时，要先判断它属于哪种总线，再看对应的匹配表。

## 16. sysfs 与设备模型的关系

`sysfs` 是设备模型在用户空间的体现。

常见路径包括：

```bash
/sys/devices
/sys/bus
/sys/class
/sys/module
```

它们分别对应设备模型中的不同视角。

| 路径 | 说明 |
| --- | --- |
| `/sys/devices` | 按真实设备层级组织 |
| `/sys/bus` | 按总线类型组织 |
| `/sys/class` | 按功能类别组织 |
| `/sys/module` | 按模块组织 |

例如查看 platform 设备：

```bash
ls /sys/bus/platform/devices
```

查看 platform 驱动：

```bash
ls /sys/bus/platform/drivers
```

查看 PCIe 设备：

```bash
ls /sys/bus/pci/devices
```

查看网络设备：

```bash
ls /sys/class/net
```

如果驱动已经绑定到设备，通常可以在设备目录下看到 `driver` 链接。

## 17. 如何判断设备是否绑定驱动

以 PCIe 设备为例：

```bash
cd /sys/bus/pci/devices/0000:01:00.0
ls -l driver
```

如果存在 `driver` 符号链接，说明设备已经绑定到某个驱动。

也可以查看：

```bash
readlink driver
```

对于 platform 设备，可以类似查看：

```bash
cd /sys/bus/platform/devices/<device-name>
ls -l driver
```

如果没有 `driver` 链接，可能说明：

1. 没有匹配到驱动
2. 驱动没有编译进内核或没有加载
3. 匹配表不正确
4. 设备树 compatible 不正确
5. 设备节点没有被创建
6. 驱动 probe 失败后解绑

## 18. 设备模型与驱动开发的基本流程

写一个典型 platform 驱动时，大致流程如下：

1. 在设备树中描述设备节点
2. 在驱动中写 `of_device_id` 匹配表
3. 定义 `platform_driver`
4. 编写 `probe()` 函数
5. 在 `probe()` 中获取资源
6. 初始化硬件
7. 注册对外接口
8. 编译驱动
9. 启动系统或加载模块
10. 查看 `dmesg` 和 `/sys` 确认是否匹配成功

其中，最关键的是：

```text
设备树 compatible 要和驱动 of_match_table 对得上。
```

如果匹配不上，`probe()` 就不会执行。

## 19. 常见资源获取接口

在 `probe()` 中，驱动经常需要获取硬件资源。

常见接口如下：

| 接口 | 作用 |
| --- | --- |
| `platform_get_resource()` | 获取 memory、IRQ 等资源 |
| `devm_ioremap_resource()` | 映射 MMIO 寄存器 |
| `platform_get_irq()` | 获取中断号 |
| `devm_request_irq()` | 申请中断 |
| `devm_clk_get()` | 获取时钟 |
| `devm_reset_control_get()` | 获取 reset 控制 |
| `devm_gpiod_get()` | 获取 GPIO |
| `dev_get_drvdata()` | 获取驱动私有数据 |
| `dev_set_drvdata()` | 保存驱动私有数据 |

其中 `devm_` 前缀表示 device managed resource，也就是资源和设备生命周期绑定。

简单理解：

使用 `devm_` 接口申请的资源，在设备解绑时通常会自动释放，可以减少手动清理错误。

## 20. devm 资源管理简介

在驱动开发中，经常会看到这样的代码：

```c
base = devm_ioremap_resource(&pdev->dev, res);
irq = platform_get_irq(pdev, 0);
ret = devm_request_irq(&pdev->dev, irq, handler, 0, "sample", data);
```

这里的 `devm_` 表示资源由设备管理。

优点：

1. 错误路径更简单
2. remove 时更不容易漏释放
3. 驱动代码更清晰
4. 适合大多数 platform 驱动

但是要注意：

`devm_` 不是万能的。某些资源仍然需要开发者按子系统要求主动注销，例如：

1. 注册的字符设备
2. 注册的 net_device
3. 创建的工作队列
4. 启动的线程
5. 某些异步任务

## 21. 从 dmesg 观察设备模型

设备和驱动匹配时，通常可以从 `dmesg` 看到相关信息。

常用命令：

```bash
dmesg | grep -i probe
dmesg | grep -i platform
dmesg | grep -i pci
dmesg | grep -i "fail\|error\|defer"
```

常见关键词：

| 关键词 | 含义 |
| --- | --- |
| `probe` | 驱动探测 |
| `deferred probe` | 延迟探测 |
| `failed` | 初始化失败 |
| `resource` | 资源相关 |
| `irq` | 中断相关 |
| `clock` | 时钟相关 |
| `reset` | reset 控制相关 |

如果看到 deferred probe，通常说明驱动依赖的资源暂时还没准备好，例如时钟、GPIO、regulator 等 provider 还没有注册完成。

## 22. deferred probe 简介

`deferred probe` 表示驱动暂时无法完成初始化，请求内核稍后再试。

常见原因包括：

1. 依赖的 clock provider 还没初始化
2. 依赖的 regulator 还没初始化
3. 依赖的 GPIO controller 还没初始化
4. 依赖的 PHY 或 reset controller 还没初始化
5. 设备初始化顺序暂时不满足

简单理解：

```text
不是驱动永远失败，而是当前依赖条件还没准备好。
```

但是如果依赖一直不存在，设备最终可能一直无法正常 probe。

排查时可以看：

```bash
dmesg | grep -i defer
```

有些内核还提供 deferred devices 信息，例如：

```bash
cat /sys/kernel/debug/devices_deferred
```

具体路径取决于内核配置。

## 23. 设备模型常见排查路径

如果一个设备驱动没有工作，可以按以下顺序排查。

### 23.1 看设备是否存在

```bash
ls /sys/bus/platform/devices
ls /sys/bus/pci/devices
```

如果设备不存在，重点检查：

1. 设备树节点是否存在
2. `status` 是否为 `okay`
3. 总线枚举是否成功
4. 内核配置是否启用相关子系统

### 23.2 看驱动是否存在

```bash
ls /sys/bus/platform/drivers
ls /sys/bus/pci/drivers
lsmod
```

如果驱动不存在，重点检查：

1. 驱动是否编译进内核
2. 驱动是否编译成模块但没有加载
3. `CONFIG_XXX` 是否启用
4. Makefile 是否把源码编译进去了

### 23.3 看设备是否绑定驱动

```bash
ls -l /sys/bus/platform/devices/<device>/driver
ls -l /sys/bus/pci/devices/<bdf>/driver
```

如果没有绑定，重点检查：

1. 匹配表是否正确
2. `compatible` 是否一致
3. PCI/USB ID 是否匹配
4. 驱动是否支持该设备
5. 是否 probe 失败

### 23.4 看 probe 日志

```bash
dmesg | grep -i "probe\|fail\|error\|defer"
```

如果 probe 失败，重点检查：

1. `reg` 地址是否正确
2. `interrupts` 是否正确
3. clock 是否准备好
4. reset 是否准备好
5. GPIO 是否配置正确
6. PHY 是否匹配
7. 内核配置是否缺少依赖项

## 24. 示例：platform 驱动匹配过程

假设设备树有：

```dts
demo@10000000 {
    compatible = "demo,simple-device";
    reg = <0x0 0x10000000 0x0 0x1000>;
    interrupts = <0 40 4>;
    status = "okay";
};
```

驱动中有：

```c
static const struct of_device_id demo_of_match[] = {
    { .compatible = "demo,simple-device" },
    { }
};

static struct platform_driver demo_driver = {
    .probe = demo_probe,
    .remove = demo_remove,
    .driver = {
        .name = "demo",
        .of_match_table = demo_of_match,
    },
};

module_platform_driver(demo_driver);
```

匹配过程可以理解为：

1. 内核解析设备树
2. 发现 `demo@10000000`
3. 因为 `status = "okay"`，创建 platform_device
4. 驱动注册 platform_driver
5. platform 总线比较 `compatible`
6. 匹配成功
7. 调用 `demo_probe()`
8. 驱动获取 `reg`、`interrupts` 等资源
9. 初始化硬件
10. 设备开始工作

## 25. 示例：PCIe 驱动匹配过程

PCIe 设备通常可以自动枚举。

匹配过程大致是：

1. PCIe Root Complex 扫描总线
2. 发现 Endpoint 设备
3. 读取设备配置空间
4. 得到 Vendor ID、Device ID、Class Code
5. 内核创建 pci_dev
6. PCI 驱动注册 pci_driver
7. PCI 总线比较 id_table
8. 匹配成功后调用驱动 probe

示例匹配表：

```c
static const struct pci_device_id demo_pci_ids[] = {
    { PCI_DEVICE(0x1234, 0x5678) },
    { }
};
MODULE_DEVICE_TABLE(pci, demo_pci_ids);
```

PCIe 驱动排查常用命令：

```bash
lspci -nn
ls /sys/bus/pci/devices
dmesg | grep -i pci
```

## 26. 设备模型与字符设备的关系

字符设备驱动也会和设备模型发生关系。

早期简单字符设备可能只注册：

1. 主设备号
2. `file_operations`
3. `/dev/xxx` 节点

但更规范的驱动通常会配合：

1. `class_create()`
2. `device_create()`
3. udev 自动创建设备节点
4. `/sys/class/...` 暴露设备信息

例如：

```text
驱动注册字符设备
    -> 创建 class
    -> 创建设备
    -> 用户空间出现 /dev/xxx
    -> /sys/class/xxx/xxx 中出现对应节点
```

所以后续学习字符设备时，也会再次遇到 Linux 设备模型。

## 27. 设备模型与电源管理

Linux 设备模型还和电源管理有关。

因为内核需要知道设备之间的父子关系和驱动关系，才能正确处理：

1. suspend
2. resume
3. runtime PM
4. shutdown
5. remove

驱动中常见的电源管理回调包括：

```c
.suspend
.resume
.runtime_suspend
.runtime_resume
```

入门阶段不需要深入掌握，但需要知道：

设备模型不只是为了匹配驱动，也为电源管理、热插拔、资源管理提供基础。

## 28. 设备模型常见误区

### 28.1 误区一：有源码就一定会加载驱动

不对。

源码存在不代表驱动会工作，还需要：

1. Kconfig 启用
2. Makefile 参与编译
3. 驱动注册成功
4. 设备存在
5. 匹配规则正确
6. probe 成功

### 28.2 误区二：设备树里有节点，驱动就一定会 probe

不对。

还需要：

1. 节点 `status = "okay"`
2. compatible 和驱动匹配表一致
3. 驱动已经编译并注册
4. 依赖资源可用
5. probe 没有返回错误

### 28.3 误区三：/dev 中有节点就代表硬件正常

不一定。

`/dev` 节点只是用户空间接口存在，不代表硬件一定工作正常。

还需要结合：

1. `dmesg`
2. `/sys`
3. 实际读写测试
4. 中断变化
5. 硬件信号
6. 驱动内部状态

### 28.4 误区四：所有设备都来自设备树

不对。

设备来源可能包括：

1. Device Tree
2. ACPI
3. PCIe 枚举
4. USB 枚举
5. 板级代码注册
6. MFD 子设备创建
7. 虚拟设备

## 29. 推荐练习

建议完成以下练习：

1. 查看当前系统有哪些 platform 设备：

```bash
ls /sys/bus/platform/devices
```

2. 查看当前系统有哪些 platform 驱动：

```bash
ls /sys/bus/platform/drivers
```

3. 查看当前系统有哪些 PCIe 设备：

```bash
ls /sys/bus/pci/devices
```

4. 查看某个网卡属于哪个设备路径：

```bash
readlink -f /sys/class/net/<网卡名>
```

5. 查看某个设备是否绑定驱动：

```bash
ls -l /sys/bus/platform/devices/<设备名>/driver
```

6. 查看当前系统加载了哪些模块：

```bash
lsmod
```

7. 搜索 probe 相关日志：

```bash
dmesg | grep -i probe
```

8. 搜索 deferred probe：

```bash
dmesg | grep -i defer
```

9. 查看运行时设备树：

```bash
ls /sys/firmware/devicetree/base
```

10. 找一个设备树节点，检查它的 `compatible` 是否和驱动匹配表一致。

## 30. 小结

本文介绍了 Linux 设备模型的基础概念。

需要重点掌握：

1. `device` 表示设备
2. `driver` 表示驱动
3. `bus` 负责设备和驱动匹配
4. `class` 负责按功能向用户空间暴露设备
5. `probe()` 是设备和驱动匹配成功后的初始化入口
6. `remove()` 是设备移除或驱动卸载时的清理入口
7. platform 总线常用于 SoC 片上设备
8. Device Tree 常用于创建 platform_device
9. `compatible` 是设备树驱动匹配的核心依据
10. `/sys` 是观察设备模型的重要窗口

对 Linux 驱动开发来说，设备模型是非常重要的基础。后续学习设备树、platform 驱动、字符设备、网卡驱动、PCIe 驱动时，都会不断回到 device、driver、bus、class 这几个概念。
