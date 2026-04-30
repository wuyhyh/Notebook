# 04-platform-device与platform-driver基础

## 1. 文档目标

本文用于说明 Linux 内核中 `platform_device` 与 `platform_driver` 的基本概念和匹配流程。

学习完成后，应能够回答以下问题：

1. 什么是 platform 总线？
2. 什么是 `platform_device`？
3. 什么是 `platform_driver`？
4. `platform_device` 和 `platform_driver` 是如何匹配的？
5. `probe()` 函数什么时候被调用？
6. 设备树中的 `compatible` 和驱动中的 `of_match_table` 有什么关系？
7. platform 驱动中如何获取寄存器、中断等硬件资源？

## 2. platform 总线是什么

`platform` 总线是一种 Linux 内核中的虚拟总线，常用于管理 SoC 内部设备。

很多片上外设并不能像 PCIe、USB 那样自动枚举出来，它们通常需要由固件、设备树或板级代码提前描述。

例如：

1. UART 控制器
2. I2C 控制器
3. SPI 控制器
4. GPIO 控制器
5. Ethernet MAC
6. DMA 控制器
7. Watchdog
8. Timer
9. PWM 控制器
10. Reset 控制器

这些设备通常挂在 `platform` 总线上。

简单理解：

```text
platform 总线 = 用来管理 SoC 片上设备的一种虚拟总线
```

## 3. 为什么需要 platform 机制

对于 PCIe 设备，系统可以通过配置空间自动发现设备：

1. Vendor ID
2. Device ID
3. Class Code
4. BAR
5. IRQ/MSI 信息

但是很多 SoC 片上设备没有类似 PCIe 配置空间，内核无法靠扫描自动发现它们。

例如一个 UART 控制器，内核需要提前知道：

1. 寄存器基地址是多少
2. 寄存器范围多大
3. 中断号是多少
4. 时钟来自哪里
5. reset 控制来自哪里
6. 是否启用
7. 用哪个驱动匹配

这些信息通常来自 Device Tree。

所以 platform 机制解决的是：

```text
不能自动枚举的片上设备，如何被内核创建、匹配和驱动。
```

## 4. platform_device 是什么

`platform_device` 表示 platform 总线上的一个设备对象。

它描述的是：

```text
系统中确实存在一个需要驱动管理的片上设备。
```

简化后的结构可以这样理解：

```c
struct platform_device {
    const char *name;
    int id;
    struct device dev;
    u32 num_resources;
    struct resource *resource;
};
```

其中：

| 成员 | 说明 |
| --- | --- |
| `name` | 设备名称 |
| `id` | 设备编号 |
| `dev` | 通用设备模型对象 |
| `num_resources` | 资源数量 |
| `resource` | 资源数组，例如 MMIO、IRQ |

`platform_device` 本质上是一个设备实例。

例如系统中有两个 UART 控制器，就可以对应两个 platform device。

## 5. platform_driver 是什么

`platform_driver` 表示 platform 总线上的驱动程序。

它描述的是：

```text
我这个驱动支持哪些 platform 设备，以及匹配成功后如何初始化。
```

典型结构如下：

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
| `id_table` | platform 设备名匹配表 |

对于设备树平台，`driver.of_match_table` 非常重要。

## 6. platform_device 与 platform_driver 的关系

可以这样理解：

```text
platform_device  = 设备
platform_driver  = 驱动
platform bus     = 负责匹配设备和驱动的中间层
```

关系图：

```text
platform_device  ----注册到---->  platform bus  <----注册到----  platform_driver
                                      |
                                      v
                                匹配成功后调用 probe()
```

基本流程：

1. 内核创建 platform device
2. 驱动注册 platform driver
3. platform 总线检查设备和驱动是否匹配
4. 匹配成功后调用驱动的 `probe()`
5. `probe()` 中完成资源获取和硬件初始化

## 7. platform_device 从哪里来

