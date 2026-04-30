# 07-probe与remove函数说明

## 1. 文档目标

本文用于说明 Linux 驱动开发中非常重要的两个函数：

```c
probe()
remove()
```

对于刚学习 Linux 驱动开发的实习生来说，必须先理解：

```text
probe() 是驱动和设备匹配成功后的入口
remove() 是驱动和设备解除绑定时的出口
```

很多驱动问题的排查，第一步都应该问：

```text
probe() 有没有被调用？
probe() 执行到哪一步失败了？
remove() 有没有被调用？
```

本文重点围绕 `platform driver` 说明 `probe()` 和 `remove()`，因为嵌入式 Linux 项目中大量板级外设驱动都采用这种模型。

---

## 2. probe函数是什么

`probe()` 是驱动匹配到设备之后，由内核自动调用的初始化函数。

以 `platform_driver` 为例：

```c
static struct platform_driver my_driver = {
	.probe = my_probe,
	.remove = my_remove,
	.driver = {
		.name = "my_driver",
		.of_match_table = my_of_match,
	},
};
```

当内核发现某个 `platform_device` 可以和这个 `platform_driver` 匹配时，就会调用：

```c
my_probe(struct platform_device *pdev)
```

简单理解：

```text
设备存在
  ↓
驱动也存在
  ↓
匹配成功
  ↓
probe() 被调用
```

所以 `probe()` 不是普通应用程序中的 `main()`，也不是模块加载后一定会执行的函数。

`probe()` 是否执行，取决于系统中是否存在能和驱动匹配的设备。

---

## 3. remove函数是什么

`remove()` 是设备和驱动解除绑定时，由内核调用的清理函数。

常见触发场景包括：

1. 卸载驱动模块；
2. 设备从系统中移除；
3. 手动从 sysfs 中 unbind 设备；
4. 驱动重新绑定；
5. 某些热插拔设备被拔出。

对于 `platform driver`，卸载模块时如果设备已经和驱动绑定，内核会调用：

```c
my_remove(struct platform_device *pdev)
```

简单理解：

```text
设备和驱动已经绑定
  ↓
驱动卸载或设备解绑
  ↓
remove() 被调用
  ↓
驱动释放资源
```

如果 `probe()` 从来没有成功执行，那么通常也不会执行对应的 `remove()`。

---

## 4. probe和remove在驱动生命周期中的位置

一个最小驱动生命周期可以表示为：

```text
insmod 驱动模块
  ↓
注册 platform_driver
  ↓
内核查找可匹配的 platform_device
  ↓
匹配成功
  ↓
调用 probe()
  ↓
驱动正常工作
  ↓
rmmod 驱动模块
  ↓
调用 remove()
  ↓
注销 platform_driver
```

注意：`insmod` 成功不等于 `probe()` 成功。

可能出现这种情况：

```text
insmod 成功
  ↓
platform_driver 注册成功
  ↓
没有匹配到设备
  ↓
probe() 没有被调用
```

这种情况不是模块加载失败，而是设备和驱动没有匹配上。

---

## 5. probe函数一般做什么

真实驱动中的 `probe()` 通常负责完成设备初始化。

常见工作包括：

```text
1. 获取 struct device
2. 分配驱动私有数据
3. 保存私有数据到设备对象
4. 获取设备树资源
5. 获取 MMIO 寄存器资源
6. 映射寄存器
7. 获取中断号
8. 申请中断
9. 获取 clock
10. 获取 reset
11. 获取 pinctrl
12. 初始化硬件寄存器
13. 注册字符设备、网络设备或其他子系统接口
14. 打印初始化成功日志
```

对于入门阶段，可以先记住这条主线：

```text
probe()
  ↓
拿资源
  ↓
初始化硬件
  ↓
注册接口
```

其中“拿资源”通常来自设备树或总线枚举信息。

---

## 6. remove函数一般做什么

`remove()` 通常负责释放或反初始化资源。

