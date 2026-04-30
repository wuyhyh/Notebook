# 07-Linux驱动开发入门路线

## 1. 文档目标

本文是 Linux 驱动开发部分的入门路线文档，用于指导实习生从最简单的 `hello module` 逐步走到简单的 `platform driver`。

本阶段的目标不是让初学者立刻掌握所有 Linux 驱动框架，而是让他先建立一条清晰主线：

```text
内核模块
  ↓
字符设备
  ↓
设备树节点
  ↓
platform_device / platform_driver 匹配
  ↓
probe() 执行
  ↓
获取 reg / irq 等资源
  ↓
ioremap + readl/writel
  ↓
中断处理
  ↓
sysfs / dmesg / /proc/interrupts 调试
```

完成本阶段学习后，实习生应该能够：

1. 编译、加载、卸载一个简单内核模块；
2. 理解字符设备和 `/dev/xxx` 的基本关系；
3. 理解设备树和 `platform driver` 的匹配关系；
4. 理解 `probe()` 和 `remove()` 的基本作用；
5. 能够从设备树获取寄存器和中断资源；
6. 能够使用 `readl()`、`writel()` 访问 MMIO 寄存器；
7. 能够注册简单中断处理函数；
8. 能够通过 `dmesg`、`sysfs`、`/proc/interrupts` 等工具进行基础调试。

---

## 2. Linux驱动开发到底在做什么

Linux 驱动的作用是让 Linux 内核能够识别、管理和控制硬件设备，并向用户空间提供统一的访问方式。

例如：

| 硬件设备 | 驱动负责的事情 |
|---|---|
| GPIO | 控制引脚输入、输出、电平读取 |
| UART | 初始化串口、收发数据、处理中断 |
| I2C 控制器 | 发起 I2C 传输，管理总线设备 |
| SPI 控制器 | 发起 SPI 传输，管理片选和时序 |
| 网卡 | 管理收发包、中断、DMA、PHY |
| PCIe 设备 | 处理枚举、BAR、中断、DMA 等资源 |
| NVMe 磁盘 | 提供块设备接口，完成高速存储访问 |

对于入门阶段来说，不需要一开始就理解所有复杂设备。当前重点是理解：

1. 驱动如何进入内核；
2. 驱动如何和设备匹配；
3. 驱动如何获取硬件资源；
4. 驱动如何访问寄存器；
5. 驱动如何对外提供接口；
6. 驱动出现问题时如何调试。

---

## 3. 本阶段的学习边界

Linux 驱动开发内容非常多，不能一开始全部学习。对于项目中的实习生，第一阶段只要求掌握基础主线。

本阶段需要学习：

1. 内核模块；
2. 字符设备；
3. 设备树基础；
4. platform driver；
5. `probe()` 和 `remove()`；
6. `compatible` 匹配；
7. `reg` 和 MMIO；
8. `readl()`、`writel()`；
9. 中断申请和中断处理；
10. sysfs 调试接口；
11. 常用驱动调试方法。

本阶段暂时不深入学习：

1. DMA；
2. I2C 设备驱动；
3. SPI 设备驱动；
4. PCIe 驱动；
5. 网络驱动；
6. 块设备驱动；
7. DRM 显示驱动；
8. 电源管理；
9. 内核并发和锁的复杂用法。

这些内容都很重要，但不适合作为第一阶段入门内容。初学者如果连 `probe()`、设备树匹配、MMIO 和中断都没有理解清楚，过早学习 DMA、PCIe、netdev 只会增加混乱。

---

## 4. 学习前置要求

## 4.1 Linux基本操作能力

学习驱动开发前，需要先熟悉 Linux 基本操作，包括：

1. 文件和目录操作；
2. 文本查看和搜索；
3. 软件包安装；
4. SSH、SCP、rsync；
5. systemd 服务管理；
6. `dmesg` 和 `journalctl` 日志查看；
7. 基本网络配置；
8. 磁盘挂载和文件系统基础。

驱动调试中常用命令：

```bash
uname -a
lsmod
modinfo xxx.ko
dmesg -w
journalctl -k -f
cat /proc/interrupts
cat /proc/iomem
ls /sys/bus/platform/devices/
ls /sys/bus/platform/drivers/
```

