# 07-platform-driver最小实验

## 1. 文档目标

本文用于带领实习生完成一个最小 `platform driver` 实验，理解嵌入式 Linux 驱动开发中最常见的一条主线：

```text
设备树节点
  ↓
内核创建 platform_device
  ↓
platform_driver 通过 compatible 匹配设备
  ↓
probe() 被调用
  ↓
驱动完成初始化
```

完成本文后，应该能够回答下面几个问题：

1. 什么是 `platform device`；
2. 什么是 `platform driver`；
3. 设备树中的 `compatible` 如何和驱动匹配；
4. `probe()` 为什么会被调用；
5. 如何通过 `dmesg` 和 `sysfs` 判断驱动是否匹配成功。

本文不涉及真实寄存器访问、中断和 DMA，只做最小匹配实验。寄存器访问会在后续 `07-ioremap-readl-writel基础.md` 中单独整理。

---

## 2. 为什么要学习platform driver

在嵌入式 Linux 中，很多外设不是通过 PCI、USB 这种可自动枚举的总线发现的，而是固定焊接在 SoC 或板卡上的。

例如：

1. UART；
2. GPIO 控制器；
3. I2C 控制器；
4. SPI 控制器；
5. 看门狗；
6. 定时器；
7. 自定义 MMIO 外设。

这些设备通常由设备树描述，例如：

```dts
mydev@28000000 {
	compatible = "training,my-platform-dev";
	reg = <0x0 0x28000000 0x0 0x1000>;
	status = "okay";
};
```

Linux 启动时会解析设备树，为这些节点创建对应的 `platform_device`。驱动代码中注册 `platform_driver`，并通过 `compatible` 字符串和设备树节点匹配。匹配成功后，内核调用驱动的 `probe()` 函数。

所以，`platform driver` 是学习嵌入式 Linux 驱动开发的关键入口。

---

## 3. platform device和platform driver的关系

可以简单理解为：

```text
platform_device：描述一个设备
platform_driver：驱动这个设备的代码
```

二者通过匹配规则绑定在一起。

在设备树系统中，最常见的匹配依据是 `compatible`。

```text
DTS 节点中的 compatible
        ↓
驱动中的 of_device_id 表
        ↓
匹配成功
        ↓
调用 probe()
```

示意图：

```text
设备树节点
mydev@28000000 {
	compatible = "training,my-platform-dev";
	status = "okay";
};

              ↓

platform_device
由内核根据设备树自动创建

              ↓

platform_driver
of_match_table 中也有 "training,my-platform-dev"

              ↓

probe() 被调用
```

---

## 4. 实验目标

本实验要实现一个最小 `platform driver`，要求：

1. 驱动可以编译成 `.ko` 模块；
2. 加载模块后，如果设备树中存在匹配节点，`probe()` 会被调用；
3. 卸载模块时，`remove()` 会被调用；
4. 可以通过 `dmesg` 看到加载、匹配和卸载日志；
5. 可以通过 `/sys/bus/platform/devices/` 查看设备；
6. 可以通过 `/sys/bus/platform/drivers/` 查看驱动。

---

## 5. 实验目录结构

建议建立如下目录：

```text
platform-demo/
├── Makefile
└── my_platform_demo.c
```

如果是在开发板上直接编译，确保开发板已经安装当前内核对应的 headers 或 kernel-devel。

如果是在交叉编译环境中编译，需要正确指定内核源码路径和交叉编译工具链。

---

## 6. 驱动源码

创建文件：

```bash
vim my_platform_demo.c
```

内容如下：

```c
#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/of.h>

static int my_platform_demo_probe(struct platform_device *pdev)
{
	struct device *dev = &pdev->dev;

	dev_info(dev, "my platform demo probe called\n");

	return 0;
}

static int my_platform_demo_remove(struct platform_device *pdev)
{
	struct device *dev = &pdev->dev;

	dev_info(dev, "my platform demo remove called\n");

	return 0;
}

static const struct of_device_id my_platform_demo_of_match[] = {
	{ .compatible = "training,my-platform-dev" },
	{ }
};

MODULE_DEVICE_TABLE(of, my_platform_demo_of_match);

static struct platform_driver my_platform_demo_driver = {
	.probe = my_platform_demo_probe,
	.remove = my_platform_demo_remove,
	.driver = {
		.name = "my_platform_demo",
		.of_match_table = my_platform_demo_of_match,
	},
};

module_platform_driver(my_platform_demo_driver);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("training");
MODULE_DESCRIPTION("Minimal platform driver demo");
```

