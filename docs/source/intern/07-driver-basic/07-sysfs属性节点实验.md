# 07-sysfs属性节点实验

## 1. 文档目标

本文用于整理 Linux 驱动开发中常见的 sysfs 属性节点实验。

在驱动调试阶段，我们经常希望通过简单命令查看或修改驱动内部状态，例如：

```bash
cat /sys/bus/platform/devices/xxx/status
echo 1 > /sys/bus/platform/devices/xxx/enable
```

这类接口通常可以通过 sysfs 属性节点实现。

完成本文后，应该能够理解：

1. sysfs 是什么；
2. sysfs 属性节点适合做什么；
3. `show()` 和 `store()` 函数分别有什么作用；
4. 如何在 `platform driver` 中创建一个简单 sysfs 属性；
5. 如何通过 `cat` 和 `echo` 访问属性节点；
6. sysfs 调试接口有哪些限制；
7. 如何排查 sysfs 属性节点创建失败的问题。

本文只讲最基础的 `DEVICE_ATTR` 实验，不深入展开 `attribute_group`、`class`、`kobject` 等更复杂内容。

---

## 2. sysfs是什么

sysfs 是 Linux 内核向用户空间导出设备、驱动、总线和内核对象信息的一种虚拟文件系统。

它通常挂载在：

```text
/sys
```

在驱动开发中，经常会查看这些目录：

```bash
ls /sys/bus/platform/devices/
ls /sys/bus/platform/drivers/
ls /sys/class/
ls /sys/devices/
```

例如，一个 platform 设备可能出现在：

```text
/sys/bus/platform/devices/28000000.my_demo/
```

如果驱动给这个设备创建了属性节点，就可能看到：

```text
/sys/bus/platform/devices/28000000.my_demo/status
/sys/bus/platform/devices/28000000.my_demo/enable
/sys/bus/platform/devices/28000000.my_demo/value
```

用户空间可以通过普通文件操作访问这些节点。

---

## 3. sysfs适合做什么

sysfs 属性节点适合用于：

```text
1. 查看设备状态
2. 查看驱动内部变量
3. 打开或关闭简单功能
4. 设置简单参数
5. 触发简单调试动作
6. 暴露低频控制接口
```

例如：

```bash
cat status
cat version
cat irq_count
echo 1 > enable
echo 0 > reset
```

sysfs 不适合用于：

```text
1. 高频数据传输
2. 大块二进制数据传输
3. 高性能数据通路
4. 复杂协议交互
5. 替代字符设备或网络接口
```

简单理解：

```text
sysfs 适合做控制和状态查看；
不适合做大量数据读写。
```

---

## 4. sysfs属性的基本形式

一个 sysfs 属性节点通常对应两个回调函数：

```text
show()
store()
```

其中：

| 函数 | 作用 | 对应用户操作 |
|---|---|---|
| `show()` | 从内核向用户空间输出文本 | `cat xxx` |
| `store()` | 从用户空间向内核写入文本 | `echo xxx > node` |

例如：

```bash
cat enable
```

会触发驱动中的 `enable_show()`。

```bash
echo 1 > enable
```

会触发驱动中的 `enable_store()`。

---

## 5. show函数

`show()` 函数用于向用户空间输出内容。

典型形式：

```c
static ssize_t enable_show(struct device *dev,
			   struct device_attribute *attr,
			   char *buf)
{
	struct my_sysfs_demo *priv = dev_get_drvdata(dev);

	return sysfs_emit(buf, "%u\n", priv->enable);
}
```

参数说明：

| 参数 | 含义 |
|---|---|
| `dev` | 当前设备对象 |
| `attr` | 当前属性对象 |
| `buf` | 输出缓冲区 |

返回值表示写入 `buf` 的字节数。

推荐使用：

```c
sysfs_emit()
```

而不是直接使用：

```c
sprintf()
```

因为 `sysfs_emit()` 更符合 sysfs 输出缓冲区的使用规范。

---

## 6. store函数

`store()` 函数用于接收用户空间写入的数据。

典型形式：

```c
static ssize_t enable_store(struct device *dev,
			    struct device_attribute *attr,
			    const char *buf,
			    size_t count)
{
	struct my_sysfs_demo *priv = dev_get_drvdata(dev);
	unsigned long val;
	int ret;

	ret = kstrtoul(buf, 0, &val);
	if (ret)
		return ret;

	priv->enable = !!val;

	return count;
}
```

