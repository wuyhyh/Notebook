# chapter 20 配置机制 configuration mechanisms

> PCI-compatible configuration space 现在仍然是现代 PCIe 系统中正在真实使用的基础部分，不只是为了兼容旧软件。
>
> Extended configuration space 则承载 PCIe 的大量增强能力，是在前者基础上的扩展。

- PCI-compatible configuration
- PCIe extended configuration

## 20.1 Introduction

每个 function 都有独立的 configuration space，大小为 4KB。

- 前 256 Bytes：PCI-compatible configuration space
- 后 3840 Bytes：PCIe extended configuration space

![img.png](pcie_pic/figure.20-1.png)

## 20.2 PCI compatible configuration mechanism

### 20.2.1 这一机制要解决的问题

PCI/PCIe 中，每个 function 都实现了一套标准的 **configuration space**，其中包含：

* Vendor ID / Device ID
* Command / Status
* BAR
* Class Code
* Capability 等寄存器

这些寄存器**位于设备 function 内部**。
因此，处理器需要一种统一机制去访问目标设备的配置空间，以便完成：

* 枚举设备
* 识别设备类型
* 分配 BAR 地址
* 使能 Memory Space / Bus Master
* 配置中断与 capability

---

### 20.2.2 PCI compatible configuration mechanism 的本质

PCI compatible configuration mechanism 是一种**传统 x86 平台上的 PCI 配置空间访问方式**。

其基本思想不是把 configuration space 直接暴露给处理器，而是由 **Root Complex / Host Bridge** 提供两个主机侧端口：

* **Configuration Address Port**
* **Configuration Data Port**

软件访问流程为：

1. 向 address port 写入目标 **Bus / Device / Function / Register** 信息，并置位 enable bit
2. 再通过 data port 对目标寄存器执行 1/2/4 字节读写
3. RC / Host Bridge 根据 address port 中保存的信息，生成真正的 PCI/PCIe configuration access

因此，这种机制本质上是：

> **通过主机侧的地址端口和数据端口，对设备内部 configuration space 进行间接访问。**

---

### 20.2.3 需要区分的两个概念

#### 1. configuration space 本体

configuration space 是每个 PCI/PCIe function 内部实现的一组标准寄存器空间。

它：

* 不在 CPU 内部
* 不在 TLP header 内部
* 不等于 address port / data port

#### 2. compatible configuration mechanism

这是**处理器访问 configuration space 的一种方法**。

也就是说：

* configuration space 是“被访问对象”
* compatible configuration mechanism 是“访问手段”

---

### 20.2.4 Configuration Address Port 的作用

处理器向 configuration address port 写入一个 32-bit 值，用来选择目标寄存器。
该值通常包含：

* Enable bit
* Bus Number
* Device Number
* Function Number
* Register Number（dword 对齐）

因此，address port 的作用是：

> **告诉 RC：本次要访问哪个 BDF 的哪个配置寄存器。**

注意：

* 这里选择的是 **dword 对齐寄存器**
* 寄存器内的 byte/word 访问，由 data port 的字节偏移完成

---

### 20.2.5 Configuration Data Port 的作用

在 address port 已经选定目标寄存器后，处理器通过 data port 执行：

* 1-byte
* 2-byte
* 4-byte

的读写。

因此，data port 的作用是：

> **对 address port 当前选中的配置寄存器执行实际数据访问。**

---

### 20.2.6 RC / Host Bridge 实际做了什么

软件并不是直接向 PCIe fabric 发送 TLP。
软件看到的只是：

* 先写 address port
* 再读写 data port

真正的转换工作由 **Root Complex / Host Bridge** 完成：

1. 记录 address port 中的 BDF 和寄存器号
2. 当软件访问 data port 时，解析目标位置
3. 生成真正的 PCI / PCIe configuration transaction
4. 将返回结果提供给处理器

所以：

> **address/data port 是主机侧接口，PCIe 配置事务才是总线侧真实发生的访问。**

---

### 20.2.7 Target Bus = 0 与 Target Bus > 0 的区别

RC 会根据 address port 中给出的 **target bus number** 决定访问类型。

#### 情况 1：Target Bus = 0

表示目标设备位于 root bus 上。
此时 RC 通常发起：

