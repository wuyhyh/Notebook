# PCI Express 体系结构标准教材 reading plan

我先给你一个总判断：

**这本书不适合“从头到尾顺读”。**
对你这种目标——**操作系统适配、Linux PCIe 框架理解、驱动开发、PCIe Switch 行为分析**——最合理的方法是：

* **先建立软件视角**
* **再补路由/枚举/配置空间**
* **再进入中断、错误处理**
* **最后按需要补物理层、功耗、热插拔**

否则你很容易一开始就陷进：

* 8b/10b
* Ordered Set
* LTSSM 细状态
* Electrical idle
* Eye diagram
* ACK/NAK timer
* VC arbitration 具体算法

这些东西当然重要，但**不是你当前最值钱的起点**。

---

# 一、先给出最终阅读优先级

如果你的目标是 **OS 适配 + 驱动 + Switch 理解**，我建议整本书优先级这样排：

## 第一梯队：必须先读

* **Chapter 2: Architecture Overview**
* **Chapter 3: Address Spaces & Transaction Routing**
* **Chapter 4: Packet-Based Transactions**
* **Chapter 19: Configuration Overview**
* **Chapter 20: Configuration Mechanisms**
* **Chapter 21: PCI Express Enumeration**
* **Chapter 22: PCI Compatible Configuration Registers**
* **Chapter 24: Express-Specific Configuration Registers**
* **Chapter 9: Interrupts**
* **Chapter 10: Error Detection and Handling**

这几章读完，你就已经具备了：

* 看懂 PCIe 软件模型
* 理解 RC / Switch / EP
* 理解 Memory / Config / Message / Completion
* 理解 Type 0 / Type 1 header
* 理解 bus numbering / BAR / bridge window
* 理解枚举流程
* 理解 MSI / INTx
* 理解 AER / UR / CA / Completion Timeout
* 理解 Switch 在系统中的“桥”属性和路由行为

这才是你当前最需要的能力。

---

## 第二梯队：需要时重点补

* **Chapter 6: QoS/TCs/VCs and Arbitration**
* **Chapter 7: Flow Control**
* **Chapter 8: Transaction Ordering**
* **Chapter 13: System Reset**
* **Chapter 14: Link Initialization & Training**
* **Chapter 16: Power Management**
* **Chapter 17: Hot Plug**

这些章节适合在你已经能跑通基本系统后补：

* Switch 内部仲裁和性能行为
* Credit flow control
* relaxed ordering
* 热复位 / Fundamental Reset
* LTSSM / 链路训练
* ASPM / L0s / L1 / PME
* 热插拔控制器与软件交互

---

## 第三梯队：先知道存在，不急着细读

* **Chapter 5: ACK/NAK Protocol**
* **Chapter 11: Physical Layer Logic**
* **Chapter 12: Electrical Physical Layer**
* **Chapter 15: Power Budgeting**
* **Chapter 18: Add-in Cards and Connectors**
* **Chapter 23: Expansion ROMs**
* Appendices（按需查）

这些更偏：

* 链路级可靠传输细节
* PHY / 电气 / 板级信号
* 插卡硬件规范
* Option ROM / BIOS 启动链
* 规范补充资料

对你当前的软件适配主线，不该先砸太多时间。

---

# 二、最适合你的实用阅读计划

我给你做成三个版本，你可以选。

---

# 版本 A：两周实战型阅读计划

适合你现在已经在做系统适配、希望尽快形成战斗力。

## 第 1 阶段：建立软件总图（3 天）

### Day 1

读：

* Chapter 1 只浏览
* **Chapter 2** 前半

    * Introduction to PCI Express Transactions
    * PCI Express Device Layers
    * Device Layers and their Associated Packets
    * Function of Each PCI Express Device Layer

目标：

* 搞清楚 TLP / DLLP / PLP 各干什么
* 搞清楚 Transaction / Data Link / Physical 三层分工
* 搞清楚 posted / non-posted / completion 的基本模型

你读完这部分后，脑子里应该能回答：