如果这些命令不会用，后面的驱动实验会很难推进。

## 4.2 C语言基础能力

Linux 内核和驱动主要使用 C 语言编写，需要掌握：

1. 变量、函数、数组、指针；
2. 结构体；
3. 函数指针；
4. 宏定义；
5. 位运算；
6. 头文件；
7. Makefile；
8. GCC 编译流程。

驱动中经常出现类似结构：

```c
struct my_device {
	void __iomem *base;
	int irq;
	struct device *dev;
};
```

这里需要理解：

1. `struct my_device` 是驱动私有数据结构；
2. `void __iomem *base` 是寄存器映射后的虚拟地址；
3. `irq` 是中断号；
4. `struct device *dev` 是 Linux 设备模型中的设备对象。

## 4.3 操作系统和计算机组成基础

驱动开发直接面对硬件和内核，需要理解一些基本概念：

1. 用户态和内核态；
2. 虚拟地址和物理地址；
3. MMU；
4. Cache；
5. 中断；
6. DMA 的基本概念；
7. MMIO；
8. 设备文件；
9. 系统调用；
10. 总线和外设。

本阶段不要求深入掌握所有底层细节，但至少要知道这些概念在驱动中为什么会出现。

---

## 5. 第一阶段：hello kernel module

## 5.1 学习目标

第一步是写一个最简单的内核模块，让实习生理解：

1. `.ko` 文件是什么；
2. 模块如何编译；
3. 模块如何加载；
4. 模块如何卸载；
5. 内核日志如何查看。

## 5.2 最小模块示例

```c
#include <linux/module.h>
#include <linux/init.h>

static int __init hello_init(void)
{
	pr_info("hello driver init\n");
	return 0;
}

static void __exit hello_exit(void)
{
	pr_info("hello driver exit\n");
}

module_init(hello_init);
module_exit(hello_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("training");
MODULE_DESCRIPTION("hello kernel module");
```

## 5.3 常用操作命令

```bash
make
sudo insmod hello.ko
lsmod | grep hello
dmesg | tail
sudo rmmod hello
dmesg | tail
```

## 5.4 本阶段需要理解的重点

1. `module_init()` 指定模块加载入口；
2. `module_exit()` 指定模块卸载入口；
3. `pr_info()` 用于输出内核日志；
4. `insmod` 用于加载模块；
5. `rmmod` 用于卸载模块；
6. `dmesg` 用于查看内核日志；
7. 模块必须和当前运行内核版本匹配。

---

## 6. 第二阶段：字符设备驱动基础

## 6.1 学习目标

字符设备驱动用于让用户空间通过 `/dev/xxx` 访问内核驱动。

本阶段需要理解：

1. 字符设备是什么；
2. 主设备号和次设备号是什么；
3. `/dev/xxx` 设备节点是什么；
4. `file_operations` 是什么；
5. 用户程序如何通过 `open()`、`read()`、`write()` 访问驱动。

## 6.2 file_operations示例

```c
static const struct file_operations my_fops = {
	.owner = THIS_MODULE,
	.open = my_open,
	.read = my_read,
	.write = my_write,
};
```

用户空间访问：

```bash
echo hello > /dev/mydev
cat /dev/mydev
```

驱动中对应执行：

1. 打开设备时进入 `my_open()`；
2. 读取设备时进入 `my_read()`；
3. 写入设备时进入 `my_write()`。

## 6.3 本阶段需要理解的重点

字符设备驱动的核心意义是让实习生明白：

```text
用户空间程序
  ↓
/dev/xxx
  ↓
file_operations
  ↓
驱动中的 open/read/write
  ↓
内核或硬件资源
```

这一阶段不需要深入 `ioctl`、`poll`、`mmap` 等复杂接口。先把 `open/read/write` 跑通即可。

---

## 7. 第三阶段：platform driver最小实验

## 7.1 学习目标

`platform driver` 是嵌入式 Linux 驱动开发中非常重要的基础框架。

本阶段需要理解：

1. 什么是 `platform_device`；
2. 什么是 `platform_driver`；
3. 设备树如何描述设备；
4. 驱动如何通过 `compatible` 匹配设备；
5. 匹配成功后为什么会调用 `probe()`。

