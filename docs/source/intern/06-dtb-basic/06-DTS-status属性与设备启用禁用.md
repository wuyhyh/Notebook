# 06-DTS-status属性与设备启用禁用

## 1. 文档目标

本文用于整理 DTS 设备树中的 `status` 属性，重点说明：

1. `status` 属性的作用
2. `okay` 和 `disabled` 的区别
3. SoC `.dtsi` 和板级 `.dts` 中常见的启用方式
4. `status` 如何影响设备创建和驱动 probe
5. 修改 `status` 后没有效果时应该如何排查

`status` 是设备树中最常见的属性之一，语法很简单，但在实际调试中非常关键。

---

## 2. status 属性是什么

`status` 属性用于描述一个设备节点当前是否可用。

常见写法：

```dts
status = "okay";
```

表示该设备节点启用。

```dts
status = "disabled";
```

表示该设备节点禁用。

简单理解：

```text
status = "okay"      表示这个设备可以被 Linux 使用
status = "disabled"  表示这个设备暂时不要被 Linux 使用
```

在驱动调试中，如果一个设备节点是 `disabled`，Linux 通常不会为它创建对应的设备对象，驱动也就不会进入 `probe()`。

---

## 3. 为什么需要 status 属性

一颗 SoC 内部通常集成了很多外设，例如：

- UART
- I2C
- SPI
- GPIO
- Ethernet MAC
- PCIe 控制器
- USB 控制器
- SD/MMC 控制器

这些外设在 SoC 层面是存在的，所以通常会在 SoC 公共 `.dtsi` 文件中统一描述。

但是不同开发板并不一定都会使用这些外设。例如：

- 有些 UART 没有引出
- 有些 I2C 总线没有挂设备
- 有些 SPI 控制器没有连接 Flash
- 有些 Ethernet MAC 没有接 PHY
- 有些 PCIe 控制器没有接插槽或者设备

因此 SoC `.dtsi` 中通常先把外设节点写出来，但默认设置为禁用：

```dts
uart1: serial@28001000 {
    compatible = "arm,pl011";
    reg = <0x0 0x28001000 0x0 0x1000>;
    interrupts = <0 33 4>;
    status = "disabled";
};
```

然后由具体板级 `.dts` 根据硬件连接情况决定是否启用。

---

## 4. 常见的启用方式

板级 `.dts` 中可以通过标签引用已有节点，然后修改它的 `status`：

```dts
&uart1 {
    status = "okay";
};
```

这表示：

```text
引用前面已经定义好的 uart1 节点
然后把它的 status 属性改成 okay
```

常见模式是：

```dts
/* SoC .dtsi 中 */
uart1: serial@28001000 {
    compatible = "arm,pl011";
    reg = <0x0 0x28001000 0x0 0x1000>;
    interrupts = <0 33 4>;
    status = "disabled";
};

/* Board .dts 中 */
&uart1 {
    status = "okay";
};
```

这样做的好处是：

1. SoC 公共外设只需要描述一次
2. 不同开发板可以复用同一份 `.dtsi`
3. 每块板只需要启用自己实际使用的外设
4. 避免 Linux 初始化不存在或未连接的硬件

---

## 5. status 的常见取值

最常用的两个取值是：

| 取值 | 含义 |
|---|---|
| `"okay"` | 设备可用 |
| `"disabled"` | 设备不可用 |

除此之外，设备树规范中还可以见到一些其他取值：

| 取值 | 大致含义 |
|---|---|
| `"reserved"` | 设备存在，但保留不用 |
| `"fail"` | 设备不可用，存在故障 |
| `"fail-xxx"` | 设备不可用，并附带平台相关故障信息 |

在 Linux 驱动适配中，最常见、最重要的仍然是：

```dts
status = "okay";
status = "disabled";
```

初学阶段先掌握这两个即可。

---

## 6. 没写 status 时是什么含义

一个容易忽略的点是：

> 如果节点没有写 `status` 属性，Linux 通常会把它当作可用节点处理。

也就是说，下面这个节点通常也会被认为是可用的：

```dts
uart0: serial@28000000 {
    compatible = "arm,pl011";
    reg = <0x0 0x28000000 0x0 0x1000>;
    interrupts = <0 32 4>;
};
```

它大致等价于：

```dts
uart0: serial@28000000 {
    compatible = "arm,pl011";
    reg = <0x0 0x28000000 0x0 0x1000>;
    interrupts = <0 32 4>;
    status = "okay";
};
```