参数说明：

| 参数 | 含义 |
|---|---|
| `dev` | 当前设备对象 |
| `attr` | 当前属性对象 |
| `buf` | 用户空间写入的字符串 |
| `count` | 写入的字节数 |

返回值通常应该是：

```c
return count;
```

表示成功处理了用户写入的数据。

如果解析失败，可以返回负数错误码，例如：

```c
return -EINVAL;
```

---

## 7. DEVICE_ATTR宏

最基础的属性节点可以使用 `DEVICE_ATTR` 定义。

示例：

```c
static DEVICE_ATTR_RW(enable);
```

这个宏会创建一个名为 `enable` 的属性，并要求代码中存在：

```c
enable_show()
enable_store()
```

也就是：

```c
static ssize_t enable_show(...);
static ssize_t enable_store(...);
```

常见宏包括：

| 宏 | 含义 |
|---|---|
| `DEVICE_ATTR_RW(name)` | 可读可写 |
| `DEVICE_ATTR_RO(name)` | 只读 |
| `DEVICE_ATTR_WO(name)` | 只写 |

例如：

```c
static DEVICE_ATTR_RO(status);
static DEVICE_ATTR_RW(enable);
static DEVICE_ATTR_WO(reset);
```

分别对应：

```text
status 只读
enable 可读可写
reset 只写
```

---

## 8. device_create_file和device_remove_file

创建属性节点：

```c
ret = device_create_file(dev, &dev_attr_enable);
if (ret)
	return ret;
```

删除属性节点：

```c
device_remove_file(dev, &dev_attr_enable);
```

其中 `dev_attr_enable` 是 `DEVICE_ATTR_RW(enable)` 生成的对象。

如果属性在 `probe()` 中创建，那么通常应该在 `remove()` 中删除。

简单流程：

```text
probe()
  device_create_file()

remove()
  device_remove_file()
```

---

## 9. 最小实验目标

本实验基于前面的 `platform driver` 实验继续扩展，实现两个 sysfs 属性：

```text
enable
status
```

其中：

| 属性 | 权限 | 作用 |
|---|---|---|
| `enable` | 可读可写 | 保存一个软件开关变量 |
| `status` | 只读 | 显示当前驱动状态 |

用户空间访问方式：

```bash
cat /sys/bus/platform/devices/xxx/enable
echo 1 > /sys/bus/platform/devices/xxx/enable
cat /sys/bus/platform/devices/xxx/status
```

这个实验先不直接操作真实硬件寄存器，只用软件变量演示 sysfs 属性节点机制。

---

## 10. 实验代码

创建文件：

```bash
vim my_sysfs_demo.c
```

内容如下：

