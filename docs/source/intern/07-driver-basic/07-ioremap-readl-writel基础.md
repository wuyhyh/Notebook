# 07-ioremap-readl-writel基础

## 1. 文档目标

本文用于说明 Linux 驱动开发中最基础、最常见的一类操作：

```text
访问硬件寄存器
```

在嵌入式 Linux 驱动中，很多外设都是通过 MMIO 寄存器控制的。驱动需要先把设备树中的 `reg` 资源映射到内核虚拟地址，然后使用 `readl()`、`writel()` 等接口访问寄存器。

完成本文后，应该能够理解：

1. 什么是 MMIO；
2. 设备树中的 `reg` 属性描述了什么；
3. 为什么不能直接访问物理地址；
4. `ioremap` 的作用是什么；
5. `readl()` 和 `writel()` 如何使用；
6. 如何在 `platform driver` 中获取并映射寄存器资源；
7. 寄存器读改写时应该注意什么；
8. 如何排查寄存器访问相关问题。

---

## 2. 为什么驱动需要访问寄存器

硬件设备通常通过寄存器提供控制接口。

例如，一个简单外设可能有下面几个寄存器：

| 偏移 | 名称 | 作用 |
|---|---|---|
| `0x00` | `CTRL` | 控制寄存器 |
| `0x04` | `STATUS` | 状态寄存器 |
| `0x08` | `DATA` | 数据寄存器 |
| `0x0c` | `IRQ_STATUS` | 中断状态寄存器 |
| `0x10` | `IRQ_ENABLE` | 中断使能寄存器 |

驱动通过读写这些寄存器控制硬件，例如：

```text
写 CTRL 寄存器：启动设备
读 STATUS 寄存器：查看设备状态
写 DATA 寄存器：发送数据
读 DATA 寄存器：接收数据
写 IRQ_ENABLE：打开中断
读 IRQ_STATUS：判断中断原因
```

所以，驱动开发中经常会看到：

```c
val = readl(base + REG_STATUS);
writel(CTRL_ENABLE, base + REG_CTRL);
```

这类代码就是在访问硬件寄存器。

---

## 3. 什么是MMIO

MMIO 是 Memory Mapped I/O 的缩写，中文通常叫：

```text
内存映射 I/O
```

它的意思是：

```text
硬件寄存器被映射到 CPU 的地址空间中，
CPU 可以通过类似访问内存地址的方式访问这些寄存器。
```

但是要注意：

```text
MMIO 地址看起来像内存地址，
但它背后不是普通 DRAM，
而是硬件设备寄存器。
```

例如：

```text
0x28000000 ~ 0x28000fff
```

这段地址可能不是内存，而是某个外设的寄存器窗口。

CPU 对这个地址范围执行读写，实际上会变成对硬件设备寄存器的访问。

---

## 4. 普通内存和MMIO的区别

普通内存和 MMIO 的区别非常重要。

| 项目 | 普通内存 | MMIO |
|---|---|---|
| 背后对象 | DRAM | 硬件寄存器 |
| 访问目的 | 存取数据 | 控制硬件 |
| 是否可以缓存 | 通常可以 | 通常不应该普通缓存 |
| 是否可以随意优化 | 编译器和 CPU 可做优化 | 需要严格顺序和访问语义 |
| 访问接口 | 普通指针 | `readl()` / `writel()` |
| 错误访问后果 | 程序异常或数据错误 | 可能导致硬件异常、总线错误、系统卡死 |

因此，在 Linux 驱动中，不应该这样访问寄存器：

```c
*(volatile u32 *)(addr) = val;
```

而应该使用：

```c
writel(val, base + offset);
val = readl(base + offset);
```

---

## 5. 设备树中的reg属性

设备树中，`reg` 属性用于描述设备的寄存器资源。

示例：

```dts
my_demo@28000000 {
	compatible = "training,my-demo";
	reg = <0x0 0x28000000 0x0 0x1000>;
	status = "okay";
};
```

这里的：

```dts
reg = <0x0 0x28000000 0x0 0x1000>;
```

表示这个设备的寄存器资源为：

```text
起始物理地址：0x0000000028000000
长度：        0x1000
```

在 ARM64 设备树中，经常使用 64 位地址和 64 位长度，所以会写成 4 个 cell：

```text
地址高32位 地址低32位 长度高32位 长度低32位
```

