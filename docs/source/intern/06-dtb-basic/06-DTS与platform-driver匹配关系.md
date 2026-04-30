# 06-DTS与platform-driver匹配关系

## 1. 文档目标

本文用于整理 DTS 设备树与 Linux `platform_driver` 的匹配关系，重点说明：

1. DTS 节点如何变成 Linux 设备对象
2. `compatible` 如何匹配 `of_device_id`
3. `platform_device` 和 `platform_driver` 分别是什么
4. 驱动的 `probe()` 为什么会被调用
5. 驱动如何从 DTS 中获取 `reg`、`interrupts`、`clocks`、`gpios` 等资源
6. 驱动不 probe 时应该如何排查

这篇文档是 DTS 学习和 Linux 驱动开发之间的衔接文档。

---

## 2. 先理解一个基本关系

设备树本身不是驱动。

设备树只是描述硬件：

```text
这里有一个设备
它的 compatible 是什么
它的寄存器地址在哪里
它用哪个中断
它需要哪些 clock / reset / gpio
它是否启用
```

驱动代码负责真正控制硬件：

```text
匹配设备
映射寄存器
申请中断
打开时钟
释放复位
初始化硬件
注册子系统接口
```

两者之间的连接点就是：

```text
DTS 节点
  |
  v
platform_device
  |
  v
platform_driver
  |
  v
probe()
```

---

## 3. 什么是 platform_device

`platform_device` 是 Linux 设备模型中的一种设备对象。

它通常用于描述 SoC 内部外设，例如：

- UART 控制器
- GPIO 控制器
- I2C 控制器
- SPI 控制器
- Ethernet MAC
- USB 控制器
- PCIe 控制器
- Watchdog
- Timer
- PWM

这些设备通常不是通过 PCI 枚举出来的，而是固定存在于 SoC 地址空间中。

例如一个 UART 控制器可能固定在：

```text
物理地址：0x28000000
中断号：32
```

这种设备非常适合通过设备树描述，然后由内核创建 `platform_device`。

---

## 4. 什么是 platform_driver

`platform_driver` 是用于驱动 `platform_device` 的驱动对象。

一个典型结构如下：

```c
static struct platform_driver foo_driver = {
    .probe = foo_probe,
    .remove = foo_remove,
    .driver = {
        .name = "foo",
        .of_match_table = foo_of_match,
    },
};

module_platform_driver(foo_driver);
```

其中最重要的是：

| 成员 | 作用 |
|---|---|
| `.probe` | 设备和驱动匹配成功后调用 |
| `.remove` | 设备移除或驱动卸载时调用 |
| `.driver.name` | 驱动名称 |
| `.of_match_table` | 用于匹配设备树 `compatible` |

---

## 5. DTS 节点示例

假设设备树中有一个设备节点：

```dts
foo@10000000 {
    compatible = "vendor,foo";
    reg = <0x0 0x10000000 0x0 0x1000>;
    interrupts = <0 40 4>;
    clocks = <&clk 10>;
    resets = <&rst 3>;
    status = "okay";
};
```

这个节点描述的信息包括：

| 属性 | 含义 |
|---|---|
| `foo@10000000` | 节点名称和单元地址 |
| `compatible = "vendor,foo"` | 用于匹配驱动 |
| `reg` | 寄存器地址范围 |
| `interrupts` | 中断资源 |
| `clocks` | 时钟资源 |
| `resets` | 复位资源 |
| `status = "okay"` | 节点启用 |

如果这个节点被 Linux 正常解析，内核可能会为它创建一个 `platform_device`。

---

## 6. 驱动匹配表示例

驱动中通常会写一个 `of_device_id` 表：

```c
static const struct of_device_id foo_of_match[] = {
    { .compatible = "vendor,foo" },
    { }
};
MODULE_DEVICE_TABLE(of, foo_of_match);
```

这里的：

```c
.compatible = "vendor,foo"
```

需要和 DTS 中的：

```dts
compatible = "vendor,foo";
```

对应。

如果匹配成功，内核就会调用该驱动的 `probe()` 函数。

---

## 7. 匹配流程总览

DTS 和 platform driver 的匹配流程可以理解为：

```text
Bootloader 加载 DTB
  |
  v
Linux 启动并解析 DTB
  |
  v
遍历设备树节点
  |
  v
对 status = okay 的节点创建设备对象
  |
  v
生成 platform_device
  |
  v
platform_driver 注册
  |
  v
比较 DTS compatible 和驱动 of_match_table
  |
  v
匹配成功
  |
  v
调用 probe()
```

核心匹配关系：

