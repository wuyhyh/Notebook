# 07-of_match_table与compatible匹配

## 1. 文档目标

本文用于说明 Linux 设备树驱动中非常关键的一组概念：

```text
DTS 里的 compatible
驱动里的 of_match_table
```

对于嵌入式 Linux 驱动开发来说，很多驱动不是靠设备名手动加载的，而是通过设备树中的 `compatible` 字符串和驱动中的 `of_match_table` 自动匹配。

完成本文后，应该能够理解：

1. `compatible` 是什么；
2. `of_match_table` 是什么；
3. 设备树节点如何匹配到驱动；
4. `MODULE_DEVICE_TABLE(of, ...)` 有什么作用；
5. `probe()` 没有执行时，如何排查是否是匹配问题。

---

## 2. compatible是什么

`compatible` 是设备树节点中的一个属性，用来描述这个硬件设备“兼容哪一种驱动”。

例如：

```dts
my_demo@28000000 {
	compatible = "training,my-demo";
	reg = <0x0 0x28000000 0x0 0x1000>;
	status = "okay";
};
```

其中：

```dts
compatible = "training,my-demo";
```

表示这个设备可以由支持 `"training,my-demo"` 的驱动来管理。

可以简单理解为：

```text
compatible 是设备对内核说：
“我是 training,my-demo 这种设备，请找能驱动我的 driver。”
```

---

## 3. of_match_table是什么

`of_match_table` 是驱动代码中的设备树匹配表。

例如：

```c
static const struct of_device_id my_demo_of_match[] = {
	{ .compatible = "training,my-demo" },
	{ }
};
```

它表示：

```text
这个驱动支持 compatible 为 "training,my-demo" 的设备树节点。
```

在 `platform_driver` 中，通常这样引用：

```c
static struct platform_driver my_demo_driver = {
	.probe = my_demo_probe,
	.remove = my_demo_remove,
	.driver = {
		.name = "my_demo",
		.of_match_table = my_demo_of_match,
	},
};
```

这样，内核就知道这个 `platform_driver` 可以匹配哪些设备树节点。

---

## 4. compatible和of_match_table的关系

二者的关系可以表示为：

```text
设备树节点中的 compatible
        ↓
驱动代码中的 of_match_table
        ↓
字符串匹配成功
        ↓
内核调用 probe()
```

例如：

设备树中写：

```dts
compatible = "training,my-demo";
```

驱动中写：

```c
{ .compatible = "training,my-demo" },
```

二者完全一致，匹配成功。

如果设备树中写：

```dts
compatible = "training,my-demo-v2";
```

而驱动中只有：

```c
{ .compatible = "training,my-demo" },
```

那么不会匹配，`probe()` 不会被调用。

---

## 5. 匹配成功后发生了什么

以 `platform driver` 为例，整体流程如下：

```text
Linux 启动
  ↓
解析 DTB
  ↓
发现 status = "okay" 的设备节点
  ↓
为设备节点创建 platform_device
  ↓
驱动注册 platform_driver
  ↓
内核比较 compatible 和 of_match_table
  ↓
匹配成功
  ↓
调用 probe()
```

所以，`compatible` 匹配是 `probe()` 执行的前提之一。

注意：

```text
模块 insmod 成功，不等于 compatible 匹配成功。
compatible 匹配成功后，probe() 才会被调用。
```

---

## 6. 最小DTS示例

下面是一个最小设备树节点示例：

```dts
my_demo@28000000 {
	compatible = "training,my-demo";
	reg = <0x0 0x28000000 0x0 0x1000>;
	status = "okay";
};
```

字段说明：

| 字段 | 说明 |
|---|---|
| `my_demo@28000000` | 节点名，通常由设备类型和基地址组成 |
| `compatible` | 用于匹配驱动 |
| `reg` | 描述寄存器物理地址和长度 |
| `status` | `"okay"` 表示启用该节点 |

对初学者来说，最关键的是：

```text
compatible 必须和驱动里的 of_match_table 对上。
status 必须是 "okay"。
系统实际启动的 DTB 必须包含这个节点。
```

