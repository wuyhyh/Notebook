# 06-DTS节点属性与compatible-reg-interrupts

## 1. 文档目标

本文用于整理 DTS 设备树中 **节点**、**属性** 以及几个最核心属性的基础用法，重点包括：

- 设备树节点的基本格式
- 节点名称和 unit-address 的含义
- 属性的常见类型
- `compatible` 如何用于驱动匹配
- `reg` 如何描述寄存器地址范围
- `interrupts` 如何描述中断资源
- 阅读节点属性时的基本排查方法

本文适合作为学习 Linux 驱动、板级适配、设备树修改和 DTS 调试时的基础材料。

---

## 2. 设备树节点是什么

设备树是一棵树，每一个节点通常表示一个硬件对象或者硬件相关的逻辑对象。

例如：

```dts
uart0: serial@28000000 {
	compatible = "arm,pl011";
	reg = <0x0 0x28000000 0x0 0x1000>;
	interrupts = <0 32 4>;
	status = "okay";
};
```

这个节点表示一个串口控制器。

它告诉 Linux：

- 这个设备是什么类型
- 它的寄存器地址在哪里
- 它使用哪个中断
- 它是否启用
- 它应该匹配哪个驱动

简单理解：

> 节点描述“有什么设备”，属性描述“这个设备有哪些硬件资源和配置信息”。

---

## 3. 节点的基本格式

设备树节点的一般格式如下：

```text
label: node-name@unit-address {
	property-name = property
	-value;
};
```

其中：

| 部分               | 说明                      |
|------------------|-------------------------|
| `label`          | 标签，方便其他节点通过 `&label` 引用 |
| `node-name`      | 节点名称，表示设备类型或功能          |
| `unit-address`   | 单元地址，通常和 `reg` 中的起始地址相关 |
| `property-name`  | 属性名                     |
| `property-value` | 属性值                     |

例如：

```dts
uart0: serial@28000000 {
	compatible = "arm,pl011";
	reg = <0x0 0x28000000 0x0 0x1000>;
};
```

这里：

| 内容           | 含义           |
|--------------|--------------|
| `uart0`      | 标签           |
| `serial`     | 节点名称         |
| `28000000`   | unit-address |
| `compatible` | 驱动匹配属性       |
| `reg`        | 寄存器地址范围属性    |

---

## 4. label 标签

label 是设备树源码层面的标签，主要用于引用节点。

例如：

```dts
uart0: serial@28000000 {
	compatible = "arm,pl011";
	status = "disabled";
};
```

后面可以用：

```dts
&uart0 {
	status = "okay";
};
```

这表示修改前面 `uart0` 标签对应的节点。

label 的常见用途包括：

- 板级 `.dts` 修改 SoC `.dtsi` 中已有节点
- 一个节点引用另一个节点
- `aliases` 中给设备指定别名
- `phy-handle`、`clocks`、`resets`、`gpios` 等属性引用其他节点

例如：

```dts
aliases {
	serial0 = &uart0;
};
```

这里 `&uart0` 就是引用 `uart0` 标签对应的节点。

需要注意：

> label 主要方便 DTS 源码编写，不一定会直接出现在最终运行时设备树的路径中。

---

## 5. node-name 节点名称

节点名称通常表示设备类型，而不是设备编号。

例如：

```text
serial@28000000
ethernet@2820c000
gpio@28100000
i2c@28020000
```

常见节点名称包括：

| 节点名称       | 常见含义        |
|------------|-------------|
| `serial`   | 串口控制器       |
| `ethernet` | 以太网 MAC 控制器 |
| `gpio`     | GPIO 控制器    |
| `i2c`      | I2C 控制器     |
| `spi`      | SPI 控制器     |
| `pcie`     | PCIe 控制器    |
| `memory`   | 内存节点        |
| `cpus`     | CPU 节点集合    |
| `chosen`   | 启动参数相关节点    |
| `aliases`  | 设备别名节点      |

节点名称不应该随便乱写，一般需要符合对应设备树 binding 的要求。

---

## 6. unit-address 单元地址

节点名称后面的 `@xxx` 叫 unit-address。

例如：

```text
serial@28000000
```

其中：

```text
28000000
```