```text
DTS:
compatible = "vendor,foo";

Driver:
{ .compatible = "vendor,foo" }

结果：
foo_probe() 被调用
```

---

## 8. probe 函数是什么

`probe()` 是驱动真正开始管理设备的入口函数。

典型形式：

```c
static int foo_probe(struct platform_device *pdev)
{
    return 0;
}
```

当设备和驱动匹配成功后，内核会调用：

```text
foo_probe(pdev)
```

这里的 `pdev` 就代表从 DTS 节点创建出来的 `platform_device`。

驱动可以通过 `pdev` 获取设备树资源。

---

## 9. probe 中获取 reg 资源

DTS 中：

```dts
reg = <0x0 0x10000000 0x0 0x1000>;
```

驱动中常见写法：

```c
struct resource *res;
void __iomem *base;

res = platform_get_resource(pdev, IORESOURCE_MEM, 0);
base = devm_ioremap_resource(&pdev->dev, res);
```

含义是：

```text
platform_get_resource() 从 platform_device 中获取 IORESOURCE_MEM 资源
devm_ioremap_resource() 把物理 MMIO 地址映射成内核虚拟地址
```

对应关系：

```text
DTS reg
  |
  v
platform_device resource
  |
  v
platform_get_resource()
  |
  v
devm_ioremap_resource()
```

---

## 10. probe 中获取 interrupt 资源

DTS 中：

```dts
interrupts = <0 40 4>;
```

驱动中常见写法：

```c
int irq;

irq = platform_get_irq(pdev, 0);
if (irq < 0)
    return irq;
```

如果驱动需要注册中断处理函数：

```c
ret = devm_request_irq(&pdev->dev, irq, foo_irq_handler,
                       0, dev_name(&pdev->dev), foo);
```

对应关系：

```text
DTS interrupts
  |
  v
platform_device IRQ resource
  |
  v
platform_get_irq()
  |
  v
request_irq()
```

---

## 11. probe 中获取 clock 资源

DTS 中：

```dts
clocks = <&clk 10>;
clock-names = "core";
```

驱动中常见写法：

```c
struct clk *clk;

clk = devm_clk_get(&pdev->dev, "core");
if (IS_ERR(clk))
    return PTR_ERR(clk);

ret = clk_prepare_enable(clk);
if (ret)
    return ret;
```

对应关系：

```text
DTS clocks / clock-names
  |
  v
devm_clk_get()
  |
  v
clk_prepare_enable()
```

如果 `clock-names` 写错，驱动可能拿不到对应 clock。

---

## 12. probe 中获取 reset 资源

DTS 中：

```dts
resets = <&rst 3>;
reset-names = "foo";
```

驱动中常见写法：

```c
struct reset_control *rst;

rst = devm_reset_control_get(&pdev->dev, "foo");
if (IS_ERR(rst))
    return PTR_ERR(rst);

reset_control_deassert(rst);
```

对应关系：

```text
DTS resets / reset-names
  |
  v
devm_reset_control_get()
  |
  v
reset_control_deassert()
```

如果 reset 没释放，硬件可能仍然处于复位状态，寄存器读写也可能异常。

---

## 13. probe 中获取 GPIO 资源

DTS 中：

```dts
reset-gpios = <&gpio0 5 GPIO_ACTIVE_LOW>;
enable-gpios = <&gpio0 6 GPIO_ACTIVE_HIGH>;
```

驱动中常见写法：

```c
struct gpio_desc *reset_gpio;

reset_gpio = devm_gpiod_get(&pdev->dev, "reset", GPIOD_OUT_LOW);
if (IS_ERR(reset_gpio))
    return PTR_ERR(reset_gpio);
```

这里驱动获取的是 `"reset"`，DTS 中对应属性名通常是：

```dts
reset-gpios
```

对应关系：

```text
devm_gpiod_get(dev, "reset", ...)
        |
        v
DTS reset-gpios
```

如果驱动获取 `"enable"`，DTS 中通常对应：

```dts
enable-gpios
```

---

## 14. 一个完整 platform driver 示例

下面是一个简化的 platform driver 示例：

