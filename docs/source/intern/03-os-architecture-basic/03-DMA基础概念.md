# 03-DMA基础概念

## 1 为什么要学习 DMA

在 Linux 驱动开发、网卡、存储、PCIe、图像采集、NPU/DPU 等场景中，经常会遇到 DMA。

DMA 的全称是 Direct Memory Access，中文通常叫直接内存访问。

简单理解：

```text
DMA = 设备不通过 CPU 搬运数据，而是直接读写系统内存
```

如果没有 DMA，大量数据传输可能需要 CPU 逐字节或逐块搬运。

例如网卡收到数据包后，如果完全由 CPU 读取设备 FIFO，再复制到内存，会非常低效。

有了 DMA 后，流程可以变成：

```text
网卡收到数据
        |
        v
网卡通过 DMA 直接把数据写入内存
        |
        v
CPU 只需要处理内存中的数据
```

这样可以减少 CPU 负担，提高数据传输效率。

## 2 没有 DMA 时的数据搬运

假设设备收到一段数据，要放到内存中。

如果没有 DMA，可能是：

```text
设备内部缓冲区
        |
        v
CPU 读取设备寄存器或 FIFO
        |
        v
CPU 写入内存
```

也就是 CPU 亲自搬运数据。

例如：

```text
CPU 从设备读 4 字节
CPU 写入内存
CPU 再从设备读 4 字节
CPU 再写入内存
...
```

这种方式在数据量小的时候可以接受。

但如果是网卡、磁盘、摄像头、NPU 这类设备，数据量很大，让 CPU 亲自搬运会浪费大量 CPU 时间。

## 3 有 DMA 时的数据搬运

有 DMA 后，设备可以直接访问内存。

大致流程是：

```text
CPU 准备一块内存缓冲区
        |
        v
CPU 把缓冲区地址告诉设备
        |
        v
设备通过 DMA 直接读写这块内存
        |
        v
设备完成后触发中断通知 CPU
        |
        v
CPU 处理结果
```

简单理解：

```text
CPU 负责安排任务
设备负责搬运数据
中断负责通知完成
```

例如网卡接收数据：

```text
CPU 分配接收缓冲区
CPU 把缓冲区 DMA 地址写入网卡描述符
网卡收到数据包
网卡通过 DMA 把数据写入缓冲区
网卡触发中断
CPU 处理收到的数据包
```

## 4 DMA 中的主动方是谁

普通 MMIO 是 CPU 主动访问设备：

```text
CPU -> 设备寄存器
```

DMA 是设备主动访问内存：

```text
设备 -> 系统内存
```

所以两者方向不同：

| 对比项 | MMIO | DMA |
|---|---|---|
| 主动方 | CPU | 设备 |
| 访问对象 | 设备寄存器 | 系统内存 |
| 主要用途 | 配置设备、读写状态 | 大块数据搬运 |
| 常见接口 | readl/writel | DMA API |

一句话记忆：

```text
MMIO 是 CPU 访问设备，DMA 是设备访问内存。
```

## 5 DMA 地址是什么

驱动开发中最容易混淆的是这些地址：

```text
CPU 虚拟地址
CPU 物理地址
DMA 地址
```

在简单系统中，设备看到的 DMA 地址可能和物理地址相同。

但在现代系统中，特别是有 IOMMU 的系统中，设备看到的地址不一定等于 CPU 物理地址。

所以不能简单认为：

```text
DMA 地址 = 物理地址
```

更不能认为：

```text
DMA 地址 = CPU 虚拟地址
```

更稳妥的理解是：

```text
DMA 地址 = 设备用于访问内存的地址
```

驱动中应该通过 DMA API 获取 DMA 地址，而不是自己随便转换。

## 6 CPU 虚拟地址和 DMA 地址的区别

驱动中经常会看到这样的代码：

```c
void *cpu_addr;
dma_addr_t dma_handle;

cpu_addr = dma_alloc_coherent(dev, size, &dma_handle, GFP_KERNEL);
```

这里有两个地址：

```text
cpu_addr：CPU 使用的内核虚拟地址
dma_handle：设备 DMA 使用的地址
```

CPU 访问这块内存时使用：

```c
memset(cpu_addr, 0, size);
```

设备访问这块内存时使用：

```c
writel(lower_32_bits(dma_handle), dev_base + DMA_ADDR_LOW);
writel(upper_32_bits(dma_handle), dev_base + DMA_ADDR_HIGH);
```

简单理解：

```text
同一块内存，CPU 和设备可能使用不同地址来访问。
```