就是 unit-address。

对于 MMIO 设备来说，它通常对应 `reg` 属性里的起始地址低位。

例如：

```dts
serial@28000000 {
	reg = <0x0 0x28000000 0x0 0x1000>;
};
```

这里 unit-address 是 `28000000`，`reg` 中的起始地址是 `0x0000000028000000`，二者是对应的。

但是要注意：

> unit-address 只是节点名称的一部分，不是内核真正解析寄存器地址的来源。内核真正使用的是 `reg` 属性。

如果节点有 `@unit-address`，通常应该有对应的 `reg` 属性，否则 dtc 可能给出 warning。

---

## 7. 属性是什么

属性用于描述节点的具体信息。

例如：

```dts
compatible = "arm,pl011";
reg = <0x0 0x28000000 0x0 0x1000>;
interrupts = <0 32 4>;
status = "okay";
```

这些都是属性。

属性可以描述：

- 驱动匹配信息
- 寄存器地址范围
- 中断资源
- 时钟资源
- GPIO 资源
- PHY 连接关系
- 复位控制器
- DMA 通道
- 设备启用状态
- 板级固定配置

简单理解：

> 节点表示设备，属性表示这个设备的硬件资源和配置参数。

---

## 8. 属性值的常见类型

DTS 中常见属性值类型包括字符串、字符串列表、数字 cell、phandle 引用和空属性。

### 8.1 字符串

```dts
status = "okay";
```

### 8.2 字符串列表

```dts
compatible = "phytium,dwmac", "snps,dwmac-3.70a";
```

`compatible` 经常使用字符串列表，前面的字符串更具体，后面的字符串更通用。

### 8.3 数字 cell

```dts
reg = <0x0 0x28000000 0x0 0x1000>;
```

尖括号 `< >` 中的每一个值通常是一个 32-bit cell。

### 8.4 phandle 引用

```dts
phy-handle = <&phy0>;
clocks = <&clk0 3>;
resets = <&rst0 1>;
```

`&phy0`、`&clk0`、`&rst0` 都是对其他节点 label 的引用。

### 8.5 空属性

```dts
dma-coherent;
```

这种属性没有显式赋值，只要存在就表示某个布尔含义。

---

## 9. compatible 属性的作用

`compatible` 是设备树中最重要的属性之一。

它用于告诉 Linux：

> 这个设备可以匹配哪些驱动。

例如：

```dts
ethernet@2820c000 {
	compatible = "phytium,dwmac", "snps,dwmac";
	reg = <0x0 0x2820c000 0x0 0x2000>;
	interrupts = <0 45 4>;
	status = "okay";
};
```

驱动中可能有类似代码：

```c
static const struct of_device_id dwmac_of_match[] = {
    { .compatible = "phytium,dwmac" },
    { .compatible = "snps,dwmac" },
    { }
};
```

当设备树中的字符串和驱动中的 `of_device_id` 匹配时，内核就会把该设备交给这个驱动处理，并调用驱动的 `probe()` 函数。

---

## 10. compatible 字符串列表

`compatible` 可以有多个字符串，例如：

```dts
compatible = "vendor,specific-device", "vendor,generic-device";
```

一般规则是：

```text
从左到右：由具体到通用
```

例如：

```dts
compatible = "phytium,dwmac", "snps,dwmac";
```

可以理解为：

- `"phytium,dwmac"`：厂商或平台相关的具体匹配
- `"snps,dwmac"`：Synopsys DWMAC 类设备的通用匹配

这样做的好处是：

- 如果内核有专门适配该平台的驱动，可以优先匹配具体字符串
- 如果没有专用适配，也可能通过通用驱动工作
- 同一类 IP 可以复用通用驱动

---

## 11. compatible 与驱动 probe 的关系

设备树和驱动匹配的大致过程如下：

```text
Linux 解析 DTB
  |
  v
发现 status = "okay" 的设备节点
  |
  v
创建 platform_device 或其他 bus device
  |
  v
驱动注册 platform_driver
  |
  v
比较 DTS compatible 和驱动 of_match_table
  |
  v
匹配成功后调用 probe()
```

以 platform driver 为例：

