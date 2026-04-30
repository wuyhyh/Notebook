# 07-hello-kernel-module实验

## 1. 文档目标

本文用于完成 Linux 驱动开发的第一个实验：编写、编译、加载和卸载一个最简单的内核模块。

完成本文后，实习生应当能够掌握：

1. 什么是 Linux 内核模块；
2. `.ko` 文件是什么；
3. 如何编写最小内核模块；
4. 如何编写模块 Makefile；
5. 如何使用 `make` 编译模块；
6. 如何使用 `insmod` 加载模块；
7. 如何使用 `rmmod` 卸载模块；
8. 如何使用 `lsmod`、`modinfo` 和 `dmesg` 验证模块状态；
9. 为什么模块版本必须和当前运行内核匹配。

这篇文档的目标不是深入讲完 Linux 模块机制，而是让实习生先完成一个可以跑通的最小实验。

---

## 2. 什么是内核模块

Linux 内核模块是一段可以动态加载到内核中的代码，通常以 `.ko` 文件形式存在。

`.ko` 是 kernel object 的缩写。

内核模块加载后，代码会运行在内核空间，拥有比普通用户态程序更高的权限。

常见内核模块包括：

| 类型 | 示例 |
|---|---|
| 驱动模块 | 网卡驱动、串口驱动、GPIO 驱动 |
| 文件系统模块 | ext4、nfs、overlayfs |
| 网络功能模块 | bridge、tun、veth |
| 调试模块 | 自定义实验模块 |

对于驱动开发来说，内核模块是最基本的入口实验。

---

## 3. 内核模块和普通程序的区别

普通 C 程序运行在用户空间，例如：

```c
#include <stdio.h>

int main(void)
{
	printf("hello user\n");
	return 0;
}
```

它有 `main()` 函数，由操作系统加载并执行。

内核模块没有 `main()` 函数，而是通过 `module_init()` 和 `module_exit()` 指定入口和出口函数。

例如：

```c
module_init(hello_init);
module_exit(hello_exit);
```

含义是：

| 函数 | 作用 |
|---|---|
| `hello_init()` | 模块加载时执行 |
| `hello_exit()` | 模块卸载时执行 |

所以，内核模块的生命周期可以简单理解为：

```text
insmod hello.ko
  ↓
执行 hello_init()
  ↓
模块留在内核中
  ↓
rmmod hello
  ↓
执行 hello_exit()
  ↓
模块从内核移除
```

---

## 4. 实验环境要求

进行实验前，需要确认当前系统具备以下条件：

1. 可以使用 root 权限；
2. 已安装编译工具；
3. 已安装当前内核对应的内核头文件或内核构建目录；
4. 当前系统允许加载内核模块。

可以先查看当前内核版本：

```bash
uname -r
```

示例输出：

```text
5.10.0-136.12.0.86.aarch64
```

内核模块编译时通常需要使用：

```bash
/lib/modules/$(uname -r)/build
```

检查该路径是否存在：

```bash
ls -l /lib/modules/$(uname -r)/build
```

如果这个路径不存在，说明当前系统缺少对应的 kernel-devel 或内核构建目录，需要先安装或准备。

---

## 5. 创建实验目录

建议给每个模块实验单独创建目录：

```bash
mkdir -p ~/driver-labs/hello-module
cd ~/driver-labs/hello-module
```

最终目录结构如下：

```text
hello-module/
├── hello.c
└── Makefile
```

---

## 6. 编写 hello.c

创建 `hello.c`：

```bash
vim hello.c
```

写入以下代码：

```c
#include <linux/module.h>
#include <linux/init.h>

static int __init hello_init(void)
{
	pr_info("hello module: init\n");
	return 0;
}

static void __exit hello_exit(void)
{
	pr_info("hello module: exit\n");
}

module_init(hello_init);
module_exit(hello_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("intern");
MODULE_DESCRIPTION("A simple hello kernel module");
```

这就是一个最小可用的 Linux 内核模块。

---

## 7. 代码说明

## 7.1 头文件

```c
#include <linux/module.h>
#include <linux/init.h>
```

其中：

| 头文件 | 作用 |
|---|---|
| `<linux/module.h>` | 提供模块相关宏和接口 |
| `<linux/init.h>` | 提供 `__init`、`__exit` 等标记 |

---

## 7.2 init函数

```c
static int __init hello_init(void)
{
	pr_info("hello module: init\n");
	return 0;
}
```

这个函数会在模块加载时执行。

返回值含义：

| 返回值 | 含义 |
|---|---|
| `0` | 加载成功 |
| 非 0 | 加载失败 |

如果 `hello_init()` 返回错误，`insmod` 会失败，模块不会留在内核中。

---

## 7.3 exit函数

```c
static void __exit hello_exit(void)
{
	pr_info("hello module: exit\n");
}
```

这个函数会在模块卸载时执行。

如果模块中申请了资源，例如内存、中断、设备号等，通常应该在 exit 函数中释放。

当前实验只是打印日志，所以不需要释放额外资源。

---

## 7.4 module_init和module_exit

```c
module_init(hello_init);
module_exit(hello_exit);
```

