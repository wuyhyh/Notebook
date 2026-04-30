# 03-Cache基础与一致性问题入门

## 1 为什么要学习 Cache

在学习 CPU、内存、DMA、驱动开发和性能优化时，经常会遇到 Cache。

Cache 中文通常叫高速缓存。

它的作用是缓解 CPU 和内存之间的速度差距。

简单理解：

```text
CPU 很快
DDR 内存相对慢
Cache 位于 CPU 和内存之间，用来缓存最近使用的数据
```

如果没有 Cache，CPU 每次读写数据都要直接访问 DDR，性能会明显下降。

有了 Cache 后，CPU 访问最近用过的数据时，可以直接从 Cache 中获取，速度更快。

## 2 Cache 是什么

Cache 是 CPU 内部或靠近 CPU 的高速存储器。

它保存 DDR 内存中部分数据的副本。

例如，内存中有一段数据：

```text
物理内存地址 0x80001000 上的数据
```

CPU 第一次访问时，可能需要从 DDR 中读取。

读取后，这段数据会被放入 Cache。

下一次 CPU 再访问同一个地址时，如果数据还在 Cache 中，就可以直接从 Cache 读取。

简单理解：

```text
Cache = 内存数据的高速副本
```

## 3 为什么需要 Cache

CPU 运行速度远高于 DDR 内存访问速度。

如果 CPU 每次执行 load/store 都直接访问 DDR，就会经常等待内存返回数据。

Cache 的作用就是减少这种等待。

它利用了程序访问内存的局部性。

局部性主要包括两类：

```text
时间局部性
空间局部性
```

时间局部性：

```text
刚刚访问过的数据，接下来很可能还会再次访问
```

空间局部性：

```text
访问某个地址后，附近的地址也很可能会被访问
```

例如数组遍历：

```c
for (i = 0; i < 1024; i++)
    sum += array[i];
```

访问 `array[i]` 后，后面很可能访问 `array[i + 1]`。

这种连续访问非常适合 Cache。

## 4 Cache 命中和 Cache 未命中

CPU 访问某个地址时，如果数据已经在 Cache 中，叫 Cache 命中。

```text
Cache hit = Cache 中有需要的数据
```

如果数据不在 Cache 中，需要从下一级 Cache 或 DDR 中读取，叫 Cache 未命中。

```text
Cache miss = Cache 中没有需要的数据
```

简单流程：

```text
CPU 访问某个地址
        |
        v
检查 Cache
        |
        +-- 命中：直接从 Cache 读取
        |
        +-- 未命中：从下一级 Cache 或 DDR 读取
```

Cache 命中率越高，程序通常运行越快。

## 5 多级 Cache

现代 CPU 通常有多级 Cache。

常见结构：

```text
L1 Cache
L2 Cache
L3 Cache
DDR 内存
```

一般来说：

```text
L1 最快，但容量最小
L2 比 L1 慢一些，但容量更大
L3 更大，但更慢
DDR 容量最大，但访问最慢
```

访问流程可以粗略理解为：

```text
CPU
 |
 v
L1 Cache
 |
 v
L2 Cache
 |
 v
L3 Cache
 |
 v
DDR
```

在 ARM64 SoC 中，不同 CPU 核心可能有自己的 L1 Cache，多个核心可能共享 L2 或 L3 Cache，具体要看芯片设计。

## 6 Cache Line 是什么

Cache 不是一个字节一个字节管理数据，而是按 Cache Line 管理。

Cache Line 是 Cache 管理的基本单位。

常见 Cache Line 大小可能是：

```text
64 bytes
```

也有平台可能是 32 bytes、128 bytes 等。

例如 Cache Line 是 64 字节时，CPU 访问某个地址，可能会把这个地址所在的 64 字节一起加载到 Cache 中。

这就是空间局部性发挥作用的基础。

简单理解：

```text
Cache Line = Cache 一次缓存的一小块连续内存
```

## 7 Cache 读数据的大致过程

假设 CPU 要读取某个内存地址的数据。

流程可以粗略理解为：

```text
CPU 发起读请求
        |
        v
查 L1 Cache
        |
        +-- L1 命中：返回数据
        |
        +-- L1 未命中：查 L2 Cache
                |
                +-- L2 命中：返回数据，并可能填充 L1
                |
                +-- L2 未命中：访问 DDR，并填充 Cache
```

这说明：CPU 看到的是一个地址，但底层可能经历多级缓存查询。

## 8 Cache 写策略

CPU 写数据时，Cache 也有不同策略。

常见概念包括：

```text
write-through
write-back
```

### 8.1 write-through

write-through 表示 CPU 写 Cache 时，同时也写回内存。

简单理解：