`platform_device` 常见来源有三种：

| 来源 | 说明 |
| --- | --- |
| Device Tree | ARM/ARM64 平台最常见 |
| ACPI | 一些服务器和 PC 平台常见 |
| 板级 C 代码 | 老式内核或特殊平台中可能存在 |

在现代 ARM64 嵌入式开发中，最常见的是：

```text
设备树节点 -> 内核解析 -> 创建 platform_device
```

例如设备树中有：

```dts
uart0: serial@28000000 {
    compatible = "arm,pl011";
    reg = <0x0 0x28000000 0x0 0x1000>;
    interrupts = <0 33 4>;
    status = "okay";
};
```

内核启动时解析这个节点，如果该节点满足条件，就可能创建对应的 `platform_device`。

## 8. platform_driver 如何注册

platform 驱动通常通过 `module_platform_driver()` 注册。

示例：

```c
static struct platform_driver demo_driver = {
    .probe = demo_probe,
    .remove = demo_remove,
    .driver = {
        .name = "demo-platform",
        .of_match_table = demo_of_match,
    },
};

module_platform_driver(demo_driver);
```

`module_platform_driver()` 是一个常用宏，大致等价于：

1. 模块加载时调用 `platform_driver_register()`
2. 模块卸载时调用 `platform_driver_unregister()`

所以驱动模块加载后，并不是直接运行硬件操作，而是先把自己注册到 platform 总线，等待匹配设备。

## 9. compatible 匹配基础

在设备树中，设备通常有 `compatible` 属性。

例如：

```dts
demo@10000000 {
    compatible = "vendor,demo-device";
    reg = <0x0 0x10000000 0x0 0x1000>;
    interrupts = <0 40 4>;
    status = "okay";
};
```

驱动中通常有对应的 `of_device_id` 表：

```c
static const struct of_device_id demo_of_match[] = {
    { .compatible = "vendor,demo-device" },
    { }
};
MODULE_DEVICE_TABLE(of, demo_of_match);
```

然后在 `platform_driver` 中引用：

```c
.driver = {
    .name = "demo-platform",
    .of_match_table = demo_of_match,
},
```

匹配规则的核心是：

```text
设备树节点 compatible == 驱动 of_match_table 中的 compatible
```

只要匹配成功，platform 总线就会调用驱动的 `probe()`。

## 10. probe 函数什么时候调用

`probe()` 函数在设备和驱动匹配成功后调用。

它表示：

```text
内核已经确认这个驱动可以管理这个设备，现在开始初始化。
```

典型 `probe()` 中会做：

1. 获取 MMIO 寄存器资源
2. 映射寄存器地址
3. 获取中断号
4. 申请中断
5. 获取时钟
6. 获取 reset 控制
7. 获取 GPIO
8. 分配驱动私有数据
9. 初始化硬件
10. 注册字符设备、网卡或其他子系统接口

示例：

```c
static int demo_probe(struct platform_device *pdev)
{
    pr_info("demo platform device probed\n");
    return 0;
}
```

如果 `probe()` 没有执行，说明设备和驱动还没有真正匹配成功。

## 11. remove 函数什么时候调用

`remove()` 函数通常在设备移除或驱动卸载时调用。

它的作用是清理 `probe()` 中申请的资源。

示例：

```c
static int demo_remove(struct platform_device *pdev)
{
    pr_info("demo platform device removed\n");
    return 0;
}
```

`remove()` 中常见工作包括：

1. 注销字符设备
2. 注销网络设备
3. 关闭硬件
4. 停止定时器或工作队列
5. 释放资源
6. 清理私有数据

如果使用了大量 `devm_` 接口，部分资源会在设备解绑时自动释放，但并不代表所有清理都可以省略。

## 12. 最小 platform 驱动示例

下面是一个最小 platform 驱动骨架。