```c
#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/of_device.h>
#include <linux/io.h>
#include <linux/interrupt.h>
#include <linux/clk.h>
#include <linux/reset.h>

struct foo_dev {
    void __iomem *base;
    int irq;
    struct clk *clk;
    struct reset_control *rst;
};

static irqreturn_t foo_irq_handler(int irq, void *data)
{
    return IRQ_HANDLED;
}

static int foo_probe(struct platform_device *pdev)
{
    struct foo_dev *foo;
    struct resource *res;
    int ret;

    foo = devm_kzalloc(&pdev->dev, sizeof(*foo), GFP_KERNEL);
    if (!foo)
        return -ENOMEM;

    res = platform_get_resource(pdev, IORESOURCE_MEM, 0);
    foo->base = devm_ioremap_resource(&pdev->dev, res);
    if (IS_ERR(foo->base))
        return PTR_ERR(foo->base);

    foo->irq = platform_get_irq(pdev, 0);
    if (foo->irq < 0)
        return foo->irq;

    ret = devm_request_irq(&pdev->dev, foo->irq, foo_irq_handler,
                           0, dev_name(&pdev->dev), foo);
    if (ret)
        return ret;

    foo->clk = devm_clk_get(&pdev->dev, "core");
    if (IS_ERR(foo->clk))
        return PTR_ERR(foo->clk);

    ret = clk_prepare_enable(foo->clk);
    if (ret)
        return ret;

    foo->rst = devm_reset_control_get_optional(&pdev->dev, "foo");
    if (IS_ERR(foo->rst)) {
        ret = PTR_ERR(foo->rst);
        goto disable_clk;
    }

    if (foo->rst)
        reset_control_deassert(foo->rst);

    platform_set_drvdata(pdev, foo);

    dev_info(&pdev->dev, "foo device probed\n");
    return 0;

disable_clk:
    clk_disable_unprepare(foo->clk);
    return ret;
}

static int foo_remove(struct platform_device *pdev)
{
    struct foo_dev *foo = platform_get_drvdata(pdev);

    if (foo->rst)
        reset_control_assert(foo->rst);

    clk_disable_unprepare(foo->clk);

    return 0;
}

static const struct of_device_id foo_of_match[] = {
    { .compatible = "vendor,foo" },
    { }
};
MODULE_DEVICE_TABLE(of, foo_of_match);

static struct platform_driver foo_driver = {
    .probe = foo_probe,
    .remove = foo_remove,
    .driver = {
        .name = "foo",
        .of_match_table = foo_of_match,
    },
};

module_platform_driver(foo_driver);

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Example platform driver for DTS matching");
```

对应 DTS 可以写成：

```dts
foo@10000000 {
    compatible = "vendor,foo";
    reg = <0x0 0x10000000 0x0 0x1000>;
    interrupts = <0 40 4>;
    clocks = <&clk 10>;
    clock-names = "core";
    resets = <&rst 3>;
    reset-names = "foo";
    status = "okay";
};
```

---

## 15. compatible 字符串可以有多个

DTS 中 `compatible` 可以写多个字符串：

```dts
compatible = "vendor,foo-v2", "vendor,foo-v1";
```

含义是：

```text
优先匹配 vendor,foo-v2
如果驱动不支持，也可以退化匹配 vendor,foo-v1
```

驱动中可能写：

```c
static const struct of_device_id foo_of_match[] = {
    { .compatible = "vendor,foo-v1" },
    { }
};
```

这样即使驱动没有写 `"vendor,foo-v2"`，仍然可以通过 `"vendor,foo-v1"` 匹配。

这种写法常用于硬件版本兼容。

---

## 16. of_device_id 的 data 字段

`of_device_id` 还可以携带私有数据：

```c
enum foo_type {
    FOO_V1,
    FOO_V2,
};

static const struct of_device_id foo_of_match[] = {
    { .compatible = "vendor,foo-v1", .data = (void *)FOO_V1 },
    { .compatible = "vendor,foo-v2", .data = (void *)FOO_V2 },
    { }
};
```

在 probe 中获取：

```c
const struct of_device_id *match;
enum foo_type type;

match = of_match_device(foo_of_match, &pdev->dev);
if (!match)
    return -ENODEV;

type = (enum foo_type)match->data;
```

这样同一个驱动可以根据不同 `compatible` 做不同初始化。

---

## 17. platform_driver 和普通字符设备驱动的关系

`platform_driver` 解决的是：

```text
如何匹配和初始化 SoC 平台设备
```

字符设备解决的是：

```text
如何向用户空间提供 /dev/xxx 接口
```

二者不是互斥关系。

一个完整驱动可能同时包含：

```text
platform_driver
  |
  v
probe()
  |
  v
初始化硬件
  |
  v
注册字符设备 / miscdevice / netdev / input device / tty / i2c adapter 等
```

例如：

- UART 驱动会注册 tty 设备
- Ethernet MAC 驱动会注册 net_device
- GPIO 控制器驱动会注册 gpiochip
- I2C 控制器驱动会注册 i2c_adapter
- 简单自定义设备可能注册 miscdevice 或 char device