```text
CPU 写 Cache
同时写 DDR
```

优点是内存内容比较容易保持最新。

缺点是写内存次数多，性能可能较差。

### 8.2 write-back

write-back 表示 CPU 写数据时，先只写 Cache，不一定马上写 DDR。

等 Cache Line 被替换或显式清理时，再写回内存。

简单理解：

```text
CPU 先写 Cache
DDR 可能暂时还是旧数据
以后再把 Cache 中的新数据写回 DDR
```

write-back 性能通常更好，但也带来一致性问题。

## 9 Dirty Cache 是什么

在 write-back 模式下，如果 CPU 修改了 Cache 中的数据，但还没有写回 DDR，这条 Cache Line 就是 dirty 的。

简单理解：

```text
Dirty Cache Line = Cache 中的数据比 DDR 中的数据更新
```

例如：

```text
DDR 中 A = 1
CPU 写 A = 2
新值 A = 2 可能只在 Cache 中
DDR 中仍然是 A = 1
```

这时候如果某个设备绕过 CPU Cache 直接读 DDR，就可能读到旧值。

这就是 DMA 和 Cache 一致性问题的来源之一。

## 10 Cache 一致性问题是什么

Cache 一致性问题指的是：同一份数据在多个地方存在副本，而这些副本可能不一致。

这些地方可能包括：

```text
CPU Cache
DDR 内存
其他 CPU 核心的 Cache
设备 DMA 看到的内存
```

例如：

```text
CPU Cache 中的数据是新值
DDR 中的数据是旧值
设备 DMA 从 DDR 读到旧值
```

或者：

```text
设备 DMA 已经把新数据写入 DDR
CPU Cache 中仍然保留旧值
CPU 读取时读到旧值
```

简单理解：

```text
Cache 一致性问题 = CPU、内存、设备看到的数据不一致
```

## 11 多核 CPU 中的 Cache 一致性

在多核 CPU 中，每个 CPU 核心可能有自己的 Cache。

例如：

```text
CPU0 L1 Cache
CPU1 L1 Cache
CPU2 L1 Cache
CPU3 L1 Cache
```

如果多个 CPU 核心访问同一块内存，就可能出现一致性问题。

例如：

```text
CPU0 读取变量 A，缓存到自己的 Cache
CPU1 修改变量 A
CPU0 再读取变量 A
```

这时需要保证 CPU0 不会一直读到旧值。

现代多核 CPU 通常有硬件 Cache Coherency 协议，例如 MESI 或类似协议，用来维护多个 CPU Cache 之间的一致性。

对普通内核代码来说，多核 CPU 之间的缓存一致性通常由硬件处理，但并发访问仍然需要锁来保证逻辑正确性。

注意：

```text
Cache 一致性解决的是数据副本是否一致
锁解决的是并发访问顺序和临界区保护
```

这两个问题有关联，但不是同一个问题。

## 12 DMA 为什么会遇到 Cache 一致性问题

DMA 是设备直接访问内存。

设备通常不会自动知道 CPU Cache 里面有没有更新的数据。

所以 DMA 读写内存时，容易遇到 Cache 一致性问题。

### 12.1 设备从内存读取数据

例如发送网络数据：

```text
CPU 准备发送缓冲区
CPU 把数据写入内存
数据可能还停留在 CPU Cache 中
设备通过 DMA 从 DDR 读取数据
设备可能读到旧数据
```

问题本质：

```text
CPU 写的新数据还没有从 Cache 写回 DDR
```

解决思路：

```text
在设备 DMA 读取前，把 CPU Cache 中的新数据写回内存
```

这个操作常叫：

```text
cache clean
cache flush
```

不同文档中术语可能略有差异。

### 12.2 设备向内存写入数据

例如接收网络数据：

```text
设备通过 DMA 把新数据写入 DDR
CPU Cache 中可能还有旧数据
CPU 读取缓冲区时可能命中 Cache
CPU 读到旧数据
```

问题本质：

```text
设备写了 DDR，但 CPU Cache 中旧副本还没失效
```

解决思路：

```text
在 CPU 读取 DMA 写入的数据前，让旧 Cache Line 失效
```

这个操作常叫：

```text
cache invalidate
```

## 13 Cache Clean 和 Invalidate

常见 Cache 操作包括：

```text
clean
invalidate
clean + invalidate
```

### 13.1 clean

clean 表示把 dirty Cache Line 写回内存。

适合场景：

```text
CPU 写了数据，设备即将通过 DMA 读取
```

目的：

```text
让 DDR 中的数据变成最新
```

### 13.2 invalidate

invalidate 表示让某些 Cache Line 失效。

适合场景：

```text
设备通过 DMA 写了内存，CPU 即将读取
```

目的：