```c
static const struct of_device_id foo_of_match[] = {
    { .compatible = "vendor,foo" },
    { }
};

static struct platform_driver foo_driver = {
    .probe = foo_probe,
    .remove = foo_remove,
    .driver = {
        .name = "foo",
        .of_match_table = foo_of_match,
    },
};
```

对应 DTS：

```dts
foo@10000000 {
	compatible = "vendor,foo";
	reg = <0x0 0x10000000 0x0 0x1000>;
	status = "okay";
};
```

只要两边的 `compatible` 一致，就具备匹配基础。

但是需要注意：

> compatible 匹配成功不代表 probe 一定成功。probe 过程中还可能因为 reg、中断、时钟、复位、GPIO、PHY 等资源错误而失败。

---

## 12. compatible 常见问题

### 12.1 status 已经 okay，但是驱动没有 probe

常见原因：

1. `compatible` 字符串写错
2. 驱动中的 `of_match_table` 没有对应字符串
3. 驱动没有编译进内核
4. 驱动是模块，但模块没有加载
5. 父节点是 `disabled`
6. bus 类型不对，内核没有创建对应设备
7. 设备节点路径或结构不符合 binding 要求

排查方法：

```bash
dmesg | grep -i compatible
dmesg | grep -i probe
ls /sys/bus/platform/devices/
ls /sys/bus/platform/drivers/
```

也可以查看运行时设备树：

```bash
dtc -I fs -O dts -o running.dts /proc/device-tree
```

确认运行中的 `compatible` 是否和源码一致。

---

## 13. reg 属性的作用

`reg` 属性用于描述设备占用的地址资源。

对于 MMIO 设备，`reg` 通常表示：

```text
寄存器基地址 + 寄存器区域大小
```

例如：

```dts
serial@28000000 {
	compatible = "arm,pl011";
	reg = <0x0 0x28000000 0x0 0x1000>;
};
```

表示：

```text
寄存器起始地址：0x0000000028000000
寄存器区域大小：0x0000000000001000
```

驱动中通常通过 platform resource 获取这个资源：

```c
res = platform_get_resource(pdev, IORESOURCE_MEM, 0);
base = devm_ioremap_resource(dev, res);
```

所以 `reg` 写错，驱动即使 probe 了，也可能无法正确访问硬件寄存器。

---

## 14. reg 需要结合父节点解释

`reg` 的格式不是固定的，它取决于父节点的两个属性：

```dts
#address-cells
#size-cells
```

例如父节点中有：

```dts
soc {
	#address-cells = <2>;
	#size-cells = <2>;

	serial@28000000 {
		reg = <0x0 0x28000000 0x0 0x1000>;
	};
};
```

表示：

- 地址使用 2 个 cell
- 大小使用 2 个 cell
- 每个 cell 是 32 bit

所以：

```dts
reg = <0x0 0x28000000 0x0 0x1000>;
```

应解释为：

```text
address = <0x0 0x28000000> = 0x0000000028000000
size    = <0x0 0x1000>     = 0x0000000000001000
```

如果父节点是：

```dts
#address-cells = <1>;
#size-cells = <1>;
```

那么 `reg` 可能写成：

```dts
reg = <0x28000000 0x1000>;
```

解释为：

```text
address = 0x28000000
size    = 0x1000
```

所以阅读 `reg` 时，第一步永远是：

> 先看父节点的 `#address-cells` 和 `#size-cells`。

---

## 15. reg 可以有多个地址区域

有些设备不止一个寄存器区域，可以在 `reg` 中写多个地址范围。

例如：

```dts
device@10000000 {
	reg = <0x0 0x10000000 0x0 0x1000>,
		  <0x0 0x10010000 0x0 0x1000>;
	reg-names = "ctrl", "config";
};
```

这里有两个寄存器区域：

| 名称       | 起始地址         | 大小       |
|----------|--------------|----------|
| `ctrl`   | `0x10000000` | `0x1000` |
| `config` | `0x10010000` | `0x1000` |

`reg-names` 用于给多个 `reg` 区域命名。

驱动中可以按名称获取资源：

```c
res = platform_get_resource_byname(pdev, IORESOURCE_MEM, "ctrl");
```