它们用于告诉内核：

1. 模块加载时调用哪个函数；
2. 模块卸载时调用哪个函数。

这两个宏是内核模块的基本入口。

---

## 7.5 MODULE_LICENSE

```c
MODULE_LICENSE("GPL");
```

这行非常重要。

如果不写 `MODULE_LICENSE("GPL")`，加载模块时可能会看到类似日志：

```text
module license 'unspecified' taints kernel
```

这表示该模块会污染内核状态，不利于后续调试。

实验模块一般使用：

```c
MODULE_LICENSE("GPL");
```

---

## 7.6 pr_info日志

```c
pr_info("hello module: init\n");
```

`pr_info()` 是内核中的日志打印函数，类似用户态程序中的 `printf()`，但是它打印到内核日志中。

查看内核日志使用：

```bash
dmesg
```

或者实时查看：

```bash
dmesg -w
```

注意：内核中不能使用普通的 `printf()`。

---

## 8. 编写 Makefile

创建 `Makefile`：

```bash
vim Makefile
```

写入以下内容：

```makefile
obj-m += hello.o

KDIR ?= /lib/modules/$(shell uname -r)/build
PWD := $(shell pwd)

all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
```

注意：

1. `all:` 和 `clean:` 下面的命令前面必须是 Tab，不能是普通空格；
2. `obj-m += hello.o` 表示把 `hello.c` 编译成模块；
3. 最终会生成 `hello.ko`。

---

## 9. Makefile说明

## 9.1 obj-m

```makefile
obj-m += hello.o
```

这表示将 `hello.o` 编译成可加载内核模块。

虽然源码文件叫 `hello.c`，这里写的是 `hello.o`。

内核构建系统会自动根据 `hello.o` 找到 `hello.c`。

---

## 9.2 KDIR

```makefile
KDIR ?= /lib/modules/$(shell uname -r)/build
```

`KDIR` 指向当前内核的构建目录。

`$(shell uname -r)` 会获取当前运行内核版本。

例如当前内核版本是：

```text
5.10.0-136.12.0.86.aarch64
```

那么 `KDIR` 实际就是：

```text
/lib/modules/5.10.0-136.12.0.86.aarch64/build
```

---

## 9.3 M=$(PWD)

```makefile
$(MAKE) -C $(KDIR) M=$(PWD) modules
```

含义是：

1. 进入内核构建目录；
2. 使用当前目录作为外部模块目录；
3. 编译当前目录下的模块。

这是编译外部内核模块的标准写法。

---

## 10. 编译模块

在 `hello-module` 目录下执行：

```bash
make
```

如果编译成功，会生成多个文件，例如：

```text
hello.ko
hello.mod
hello.mod.c
hello.mod.o
hello.o
modules.order
Module.symvers
```

其中最重要的是：

```text
hello.ko
```

这就是可以加载到内核中的模块文件。

查看文件：

```bash
ls -l
```

---

## 11. 查看模块信息

加载之前，可以先查看模块信息：

```bash
modinfo hello.ko
```

可能看到类似输出：

```text
filename:       /home/user/driver-labs/hello-module/hello.ko
description:    A simple hello kernel module
author:         intern
license:        GPL
vermagic:       5.10.0-136.12.0.86.aarch64 SMP mod_unload aarch64
```

重点关注：

| 字段 | 含义 |
|---|---|
| `filename` | 模块文件路径 |
| `description` | 模块描述 |
| `author` | 作者信息 |
| `license` | 模块许可证 |
| `vermagic` | 模块匹配的内核版本信息 |

其中 `vermagic` 很重要。它必须和当前运行内核基本匹配，否则模块可能无法加载。

---

## 12. 加载模块

执行：

```bash
sudo insmod hello.ko
```

如果没有报错，说明模块加载成功。

查看模块是否存在：

```bash
lsmod | grep hello
```

示例输出：

```text
hello 16384 0
```

查看内核日志：

```bash
dmesg | tail
```

应该能看到：

```text
hello module: init
```

也可以在另一个终端实时观察：

```bash
sudo dmesg -w
```

然后再执行 `insmod`。

---

## 13. 卸载模块

执行：

```bash
sudo rmmod hello
```

注意，`rmmod` 后面写模块名，一般不写 `.ko` 后缀。

再次查看模块：

```bash
lsmod | grep hello
```

如果没有输出，说明模块已经卸载。

查看日志：

```bash
dmesg | tail
```

应该能看到：

```text
hello module: exit
```

---

## 14. 清理编译产物

执行：

```bash
make clean
```

清理后，当前目录中间文件会被删除。

---

## 15. 完整操作流程

完整流程如下：

```bash
mkdir -p ~/driver-labs/hello-module
cd ~/driver-labs/hello-module

vim hello.c
vim Makefile

make
modinfo hello.ko
sudo insmod hello.ko
lsmod | grep hello
dmesg | tail
sudo rmmod hello
dmesg | tail
make clean
```

建议实习生第一次实验时，一步一步执行，不要直接复制整段脚本。

---

## 16. 常见错误和排查

## 16.1 找不到内核构建目录