```text
避免 CPU 继续读到 Cache 中的旧数据
```

### 13.3 clean + invalidate

有时需要先写回，再失效。

具体使用要看场景和架构要求。

初学时可以先记住：

```text
设备读内存前：确保 CPU 写入的数据已经到内存
设备写内存后：确保 CPU 不读旧 Cache
```

## 14 Linux DMA API 如何处理 Cache 一致性

在 Linux 驱动中，不应该手写架构相关的 Cache 操作。

应该使用 DMA API。

例如流式 DMA：

```c
dma_addr_t dma_addr;

dma_addr = dma_map_single(dev, buf, len, DMA_TO_DEVICE);
if (dma_mapping_error(dev, dma_addr))
    return -EIO;
```

对于 `DMA_TO_DEVICE`，DMA API 会处理设备读取前所需的缓存同步。

设备完成后：

```c
dma_unmap_single(dev, dma_addr, len, DMA_TO_DEVICE);
```

对于设备写入内存：

```c
dma_addr = dma_map_single(dev, buf, len, DMA_FROM_DEVICE);
```

设备完成后：

```c
dma_unmap_single(dev, dma_addr, len, DMA_FROM_DEVICE);
```

DMA API 会在合适时机处理 cache 同步和地址映射。

所以驱动开发中要记住：

```text
不要绕过 DMA API 自己把指针交给设备
不要自己假设 DMA 地址等于物理地址
不要随便手写 cache 操作
```

## 15 一致性 DMA 为什么简单一些

使用 `dma_alloc_coherent()` 分配的内存，通常叫一致性 DMA 内存。

示例：

```c
void *cpu_addr;
dma_addr_t dma_handle;

cpu_addr = dma_alloc_coherent(dev, size, &dma_handle, GFP_KERNEL);
```

其中：

```text
cpu_addr：CPU 使用的虚拟地址
dma_handle：设备使用的 DMA 地址
```

这类内存适合 CPU 和设备长期共享，例如：

```text
DMA 描述符环
控制块
状态队列
```

它的特点是：

```text
CPU 和设备之间保持一致性
通常不需要驱动手动 clean/invalidate
适合频繁共享的小块控制结构
```

但是它不一定适合所有大数据缓冲区，因为一致性内存可能有额外性能代价。

## 16 流式 DMA 为什么更容易出错

流式 DMA 常用于临时数据传输。

例如：

```c
dma_addr = dma_map_single(dev, buf, len, DMA_TO_DEVICE);
```

它要求驱动遵守严格的使用规则。

例如：

```text
map 之后，设备使用这段 buffer
设备使用期间，CPU 不应该随便修改同一段 buffer
设备完成后，要 unmap
unmap 后，CPU 才安全地重新使用 buffer
```

如果驱动在设备 DMA 期间同时修改 buffer，可能产生数据竞争或 cache 一致性问题。

简单记忆：

```text
map 给设备后，就先别乱动
设备完成并 unmap 后，CPU 再继续用
```

## 17 DMA 方向和 Cache 同步关系

DMA 方向会影响 Cache 同步方式。

| DMA 方向 | 场景 | Cache 关注点 |
|---|---|---|
| DMA_TO_DEVICE | 设备从内存读 | CPU 写入的数据要先到内存 |
| DMA_FROM_DEVICE | 设备向内存写 | CPU 读取前不能读旧 Cache |
| DMA_BIDIRECTIONAL | 设备既读又写 | 两方面都要考虑 |

容易记错的一点：

```text
DMA_TO_DEVICE：数据从内存到设备
DMA_FROM_DEVICE：数据从设备到内存
```

方向是从设备视角命名的。

## 18 Cache 和 MMIO 的关系

MMIO 区域通常不应该像普通内存一样缓存。

原因是设备寄存器访问有副作用。

例如：

```text
读状态寄存器可能清除状态
写控制寄存器可能启动设备
写清中断寄存器可能清除中断
```

如果 MMIO 被错误缓存，可能出现严重问题：

```text
读状态寄存器一直读到旧值
写控制寄存器没有真正到达设备
重复读取被编译器或 CPU 优化
设备行为异常
```

所以 Linux 驱动中访问 MMIO 应使用：

```c
readl()
writel()
```

而不是把设备寄存器当普通内存变量访问。

## 19 Cache 和内存屏障

Cache 一致性和内存访问顺序也有关。

CPU 和编译器可能为了性能调整访问顺序。

但驱动访问硬件时，有些顺序必须保证。

例如：

```text
先写 DMA 地址
再写 DMA 长度
最后写启动寄存器
```

如果顺序乱了，设备可能在参数还没写完整时就启动。

Linux 提供了一些内存屏障和 I/O 访问接口来保证顺序。