---

## 7. 最小驱动示例

下面是一个最小 `platform driver` 匹配示例：

```c
#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/of.h>

static int my_demo_probe(struct platform_device *pdev)
{
	dev_info(&pdev->dev, "my demo probe called\n");
	return 0;
}

static int my_demo_remove(struct platform_device *pdev)
{
	dev_info(&pdev->dev, "my demo remove called\n");
	return 0;
}

static const struct of_device_id my_demo_of_match[] = {
	{ .compatible = "training,my-demo" },
	{ }
};

MODULE_DEVICE_TABLE(of, my_demo_of_match);

static struct platform_driver my_demo_driver = {
	.probe = my_demo_probe,
	.remove = my_demo_remove,
	.driver = {
		.name = "my_demo",
		.of_match_table = my_demo_of_match,
	},
};

module_platform_driver(my_demo_driver);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("training");
MODULE_DESCRIPTION("of_match_table and compatible demo");
```

这段代码中最关键的是：

```c
static const struct of_device_id my_demo_of_match[] = {
	{ .compatible = "training,my-demo" },
	{ }
};
```

以及：

```c
.of_match_table = my_demo_of_match,
```

没有这两部分，设备树节点通常无法通过 `compatible` 匹配到这个驱动。

---

## 8. of_device_id结构体

`of_match_table` 的元素类型是：

```c
struct of_device_id
```

常见写法：

```c
static const struct of_device_id my_demo_of_match[] = {
	{ .compatible = "training,my-demo" },
	{ }
};
```

最后的：

```c
{ }
```

表示数组结束。这个结束项不能省略。

如果省略，内核在遍历匹配表时可能越界读取，导致不可预期问题。

---

## 9. MODULE_DEVICE_TABLE的作用

常见写法：

```c
MODULE_DEVICE_TABLE(of, my_demo_of_match);
```

它的作用是把匹配表信息导出到模块信息中，让用户空间工具和内核模块自动加载机制可以识别这个模块支持哪些设备。

编译模块后，可以执行：

```bash
modinfo my_demo.ko
```

正常情况下会看到类似：

```text
alias:          of:N*T*Ctraining,my-demo
```

这个 `alias` 来自 `MODULE_DEVICE_TABLE(of, my_demo_of_match)`。

对实习生来说，可以先这样理解：

```text
of_match_table 负责内核中的匹配。
MODULE_DEVICE_TABLE 负责把匹配信息导出到模块元数据中。
```

如果是手动 `insmod`，即使没有 `MODULE_DEVICE_TABLE()`，有时也能匹配成功。  
但规范驱动应该保留它，尤其是希望支持自动加载模块时。

---

## 10. compatible的命名习惯

`compatible` 一般使用下面格式：

```text
厂商名,设备名
```

例如：

```dts
compatible = "training,my-demo";
compatible = "phytium,my-uart";
compatible = "snps,dwmac-3.70a";
compatible = "realtek,rtl8211f";
```

其中逗号前面通常是厂商或组织名称，逗号后面是具体设备或 IP 名称。

不要随意写成：

```dts
compatible = "my_demo";
```

更推荐写成：

```dts
compatible = "training,my-demo";
```

这样更接近 Linux 内核设备树绑定规范。

---

## 11. compatible可以有多个字符串

设备树中的 `compatible` 可以包含多个字符串，从具体到通用排列。

例如：

```dts
ethernet@2820c000 {
	compatible = "phytium,d2000-dwmac", "snps,dwmac-3.70a";
	reg = <0x0 0x2820c000 0x0 0x2000>;
	status = "okay";
};
```

可以理解为：

```text
这个设备首先是 phytium,d2000-dwmac；
同时也兼容通用的 snps,dwmac-3.70a。
```

驱动匹配时，只要 `of_match_table` 中有任意一个字符串匹配，就可能匹配成功。

这种写法的意义是：

1. 优先表达具体 SoC 或板级设备；
2. 同时保留对通用 IP 驱动的兼容；
3. 便于一个通用驱动支持多个 SoC 变种。

