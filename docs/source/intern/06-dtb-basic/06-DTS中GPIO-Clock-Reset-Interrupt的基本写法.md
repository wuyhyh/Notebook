# 06-DTS中GPIO-Clock-Reset-Interrupt的基本写法

## 1. 为什么单独写这篇文档

这篇文档建议单独写，原因不是因为 GPIO、Clock、Reset、Interrupt 每一个都很复杂，而是因为它们在驱动适配中经常一起出现。

前几篇文档主要解决的是：

```text
这个设备节点是否存在？
这个设备节点是否启用？
这个设备节点能不能匹配到驱动？
```

也就是：

```text
节点结构
compatible
reg
interrupts
status
```

而本文要解决的是另一个问题：

```text
驱动 probe 之后，需要从 DTS 中拿哪些硬件资源？
```

很多驱动即使已经匹配成功，也仍然可能因为资源缺失而初始化失败，例如：

- 没有 GPIO，无法控制电源、复位、使能脚
- 没有 Clock，控制器时钟没打开
- 没有 Reset，硬件还处于复位状态
- 没有 Interrupt，设备事件无法通知 CPU
- GPIO / Clock / Reset / Interrupt 的 phandle 写错，驱动拿不到资源

所以这篇文档更偏向 **驱动实际初始化阶段的 DTS 资源写法**。

可以把设备树学习分成两层：

```text
第一层：设备能不能被内核发现
  - compatible
  - reg
  - interrupts
  - status

第二层：设备能不能被驱动正确初始化
  - gpios
  - clocks
  - resets
  - interrupts
  - pinctrl
  - power-domains
  - phys
  - dmas
```

本文先整理最常见的四类资源：

```text
GPIO
Clock
Reset
Interrupt
```

---

## 2. 文档目标

本文用于整理 DTS 中 GPIO、Clock、Reset、Interrupt 的基本写法，帮助理解：

1. DTS 中如何引用 GPIO 控制器
2. DTS 中如何引用 Clock Provider
3. DTS 中如何引用 Reset Controller
4. DTS 中如何描述中断资源
5. 驱动如何从设备树中获取这些资源
6. 阅读这类属性时应该注意哪些基本规则

本文重点不是展开每一种 binding 的所有细节，而是建立基本阅读能力。

---

## 3. 共同特点：都是跨节点引用资源

GPIO、Clock、Reset、Interrupt 有一个共同特点：

> 当前设备节点通常不是自己直接定义这些资源，而是引用别的控制器节点。

例如一个 Ethernet MAC 节点可能写成：

```dts
eth0: ethernet@2820c000 {
    compatible = "phytium,dwmac";
    reg = <0x0 0x2820c000 0x0 0x2000>;
    interrupts = <0 45 4>;
    clocks = <&clk 10>;
    resets = <&rst 3>;
    reset-gpios = <&gpio0 5 GPIO_ACTIVE_LOW>;
    status = "okay";
};
```

这里涉及几类资源：

| 属性 | 引用对象 | 作用 |
|---|---|---|
| `interrupts` | 中断控制器 | 描述设备使用哪个中断 |
| `clocks` | 时钟控制器 | 描述设备需要哪个时钟 |
| `resets` | 复位控制器 | 描述设备使用哪个复位线 |
| `reset-gpios` | GPIO 控制器 | 描述一个用于复位的 GPIO 引脚 |

这些属性往往通过 `phandle` 引用其他节点。

---

## 4. phandle 基础回顾

设备树中经常用 `&label` 引用其他节点。

例如：

```dts
gpio0: gpio@28004000 {
    compatible = "vendor,gpio";
    gpio-controller;
    #gpio-cells = <2>;
};
```

这里的：

```dts
gpio0:
```

是标签。

其他节点可以通过：

```dts
<&gpio0 5 GPIO_ACTIVE_LOW>
```

引用它。

这类引用方式就是 phandle 的典型用法。

简单理解：

```text
&gpio0 表示引用 gpio0 这个控制器节点
后面的参数由 gpio0 自己的 #gpio-cells 决定
```

---

## 5. GPIO 的基本写法

GPIO 常用于描述控制引脚，例如：

- reset 引脚
- enable 引脚
- power 引脚
- interrupt 引脚
- detect 引脚

常见写法：

```dts
reset-gpios = <&gpio0 5 GPIO_ACTIVE_LOW>;
```

含义大致是：

```text
使用 gpio0 控制器
使用第 5 号 GPIO
有效电平为低电平
```

其中：