## 7.2 最小设备树节点示例

```dts
mydev@28000000 {
	compatible = "training,mydev";
	reg = <0x0 0x28000000 0x0 0x1000>;
	status = "okay";
};
```

## 7.3 最小platform driver示例

```c
static int mydev_probe(struct platform_device *pdev)
{
	dev_info(&pdev->dev, "mydev probe\n");
	return 0;
}

static int mydev_remove(struct platform_device *pdev)
{
	dev_info(&pdev->dev, "mydev remove\n");
	return 0;
}

static const struct of_device_id mydev_of_match[] = {
	{ .compatible = "training,mydev" },
	{ }
};
MODULE_DEVICE_TABLE(of, mydev_of_match);

static struct platform_driver mydev_driver = {
	.probe = mydev_probe,
	.remove = mydev_remove,
	.driver = {
		.name = "mydev",
		.of_match_table = mydev_of_match,
	},
};

module_platform_driver(mydev_driver);
```

## 7.4 本阶段需要理解的重点

这部分是 Linux 驱动入门的关键。

必须理解下面这条链路：

```text
DTS 中描述设备节点
  ↓
内核解析设备树
  ↓
创建 platform_device
  ↓
platform_driver 注册到内核
  ↓
compatible 匹配成功
  ↓
调用 probe()
```

如果 `probe()` 没有执行，通常要优先检查：

1. DTS 节点是否存在；
2. `status` 是否为 `okay`；
3. `compatible` 字符串是否完全一致；
4. 驱动是否已经加载；
5. 内核配置是否启用了相关驱动；
6. dmesg 中是否有报错。

---

## 8. 第四阶段：probe与remove函数

## 8.1 probe函数的作用

`probe()` 是驱动和设备匹配成功后执行的初始化函数。

通常在 `probe()` 中完成：

1. 分配驱动私有数据；
2. 保存 `struct device` 指针；
3. 获取设备树资源；
4. 映射寄存器；
5. 获取中断号；
6. 申请中断；
7. 初始化硬件；
8. 注册字符设备、sysfs、子系统接口等；
9. 调用 `platform_set_drvdata()` 保存私有数据。

常见代码：

```c
struct my_device *priv;

priv = devm_kzalloc(&pdev->dev, sizeof(*priv), GFP_KERNEL);
if (!priv)
	return -ENOMEM;

priv->dev = &pdev->dev;
platform_set_drvdata(pdev, priv);
```

## 8.2 remove函数的作用

`remove()` 在设备移除或驱动卸载时执行。

通常用于释放资源、关闭硬件、注销接口。

如果使用 `devm_` 系列接口，很多资源会在设备解绑时自动释放，例如：

1. `devm_kzalloc()`；
2. `devm_ioremap_resource()`；
3. `devm_request_irq()`。

所以入门阶段应该优先使用 `devm_` 系列接口，减少资源释放错误。

## 8.3 probe返回值的含义

`probe()` 返回 `0` 表示成功。

常见错误码：

| 错误码 | 含义 |
|---|---|
| `-ENOMEM` | 内存分配失败 |
| `-EINVAL` | 参数错误或设备树资源错误 |
| `-ENODEV` | 没有找到设备 |
| `-EBUSY` | 资源被占用 |
| `-EPROBE_DEFER` | 依赖资源暂时未准备好，稍后重试 |

调试驱动时，一个非常重要的原则是：

```text
先确认 probe 有没有进入，再分析后面的寄存器、中断和数据通路。
```

---

## 9. 第五阶段：of_match_table与compatible匹配

## 9.1 compatible的作用

设备树中的 `compatible` 用于描述设备兼容的硬件类型。

示例：

```dts
mydev@28000000 {
	compatible = "training,mydev";
	reg = <0x0 0x28000000 0x0 0x1000>;
	status = "okay";
};
```

驱动中的匹配表：

```c
static const struct of_device_id mydev_of_match[] = {
	{ .compatible = "training,mydev" },
	{ }
};
MODULE_DEVICE_TABLE(of, mydev_of_match);
```

只有两边字符串匹配，驱动才会绑定到该设备，并调用 `probe()`。

## 9.2 常见错误

