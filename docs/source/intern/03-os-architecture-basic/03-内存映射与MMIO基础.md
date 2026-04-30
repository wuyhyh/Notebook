# 03-内存映射与MMIO基础

## 1 为什么要学习内存映射和 MMIO

在 Linux 驱动开发、设备树、PCIe、SoC 外设访问中，经常会看到这些概念：

```text
memory map
MMIO
寄存器基地址
reg 属性
ioremap
readl
writel
BAR
```

这些概念的核心问题是：

```text
CPU 如何访问外设寄存器？
```

现代处理器通常会把内存和外设寄存器都放到统一的地址空间中。CPU 通过访问某个地址，就可以访问 DDR，也可以访问 UART、GPIO、网卡、PCIe 控制器等设备寄存器。

这就是内存映射和 MMIO 要解决的问题。

## 2 什么是内存映射

内存映射可以理解为：系统把某些硬件资源安排到处理器可以访问的地址空间中。

例如：

```text
0x80000000 ~ 0xffffffff     DDR 内存
0x28000000 ~ 0x28000fff     UART0 寄存器
0x2820c000 ~ 0x2820ffff     Ethernet MAC 寄存器
0x40000000 ~ 0x4fffffff     PCIe MMIO 空间
```

这些地址范围共同组成了 CPU 可以访问的系统地址空间。

简单理解：

```text
内存映射 = 给硬件资源分配地址范围
```

这里的“内存”不一定只是真正的 DDR。很多设备寄存器也会被映射到地址空间中。

## 3 什么是 MMIO

MMIO 是 Memory-Mapped I/O，中文通常叫内存映射 I/O。

它的意思是：把设备寄存器映射到内存地址空间中，CPU 像访问内存一样访问设备寄存器。

例如某个 UART 控制器的寄存器基地址是：

```text
0x28001000
```

其中不同偏移对应不同寄存器：

```text
0x28001000 + 0x00    数据寄存器
0x28001000 + 0x04    状态寄存器
0x28001000 + 0x08    控制寄存器
```

CPU 访问这些地址时，并不是在访问 DDR，而是在访问 UART 控制器内部的寄存器。

简单理解：

```text
MMIO = 用内存地址访问设备寄存器
```

## 4 MMIO 和普通内存访问的区别

虽然 MMIO 看起来像访问内存地址，但它和普通 DDR 内存有明显区别。

| 对比项 | 普通内存 DDR | MMIO 设备寄存器 |
|---|---|---|
| 对应对象 | 内存颗粒 | 外设寄存器 |
| 访问目的 | 读写数据 | 控制硬件 |
| 是否可缓存 | 通常可以缓存 | 通常不能随便缓存 |
| 读写副作用 | 通常没有特殊副作用 | 读写可能触发硬件动作 |
| 访问方式 | 普通 load/store | 驱动中使用 readl/writel 等接口 |

例如，对普通内存写入一个值，只是修改内存内容。

但是对某个设备控制寄存器写入一个值，可能会导致：

```text
启动 DMA
清除中断
复位设备
发送数据
打开某个功能
```

所以 MMIO 不是普通内存，不能随便当作普通变量访问。

## 5 什么是寄存器基地址和偏移

设备通常会有一组寄存器，而不是只有一个寄存器。

这组寄存器从某个起始地址开始排列，这个起始地址叫寄存器基地址。

例如：

```text
UART0 基地址：0x28001000
寄存器大小：0x1000
```

那么这个设备的寄存器范围就是：

```text
0x28001000 ~ 0x28001fff
```

不同寄存器通过偏移区分：

```text
基地址 + 0x00
基地址 + 0x04
基地址 + 0x08
基地址 + 0x0c
```

驱动中经常写成：

```c
#define UART_DR     0x00
#define UART_FR     0x18
#define UART_CR     0x30
```

访问时：

```c
readl(base + UART_FR);
writel(value, base + UART_CR);
```

这里的 `base` 是映射后的内核虚拟地址，不是原始物理地址。

## 6 设备树中的 reg 属性

在 ARM64 Linux 中，很多硬件资源通过设备树描述。

例如：

```dts
uart0: serial@28001000 {
    compatible = "arm,pl011";
    reg = <0x0 0x28001000 0x0 0x1000>;
    interrupts = <0 33 4>;
};
```

这里的重点是：

```text
reg = <0x0 0x28001000 0x0 0x1000>;
```

可以理解为：

```text
设备寄存器物理基地址：0x28001000
设备寄存器范围大小：0x1000
```

也就是这个 UART 设备的 MMIO 寄存器区域。