所以不要把 `platform_driver` 理解成用户空间接口。

它更像是：

> 平台设备和驱动匹配、初始化的入口框架。

---

## 18. platform bus、device、driver 三者关系

可以这样理解：

```text
platform bus
  |
  |-- platform_device 1
  |-- platform_device 2
  |-- platform_device 3
  |
  |-- platform_driver A
  |-- platform_driver B
  |-- platform_driver C
```

platform bus 负责把 device 和 driver 进行匹配。

设备侧来源可能是：

```text
DTS 节点
ACPI 表
板级 C 代码注册
```

在 ARM/ARM64 DTS 启动场景下，很多 `platform_device` 来自 DTS。

驱动侧来源是：

```text
platform_driver_register()
module_platform_driver()
```

当 device 和 driver 匹配成功，platform bus 调用驱动的 `probe()`。

---

## 19. 驱动为什么没有 probe

驱动没有 probe 是 DTS 和驱动调试中最常见的问题。

常见原因包括：

1. DTS 节点没有被编译进实际使用的 DTB
2. Bootloader 加载的不是你修改后的 DTB
3. 节点 `status = "disabled"`
4. 父节点 `status = "disabled"`
5. `compatible` 字符串和驱动 `of_match_table` 不一致
6. 驱动没有编译进内核
7. 驱动是模块，但没有加载
8. 节点所在总线没有被正确解析
9. 驱动 probe 被调用了，但失败返回，误以为没 probe
10. 内核使用 ACPI 启动，而不是 Device Tree

排查时不要只看 DTS 源码，要看运行时状态。

---

## 20. 如何确认当前运行时 DTS

导出当前运行时设备树：

```bash
dtc -I fs -O dts -o running.dts /proc/device-tree
```

然后搜索目标节点：

```bash
grep -n "foo@10000000" -A40 running.dts
```

重点确认：

```text
节点是否存在
status 是否为 okay
compatible 是否正确
reg 是否正确
interrupts 是否正确
clocks / resets / gpios 是否存在
```

如果 `running.dts` 中没有你的修改，说明问题不在驱动，而在 DTB 加载或编译流程。

---

## 21. 如何确认 platform_device 是否创建

查看 platform devices：

```bash
ls /sys/bus/platform/devices/
```

按地址搜索：

```bash
ls /sys/bus/platform/devices/ | grep 10000000
```

也可以搜索设备名：

```bash
find /sys/bus/platform/devices/ -maxdepth 1 -iname "*foo*"
```

如果能看到设备，说明设备对象大概率已经创建。

如果看不到，优先查：

```text
running.dts
status
父节点
节点位置
compatible
```

---

## 22. 如何确认驱动是否注册

查看 platform drivers：

```bash
ls /sys/bus/platform/drivers/
```

按驱动名搜索：

```bash
ls /sys/bus/platform/drivers/ | grep foo
```

如果驱动是模块，查看是否加载：

```bash
lsmod | grep foo
```

查看模块信息：

```bash
modinfo foo.ko
```

查看模块支持的 alias：

```bash
modinfo foo.ko | grep alias
```

如果 `MODULE_DEVICE_TABLE(of, foo_of_match)` 写对，模块通常会带有 OF alias 信息。

---

## 23. 查看设备和驱动绑定关系

如果设备已经创建，并且驱动已经绑定，通常可以在设备目录中看到 `driver` 符号链接。

例如：

```bash
ls -l /sys/bus/platform/devices/10000000.foo/driver
```

如果没有 `driver` 链接，说明设备还没有绑定驱动。

也可以查看驱动目录下绑定了哪些设备：

```bash
ls /sys/bus/platform/drivers/foo/
```

如果设备名出现在里面，说明绑定成功。

---

## 24. dmesg 排查

查看设备树相关日志：

```bash
dmesg | grep -i "of:"
dmesg | grep -i "device tree"
```

查看目标驱动日志：

```bash
dmesg | grep -i foo
```

查看资源错误：

```bash
dmesg | grep -i clk
dmesg | grep -i reset
dmesg | grep -i irq
dmesg | grep -i gpio
```

如果驱动中有：

```c
dev_info(&pdev->dev, "foo device probed\n");
```

可以直接搜索：

```bash
dmesg | grep -i "foo device probed"
```

建议在调试驱动时，在 probe 开头加一条日志：

```c
dev_info(&pdev->dev, "probe start\n");
```

这样可以区分：

```text
probe 根本没有进
probe 进了但中途失败
```

---

## 25. 手动 bind / unbind 调试