| 部分 | 含义 |
|---|---|
| `&gpio0` | 引用 GPIO 控制器 |
| `5` | GPIO 控制器内部的引脚编号 |
| `GPIO_ACTIVE_LOW` | 低电平有效 |

如果是高电平有效：

```dts
enable-gpios = <&gpio0 12 GPIO_ACTIVE_HIGH>;
```

含义是：

```text
使用 gpio0 的第 12 号 GPIO
高电平表示 enable 有效
```

---

## 6. GPIO 控制器节点

GPIO 控制器通常会有类似写法：

```dts
gpio0: gpio@28004000 {
    compatible = "vendor,gpio";
    reg = <0x0 0x28004000 0x0 0x1000>;
    gpio-controller;
    #gpio-cells = <2>;
    status = "okay";
};
```

关键属性包括：

| 属性 | 作用 |
|---|---|
| `gpio-controller` | 表示该节点是 GPIO 控制器 |
| `#gpio-cells` | 表示引用该 GPIO 时需要几个参数 |
| `reg` | GPIO 控制器寄存器地址 |
| `status` | GPIO 控制器是否启用 |

例如：

```dts
#gpio-cells = <2>;
```

通常表示引用 GPIO 时需要两个参数：

```text
GPIO 编号
GPIO flags
```

所以：

```dts
<&gpio0 5 GPIO_ACTIVE_LOW>
```

可以拆成：

```text
&gpio0           引用 GPIO 控制器
5                GPIO 编号
GPIO_ACTIVE_LOW  GPIO 标志
```

不过不同 GPIO controller 的 binding 可能不同，具体仍要以对应 binding 文档为准。

---

## 7. GPIO 属性命名习惯

GPIO 属性通常以 `-gpios` 结尾。

常见例子：

```dts
reset-gpios = <&gpio0 5 GPIO_ACTIVE_LOW>;
enable-gpios = <&gpio0 12 GPIO_ACTIVE_HIGH>;
power-gpios = <&gpio1 3 GPIO_ACTIVE_HIGH>;
detect-gpios = <&gpio2 7 GPIO_ACTIVE_LOW>;
```

其中属性名前半部分通常描述用途：

| 属性名 | 可能含义 |
|---|---|
| `reset-gpios` | 复位引脚 |
| `enable-gpios` | 使能引脚 |
| `power-gpios` | 电源控制引脚 |
| `detect-gpios` | 检测引脚 |
| `cd-gpios` | SD 卡插入检测 |
| `wp-gpios` | 写保护检测 |

需要注意：

> DTS 属性名不是随便起的，必须和驱动或 binding 文档约定一致。

例如驱动里如果查找的是：

```c
devm_gpiod_get(dev, "reset", GPIOD_OUT_LOW);
```

那么 DTS 中一般对应：

```dts
reset-gpios = <...>;
```

如果属性名写错，驱动可能就拿不到这个 GPIO。

---

## 8. Clock 的基本写法

Clock 用于描述设备需要的时钟资源。

常见写法：

```dts
clocks = <&clk 10>;
clock-names = "apb";
```

含义大致是：

```text
该设备使用 clk 控制器提供的第 10 号时钟
这个时钟在驱动中叫 apb
```

如果一个设备有多个时钟：

```dts
clocks = <&clk 10>, <&clk 11>;
clock-names = "apb", "core";
```

含义是：

```text
第一个时钟名为 apb
第二个时钟名为 core
```

驱动中可以按名字获取：

```c
clk_apb = devm_clk_get(dev, "apb");
clk_core = devm_clk_get(dev, "core");
```

---

## 9. Clock Provider 节点

Clock provider 是提供时钟的节点，常见写法类似：

```dts
clk: clock-controller@28005000 {
    compatible = "vendor,clock-controller";
    reg = <0x0 0x28005000 0x0 0x1000>;
    #clock-cells = <1>;
};
```

关键属性是：

```dts
#clock-cells = <1>;
```

这表示引用该 clock provider 时，需要 1 个参数。

所以：

```dts
clocks = <&clk 10>;
```

可以拆成：

```text
&clk  引用 clock provider
10    clock id
```

如果某个 clock provider 写成：

```dts
#clock-cells = <0>;
```

那么引用时可能是：

```dts
clocks = <&fixed_clk>;
```

不需要额外参数。

---

## 10. clock-names 的作用

`clock-names` 用于给 `clocks` 中的每个时钟起名字。

例如：

```dts
clocks = <&clk 10>, <&clk 11>, <&clk 12>;
clock-names = "apb", "core", "tx";
```

对应关系是按顺序来的：