---

## 12. 驱动支持多个compatible

驱动也可以支持多个 `compatible`。

例如：

```c
static const struct of_device_id my_demo_of_match[] = {
	{ .compatible = "training,my-demo-v1" },
	{ .compatible = "training,my-demo-v2" },
	{ .compatible = "training,my-demo-v3" },
	{ }
};
```

这样同一个驱动可以支持多个硬件版本。

设备树中只要写了其中任意一个，就可以匹配到该驱动。

---

## 13. 使用data区分不同硬件版本

有时候同一个驱动支持多个设备版本，但不同版本需要不同配置。

可以使用 `.data` 字段保存版本信息。

示例：

```c
struct my_demo_config {
	u32 fifo_depth;
	bool has_dma;
};

static const struct my_demo_config demo_v1_config = {
	.fifo_depth = 16,
	.has_dma = false,
};

static const struct my_demo_config demo_v2_config = {
	.fifo_depth = 64,
	.has_dma = true,
};

static const struct of_device_id my_demo_of_match[] = {
	{
		.compatible = "training,my-demo-v1",
		.data = &demo_v1_config,
	},
	{
		.compatible = "training,my-demo-v2",
		.data = &demo_v2_config,
	},
	{ }
};
```

在 `probe()` 中获取匹配到的配置：

```c
const struct of_device_id *match;
const struct my_demo_config *config;

match = of_match_device(my_demo_of_match, &pdev->dev);
if (!match)
	return -ENODEV;

config = match->data;

dev_info(&pdev->dev, "fifo depth = %u\n", config->fifo_depth);
```

这样可以避免在代码中大量使用硬编码判断。

---

## 14. of_match_ptr是什么

有些驱动中会看到：

```c
.of_match_table = of_match_ptr(my_demo_of_match),
```

`of_match_ptr()` 通常用于兼容是否启用设备树配置的情况。

如果内核没有启用设备树支持，`of_match_ptr()` 可能会让该字段变成 `NULL`，避免编译警告或无用引用。

在面向 ARM64 设备树平台的项目中，初学阶段可以先直接写：

```c
.of_match_table = my_demo_of_match,
```

这样更直观。

---

## 15. compatible匹配和driver.name匹配的区别

`platform_driver` 中还有一个字段：

```c
.driver = {
	.name = "my_demo",
}
```

初学者容易把它和 `compatible` 混淆。

二者区别如下：

| 项目 | 作用 |
|---|---|
| `compatible` | 设备树匹配使用 |
| `of_match_table` | 驱动声明支持哪些设备树 compatible |
| `driver.name` | 驱动在内核中的名字，也可能用于非设备树平台匹配 |
| 模块文件名 | `.ko` 文件名，不等于设备匹配名 |

在设备树平台上，重点看：

```text
DTS compatible
驱动 of_match_table
```

不要只看 `.driver.name`。

例如：

```c
.driver = {
	.name = "abc_driver",
	.of_match_table = my_demo_of_match,
},
```

只要 `of_match_table` 里有：

```c
{ .compatible = "training,my-demo" }
```

并且 DTS 中也有：

```dts
compatible = "training,my-demo";
```

就仍然可以匹配。

---

## 16. status属性对匹配的影响

即使 `compatible` 完全一致，如果设备树节点被禁用，通常也不会创建可用设备。

例如：

```dts
my_demo@28000000 {
	compatible = "training,my-demo";
	reg = <0x0 0x28000000 0x0 0x1000>;
	status = "disabled";
};
```

此时驱动一般不会进入 `probe()`。

应该改为：

```dts
status = "okay";
```

有些节点如果没有写 `status`，默认是否启用需要结合具体设备树解析规则和节点位置判断。为了训练和调试清晰，建议显式写：

```dts
status = "okay";
```

---

## 17. 如何确认运行时设备树中有节点

修改 DTS 后，不代表系统一定使用了新的 DTB。

Linux 启动后，可以查看运行时设备树：

```bash
ls /proc/device-tree/
```

查找自己的节点：

```bash
find /proc/device-tree/ -name '*demo*'
```