不过为了文档清晰和维护方便，板级 DTS 中通常建议显式写出 `status`。

---

## 7. status 如何影响设备创建

Linux 启动时会解析 DTB，并根据设备树节点创建对应的设备对象。

对于很多 SoC 内部外设，常见流程是：

```text
Linux 解析 DTB
  |
  v
检查节点 status
  |
  v
status 可用
  |
  v
创建 platform_device / amba_device 等设备对象
  |
  v
驱动和设备通过 compatible 匹配
  |
  v
调用 probe()
```

如果节点是：

```dts
status = "disabled";
```

通常流程会变成：

```text
Linux 解析 DTB
  |
  v
发现节点 status = "disabled"
  |
  v
跳过该节点
  |
  v
不创建对应设备对象
  |
  v
驱动不会 probe
```

所以调试驱动不 probe 时，`status` 是第一批需要确认的属性之一。

---

## 8. status 和 compatible 的关系

`status` 和 `compatible` 解决的是两个不同问题。

| 属性 | 作用 |
|---|---|
| `status` | 控制设备节点是否启用 |
| `compatible` | 控制设备节点匹配哪个驱动 |

一个设备想要正常 probe，通常需要同时满足：

1. 节点是启用状态
2. `compatible` 能匹配到驱动
3. 驱动已经编译进内核或模块已经加载
4. 节点资源描述基本正确

例如：

```dts
eth0: ethernet@2820c000 {
    compatible = "phytium,dwmac";
    reg = <0x0 0x2820c000 0x0 0x2000>;
    interrupts = <0 45 4>;
    status = "okay";
};
```

其中：

```text
status = "okay"             决定这个设备是否参与初始化
compatible = "phytium,dwmac" 决定它应该匹配哪个驱动
```

如果写成：

```dts
status = "disabled";
```

即使 `compatible` 写对了，驱动通常也不会 probe。

如果写成：

```dts
status = "okay";
compatible = "vendor,wrong-device";
```

节点虽然启用了，但因为 `compatible` 匹配不到驱动，probe 也不会发生。

---

## 9. status 和父节点的关系

阅读 `status` 时不能只看当前节点，还要注意父节点是否启用。

例如：

```dts
soc {
    status = "disabled";

    uart0: serial@28000000 {
        compatible = "arm,pl011";
        reg = <0x0 0x28000000 0x0 0x1000>;
        status = "okay";
    };
};
```

虽然 `uart0` 自己写了：

```dts
status = "okay";
```

但是它的父节点 `soc` 是：

```dts
status = "disabled";
```

这种情况下，子节点是否会被正常创建要看内核遍历和总线逻辑，实际调试时必须同时检查父节点。

一般建议：

> 当前节点和关键父节点都应该是可用状态。

特别是以下父节点需要关注：

- `soc`
- `simple-bus`
- `mdio`
- `i2c`
- `spi`
- `pcie`
- `usb`
- `gpio-controller`

例如 I2C 设备：

```dts
&i2c0 {
    status = "disabled";

    eeprom@50 {
        compatible = "atmel,24c02";
        reg = <0x50>;
        status = "okay";
    };
};
```

如果 `i2c0` 控制器没有启用，那么下面的 `eeprom@50` 通常也不会正常工作。

---

## 10. status 和 pinctrl、clock、reset 的关系

`status = "okay"` 只是表示设备可以启用，并不代表设备一定能正常工作。

设备 probe 还可能依赖：

- `pinctrl`
- `clocks`
- `resets`
- `power-domains`
- `phys`
- `phy-handle`
- `dmas`
- `iommus`

例如：

```dts
&uart1 {
    pinctrl-names = "default";
    pinctrl-0 = <&uart1_pins>;
    clocks = <&clk 12>;
    status = "okay";
};
```

这里 `status = "okay"` 只是第一步。

如果 `pinctrl-0` 引用错误，或者 `clocks` 缺失，驱动仍然可能 probe 失败。

所以要区分：

```text
status = "okay" 只是允许内核尝试初始化
资源描述正确      才能保证驱动初始化成功
```

---

## 11. 常见示例：启用 UART

SoC `.dtsi` 中：

```dts
uart2: serial@28002000 {
    compatible = "arm,pl011";
    reg = <0x0 0x28002000 0x0 0x1000>;
    interrupts = <0 34 4>;
    clocks = <&clk 10>;
    status = "disabled";
};
```

