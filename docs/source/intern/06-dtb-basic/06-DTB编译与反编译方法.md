# 06-DTB编译与反编译方法

## 1. 文档目标

本文用于整理 DTB 的编译、反编译和运行时设备树导出方法，重点说明：

1. `.dts`、`.dtsi`、`.dtb` 的关系
2. 如何使用 `dtc` 手动编译 DTB
3. 如何使用 `dtc` 反编译 DTB
4. 如何在 Linux 内核源码中编译 DTB
5. 如何从 `/proc/device-tree` 导出运行时设备树
6. 修改 DTS 后没有生效时如何排查

DTB 编译和反编译是设备树调试中的基础技能。

---

## 2. DTS、DTSI、DTB 的关系

设备树相关文件常见有三类：

| 文件类型 | 全称 | 作用 |
|---|---|---|
| `.dts` | Device Tree Source | 板级设备树源码 |
| `.dtsi` | Device Tree Source Include | 公共设备树片段 |
| `.dtb` | Device Tree Blob | 编译后的二进制设备树 |

它们之间的关系可以理解为：

```text
.dtsi 公共片段
    +
.dts 板级文件
    |
    | dtc 编译
    v
.dtb 二进制设备树
    |
    | Bootloader 加载
    v
Linux Kernel 解析
```

Linux 启动时通常不会直接读取 `.dts`，而是读取编译后的 `.dtb`。

---

## 3. 什么是 dtc

`dtc` 是 Device Tree Compiler，即设备树编译器。

它可以完成两类常见操作：

```text
DTS -> DTB
DTB -> DTS
```

也可以从运行时文件系统形式的设备树导出 DTS：

```text
/proc/device-tree -> DTS
```

常见命令格式：

```bash
dtc -I <input-format> -O <output-format> -o <output-file> <input-file>
```

其中：

| 参数 | 含义 |
|---|---|
| `-I` | 指定输入格式 |
| `-O` | 指定输出格式 |
| `-o` | 指定输出文件 |

常见格式：

| 格式 | 含义 |
|---|---|
| `dts` | 设备树源码 |
| `dtb` | 设备树二进制 |
| `fs` | 文件系统形式的设备树，例如 `/proc/device-tree` |

---

## 4. 安装 dtc

在 openEuler / Fedora / CentOS 类系统上，可以尝试：

```bash
sudo dnf install dtc
```

在 Ubuntu / Debian 类系统上，可以尝试：

```bash
sudo apt install device-tree-compiler
```

确认是否安装成功：

```bash
dtc -v
```

可能输出类似：

```text
Version: DTC 1.6.1
```

不同发行版版本可能不同，只要能正常编译和反编译即可。

---

## 5. 手动编译 DTS 为 DTB

最基本命令：

```bash
dtc -I dts -O dtb -o board.dtb board.dts
```

含义：

| 参数 | 作用 |
|---|---|
| `-I dts` | 输入是 DTS 源码 |
| `-O dtb` | 输出是 DTB 二进制 |
| `-o board.dtb` | 输出文件名 |
| `board.dts` | 输入文件名 |

示例：

```bash
dtc -I dts -O dtb -o pd2008-devboard.dtb pd2008-devboard.dts
```

编译完成后会生成：

```text
pd2008-devboard.dtb
```

---

## 6. 带 include 路径编译

实际 DTS 经常会包含 `.dtsi` 文件，例如：

```dts
#include "soc.dtsi"
#include "board-common.dtsi"
```

如果 `.dtsi` 不在当前目录，可能需要指定 include 路径。

`dtc` 可以使用 `-i` 指定 include 搜索路径：

```bash
dtc -I dts -O dtb -i ./include -o board.dtb board.dts
```

如果有多个 include 路径，可以写多个 `-i`：

```bash
dtc -I dts -O dtb \
    -i ./include \
    -i ./arch/arm64/boot/dts/vendor \
    -o board.dtb board.dts
```

不过在 Linux 内核源码树中，通常不建议手动处理复杂 include，而是使用内核构建系统编译 DTB。