这段代码的核心是：

1. `my_platform_demo_of_match[]` 描述驱动能匹配哪些设备树节点；
2. `.compatible = "training,my-platform-dev"` 必须和 DTS 中的 `compatible` 对应；
3. `my_platform_demo_probe()` 是匹配成功后的入口；
4. `my_platform_demo_remove()` 是驱动解绑或模块卸载时的出口；
5. `module_platform_driver()` 用于注册和注销 `platform_driver`。

---

## 7. Makefile

创建文件：

```bash
vim Makefile
```

内容如下：

```makefile
obj-m += my_platform_demo.o

KDIR ?= /lib/modules/$(shell uname -r)/build
PWD  := $(shell pwd)

all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
```

说明：

1. `obj-m += my_platform_demo.o` 表示编译为外部内核模块；
2. `KDIR` 指向当前运行内核的构建目录；
3. `M=$(PWD)` 表示当前目录是外部模块目录；
4. `make clean` 用于清理编译产物。

---

## 8. 添加设备树节点

要让 `probe()` 被调用，系统中必须存在能匹配的 `platform_device`。

对于使用设备树的 ARM64 开发板，可以在对应 DTS 中添加一个测试节点。

示例：

```dts
my_platform_demo@28000000 {
	compatible = "training,my-platform-dev";
	reg = <0x0 0x28000000 0x0 0x1000>;
	status = "okay";
};
```

这里先说明几个字段：

| 字段 | 作用 |
|---|---|
| `my_platform_demo@28000000` | 节点名称，`@` 后面通常写设备基地址 |
| `compatible` | 用于和驱动匹配 |
| `reg` | 描述设备寄存器地址范围 |
| `status` | `"okay"` 表示启用该节点 |

本实验暂时不读取 `reg`，但保留 `reg` 是为了让这个节点更接近真实设备节点。

注意：`reg` 地址不要随便使用真实硬件已经占用的地址。本文只是演示节点结构，实际项目中应根据芯片手册和板级资源填写。

---

## 9. 编译和部署设备树

修改 DTS 后，需要重新编译 DTB，并让 U-Boot 或系统启动时加载新的 DTB。

常见编译命令示例：

```bash
make ARCH=arm64 dtbs
```

或者在完整内核编译流程中一起生成：

```bash
make ARCH=arm64 Image dtbs modules
```

部署时，通常需要把新的 `.dtb` 拷贝到目标系统的 `/boot` 或 U-Boot 实际加载的位置。

例如：

```bash
cp arch/arm64/boot/dts/xxx/board.dtb /boot/dtb/board.dtb
sync
```

实际路径需要根据项目启动脚本和 U-Boot 环境变量确认。

可以在 U-Boot 中关注：

```text
fdt_addr_r
fdtfile
bootcmd
bootargs
```

也可以在 Linux 启动后检查运行时设备树是否存在该节点。

---

## 10. 编译模块

在 `platform-demo` 目录下执行：

```bash
make
```

成功后应该生成：

```text
my_platform_demo.ko
```

查看文件：

```bash
ls -lh
```

查看模块信息：

```bash
modinfo my_platform_demo.ko
```

关注：

```text
license:        GPL
description:    Minimal platform driver demo
author:         training
alias:          of:N*T*Ctraining,my-platform-dev
```

如果能看到 `alias` 中包含 `training,my-platform-dev`，说明 `MODULE_DEVICE_TABLE()` 生效。

---

## 11. 加载模块

执行：

```bash
sudo insmod my_platform_demo.ko
```

查看日志：