```c
#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/of.h>
#include <linux/mutex.h>

struct my_sysfs_demo {
	struct device *dev;
	bool enable;
	u32 status;
	struct mutex lock;
};

static ssize_t enable_show(struct device *dev,
			   struct device_attribute *attr,
			   char *buf)
{
	struct my_sysfs_demo *priv = dev_get_drvdata(dev);
	bool enable;

	mutex_lock(&priv->lock);
	enable = priv->enable;
	mutex_unlock(&priv->lock);

	return sysfs_emit(buf, "%u\n", enable ? 1 : 0);
}

static ssize_t enable_store(struct device *dev,
			    struct device_attribute *attr,
			    const char *buf,
			    size_t count)
{
	struct my_sysfs_demo *priv = dev_get_drvdata(dev);
	unsigned long val;
	int ret;

	ret = kstrtoul(buf, 0, &val);
	if (ret)
		return ret;

	mutex_lock(&priv->lock);
	priv->enable = !!val;
	mutex_unlock(&priv->lock);

	dev_info(dev, "enable set to %u\n", priv->enable ? 1 : 0);

	return count;
}

static DEVICE_ATTR_RW(enable);

static ssize_t status_show(struct device *dev,
			   struct device_attribute *attr,
			   char *buf)
{
	struct my_sysfs_demo *priv = dev_get_drvdata(dev);
	u32 status;

	mutex_lock(&priv->lock);
	status = priv->status;
	mutex_unlock(&priv->lock);

	return sysfs_emit(buf, "status=0x%08x\n", status);
}

static DEVICE_ATTR_RO(status);

static int my_sysfs_demo_probe(struct platform_device *pdev)
{
	struct device *dev = &pdev->dev;
	struct my_sysfs_demo *priv;
	int ret;

	dev_info(dev, "probe start\n");

	priv = devm_kzalloc(dev, sizeof(*priv), GFP_KERNEL);
	if (!priv)
		return -ENOMEM;

	priv->dev = dev;
	priv->enable = false;
	priv->status = 0x12345678;
	mutex_init(&priv->lock);

	platform_set_drvdata(pdev, priv);

	ret = device_create_file(dev, &dev_attr_enable);
	if (ret) {
		dev_err(dev, "failed to create enable attribute: %d\n", ret);
		return ret;
	}

	ret = device_create_file(dev, &dev_attr_status);
	if (ret) {
		dev_err(dev, "failed to create status attribute: %d\n", ret);
		device_remove_file(dev, &dev_attr_enable);
		return ret;
	}

	dev_info(dev, "probe done\n");

	return 0;
}

static int my_sysfs_demo_remove(struct platform_device *pdev)
{
	struct device *dev = &pdev->dev;

	device_remove_file(dev, &dev_attr_status);
	device_remove_file(dev, &dev_attr_enable);

	dev_info(dev, "remove called\n");

	return 0;
}

static const struct of_device_id my_sysfs_demo_of_match[] = {
	{ .compatible = "training,my-sysfs-demo" },
	{ }
};

MODULE_DEVICE_TABLE(of, my_sysfs_demo_of_match);

static struct platform_driver my_sysfs_demo_driver = {
	.probe = my_sysfs_demo_probe,
	.remove = my_sysfs_demo_remove,
	.driver = {
		.name = "my_sysfs_demo",
		.of_match_table = my_sysfs_demo_of_match,
	},
};

module_platform_driver(my_sysfs_demo_driver);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("training");
MODULE_DESCRIPTION("basic sysfs attribute demo");
```

---

## 11. 代码说明

## 11.1 私有数据结构

```c
struct my_sysfs_demo {
	struct device *dev;
	bool enable;
	u32 status;
	struct mutex lock;
};
```

字段说明：

| 字段 | 作用 |
|---|---|
| `dev` | 保存设备对象 |
| `enable` | 软件开关变量 |
| `status` | 模拟设备状态 |
| `lock` | 保护变量并发访问 |

sysfs 的 `show()` 和 `store()` 可能和其他代码路径并发执行，所以访问共享变量时要考虑加锁。

---

## 11.2 enable属性

定义：

```c
static DEVICE_ATTR_RW(enable);
```

表示创建一个可读可写属性：

```text
enable
```

读取时触发：

```c
enable_show()
```

写入时触发：

```c
enable_store()
```

读取：

```bash
cat enable
```

写入：

```bash
echo 1 > enable
echo 0 > enable
```

---

## 11.3 status属性

定义：

```c
static DEVICE_ATTR_RO(status);
```

表示创建一个只读属性：

```text
status
```

读取时触发：

```c
status_show()
```

因为是只读属性，所以不需要实现：

```c
status_store()
```

读取：

```bash
cat status
```

如果尝试写入：

```bash
echo 1 > status
```

通常会失败。

---

## 12. Makefile

创建文件：

```bash
vim Makefile
```

内容如下：

```makefile
obj-m += my_sysfs_demo.o

KDIR ?= /lib/modules/$(shell uname -r)/build
PWD  := $(shell pwd)

all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
```

编译：

```bash
make
```

生成：

```text
my_sysfs_demo.ko
```

查看模块信息：

```bash
modinfo my_sysfs_demo.ko
```

---

## 13. DTS节点示例

添加设备树节点：

```dts
my_sysfs_demo@28000000 {
	compatible = "training,my-sysfs-demo";
	reg = <0x0 0x28000000 0x0 0x1000>;
	status = "okay";
};
```

注意：

```text
本实验不访问 reg 寄存器。
这里保留 reg 是为了让节点形式接近真实 platform 设备。
```

如果只是做匹配实验，`reg` 地址要避免和真实设备冲突。实际项目中必须根据硬件资源填写。

---

## 14. 加载模块

编译完成后加载：

```bash
sudo insmod my_sysfs_demo.ko
```

查看日志：

```bash
dmesg | tail -n 50
```

期望看到：

```text
probe start
probe done
```

如果没有看到 `probe done`，先排查：