板级 `.dts` 中：

```dts
&uart2 {
    pinctrl-names = "default";
    pinctrl-0 = <&uart2_pins>;
    status = "okay";
};
```

这表示该开发板实际使用 `uart2`，所以在板级文件中启用它。

调试时可以检查：

```bash
dmesg | grep -i uart
dmesg | grep -i tty
ls /sys/bus/platform/devices/
```

也可以查看运行时设备树：

```bash
tr '\0' '\n' < /proc/device-tree/soc/serial@28002000/status
```

---

## 12. 常见示例：启用 Ethernet MAC

SoC `.dtsi` 中：

```dts
eth0: ethernet@2820c000 {
    compatible = "phytium,dwmac";
    reg = <0x0 0x2820c000 0x0 0x2000>;
    interrupts = <0 45 4>;
    status = "disabled";
};
```

板级 `.dts` 中：

```dts
&eth0 {
    phy-mode = "rgmii";
    phy-handle = <&phy0>;
    status = "okay";
};
```

这里不仅要启用 MAC，还要确保 PHY 节点也正确：

```dts
&mdio0 {
    status = "okay";

    phy0: ethernet-phy@1 {
        reg = <1>;
    };
};
```

否则可能出现：

```text
MAC 节点启用了
驱动也 probe 了
但是 PHY attach 失败
网口仍然不可用
```

所以网卡类问题不要只看 MAC 的 `status`，还要看：

- MDIO 控制器是否启用
- PHY 节点是否存在
- `phy-handle` 是否指向正确节点
- `phy-mode` 是否正确
- PHY 驱动是否支持该 PHY 芯片

---

## 13. 常见示例：启用 I2C 设备

I2C 控制器节点：

```dts
&i2c0 {
    status = "okay";

    eeprom@50 {
        compatible = "atmel,24c02";
        reg = <0x50>;
    };
};
```

这里的含义是：

```text
i2c0 控制器启用
eeprom@50 是挂在 i2c0 总线上的设备
```

如果只写子设备：

```dts
&i2c0 {
    status = "disabled";

    eeprom@50 {
        compatible = "atmel,24c02";
        reg = <0x50>;
        status = "okay";
    };
};
```

由于 `i2c0` 控制器禁用了，子设备通常也无法被正常枚举。

---

## 14. 修改 status 后为什么没有效果

这是设备树调试中非常常见的问题。

常见原因包括：

1. 修改了 `.dts`，但没有重新编译 `.dtb`
2. 编译了 `.dtb`，但没有复制到启动分区
3. U-Boot 实际加载的不是这个 `.dtb`
4. U-Boot 启动脚本中写死了另一个 DTB 文件名
5. U-Boot 启动前动态修改了设备树
6. 修改的是 `.dtsi`，但目标 `.dts` 没有包含它
7. 板级 `.dts` 后面又覆盖了一次 `status`
8. 父节点仍然是 `disabled`
9. 驱动没有编译或没有加载
10. `compatible` 匹配失败
11. probe 失败被误认为没有 probe

排查时不要只看源码中的 DTS，而要看 Linux 实际使用的运行时设备树。

---

## 15. 查看运行时 status

Linux 启动后，可以查看 `/proc/device-tree`。

例如查看某个 UART：

```bash
cat /proc/device-tree/soc/serial@28002000/status
```

如果没有换行，可以用：

```bash
tr '\0' '\n' < /proc/device-tree/soc/serial@28002000/status
```

也可以把当前运行时设备树导出成 DTS：

```bash
dtc -I fs -O dts -o running.dts /proc/device-tree
```

然后搜索：

```bash
grep -n "serial@28002000" -A20 running.dts
```

这样看到的是：

> Linux 当前实际使用的设备树，而不是源码中你以为正在使用的设备树。

---

## 16. 通过 sysfs 判断设备是否创建

如果节点启用并被内核创建为 platform device，通常可以在：

```bash
ls /sys/bus/platform/devices/
```

中看到类似设备。

例如：

```bash
ls /sys/bus/platform/devices/ | grep 28002000
```

如果节点没有出现在 platform devices 中，可能说明：

- `status` 仍然是 disabled
- 父节点没有被遍历
- 节点位置不符合该 bus 的创建逻辑
- DTB 不是你修改后的版本