```c
#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/of.h>

static int demo_probe(struct platform_device *pdev)
{
    pr_info("demo: probe called\n");
    return 0;
}

static int demo_remove(struct platform_device *pdev)
{
    pr_info("demo: remove called\n");
    return 0;
}

static const struct of_device_id demo_of_match[] = {
    { .compatible = "demo,simple-platform-device" },
    { }
};
MODULE_DEVICE_TABLE(of, demo_of_match);

static struct platform_driver demo_driver = {
    .probe = demo_probe,
    .remove = demo_remove,
    .driver = {
        .name = "demo-platform-driver",
        .of_match_table = demo_of_match,
    },
};

module_platform_driver(demo_driver);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("training");
MODULE_DESCRIPTION("A simple platform driver example");
```

这个驱动的重点不是控制真实硬件，而是验证：

1. 驱动能否编译
2. 驱动能否注册
3. 设备树是否能创建设备
4. `compatible` 是否能匹配
5. `probe()` 是否能被调用

## 13. 对应设备树示例

可以配合如下设备树节点理解：

```dts
demo@10000000 {
    compatible = "demo,simple-platform-device";
    reg = <0x0 0x10000000 0x0 0x1000>;
    interrupts = <0 40 4>;
    status = "okay";
};
```

重点字段说明：

| 属性 | 说明 |
| --- | --- |
| `compatible` | 用于和驱动匹配 |
| `reg` | 描述寄存器物理地址和大小 |
| `interrupts` | 描述中断信息 |
| `status` | 表示设备是否启用 |

注意：

这里只是示例地址和中断号，实际项目中必须根据芯片手册和板级设计填写。

不要随便把示例地址放进真实设备树。

## 14. Makefile 示例

如果作为外部模块编译，可以使用如下 Makefile：

```makefile
obj-m += demo_platform.o

KDIR ?= /lib/modules/$(shell uname -r)/build
PWD := $(shell pwd)

all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
```

如果源码文件是：

```text
demo_platform.c
```

则最终会生成：

```text
demo_platform.ko
```

## 15. 编译和加载

编译：

```bash
make
```

加载模块：

```bash
sudo insmod demo_platform.ko
```

查看日志：

```bash
dmesg | tail -n 50
```

如果系统中存在匹配的设备树节点，并且驱动加载成功，应该能看到类似日志：

```text
demo: probe called
```

卸载模块：

```bash
sudo rmmod demo_platform
```

查看日志：

```bash
dmesg | tail -n 50
```

可能看到：

```text
demo: remove called
```

如果没有看到 `probe called`，说明驱动注册了，但没有匹配到设备，或者设备没有被创建。

## 16. 如何确认 platform 设备是否存在

查看 platform 设备：

```bash
ls /sys/bus/platform/devices
```

如果设备树节点被成功创建为 platform 设备，通常可以在这里看到相关设备。

也可以按关键字搜索：

```bash
ls /sys/bus/platform/devices | grep demo
```

如果找不到设备，重点检查：

1. 设备树节点是否真的被 Linux 使用
2. 节点 `status` 是否为 `okay`
3. 节点是否在合适的父节点下
4. 设备树是否重新编译成 dtb
5. U-Boot 是否加载了新的 dtb
6. 内核启动后 `/sys/firmware/devicetree/base` 中是否存在该节点

## 17. 如何确认 platform 驱动是否存在

查看 platform 驱动：

```bash
ls /sys/bus/platform/drivers
```

按名称过滤：

```bash
ls /sys/bus/platform/drivers | grep demo
```

如果驱动不存在，重点检查：

1. 模块是否加载成功
2. 驱动是否编译进内核
3. `module_platform_driver()` 是否使用正确
4. 驱动初始化是否失败

查看模块是否加载：

```bash
lsmod | grep demo_platform
```

查看日志：

```bash
dmesg | grep -i demo
```

## 18. 如何确认设备和驱动是否绑定

如果设备存在，可以进入设备目录：