错误现象：

```text
/lib/modules/xxx/build: No such file or directory
```

原因：

当前系统没有安装与运行内核匹配的内核头文件或 kernel-devel。

检查：

```bash
uname -r
ls -l /lib/modules/$(uname -r)/build
```

解决方向：

1. 安装当前内核版本对应的 kernel-devel；
2. 或者指定自己的内核源码构建目录；
3. 确保该内核源码已经完成配置和必要构建准备。

---

## 16.2 Makefile命令前使用了空格

错误现象：

```text
Makefile:7: *** missing separator.  Stop.
```

原因：

Makefile 规则下面的命令前面必须使用 Tab，不能使用普通空格。

错误写法：

```makefile
all:
    $(MAKE) -C $(KDIR) M=$(PWD) modules
```

正确写法：

```makefile
all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules
```

在编辑器中要注意显示空格和 Tab。

---

## 16.3 insmod提示Invalid module format

错误现象：

```text
insmod: ERROR: could not insert module hello.ko: Invalid module format
```

常见原因：

1. 模块编译使用的内核版本和当前运行内核不一致；
2. 架构不一致，例如在 x86 上编译了模块却拿到 ARM64 系统加载；
3. 内核配置差异导致 vermagic 不匹配；
4. 使用了错误的 `KDIR`。

排查命令：

```bash
uname -r
modinfo hello.ko | grep vermagic
file hello.ko
```

重点比较：

1. `uname -r`；
2. `modinfo` 中的 `vermagic`；
3. `file` 显示的目标架构。

---

## 16.4 rmmod提示Module is in use

错误现象：

```text
rmmod: ERROR: Module hello is in use
```

原因：

模块正在被使用，引用计数不为 0。

对于本实验中的 hello 模块，正常情况下不会出现这个问题。

如果后续字符设备驱动中出现该问题，可能是设备文件仍然被进程打开。

排查方向：

```bash
lsmod | grep hello
lsof | grep hello
```

---

## 16.5 dmesg看不到日志

可能原因：

1. 模块没有成功加载；
2. 日志太多，被其他日志刷走；
3. 当前用户没有权限查看完整 dmesg；
4. 内核日志级别过滤。

建议使用：

```bash
sudo dmesg -w
```

在另一个终端执行：

```bash
sudo insmod hello.ko
sudo rmmod hello
```

这样更容易观察日志。

---

## 17. 实习生实验要求

完成本实验后，实习生需要提交一份简单记录，至少包括：

1. 当前系统内核版本：`uname -r`；
2. 实验目录路径；
3. `hello.c` 代码；
4. `Makefile` 内容；
5. `make` 是否成功；
6. `modinfo hello.ko` 关键输出；
7. `insmod` 后的 `dmesg` 输出；
8. `lsmod | grep hello` 输出；
9. `rmmod` 后的 `dmesg` 输出；
10. 遇到的问题和解决方法。

建议记录格式：

```text
实验名称：hello kernel module 实验
实验人员：xxx
实验日期：xxxx-xx-xx
内核版本：xxxx
实验结果：成功 / 失败
问题记录：
1. ...
2. ...
```

这能培养实习生的基本工程记录习惯。

---

## 18. 本实验需要真正理解的内容

完成实验后，不要求实习生理解所有内核机制，但至少要回答下面几个问题：

1. `.ko` 文件是什么？
2. `module_init()` 什么时候执行？
3. `module_exit()` 什么时候执行？
4. `insmod` 和 `rmmod` 分别做什么？
5. `lsmod` 能看到什么？
6. `modinfo` 能看到什么？
7. `dmesg` 为什么能看到模块打印？
8. 为什么模块版本要和当前内核匹配？
9. 为什么内核模块不能使用普通用户态的 `printf()`？
10. Makefile 里的 `KDIR` 是什么？

如果这些问题回答不出来，说明实验只是“照抄跑通”，还没有真正理解。

---

## 19. 和后续驱动学习的关系

hello module 是 Linux 驱动开发的入口实验。

后续学习字符设备、platform driver、中断、MMIO、sysfs 时，都会继续使用模块加载和卸载流程。

后续复杂驱动只是增加了更多内容，例如：

```text
hello module
  ↓
增加 file_operations
  ↓
变成字符设备驱动
  ↓
增加 platform_driver
  ↓
通过设备树匹配设备
  ↓
增加 ioremap/readl/writel
  ↓
访问硬件寄存器
  ↓
增加 request_irq
  ↓
处理中断
```

所以本实验虽然简单，但非常重要。

---

## 20. 小结

本文完成了第一个 Linux 内核模块实验，核心流程是：

```text
编写 hello.c
  ↓
编写 Makefile
  ↓
make 编译 hello.ko
  ↓
modinfo 查看模块信息
  ↓
insmod 加载模块
  ↓
dmesg 查看 init 日志
  ↓
lsmod 确认模块已加载
  ↓
rmmod 卸载模块
  ↓
dmesg 查看 exit 日志
```

掌握这个实验后，实习生就具备了继续学习字符设备驱动和 platform driver 的基本入口能力。