* 为什么 PCIe 主要看 TLP
* DLLP 为什么不是“业务数据包”
* Completion 为什么重要

---

### Day 2

继续读 **Chapter 2**：

* Flow Control
* Traffic Classes and Virtual Channels
* Port Arbitration and VC Arbitration
* Transaction Ordering
* Configuration Registers
* Example of a Non-Posted Memory Read Transaction

目标：

* 把你前面问过的问题彻底打通：

    * VC 仲裁是什么
    * Port 仲裁是什么
    * 两者关系是什么
    * 非 Posted Read 为什么一定有 Completion
    * TLP 在链路上传输时经历了什么

---

### Day 3

读 **Chapter 3**
重点：

* Transaction Layer Packet Routing Basics
* TLPs Used to Access Four Address Spaces
* Three Methods of TLP Routing
* Header Fields Define Packet Format and Routing
* Address Routing
* ID Routing
* Implicit Routing

目标：

* 理解 Memory / IO / Config / Message 四种地址/访问空间
* 理解 address-routed、ID-routed、implicit-routed
* 理解 Switch 为什么能转发不同类型 TLP

这一天特别关键。
**你对 Switch 的理解，基本就从这章开始变得扎实。**

---

## 第 2 阶段：打通配置空间、桥、枚举（4 天）

### Day 4

继续 **Chapter 3**
重点：

* Plug-And-Play Configuration of Routing Options
* Type 0 / Type 1 headers
* BARs
* Base/Limit Registers
* Bus Number Registers
* A Switch Is a Two-Level Bridge Structure

目标：

* 理解桥/交换机为何需要 Primary/Secondary/Subordinate Bus Number
* 理解 Type 0 对 endpoint，Type 1 对桥/端口
* 理解 bridge window / memory base-limit / I/O base-limit

这一部分读明白后，你看 Linux PCI 的桥配置就不会再觉得“像黑魔法”。

---

### Day 5

读 **Chapter 19 + Chapter 20**
重点：

* Configuration Overview
* Configuration Mechanisms
* Type 0 Configuration Request
* Type 1 Configuration Request
* Initial Configuration Accesses
* CRS

目标：

* 理解配置事务只能由 RC 发起
* 理解配置事务为什么只往下游走
* 理解 BIOS/固件/OS 访问配置空间时的基本机制
* 理解 CRS（Configuration Request Retry Status）是什么

---

### Day 6

读 **Chapter 21: PCI Express Enumeration**

重点：

* Enumerating a System With a Single Root Complex
* Enumerating a System With Multiple Root Complexes
* The Enumeration Process
* A Multifunction Device Within a Root Complex or a Switch
* An Endpoint Embedded in a Switch or Root Complex
* Root Complex Register Blocks (RCRBs)

目标：

* 把枚举过程串起来
* 理解 bus/device/function 是如何逐步分配和发现的
* 理解为什么 Switch 后面还能继续扫
* 理解 multifunction device 和 switch port 的差别

---

### Day 7

读 **Chapter 22 + Chapter 24**
重点读这些寄存器相关内容：

**Chapter 22**

* Vendor ID / Device ID / Revision ID
* Class Code
* Command / Status
* Capabilities Pointer
* BAR
* Header Type 1
* Bus Number Registers
* Bridge Command / Status
* Bridge memory / I/O filters

**Chapter 24**

* PCI Express Capability Register Set
* Device Capabilities / Control / Status
* Link Capabilities / Control / Status
* Slot Registers（浏览）
* Root Port Registers（浏览）
* AER
* VC Capability（先浏览）

目标：

* 看懂 `lspci -vv` 的大部分内容
* 看懂 Linux PCI core 为什么会改这些寄存器
* 看懂 link speed / width / retrain / error status 等字段

---

## 第 3 阶段：驱动关键点（3 天）

### Day 8

读 **Chapter 4**
重点：

* TLP Structure
* Generic Header Field Summary
* Header Type / Format Field Encodings
* Memory Requests
* Configuration Requests
* Completions
* Message Requests