```bash
cd /sys/bus/platform/devices/<device-name>
ls -l driver
```

如果存在 `driver` 符号链接，说明设备已经绑定到某个驱动。

查看绑定到哪个驱动：

```bash
readlink driver
```

如果没有 `driver` 链接，可能是：

1. 驱动没有加载
2. `compatible` 不匹配
3. 驱动 probe 返回错误
4. 设备还处于 deferred probe
5. 驱动支持表没有正确导出

## 19. 获取 MMIO 资源

设备树中的 `reg` 属性通常会被转换成 platform resource。

驱动中常用：

```c
struct resource *res;

res = platform_get_resource(pdev, IORESOURCE_MEM, 0);
```

然后映射：

```c
void __iomem *base;

base = devm_ioremap_resource(&pdev->dev, res);
if (IS_ERR(base))
    return PTR_ERR(base);
```

完整示例：

```c
static int demo_probe(struct platform_device *pdev)
{
    struct resource *res;
    void __iomem *base;

    res = platform_get_resource(pdev, IORESOURCE_MEM, 0);
    base = devm_ioremap_resource(&pdev->dev, res);
    if (IS_ERR(base))
        return PTR_ERR(base);

    dev_info(&pdev->dev, "MMIO mapped\n");
    return 0;
}
```

说明：

| 接口 | 作用 |
| --- | --- |
| `platform_get_resource()` | 从 platform_device 中取资源 |
| `IORESOURCE_MEM` | 表示内存映射资源 |
| `devm_ioremap_resource()` | 检查并映射 MMIO 资源 |

## 20. 获取 IRQ 中断资源

设备树中的 `interrupts` 属性通常会被转换成 IRQ 资源。

常用接口：

```c
int irq;

irq = platform_get_irq(pdev, 0);
if (irq < 0)
    return irq;
```

申请中断：

```c
ret = devm_request_irq(&pdev->dev, irq, demo_irq_handler, 0,
                       dev_name(&pdev->dev), data);
if (ret)
    return ret;
```

中断处理函数示例：

```c
static irqreturn_t demo_irq_handler(int irq, void *dev_id)
{
    return IRQ_HANDLED;
}
```

注意：

中断处理函数中不能做耗时操作，不能随便睡眠。

## 21. 获取设备树属性

有时驱动需要读取设备树中的普通属性。

例如设备树中有：

```dts
demo@10000000 {
    compatible = "demo,simple-platform-device";
    reg = <0x0 0x10000000 0x0 0x1000>;
    demo,value = <123>;
    status = "okay";
};
```

驱动中读取：

```c
u32 value;
int ret;

ret = of_property_read_u32(pdev->dev.of_node, "demo,value", &value);
if (ret)
    dev_warn(&pdev->dev, "demo,value not found\n");
else
    dev_info(&pdev->dev, "demo,value=%u\n", value);
```

常见接口：

| 接口 | 作用 |
| --- | --- |
| `of_property_read_u32()` | 读取 32 位整数 |
| `of_property_read_u64()` | 读取 64 位整数 |
| `of_property_read_string()` | 读取字符串 |
| `of_property_read_bool()` | 判断布尔属性是否存在 |

## 22. 保存驱动私有数据

驱动通常需要为每个设备保存私有数据。

示例：

```c
struct demo_priv {
    void __iomem *base;
    int irq;
};

static int demo_probe(struct platform_device *pdev)
{
    struct demo_priv *priv;

    priv = devm_kzalloc(&pdev->dev, sizeof(*priv), GFP_KERNEL);
    if (!priv)
        return -ENOMEM;

    platform_set_drvdata(pdev, priv);

    return 0;
}
```

在 `remove()` 中获取：

```c
static int demo_remove(struct platform_device *pdev)
{
    struct demo_priv *priv = platform_get_drvdata(pdev);

    return 0;
}
```

说明：