即：

```text
0x0 0x28000000 0x0 0x1000
```

如果父节点的 `#address-cells` 和 `#size-cells` 不同，`reg` 的写法也会不同。因此实际项目中要结合父节点定义理解。

---

## 6. 物理地址不能直接在内核中使用

设备树中的 `reg` 描述的是物理地址范围。

但是 Linux 内核运行时，代码访问的是虚拟地址。

所以不能直接这样写：

```c
void __iomem *base = (void __iomem *)0x28000000;
writel(1, base + 0x00);
```

正确流程是：

```text
从设备树获取物理地址资源
  ↓
通过 ioremap 映射成内核可访问的虚拟地址
  ↓
使用 readl/writel 访问映射后的地址
```

也就是：

```text
物理地址不能直接用；
要先映射，后访问。
```

---

## 7. ioremap的作用

`ioremap()` 的作用是把一段设备物理地址映射到内核虚拟地址空间。

可以简单理解为：

```text
ioremap()
  输入：设备寄存器物理地址
  输出：内核可以访问的虚拟地址
```

传统写法类似：

```c
base = ioremap(res->start, resource_size(res));
if (!base)
	return -ENOMEM;
```

释放时需要：

```c
iounmap(base);
```

但是在现代 `platform driver` 中，更推荐使用 `devm_` 管理接口，例如：

```c
base = devm_platform_ioremap_resource(pdev, 0);
if (IS_ERR(base))
	return PTR_ERR(base);
```

这样更简单，也更不容易漏释放资源。

---

## 8. __iomem是什么意思

驱动中经常看到：

```c
void __iomem *base;
```

这里的 `__iomem` 是一个标记，用于说明这个指针指向的是 I/O memory 区域，而不是普通内存。

它提醒开发者和静态检查工具：

```text
这个地址不能当普通内存指针乱用；
应该通过 readl/writel 等 I/O 访问接口访问。
```

例如：

```c
struct my_demo_dev {
	struct device *dev;
	void __iomem *base;
};
```

其中：

```c
void __iomem *base;
```

表示 `base` 是映射后的 MMIO 基地址。

---

## 9. readl和writel基础

`readl()` 用于从 MMIO 寄存器读取 32 位值：

```c
u32 val;

val = readl(base + REG_STATUS);
```

`writel()` 用于向 MMIO 寄存器写入 32 位值：

```c
writel(CTRL_ENABLE, base + REG_CTRL);
```

常用接口还有：

| 接口 | 作用 |
|---|---|
| `readb()` | 读取 8 位 |
| `readw()` | 读取 16 位 |
| `readl()` | 读取 32 位 |
| `readq()` | 读取 64 位 |
| `writeb()` | 写入 8 位 |
| `writew()` | 写入 16 位 |
| `writel()` | 写入 32 位 |
| `writeq()` | 写入 64 位 |

实际使用哪个接口，要看硬件手册中寄存器宽度和访问要求。

多数 SoC 外设寄存器使用 32 位访问，所以入门阶段最常见的是：

```c
readl()
writel()
```

---

## 10. 寄存器偏移和宏定义

驱动代码中通常不会直接写裸数字，而是定义寄存器偏移和位含义。

例如：

```c
#define MY_REG_CTRL		0x00
#define MY_REG_STATUS		0x04
#define MY_REG_DATA		0x08

#define MY_CTRL_ENABLE		BIT(0)
#define MY_CTRL_RESET		BIT(1)
#define MY_STATUS_BUSY		BIT(0)
#define MY_STATUS_READY		BIT(1)
```

访问时写成：

```c
writel(MY_CTRL_ENABLE, priv->base + MY_REG_CTRL);

val = readl(priv->base + MY_REG_STATUS);
if (val & MY_STATUS_READY)
	dev_info(priv->dev, "device ready\n");
```

这样比直接写：

```c
writel(1, base + 0);
```

可读性好很多，也方便对照芯片手册。

---

## 11. 读改写操作

很多寄存器需要只修改某一位，保留其他位不变。

这种情况下要使用读改写：

```c
u32 val;

val = readl(base + MY_REG_CTRL);
val |= MY_CTRL_ENABLE;
writel(val, base + MY_REG_CTRL);
```

关闭某一位：