```bash
dmesg | tail -n 30
```

如果设备树节点和驱动匹配成功，应该看到类似日志：

```text
my_platform_demo 28000000.my_platform_demo: my platform demo probe called
```

如果没有看到 `probe called`，说明驱动可能加载了，但没有匹配到设备。

---

## 12. 查看platform设备和驱动

查看 platform 设备：

```bash
ls /sys/bus/platform/devices/
```

可以尝试搜索：

```bash
find /sys/bus/platform/devices/ -name '*my*'
```

查看 platform 驱动：

```bash
ls /sys/bus/platform/drivers/
```

搜索驱动：

```bash
find /sys/bus/platform/drivers/ -name '*my*'
```

如果驱动已经注册，通常可以看到：

```text
/sys/bus/platform/drivers/my_platform_demo
```

查看驱动绑定情况：

```bash
ls -l /sys/bus/platform/drivers/my_platform_demo/
```

如果匹配成功，驱动目录下可能会出现指向设备的符号链接。

---

## 13. 卸载模块

执行：

```bash
sudo rmmod my_platform_demo
```

查看日志：

```bash
dmesg | tail -n 30
```

如果设备已经和驱动绑定，卸载时应该看到：

```text
my platform demo remove called
```

如果之前没有进入 `probe()`，那么卸载时一般也不会进入 `remove()`。

---

## 14. 实验现象总结

正常情况下，完整实验现象应该是：

```text
1. make 成功生成 my_platform_demo.ko
2. modinfo 能看到 of alias
3. insmod 后模块加载成功
4. 如果设备树节点存在且 compatible 匹配，probe 被调用
5. dmesg 中出现 probe called
6. /sys/bus/platform/drivers/ 下出现 my_platform_demo
7. rmmod 时 remove 被调用
8. dmesg 中出现 remove called
```

如果只看到模块加载成功，但是没有看到 `probe called`，说明重点应该排查设备树和匹配关系。

---

## 15. 常见问题排查

## 15.1 insmod成功但probe没有执行

这是最常见的问题。

排查顺序：

```text
1. DTS 中有没有添加节点？
2. 节点 status 是否为 "okay"？
3. compatible 字符串是否完全一致？
4. 系统启动时是否加载了新的 DTB？
5. /proc/device-tree/ 中是否能看到该节点？
6. /sys/bus/platform/devices/ 中是否有对应设备？
7. 驱动中的 of_match_table 是否正确？
8. 是否写了 MODULE_DEVICE_TABLE(of, ...)？
```

检查运行时设备树：

```bash
find /proc/device-tree/ -name '*my*'
```

查看 compatible：

```bash
cat /proc/device-tree/路径/compatible
```

注意：`/proc/device-tree` 中的字符串可能没有换行，显示不一定美观。

可以使用：

```bash
strings /proc/device-tree/路径/compatible
```

---

## 15.2 compatible写错

例如 DTS 中写的是：

```dts
compatible = "training,my-platform-device";
```

但驱动中写的是：

```c
{ .compatible = "training,my-platform-dev" },
```

这两个字符串不完全一致，所以不会匹配。

`compatible` 必须逐字符匹配。

---

## 15.3 status没有设置为okay

如果节点写成：

```dts
status = "disabled";
```

或者节点默认被禁用，内核不会为它创建可用设备。

应该改为：

```dts
status = "okay";
```

---

## 15.4 修改了DTS但实际启动的不是新DTB

这是项目中非常常见的问题。

现象是：

1. 代码和 DTS 看起来都对；
2. 重新编译也成功；
3. 但 `probe()` 一直不进；
4. `/proc/device-tree/` 中看不到新节点。

这通常说明系统启动时没有加载你刚刚编译的 DTB。

应该检查：

```bash
ls -l /boot
ls -l /boot/dtb
```

也要检查 U-Boot 的启动变量：

```text
printenv
```

重点看实际加载的 DTB 文件路径。

---

## 15.5 模块版本不匹配

如果加载模块时出现类似错误：

```text
Invalid module format
```

可能是模块和当前运行内核版本不匹配。