注意，设备树里的 `reg` 通常描述的是物理地址资源，不是驱动代码可以直接解引用的 C 指针。

## 7 为什么不能直接访问物理地址

在 Linux 内核开启 MMU 后，内核代码访问地址时使用的是虚拟地址。

设备树中的寄存器地址通常是物理地址。

例如：

```text
设备树 reg：0x28001000
```

驱动中不能直接写：

```c
volatile uint32_t *reg = (volatile uint32_t *)0x28001000;
*reg = value;
```

这种写法在 Linux 驱动中通常是不正确的。

正确思路是：

```text
物理地址
  |
  v
ioremap 映射
  |
  v
内核虚拟地址
  |
  v
readl/writel 访问
```

## 8 ioremap 的作用

`ioremap()` 用于把设备寄存器的物理地址映射成内核虚拟地址。

例如：

```c
void __iomem *base;

base = ioremap(0x28001000, 0x1000);
if (!base)
    return -ENOMEM;
```

映射成功后，`base` 就是内核可以访问的 MMIO 虚拟地址。

之后可以这样访问寄存器：

```c
u32 val;

val = readl(base + 0x00);
writel(val | BIT(0), base + 0x04);
```

使用结束后，通常需要释放映射：

```c
iounmap(base);
```

简单理解：

```text
ioremap = 把设备物理地址变成内核可访问的虚拟地址
```

## 9 readl 和 writel 的作用

`readl()` 和 `writel()` 是 Linux 内核中访问 32 位 MMIO 寄存器的常见接口。

例如：

```c
u32 val;

val = readl(base + REG_STATUS);
writel(0x1, base + REG_CTRL);
```

常见接口包括：

```text
readb / writeb     访问 8 bit 寄存器
readw / writew     访问 16 bit 寄存器
readl / writel     访问 32 bit 寄存器
readq / writeq     访问 64 bit 寄存器
```

这些接口比普通指针访问更合适，因为它们会处理 MMIO 访问所需的语义，例如访问顺序和编译器优化问题。

## 10 为什么 MMIO 通常不能缓存

普通 DDR 内存可以缓存，因为重复读取同一个地址，一般应该得到相同内存内容。

但是 MMIO 寄存器通常不能随便缓存。

例如状态寄存器：

```text
第一次读取：设备忙
第二次读取：设备空闲
```

如果 CPU 把第一次读取结果缓存起来，后面一直读到旧值，驱动就无法正确判断硬件状态。

再比如清中断寄存器：

```text
写 1 清除中断
```

这个写操作必须真正到达硬件，不能只停留在 CPU cache 中。

所以 MMIO 区域通常要映射成 device memory 或 non-cacheable memory。

## 11 MMIO 访问的副作用

MMIO 访问可能有副作用。

例如：

```text
读状态寄存器：可能清除某些状态位
写控制寄存器：可能启动硬件操作
写中断清除寄存器：可能清除中断
读 FIFO 寄存器：可能弹出一个数据
写 FIFO 寄存器：可能发送一个数据
```

所以访问 MMIO 寄存器时，不能像普通内存那样随便重复读取或写入。

例如下面这种写法可能有问题：

```c
if (readl(base + STATUS) & BIT(0)) {
    if (readl(base + STATUS) & BIT(1)) {
        ...
    }
}
```

如果读取状态寄存器有副作用，重复读取可能改变硬件状态。

更稳妥的方式通常是读取一次后保存：

```c
u32 status;

status = readl(base + STATUS);

if (status & BIT(0)) {
    ...
}
```

## 12 MMIO 和 PIO 的区别

除了 MMIO，还有一种方式叫 PIO，也就是 Port I/O。

在 x86 平台上，历史上存在独立的 I/O 端口地址空间，例如使用：

```text
in
out
```

指令访问 I/O 端口。

而 MMIO 是把设备寄存器放进内存地址空间，通过普通地址访问机制访问。

简单对比：

| 对比项 | MMIO | PIO |
|---|---|---|
| 地址空间 | 内存地址空间 | 独立 I/O 端口空间 |
| 访问方式 | load/store 或 readl/writel | in/out 指令 |
| 常见平台 | ARM、RISC-V、现代 PCIe 设备 | x86 历史兼容场景 |
| 驱动接口 | ioremap、readl、writel | inb、outb 等 |

在 ARM64 SoC 上，主要使用 MMIO。

## 13 PCIe BAR 和 MMIO

PCIe 设备也经常通过 MMIO 暴露寄存器。

PCIe 设备的 BAR 用于告诉系统：这个设备需要一段地址空间。

例如一个网卡可能有 BAR0：