```c
val = readl(base + MY_REG_CTRL);
val &= ~MY_CTRL_ENABLE;
writel(val, base + MY_REG_CTRL);
```

修改某个字段：

```c
#define MY_CTRL_MODE_MASK	GENMASK(5, 4)
#define MY_CTRL_MODE_SHIFT	4

val = readl(base + MY_REG_CTRL);
val &= ~MY_CTRL_MODE_MASK;
val |= (mode << MY_CTRL_MODE_SHIFT) & MY_CTRL_MODE_MASK;
writel(val, base + MY_REG_CTRL);
```

读改写要注意：

```text
1. 不要误清除其他位；
2. 注意写 1 清除位，也就是 W1C 位；
3. 注意只读位和保留位；
4. 不要向 reserved bit 写入随意值；
5. 多线程或中断并发访问时需要加锁。
```

---

## 12. W1C寄存器要特别小心

有些状态寄存器是 W1C 类型：

```text
Write 1 Clear
```

意思是：

```text
向某一位写 1，会清除该状态位；
写 0，不影响该位。
```

例如中断状态寄存器：

```c
status = readl(base + MY_REG_IRQ_STATUS);

if (status & MY_IRQ_RX_DONE)
	writel(MY_IRQ_RX_DONE, base + MY_REG_IRQ_STATUS);
```

不要对 W1C 寄存器做普通读改写：

```c
val = readl(base + MY_REG_IRQ_STATUS);
val |= MY_IRQ_RX_DONE;
writel(val, base + MY_REG_IRQ_STATUS);
```

这种写法可能会把其他已经置位的状态也一起清掉。

正确做法要根据芯片手册确认。

---

## 13. devm_platform_ioremap_resource

在 `platform driver` 中，最推荐的入门写法是：

```c
base = devm_platform_ioremap_resource(pdev, 0);
if (IS_ERR(base))
	return PTR_ERR(base);
```

它会完成几件事：

```text
1. 获取第 0 个 memory resource
2. 检查资源合法性
3. 申请资源区域
4. ioremap 映射寄存器
5. 返回 __iomem 虚拟地址
6. 设备解绑时自动释放资源
```

完整示例：

```c
struct my_demo_dev {
	struct device *dev;
	void __iomem *base;
};

static int my_demo_probe(struct platform_device *pdev)
{
	struct device *dev = &pdev->dev;
	struct my_demo_dev *priv;
	u32 val;

	priv = devm_kzalloc(dev, sizeof(*priv), GFP_KERNEL);
	if (!priv)
		return -ENOMEM;

	priv->dev = dev;

	priv->base = devm_platform_ioremap_resource(pdev, 0);
	if (IS_ERR(priv->base)) {
		dev_err(dev, "failed to map registers\n");
		return PTR_ERR(priv->base);
	}

	val = readl(priv->base + MY_REG_STATUS);
	dev_info(dev, "status = 0x%08x\n", val);

	platform_set_drvdata(pdev, priv);

	return 0;
}
```

这里的 `0` 表示使用设备树 `reg` 中的第 0 组资源。

---

## 14. platform_get_resource加devm_ioremap_resource写法

有时也会看到分两步的写法：

```c
struct resource *res;

res = platform_get_resource(pdev, IORESOURCE_MEM, 0);
base = devm_ioremap_resource(dev, res);
if (IS_ERR(base))
	return PTR_ERR(base);
```

这种写法和：

```c
base = devm_platform_ioremap_resource(pdev, 0);
```

作用类似，只是后者更简洁。

分两步写的好处是可以打印资源地址：

```c
res = platform_get_resource(pdev, IORESOURCE_MEM, 0);
if (!res)
	return -ENODEV;

dev_info(dev, "res start = %pa, size = %pa\n",
	 &res->start, &(resource_size(res)));

base = devm_ioremap_resource(dev, res);
if (IS_ERR(base))
	return PTR_ERR(base);
```

注意：实际打印 `resource_size(res)` 时通常要先保存到变量，避免取临时值地址不规范。

更稳妥写法：

```c
resource_size_t size;

size = resource_size(res);
dev_info(dev, "res start = %pa, size = %pa\n",
	 &res->start, &size);
```

---

## 15. 最小实验代码

下面给出一个最小的 MMIO 映射和寄存器读取实验代码。

注意：这个实验需要设备树中有合法的 `reg` 资源。不要随意映射真实硬件中不属于你的地址。