常见工作包括：

```text
1. 停止硬件工作
2. 关闭中断
3. 注销字符设备、网络设备或其他接口
4. 释放中断
5. 释放 DMA buffer
6. 关闭 clock
7. 释放 reset、pinctrl 等资源
8. 清理私有数据
```

不过在现代 Linux 驱动中，大量资源会使用 `devm_` 接口申请。  
使用 `devm_` 接口后，很多资源会在设备解绑时自动释放，`remove()` 可以明显简化。

例如：

```c
priv = devm_kzalloc(dev, sizeof(*priv), GFP_KERNEL);
base = devm_platform_ioremap_resource(pdev, 0);
ret = devm_request_irq(dev, irq, handler, 0, dev_name(dev), priv);
```

这些资源会跟随 `struct device` 的生命周期自动释放。

但即使使用了 `devm_`，`remove()` 仍然可能需要做一些主动操作，例如：

1. 停止硬件；
2. 关闭设备；
3. 注销用户空间接口；
4. 确保没有新的数据传输；
5. 等待正在执行的任务结束。

---

## 7. 最小代码示例

下面是一个最小 `probe()` 和 `remove()` 示例：

```c
#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/of.h>

struct my_demo_dev {
	struct device *dev;
};

static int my_demo_probe(struct platform_device *pdev)
{
	struct device *dev = &pdev->dev;
	struct my_demo_dev *priv;

	dev_info(dev, "probe start\n");

	priv = devm_kzalloc(dev, sizeof(*priv), GFP_KERNEL);
	if (!priv)
		return -ENOMEM;

	priv->dev = dev;
	platform_set_drvdata(pdev, priv);

	dev_info(dev, "probe done\n");

	return 0;
}

static int my_demo_remove(struct platform_device *pdev)
{
	struct my_demo_dev *priv = platform_get_drvdata(pdev);

	dev_info(&pdev->dev, "remove called\n");

	/*
	 * 如果使用 devm_kzalloc() 分配 priv，
	 * 这里不需要手动 kfree(priv)。
	 */

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
MODULE_DESCRIPTION("probe and remove demo");
```

这个例子中，`probe()` 做了三件事：

1. 打印 `probe start`；
2. 分配私有数据；
3. 使用 `platform_set_drvdata()` 保存私有数据。

`remove()` 中通过：

```c
platform_get_drvdata(pdev);
```

取回之前保存的私有数据。

---

## 8. platform_set_drvdata和platform_get_drvdata

驱动通常需要保存自己的私有数据结构，例如：

```c
struct my_demo_dev {
	struct device *dev;
	void __iomem *base;
	int irq;
};
```

这个结构体保存当前设备实例的状态和资源。

在 `probe()` 中分配并保存：

```c
priv = devm_kzalloc(dev, sizeof(*priv), GFP_KERNEL);
if (!priv)
	return -ENOMEM;

platform_set_drvdata(pdev, priv);
```

在其他地方取回：

```c
priv = platform_get_drvdata(pdev);
```

常见用途包括：

1. `remove()` 中取回私有数据；
2. 中断处理函数中使用私有数据；
3. sysfs 回调中访问设备状态；
4. 字符设备接口中访问设备资源。

可以简单理解为：

```text
platform_set_drvdata()
  把驱动私有数据挂到设备上

platform_get_drvdata()
  从设备上取回驱动私有数据
```

---

## 9. probe返回值的含义

`probe()` 返回 `0` 表示成功。

```c
return 0;
```

如果返回负数错误码，表示初始化失败，驱动不会和设备成功绑定。

常见错误码如下：

| 错误码 | 含义 | 常见场景 |
|---|---|---|
| `-ENOMEM` | 内存不足 | `kzalloc()` / `devm_kzalloc()` 失败 |
| `-EINVAL` | 参数无效 | 设备树属性格式错误 |
| `-ENODEV` | 没有设备 | 设备不符合驱动要求 |
| `-ENOENT` | 找不到资源 | 某些资源不存在 |
| `-EBUSY` | 资源忙 | 中断、IO资源被占用 |
| `-EPROBE_DEFER` | 延迟探测 | clock、reset、regulator 等依赖还没准备好 |