---

## 7. 使用 cpp 预处理的 DTS

Linux 内核中的 DTS 通常使用 C 预处理器处理，例如：

```dts
#include <dt-bindings/interrupt-controller/arm-gic.h>
#include <dt-bindings/gpio/gpio.h>
```

这类 DTS 里可能出现宏：

```dts
interrupts = <GIC_SPI 45 IRQ_TYPE_LEVEL_HIGH>;
reset-gpios = <&gpio0 5 GPIO_ACTIVE_LOW>;
```

这些宏需要先经过预处理。

因此直接用 `dtc board.dts` 可能报错，例如：

```text
syntax error
```

这是因为 `dtc` 不认识 `GIC_SPI`、`IRQ_TYPE_LEVEL_HIGH`、`GPIO_ACTIVE_LOW` 这类宏。

内核构建系统会自动完成预处理和编译，所以更推荐使用：

```bash
make ARCH=arm64 dtbs
```

---

## 8. 在 Linux 内核源码中编译所有 DTB

ARM64 设备树通常位于：

```text
arch/arm64/boot/dts/
```

编译所有 DTB：

```bash
make ARCH=arm64 dtbs
```

如果是交叉编译，还需要指定交叉编译器：

```bash
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- dtbs
```

或者你的工具链前缀是：

```bash
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnueabi- dtbs
```

编译完成后，DTB 通常位于：

```text
arch/arm64/boot/dts/<vendor>/*.dtb
```

例如：

```text
arch/arm64/boot/dts/phytium/pd2008-devboard-dsk.dtb
```

---

## 9. 在 Linux 内核源码中编译单个 DTB

如果只想编译一个 DTB，可以指定目标文件。

例如：

```bash
make ARCH=arm64 phytium/pd2008-devboard-dsk.dtb
```

或者使用交叉编译：

```bash
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnueabi- \
    phytium/pd2008-devboard-dsk.dtb
```

编译结果一般在：

```text
arch/arm64/boot/dts/phytium/pd2008-devboard-dsk.dtb
```

这个方法比每次编译所有 DTB 更快，适合设备树调试。

---

## 10. 使用 O= 指定输出目录

如果内核使用独立输出目录构建，例如：

```bash
make ARCH=arm64 O=build defconfig
make ARCH=arm64 O=build Image dtbs
```

那么单独编译 DTB 时也要带上 `O=build`：

```bash
make ARCH=arm64 O=build phytium/pd2008-devboard-dsk.dtb
```

编译结果通常在：

```text
build/arch/arm64/boot/dts/phytium/pd2008-devboard-dsk.dtb
```

不要误以为结果还在源码目录：

```text
arch/arm64/boot/dts/phytium/
```

使用 `O=` 后，构建产物会进入输出目录。

---

## 11. 反编译 DTB 为 DTS

将 DTB 反编译为 DTS：

```bash
dtc -I dtb -O dts -o board.dump.dts board.dtb
```

示例：

```bash
dtc -I dtb -O dts \
    -o pd2008-devboard-dsk.dump.dts \
    pd2008-devboard-dsk.dtb
```

反编译后的文件可以用文本编辑器查看：

```bash
less pd2008-devboard-dsk.dump.dts
```

反编译常用于：

1. 确认 DTB 中是否真的包含某个节点
2. 确认某个 `status` 是否被编译进去
3. 确认 `compatible`、`reg`、`interrupts` 是否符合预期
4. 对比两个 DTB 的差异
5. 检查 bootloader 使用的 DTB 是否正确

---

## 12. 反编译结果和原始 DTS 为什么不一样

反编译出来的 DTS 通常和原始 DTS 不完全一样。

常见差异包括：

1. `#include` 已经展开
2. 宏已经被替换成数字
3. label 可能丢失
4. 注释会丢失
5. 节点顺序可能有变化
6. 某些 phandle 会变成数字
7. 格式和缩进可能改变

例如原始 DTS 中可能写：

```dts
interrupts = <GIC_SPI 45 IRQ_TYPE_LEVEL_HIGH>;
```