这比只按序号获取更清晰。

---

## 16. reg 和 ranges 的关系

如果设备位于某个总线节点下面，`reg` 中的地址可能是子总线地址，不一定直接等于 CPU 物理地址。

这时需要看父节点的 `ranges`。

例如：

```dts
bus@0 {
	#address-cells = <1>;
	#size-cells = <1>;
	ranges = <0x0 0x0 0x10000000>;

	device@1000 {
		reg = <0x1000 0x100>;
	};
};
```

这里 `device@1000` 的 `reg` 是子总线地址：

```text
0x1000
```

经过 `ranges` 映射后，才得到父总线地址。

简单理解：

> `reg` 描述设备在当前父总线地址空间中的位置，`ranges` 描述子总线地址如何转换到父总线地址。

在 SoC 内部外设中，很多时候 `ranges` 是空属性或者直接映射，因此看起来 `reg` 就像 CPU 物理地址。

但在 PCIe、外部总线、复杂片上总线中，`ranges` 非常重要。

---

## 17. reg 常见问题

### 17.1 为什么节点名是 serial@28000000，但 reg 不是两个数？

因为 `reg` 的长度由父节点决定。

例如：

```dts
#address-cells = <2>;
#size-cells = <2>;
```

则一个地址范围需要 4 个 cell：

```dts
reg = <0x0 0x28000000 0x0 0x1000>;
```

而不是：

```dts
reg = <0x28000000 0x1000>;
```

### 17.2 unit-address 和 reg 不一致会怎样？

例如：

```dts
serial@28000000 {
	reg = <0x0 0x29000000 0x0 0x1000>;
};
```

这种写法容易引起混乱，dtc 也可能给出 warning。

建议：

> `@unit-address` 应该和 `reg` 的起始地址保持一致。

### 17.3 reg 写错会导致什么？

常见后果包括：

- 驱动 probe 失败
- `ioremap` 失败
- 能 probe 但访问寄存器异常
- 设备无响应
- 内核卡死或触发 synchronous external abort
- 访问到了其他设备的寄存器区域

所以移植驱动时，`reg` 是最需要重点核对的属性之一。

---

## 18. interrupts 属性的作用

`interrupts` 属性用于描述设备使用的中断资源。

例如：

```dts
serial@28000000 {
	compatible = "arm,pl011";
	reg = <0x0 0x28000000 0x0 0x1000>;
	interrupts = <0 32 4>;
};
```

这表示该设备有一个中断，具体解释方式由中断控制器决定。

对于 ARM GIC，常见格式是：

```text
<中断类型 中断号 触发方式>
```

例如：

```dts
interrupts = <0 32 4>;
```

可以理解为：

| cell | 含义                 |
|------|--------------------|
| `0`  | 中断类型，通常表示 SPI      |
| `32` | 中断号                |
| `4`  | 触发方式，例如 level high |

但是具体含义一定要以对应 interrupt-controller binding 为准。

---

## 19. interrupt-parent

`interrupts` 的解释依赖中断控制器。

设备可以通过 `interrupt-parent` 指定自己的中断父节点：

```dts
interrupt-parent = <&gic>;
```

例如：

```dts
uart0: serial@28000000 {
	compatible = "arm,pl011";
	reg = <0x0 0x28000000 0x0 0x1000>;
	interrupt-parent = <&gic>;
	interrupts = <0 32 4>;
};
```

如果某个节点没有显式写 `interrupt-parent`，它可能继承父节点的 `interrupt-parent`。

所以阅读中断时，需要确认：

- 当前节点有没有 `interrupt-parent`
- 父节点有没有 `interrupt-parent`
- 最终对应的是哪个 interrupt-controller
- 该 interrupt-controller 的 `#interrupt-cells` 是多少

---

## 20. #interrupt-cells

中断控制器节点通常会定义：

```dts
#interrupt-cells = <3>;
```

这表示一个中断描述符需要 3 个 cell。

例如 GIC 中常见：

```text
gic: interrupt-controller@... {
	compatible = "arm,gic-v3";
	interrupt-controller;
	#interrupt-cells = <3>;
};
```

于是设备节点中可以写：

```dts
interrupts = <0 32 4>;
```