1. DTS 中 `compatible` 拼写错误；
2. 驱动中 `compatible` 拼写错误；
3. DTS 节点没有编译进当前使用的 DTB；
4. 实际启动时使用的不是修改后的 DTB；
5. `status` 是 `disabled`；
6. 驱动没有加载；
7. 内核配置没有打开。

## 9.3 验证方法

查看运行时设备树：

```bash
ls /proc/device-tree/
find /proc/device-tree -name '*mydev*'
```

查看 platform 设备：

```bash
ls /sys/bus/platform/devices/
```

查看 platform 驱动：

```bash
ls /sys/bus/platform/drivers/
```

查看日志：

```bash
dmesg | grep mydev
```

---

## 10. 第六阶段：ioremap、readl、writel基础

## 10.1 MMIO是什么

很多外设寄存器不是通过普通变量访问的，而是映射到 CPU 的地址空间中。CPU 访问某些地址时，实际是在访问硬件寄存器，这种方式称为 MMIO。

驱动中不能把 MMIO 地址当普通内存随便访问，应该使用内核提供的接口。

## 10.2 从设备树获取reg资源

设备树中常见写法：

```dts
mydev@28000000 {
	compatible = "training,mydev";
	reg = <0x0 0x28000000 0x0 0x1000>;
	status = "okay";
};
```

这里表示设备寄存器物理地址从 `0x28000000` 开始，大小为 `0x1000`。

驱动中可以使用：

```c
priv->base = devm_platform_ioremap_resource(pdev, 0);
if (IS_ERR(priv->base))
	return PTR_ERR(priv->base);
```

## 10.3 访问寄存器

定义寄存器偏移：

```c
#define REG_CTRL	0x00
#define REG_STATUS	0x04
#define CTRL_ENABLE	BIT(0)
```

写寄存器：

```c
writel(CTRL_ENABLE, priv->base + REG_CTRL);
```

读寄存器：

```c
val = readl(priv->base + REG_STATUS);
```

读改写：

```c
val = readl(priv->base + REG_CTRL);
val |= CTRL_ENABLE;
writel(val, priv->base + REG_CTRL);
```

## 10.4 本阶段需要理解的重点

1. `reg` 描述硬件寄存器物理地址；
2. `ioremap` 把物理地址映射为内核可访问的虚拟地址；
3. `readl()` 用于读取 32 bit MMIO 寄存器；
4. `writel()` 用于写入 32 bit MMIO 寄存器；
5. 不要直接把寄存器地址强转成普通指针访问；
6. 修改寄存器某一位时，通常需要读改写。

---

## 11. 第七阶段：中断申请与中断处理

## 11.1 中断的作用

中断用于让硬件主动通知 CPU 某个事件已经发生。

例如：

1. 串口收到数据；
2. 网卡收到数据包；
3. DMA 传输完成；
4. GPIO 电平变化；
5. 设备发生错误。

如果没有中断，CPU 可能需要不断轮询寄存器，效率很低。

## 11.2 设备树中的中断描述

示例：

```dts
mydev@28000000 {
	compatible = "training,mydev";
	reg = <0x0 0x28000000 0x0 0x1000>;
	interrupts = <0 45 4>;
	status = "okay";
};
```

具体 `interrupts` 的格式和中断控制器有关，入门阶段先知道它用于描述设备连接到哪个中断即可。

## 11.3 驱动中获取和申请中断

获取中断号：

```c
priv->irq = platform_get_irq(pdev, 0);
if (priv->irq < 0)
	return priv->irq;
```

申请中断：

```c
ret = devm_request_irq(&pdev->dev, priv->irq, mydev_irq_handler,
		       0, dev_name(&pdev->dev), priv);
if (ret)
	return ret;
```

中断处理函数：

```c
static irqreturn_t mydev_irq_handler(int irq, void *data)
{
	struct my_device *priv = data;
	u32 status;

	status = readl(priv->base + REG_IRQ_STATUS);
	if (!status)
		return IRQ_NONE;

	writel(status, priv->base + REG_IRQ_CLEAR);

	return IRQ_HANDLED;
}
```

## 11.4 中断调试方法

查看中断计数：

```bash
cat /proc/interrupts
```

查看日志：

```bash
dmesg -w
```