* **Type 0 Configuration Access**

在 PCIe 中对应：

* **Configuration Request Type 0**

它用于访问**当前总线上的设备**。

---

#### 情况 2：Target Bus > 0

表示目标设备位于某个 bridge / switch 的下游总线。
此时 RC 会先发起：

* **Type 1 Configuration Access**

在 PCIe 中对应：

* **Configuration Request Type 1**

它用于访问**其他总线上的设备**，请求会沿着 bridge 层次向下转发。

---

### 20.2.8 Bridge 的 bus compare 机制

每个 PCI bridge 都维护以下总线号寄存器：

* **Primary Bus Number**
* **Secondary Bus Number**
* **Subordinate Bus Number**

含义为：

* Primary：桥的上游总线号
* Secondary：桥直接下游总线号
* Subordinate：桥下游整个子树中最大的总线号

当 bridge 收到一个 **Type 1 configuration request** 时，会比较目标 bus number：

* 若 `Secondary <= Target Bus <= Subordinate`

    * 说明目标位于本桥下游子树中
    * 应继续向下游转发
* 否则

    * 目标不在本桥管理范围内
    * 不应转发

因此，bus compare 的本质是：

> **bridge 根据自己管理的总线范围，判断某个 configuration request 是否应该继续向下游传播。**

---

### 20.2.9 Type 0 与 Type 1 的关系

两者的关系可以概括为：

* **Type 1**：用于跨 bridge 寻找目标总线
* **Type 0**：用于在目标总线上选中具体 device/function

典型过程为：

1. RC 根据 target bus > 0 发起 Type 1 request
2. 中间 bridge 根据 Secondary/Subordinate 比较决定是否继续转发
3. 当请求到达目标 bus 的上游 bridge 后，Type 1 被转换为 Type 0
4. 再由目标总线上的 device/function 接收该配置访问

所以可以记为：

> **Type 1 负责“找总线”，Type 0 负责“选设备”。**

---

### 20.2.10 Single Host/PCI bridge 与 Multiple Host/PCI bridge

#### Single Host/PCI bridge

系统中只有一个 Host/PCI bridge，处理器的 compatible configuration access 统一由该桥处理。

#### Multiple Host/PCI bridge

系统中存在多个 Host/PCI bridge 或多个 PCI 层次域时，单一的一对 address/data port 在扩展性上会变得受限。

这说明 compatible mechanism 更适合：

* 传统
* 简单
* 单 host bridge 风格的系统结构

而不适合复杂、多层、多 segment 的现代系统。

---

### 20.2.11 与现代 PCIe ECAM 的区别

PCI compatible configuration mechanism 是**传统兼容方式**。
现代 PCIe 系统更常使用 **ECAM / MMCONFIG**。

两者区别如下：

#### Compatible mechanism

* 通过 address port + data port 间接访问
* 具有明显的传统 x86 兼容色彩
* 访问模型较老
* 扩展能力较弱

#### ECAM / MMCONFIG

* 将 configuration space 映射到 memory address space
* 处理器通过普通 load/store 访问配置空间
* 更适合 PCIe 的 4KB extended configuration space
* 是现代 PCIe 平台更常见的方式

因此应理解为：

> **compatible mechanism 是历史兼容路径，ECAM 是现代主流路径。**

---

### 20.2.12 本节最重要的结论

#### 1.

PCI compatible configuration mechanism 不是 configuration space 本身，
而是处理器访问 configuration space 的一种**主机侧间接访问机制**。

#### 2.

address port 用于选择目标：

* Bus
* Device
* Function
* Register

data port 用于执行实际读写。

#### 3.

如果目标位于 root bus，RC 产生 **Type 0 configuration access**；
如果目标位于 bridge 下游，则先产生 **Type 1 configuration access**。

#### 4.

bridge 通过比较：

`Secondary <= Target Bus <= Subordinate`

决定是否继续向下游转发 Type 1 request。

#### 5.

到达目标总线后，配置访问会转为 **Type 0**，再选中具体 device/function。

#### 6.

现代 PCIe 平台中，更常见的配置空间访问方式是 **ECAM / MMCONFIG**，而不是传统 compatible mechanism。

---

### 一段更短的总结版

