# 04-内核模块基础与hello-module实验

## 1. 文档目标

本文用于说明 Linux 内核模块的基本概念，并通过一个最简单的 `hello_module` 实验，让初学者理解内核模块的编写、编译、加载、查看和卸载流程。

学习完成后，应能够回答以下问题：

1. 什么是内核模块？
2. `.ko` 文件是什么？
3. `insmod`、`rmmod`、`lsmod`、`modinfo` 分别用于什么场景？
4. `printk()` 打印的信息应该在哪里查看？
5. 内核模块和普通用户态程序有什么区别？

## 2. 什么是内核模块

Linux 内核模块是一段可以动态加载到内核中的代码，通常用于实现驱动程序、文件系统、网络功能或调试功能。

内核模块的常见文件后缀是：

```text
.ko
```

`.ko` 是 kernel object 的缩写，可以理解为“内核目标文件”。

与普通用户态程序不同，内核模块不是通过 `./a.out` 这种方式运行，而是由内核加载后在内核态执行。

## 3. 内核模块的作用

内核模块的主要作用包括：

1. 不重新编译整个内核，也可以增加某些功能
2. 驱动可以按需加载和卸载
3. 方便调试某些内核功能
4. 方便开发板适配不同硬件配置

例如，一个网卡驱动、一个字符设备驱动、一个文件系统驱动，都可以被编译成内核模块。

## 4. 内核模块与内核镜像的关系

Linux 内核功能通常有三种编译方式：

| 配置状态 | 含义 |
| --- | --- |
| `CONFIG_XXX=y` | 编译进内核镜像，例如 `Image` |
| `CONFIG_XXX=m` | 编译成内核模块，例如 `xxx.ko` |
| `# CONFIG_XXX is not set` | 不编译该功能 |

如果驱动被编译进内核镜像，系统启动时就已经存在。

如果驱动被编译成模块，则需要通过 `insmod` 或 `modprobe` 加载。

## 5. 常用模块命令

| 命令 | 作用 |
| --- | --- |
| `lsmod` | 查看当前已经加载的模块 |
| `insmod xxx.ko` | 加载指定模块 |
| `rmmod xxx` | 卸载指定模块 |
| `modinfo xxx.ko` | 查看模块信息 |
| `dmesg` | 查看内核日志 |
| `dmesg -w` | 实时跟踪内核日志 |

注意：

`insmod` 后面通常跟 `.ko` 文件路径。

`rmmod` 后面通常跟模块名，不需要写 `.ko` 后缀。

## 6. hello_module 实验目录结构

建议创建如下实验目录：

```text
hello-module/
├── Makefile
└── hello_module.c
```

其中：

| 文件 | 作用 |
| --- | --- |
| `hello_module.c` | 模块源码 |
| `Makefile` | 调用内核构建系统编译模块 |

## 7. hello_module.c 示例

创建 `hello_module.c`：

```c
#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>

static int __init hello_module_init(void)
{
    printk(KERN_INFO "hello_module: init\n");
    return 0;
}

static void __exit hello_module_exit(void)
{
    printk(KERN_INFO "hello_module: exit\n");
}

module_init(hello_module_init);
module_exit(hello_module_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("training");
MODULE_DESCRIPTION("A simple hello Linux kernel module");
```

代码说明：

| 代码 | 说明 |
| --- | --- |
| `module_init()` | 指定模块加载时执行的函数 |
| `module_exit()` | 指定模块卸载时执行的函数 |
| `printk()` | 内核态打印函数，类似用户态的 `printf()` |
| `MODULE_LICENSE("GPL")` | 声明模块许可证，避免内核提示 tainted |
| `__init` | 表示初始化函数，加载后相关内存可能被释放 |
| `__exit` | 表示退出函数，只在模块卸载时使用 |

## 8. Makefile 示例

创建 `Makefile`：

```makefile
obj-m += hello_module.o

KDIR ?= /lib/modules/$(shell uname -r)/build
PWD := $(shell pwd)

all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
```

说明：

| 内容 | 说明 |
| --- | --- |
| `obj-m += hello_module.o` | 表示将 `hello_module.c` 编译成模块 |
| `KDIR` | 指向当前内核的构建目录 |
| `M=$(PWD)` | 告诉内核构建系统当前目录是外部模块目录 |
| `modules` | 编译外部模块 |
| `clean` | 清理编译产物 |

注意：

Makefile 命令行前面必须是 Tab，不能是普通空格。

## 9. 编译模块

在 `hello-module/` 目录下执行：

```bash
make
```

如果编译成功，目录下会出现类似文件：

```text
hello_module.ko
hello_module.o
hello_module.mod
hello_module.mod.c
Module.symvers
modules.order
```

其中最重要的是：

```text
hello_module.ko
```

它就是最终生成的内核模块文件。

## 10. 查看模块信息

执行：

```bash
modinfo hello_module.ko
```