如果某个中断控制器的 `#interrupt-cells = <2>`，那么它的 `interrupts` 格式就会不同。

所以阅读 `interrupts` 时，不能只看当前节点，要看：

```text
interrupt-parent 指向哪个中断控制器
该中断控制器的 #interrupt-cells 是多少
对应 binding 规定每个 cell 的含义是什么
```

---

## 21. interrupts 可以有多个中断

有些设备有多个中断源，例如：

```dts
device@10000000 {
	interrupts = <0 40 4>,
				 <0 41 4>;
	interrupt-names = "rx", "tx";
};
```

这里有两个中断：

| 名称   | 中断描述       |
|------|------------|
| `rx` | `<0 40 4>` |
| `tx` | `<0 41 4>` |

`interrupt-names` 用于给多个中断命名。

驱动中可以通过名称获取中断号：

```c
irq = platform_get_irq_byname(pdev, "rx");
```

这比按序号获取更清晰，也更不容易出错。

---

## 22. interrupts-extended

有些设备会使用 `interrupts-extended`，它可以同时指定中断控制器和中断参数。

例如：

```dts
interrupts-extended = <&gic 0 32 4>;
```

它的含义是：

```text
中断控制器：&gic
中断参数：0 32 4
```

相比普通的：

```dts
interrupt-parent = <&gic>;
interrupts = <0 32 4>;
```

`interrupts-extended` 把中断父节点和中断参数放在了一起。

简单理解：

> `interrupts` 依赖 `interrupt-parent`，而 `interrupts-extended` 自己包含中断控制器引用。

---

## 23. interrupts 常见问题

### 23.1 interrupts 写错会导致什么？

常见问题包括：

- 驱动申请 IRQ 失败
- 设备能初始化但没有中断响应
- 网卡收不到包或发包异常
- 串口收不到输入
- 中断风暴
- 系统卡死
- dmesg 中出现 IRQ 相关错误

### 23.2 中断号是不是 Linux 里看到的 IRQ 号？

不一定。

DTS 中的中断号是硬件中断描述的一部分，Linux 启动后可能会映射成另一个虚拟 IRQ 号。

所以不能简单认为：

```text
DTS interrupts 中写的 32 == Linux /proc/interrupts 中显示的 IRQ 32
```

更准确的理解是：

> DTS 描述硬件中断输入，Linux irqdomain 会把它映射成内核内部使用的 IRQ 编号。

### 23.3 怎么查看运行中的中断？

常用命令：

```bash
cat /proc/interrupts
dmesg | grep -i irq
dmesg | grep -i interrupt
```

如果是具体设备，例如网卡：

```bash
cat /proc/interrupts | grep -i eth
dmesg | grep -i eth
dmesg | grep -i stmmac
```

---

## 24. status 属性补充

虽然本文重点是 `compatible`、`reg`、`interrupts`，但实际调试时 `status` 也必须一起看。

```dts
status = "okay";
```

表示设备启用。

```dts
status = "disabled";
```

表示设备禁用。

很多 SoC `.dtsi` 中会先定义外设，但默认关闭：

```dts
uart0: serial@28000000 {
	compatible = "arm,pl011";
	reg = <0x0 0x28000000 0x0 0x1000>;
	interrupts = <0 32 4>;
	status = "disabled";
};
```

板级 `.dts` 中再启用：

```dts
&uart0 {
	status = "okay";
};
```

调试时要注意：

> 子节点 status 是 okay 还不够，父节点如果 disabled，也可能导致设备无法正常创建。

---

## 25. 一个完整节点的阅读示例

示例节点：

```dts
uart0: serial@28000000 {
	compatible = "arm,pl011", "arm,primecell";
	reg = <0x0 0x28000000 0x0 0x1000>;
	interrupts = <0 32 4>;
	clocks = <&clk0 5>;
	clock-names = "apb_pclk";
	status = "okay";
};
```

阅读顺序建议如下：

### 25.1 看节点身份

```text
uart0: serial@28000000
```

说明：

- label 是 `uart0`
- 节点类型是 `serial`
- unit-address 是 `28000000`

### 25.2 看驱动匹配

```dts
compatible = "arm,pl011", "arm,primecell";
```