| clocks 条目 | clock-names |
|---|---|
| `<&clk 10>` | `"apb"` |
| `<&clk 11>` | `"core"` |
| `<&clk 12>` | `"tx"` |

驱动中可以这样获取：

```c
devm_clk_get(dev, "apb");
devm_clk_get(dev, "core");
devm_clk_get(dev, "tx");
```

如果顺序写错，可能导致驱动拿到错误时钟。

如果名字写错，驱动可能拿不到对应 clock。

---

## 11. Reset 的基本写法

Reset 用于描述设备的复位控制线。

常见写法：

```dts
resets = <&rst 3>;
reset-names = "mac";
```

含义大致是：

```text
该设备使用 rst 控制器的第 3 条复位线
这条复位线在驱动中叫 mac
```

如果有多个 reset：

```dts
resets = <&rst 3>, <&rst 4>;
reset-names = "mac", "phy";
```

对应关系为：

| resets 条目 | reset-names |
|---|---|
| `<&rst 3>` | `"mac"` |
| `<&rst 4>` | `"phy"` |

驱动中可能通过名字获取：

```c
devm_reset_control_get(dev, "mac");
devm_reset_control_get(dev, "phy");
```

---

## 12. Reset Controller 节点

Reset controller 节点通常类似：

```dts
rst: reset-controller@28006000 {
    compatible = "vendor,reset-controller";
    reg = <0x0 0x28006000 0x0 0x1000>;
    #reset-cells = <1>;
};
```

关键属性是：

```dts
#reset-cells = <1>;
```

这表示引用该 reset controller 时，需要 1 个参数。

所以：

```dts
resets = <&rst 3>;
```

可以拆成：

```text
&rst  引用 reset controller
3     reset line id
```

---

## 13. reset-gpios 和 resets 的区别

很多初学者容易混淆：

```dts
reset-gpios = <&gpio0 5 GPIO_ACTIVE_LOW>;
```

和：

```dts
resets = <&rst 3>;
```

它们都和复位有关，但含义不同。

| 写法 | 控制方式 | 说明 |
|---|---|---|
| `reset-gpios` | 通过 GPIO 引脚控制复位 | 常见于外部芯片 |
| `resets` | 通过 SoC reset controller 控制复位线 | 常见于 SoC 内部控制器 |

例如外部 PHY 芯片可能使用 GPIO 复位：

```dts
phy0: ethernet-phy@1 {
    reg = <1>;
    reset-gpios = <&gpio0 5 GPIO_ACTIVE_LOW>;
};
```

而 SoC 内部 MAC 控制器可能使用 reset controller：

```dts
eth0: ethernet@2820c000 {
    resets = <&rst 3>;
    reset-names = "mac";
};
```

简单记忆：

```text
reset-gpios：GPIO 控一个外部复位脚
resets：reset controller 控一个内部复位线
```

---

## 14. Interrupt 的基本写法

Interrupt 用于描述设备中断。

最常见写法：

```dts
interrupts = <0 45 4>;
```

它的具体含义依赖父中断控制器的 binding。

以 ARM GIC 常见写法为例：

```text
<中断类型 中断号 触发方式>
```

例如：

```dts
interrupts = <0 45 4>;
```

可以大致理解为：

```text
0   SPI 类型中断
45  中断号
4   触发方式，例如高电平触发
```

但注意：

> 中断参数的准确含义必须看 interrupt-controller 的 binding，不要脱离平台文档死记。

---

## 15. interrupt-parent

设备节点可以通过 `interrupt-parent` 指定自己的中断控制器。

例如：

```dts
gic: interrupt-controller@29900000 {
    compatible = "arm,gic-v3";
    interrupt-controller;
    #interrupt-cells = <3>;
};

uart0: serial@28000000 {
    compatible = "arm,pl011";
    reg = <0x0 0x28000000 0x0 0x1000>;
    interrupt-parent = <&gic>;
    interrupts = <0 32 4>;
};
```

这里表示：

```text
uart0 的 interrupts 属性由 gic 这个中断控制器解释
```

如果很多设备都使用同一个中断控制器，也可能在上层节点统一指定：

```dts
/ {
    interrupt-parent = <&gic>;

    soc {
        uart0: serial@28000000 {
            interrupts = <0 32 4>;
        };
    };
};
```

这样子节点可以继承父节点的 `interrupt-parent`。

---

## 16. #interrupt-cells

中断控制器节点中通常会有：

```dts
#interrupt-cells = <3>;
```

它表示引用这个 interrupt controller 时，`interrupts` 里每个中断需要几个 cell。