反编译后可能变成：

```dts
interrupts = <0x00 0x2d 0x04>;
```

原始 DTS 中可能写：

```dts
reset-gpios = <&gpio0 5 GPIO_ACTIVE_LOW>;
```

反编译后可能变成：

```dts
reset-gpios = <0x12 0x05 0x01>;
```

这是正常现象。

反编译 DTS 适合用于确认实际内容，不适合作为长期维护的源码文件。

---

## 13. 保留符号信息的 DTB

如果希望反编译时保留更多符号信息，可以在编译时使用 `-@`：

```bash
dtc -@ -I dts -O dtb -o board.dtb board.dts
```

`-@` 会生成符号相关信息，常用于 overlay 场景。

在某些情况下，反编译后能看到类似：

```dts
__symbols__ {
    uart0 = "/soc/serial@28000000";
};
```

这有助于调试 phandle 和 overlay。

不过普通板级 DTB 调试中，不一定必须使用 `-@`。

---

## 14. 导出运行时设备树

Linux 启动后，可以通过 `/proc/device-tree` 查看内核当前使用的设备树。

更常用的方式是导出成 DTS：

```bash
dtc -I fs -O dts -o running.dts /proc/device-tree
```

这条命令非常重要。

它导出的不是源码中的 DTS，而是：

```text
Linux 当前实际使用的设备树
```

这可以用来检查：

1. U-Boot 实际传给 Linux 的 DTB 是哪个
2. U-Boot 是否修改了 `chosen`
3. U-Boot 是否修改了 `bootargs`
4. U-Boot 是否修改了 `memory`
5. 自己修改的节点是否真的进入运行系统
6. `status` 是否真的变成了 `okay`
7. `compatible`、`reg`、`interrupts` 是否和预期一致

---

## 15. 查看 /proc/device-tree

也可以直接查看 `/proc/device-tree`：

```bash
ls /proc/device-tree
```

查看根节点 compatible：

```bash
cat /proc/device-tree/compatible
```

由于设备树字符串通常用 `\0` 分隔，显示可能不美观，可以用：

```bash
tr '\0' '\n' < /proc/device-tree/compatible
```

查看 bootargs：

```bash
cat /proc/device-tree/chosen/bootargs
```

查看某个节点的 status：

```bash
tr '\0' '\n' < /proc/device-tree/soc/serial@28000000/status
```

如果路径中节点名称不同，需要以实际 `/proc/device-tree` 中的路径为准。

---

## 16. 对比源码 DTS 和运行时 DTS

设备树调试时，建议经常做对比：

```text
源码 DTS
  |
  | 编译
  v
生成 DTB
  |
  | bootloader 加载
  v
running.dts
```

可以分别反编译和导出：

```bash
dtc -I dtb -O dts -o built.dts board.dtb
dtc -I fs -O dts -o running.dts /proc/device-tree
```

然后对比：

```bash
diff -u built.dts running.dts | less
```

重点关注：

```text
chosen
bootargs
memory
目标设备节点
status
compatible
reg
interrupts
clocks
resets
gpios
```

如果 `built.dts` 是正确的，但 `running.dts` 不正确，通常说明 bootloader 没有加载你编译出来的新 DTB，或者启动过程中被修改了。

---

## 17. 修改 DTS 后的完整流程

修改 DTS 后，一般流程是：

```text
修改 .dts / .dtsi
  |
  v
重新编译 .dtb
  |
  v
复制 .dtb 到启动分区或 bootloader 指定位置
  |
  v
确认 U-Boot / UEFI 加载的是新 .dtb
  |
  v
重启 Linux
  |
  v
导出 running.dts
  |
  v
确认修改是否生效
```

示例命令：

```bash
make ARCH=arm64 O=build phytium/pd2008-devboard-dsk.dtb
```

复制到目标系统启动目录：

```bash
sudo cp build/arch/arm64/boot/dts/phytium/pd2008-devboard-dsk.dtb \
    /boot/dtb/pd2008-devboard-dsk.dtb
```

重启后导出：