说明这是 ARM PL011 串口设备，可匹配 PL011 相关驱动。

### 25.3 看寄存器资源

```dts
reg = <0x0 0x28000000 0x0 0x1000>;
```

如果父节点是：

```dts
#address-cells = <2>;
#size-cells = <2>;
```

则表示：

```text
寄存器基地址：0x0000000028000000
寄存器大小：0x0000000000001000
```

### 25.4 看中断资源

```dts
interrupts = <0 32 4>;
```

需要结合 `interrupt-parent` 和中断控制器 binding 解释。

如果是 GIC，通常可以理解为 SPI 类型中断，中断号 32，触发方式为 level high。

### 25.5 看时钟资源

```dts
clocks = <&clk0 5>;
clock-names = "apb_pclk";
```

说明该设备需要引用 `clk0` 时钟控制器中的某个时钟。

### 25.6 看是否启用

```dts
status = "okay";
```

说明该设备启用，内核会尝试创建设备并匹配驱动。

---

## 26. 节点属性调试顺序

当一个设备无法工作时，可以按下面顺序排查：

```text
确认实际运行的 DTB
  |
  v
确认节点是否存在
  |
  v
确认 status 是否为 okay
  |
  v
确认 compatible 是否能匹配驱动
  |
  v
确认 reg 是否正确
  |
  v
确认 interrupts 是否正确
  |
  v
确认 clocks / resets / gpios / pinctrl / phy-handle 等依赖资源
  |
  v
查看 dmesg 中 probe 失败原因
```

常用命令：

```bash
dtc -I fs -O dts -o running.dts /proc/device-tree
```

```bash
grep -n "serial@28000000" -n running.dts
grep -n "compatible" running.dts
grep -n "interrupts" running.dts
```

查看 platform device：

```bash
ls /sys/bus/platform/devices/
```

查看驱动：

```bash
ls /sys/bus/platform/drivers/
```

查看日志：

```bash
dmesg | grep -i probe
dmesg | grep -i irq
dmesg | grep -i resource
```

---

## 27. 初学者容易混淆的点

### 27.1 compatible 不是驱动文件名

`compatible` 是匹配字符串，不一定等于驱动源码文件名，也不一定等于模块名。

真正匹配的是驱动中的：

```c
of_match_table
```

### 27.2 reg 不是普通变量

`reg` 描述硬件地址资源，需要结合父节点的 `#address-cells` 和 `#size-cells` 解释。

### 27.3 interrupts 中的数字不能脱离中断控制器解释

不同 interrupt-controller 的 `interrupts` 格式可能不同。

同样是：

```dts
interrupts = <1 2 3>;
```

在不同中断控制器下面含义可能完全不同。

### 27.4 unit-address 不是内核访问硬件的直接依据

内核真正使用寄存器地址时，主要看 `reg`。

`@unit-address` 更多是设备树节点命名规范的一部分。

### 27.5 DTS 源码不一定等于 Linux 实际看到的设备树

U-Boot 可能会修改：

- `/chosen/bootargs`
- `memory`
- `status`
- MAC 地址
- initrd 信息
- reserved-memory

所以调试时要看运行时设备树，而不是只看源码。

---

## 28. 小结

设备树节点和属性是阅读 DTS 的基本单位。

可以用一句话理解：

> 节点描述设备，属性描述设备资源，`compatible` 用于匹配驱动，`reg` 描述地址资源，`interrupts` 描述中断资源。

本文最重要的几个结论是：

1. 读节点时先看 `node-name@unit-address`
2. `label` 用于源码中的节点引用
3. `compatible` 决定设备能否匹配驱动
4. `reg` 必须结合父节点的 `#address-cells` 和 `#size-cells` 阅读
5. `interrupts` 必须结合 `interrupt-parent`、`#interrupt-cells` 和 binding 阅读
6. `status = "okay"` 只是设备启用条件之一，不代表驱动一定成功 probe
7. 调试时应优先导出 `/proc/device-tree`，确认 Linux 实际使用的设备树

掌握这些内容后，就可以进一步学习具体外设节点，例如 UART、GPIO、I2C、SPI、Ethernet、PCIe 等设备树写法。