中断调试时需要确认：

1. 中断号是否获取成功；
2. `request_irq()` 是否成功；
3. 硬件是否真的触发中断；
4. `/proc/interrupts` 中计数是否增加；
5. 中断状态寄存器是否正确；
6. 是否正确清除了中断；
7. 中断处理函数中是否做了不该做的阻塞操作。

---

## 12. 第八阶段：sysfs属性节点实验

## 12.1 sysfs的作用

sysfs 是内核向用户空间暴露设备、驱动和内核对象信息的一种方式。

驱动中可以通过 sysfs 暴露一些简单调试接口，例如：

```text
/sys/bus/platform/devices/xxx/status
/sys/bus/platform/devices/xxx/enable
/sys/bus/platform/devices/xxx/reg
```

用户可以通过 `cat` 读取，也可以通过 `echo` 写入。

## 12.2 典型用途

sysfs 适合用于：

1. 查看设备状态；
2. 打开或关闭简单功能；
3. 读取寄存器状态；
4. 修改简单配置；
5. 做驱动调试入口。

sysfs 不适合用于：

1. 大量数据传输；
2. 高频实时控制；
3. 复杂二进制协议；
4. 替代正式用户态接口。

## 12.3 基本访问方式

读取：

```bash
cat /sys/bus/platform/devices/xxx/status
```

写入：

```bash
echo 1 > /sys/bus/platform/devices/xxx/enable
```

## 12.4 本阶段需要理解的重点

1. sysfs 是驱动调试常用接口；
2. sysfs 属性通常是文本形式；
3. `show()` 负责读；
4. `store()` 负责写；
5. sysfs 接口要保持简单；
6. 不要把 sysfs 当成高性能数据通道。

---

## 13. 第九阶段：驱动调试常用方法

## 13.1 调试基本原则

驱动调试不要一上来猜测复杂问题，应该按固定顺序排查：

```text
1. 当前运行的内核版本是否正确？
2. 模块是否成功加载？
3. DTS 是否是当前正在使用的版本？
4. DTS 节点是否存在？
5. status 是否为 okay？
6. compatible 是否匹配？
7. probe 是否进入？
8. reg 是否获取成功？
9. ioremap 是否成功？
10. irq 是否获取成功？
11. request_irq 是否成功？
12. 中断计数是否变化？
13. dmesg 是否有报错？
```

## 13.2 查看内核日志

```bash
dmesg -w
journalctl -k -f
```

驱动中常用打印：

```c
dev_info(dev, "init ok\n");
dev_err(dev, "failed to get irq\n");
dev_dbg(dev, "debug value = %u\n", value);
```

在驱动代码中，优先使用 `dev_info()`、`dev_err()`、`dev_dbg()`，因为它们会自动带上设备信息。

## 13.3 查看模块信息

```bash
lsmod
modinfo xxx.ko
```

重点确认：

1. 模块是否已经加载；
2. 模块依赖是否正确；
3. 模块 vermagic 是否匹配当前内核。

## 13.4 查看platform设备和驱动

```bash
ls /sys/bus/platform/devices/
ls /sys/bus/platform/drivers/
```

如果设备没有出现在 `/sys/bus/platform/devices/`，可能是设备树没有生效或节点状态不正确。

如果驱动没有出现在 `/sys/bus/platform/drivers/`，可能是驱动没有编译或没有加载。

## 13.5 查看中断

```bash
cat /proc/interrupts
```

重点看：

1. 是否有对应中断项；
2. 中断计数是否增加；
3. 中断名称是否符合预期；
4. 中断是否集中在某些 CPU 上。

## 13.6 查看IO资源

```bash
cat /proc/iomem
```

可以用于确认设备寄存器地址资源是否被内核记录。

## 13.7 反编译DTB

```bash
dtc -I dtb -O dts -o out.dts board.dtb
```

如果怀疑设备树没有生效，需要反编译当前实际启动使用的 DTB，而不是只看源码中的 `.dts` 文件。

---

## 14. 推荐文档顺序

本章节建议按下面顺序整理和学习：