目标：

* 真正会读 TLP
* 知道各类请求包头的核心字段
* 理解 Completion header 里那些状态字段

---

### Day 9

继续 **Chapter 4**
重点：

* INTx Interrupt Signaling
* Power Management Messages
* Error Messages
* Hot Plug Signaling Message
* Data Link Layer Packets（只看总览，不深挖格式细节）

目标：

* 理解消息类事务的地位
* 知道 MSI/错误/热插拔很多事情不是 MMIO，而是 Message 或相关机制

---

### Day 10

读 **Chapter 9: Interrupts**
重点：

* Message Signaled Interrupts
* MSI capability register set
* Basics of MSI configuration
* Basics of Generating an MSI Interrupt Request
* Legacy PCI Interrupt Delivery
* Virtual INTx Signaling
* Devices May Support Both MSI and Legacy Interrupts

目标：

* 理解 MSI 的本质
* 理解为什么 MSI 比 INTx 好
* 理解驱动 `pci_alloc_irq_vectors()` 背后做了什么

---

## 第 4 阶段：调试与故障定位（2 天）

### Day 11

读 **Chapter 10**
重点：

* PCI Express Error Checking Mechanisms
* Sources of PCI Express Errors
* ECRC
* Malformed TLP
* Unsupported Request
* Completer Abort
* Unexpected Completion
* Completion Time-out
* Error Classifications

目标：

* 建立“错误语义字典”
* 以后看到日志，不再只会觉得“报错了”，而是知道是哪类协议层问题

---

### Day 12

继续 **Chapter 10**
重点：

* Baseline Error Detection and Handling
* Advanced Error Reporting Mechanisms
* Root Complex Error Tracking and Reporting
* Summary of Error Logging and Reporting

目标：

* 理解 AER 和 Root Port 日志路径
* 理解设备、桥、RC 分别怎么看待错误

---

## 第 5 阶段：按需深入（2 天）

### Day 13

读 **Chapter 6 + Chapter 7**
重点：

* Traffic Classes and Virtual Channels
* Virtual Channel Arbitration
* Port Arbitration
* Switch Arbitration Example
* Flow Control Concept
* Flow Control Credits
* FC Init / FC Update

目标：

* 专门解决 Switch 性能和仲裁问题
* 理解 credit-based flow control 的工作方式

---

### Day 14

读 **Chapter 13 + Chapter 14**（只抓关键）
重点：

* Fundamental Reset
* Hot Reset
* Link Initialization and Training Overview
* Ordered-Sets Used During LTSSM
* LTSSM Overview
* Link Status / Link Control registers

目标：

* 理解复位和链路训练
* 为你以后分析链路起不来、速率不对、宽度不对、反复 recovery 做准备

---

# 版本 B：四周稳扎稳打计划

适合你想吃得更透一点。

## 第 1 周：总体架构 + 路由 + TLP

* Ch1 浏览
* Ch2 全读
* Ch3 全读
* Ch4 前半精读

## 第 2 周：配置空间 + 枚举 + 寄存器

* Ch19
* Ch20
* Ch21
* Ch22
* Ch24 前半

## 第 3 周：驱动运行期机制

* Ch9
* Ch10
* Ch6
* Ch7
* Ch8（至少读 ordering 总体概念）

## 第 4 周：链路、复位、功耗、热插拔

* Ch13
* Ch14
* Ch16
* Ch17
* Ch11/12 只浏览你关心的小节

---

# 版本 C：面向 Linux PCIe 驱动的最短路线

如果你只想先快速支撑 Linux 开发，直接读下面这些。

## 必读章节

* Ch2
* Ch3
* Ch4
* Ch9
* Ch10
* Ch19
* Ch20
* Ch21
* Ch22
* Ch24

## 第二批补充

* Ch6
* Ch7
* Ch13
* Ch14
* Ch16

## 暂时跳过

* Ch5
* Ch11
* Ch12
* Ch15
* Ch17
* Ch18
* Ch23
* Appendices