其中 `-EPROBE_DEFER` 在嵌入式驱动中很常见。

例如驱动依赖某个 clock provider，但这个 provider 还没有初始化完成，驱动就可能返回 `-EPROBE_DEFER`。内核稍后会再次尝试调用 `probe()`。

---

## 10. probe中常见的错误处理写法

简单驱动可以直接返回错误码：

```c
base = devm_platform_ioremap_resource(pdev, 0);
if (IS_ERR(base))
	return PTR_ERR(base);
```

获取中断失败：

```c
irq = platform_get_irq(pdev, 0);
if (irq < 0)
	return irq;
```

申请中断失败：

```c
ret = devm_request_irq(dev, irq, my_irq_handler, 0, dev_name(dev), priv);
if (ret)
	return ret;
```

推荐写法是：每一步失败都打印清楚原因。

```c
base = devm_platform_ioremap_resource(pdev, 0);
if (IS_ERR(base)) {
	dev_err(dev, "failed to map register resource\n");
	return PTR_ERR(base);
}
```

这样调试时可以直接从 `dmesg` 看出失败位置。

---

## 11. devm资源管理机制

Linux 驱动中有很多 `devm_` 开头的接口，例如：

```c
devm_kzalloc()
devm_ioremap_resource()
devm_platform_ioremap_resource()
devm_request_irq()
devm_gpiod_get()
devm_clk_get()
devm_reset_control_get()
```

`devm` 可以理解为：

```text
device managed resource
```

也就是“由设备生命周期自动管理的资源”。

使用 `devm_` 的好处是：

1. `probe()` 失败时，已经申请的资源会自动释放；
2. `remove()` 时，资源会自动释放；
3. 错误处理代码更简单；
4. 不容易漏释放资源。

对实习生来说，前期建议优先使用 `devm_` 接口，减少手动资源释放的复杂度。

但是也要理解：

```text
devm_ 只负责释放资源，不一定负责停止硬件逻辑。
```

例如，驱动在 `probe()` 中启动了硬件，那么在 `remove()` 中仍然可能需要主动关闭硬件。

---

## 12. probe为什么没有执行

这是驱动调试中最常见的问题。

如果模块已经 `insmod` 成功，但是没有看到 `probe()` 日志，通常不是 C 代码逻辑问题，而是设备和驱动没有匹配成功。

排查顺序：

```text
1. 模块是否加载成功？
2. platform_driver 是否注册成功？
3. 设备树节点是否存在？
4. 设备树节点 status 是否为 "okay"？
5. compatible 字符串是否完全一致？
6. 系统实际启动的是否是修改后的 DTB？
7. /proc/device-tree/ 中是否能看到节点？
8. /sys/bus/platform/devices/ 中是否有设备？
9. /sys/bus/platform/drivers/ 中是否有驱动？
```

常用命令：

```bash
lsmod | grep my_demo
dmesg | tail -n 50
find /proc/device-tree/ -name '*demo*'
find /sys/bus/platform/devices/ -name '*demo*'
find /sys/bus/platform/drivers/ -name '*demo*'
```

查看 compatible：

```bash
strings /proc/device-tree/路径/compatible
```

如果 `/proc/device-tree/` 中看不到你的节点，优先怀疑：

```text
实际启动的不是你修改后的 DTB。
```

---

## 13. probe执行了但失败

如果能看到 `probe start`，但是没有看到 `probe done`，说明 `probe()` 进入了，但中间某一步失败。

这时要做的是：

1. 在每一步资源获取后打印日志；
2. 检查返回值；
3. 不要忽略错误码；
4. 使用 `dev_err()` 打印失败原因。

示例：