platform driver 支持通过 sysfs 手动解绑和绑定。

查看设备名：

```bash
ls /sys/bus/platform/devices/
```

查看驱动名：

```bash
ls /sys/bus/platform/drivers/
```

解绑：

```bash
echo 10000000.foo > /sys/bus/platform/drivers/foo/unbind
```

绑定：

```bash
echo 10000000.foo > /sys/bus/platform/drivers/foo/bind
```

注意：

> 实际设备名要以 `/sys/bus/platform/devices/` 下显示的名称为准。

这个方法适合调试 probe/remove，但不要在关键系统设备上随便操作，避免系统异常。

---

## 26. DTS 节点、platform_device、platform_driver 对应关系

可以用下面这张表理解：

| DTS 内容 | 内核对象 / 驱动接口 |
|---|---|
| `compatible` | `of_device_id` / `.of_match_table` |
| `reg` | `platform_get_resource()` |
| `interrupts` | `platform_get_irq()` |
| `clocks` / `clock-names` | `devm_clk_get()` |
| `resets` / `reset-names` | `devm_reset_control_get()` |
| `xxx-gpios` | `devm_gpiod_get()` |
| `status` | 决定节点是否参与设备创建 |
| 节点本身 | `platform_device` |
| 匹配成功 | 调用 `platform_driver.probe()` |

---

## 27. 一个完整排查流程

遇到 platform driver 没有 probe，可以按下面顺序排查：

```text
1. 确认内核是否使用 Device Tree 启动
   |
   v
2. 导出 running.dts，确认节点是否存在
   |
   v
3. 确认 status 是否 okay
   |
   v
4. 确认父节点 status 是否 okay
   |
   v
5. 确认 compatible 和 of_match_table 完全一致
   |
   v
6. 确认驱动是否编译进内核或模块是否加载
   |
   v
7. 查看 /sys/bus/platform/devices/ 是否有设备
   |
   v
8. 查看 /sys/bus/platform/drivers/ 是否有驱动
   |
   v
9. 查看设备目录是否有 driver 链接
   |
   v
10. 查看 dmesg，确认 probe 是没进还是进了后失败
```

---

## 28. 常见误区

### 28.1 误区一：DTS 中有节点，驱动就一定会 probe

不一定。

还需要满足：

```text
节点在实际运行 DTB 中存在
status 可用
compatible 匹配
驱动已注册
所在总线能创建设备
```

---

### 28.2 误区二：compatible 写对了就一定能工作

不一定。

`compatible` 只解决匹配问题。

设备真正工作还需要：

```text
reg 正确
interrupts 正确
clock 正确
reset 正确
gpio 正确
pinctrl 正确
驱动初始化逻辑正确
硬件连接正确
```

---

### 28.3 误区三：probe 没日志就是没有 probe

不一定。

可能是：

```text
probe 进了，但没有打印日志
probe 进了，前面某一步失败返回
日志级别过滤了
驱动报错信息被忽略了
```

建议在 probe 开头添加明确日志。

---

### 28.4 误区四：platform_driver 就等于字符设备驱动

不对。

`platform_driver` 是设备和驱动匹配框架。

字符设备、网络设备、输入设备、TTY 设备等是驱动初始化后向内核子系统注册的接口类型。

---

### 28.5 误区五：所有 DTS 节点都会变成 platform_device

不一定。

有些节点是总线节点、描述节点或资源 provider，例如：

```text
chosen
aliases
memory
cpus
gpio-controller
clock-controller
interrupt-controller
pinctrl
```

它们不一定都以普通 platform device 的方式出现在你预期的位置。

---

## 29. 小结

DTS 与 `platform_driver` 的核心关系可以概括为：

```text
DTS 描述硬件节点
  |
  v
Linux 解析 DTB
  |
  v
为可用节点创建 platform_device
  |
  v
platform_driver 注册到 platform bus
  |
  v
compatible 匹配 of_match_table
  |
  v
匹配成功后调用 probe()
```

最关键的对应关系是：

```text
DTS compatible
        |
        v
driver of_match_table
        |
        v
platform_driver probe()
```

驱动进入 `probe()` 后，会继续从 DTS 中获取各种硬件资源：

```text
reg         -> platform_get_resource()
interrupts  -> platform_get_irq()
clocks      -> devm_clk_get()
resets      -> devm_reset_control_get()
gpios       -> devm_gpiod_get()
```

可以用一句话总结：

> DTS 负责描述设备在哪里、叫什么、需要什么资源；platform driver 负责匹配这个设备，并在 probe 中读取这些资源、初始化硬件。