```bash
dtc -I fs -O dts -o running.dts /proc/device-tree
```

确认修改：

```bash
grep -n "serial@28000000" -A20 running.dts
```

---

## 18. U-Boot 中加载 DTB 的常见方式

在 U-Boot 中，DTB 通常会加载到某个内存地址，例如：

```bash
load nvme 0:1 ${fdt_addr_r} /boot/dtb/pd2008-devboard-dsk.dtb
```

然后启动内核：

```bash
booti ${kernel_addr_r} - ${fdt_addr_r}
```

其中：

| 变量 | 含义 |
|---|---|
| `kernel_addr_r` | 内核 Image 加载地址 |
| `fdt_addr_r` | DTB 加载地址 |
| `-` | 表示不使用 initrd |

完整流程可能是：

```bash
load nvme 0:1 ${kernel_addr_r} /boot/Image
load nvme 0:1 ${fdt_addr_r} /boot/dtb/pd2008-devboard-dsk.dtb
booti ${kernel_addr_r} - ${fdt_addr_r}
```

如果你修改了 DTB，但 U-Boot 加载的是另一个路径，Linux 就不会看到你的修改。

---

## 19. U-Boot 可能修改 DTB

即使 DTB 文件本身正确，U-Boot 也可能在启动前修改设备树。

常见修改包括：

1. 修改 `/chosen/bootargs`
2. 添加 initrd 信息
3. 修改 memory 节点
4. 添加 MAC 地址
5. 添加 reserved-memory
6. 根据启动参数修改某些节点

例如 U-Boot 中可能执行：

```bash
setenv bootargs "console=ttyAMA1,115200 root=/dev/nvme0n1p2 rw rootwait"
```

然后启动时把 bootargs 写入设备树的 `/chosen` 节点。

所以实际 Linux 看到的设备树可能是：

```text
DTB 文件内容 + U-Boot 动态修改
```

这也是为什么 `running.dts` 很重要。

---

## 20. 常见 warning 如何看待

反编译或编译 DTB 时，`dtc` 可能输出 warning。

例如：

```text
Warning (unit_address_vs_reg): /soc/xxx@1000: node has a unit name, but no reg property
```

这类 warning 表示：

```text
节点名带 @地址，但节点没有 reg 属性
```

常见 warning 类型包括：

| warning | 大致含义 |
|---|---|
| `unit_address_vs_reg` | 节点名和 `reg` 使用不规范 |
| `simple_bus_reg` | simple-bus 下的 reg/ranges 描述可能不规范 |
| `avoid_default_addr_size` | 没有显式写 `#address-cells` 或 `#size-cells` |
| `unique_unit_address` | 同级节点 unit-address 重复 |
| `graph_child_address` | graph/port 节点地址描述可能不规范 |

有些 warning 不一定导致系统不能启动，但长期维护时应尽量修正。

如果是驱动不工作的问题，重点关注：

```text
目标节点是否存在
status 是否 okay
compatible 是否正确
reg 是否正确
interrupts 是否正确
依赖资源是否正确
```

不要被大量无关 warning 完全带偏。

---

## 21. dtc 常用命令汇总

### 21.1 DTS 编译为 DTB

```bash
dtc -I dts -O dtb -o board.dtb board.dts
```

### 21.2 DTB 反编译为 DTS

```bash
dtc -I dtb -O dts -o board.dump.dts board.dtb
```

### 21.3 导出运行时设备树

```bash
dtc -I fs -O dts -o running.dts /proc/device-tree
```

### 21.4 编译内核源码中的所有 DTB

```bash
make ARCH=arm64 dtbs
```

### 21.5 编译内核源码中的单个 DTB

```bash
make ARCH=arm64 phytium/pd2008-devboard-dsk.dtb
```

### 21.6 使用独立输出目录编译单个 DTB

```bash
make ARCH=arm64 O=build phytium/pd2008-devboard-dsk.dtb
```

### 21.7 反编译并保留符号信息

```bash
dtc -@ -I dtb -O dts -o board.dump.dts board.dtb
```

---