## 7 DMA 为什么不能直接用普通指针

普通指针通常是 CPU 虚拟地址。

例如：

```c
void *buf;
```

这个 `buf` 是 CPU 看见的地址。

但是设备不是 CPU，设备不能直接理解这个虚拟地址。

错误理解：

```text
把 buf 指针强转成整数，然后写给设备做 DMA
```

这是很危险的。

错误示例：

```c
writel((u32)buf, dev_base + DMA_ADDR);
```

问题在于：

```text
buf 是 CPU 虚拟地址
设备需要 DMA 地址
两者不是一个概念
```

正确做法是使用 DMA API。

## 8 一致性 DMA 和流式 DMA

Linux 中常见 DMA 使用方式可以先粗略分成两类：

```text
一致性 DMA
流式 DMA
```

一致性 DMA 也叫 coherent DMA。

常用接口：

```c
dma_alloc_coherent()
dma_free_coherent()
```

它适合设备和 CPU 长期共享的一块内存，例如描述符环。

流式 DMA 适合临时把一段已有内存交给设备传输。

常用接口：

```c
dma_map_single()
dma_unmap_single()
dma_map_page()
dma_unmap_page()
```

简单对比：

| 类型 | 常见接口 | 适合场景 |
|---|---|---|
| 一致性 DMA | dma_alloc_coherent | 描述符环、长期共享缓冲区 |
| 流式 DMA | dma_map_single | 临时数据缓冲区、一次性传输 |

初学阶段可以先记住：

```text
长期共享用 dma_alloc_coherent
临时映射用 dma_map_single
```

## 9 一致性 DMA 的基本用法

一致性 DMA 的典型分配方式：

```c
void *cpu_addr;
dma_addr_t dma_handle;

cpu_addr = dma_alloc_coherent(dev, size, &dma_handle, GFP_KERNEL);
if (!cpu_addr)
    return -ENOMEM;
```

使用时：

```text
CPU 用 cpu_addr 访问
设备用 dma_handle 访问
```

释放时：

```c
dma_free_coherent(dev, size, cpu_addr, dma_handle);
```

这种内存的特点是 CPU 和设备之间保持一致性，通常不需要驱动手动做缓存同步。

它常用于：

```text
DMA 描述符
环形队列
设备和 CPU 频繁共享的控制结构
```

## 10 流式 DMA 的基本用法

流式 DMA 常用于已有数据缓冲区。

例如 CPU 准备好一段数据后，让设备读取：

```c
dma_addr_t dma_addr;

dma_addr = dma_map_single(dev, buf, len, DMA_TO_DEVICE);
if (dma_mapping_error(dev, dma_addr))
    return -EIO;
```

然后把 `dma_addr` 写给设备。

设备传输完成后，需要解除映射：

```c
dma_unmap_single(dev, dma_addr, len, DMA_TO_DEVICE);
```

如果是设备写入内存，方向通常是：

```c
DMA_FROM_DEVICE
```

如果是设备读取内存，方向通常是：

```c
DMA_TO_DEVICE
```

如果双向访问，可以使用：

```c
DMA_BIDIRECTIONAL
```

## 11 DMA 方向是什么意思

DMA 方向是从设备视角描述的。

常见方向：

| DMA 方向 | 含义 |
|---|---|
| DMA_TO_DEVICE | 设备从内存读取数据 |
| DMA_FROM_DEVICE | 设备向内存写入数据 |
| DMA_BIDIRECTIONAL | 设备既读又写 |
| DMA_NONE | 不用于实际 DMA |

注意这里容易反：

```text
DMA_TO_DEVICE = 内存到设备
DMA_FROM_DEVICE = 设备到内存
```

例如：

```text
发送网卡数据包：DMA_TO_DEVICE
接收网卡数据包：DMA_FROM_DEVICE
磁盘读数据到内存：DMA_FROM_DEVICE
磁盘把内存数据写入磁盘：DMA_TO_DEVICE
```

## 12 DMA 和 cache 一致性

DMA 最麻烦的问题之一是 cache 一致性。

CPU 访问内存时通常会经过 cache。

设备 DMA 访问内存时，不一定经过 CPU cache。

这会导致问题。

### 12.1 CPU 写了数据，设备看不到

例如发送数据：

```text
CPU 把数据写入缓冲区
数据可能还在 CPU cache 中
设备通过 DMA 从内存读取
设备可能读到旧数据
```

### 12.2 设备写了数据，CPU 看不到

例如接收数据：

```text
设备通过 DMA 把数据写入内存
CPU cache 中可能还有旧数据
CPU 读取时可能读到旧数据
```