```c
#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/of.h>
#include <linux/io.h>

#define MY_REG_STATUS	0x00
#define MY_REG_CTRL	0x04

struct my_mmio_demo {
	struct device *dev;
	void __iomem *base;
};

static int my_mmio_demo_probe(struct platform_device *pdev)
{
	struct device *dev = &pdev->dev;
	struct my_mmio_demo *priv;
	u32 val;

	dev_info(dev, "probe start\n");

	priv = devm_kzalloc(dev, sizeof(*priv), GFP_KERNEL);
	if (!priv)
		return -ENOMEM;

	priv->dev = dev;

	priv->base = devm_platform_ioremap_resource(pdev, 0);
	if (IS_ERR(priv->base)) {
		dev_err(dev, "failed to map mmio resource\n");
		return PTR_ERR(priv->base);
	}

	val = readl(priv->base + MY_REG_STATUS);
	dev_info(dev, "status register = 0x%08x\n", val);

	platform_set_drvdata(pdev, priv);

	dev_info(dev, "probe done\n");

	return 0;
}

static int my_mmio_demo_remove(struct platform_device *pdev)
{
	dev_info(&pdev->dev, "remove called\n");
	return 0;
}

static const struct of_device_id my_mmio_demo_of_match[] = {
	{ .compatible = "training,my-mmio-demo" },
	{ }
};

MODULE_DEVICE_TABLE(of, my_mmio_demo_of_match);

static struct platform_driver my_mmio_demo_driver = {
	.probe = my_mmio_demo_probe,
	.remove = my_mmio_demo_remove,
	.driver = {
		.name = "my_mmio_demo",
		.of_match_table = my_mmio_demo_of_match,
	},
};

module_platform_driver(my_mmio_demo_driver);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("training");
MODULE_DESCRIPTION("ioremap readl writel demo");
```

---

## 16. 对应DTS节点示例

示例设备树节点：

```dts
my_mmio_demo@28000000 {
	compatible = "training,my-mmio-demo";
	reg = <0x0 0x28000000 0x0 0x1000>;
	status = "okay";
};
```

注意：

```text
这个地址只是示例。
实际项目中必须使用芯片手册、原理图和 SoC 地址映射表中确认过的地址。
不要随便映射和访问未知地址。
```

如果访问了不存在的 MMIO 地址，可能出现：

1. synchronous external abort；
2. kernel panic；
3. 总线错误；
4. 系统卡死；
5. 读到全 0 或全 1；
6. 触发未知硬件行为。

---

## 17. Makefile示例

```makefile
obj-m += my_mmio_demo.o

KDIR ?= /lib/modules/$(shell uname -r)/build
PWD  := $(shell pwd)

all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
```

编译：

```bash
make
```

加载：

```bash
sudo insmod my_mmio_demo.ko
```

查看日志：

```bash
dmesg | tail -n 50
```

卸载：

```bash
sudo rmmod my_mmio_demo
```

---

## 18. 如何查看资源是否进入系统

查看运行时设备树：

```bash
find /proc/device-tree/ -name '*mmio*'
strings /proc/device-tree/路径/compatible
```

查看 platform 设备：

```bash
find /sys/bus/platform/devices/ -name '*mmio*'
```

查看系统 I/O memory 资源：

```bash
cat /proc/iomem
```

可以尝试搜索地址：

```bash
grep -i 28000000 /proc/iomem
```

如果驱动成功申请了资源，有时能在 `/proc/iomem` 中看到类似记录。

---

## 19. 常见错误1：直接使用物理地址

错误写法：

```c
#define BASE 0x28000000

writel(1, (void __iomem *)(BASE + 0x00));
```

问题是：

```text
0x28000000 是物理地址，不是当前内核可以直接访问的虚拟地址。
```

正确写法：

```c
base = devm_platform_ioremap_resource(pdev, 0);
writel(1, base + 0x00);
```

---

## 20. 常见错误2：把MMIO当普通内存访问

错误写法：

```c
*(u32 *)(base + MY_REG_CTRL) = MY_CTRL_ENABLE;
```

或者：

```c
val = *(u32 *)(base + MY_REG_STATUS);
```

正确写法：

```c
writel(MY_CTRL_ENABLE, base + MY_REG_CTRL);
val = readl(base + MY_REG_STATUS);
```