查看 compatible：

```bash
strings /proc/device-tree/路径/compatible
```

例如：

```bash
strings /proc/device-tree/my_demo@28000000/compatible
```

如果这里看不到新节点，优先怀疑：

```text
系统启动时没有加载你修改后的 DTB。
```

这在实际项目中非常常见。

---

## 18. 如何确认platform设备已经创建

查看 platform 设备目录：

```bash
ls /sys/bus/platform/devices/
```

查找相关设备：

```bash
find /sys/bus/platform/devices/ -name '*demo*'
```

或者根据地址查找：

```bash
find /sys/bus/platform/devices/ -name '*28000000*'
```

如果 `/proc/device-tree/` 中有节点，但 `/sys/bus/platform/devices/` 中没有对应设备，需要继续检查：

1. 节点位置是否正确；
2. 父节点是否是可枚举的 simple-bus 或 SoC bus；
3. 父节点是否有正确的 `compatible`；
4. 父节点是否有 `#address-cells` 和 `#size-cells`；
5. 节点是否被禁用。

---

## 19. 如何确认驱动已经注册

查看 platform 驱动目录：

```bash
ls /sys/bus/platform/drivers/
```

查找驱动：

```bash
find /sys/bus/platform/drivers/ -name '*demo*'
```

如果模块已经加载，通常可以看到驱动目录。

也可以查看模块：

```bash
lsmod | grep my_demo
```

如果模块没有加载，驱动自然不会注册，`probe()` 也不会执行。

---

## 20. 如何确认设备和驱动已经绑定

进入驱动目录：

```bash
ls -l /sys/bus/platform/drivers/my_demo/
```

如果绑定成功，通常可以看到指向设备的符号链接，例如：

```text
28000000.my_demo -> ../../../../devices/platform/28000000.my_demo
```

也可以看设备目录中是否有 `driver` 链接：

```bash
ls -l /sys/bus/platform/devices/28000000.my_demo/driver
```

如果存在 `driver` 符号链接，说明设备已经绑定到某个驱动。

---

## 21. 常见错误1：compatible字符串不一致

这是最常见的问题。

DTS：

```dts
compatible = "training,my-demo";
```

驱动：

```c
{ .compatible = "training,my_demo" },
```

注意：

```text
my-demo
my_demo
```

一个是短横线，一个是下划线，不一致，所以不会匹配。

`compatible` 是字符串匹配，必须逐字符一致。

---

## 22. 常见错误2：修改了DTS但没更新DTB

现象：

```text
1. 驱动代码看起来正确
2. DTS 看起来正确
3. 模块也能加载
4. 但是 probe() 一直不执行
5. /proc/device-tree/ 中看不到新节点
```

这通常说明系统没有使用新 DTB。

排查：

```bash
find /proc/device-tree/ -name '*demo*'
strings /proc/device-tree/路径/compatible
```

如果运行时设备树中没有新节点，就要检查：

1. DTB 是否重新编译；
2. DTB 是否复制到正确路径；
3. U-Boot 实际加载的是哪个 DTB；
4. 启动脚本是否覆盖了手动复制的文件；
5. 是否启动到了另一个分区或另一个 `/boot`。

---

## 23. 常见错误3：节点status是disabled

DTS：

```dts
status = "disabled";
```

这种情况下，通常不会进入 `probe()`。

改成：

```dts
status = "okay";
```

然后重新编译和部署 DTB。

---

## 24. 常见错误4：忘记of_match_table

有些初学者只写了：

```c
static struct platform_driver my_demo_driver = {
	.probe = my_demo_probe,
	.remove = my_demo_remove,
	.driver = {
		.name = "my_demo",
	},
};
```

但是没有：

```c
.of_match_table = my_demo_of_match,
```

这样在设备树平台上通常无法通过 `compatible` 匹配。

---

## 25. 常见错误5：忘记匹配表结束项

错误写法：

```c
static const struct of_device_id my_demo_of_match[] = {
	{ .compatible = "training,my-demo" },
};
```

正确写法：