DMA API 的一个重要作用，就是在合适的时候处理 cache 同步。

所以驱动不要绕过 DMA API。

## 13 IOMMU 是什么

IOMMU 可以理解为设备侧的地址转换单元。

CPU 访问内存时有 MMU：

```text
CPU 虚拟地址 -> CPU 物理地址
```

设备访问内存时，如果系统有 IOMMU，可能是：

```text
设备 DMA 地址 -> 物理地址
```

简单理解：

```text
MMU：给 CPU 做地址转换
IOMMU：给设备做地址转换
```

IOMMU 的作用包括：

```text
设备 DMA 地址转换
限制设备能访问的内存范围
提高系统安全性
支持虚拟化中的设备直通
```

所以在有 IOMMU 的系统中，DMA 地址更不能简单等同于物理地址。

## 14 DMA mask 是什么

设备并不一定能访问全部内存地址。

例如有些设备只能发出 32 位 DMA 地址，那么它只能访问：

```text
0x00000000 ~ 0xffffffff
```

也就是最多 4GB 地址范围。

如果系统内存超过 4GB，驱动需要告诉内核设备的 DMA 地址能力。

常见接口：

```c
dma_set_mask_and_coherent(dev, DMA_BIT_MASK(32));
```

或者设备支持 64 位 DMA：

```c
dma_set_mask_and_coherent(dev, DMA_BIT_MASK(64));
```

简单理解：

```text
DMA mask = 设备能访问多少位宽的 DMA 地址
```

如果 mask 设置不正确，可能导致设备拿到自己访问不了的 DMA 地址。

## 15 DMA 描述符是什么

很多设备不会只做一次简单 DMA，而是使用描述符队列。

DMA 描述符通常用于告诉设备：

```text
数据缓冲区地址
数据长度
传输方向
控制标志
完成状态
下一个描述符位置
```

例如网卡接收数据时，驱动会提前准备一批接收描述符：

```text
RX 描述符 0 -> 接收缓冲区 0
RX 描述符 1 -> 接收缓冲区 1
RX 描述符 2 -> 接收缓冲区 2
...
```

网卡收到数据后，根据描述符把数据 DMA 到对应缓冲区中。

CPU 和设备通过描述符环协作。

## 16 DMA 完成后如何通知 CPU

设备完成 DMA 后，通常会通过中断通知 CPU。

典型流程：

```text
CPU 准备 DMA 缓冲区和描述符
        |
        v
CPU 启动设备 DMA
        |
        v
设备执行 DMA 传输
        |
        v
设备更新完成状态
        |
        v
设备触发中断
        |
        v
CPU 在中断处理程序中回收或处理缓冲区
```

所以 DMA 和中断经常配合使用：

```text
DMA 负责搬数据
中断负责通知完成
```

## 17 DMA 和 memcpy 的区别

`memcpy()` 是 CPU 执行的数据复制。

DMA 是设备执行的数据搬运。

| 对比项 | memcpy | DMA |
|---|---|---|
| 执行者 | CPU | 设备或 DMA 控制器 |
| 数据路径 | CPU load/store | 设备直接访问内存 |
| 适合场景 | 小数据、普通内存复制 | 大块数据、外设数据搬运 |
| 是否需要驱动配置 | 不需要 | 需要设置 DMA 地址、长度、方向 |
| 是否涉及 cache 同步 | 普通 CPU 内存语义 | 需要考虑 DMA cache 一致性 |

简单理解：

```text
memcpy 是 CPU 搬，DMA 是设备搬。
```

## 18 DMA 和 MMIO 的配合关系

驱动通常使用 MMIO 配置 DMA。

例如：

```text
CPU 通过 MMIO 写设备寄存器
告诉设备 DMA 地址、长度和启动命令
设备根据这些信息执行 DMA
```

示意：

```text
CPU
 |
 | MMIO 写寄存器
 v
设备控制寄存器
 |
 | 设备发起 DMA
 v
系统内存
```

所以实际驱动里经常同时出现：

```c
writel(lower_32_bits(dma_addr), base + DMA_ADDR_LOW);
writel(upper_32_bits(dma_addr), base + DMA_ADDR_HIGH);
writel(len, base + DMA_LEN);
writel(START, base + DMA_CTRL);
```

这里：

```text
base：设备寄存器 MMIO 地址
dma_addr：设备 DMA 使用的内存地址
```

这两个地址不是一回事。

## 19 Linux 中常见 DMA API

初学阶段常见 DMA API：

