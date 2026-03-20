# chapter 2 体系结构概览 architecture overview

## 2.1 PCIe transaction 简介

PCIe 使用数据包进行数据传输：TLP

PCIe 事务可以有两个维度的分类：存储器事务、IO事务、配置事务、消息事务；posted 和 non-posted

![img_2.png](../../_static/_pic/transaction_types.png)

### 2.1.1 PCIe transaction protocol 事务层协议

![img_2.png](../../_static/_pic/TLP_types.png)

不同的 TLP 数据包由不同的事务来使用。

错误处理一般是由软件层进行处理的。

> PCIe 中不同事务会映射为不同类型的 TLP。对于需要原子性保证的访问，PCIe 不再采用传统 PCI 的总线锁，而更多体现为锁定/原子事务语义。
>
> 当请求者与完成者不能正常完成事务时，链路层和事务层会先检测并上报错误，而最终的重试、恢复或失败处理通常由请求者侧的软件栈负责。

### 2.1.2 一些事务示例

请求者和完成者之间完成一次事务需要传递一系列的数据包。

#### 一、四类常见事务的数据包流动：简短总结

##### 1. Memory Write

**流动：Requester → Completer**

* 请求包里**已经带数据**
* 目标收到后写入对应地址
* **通常没有 Completion 返回**
* 属于 **Posted Request**

你可以记成一句话：

> **写操作把数据直接送过去，所以通常单向结束。**

---

##### 2. Memory Read

**流动：Requester → Completer → Completion with Data → Requester**

* Requester 先发出读请求
* 请求里只有“我要读哪里、读多少”
* 目标取到数据后，再回一个 **Completion with Data**
* 属于 **Non-Posted Request**

一句话记忆：

> **读操作的数据不在请求里，只能靠 Completion 带回来。**

---

##### 3. Config Read / Write

**流动：Requester → Target Function → Completion → Requester**

* 用来访问 **配置空间**
* Read：返回 **Completion with Data**
* Write：通常也要返回 **Completion（一般不带数据，只给状态）**
* 通常属于 **Non-Posted Request**

一句话记忆：

> **配置访问更像控制/管理访问，所以通常要明确回执。**

---

##### 4. Message

**流动：Requester → 接收方 / 系统中的某个逻辑目标**

* 用来传递**事件/通知/控制消息**
* 常见如中断、错误上报、电源管理消息等
* **多数 Message 是 Posted**
* 一般**没有 Completion**

一句话记忆：

> **Message 更像“通知”，不是普通读写。**

---

##### 把它们再压缩成一张最小表

| 事务           | 基本流动                           |         是否带数据 | 是否要 Completion | 类型         |
|--------------|--------------------------------|--------------:|---------------:|------------|
| Memory Write | 单向：Requester → Target          |        请求里带数据 |              否 | Posted     |
| Memory Read  | 双向：Req → Cplter → Completion回返 | Completion带数据 |              是 | Non-Posted |
| Config Read  | 双向                             | Completion带数据 |              是 | Non-Posted |
| Config Write | 双向                             |        请求里带数据 |       是，通常只回状态 | Non-Posted |
| Message      | 多数单向                           |         视消息而定 |            多数否 | 多数 Posted  |

你脑子里先只留一句总纲：

> **写多半单向，读一定回包，配置访问重回执，消息主要是通知。**

---

#### 二、CPU 发出的 request 和 EP 发出的 request，有很大区别吗？

有区别，但**你现阶段不用把它想得太复杂**。你现在这样理解最合适：

> **先重点区分：是谁在发起事务，它在 PCIe 拓扑里扮演什么角色。**

更具体一点：

---

##### 1. 从协议动作上看：本质都是“Requester 发 TLP”

不管是谁发，只要它在这笔事务里是发起者，它就是 Requester。

比如：

* CPU/主机侧发 Memory Read 去读 EP BAR
* EP 发 DMA Write 往主机内存写数据
* EP 发 DMA Read 去主机内存取数据

这些都符合：

* 有发起方 requester
* 有目标 completer
* 如果是 non-posted，要有 completion

所以从**事务模板**上看，差异没你想象得那么大。

---

##### 2. 从系统角色上看：RC 发起和 EP 发起，意义不同

这个区别你要开始有感觉。

###### RC 发起

典型是：

* CPU 通过 Root Complex 发配置访问
* CPU 访问设备 BAR（MMIO）
* 系统初始化、枚举、驱动寄存器访问

这类事务常常是：

* **主机控制设备**
* 偏管理、控制、寄存器访问

---

###### EP 发起

典型是：

* 网卡/NVMe/加速器发 DMA
* EP 往主机内存写数据
* EP 从主机内存读描述符/命令队列

这类事务常常是：

* **设备主动访问主机内存**
* 偏数据搬运、DMA 数据面

---

#### 三、IO 读写是不是只是为了兼容 PCI？