原因是：

```text
MMIO 需要使用内核提供的 I/O 访问接口，
这些接口包含了体系结构相关的访问语义。
```

---

## 21. 常见错误3：没有检查ioremap返回值

错误写法：

```c
base = devm_platform_ioremap_resource(pdev, 0);
val = readl(base + MY_REG_STATUS);
```

如果映射失败，`base` 是错误指针，继续访问会导致异常。

正确写法：

```c
base = devm_platform_ioremap_resource(pdev, 0);
if (IS_ERR(base))
	return PTR_ERR(base);

val = readl(base + MY_REG_STATUS);
```

---

## 22. 常见错误4：reg写错

如果 DTS 中 `reg` 地址或长度写错，可能导致：

1. 映射失败；
2. 访问错误设备；
3. 读到错误值；
4. 系统异常；
5. 与其他设备资源冲突。

排查：

```bash
dtc -I dtb -O dts -o running.dts /sys/firmware/fdt
grep -n "my_mmio_demo" -A 10 running.dts
cat /proc/iomem
```

也可以查看运行时设备树：

```bash
hexdump -C /proc/device-tree/路径/reg
```

注意：`reg` 是二进制格式，直接 `cat` 不容易看。

---

## 23. 常见错误5：寄存器偏移写错

比如硬件手册中：

```text
STATUS offset = 0x04
```

但代码中写成：

```c
#define MY_REG_STATUS 0x08
```

这会导致读错寄存器。

建议：

1. 寄存器宏定义和手册保持同名；
2. 每个寄存器旁边写注释；
3. 不要使用魔法数字；
4. 先读只读状态寄存器验证基地址是否正确；
5. 不要一上来就写控制寄存器。

---

## 24. 常见错误6：误写保留位

硬件手册中经常会写：

```text
Reserved bits must be kept as reset value.
```

如果驱动直接写整个寄存器：

```c
writel(0xffffffff, base + MY_REG_CTRL);
```

可能会触发未定义行为。

更安全的做法是：

```c
val = readl(base + MY_REG_CTRL);
val &= ~MY_CTRL_MODE_MASK;
val |= FIELD_PREP(MY_CTRL_MODE_MASK, mode);
writel(val, base + MY_REG_CTRL);
```

如果内核中可用，也可以使用 `FIELD_PREP()`、`FIELD_GET()` 等宏来处理位域。

---

## 25. 常见错误7：并发读改写没有保护

如果同一个寄存器可能在多个上下文中被修改，例如：

1. `probe()`；
2. sysfs `store()`；
3. 中断处理函数；
4. workqueue；
5. ioctl；

那么普通读改写可能发生并发问题。

例如：

```text
线程 A 读取 CTRL = 0x01
线程 B 读取 CTRL = 0x01
线程 A 设置 bit1，写回 0x03
线程 B 清除 bit0，写回 0x00
线程 A 的 bit1 修改被覆盖
```

这时需要使用锁，例如：

```c
spinlock_t lock;
```

或者：

```c
mutex
```

具体用哪种锁，要看上下文是否允许睡眠。中断上下文中不能使用可能睡眠的锁。

入门阶段先记住：

```text
多个地方改同一个寄存器，要考虑并发保护。
```

---

## 26. readl和readl_relaxed

有些代码中会看到：

```c
readl_relaxed()
writel_relaxed()
```

它们和 `readl()`、`writel()` 相比，内存屏障语义更弱，可能性能更好，但需要开发者自己理解访问顺序要求。

对初学者来说，建议先使用：

```c
readl()
writel()
```

等理解 DMA、中断、内存屏障和设备访问顺序后，再研究 relaxed 版本。

---

## 27. 访问寄存器的推荐顺序

调试一个新设备时，不建议一上来就乱写控制寄存器。

推荐顺序：

```text
1. 确认 DTS reg 地址正确
2. 确认 probe 能进入
3. 确认 ioremap 成功
4. 先读取只读 ID/version/status 寄存器
5. 对照硬件手册确认读数合理
6. 再尝试写控制寄存器
7. 每次只修改少量位
8. 观察 dmesg、硬件状态和寄存器回读结果
```

如果有 ID 寄存器，优先读取 ID 寄存器。  
它通常是确认基地址正确的最好方法。

---

## 28. 实习生实验要求