```text
BAR0 size：16MB
```

系统枚举 PCIe 设备时，会给这个 BAR 分配一段 CPU 地址空间。

例如：

```text
BAR0 -> 0x40000000 ~ 0x40ffffff
```

驱动访问这个范围时，就是在访问 PCIe 设备内部的寄存器或存储空间。

关系可以理解为：

```text
CPU 地址访问
  |
  v
Root Complex
  |
  v
PCIe Memory Read/Write TLP
  |
  v
Endpoint BAR
  |
  v
设备内部寄存器或存储区域
```

所以 PCIe BAR 本质上也是 MMIO 机制的重要应用。

## 14 MMIO 和 DMA 的区别

MMIO 和 DMA 都和设备访问有关，但方向不同。

| 对比项 | MMIO | DMA |
|---|---|---|
| 主动方 | CPU | 设备 |
| 访问对象 | CPU 访问设备寄存器 | 设备访问系统内存 |
| 常见用途 | 配置设备、读写控制寄存器 | 大块数据搬运 |
| 驱动关注点 | ioremap/readl/writel | dma_alloc/dma_map/dma_unmap |

简单理解：

```text
MMIO：CPU 主动访问设备
DMA：设备主动访问内存
```

例如网卡驱动中：

```text
CPU 通过 MMIO 配置网卡寄存器
网卡通过 DMA 把收到的数据写入内存
```

这两个机制经常配合使用。

## 15 驱动中的典型访问流程

一个简单平台设备驱动中，访问 MMIO 的流程通常是：

```text
从设备树获取资源
        |
        v
申请资源区域
        |
        v
ioremap 映射寄存器
        |
        v
readl/writel 访问寄存器
        |
        v
驱动卸载时释放资源
```

内核中常见写法是使用 devm 接口：

```c
struct resource *res;
void __iomem *base;

res = platform_get_resource(pdev, IORESOURCE_MEM, 0);
base = devm_ioremap_resource(&pdev->dev, res);
if (IS_ERR(base))
    return PTR_ERR(base);
```

这种写法比手动 `ioremap()` 更推荐，因为它会自动处理资源申请和释放。

## 16 常见命令和观察方法

查看设备树中的寄存器资源：

```bash
dtc -I fs -O dts /proc/device-tree > running.dts
grep -n "reg =" running.dts | head
```

查看内核启动日志中的 MMIO 资源：

```bash
dmesg | grep -i "iomem"
```

查看系统 I/O 内存资源：

```bash
cat /proc/iomem
```

查看某个驱动是否绑定设备：

```bash
ls /sys/bus/platform/devices/
ls /sys/bus/platform/drivers/
```

查看 PCIe 设备 BAR：

```bash
lspci -vv
```

查看 PCIe 设备资源文件：

```bash
ls /sys/bus/pci/devices/0000:xx:yy.z/resource*
cat /sys/bus/pci/devices/0000:xx:yy.z/resource
```

## 17 常见理解误区

### 17.1 MMIO 不是普通内存

MMIO 虽然占用内存地址空间，但它对应的是设备寄存器，不是 DDR。

访问 MMIO 可能触发硬件动作。

### 17.2 设备树 reg 不是 C 指针

设备树中的 `reg` 描述的是设备物理地址资源。

驱动中不能直接把它当成普通指针访问。

### 17.3 ioremap 后得到的是虚拟地址

`ioremap()` 输入的是设备物理地址，返回的是内核虚拟地址。

驱动实际访问的是返回值，而不是原始物理地址。

### 17.4 readl/writel 不是多余的

MMIO 访问不建议直接使用普通指针读写。

`readl()`、`writel()` 这类接口表达了这是一次设备寄存器访问，也能避免一些编译器优化和访问顺序问题。

### 17.5 MMIO 和 DMA 不是一回事

MMIO 是 CPU 访问设备。

DMA 是设备访问内存。

两者方向不同，使用的驱动接口也不同。

## 18 总结

内存映射和 MMIO 可以这样理解：

```text
系统把设备寄存器放到 CPU 地址空间中
CPU 通过访问特定地址来访问设备寄存器
这种机制叫 MMIO
```

驱动开发中要记住：

```text
设备树 reg 描述设备寄存器物理地址
Linux 内核开启 MMU 后不能直接访问物理地址
驱动需要通过 ioremap 或 devm_ioremap_resource 建立映射
访问寄存器应使用 readl/writel 等 MMIO 接口
```

一句话总结：

```text
MMIO 是 CPU 通过地址空间访问设备寄存器的机制，是 Linux 驱动开发中最基础的硬件访问方式之一。
```