| 接口 | 作用 |
| --- | --- |
| `platform_set_drvdata()` | 保存驱动私有数据 |
| `platform_get_drvdata()` | 获取驱动私有数据 |
| `devm_kzalloc()` | 分配随设备生命周期管理的内存 |

## 23. devm_ 接口的意义

platform 驱动中经常使用 `devm_` 接口。

例如：

```c
devm_kzalloc()
devm_ioremap_resource()
devm_request_irq()
devm_clk_get()
devm_gpiod_get()
```

`devm_` 表示 device managed resource，即资源由设备生命周期管理。

优点：

1. probe 失败时自动释放资源
2. remove 时减少手动释放代码
3. 错误路径更简单
4. 降低资源泄漏风险

但是要注意：

并不是所有资源都可以完全依赖 `devm_` 自动处理。

例如注册到某些子系统的对象，仍然可能需要主动注销。

## 24. of_match_table 和 MODULE_DEVICE_TABLE

驱动中常见：

```c
static const struct of_device_id demo_of_match[] = {
    { .compatible = "demo,simple-platform-device" },
    { }
};
MODULE_DEVICE_TABLE(of, demo_of_match);
```

其中：

| 内容 | 作用 |
| --- | --- |
| `of_match_table` | 运行时用于设备树匹配 |
| `MODULE_DEVICE_TABLE(of, ...)` | 导出模块别名信息，方便模块自动加载 |

如果驱动编译成模块，`MODULE_DEVICE_TABLE` 可以帮助用户空间根据设备信息自动加载对应模块。

入门阶段可以先记住：

```text
写了 of_match_table 后，通常也要配套写 MODULE_DEVICE_TABLE(of, xxx)。
```

## 25. 为什么 probe 没有执行

这是 platform 驱动调试中最常见的问题。

常见原因：

| 原因 | 排查方法 |
| --- | --- |
| 设备树节点不存在 | 查看 `/sys/firmware/devicetree/base` |
| 设备树节点 status 不是 okay | 查看节点的 `status` |
| compatible 写错 | 对比设备树和驱动源码 |
| 驱动没有加载 | `lsmod`、`dmesg` |
| 驱动没有注册成功 | 查看 `/sys/bus/platform/drivers` |
| 设备没有创建为 platform device | 查看 `/sys/bus/platform/devices` |
| probe 返回错误 | 查看 `dmesg` |
| 依赖资源未准备好 | 搜索 deferred probe |

常用命令：

```bash
dmesg | grep -i "demo\|probe\|defer\|fail\|error"
ls /sys/bus/platform/devices
ls /sys/bus/platform/drivers
lsmod
```

## 26. 设备树没有生效的常见原因

有时候设备树源码改了，但 Linux 里没有变化。

常见原因：

1. 只改了 `.dts`，没有重新编译 `.dtb`
2. 编译了 `.dtb`，但没有复制到启动分区
3. U-Boot 实际加载的是另一个 `.dtb`
4. 启动命令中的 `fdt_addr_r` 指向旧设备树
5. 多个分区中存在多个 `/boot/dtb`
6. 内核启动使用了 ACPI 而不是 Device Tree
7. 修改的节点被其他 `.dtsi` 覆盖
8. 节点 `status` 最终仍然是 `disabled`

确认运行时设备树：

```bash
ls /sys/firmware/devicetree/base
find /sys/firmware/devicetree/base -name compatible
```

对于具体节点，可以用 `hexdump` 或 `xxd` 查看属性：

```bash
hexdump -C /sys/firmware/devicetree/base/<path>/compatible
```

## 27. platform 驱动调试流程

调试一个 platform 驱动时，可以按以下顺序：

### 27.1 确认设备树节点存在

```bash
find /sys/firmware/devicetree/base -iname '*demo*'
```

### 27.2 确认 platform device 存在

```bash
ls /sys/bus/platform/devices | grep demo
```

### 27.3 确认 platform driver 存在