可以看到模块的作者、描述、许可证、vermagic 等信息。

其中 `vermagic` 很重要，它用于描述该模块对应的内核版本信息。

如果模块编译时使用的内核版本与目标系统运行的内核版本不一致，加载时可能失败。

## 11. 加载模块

执行：

```bash
sudo insmod hello_module.ko
```

查看模块是否已经加载：

```bash
lsmod | grep hello_module
```

查看内核日志：

```bash
dmesg | tail
```

正常情况下可以看到类似输出：

```text
hello_module: init
```

## 12. 卸载模块

执行：

```bash
sudo rmmod hello_module
```

查看内核日志：

```bash
dmesg | tail
```

正常情况下可以看到类似输出：

```text
hello_module: exit
```

## 13. 实时观察日志

可以打开一个终端实时观察内核日志：

```bash
sudo dmesg -w
```

然后在另一个终端执行：

```bash
sudo insmod hello_module.ko
sudo rmmod hello_module
```

这样可以更直观地看到模块加载和卸载时触发的打印。

## 14. 常见错误

### 14.1 找不到内核构建目录

错误示例：

```text
/lib/modules/xxx/build: No such file or directory
```

原因：

当前系统没有安装对应版本的内核头文件或内核开发包。

解决思路：

1. 确认当前运行内核版本：

```bash
uname -r
```

2. 确认 `/lib/modules/$(uname -r)/build` 是否存在：

```bash
ls -l /lib/modules/$(uname -r)/build
```

3. 安装对应版本的 `kernel-devel` 或准备完整内核源码树。

### 14.2 模块版本不匹配

错误示例：

```text
invalid module format
```

常见原因：

1. 编译模块时使用的内核源码版本不对
2. 目标板运行的内核版本和编译环境不一致
3. `CONFIG_MODVERSIONS` 等配置不一致
4. 交叉编译工具链或架构设置不正确

排查命令：

```bash
uname -r
modinfo hello_module.ko
```

重点比较 `uname -r` 和 `modinfo` 里的 `vermagic`。

### 14.3 权限不足

错误示例：

```text
Operation not permitted
```

原因：

加载和卸载内核模块需要 root 权限。

解决：

```bash
sudo insmod hello_module.ko
sudo rmmod hello_module
```

### 14.4 模块正在被使用

错误示例：

```text
Module hello_module is in use
```

原因：

模块仍然被某些功能、设备或其他模块引用。

解决思路：

1. 查看模块使用情况：

```bash
lsmod | grep hello_module
```

2. 先停止依赖该模块的服务或卸载依赖模块。

## 15. 在交叉编译环境中编译模块

如果是在 x86 主机上为 ARM64 开发板编译模块，通常需要指定 `ARCH` 和 `CROSS_COMPILE`。

示例：

```bash
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- \
     KDIR=/path/to/kernel/build
```

其中：

| 参数 | 说明 |
| --- | --- |
| `ARCH=arm64` | 指定目标架构为 ARM64 |
| `CROSS_COMPILE=...` | 指定交叉编译工具链前缀 |
| `KDIR=...` | 指向目标内核对应的构建目录 |

注意：

外部模块必须匹配目标板正在运行的内核，而不是匹配编译主机的内核。

## 16. 与驱动开发的关系

`hello_module` 本身不是一个真正的设备驱动，它只是一个最小内核模块实验。

但是后续学习字符设备驱动、平台设备驱动、I2C 驱动、SPI 驱动、PCIe 驱动时，都会继续使用类似的基本结构：

1. 模块初始化函数
2. 模块退出函数
3. 内核日志打印
4. Makefile 调用内核构建系统
5. 编译生成 `.ko`
6. 加载、测试、卸载

所以，理解 `hello_module` 是后续学习 Linux 驱动开发的第一步。

## 17. 推荐练习

完成基础实验后，可以做以下练习：

1. 修改 `printk()` 打印内容，重新编译并加载模块
2. 使用 `modinfo` 查看模块信息
3. 故意修改 `MODULE_AUTHOR` 和 `MODULE_DESCRIPTION`
4. 使用 `dmesg -w` 实时观察模块加载和卸载
5. 尝试将模块复制到开发板上加载
6. 尝试在交叉编译环境下编译该模块

## 18. 小结

本文介绍了 Linux 内核模块的基本概念，并完成了一个最小 `hello_module` 实验。

需要重点掌握：

1. 内核模块最终产物是 `.ko`
2. `insmod` 用于加载模块
3. `rmmod` 用于卸载模块
4. `lsmod` 用于查看已加载模块
5. `modinfo` 用于查看模块信息
6. `printk()` 输出通过 `dmesg` 查看
7. 外部模块编译依赖目标内核的构建目录
8. 模块版本必须和目标系统运行的内核匹配

对于 Linux 驱动开发来说，内核模块是最基础的实验入口。先把模块的编译、加载、日志和卸载流程跑通，再继续学习具体设备驱动会更稳。