```c
dev_info(dev, "probe start\n");

priv = devm_kzalloc(dev, sizeof(*priv), GFP_KERNEL);
if (!priv) {
	dev_err(dev, "failed to allocate priv\n");
	return -ENOMEM;
}

dev_info(dev, "priv allocated\n");

irq = platform_get_irq(pdev, 0);
if (irq < 0) {
	dev_err(dev, "failed to get irq: %d\n", irq);
	return irq;
}

dev_info(dev, "irq = %d\n", irq);
```

这样可以通过日志判断失败位置。

---

## 14. remove为什么没有执行

常见原因有：

```text
1. probe() 从未成功执行
2. 驱动没有和设备绑定
3. 模块没有真正卸载
4. 驱动是内建到内核的，不是模块
5. remove() 没有配置到 platform_driver 中
```

例如下面代码中，如果忘记设置 `.remove`：

```c
static struct platform_driver my_driver = {
	.probe = my_probe,
	.driver = {
		.name = "my_driver",
		.of_match_table = my_of_match,
	},
};
```

那么卸载时自然不会调用驱动自己的 `remove()`。

---

## 15. 手动bind和unbind

Linux 允许通过 sysfs 手动绑定和解绑设备。

假设驱动目录是：

```text
/sys/bus/platform/drivers/my_demo
```

设备名是：

```text
28000000.my_demo
```

可以手动解绑：

```bash
echo 28000000.my_demo > /sys/bus/platform/drivers/my_demo/unbind
```

也可以重新绑定：

```bash
echo 28000000.my_demo > /sys/bus/platform/drivers/my_demo/bind
```

执行 `unbind` 时，如果设备已经绑定，通常会触发 `remove()`。

执行 `bind` 时，如果匹配成功，通常会再次触发 `probe()`。

查看设备名：

```bash
ls /sys/bus/platform/devices/
```

查看驱动名：

```bash
ls /sys/bus/platform/drivers/
```

注意：手动 bind/unbind 适合调试，但不要在不了解设备状态时随意操作真实关键设备，例如存储控制器、网卡、时钟控制器等。

---

## 16. probe和模块init的区别

初学者很容易混淆：

```text
module_init()
probe()
```

二者不是一回事。

对于 `module_platform_driver()` 来说，它内部会生成模块初始化和退出逻辑。

可以简单理解为：

```text
module_init()
  注册 platform_driver

probe()
  platform_driver 匹配到 platform_device 后被调用
```

也就是说：

```text
模块加载成功，只能说明 driver 注册了
probe 被调用，才说明 driver 找到了匹配的 device
```

对调试来说，这个区别非常关键。

---

## 17. probe和设备树的关系

在设备树系统中，`probe()` 通常依赖下面几个条件：

```text
1. DTS 中存在设备节点
2. 节点 status = "okay"
3. 节点 compatible 和驱动 of_match_table 匹配
4. 系统启动时加载了包含该节点的 DTB
5. 对应 bus 能够创建 platform_device
6. 驱动模块已经加载或内建到内核
```

最小 DTS 示例：

```dts
my_demo@28000000 {
	compatible = "training,my-demo";
	reg = <0x0 0x28000000 0x0 0x1000>;
	status = "okay";
};
```

对应驱动匹配表：

```c
static const struct of_device_id my_demo_of_match[] = {
	{ .compatible = "training,my-demo" },
	{ }
};
```

这两个字符串必须完全一致：

```text
training,my-demo
```

---

## 18. probe函数中的日志建议

驱动调试时，不建议只写一条日志。

更推荐在关键阶段打印：

```c
dev_info(dev, "probe start\n");

dev_info(dev, "resource parsed\n");

dev_info(dev, "irq requested\n");

dev_info(dev, "hardware initialized\n");

dev_info(dev, "probe done\n");
```

失败时使用：

```c
dev_err(dev, "failed to get irq: %d\n", irq);
```

调试信息可以使用：

