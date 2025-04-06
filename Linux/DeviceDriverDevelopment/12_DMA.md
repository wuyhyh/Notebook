# 第12章 DMA 直接内存访问

DMA 允许设备在没有 CPU 干预的情况下访问主存储器 RAM，CPU 可以去完成其他任务。

DMA 控制器是负责管理 DMA的外设

本章涉及的主题：

- 一致性和非一致性DMA映射，以及一致性问题
- DMA引擎API
- DMA和DT绑定

## 12.1 设置DMA映射

## 12.2 完成的概念

## 12.3 DMA引擎API

# 面试？

DMA（Direct Memory Access）是内核驱动开发、嵌入式开发面试中的**高频考点**，特别是在设备驱动、总线控制器、SoC平台中经常被问到。下面为你系统梳理：

---

## 一、你必须掌握的 DMA 核心知识点

### 1. 什么是 DMA？为什么要用它？

> DMA（直接内存访问）是一种让**外设绕过 CPU**、直接访问内存的机制，用来提高数据传输效率、减少 CPU 干预。

**不使用 DMA 的问题：**

- 数据必须通过 CPU 中转；
- CPU 频繁参与读写，效率低；
- 无法处理大规模高速数据传输（如音频、网络、存储）。

**使用 DMA 后：**

- CPU 只负责启动传输；
- 实际搬运由 DMA 控制器完成；
- CPU 可以并发做其他事，提高系统吞吐率。

---

### 2. DMA 的基本原理

DMA 控制器将**源地址**的数据搬运到**目的地址**：

```
+-----------+       +--------------+       +-------------+
| 外设/内存 | <---> | DMA 控制器   | <---> | 系统内存     |
+-----------+       +--------------+       +-------------+
```

- DMA 控制器接收配置请求（源地址、目的地址、传输大小）；
- 开始传输时通过总线从一个区域搬到另一个区域；
- 传输完成后发起 **中断** 通知 CPU。

---

### 3. DMA 的分类（按传输方式）

| 类型                    | 描述             |
|-----------------------|----------------|
| **内存到外设**（Mem-to-Dev） | 比如音频播放、串口发送    |
| **外设到内存**（Dev-to-Mem） | 比如 ADC 采样、串口接收 |
| **内存到内存**（Mem-to-Mem） | 比如图像搬运、缓存刷新    |

---

### 4. 驱动开发中使用 DMA 的关键接口（Linux 内核 API）

| 功能             | 函数接口                                  |
|----------------|---------------------------------------|
| 分配 DMA 缓冲区（连续） | `dma_alloc_coherent()`                |
| 映射用户空间/动态地址    | `dma_map_single()` / `dma_map_page()` |
| 解映射            | `dma_unmap_single()`                  |
| 获取物理地址         | `dma_handle_t` 返回的是**设备可访问的地址（总线地址）** |
| 获取设备结构体支持      | `struct device *dev` 是 DMA 分配的关键参数    |

---

### 5. `dma_alloc_coherent()` 示例代码

```c
void *cpu_addr;
dma_addr_t dma_handle;

cpu_addr = dma_alloc_coherent(dev, size, &dma_handle, GFP_KERNEL);
```

- `cpu_addr`：CPU 访问的虚拟地址；
- `dma_handle`：设备访问的物理地址；
- 分配的是一致性缓冲区（cache coherent）。

---

### 6. DMA 的缓存一致性问题（重要！）

DMA 缓冲区可能绕过 CPU Cache：

- 使用 `dma_alloc_coherent()` 的区域是不可缓存的，**无须手动同步**；
- 使用 `dma_map_single()` 映射普通内存时，必须配合：
    - `dma_sync_single_for_device()`
    - `dma_sync_single_for_cpu()`

---

### 7. 设备树中的 DMA

DMA 通常通过设备树传递 DMA 控制器和通道信息，比如：

```dts
dma-names = "tx", "rx";
dmas = <&dma1 1>, <&dma1 2>;
```

驱动中使用 `of_dma_request_slave_channel()` 获取 DMA 通道。

---

## 二、DMA 面试常见问题清单（含答题要点）

| 面试问题                                               | 你应该知道的要点                                              |
|----------------------------------------------------|-------------------------------------------------------|
| 什么是 DMA？                                           | DMA 是一种硬件机制，用于绕过 CPU 直接搬运数据，提高效率。                     |
| 为什么用 DMA 而不是直接 CPU copy？                           | 减少 CPU 负担，提升吞吐率，适用于大规模、频繁传输场景。                        |
| 如何在 Linux 驱动中分配 DMA 缓冲区？                           | 使用 `dma_alloc_coherent()`，返回虚拟地址和设备访问地址。              |
| DMA 的缓存一致性问题如何处理？                                  | coherent 区不需要同步；非一致性内存使用 `dma_sync_*()`。              |
| `dma_map_single()` 和 `dma_alloc_coherent()` 有什么区别？ | 前者映射已有内存，后者分配连续 DMA 内存，适用于不同场景。                       |
| DMA 传输完成后如何通知 CPU？                                 | DMA 控制器会发出中断，驱动中设置 ISR 进行处理。                          |
| 设备树中 DMA 是如何描述的？                                   | 使用 `dmas` 和 `dma-names`，驱动通过 `of_dma_request_*()` 获取。 |

---

## 三、进阶 & 项目经验加分项

- 知道 **DMA Engine 框架** 的使用（`dma_request_chan()`、`dma_async_device` 等）；
- 熟悉平台 DMA 控制器（如 pl330、SDMA、EDMA）；
- 了解 Scatter-Gather 模式（DMA 分散内存表）；
- 能描述一个实际 DMA 传输流程（如音频录音、LCD 显存刷新）；
- 用过 zero-copy 机制优化 DMA 与网络/USB子系统结合；

---

## 四、答题模板（适合面试快速回答）

### Q: 简要说说 DMA 是什么？使用场景有哪些？

> DMA（Direct Memory Access）是一种硬件机制，允许外设直接访问系统内存，而无需 CPU 参与。它用于提升数据搬运效率，降低 CPU
> 占用，广泛应用于音频、网络、视频采集、串口等高频数据交互的场景。

---

### Q: Linux 中如何分配 DMA 缓冲区？

> 在驱动中通常使用 `dma_alloc_coherent()` 函数，该函数返回 CPU 可访问的虚拟地址和设备可访问的总线地址。例如：

```c
void *vaddr;
dma_addr_t dma_handle;
vaddr = dma_alloc_coherent(dev, size, &dma_handle, GFP_KERNEL);
```

---

### Q: 如何处理 DMA 与缓存一致性问题？

> 使用 `dma_alloc_coherent()` 分配的内存是不可缓存的，系统保证 cache coherent，无需同步。但如果使用 `dma_map_single()`
> 映射普通内存，必须使用 `dma_sync_single_for_device()` 和 `dma_sync_single_for_cpu()` 来手动同步缓存。