初学阶段先记住：

```text
驱动中不要用普通指针随便访问 MMIO
优先使用 readl/writel 等内核接口
涉及 DMA 时使用 DMA API
```

后面学习更深入时，再理解：

```text
mb()
rmb()
wmb()
dma_wmb()
dma_rmb()
readl_relaxed()
writel_relaxed()
```

## 20 False Sharing 是什么

False Sharing 通常翻译为伪共享。

它是多核 CPU Cache 中常见的性能问题。

因为 Cache 是按 Cache Line 管理的。

假设一个 Cache Line 是 64 字节，里面有两个变量：

```text
变量 A：CPU0 频繁写
变量 B：CPU1 频繁写
```

即使 A 和 B 是两个不同变量，只要它们位于同一个 Cache Line，不同 CPU 核心反复写它们时，也会导致这个 Cache Line 在多个 CPU Cache 之间来回失效。

这会严重影响性能。

简单理解：

```text
伪共享 = 不同 CPU 写不同变量，但这些变量在同一个 Cache Line 中，导致 Cache 频繁抖动
```

初学阶段只需要知道它是多核性能问题，不需要过早深入。

## 21 Cache 和性能优化的基本思路

写程序时，可以通过更好的内存访问方式提升 Cache 命中率。

常见原则：

```text
尽量连续访问内存
减少随机访问
热点数据放在一起
避免频繁跨大范围访问
减少无意义的数据拷贝
多核并发时注意伪共享
```

例如数组连续遍历通常比链表随机访问更容易利用 Cache。

数组：

```text
内存连续，Cache 友好
```

链表：

```text
节点分散，可能频繁 Cache miss
```

所以在性能敏感代码中，数据结构的内存布局非常重要。

## 22 常见命令和观察方法

查看 CPU Cache 信息：

```bash
lscpu
```

查看更详细的 Cache 层级信息：

```bash
ls /sys/devices/system/cpu/cpu0/cache/
```

查看每级 Cache 信息：

```bash
cat /sys/devices/system/cpu/cpu0/cache/index0/level
cat /sys/devices/system/cpu/cpu0/cache/index0/type
cat /sys/devices/system/cpu/cpu0/cache/index0/size
cat /sys/devices/system/cpu/cpu0/cache/index0/coherency_line_size
```

查看所有 Cache 信息：

```bash
for i in /sys/devices/system/cpu/cpu0/cache/index*; do
    echo "== $i =="
    cat $i/level
    cat $i/type
    cat $i/size
    cat $i/coherency_line_size
done
```

查看性能事件可以使用：

```bash
perf stat ./your_program
```

如果系统支持，也可以观察 cache 相关事件：

```bash
perf stat -e cache-references,cache-misses ./your_program
```

## 23 常见理解误区

### 23.1 Cache 不是普通内存

Cache 是内存数据的高速副本，不是程序直接管理的一块普通内存。

程序访问的仍然是地址，CPU 硬件负责决定是否命中 Cache。

### 23.2 Cache 命中不改变程序语义，但影响性能

普通程序通常不用关心每次访问是否命中 Cache。

但 Cache 命中率会明显影响性能。

### 23.3 多核 Cache 一致性不等于不用加锁

硬件 Cache 一致性可以保证多个 CPU 看到的数据副本不会长期矛盾。

但它不能保证多个线程修改共享变量时的逻辑正确性。

并发代码仍然需要锁、原子操作或其他同步机制。

### 23.4 DMA 不能忽略 Cache

设备 DMA 直接访问内存，可能绕过 CPU Cache。

所以驱动必须使用 DMA API 处理地址映射和缓存同步。

### 23.5 MMIO 不应该当普通内存缓存

设备寄存器访问有副作用。

MMIO 区域通常应该使用 device memory 属性，并通过 `readl()`、`writel()` 访问。

## 24 总结

Cache 可以这样理解：

```text
Cache 是 CPU 和内存之间的高速缓存
它保存内存数据的副本
目的是减少 CPU 等待内存的时间
```

Cache 一致性问题可以这样理解：

```text
同一份数据可能同时存在于 CPU Cache、DDR、其他 CPU Cache 或设备 DMA 视角中
如果这些副本不同步，就会产生一致性问题
```

驱动开发中要特别记住：

```text
DMA 不能直接使用普通指针
设备读内存前，要确保 CPU 写入数据对设备可见
设备写内存后，要确保 CPU 不读旧 Cache
Linux 驱动应使用 DMA API 处理缓存一致性
MMIO 区域不能当普通缓存内存访问
```

一句话总结：

```text
Cache 提高了 CPU 访问内存的性能，但也带来了多核和 DMA 场景下的数据一致性问题。
```