检查当前内核：

```bash
uname -r
```

检查模块 vermagic：

```bash
modinfo my_platform_demo.ko | grep vermagic
```

二者必须匹配或兼容。

---

## 15.6 Makefile路径不对

如果编译时报错：

```text
/lib/modules/xxx/build: No such file or directory
```

说明当前系统没有安装对应内核的构建目录。

需要确认：

```bash
ls /lib/modules/$(uname -r)/build
```

如果没有该目录，需要安装对应的 kernel-devel，或者指定 `KDIR` 为内核源码构建目录。

例如：

```bash
make KDIR=/path/to/kernel/build
```

---

## 16. 最小platform driver的代码阅读顺序

阅读这类驱动时，不要从第一行细抠，而应该按下面顺序看：

```text
1. module_platform_driver()
2. platform_driver 结构体
3. driver.name
4. of_match_table
5. compatible 字符串
6. probe()
7. remove()
```

对应代码位置：

```c
module_platform_driver(my_platform_demo_driver);
```

先找到驱动注册入口。

```c
static struct platform_driver my_platform_demo_driver = {
	.probe = my_platform_demo_probe,
	.remove = my_platform_demo_remove,
	.driver = {
		.name = "my_platform_demo",
		.of_match_table = my_platform_demo_of_match,
	},
};
```

再看驱动结构体。

```c
static const struct of_device_id my_platform_demo_of_match[] = {
	{ .compatible = "training,my-platform-dev" },
	{ }
};
```

最后看匹配表和 `probe()`。

---

## 17. 本实验和真实驱动的关系

本文实验只是最小骨架。

真实 platform driver 通常还会在 `probe()` 中做这些事情：

```text
1. 分配私有数据结构
2. 读取设备树属性
3. 获取 reg 资源
4. ioremap 寄存器
5. 获取 irq
6. 申请中断
7. 获取 clock
8. 获取 reset
9. 获取 pinctrl
10. 初始化硬件
11. 注册字符设备、网络设备、input设备或其他子系统接口
```

例如真实代码中常见：

```c
priv = devm_kzalloc(dev, sizeof(*priv), GFP_KERNEL);
platform_set_drvdata(pdev, priv);

base = devm_platform_ioremap_resource(pdev, 0);
irq = platform_get_irq(pdev, 0);
```

这些内容会在后续文档中逐步展开。

本篇只要求实习生先理解一件事：

> 设备树中的设备节点如何触发 platform driver 的 probe。

---

## 18. 实习生检查清单

完成实验后，实习生应该提交下面信息：

```text
1. 驱动源码 my_platform_demo.c
2. Makefile
3. 添加的 DTS 节点
4. make 编译日志
5. insmod 命令和结果
6. dmesg 中 probe called 的截图或文本
7. /sys/bus/platform/devices/ 下对应设备信息
8. /sys/bus/platform/drivers/ 下对应驱动信息
9. rmmod 后 remove called 的日志
10. 遇到的问题和解决过程
```

如果没有进入 `probe()`，也要提交：

```text
1. 当前 DTS 节点内容
2. 当前运行时 /proc/device-tree 检查结果
3. compatible 字符串对比
4. 当前加载的 DTB 路径判断
5. dmesg 中相关日志
```

不要只说“驱动没跑起来”，必须说明：

```text
模块有没有加载？
设备有没有创建？
驱动有没有注册？
compatible 是否匹配？
probe 有没有进入？
```

---

## 19. 小结

`platform driver` 是嵌入式 Linux 驱动开发的基础模型。

本篇实验要建立的核心理解是：

```text
设备树描述硬件
  ↓
内核根据设备树创建 platform_device
  ↓
驱动注册 platform_driver
  ↓
compatible 匹配成功
  ↓
probe() 被调用
```

对于初学者来说，能把这个最小实验跑通非常重要。因为后续学习 MMIO、中断、GPIO、I2C、SPI、DMA 等内容，基本都会建立在这个模型之上。

先让 `probe()` 进来，再谈寄存器、中断和数据通路。