例如：

```dts
#interrupt-cells = <3>;
```

那么：

```dts
interrupts = <0 32 4>;
```

表示一个中断，由 3 个 cell 描述。

如果有两个中断，可能写成：

```dts
interrupts = <0 32 4>, <0 33 4>;
```

这表示两个中断，每个中断 3 个 cell。

---

## 17. interrupts 和 interrupts-extended

普通写法：

```dts
interrupt-parent = <&gic>;
interrupts = <0 32 4>;
```

表示：

```text
中断控制器由 interrupt-parent 指定
interrupts 中只写中断参数
```

另一种写法是 `interrupts-extended`：

```dts
interrupts-extended = <&gic 0 32 4>;
```

它把中断控制器 phandle 和参数写在一起。

如果一个设备有多个中断，而且来自不同的 interrupt controller，`interrupts-extended` 更方便：

```dts
interrupts-extended = <&gic 0 32 4>,
                      <&gpio0 5 1>;
```

简单区别：

| 写法 | 特点 |
|---|---|
| `interrupts` + `interrupt-parent` | 中断控制器单独指定 |
| `interrupts-extended` | 每个中断条目里直接带控制器 phandle |

---

## 18. Interrupt 和 GPIO Interrupt 的关系

有些设备的中断并不是直接连到 GIC，而是先接到 GPIO 控制器。

例如一个外部芯片的中断脚连到 GPIO5：

```dts
touch@38 {
    compatible = "vendor,touch";
    reg = <0x38>;
    interrupt-parent = <&gpio0>;
    interrupts = <5 IRQ_TYPE_EDGE_FALLING>;
};
```

这里的含义是：

```text
touch 芯片的中断脚接到了 gpio0 控制器的第 5 个 GPIO
触发方式是下降沿触发
```

前提是 GPIO 控制器本身也支持 interrupt-controller：

```dts
gpio0: gpio@28004000 {
    compatible = "vendor,gpio";
    gpio-controller;
    #gpio-cells = <2>;

    interrupt-controller;
    #interrupt-cells = <2>;
};
```

注意同一个 GPIO 控制器可能同时是：

```text
GPIO provider
Interrupt provider
```

所以它可能同时有：

```dts
gpio-controller;
#gpio-cells = <2>;

interrupt-controller;
#interrupt-cells = <2>;
```

---

## 19. 综合示例：一个设备节点

假设有一个设备节点：

```dts
foo@10000000 {
    compatible = "vendor,foo";
    reg = <0x0 0x10000000 0x0 0x1000>;

    interrupts = <0 40 4>;

    clocks = <&clk 10>, <&clk 11>;
    clock-names = "apb", "core";

    resets = <&rst 3>;
    reset-names = "foo";

    enable-gpios = <&gpio0 12 GPIO_ACTIVE_HIGH>;
    reset-gpios = <&gpio0 13 GPIO_ACTIVE_LOW>;

    status = "okay";
};
```

可以按以下方式阅读：

| 属性 | 含义 |
|---|---|
| `compatible` | 匹配 `vendor,foo` 对应驱动 |
| `reg` | 设备寄存器地址范围 |
| `interrupts` | 设备使用的中断 |
| `clocks` | 设备需要的时钟 |
| `clock-names` | 时钟名称，驱动按名字获取 |
| `resets` | 设备使用的复位控制线 |
| `reset-names` | 复位线名称 |
| `enable-gpios` | 外部使能 GPIO |
| `reset-gpios` | 外部复位 GPIO |
| `status` | 设备节点启用 |

这个节点能不能工作，不只取决于 `status = "okay"`，还取决于这些资源是否都写对。

---

## 20. 驱动中如何获取这些资源

设备树中的资源最终会被驱动读取。

常见接口包括：

### 20.1 获取 GPIO

```c
struct gpio_desc *reset;

reset = devm_gpiod_get(dev, "reset", GPIOD_OUT_LOW);
```

对应 DTS：

```dts
reset-gpios = <&gpio0 13 GPIO_ACTIVE_LOW>;
```

### 20.2 获取 Clock

```c
struct clk *clk;

clk = devm_clk_get(dev, "core");
```

对应 DTS：

```dts
clocks = <&clk 11>;
clock-names = "core";
```

### 20.3 获取 Reset

```c
struct reset_control *rst;

rst = devm_reset_control_get(dev, "foo");
```

对应 DTS：

```dts
resets = <&rst 3>;
reset-names = "foo";
```

### 20.4 获取 Interrupt