---

# 三、每章怎么读，最省时间

下面我直接给你“读法”，不是只说读什么。

---

## 1）Chapter 2 怎么读

### 必看

* Transactions
* Device Layers
* TLP / DLLP / PLP
* Flow Control
* TC / VC
* Port Arbitration / VC Arbitration
* Example of Non-Posted Memory Read

### 可略读

* Performance and Data Transfer Efficiency
* Hot Plug（先知道概念）

### 读完应掌握

* PCIe 业务核心是 TLP
* DLLP 用于链路控制
* PLP 偏物理传输表示
* Memory Read 一定分 Request/Completion 两段
* 事务层和链路层关注点不同

---

## 2）Chapter 3 怎么读

### 必看

* Routing Basics
* Three Methods of TLP Routing
* Address / ID / Implicit Routing
* Type 0 / Type 1 header
* BAR
* Base/Limit
* Bus Number Registers
* Switch as Two-Level Bridge

### 读完应掌握

* Switch 到底如何转发不同类型事务
* 桥为何需要 bus number 和窗口寄存器
* Config TLP 为什么和 Memory TLP 不同
* 枚举为何可以逐层向下推进

---

## 3）Chapter 4 怎么读

### 必看

* TLP Structure
* Memory Requests
* Configuration Requests
* Completions
* Message Requests

### 只看概念即可

* DLLP 细字段
* 各种消息的所有编码细节

### 读完应掌握

* 驱动看到的 MMIO/配置/中断在协议上长什么样
* 哪些请求需要 Completion
* Message 事务有哪些典型用途

---

## 4）Chapter 9 怎么读

### 必看

* MSI capability
* MSI configuration
* MSI request generation
* Legacy INTx

### 读完应掌握

* MSI 是 memory write
* INTx 是兼容机制，不是主流最佳路径
* capability 链在驱动使能中断中的作用

---

## 5）Chapter 10 怎么读

### 必看

* Error sources
* UR / CA / Unexpected Completion / Timeout
* Error classification
* AER
* Root complex reporting

### 读完应掌握

* 常见 PCIe 错误日志能对应回协议语义
* 错误由谁检测、谁上报、谁记录

---

## 6）Chapter 19~24 怎么读

这一组非常关键，建议连着读。

### Chapter 19

建立配置空间总体认知

### Chapter 20

理解配置访问机制和 Type0/Type1 request

### Chapter 21

理解枚举算法和 BDF 分配过程

### Chapter 22

吃透 Type0/Type1 配置寄存器

### Chapter 24

吃透 PCIe capability / Link / Device / AER / VC capability

### 读完应掌握

* 看懂 `lspci -vv`
* 理解 Linux 枚举桥和设备时在干什么
* 理解 BAR 分配和桥窗口分配
* 理解 link speed/width/status 寄存器

---

# 四、哪些章节你当前不该硬啃

这个我直接替你踩刹车。

## 暂时不要深挖

### Chapter 5: ACK/NAK Protocol

除非你现在做：

* 协议分析仪抓链路层包
* 调链路重传
* 做 Switch/控制器 RTL 级实现

否则这章先知道：

* ACK/NAK 是 DLLP
* 保证每一跳链路的 TLP 可靠传递
* 出错会 replay

就够了。

---

### Chapter 11 / 12: Physical / Electrical

除非你现在就在解决：

* 链路训练失败
* lane width 异常
* de-skew
* electrical idle 问题
* SI/PI / 板级信号完整性

否则别一开始扑进去。

---

### Chapter 15: Power Budgeting

对 OS 适配不是优先项。

---

### Chapter 18: Add-in Cards and Connectors

更多是板卡规范、插槽、电气接口。

---

### Chapter 23: Expansion ROMs

更多偏启动链、Option ROM、固件。

---

# 五、建议你边读边做的“配套动作”

这个非常重要。只读书不够。

## 每读完一个阶段，就做一次对应验证

### 读完 Ch2~4 后

拿一张纸自己画：