```bash
ls /sys/bus/platform/drivers | grep demo
```

### 27.4 确认设备是否绑定驱动

```bash
ls -l /sys/bus/platform/devices/<device-name>/driver
```

### 27.5 查看 probe 日志

```bash
dmesg | grep -i "demo\|probe\|fail\|error\|defer"
```

### 27.6 检查资源

```bash
cat /proc/iomem
cat /proc/interrupts
```

这个顺序比盲目改代码更可靠。

## 28. platform 与 PCIe 的区别

| 项目 | platform 设备 | PCIe 设备 |
| --- | --- | --- |
| 发现方式 | 设备树、ACPI、板级代码 | 总线枚举 |
| 是否能自动发现 | 通常不能 | 通常可以 |
| 匹配依据 | `compatible`、设备名 | Vendor ID、Device ID、Class |
| 资源来源 | `reg`、`interrupts` 等固件描述 | PCI 配置空间和 BAR |
| 常见设备 | SoC 内部外设 | 网卡、NVMe、显卡、加速卡 |
| sysfs 路径 | `/sys/bus/platform/devices` | `/sys/bus/pci/devices` |

简单理解：

1. platform 设备多用于 SoC 片上外设
2. PCIe 设备多用于可枚举外设
3. 两者都接入 Linux 设备模型
4. 两者都有 device、driver、probe 的概念

## 29. 常见误区

### 29.1 误区一：设备树里写了节点，probe 就一定执行

不一定。

还需要：

1. 节点被实际使用
2. `status = "okay"`
3. 驱动成功注册
4. `compatible` 匹配成功
5. 资源没有严重错误
6. probe 没有返回错误

### 29.2 误区二：insmod 后没日志，说明模块没加载

不一定。

模块可能已经加载，但没有匹配设备，所以 `probe()` 没有执行。

应该同时查看：

```bash
lsmod
ls /sys/bus/platform/drivers
dmesg
```

### 29.3 误区三：platform 驱动一定要有真实硬件

不完全是。

可以写一个简单 platform 驱动配合设备树节点验证匹配流程。

但是如果要访问真实寄存器、中断、时钟，就必须有正确的硬件资源。

### 29.4 误区四：compatible 只是注释

不对。

`compatible` 是设备树匹配驱动的关键字段。

一个字符写错，就可能导致驱动无法匹配。

## 30. 推荐练习

建议完成以下练习：

1. 编写一个最小 platform 驱动，只打印 `probe()` 和 `remove()`
2. 编写一个对应设备树节点，使用相同 `compatible`
3. 编译并加载模块，观察 `probe()` 是否执行
4. 故意改错 `compatible`，观察 `probe()` 不执行
5. 查看 `/sys/bus/platform/devices`
6. 查看 `/sys/bus/platform/drivers`
7. 查看设备目录下是否存在 `driver` 链接
8. 在设备树中添加一个自定义属性，并在驱动中读取
9. 使用 `platform_get_resource()` 获取 `reg`
10. 使用 `platform_get_irq()` 获取中断号

## 31. 小结

本文介绍了 `platform_device` 与 `platform_driver` 的基础知识。

需要重点掌握：

1. platform 总线常用于 SoC 片上设备
2. `platform_device` 表示设备
3. `platform_driver` 表示驱动
4. platform 总线负责匹配设备和驱动
5. 设备树节点通常会被内核转换成 platform device
6. `compatible` 是设备树匹配驱动的关键
7. 匹配成功后会调用 `probe()`
8. `probe()` 中完成资源获取和硬件初始化
9. `remove()` 中完成清理
10. `/sys/bus/platform/devices` 和 `/sys/bus/platform/drivers` 是重要排查入口

掌握 platform 机制之后，再学习设备树、字符设备驱动、I2C/SPI 控制器驱动、以太网 MAC 驱动时，就能更清楚地理解驱动为什么会被调用，以及硬件资源是如何传递给驱动的。