如果设备出现了，但驱动没有绑定，可以继续看：

```bash
ls /sys/bus/platform/drivers/
```

以及：

```bash
dmesg | grep -i probe
dmesg | grep -i 28002000
```

---

## 17. status 调试顺序

遇到设备没有起来，可以按下面顺序排查：

```text
确认当前内核使用的是 Device Tree 启动
  |
  v
确认实际加载的 DTB 是自己修改后的 DTB
  |
  v
导出 /proc/device-tree 为 running.dts
  |
  v
检查目标节点 status 是否为 okay
  |
  v
检查父节点 status 是否为 okay
  |
  v
检查 compatible 是否能匹配驱动
  |
  v
检查驱动是否编译进内核或模块是否加载
  |
  v
检查 dmesg 中是否有 probe 失败信息
  |
  v
检查 clocks / resets / pinctrl / phy / gpio 等依赖资源
```

这比只盯着 DTS 源码更可靠。

---

## 18. status 常见误区

### 18.1 误区一：status = okay 就一定能工作

不一定。

`status = "okay"` 只表示这个设备可以被内核尝试初始化。

设备是否真正可用，还取决于：

- 寄存器地址是否正确
- 中断是否正确
- 时钟是否正确
- 复位是否正确
- pinctrl 是否正确
- 驱动是否支持
- 硬件连接是否正确

---

### 18.2 误区二：驱动没有 probe 一定是 compatible 错了

不一定。

如果节点是 `disabled`，驱动也不会 probe。

所以要同时检查：

```text
status
compatible
驱动编译状态
运行时 DTB
dmesg
```

---

### 18.3 误区三：只看 .dts 源码就够了

不够。

实际 Linux 使用的是 bootloader 传入的 DTB。

中间可能发生：

- 没有重新编译
- 没有复制新 DTB
- U-Boot 加载了旧 DTB
- U-Boot 修改了 bootargs 或节点
- 多个启动分区使用不同 DTB

所以调试时应优先确认运行时设备树：

```bash
dtc -I fs -O dts -o running.dts /proc/device-tree
```

---

### 18.4 误区四：子节点 okay 就够了

不一定。

例如 I2C、SPI、MDIO 等总线设备，父控制器没启用，子设备通常也无法正常工作。

需要同时检查：

```text
总线控制器 status
子设备 status
子设备 reg 地址
驱动匹配情况
```

---

## 19. 一个完整阅读示例

假设有如下节点：

```dts
&eth0 {
    compatible = "phytium,dwmac";
    reg = <0x0 0x2820c000 0x0 0x2000>;
    interrupts = <0 45 4>;
    phy-mode = "rgmii";
    phy-handle = <&phy0>;
    status = "okay";
};
```

阅读顺序可以是：

1. `&eth0`：这是引用前面定义过的 `eth0` 节点
2. `compatible`：该设备尝试匹配 `phytium,dwmac` 对应驱动
3. `reg`：MAC 控制器寄存器地址范围
4. `interrupts`：MAC 使用的中断资源
5. `phy-mode`：MAC 和 PHY 之间的接口模式
6. `phy-handle`：引用具体 PHY 节点
7. `status = "okay"`：该 MAC 节点在当前板级 DTS 中启用

如果网口不工作，不能只看 `status`，还要继续检查：

```text
eth0 是否真的出现在 running.dts 中
mdio 节点是否 okay
phy0 节点是否存在
PHY 地址 reg 是否正确
PHY 驱动是否支持
dmesg 中 stmmac / phy 是否报错
```

---

## 20. 小结

`status` 属性用于控制设备树节点是否启用。

最重要的结论是：

```text
status = "okay"      设备节点可用，内核可以尝试创建设备并匹配驱动
status = "disabled" 设备节点禁用，通常不会创建对应设备，驱动不会 probe
```

但在实际调试中还要记住：

1. 没写 `status` 通常等价于可用
2. 子节点启用不代表父节点也启用
3. `status = "okay"` 不代表硬件一定工作
4. 驱动 probe 还依赖 `compatible`、驱动编译状态和其他资源
5. 排查时应以 `/proc/device-tree` 导出的运行时设备树为准
6. 修改 DTS 后必须重新编译并确认 bootloader 加载了新的 DTB

可以用一句话概括：

> `status` 决定设备树节点是否参与初始化，但设备能不能真正工作，还要看 compatible 匹配、资源描述和驱动初始化结果。
