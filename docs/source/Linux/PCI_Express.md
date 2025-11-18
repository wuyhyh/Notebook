# PCI Express

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

![img.png](img.png)

## Extensions and future directions

## Hardware protocol summary

PCI Express is a layered protocol, consisting of a transaction layer, a data link layer, and a physical layer.
The Data Link Layer is subdivided to include a media access control (MAC) sublayer. The Physical Layer is subdivided
into logical and electrical sublayers. The Physical logical-sublayer contains a physical coding sublayer (PCS).

PCIe 是一个层次化的协议。






