建议实习生基于 `07-platform-driver最小实验.md` 的代码继续修改。

## 28.1 实验1：添加reg资源

在 DTS 中添加：

```dts
my_mmio_demo@28000000 {
	compatible = "training,my-mmio-demo";
	reg = <0x0 0x28000000 0x0 0x1000>;
	status = "okay";
};
```

要求：

1. 重新编译并部署 DTB；
2. 确认 `/proc/device-tree/` 中能看到节点；
3. 确认 `/sys/bus/platform/devices/` 中能看到设备。

## 28.2 实验2：映射寄存器资源

在 `probe()` 中添加：

```c
priv->base = devm_platform_ioremap_resource(pdev, 0);
if (IS_ERR(priv->base))
	return PTR_ERR(priv->base);
```

要求：

1. `insmod` 后 `probe()` 正常执行；
2. `dmesg` 中打印映射成功；
3. 如果失败，记录错误码。

## 28.3 实验3：读取一个寄存器

在确认地址安全的前提下，读取一个只读寄存器：

```c
val = readl(priv->base + MY_REG_STATUS);
dev_info(dev, "status = 0x%08x\n", val);
```

要求记录：

1. 读取的寄存器偏移；
2. 读取到的值；
3. 该值和手册描述是否一致。

## 28.4 实验4：故意删除reg属性

临时删除 DTS 中的 `reg`：

```dts
my_mmio_demo@28000000 {
	compatible = "training,my-mmio-demo";
	status = "okay";
};
```

观察：

1. `probe()` 是否进入；
2. `devm_platform_ioremap_resource()` 是否失败；
3. dmesg 中错误是什么；
4. 返回值是多少。

这个实验可以帮助理解：

```text
compatible 负责匹配；
reg 负责提供寄存器资源。
```

二者不是一回事。

---

## 29. 问题排查清单

遇到 MMIO 访问问题时，按下面顺序排查：

```text
1. probe 是否进入？
2. compatible 是否匹配？
3. DTS 中是否有 reg？
4. reg 地址和长度是否正确？
5. 实际启动的 DTB 是否包含修改？
6. devm_platform_ioremap_resource() 是否成功？
7. base 是否为错误指针？
8. 寄存器偏移是否正确？
9. 访问宽度是否正确？
10. 该寄存器是否允许读写？
11. 是否误写 W1C 或 reserved bit？
12. 是否存在并发读改写？
13. 是否访问了错误设备或不存在地址？
```

常用命令：

```bash
dmesg -w
lsmod
modinfo my_mmio_demo.ko
find /proc/device-tree/ -name '*mmio*'
strings /proc/device-tree/路径/compatible
hexdump -C /proc/device-tree/路径/reg
find /sys/bus/platform/devices/ -name '*mmio*'
cat /proc/iomem
```

---

## 30. 实习生提交要求

完成本文实验后，实习生应提交：

```text
1. DTS 节点内容
2. 驱动源码中寄存器相关宏定义
3. probe 中 ioremap 相关代码
4. readl/writel 相关代码
5. make 编译结果
6. insmod/rmmod 操作记录
7. dmesg 日志
8. /proc/device-tree 中节点检查结果
9. /sys/bus/platform/devices 中设备检查结果
10. 如果访问失败，提交错误码和排查过程
```

问题报告不要只写：

```text
寄存器读不到。
```

而应该写清楚：

```text
probe 是否进入？
reg 是否存在？
ioremap 是否成功？
读的是哪个 offset？
期望值是什么？
实际值是什么？
dmesg 有没有异常？
```

这样才能快速定位问题。

---

## 31. 小结

Linux 驱动访问 MMIO 寄存器的基本流程是：

```text
DTS reg 描述寄存器物理地址
  ↓
platform driver 匹配设备
  ↓
probe() 中获取 reg 资源
  ↓
devm_platform_ioremap_resource() 映射
  ↓
使用 readl()/writel() 访问寄存器
```

入门阶段要牢记：

```text
不要直接使用物理地址；
不要把 MMIO 当普通内存；
不要随意写未知寄存器；
不要忽略 ioremap 返回值；
不要乱改 reserved bit；
不要对 W1C 寄存器做普通读改写。
```

能把 `reg`、`ioremap`、`readl/writel` 这条线理解清楚，才算真正进入了嵌入式 Linux 驱动开发的核心区域。