PCI compatible configuration mechanism 是一种传统 x86 风格的 PCI 配置空间访问方法。处理器并不直接访问设备内部的
configuration space，而是先将目标 BDF 和寄存器号写入 RC/Host Bridge 提供的 configuration address port，再通过
configuration data port 执行 1/2/4 字节读写。RC 根据这些信息生成真正的 PCI/PCIe configuration access：若目标位于 root
bus，则使用 Type 0；若目标位于 bridge 下游，则先使用 Type 1，并由各级 bridge 根据 Secondary/Subordinate bus number
判断是否向下游转发，到达目标总线后再转为 Type 0。该机制是传统兼容方案；在现代 PCIe 系统中，更常见的是使用 ECAM/MMCONFIG 进行
memory-mapped configuration access。

---

## 20.3 PCIe extended configuration mechanism

每种 function 的 4KB configuration space 都开始于 4KB-aligned address
从这个地址开始的连续 4KB 区域被用作配置空间。

### 20.3.1 本质

PCIe 将每个 function 的 configuration space 从传统 PCI 的 256B 扩展为 4KB。
为了高效访问这 4KB 配置空间，PCIe 引入了 extended configuration mechanism，即将各 BDF 对应的 configuration space 统一映射到一片
memory address space 中，由软件通过普通的内存读写访问配置寄存器。这种机制通常称为 **ECAM / MMCONFIG**。

### 20.3.2 空间组织

在 ECAM 中：

* 每个 function 占用 4KB 配置空间
* 每个 function 的配置空间起始地址必须 4KB 对齐
* 每个 device 最多 8 个 functions，因此占 32KB
* 每条 bus 最多 32 个 devices，因此占 1MB

所以软件可以通过：

* bus number
* device number
* function number
* register offset

直接计算某个 function 的配置空间地址。

### 20.3.3 与 compatible mechanism 的区别

PCI compatible configuration mechanism 通过主机侧 address/data port 间接访问配置空间；
PCIe extended configuration mechanism 则通过 memory-mapped address 直接访问配置空间。
前者属于传统兼容方式，后者更适合现代 PCIe 的 4KB extended configuration space。

### 20.3.4 理解重点

extended configuration mechanism 的重点不在“配置空间变成了内存”，而在于：

* CPU 通过 memory address 访问配置空间
* RC 将该访问翻译为对目标 PCIe function configuration space 的访问
* 这种方式支持 PCIe 的完整 4KB configuration space

---

## 20.8 Initial configuration accesses

初始化期间，配置软件要访问每种功能内的配置寄存器，以确定某种功能是否存在及其资源要求。

CRS = configuration request retry completion status

### 20.8.1 本质

Initial configuration accesses 是指系统初始化阶段，BIOS/固件/OS 对 PCIe configuration space
执行的一系列早期访问，用于完成设备枚举、类型识别、资源需求探测和总线拓扑建立。

### 20.8.2 初始访问的目的

初始化阶段访问配置寄存器，主要是为了确定：

* 某个 BDF 对应的 function 是否存在
* 该 function 是 endpoint 还是 bridge
* 该 function 的类别和能力
* 该设备需要多少 BAR 空间及其属性
* bridge 下游还包含哪些 bus 和 device

### 20.8.3 典型过程

初始配置访问通常包括：

1. 读取 Vendor ID / Device ID，判断 function 是否存在
2. 读取 Header Type / Class Code，识别 function 类型
3. 探测 BAR，确定资源需求
4. 若为 bridge，则配置 Primary/Secondary/Subordinate Bus Number
5. 继续扫描下游 bus，直至完成整个 PCIe 层次枚举

### 20.8.4 CRS 的含义

CRS（Configuration Request Retry Status）表示：

> 目标 function 已存在，但当前尚未准备好完成该 configuration request，需要稍后重试。

CRS 主要出现在初始化阶段，因为设备在上电、链路训练或内部初始化尚未完成时，可能暂时无法返回正常配置数据。

### 20.8.5 理解重点

Initial configuration accesses 的核心不是“普通读写配置寄存器”，而是：

* 用配置访问完成枚举
* 用配置访问发现资源需求
* 用配置访问建立 bus 层次
* 用 CRS 区分“暂未就绪”和“设备不存在”