```text
07-Linux驱动开发入门路线.md
07-hello-kernel-module实验.md
07-字符设备驱动基础.md
07-platform-driver最小实验.md
07-probe与remove函数说明.md
07-of_match_table与compatible匹配.md
07-ioremap-readl-writel基础.md
07-中断申请与中断处理函数基础.md
07-sysfs属性节点实验.md
07-驱动调试常用方法.md
```

这个顺序对应的能力递进是：

```text
能加载模块
  ↓
能理解 /dev/xxx
  ↓
能理解 platform driver
  ↓
能理解 probe 生命周期
  ↓
能理解 DTS 与 compatible 匹配
  ↓
能访问 MMIO 寄存器
  ↓
能申请和处理中断
  ↓
能用 sysfs 做简单调试
  ↓
能用常用命令排查问题
```

---

## 15. 暂缓学习的内容

下面这些内容后续会用到，但不建议放在本阶段第一批学习材料中：

| 内容 | 建议放到后续章节的原因 |
|---|---|
| DMA | 涉及地址映射、Cache 一致性、IOMMU，入门阶段过早 |
| I2C/SPI 驱动 | 属于具体总线框架，应在 platform 基础之后学习 |
| GPIO 子系统 | 可以作为常见外设专题，不必放在第一批主线里 |
| pinctrl/clock/reset | 与板级资源强相关，适合后续结合项目学习 |
| PCIe 驱动 | 涉及枚举、BAR、MSI、DMA，复杂度较高 |
| 网络驱动 | 涉及 netdev、NAPI、PHY、DMA，复杂度较高 |
| 块设备驱动 | 涉及块层、请求队列、存储协议，复杂度较高 |

本阶段应该先让实习生把基础链路跑通，而不是追求覆盖所有驱动类型。

---

## 16. 实习生阶段性能力要求

## 16.1 入门合格

能够：

1. 编译一个 `.ko`；
2. 使用 `insmod` 加载模块；
3. 使用 `rmmod` 卸载模块；
4. 使用 `dmesg` 查看日志；
5. 知道 `module_init()` 和 `module_exit()` 的作用。

## 16.2 基础可用

能够：

1. 看懂简单字符设备驱动；
2. 理解 `/dev/xxx` 和 `file_operations`；
3. 看懂最小 `platform_driver`；
4. 知道 `probe()` 什么时候执行；
5. 知道 `compatible` 如何匹配。

## 16.3 项目辅助可用

能够：

1. 修改简单 DTS 节点；
2. 判断 DTS 是否生效；
3. 判断 `probe()` 是否进入；
4. 从设备树获取 `reg` 和 `irq`；
5. 使用 `readl()` 和 `writel()` 访问寄存器；
6. 查看 `/proc/interrupts` 判断中断是否触发；
7. 使用 sysfs 进行简单调试；
8. 整理问题现象、操作步骤和日志。

---

## 17. 实验过程要求

为了减少沟通成本，实习生做实验时必须养成记录习惯。

每次实验至少记录：

1. 实验目标；
2. 当前内核版本；
3. 当前 DTB 文件；
4. 修改了哪些文件；
5. 执行了哪些命令；
6. 期望现象是什么；
7. 实际现象是什么；
8. dmesg 关键日志；
9. 问题分析；
10. 最终结论。

建议记录模板：

```text
实验名称：
实验目标：
内核版本：
DTB版本：
修改文件：
执行命令：
预期现象：
实际现象：
关键日志：
问题分析：
结论：
```

这比单纯问“为什么不行”更有效，也能帮助负责人快速判断问题。

---

## 18. 小结

本阶段的 Linux 驱动开发入门路线可以概括为一句话：

```text
先让驱动进内核，再让驱动匹配设备，然后获取资源、访问寄存器、处理中断，最后学会用日志和 sysfs 调试。
```

对于项目实习生来说，第一阶段最重要的不是掌握多少复杂 API，而是建立下面这条主线：

```text
DTS 描述硬件
  ↓
内核创建设备
  ↓
驱动通过 compatible 匹配
  ↓
probe 执行
  ↓
获取 reg / irq
  ↓
访问寄存器
  ↓
处理中断
  ↓
通过 dmesg / sysfs / proc 调试
```

只要这条主线清楚，后面学习 I2C、SPI、DMA、PCIe、网络驱动时，就不会完全迷失方向。