```c
static const struct of_device_id my_demo_of_match[] = {
	{ .compatible = "training,my-demo" },
	{ }
};
```

最后的 `{ }` 是结束标记，不能省略。

---

## 26. 常见错误6：只看driver.name不看compatible

错误理解：

```text
driver.name 和 DTS 节点名一样，所以应该能匹配。
```

在设备树 platform driver 中，更关键的是：

```text
DTS compatible 是否和 of_match_table 匹配。
```

节点名、模块名、驱动名可以帮助识别，但不是最核心的匹配依据。

---

## 27. 故意改错实验

建议实习生做几个故意改错实验，加深理解。

## 27.1 改错compatible

把 DTS 中的：

```dts
compatible = "training,my-demo";
```

改成：

```dts
compatible = "training,my-demo-wrong";
```

重新编译并启动后，观察：

```text
1. 模块是否能 insmod？
2. probe 是否执行？
3. /sys/bus/platform/drivers/ 下是否有驱动？
4. /sys/bus/platform/devices/ 下是否有设备？
5. 设备和驱动是否绑定？
```

重点理解：

```text
模块可以加载，但 compatible 不匹配时，probe 不会执行。
```

## 27.2 改错status

把：

```dts
status = "okay";
```

改成：

```dts
status = "disabled";
```

观察设备是否还出现在 `/sys/bus/platform/devices/` 中。

## 27.3 删除of_match_table

在驱动中临时去掉：

```c
.of_match_table = my_demo_of_match,
```

观察 `probe()` 是否执行。

---

## 28. 推荐排查顺序

当 `probe()` 没有执行时，按下面顺序查：

```text
1. lsmod 看模块是否加载
2. dmesg 看模块是否有报错
3. modinfo 看是否有 of alias
4. /proc/device-tree 看节点是否存在
5. strings 查看运行时 compatible
6. /sys/bus/platform/devices 看设备是否创建
7. /sys/bus/platform/drivers 看驱动是否注册
8. 驱动目录下看设备是否绑定
9. 对比 DTS compatible 和 of_match_table 字符串
10. 检查 status 是否为 okay
11. 检查实际启动的 DTB 是否正确
```

对应命令：

```bash
lsmod | grep my_demo
dmesg | tail -n 50
modinfo my_demo.ko
find /proc/device-tree/ -name '*demo*'
strings /proc/device-tree/路径/compatible
find /sys/bus/platform/devices/ -name '*demo*'
find /sys/bus/platform/drivers/ -name '*demo*'
ls -l /sys/bus/platform/drivers/my_demo/
```

---

## 29. 实习生提交要求

完成本实验后，实习生应提交：

```text
1. DTS 节点内容
2. 驱动中的 of_match_table 内容
3. modinfo my_demo.ko 输出
4. /proc/device-tree 中节点检查结果
5. compatible 的 strings 输出
6. /sys/bus/platform/devices/ 检查结果
7. /sys/bus/platform/drivers/ 检查结果
8. dmesg 中 probe 是否执行的日志
9. 如果 probe 没有执行，说明排查过程
```

提交问题时，不要只写：

```text
probe 没进。
```

而应该写清楚：

```text
模块是否加载？
设备树节点是否存在？
compatible 是否一致？
platform_device 是否创建？
platform_driver 是否注册？
设备和驱动是否绑定？
```

这样沟通效率会高很多。

---

## 30. 小结

`compatible` 和 `of_match_table` 是设备树驱动匹配的核心。

可以把整个过程记成一句话：

```text
DTS 用 compatible 描述设备类型，
driver 用 of_match_table 声明自己支持哪些 compatible，
二者匹配成功后，内核调用 probe()。
```

调试 `probe()` 没有执行的问题时，优先检查：

```text
设备树节点是否真的存在；
status 是否为 okay；
compatible 是否完全一致；
驱动是否设置了 of_match_table；
系统实际启动的 DTB 是否正确。
```

这部分理解清楚后，后续学习 `reg`、`ioremap`、`interrupts`、GPIO、clock、reset 等资源获取时，就会顺畅很多。