```text
1. 模块是否加载成功；
2. compatible 是否匹配；
3. 设备树节点是否存在；
4. 实际启动的 DTB 是否正确；
5. device_create_file 是否失败。
```

---

## 15. 查找设备目录

查看 platform 设备：

```bash
ls /sys/bus/platform/devices/
```

查找 demo 设备：

```bash
find /sys/bus/platform/devices/ -name '*sysfs*'
```

也可以按地址查找：

```bash
find /sys/bus/platform/devices/ -name '*28000000*'
```

假设设备目录是：

```text
/sys/bus/platform/devices/28000000.my_sysfs_demo/
```

进入目录：

```bash
cd /sys/bus/platform/devices/28000000.my_sysfs_demo/
```

查看属性节点：

```bash
ls -l
```

应该能看到：

```text
enable
status
```

---

## 16. 读取属性

读取 `enable`：

```bash
cat enable
```

初始值应该是：

```text
0
```

读取 `status`：

```bash
cat status
```

输出示例：

```text
status=0x12345678
```

这说明 `show()` 函数正常工作。

---

## 17. 写入属性

写入 `enable`：

```bash
echo 1 > enable
cat enable
```

期望输出：

```text
1
```

再写入：

```bash
echo 0 > enable
cat enable
```

期望输出：

```text
0
```

查看内核日志：

```bash
dmesg | tail -n 20
```

可以看到类似：

```text
enable set to 1
enable set to 0
```

---

## 18. 尝试写入只读属性

`status` 是只读属性，尝试写入：

```bash
echo 1 > status
```

通常会失败，可能提示：

```text
Permission denied
```

或者：

```text
Read-only file system
```

具体提示和 shell、权限、系统环境有关。

这说明只读属性生效。

---

## 19. 卸载模块

执行：

```bash
sudo rmmod my_sysfs_demo
```

查看日志：

```bash
dmesg | tail -n 50
```

期望看到：

```text
remove called
```

卸载后，原来的 sysfs 属性节点也应该消失。

---

## 20. 为什么要在remove中删除属性

如果在 `probe()` 中创建：

```c
device_create_file(dev, &dev_attr_enable);
```

就应该在 `remove()` 中删除：

```c
device_remove_file(dev, &dev_attr_enable);
```

否则可能出现：

1. 设备解绑后属性节点残留；
2. 用户空间还能访问已失效对象；
3. 内核访问已释放数据；
4. 引发 use-after-free 风险。

基本原则：

```text
probe 中创建的外部接口，remove 中要撤销。
```

即使使用 `devm_` 管理部分资源，sysfs 文件也要注意生命周期。

---

## 21. show函数注意事项

`show()` 函数要注意：

```text
1. 输出文本，通常以换行结尾；
2. 返回实际写入字节数；
3. 推荐使用 sysfs_emit()；
4. 不要输出大量内容；
5. 不要在 show() 中做耗时操作；
6. 访问共享数据时考虑加锁；
7. 不要返回超过 PAGE_SIZE 的内容。
```

推荐：

```c
return sysfs_emit(buf, "%u\n", value);
```

不要写复杂长输出。

---

## 22. store函数注意事项

`store()` 函数要注意：

```text
1. 输入是字符串，不是二进制结构体；
2. 要检查输入是否合法；
3. 推荐使用 kstrto* 系列函数解析；
4. 成功时通常返回 count；
5. 失败时返回负数错误码；
6. 不要信任用户输入；
7. 不要在 store() 中做长时间阻塞操作。
```

解析整数常用：

```c
kstrtoul()
kstrtouint()
kstrtoint()
kstrtobool()
```

例如解析布尔值，可以写：

```c
bool val;
int ret;

ret = kstrtobool(buf, &val);
if (ret)
	return ret;
```

这样可以接受：

```text
0/1
y/n
yes/no
true/false
on/off
```

具体行为以当前内核实现为准。

---

## 23. sysfs权限

使用 `DEVICE_ATTR_RW(enable)` 时，内核会自动生成常见读写权限。

如果使用更底层的 `DEVICE_ATTR()`，可以手动指定权限，例如：

```c
static DEVICE_ATTR(enable, 0644, enable_show, enable_store);
```

其中：

```text
0644
```

表示：

```text
owner 可读写
group 可读
others 可读
```

常见权限：

| 权限 | 含义 |
|---|---|
| `0444` | 只读 |
| `0644` | root 可写，所有用户可读 |
| `0200` | 只写 |
| `0600` | root 可读写 |