## 22. 实际排查案例思路

假设你修改了：

```dts
&uart1 {
    status = "okay";
};
```

但 Linux 启动后没有看到对应串口。

建议按下面流程排查：

### 22.1 确认编译是否成功

```bash
make ARCH=arm64 O=build phytium/pd2008-devboard-dsk.dtb
```

确认新 DTB 时间戳：

```bash
ls -lh build/arch/arm64/boot/dts/phytium/pd2008-devboard-dsk.dtb
```

### 22.2 反编译编译产物

```bash
dtc -I dtb -O dts \
    -o built.dts \
    build/arch/arm64/boot/dts/phytium/pd2008-devboard-dsk.dtb
```

检查：

```bash
grep -n "serial@28001000" -A20 built.dts
```

确认里面有：

```dts
status = "okay";
```

### 22.3 确认复制到启动位置

```bash
sudo cp build/arch/arm64/boot/dts/phytium/pd2008-devboard-dsk.dtb \
    /boot/dtb/pd2008-devboard-dsk.dtb
```

### 22.4 重启后导出 running.dts

```bash
dtc -I fs -O dts -o running.dts /proc/device-tree
```

检查：

```bash
grep -n "serial@28001000" -A20 running.dts
```

如果 `built.dts` 中是 `okay`，但 `running.dts` 中不是，说明启动时加载的 DTB 不是你复制的这个，或者被 bootloader 修改了。

---

## 23. 常见问题

### 23.1 修改 DTS 后为什么没有生效

常见原因：

1. 没有重新编译 DTB
2. 编译了错误的 DTB 目标
3. 使用 `O=build` 后复制错了路径
4. 新 DTB 没有复制到启动分区
5. U-Boot 加载了另一个 DTB 文件
6. U-Boot 环境变量中写死了旧路径
7. Linux 实际通过 ACPI 启动，而不是 DTB
8. 修改的是 `.dtsi`，但目标 `.dts` 没有包含它
9. 后面的 DTS 片段又覆盖了你的修改

---

### 23.2 反编译出来为什么没有 label

正常。

例如源码中：

```dts
uart0: serial@28000000 {
    status = "okay";
};
```

反编译后可能变成：

```dts
serial@28000000 {
    status = "okay";
};
```

`uart0:` 这种 label 主要是源码层面方便引用，编译后不一定保留。

---

### 23.3 为什么宏都变成数字了

因为 DTS 编译时经过了预处理。

例如：

```dts
GPIO_ACTIVE_LOW
IRQ_TYPE_LEVEL_HIGH
GIC_SPI
```

反编译后可能变成：

```text
0x1
0x4
0x0
```

这是正常现象。

阅读反编译 DTS 时，要结合对应头文件或 binding 文档理解这些数字含义。

---

### 23.4 可以直接修改反编译出来的 DTS 再编译吗

可以临时调试，但不建议长期这样维护。

原因是：

1. 注释丢失
2. include 结构丢失
3. label 可能丢失
4. 宏变成数字
5. 可读性变差
6. 后续难以和源码仓库维护

推荐做法是：

```text
反编译 DTS 用于观察和对比
真正修改仍然回到原始 .dts / .dtsi 源码
```

---

## 24. 小结

DTB 编译和反编译是设备树调试的基础能力。

核心流程是：

```text
.dts / .dtsi
    |
    | dtc 或内核构建系统
    v
.dtb
    |
    | bootloader 加载并传给 Linux
    v
Linux 解析设备树
```

最常用的三个命令是：

```bash
dtc -I dts -O dtb -o board.dtb board.dts
dtc -I dtb -O dts -o board.dump.dts board.dtb
dtc -I fs -O dts -o running.dts /proc/device-tree
```

实际工程中，最可靠的排查思路是：

```text
不要只看源码 DTS
也不要只看编译出来的 DTB
一定要看 running.dts
```

可以用一句话总结：

> DTS 是源码，DTB 是启动时使用的二进制，running.dts 是 Linux 实际看到的设备树；调试设备树问题时，最终应以 running.dts 为准。