* CPU 发 Memory Read 到 EP
* EP 返回 Completion with Data
* TLP、DLLP、ACK/NAK 分别在哪一步出现
* Switch 在哪里只做转发、不改事务语义

如果你画不出来，说明还没真正懂。

---

### 读完 Ch19~24 后

结合 `lspci -vv` 看一台真实机器：

* Root Port
* Switch Upstream Port
* Switch Downstream Port
* Endpoint

分别看：

* Header Type
* BAR
* Bus Numbers
* Capabilities
* Link Cap / Link Sta
* AER
* MSI/MSI-X

这样这本书就会和真实系统接上。

---

### 读完 Ch9~10 后

去对照 Linux 内核：

* `drivers/pci/probe.c`
* `drivers/pci/setup-bus.c`
* `drivers/pci/pci.c`
* `drivers/pci/msi/`
* `drivers/pci/pcie/`
* `drivers/pci/hotplug/`
* `drivers/pci/pcie/aer.c`

你会明显发现，之前很多代码只是“看起来像流程”，读完这几章后就会变成“看得懂为什么这么写”。

---

# 六、按你当前方向，我给一个最实用的章节映射

## 目标 1：做 Linux PCIe 驱动

优先读：

* Ch2
* Ch4
* Ch9
* Ch10
* Ch22
* Ch24

## 目标 2：做 RC / 桥 / 枚举 / 系统适配

优先读：

* Ch3
* Ch19
* Ch20
* Ch21
* Ch22
* Ch24

## 目标 3：研究 PCIe Switch

优先读：

* Ch3
* Ch6
* Ch7
* Ch10
* Ch13
* Ch14
* Ch21
* Ch24

## 目标 4：排查链路起不来、掉速、降宽

优先读：

* Ch14
* Ch11
* Ch12
* Ch13
* Ch24 中 Link registers

## 目标 5：排查 ASPM / 低功耗 / 唤醒

优先读：

* Ch16
* Ch13
* Ch14
* Ch24 中 Link/PM 相关寄存器

---

# 七、我建议你的实际执行方式

别一口气读太多。用下面节奏最稳：

## 每天 1 章或半章

读的时候只做三件事：

### 1. 记“角色”

这一章里谁在做事：

* RC
* Switch
* Bridge
* EP
* Port
* Function

### 2. 记“对象”

这一章处理什么对象：

* TLP
* DLLP
* Config Header
* BAR
* Capability
* Credit
* MSI
* AER

### 3. 记“方向”

事务怎么流动：

* upstream / downstream
* request / completion
* address routed / ID routed / implicit routed

只要你一直按这三件事去读，书再厚都不会乱。

---

# 八、最终推荐阅读顺序

我给你一个最终版，直接照着走就行：

## 第一阶段：主线打通

1. Chapter 2
2. Chapter 3
3. Chapter 4
4. Chapter 19
5. Chapter 20
6. Chapter 21
7. Chapter 22
8. Chapter 24
9. Chapter 9
10. Chapter 10

## 第二阶段：增强理解

11. Chapter 6
12. Chapter 7
13. Chapter 8
14. Chapter 13
15. Chapter 14
16. Chapter 16

## 第三阶段：按需补课

17. Chapter 17
18. Chapter 5
19. Chapter 11
20. Chapter 12
21. Chapter 18
22. Chapter 23
23. Appendices

---

# 九、最简结论

如果你现在时间有限，只读下面 10 章就最值：

* **2**
* **3**
* **4**
* **9**
* **10**
* **19**
* **20**
* **21**
* **22**
* **24**

这 10 章就是你这本书里的**软件/系统/驱动主干**。

---

如果你愿意，我下一条可以继续直接给你整理成一个更适合落地执行的版本：

**《30 天 PCIe 学习打卡表（按天拆到具体小节）》**

我会直接写成：

* 第 1 天读哪些页
* 做什么笔记
* 画什么图
* 配合 Linux 看哪些命令和源码
  这样你可以直接照表推进。