入门阶段建议优先使用：

```c
DEVICE_ATTR_RO()
DEVICE_ATTR_RW()
DEVICE_ATTR_WO()
```

这样更简单。

---

## 24. sysfs和字符设备的区别

sysfs 和字符设备都能让用户空间访问驱动，但用途不同。

| 项目 | sysfs | 字符设备 |
|---|---|---|
| 路径 | `/sys/...` | `/dev/...` |
| 适合用途 | 状态、配置、低频控制 | 数据读写、复杂交互 |
| 数据形式 | 文本为主 | 字节流或 ioctl |
| 典型操作 | `cat` / `echo` | `read` / `write` / `ioctl` |
| 是否适合大量数据 | 不适合 | 更适合 |

简单判断：

```text
查看一个状态，用 sysfs；
设置一个简单开关，用 sysfs；
传输大量数据，用字符设备或其他子系统接口。
```

---

## 25. sysfs和debugfs的区别

sysfs 和 debugfs 都常用于调试，但定位不同。

| 项目 | sysfs | debugfs |
|---|---|---|
| 路径 | `/sys/...` | `/sys/kernel/debug/...` |
| 主要用途 | 稳定设备属性和控制接口 | 调试信息 |
| 是否适合长期对外接口 | 可以，但要谨慎 | 不适合作为稳定 ABI |
| 面向对象 | 设备、驱动、类、总线 | 调试开发 |
| 是否默认挂载 | 通常是 | 不一定 |

对实习生来说，先掌握 sysfs。  
后续需要更灵活的调试信息时，再学习 debugfs。

---

## 26. 常见错误1：属性函数命名不匹配

如果使用：

```c
static DEVICE_ATTR_RW(enable);
```

那么必须定义：

```c
enable_show()
enable_store()
```

如果函数名写成：

```c
my_enable_show()
my_enable_store()
```

会编译失败，因为宏找不到对应函数。

解决方法：

1. 按宏要求命名；
2. 或者使用更底层的 `DEVICE_ATTR()` 手动指定函数。

---

## 27. 常见错误2：没有设置driver data

如果 `show()` 中写：

```c
struct my_sysfs_demo *priv = dev_get_drvdata(dev);
```

但是 `probe()` 中忘记：

```c
platform_set_drvdata(pdev, priv);
```

那么 `priv` 可能是 `NULL`，访问会导致内核异常。

正确流程：

```c
platform_set_drvdata(pdev, priv);
```

然后在 sysfs 回调中：

```c
priv = dev_get_drvdata(dev);
```

---

## 28. 常见错误3：store返回值错误

错误写法：

```c
return 0;
```

这会让用户空间认为没有成功写入任何数据，可能导致行为异常。

成功处理写入时通常应该：

```c
return count;
```

如果输入非法，再返回错误码：

```c
return -EINVAL;
```

---

## 29. 常见错误4：没有删除属性节点

如果 `probe()` 中创建属性：

```c
device_create_file(dev, &dev_attr_enable);
```

但 `remove()` 中没有删除：

```c
device_remove_file(dev, &dev_attr_enable);
```

可能产生生命周期问题。

正确做法是：

```c
static int my_remove(struct platform_device *pdev)
{
	struct device *dev = &pdev->dev;

	device_remove_file(dev, &dev_attr_enable);
	return 0;
}
```

如果创建了多个属性，删除顺序通常与创建顺序相反。

---

## 30. 常见错误5：并发访问没有保护

`show()` 和 `store()` 可能并发执行，也可能和中断、workqueue、ioctl 等路径并发访问同一个变量。

如果是简单变量，有时问题不明显；但工程上应该养成加锁意识。

示例：

```c
mutex_lock(&priv->lock);
priv->enable = !!val;
mutex_unlock(&priv->lock);
```

注意：

```text
sysfs show/store 运行在进程上下文中，可以使用 mutex。
普通硬中断处理函数中不能使用可能睡眠的 mutex。
```

如果变量也在中断上下文中访问，要考虑使用 `spinlock` 或原子变量等方式。

---

## 31. 常见错误6：在sysfs中做复杂协议

不要把 sysfs 当成万能接口。

不建议通过 sysfs 做：

```text
1. 大量数据收发
2. 长时间阻塞等待
3. 复杂二进制协议
4. 高频寄存器读写
5. 用户空间和内核之间的大块数据搬运
```