```c
dev_dbg(dev, "debug value = %u\n", val);
```

`dev_info()`、`dev_err()` 相比 `pr_info()`、`pr_err()` 的好处是，它们会带上设备信息，更容易判断是哪一个设备实例打印的日志。

---

## 19. 实习生实验要求

建议实习生基于前一篇 `07-platform-driver最小实验.md` 的代码，完成下面实验。

## 19.1 实验1：观察probe和remove

操作：

```bash
make
sudo insmod my_demo.ko
dmesg | tail -n 30
sudo rmmod my_demo
dmesg | tail -n 30
```

要求看到：

```text
probe start
probe done
remove called
```

## 19.2 实验2：故意改错compatible

把 DTS 中的：

```dts
compatible = "training,my-demo";
```

故意改成：

```dts
compatible = "training,my-demo-wrong";
```

重新启动后加载模块，观察：

```text
1. insmod 是否成功？
2. probe 是否执行？
3. dmesg 有什么变化？
```

要求理解：

```text
insmod 成功不等于 probe 成功。
```

## 19.3 实验3：在probe中模拟失败

在 `probe()` 中添加：

```c
return -EINVAL;
```

观察：

```text
1. probe 是否进入？
2. 模块是否加载？
3. 驱动和设备是否绑定？
4. remove 是否会执行？
```

## 19.4 实验4：手动unbind和bind

查看设备名和驱动名后，执行：

```bash
echo 设备名 > /sys/bus/platform/drivers/驱动名/unbind
echo 设备名 > /sys/bus/platform/drivers/驱动名/bind
```

观察：

```text
1. unbind 是否触发 remove？
2. bind 是否触发 probe？
```

---

## 20. 常见错误总结

## 20.1 以为insmod成功就代表驱动工作了

错误理解：

```text
insmod 成功，所以驱动已经工作。
```

正确理解：

```text
insmod 成功只说明模块加载成功。
probe 成功才说明驱动和设备匹配并初始化成功。
```

## 20.2 以为probe一定会执行

错误理解：

```text
我加载了模块，probe 就应该执行。
```

正确理解：

```text
probe 只有在驱动匹配到设备后才会执行。
```

## 20.3 不检查probe返回值

错误写法：

```c
platform_get_irq(pdev, 0);
```

正确写法：

```c
irq = platform_get_irq(pdev, 0);
if (irq < 0)
	return irq;
```

驱动中所有可能失败的函数都应该检查返回值。

## 20.4 remove中手动释放devm资源

如果资源是通过 `devm_kzalloc()` 申请的，一般不需要在 `remove()` 中手动 `kfree()`。

错误写法：

```c
priv = platform_get_drvdata(pdev);
kfree(priv);
```

如果 `priv` 来自 `devm_kzalloc()`，这样可能导致重复释放。

## 20.5 remove中没有停止硬件

即使使用了 `devm_` 自动释放资源，也不能完全忽略 `remove()`。

如果硬件已经启动，`remove()` 中仍然应该考虑：

```text
1. 禁止中断
2. 停止 DMA
3. 停止硬件发送或接收
4. 注销对外接口
```

---

## 21. 小结

`probe()` 和 `remove()` 是理解 Linux 驱动生命周期的关键。

对于入门阶段，可以先记住：

```text
probe()
  驱动和设备匹配成功后执行
  用于获取资源、初始化硬件、注册接口

remove()
  驱动和设备解绑时执行
  用于停止硬件、注销接口、释放资源
```

调试驱动时，最重要的第一步是判断：

```text
probe() 到底有没有进？
```

如果 `probe()` 没进，优先查设备树、`compatible`、DTB 是否更新、设备是否创建。

如果 `probe()` 进了但失败，优先查每一步资源获取的返回值和 `dmesg` 日志。

把 `probe()` 和 `remove()` 理解清楚后，再学习 MMIO、中断、sysfs、I2C、SPI、DMA 等内容，就会顺畅很多。
