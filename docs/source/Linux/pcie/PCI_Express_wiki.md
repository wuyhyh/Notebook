# PCI Express

[pcie wiki](https://en.wikipedia.org/wiki/PCI_Express#Extensions_and_future_directions)

PCI Express is abbreviation of **Peripheral Component Interconnect Express**, is a high-speed standard used to connect
hardware components inside computers.

计算机组件间的高速互联总线

PCIe is commonly used to connect graphics cards, sound cards, Wi-Fi and Ethernet adapters, and storage devices such as
solid-state drives and hard disk drives.

可以连接显卡、声卡、Wi-Fi、以太网适配器、SSD、HDD

PCIe connections are made through lanes, which are pairs of conductors that send and receive data.
Devices can use one or more lanes depending on how much data they need to transfer.

连接建立在 lane 上，根据传输数据量可以选择更多的 lanes

## Architecture

PCI Express is based on point-to-point topology, with separate serial links connecting every device to the root
complex (host).

基于点对点的 topology，采用串行 link

PCI Express bus link supports full-duplex communication between any two endpoints, with no inherent limitation on
concurrent access across multiple endpoints.

endpoints 之间全双工 link, 多个endpoints 互不影响

In terms of bus protocol, PCI Express communication is encapsulated in packets.
The work of packetizing and de-packetizing data and status-message traffic is handled by the transaction layer

总线协议基于 packets 实现
打包和解包在 transaction layer 处理。

The PCI Express link between two devices can vary in size from one to 16 lanes.
In a multi-lane link, the packet data is striped across lanes, and peak data throughput scales with the overall link
width.
The lane count is automatically negotiated during device initialization and can be restricted by either endpoint.

一个 link 包含多个 lane, 从1到16。
对于多 lanes 组成的 link, packets 数据是交织的，总的带宽等于所有 lanes 的总和。

The link can dynamically down-configure itself to use fewer lanes, providing a failure tolerance in case bad or
unreliable lanes are present. The PCI Express standard defines link widths of ×1, ×2, ×4, ×8, and ×16.

link 可以降速适应 lanes 失效的情况。一种向下兼容的设计思想。
link 包含的 lanes 数量是 2 的次方，典型的是 ×1, ×2, ×4, ×8, and ×16.

This allows the PCI Express bus to serve both cost-sensitive applications where high throughput is not needed, and
performance-critical applications such as 3D graphics, networking (10 Gigabit Ethernet or multiport Gigabit Ethernet),
and enterprise storage (SAS or Fibre Channel).

这种设计让 PCIe 可以连接 cost-sensitive 的应用，也可以连接 performance-critical 的应用。

Slots and connectors are only defined for a subset of these widths, with link widths in between using the next larger
physical slot size.

插槽和连接器的设计遵循这些 lanes 的多少。

### Interconnect

PCI Express devices communicate via a logical connection called an interconnect or link.

逻辑上的 PCIe 设备之间的连接叫做 interconnect 或者 link

A link is a point-to-point communication channel between two PCI Express ports allowing both of them to send and receive
ordinary PCI requests (configuration, I/O or memory read/write) and interrupts (INTx, MSI or MSI-X).

link 就是一个点对点的 channel，可以传输 PCI requests 和 interrupts.

### Lane

A lane is composed of two differential signaling pairs, with one pair for receiving data and the other for transmitting.
Thus, each lane is composed of four wires or signal traces.

一个 lane 由两对差分信号线组成，一对发送一对接收，因此对应 4 条 wires.

Conceptually, each lane is used as a full-duplex byte stream, transporting data packets in eight-bit "byte" format
simultaneously in both directions between endpoints of a link.

每条 lane 都工作在全双工状态下传递字节流，一个 link 中传递的是 8 比特字节格式的 packet。

The PCIe slots on a motherboard are often labeled with the number of PCIe lanes they have. Sometimes what may seem like
a large slot may only have a few lanes.

主板上的 PCIe slots 旁边会写这个 slot 支持的 lanes 有多少。但是有时候 large slot 中实际的 lanes 是更少的。

### Serial bus

Since timing skew over a parallel bus can amount to a few nanoseconds, the resulting bandwidth limitation is in the
range of hundreds of megahertz.

并行总线的设计受限于 timing skew，超过数纳秒的时序偏差带来的结果就是带宽被限制为数百 MHz

A serial interface does not exhibit timing skew because there is only one differential signal in each direction within
each lane, and there is no external clock signal since clocking information is embedded within the serial signal itself.
As such, typical bandwidth limitations on serial signals are in the multi-gigahertz range.

串行接口不存在时序偏移问题，因为一个传输方向只有一对差分信号，不需要额外的时钟信号线，时钟信息编码在串行信号内。
所以，串行信号的带宽可以达到数个 GHz

Multichannel serial design increases flexibility with its ability to allocate fewer lanes for slower devices.

多 channel 的串行信号设计增加了对慢设备分配少的 lanes 的灵活性。

## Form factors

### PCI Express add-in card

A PCI Express add-in card fits into a slot of its physical size or larger (with ×16 as the largest used), but may not
fit into a smaller PCI Express slot

一个带 PCIe 接口的卡可以放在同样大小的 slot 中，也可以放在更大的 slot 中。就是说 slot >= pins

The number of lanes actually connected to a slot may also be fewer than the number supported by the physical slot size.

前面说过的，slot 里面实际能工作的 lanes 数量可能比物理 size 小。

The cards themselves are designed and manufactured in various sizes.
For example, solid-state drives (SSDs) that come in the form of PCI Express cards often use HHHL (half height, half
length) and FHHL (full height, half length) to describe the physical dimensions of the card.

card 的大小各种各样。有的 SSD 就是 HHHL，或者 FHHL

#### Non-standard video card form factors

很多显卡的 size 做得很大

#### Pinout

The following table identifies the conductors on each side of the edge connector on a PCI Express card.
The solder side of the printed circuit board (PCB) is the A-side, and the component side is the B-side.

card 的元器件面是 B-side，焊接面是 A-side

#### Power

##### Slot power

X1 最大25W，X16 75W

##### 6- and 8-pin power connectors

外接供电线功率可以更高

### PCI Express Mini Card

PCI Express Mini Card (also known as Mini PCI Express, Mini PCIe, Mini PCI-E, mPCIe, and PEM), based on PCI Express, is
a replacement for the Mini PCI form factor.

mini PCIe 接口

### PCI Express M.2

M.2 replaces the mSATA standard and Mini PCIe.

### PCI Express External Cabling

PCIe-to-ePCIe adapter circuitry

主要用在扩展 adapter 上

#### PCI Express OCuLink

optical-copper link

光电链路

## History and revisions

### Comparison table

## Extensions and future directions

## Hardware protocol summary

PCI Express is a layered protocol, consisting of a transaction layer, a data link layer, and a physical layer.
The Data Link Layer is subdivided to include a media access control (MAC) sublayer. The Physical Layer is subdivided
into logical and electrical sublayers. The Physical logical-sublayer contains a physical coding sublayer (PCS).

PCIe 是一个层次化的协议。事务层、数据链路层、物理层。数据链路层包含 MAC 层，物理层包含逻辑层和电气层。逻辑层中包含一个 PCS
编码层。

### Physical layer

Transmit and receive are separate differential pairs, for a total of four data wires per lane.

一个 lane, 4 wires

A connection between any two PCIe devices is known as a link, and is built up from a collection of one or more lanes.

一个 link 多个 lanes

#### Data transmission

PCIe sends all control messages, including interrupts, over the same links used for data.

控制信息，中断信号，数据都使用 link 传输。

message signaled interrupts (MSI) can bypass an I/O APIC and be delivered to the CPU directly, MSI performance ends up
being substantially better.

MSI 可以不经过 APIC 直接到 CPU，所以性能会更好

Data transmitted on multiple-lane links is interleaved, meaning that each successive byte is sent down successive lanes.
The PCIe specification refers to this interleaving as data striping.

striping 技术用复杂性得到了更高的性能。

Due to padding requirements, striping may not necessarily reduce the latency of small data packets on a link.

由于填充，小数据包未必能从条带化受益。

As with other high data rate serial transmission protocols, the clock is embedded in the signal.

串行链路不需要单独的时钟线，此外编码方式是一个开销。

Dual simplex in PCIe means there are two simplex channels on every PCIe lane.

全双工模式意味着每个 lane 有两个单工通道。

### Data link layer

The data link layer performs three vital services for the PCIe link:

- sequence the transaction layer packets (TLPs) that are generated by the transaction layer,
- ensure reliable delivery of TLPs between two endpoints via an acknowledgement protocol (ACK and NAK signaling) that
  explicitly requires replay of unacknowledged/bad TLPs,
- initialize and manage flow control credits

数据链路层的三个服务：

- 序列化 TLP 包
- 支持 ACK NAK 这样的可靠传输
- 流量控制

### Transaction layer

PCI Express implements split transactions (transactions with request and response separated by time), allowing the link
to carry other traffic while the target device gathers data for the response.

transaction 中的 request 和 response 是分开的

PCI Express uses credit-based flow control.

流量控制基于 credit

### Efficiency of the link

As for any network-like communication links, some of the raw bandwidth is consumed by protocol overhead

协议开销

## Applications

PCI Express operates in consumer, server, and industrial applications, as a motherboard-level interconnect (to link
motherboard-mounted peripherals), a passive backplane interconnect and as an expansion card interface for add-in boards.

用于板上组件的互联和扩展卡接口

### External GPUs

外接显卡可以是笔记本获得和台式机一样的图形处理能力。

### Storage devices

The PCI Express protocol can be used as data interface to flash memory devices, such as memory cards and solid-state
drives (SSDs).

记忆卡和 SSD

### Cluster interconnect

Typically, a network-oriented standard such as Ethernet or Fibre Channel suffices for these applications, but in some
cases the overhead introduced by routable protocols is undesirable and a lower-level interconnect, such as InfiniBand,
RapidIO, or NUMAlink is needed.

处理器互联对 routable 协议是难以接受的。