**基本可以这么理解。**

更准确一点说：

> **PCIe 规范保留了 IO Read / IO Write 事务，主要是为了兼容传统 PCI / x86 I/O 空间模型。**
> **但现代绝大多数 PCIe 设备的正常编程接口，主要都是 MMIO，也就是 Memory Read / Memory Write。**

所以你的方向是对的。

---

##### 1. 为什么会有 IO 事务

传统 PCI 时代，地址空间常分两类：

* **Memory Space**
* **I/O Space**

在 x86 里，I/O Space 甚至还有专门的指令：

* `in`
* `out`

所以为了兼容这套历史模型，PCIe 还保留了：

* IO Read
* IO Write

---

##### 2. 现代 PCIe 设备主要还是 MMIO

现实工程里，大多数 PCIe 设备：

* BAR 映射成 **Memory Space**
* 驱动通过 MMIO 读写寄存器
* 数据面靠 DMA

也就是说，平时你最常见的是：

* RC 对 EP BAR 做 **Memory Read/Write**
* EP 对主机内存做 **Memory Read/Write**

而不是 IO Read/Write。

---

所以更准确的表述是：

> **现代 PCIe 设备主要依赖 MMIO 和 DMA，因此 Memory Read/Write 最重要；IO Read/Write 更多是历史兼容语义。**

---

## 2.2 PCIe 设备层 device layer

PCIe 规范是一种分层的设备设计体系结构。

transaction layer、data link layer、physical layer

垂直方向上又能进一步分为两部分：处理出站流量的发送部分、处理入站流量的接收部分。

![img_2.png](../../_static/_pic/pcie_device_layer.png)

### 2.2.2 device layers 和对应的数据包

TLP DLLP PLP

#### TLP

PCIe 事务使用的 TLP 起源于发送设备的 transaction layer，终止于接收设备的 transaction layer.

软件层和设备核心将装配 TLP 的信息传递给 transaction layer。

#### DLLP

DLLP 起止于数据链路层。

#### PLP

PLP 起止于物理层

TLP 是事务主体；LCRC 是链路保护；DLLP 是链路层另发的控制包

### 2.2.3 各 PCIe 设备层的功能

![img_2.png](../../_static/_pic/pcie_dev_layers.png)

#### device core / software layer

device core 层向 transaction layer 提供生成 TLP 的必要信息，同时也接收来着 transaction layer 的信息。

#### transaction layer

处理层负责生成出站 TLP 流量和接收入站 TLP 流量。

处理层含有 VC 缓冲区，用于存储 TLP，并能对 TLP 进行排序，支持 QoS 协议。

处理层支持4种地址空间：存储器地址空间、IO地址空间、配置地址空间和消息空间。

完成者会记住请求者的标记字段中的请求者 ID，并使用相同的 ID。

**流量控制**是在硬件级自动管理的，对软件是透明的。

**QoS** 为不同的 TLP 提供不同的带宽时延传输服务。
VC 缓冲区的优先级是可以配置的。

不同类型/不同服务等级的 TLP，可以映射到不同 VC；
当多个 VC 都想占用同一个输出链路时，要做 **VC 仲裁**。

不同 TLP 携带的 TC 会被映射到不同 VC。
VC 主要是按 TC/QoS 分类承载流量，不是单纯按 TLP 功能类型分类。

当某个 Switch 的同一输出端口上有多个 VC 都存在待发送流量时，需要进行 **VC 仲裁**，以决定哪个 VC 先获得发送机会。

在选定的发送端口以及候选 VC 范围内，若仍有多个 TLP 可发送，则需要进一步进行**端口仲裁**，决定具体哪个 TLP 先发出端口

**事务顺序**：处理层需要维护 TC 标志相同的 TLP 之间的顺序是正确的。

**电源管理**：硬件会进行活动状态电源管理，软件通过配置寄存器也可以管理设备的电源状态。

**配置寄存器**：在初始化和总线计数时由驱动程序进行配置。

#### 数据链路层

数据链路层保证链路上的数据包的完整性。

数据链路层对 TLP 和 DLLP 的影响：数据链路层将一个12比特的序列和一个32比特的 LCRC 字段与处理层出站的 TLP 连接到一起。

![img_2.png](../../_static/_pic/pcie_dl.png)

数据链路层的初始化由硬件完成，没有软件参与。

#### 物理层

物理层分为两部分：逻辑物理层和电气物理层

物理层负责初始化和定向链路:**链路训练**

![img_2.png](../../_static/_pic/TLP_at_pl.png)

## 2.3 Non-posted memory read transaction 例子

![img_2.png](../../_static/_pic/mem_read_phase.png)

## 2.4 热插拔

PCIe 支持热插拔

## 2.5 PCIe 性能

交换器支持**直接交换**模式：Switch 直接在端口之间转发数据包，不进行缓存。