```c
int irq;

irq = platform_get_irq(pdev, 0);
```

对应 DTS：

```dts
interrupts = <0 40 4>;
```

理解这些对应关系后，阅读驱动和 DTS 会容易很多。

---

## 21. 常见错误

### 21.1 属性名写错

例如驱动中获取：

```c
devm_gpiod_get(dev, "reset", ...);
```

DTS 应该写：

```dts
reset-gpios = <...>;
```

如果写成：

```dts
rst-gpios = <...>;
```

驱动可能拿不到。

---

### 21.2 clock-names 顺序错误

例如：

```dts
clocks = <&clk 10>, <&clk 11>;
clock-names = "core", "apb";
```

但驱动认为：

```text
apb 对应第一个 clock
core 对应第二个 clock
```

就可能导致时钟配置错误。

---

### 21.3 #gpio-cells / #clock-cells / #reset-cells 理解错误

例如：

```dts
#gpio-cells = <2>;
```

就意味着引用 GPIO 时通常需要两个参数。

如果只写：

```dts
reset-gpios = <&gpio0 5>;
```

就可能缺少 flags 参数。

---

### 21.4 中断控制器写错

如果 `interrupt-parent` 指错，`interrupts` 的解释就会错。

例如设备中断实际接在 GPIO 控制器上，但 DTS 写成 GIC：

```dts
interrupt-parent = <&gic>;
interrupts = <0 5 4>;
```

这可能完全不是你想表达的含义。

---

### 21.5 控制器本身没有启用

即使设备节点写了：

```dts
clocks = <&clk 10>;
reset-gpios = <&gpio0 5 GPIO_ACTIVE_LOW>;
```

如果 `clk` 或 `gpio0` 对应控制器没有启用，也可能失败。

因此要检查：

```text
当前设备节点 status
GPIO 控制器 status
Clock provider 是否存在
Reset controller 是否存在
Interrupt controller 是否存在
```

---

## 22. 调试建议

### 22.1 查看运行时设备树

```bash
dtc -I fs -O dts -o running.dts /proc/device-tree
```

然后搜索目标节点：

```bash
grep -n "foo@10000000" -A40 running.dts
```

重点检查：

```text
gpios
clocks
clock-names
resets
reset-names
interrupts
interrupt-parent
status
```

---

### 22.2 查看 dmesg

```bash
dmesg | grep -i gpio
dmesg | grep -i clock
dmesg | grep -i reset
dmesg | grep -i irq
dmesg | grep -i interrupt
```

也可以按设备名搜索：

```bash
dmesg | grep -i foo
```

---

### 22.3 查看 sysfs

查看 platform device：

```bash
ls /sys/bus/platform/devices/
```

查看驱动绑定：

```bash
ls /sys/bus/platform/drivers/
```

查看中断计数：

```bash
cat /proc/interrupts
```

如果设备中断正常触发，相关中断计数通常会变化。

---

## 23. 阅读 DTS 资源属性的顺序

建议按下面顺序阅读一个设备节点：

```text
1. compatible
   |
   v
2. reg
   |
   v
3. interrupts / interrupt-parent
   |
   v
4. clocks / clock-names
   |
   v
5. resets / reset-names
   |
   v
6. gpios
   |
   v
7. pinctrl
   |
   v
8. status
```

也可以从驱动角度反过来看：

```text
probe()
  |
  v
platform_get_resource()
platform_get_irq()
devm_clk_get()
devm_reset_control_get()
devm_gpiod_get()
```

然后回到 DTS 中找对应属性。

---

## 24. 小结

GPIO、Clock、Reset、Interrupt 是 DTS 中最常见的硬件资源描述。

它们的共同点是：

```text
设备节点通过 phandle 引用对应的控制器或 provider
引用参数由 provider 节点中的 #xxx-cells 决定
驱动 probe 时通过内核接口读取这些资源
```

最重要的几组关系是：

```text
reset-gpios = <&gpio0 5 GPIO_ACTIVE_LOW>;
        |
        v
gpio0 + #gpio-cells

clocks = <&clk 10>;
clock-names = "core";
        |
        v
clk + #clock-cells

resets = <&rst 3>;
reset-names = "foo";
        |
        v
rst + #reset-cells

interrupt-parent = <&gic>;
interrupts = <0 40 4>;
        |
        v
gic + #interrupt-cells
```

可以用一句话概括：

> `compatible` 让驱动找到设备，`reg` 让驱动找到寄存器，`interrupts` 让驱动接收事件，而 GPIO、Clock、Reset 等资源决定设备能不能被正确拉起和运行。