如果需要这些能力，应该考虑：

```text
字符设备
netlink
ioctl
mmap
专用内核子系统接口
```

sysfs 的优势是简单、清晰、适合低频控制。

---

## 32. 调试排查顺序

如果 sysfs 属性没有出现，按下面顺序排查：

```text
1. 模块是否加载成功？
2. probe 是否执行？
3. compatible 是否匹配？
4. platform_set_drvdata 是否调用？
5. device_create_file 是否返回错误？
6. /sys/bus/platform/devices/ 下设备目录是否存在？
7. 是否进入了正确的设备目录？
8. 属性名是否和 DEVICE_ATTR 宏一致？
9. remove 是否过早执行？
10. dmesg 中是否有错误日志？
```

常用命令：

```bash
lsmod | grep my_sysfs_demo
dmesg | tail -n 50
find /sys/bus/platform/devices/ -name '*sysfs*'
find /sys/bus/platform/drivers/ -name '*sysfs*'
ls -l /sys/bus/platform/devices/设备名/
```

如果属性出现但读写失败，继续检查：

```text
1. 权限是否正确？
2. show/store 是否实现？
3. 输入格式是否合法？
4. store 是否返回 count？
5. dev_get_drvdata 是否得到有效 priv？
6. 是否出现内核 oops？
```

---

## 33. 实习生实验要求

建议实习生基于 `07-platform-driver最小实验.md` 继续完成本实验。

## 33.1 实验1：创建enable属性

要求：

1. 添加 `enable_show()`；
2. 添加 `enable_store()`；
3. 添加 `DEVICE_ATTR_RW(enable)`；
4. 在 `probe()` 中调用 `device_create_file()`；
5. 在 `remove()` 中调用 `device_remove_file()`。

验证：

```bash
cat enable
echo 1 > enable
cat enable
echo 0 > enable
cat enable
```

---

## 33.2 实验2：创建status只读属性

要求：

1. 添加 `status_show()`；
2. 添加 `DEVICE_ATTR_RO(status)`；
3. 在 `probe()` 中创建；
4. 在 `remove()` 中删除。

验证：

```bash
cat status
echo 1 > status
```

确认写入只读属性失败。

---

## 33.3 实验3：故意输入非法值

执行：

```bash
echo abc > enable
```

观察：

1. `store()` 返回错误；
2. shell 有什么提示；
3. dmesg 是否有异常；
4. enable 值是否保持不变。

---

## 33.4 实验4：故意去掉platform_set_drvdata

临时注释：

```c
platform_set_drvdata(pdev, priv);
```

观察访问 sysfs 时是否异常。

这个实验用于理解：

```text
sysfs 回调中拿到的 dev，需要通过 dev_get_drvdata() 找回驱动私有数据。
```

注意：这个实验可能导致内核异常，只建议在可恢复的测试环境中进行。

---

## 34. 实习生提交要求

完成本文实验后，实习生应提交：

```text
1. 驱动源码
2. Makefile
3. DTS 节点内容
4. make 编译结果
5. insmod/rmmod 操作记录
6. dmesg 日志
7. /sys/bus/platform/devices/ 下设备路径
8. enable 属性读写结果
9. status 属性读取结果
10. 非法输入测试结果
11. 遇到的问题和排查过程
```

问题报告不要只写：

```text
sysfs 不行。
```

应该写清楚：

```text
probe 是否进入？
设备目录是否存在？
属性文件是否存在？
cat 报什么错？
echo 报什么错？
dmesg 有没有错误？
device_create_file 返回值是多少？
```

---

## 35. 小结

sysfs 属性节点是 Linux 驱动调试和简单控制中非常常用的机制。

基本流程是：

```text
定义 show/store
  ↓
使用 DEVICE_ATTR 定义属性
  ↓
probe 中 device_create_file
  ↓
用户空间 cat/echo 访问
  ↓
remove 中 device_remove_file
```

入门阶段要牢记：

```text
show 对应 cat；
store 对应 echo；
成功 store 通常返回 count；
show 推荐使用 sysfs_emit；
sysfs 适合低频状态和控制；
sysfs 不适合大数据传输；
probe 中创建的属性，remove 中要删除。
```

掌握 sysfs 后，实习生就可以为简单驱动增加状态查看和调试开关，这对实际项目调试很有帮助。