```c
dma_alloc_coherent()
dma_free_coherent()
dma_map_single()
dma_unmap_single()
dma_mapping_error()
dma_set_mask_and_coherent()
```

简单说明：

| 接口 | 作用 |
|---|---|
| dma_alloc_coherent | 分配一致性 DMA 内存 |
| dma_free_coherent | 释放一致性 DMA 内存 |
| dma_map_single | 把已有缓冲区映射给设备 DMA 使用 |
| dma_unmap_single | 解除流式 DMA 映射 |
| dma_mapping_error | 检查 DMA 映射是否失败 |
| dma_set_mask_and_coherent | 设置设备 DMA 地址能力 |

初学时重点掌握：

```text
dma_alloc_coherent
dma_map_single
dma_unmap_single
DMA_TO_DEVICE
DMA_FROM_DEVICE
```

## 20 简单示例：一致性 DMA

下面是一个非常简化的示例：

```c
struct mydev {
    void __iomem *base;
    void *cpu_buf;
    dma_addr_t dma_addr;
    size_t size;
};

static int mydev_alloc_dma(struct device *dev, struct mydev *mdev)
{
    mdev->size = 4096;

    mdev->cpu_buf = dma_alloc_coherent(dev, mdev->size,
                                       &mdev->dma_addr,
                                       GFP_KERNEL);
    if (!mdev->cpu_buf)
        return -ENOMEM;

    memset(mdev->cpu_buf, 0, mdev->size);

    writel(lower_32_bits(mdev->dma_addr), mdev->base + DMA_ADDR_LOW);
    writel(upper_32_bits(mdev->dma_addr), mdev->base + DMA_ADDR_HIGH);
    writel(mdev->size, mdev->base + DMA_LEN);

    return 0;
}
```

这个例子中：

```text
mdev->cpu_buf：CPU 用来访问缓冲区
mdev->dma_addr：设备用来访问缓冲区
mdev->base：设备 MMIO 寄存器基地址
```

这三个地址含义不同，不能混淆。

## 21 常见命令和观察方法

查看设备是否启用 IOMMU，具体和平台有关，可以尝试：

```bash
dmesg | grep -i iommu
```

查看 DMA 相关内核日志：

```bash
dmesg | grep -i dma
```

查看设备树中的 dma 相关属性：

```bash
dtc -I fs -O dts /proc/device-tree > running.dts
grep -i dma running.dts
```

查看 PCIe 设备信息：

```bash
lspci -vv
```

查看中断变化，辅助判断 DMA 完成通知：

```bash
cat /proc/interrupts
```

## 22 常见理解误区

### 22.1 DMA 不是 CPU 复制内存

DMA 是设备或 DMA 控制器直接访问内存。

CPU 负责配置，不负责逐字节搬运。

### 22.2 DMA 地址不等于普通指针

普通指针通常是 CPU 虚拟地址。

设备不能直接使用普通指针做 DMA。

### 22.3 DMA 地址不一定等于物理地址

在有 IOMMU 的系统中，设备看到的是 DMA 地址或 I/O 虚拟地址，不一定是 CPU 物理地址。

### 22.4 dma_alloc_coherent 返回两个地址

`dma_alloc_coherent()` 返回 CPU 虚拟地址，同时通过参数返回 DMA 地址。

这两个地址分别给 CPU 和设备使用。

### 22.5 DMA 方向不要写反

`DMA_TO_DEVICE` 表示数据从内存到设备。

`DMA_FROM_DEVICE` 表示数据从设备到内存。

方向写错可能导致 cache 同步错误，数据异常。

### 22.6 DMA 通常要配合中断

DMA 完成后，设备通常通过中断通知 CPU。

所以调试 DMA 时，也要关注中断是否正常触发。

## 23 总结

DMA 可以这样理解：

```text
CPU 准备内存和参数
CPU 通过 MMIO 配置设备
设备通过 DMA 直接读写内存
设备完成后通过中断通知 CPU
CPU 处理结果
```

一句话总结：

```text
DMA 是设备直接访问系统内存进行数据搬运的机制，可以减少 CPU 复制数据的开销。
```

驱动开发中要特别记住：

```text
CPU 使用虚拟地址
设备使用 DMA 地址
不要把普通指针直接交给设备
DMA 地址应通过 DMA API 获取
DMA 方向要从设备视角理解
有 cache 和 IOMMU 时更不能绕过 DMA API
```

对于 Linux 驱动开发来说，DMA 是从“能访问寄存器”走向“能做高性能数据传输”的关键基础概念。
