# 04-内核模块加载卸载与modinfo

## 1. 文档目标

本文用于说明 Linux 内核模块的加载、卸载、查看和排查方法，重点理解 `insmod`、`rmmod`、`lsmod`、`modinfo`、`modprobe` 等常用命令。

学习完成后，应能够回答以下问题：

1. `.ko` 文件是什么？
2. 如何加载和卸载内核模块？
3. `insmod` 和 `modprobe` 有什么区别？
4. `lsmod` 能看到什么信息？
5. `modinfo` 中的 `vermagic` 有什么作用？
6. 模块加载失败时应该如何排查？
7. 为什么模块版本不匹配会出现 `invalid module format`？

## 2. 什么是内核模块

Linux 内核模块是一段可以动态加载到内核中的代码，常见后缀是：

```text
.ko
```

`.ko` 是 kernel object 的缩写。

内核模块常用于：

1. 设备驱动
2. 文件系统支持
3. 网络协议扩展
4. 调试功能
5. 特定硬件平台功能

模块的好处是：

1. 不需要重新编译整个内核
2. 可以按需加载
3. 可以在运行时卸载
4. 方便驱动开发和调试

但模块运行在内核态，错误代码可能导致系统崩溃，所以加载模块前必须确认来源和版本。

## 3. 模块和内核镜像的关系

Linux 内核功能通常有三种编译状态：

| 配置状态 | 含义 |
| --- | --- |
| `CONFIG_XXX=y` | 编译进内核镜像 |
| `CONFIG_XXX=m` | 编译成内核模块 |
| `# CONFIG_XXX is not set` | 不编译 |

如果某个驱动被编译进内核镜像，系统启动后它已经在内核中，不需要 `insmod`。

如果某个驱动被编译成模块，则最终会生成 `.ko` 文件，需要加载后才能使用。

## 4. 常用模块命令概览

| 命令 | 作用 |
| --- | --- |
| `lsmod` | 查看当前已经加载的模块 |
| `insmod xxx.ko` | 加载指定 `.ko` 文件 |
| `rmmod xxx` | 卸载指定模块 |
| `modinfo xxx.ko` | 查看模块信息 |
| `modprobe xxx` | 按模块名加载模块，并自动处理依赖 |
| `modprobe -r xxx` | 卸载模块，并处理依赖 |
| `depmod` | 生成模块依赖索引 |
| `dmesg` | 查看模块加载和卸载相关日志 |

## 5. 使用 lsmod 查看已加载模块

执行：

```bash
lsmod
```

输出示例：

```text
Module                  Size  Used by
hello_module           16384  0
```

字段说明：

| 字段 | 说明 |
| --- | --- |
| `Module` | 模块名称 |
| `Size` | 模块占用内存大小 |
| `Used by` | 被多少对象引用，以及被哪些模块依赖 |

查找某个模块：

```bash
lsmod | grep hello
```

注意：

`lsmod` 只能看到已经加载的模块，不能看到所有可用模块。

## 6. 使用 insmod 加载模块

`insmod` 用于加载指定路径的 `.ko` 文件。

示例：

```bash
sudo insmod hello_module.ko
```

加载后查看：

```bash
lsmod | grep hello_module
dmesg | tail -n 50
```

如果模块的初始化函数执行了，通常可以在 `dmesg` 中看到对应日志。

例如：

```text
hello_module: init
```

`insmod` 的特点：

1. 需要指定 `.ko` 文件路径
2. 不会自动查找模块
3. 不会自动加载依赖模块
4. 更适合开发阶段加载本地编译出来的模块

## 7. 使用 rmmod 卸载模块

`rmmod` 用于卸载已经加载的模块。

示例：

```bash
sudo rmmod hello_module
```

注意：

`rmmod` 后面通常写模块名，不写 `.ko` 后缀。

卸载后查看：

```bash
lsmod | grep hello_module
dmesg | tail -n 50
```

正常情况下可以看到模块退出日志：

```text
hello_module: exit
```

如果模块正在被使用，卸载可能失败。

## 8. 使用 modinfo 查看模块信息

`modinfo` 用于查看模块元信息。

示例：

```bash
modinfo hello_module.ko
```

可能输出：

```text
filename:       /path/to/hello_module.ko
description:    A simple hello Linux kernel module
author:         training
license:        GPL
vermagic:       5.10.0 SMP mod_unload aarch64
```

常见字段说明：

| 字段 | 说明 |
| --- | --- |
| `filename` | 模块文件路径 |
| `description` | 模块描述 |
| `author` | 作者 |
| `license` | 许可证 |
| `alias` | 模块别名，用于自动匹配 |
| `depends` | 依赖的其他模块 |
| `vermagic` | 模块编译时对应的内核版本和关键配置 |
| `parm` | 模块参数 |

其中最重要的是：

```text
vermagic
```

它常用于判断模块是否和当前运行内核匹配。

## 9. vermagic 是什么

`vermagic` 是模块中记录的一段版本匹配信息。

它通常包含：

1. 内核版本
2. SMP 信息
3. preempt 信息
4. mod_unload 信息
5. modversions 信息
6. 目标架构信息

查看当前内核版本：

```bash
uname -r
```

查看模块 `vermagic`：

```bash
modinfo hello_module.ko | grep vermagic
```

如果 `vermagic` 与当前运行内核不匹配，加载模块时可能出现：

```text
invalid module format
```

这说明模块不是针对当前运行内核编译的。

## 10. 使用 modprobe 加载模块

`modprobe` 按模块名加载模块，并会根据依赖关系自动加载其他模块。

示例：

```bash
sudo modprobe e1000e
```

与 `insmod` 不同，`modprobe` 通常不直接指定 `.ko` 路径，而是指定模块名。

`modprobe` 会在模块安装目录中查找模块：

```text
/lib/modules/$(uname -r)/
```

例如：

```bash
find /lib/modules/$(uname -r) -name '*.ko*'
```

`modprobe` 的特点：

1. 按模块名加载
2. 会自动处理依赖
3. 依赖 `/lib/modules/<kernel-release>/` 下的模块索引
4. 更适合系统正常运行环境
5. 不适合直接加载当前目录下的临时模块，除非模块已经安装到系统模块目录

## 11. insmod 和 modprobe 的区别

| 对比项 | `insmod` | `modprobe` |
| --- | --- | --- |
| 加载方式 | 指定 `.ko` 文件路径 | 指定模块名 |
| 是否自动处理依赖 | 不会 | 会 |
| 是否需要模块索引 | 不需要 | 需要 |
| 常见用途 | 开发调试本地模块 | 系统正常加载模块 |
| 查找路径 | 当前指定路径 | `/lib/modules/$(uname -r)/` |
| 失败常见原因 | 依赖缺失、版本不匹配 | 模块未安装、索引未更新 |

简单建议：

1. 开发阶段测试本地 `.ko`，用 `insmod`
2. 系统环境中加载已安装模块，用 `modprobe`
3. 有模块依赖关系时，优先考虑 `modprobe`

## 12. 使用 modprobe 卸载模块

卸载模块：

```bash
sudo modprobe -r <module_name>
```

例如：

```bash
sudo modprobe -r e1000e
```

相比 `rmmod`，`modprobe -r` 也会考虑依赖关系。

注意：

如果模块正在使用，仍然无法卸载。

## 13. depmod 的作用

`depmod` 用于扫描 `/lib/modules/<kernel-release>/` 下的模块，并生成模块依赖索引。

常见索引文件包括：

```text
modules.dep
modules.alias
modules.symbols
```

当你把新的 `.ko` 安装到系统模块目录后，通常需要执行：

```bash
sudo depmod -a
```

然后才能通过 `modprobe` 正常按模块名加载。

典型流程：

```bash
sudo cp hello_module.ko /lib/modules/$(uname -r)/extra/
sudo depmod -a
sudo modprobe hello_module
```

如果没有 `extra` 目录，可以创建：

```bash
sudo mkdir -p /lib/modules/$(uname -r)/extra
```

## 14. 模块安装目录

内核模块通常安装在：

```text
/lib/modules/<kernel-release>/
```

其中 `<kernel-release>` 对应：

```bash
uname -r
```

查看当前内核模块目录：

```bash
ls /lib/modules/$(uname -r)
```

常见内容：

| 文件或目录 | 说明 |
| --- | --- |
| `kernel/` | 内核自带模块 |
| `extra/` | 第三方或手动安装模块常用目录 |
| `build` | 指向内核构建目录 |
| `source` | 指向内核源码目录 |
| `modules.dep` | 模块依赖索引 |
| `modules.alias` | 模块别名索引 |

如果 `/lib/modules/$(uname -r)/build` 不存在，通常无法直接编译外部模块。

## 15. 模块参数

模块可以定义参数，在加载时传入。

示例代码中可能有：

```c
static int debug = 0;
module_param(debug, int, 0644);
MODULE_PARM_DESC(debug, "Enable debug output");
```

加载时传参：

```bash
sudo insmod demo.ko debug=1
```

或者：

```bash
sudo modprobe demo debug=1
```

查看模块参数：

```bash
ls /sys/module/demo/parameters
cat /sys/module/demo/parameters/debug
```

如果参数权限允许，也可以运行时修改：

```bash
echo 1 | sudo tee /sys/module/demo/parameters/debug
```

是否能修改取决于模块参数定义时的权限。

## 16. 查看模块依赖

使用 `modinfo` 查看依赖：

```bash
modinfo xxx.ko | grep depends
```

例如：

```text
depends:        libphy,phylink
```

如果使用 `insmod` 加载模块，而依赖模块没有提前加载，可能失败。

可以先加载依赖：

```bash
sudo modprobe libphy
sudo modprobe phylink
sudo insmod xxx.ko
```

或者把模块安装到 `/lib/modules/$(uname -r)/` 后，执行 `depmod -a`，再用 `modprobe` 加载。

## 17. 模块自动加载

很多驱动模块可以自动加载。

常见依据包括：

1. PCI Vendor ID / Device ID
2. USB Vendor ID / Product ID
3. Device Tree compatible
4. ACPI ID
5. 模块 alias 信息

这些信息通常由驱动中的 `MODULE_DEVICE_TABLE()` 导出。

例如设备树驱动中常见：

```c
MODULE_DEVICE_TABLE(of, demo_of_match);
```

PCI 驱动中常见：

```c
MODULE_DEVICE_TABLE(pci, demo_pci_ids);
```

自动加载依赖用户空间工具和模块别名索引。

所以如果希望模块能自动加载，通常需要：

1. 驱动中写正确的匹配表
2. 写 `MODULE_DEVICE_TABLE`
3. 模块安装到 `/lib/modules/$(uname -r)/`
4. 执行 `depmod -a`
5. 用户空间有对应的模块加载机制

## 18. 查看模块在 sysfs 中的信息

已加载模块通常可以在 `/sys/module` 下看到。

示例：

```bash
ls /sys/module/hello_module
```

常见内容：

| 路径 | 说明 |
| --- | --- |
| `/sys/module/<name>/parameters` | 模块参数 |
| `/sys/module/<name>/holders` | 依赖该模块的其他模块 |
| `/sys/module/<name>/refcnt` | 模块引用计数 |
| `/sys/module/<name>/sections` | 模块段信息 |
| `/sys/module/<name>/drivers` | 关联驱动 |

查看引用计数：

```bash
cat /sys/module/hello_module/refcnt
```

如果引用计数不为 0，模块可能无法卸载。

## 19. 模块加载失败的常见原因

### 19.1 invalid module format

错误示例：

```text
insmod: ERROR: could not insert module xxx.ko: Invalid module format
```

常见原因：

1. 模块编译时使用的内核版本不对
2. 目标板运行的内核和编译目录不一致
3. 架构不一致，例如 x86 模块拿到 ARM64 上加载
4. `CONFIG_MODVERSIONS` 等配置不一致
5. `LOCALVERSION` 或内核 release 不一致

排查命令：

```bash
uname -r
modinfo xxx.ko | grep vermagic
file xxx.ko
dmesg | tail -n 50
```

### 19.2 Unknown symbol

错误示例：

```text
Unknown symbol xxx
```

常见原因：

1. 依赖模块没有加载
2. 内核没有导出该符号
3. 模块编译环境和目标内核不一致
4. `Module.symvers` 不匹配
5. 外部模块依赖另一个外部模块，但没有正确提供符号表

排查命令：

```bash
dmesg | grep -i "unknown symbol"
modinfo xxx.ko | grep depends
cat /proc/kallsyms | grep <symbol_name>
```

### 19.3 No such device

错误示例：

```text
No such device
```

常见原因：

1. 驱动模块加载了，但没有对应硬件设备
2. 设备树节点不存在或 `compatible` 不匹配
3. PCIe/USB 设备没有枚举出来
4. 驱动初始化时发现硬件状态不符合预期

排查命令：

```bash
dmesg | tail -n 100
ls /sys/bus/platform/devices
ls /sys/bus/pci/devices
```

### 19.4 Operation not permitted

错误示例：

```text
Operation not permitted
```

常见原因：

1. 没有 root 权限
2. 系统启用了模块加载限制
3. Secure Boot 或内核签名策略限制
4. 内核配置禁止加载模块

排查思路：

```bash
whoami
sudo insmod xxx.ko
dmesg | tail -n 50
```

### 19.5 Module is in use

错误示例：

```text
rmmod: ERROR: Module xxx is in use
```

常见原因：

1. 模块被其他模块依赖
2. 设备正在使用
3. 文件节点还被进程打开
4. 网络接口还处于启用状态
5. 引用计数没有归零

排查命令：

```bash
lsmod | grep xxx
cat /sys/module/xxx/refcnt
ls /sys/module/xxx/holders
```

## 20. 查看内核日志

模块加载和卸载失败时，终端提示通常不够详细，必须看内核日志。

常用命令：

```bash
dmesg | tail -n 100
dmesg | grep -i "module\|symbol\|vermagic\|format\|taint"
journalctl -k -n 100
```

实时观察：

```bash
sudo dmesg -w
```

建议在一个终端执行：

```bash
sudo dmesg -w
```

另一个终端执行：

```bash
sudo insmod xxx.ko
```

这样可以第一时间看到内核给出的真实错误原因。

## 21. 内核 tainted 提示

加载某些模块后，内核可能出现 tainted 标记。

常见原因包括：

1. 加载了非 GPL 模块
2. 加载了闭源模块
3. 强制加载了不匹配模块
4. 内核发生过 warning、oops
5. 加载了 out-of-tree 模块

查看 tainted 状态：

```bash
cat /proc/sys/kernel/tainted
```

查看日志：

```bash
dmesg | grep -i taint
```

对于开发阶段来说，out-of-tree 模块导致 tainted 很常见，但如果是正式系统，需要认真评估影响。

## 22. 强制加载模块的风险

有些系统支持强制加载模块，例如：

```bash
sudo insmod --force xxx.ko
```

或：

```bash
sudo modprobe --force xxx
```

不建议这样做。

强制加载可能绕过版本检查，导致：

1. 内核崩溃
2. 数据损坏
3. 驱动异常
4. 难以复现的问题
5. 系统稳定性下降

正确做法是：

1. 使用目标系统对应的内核源码或构建目录
2. 使用一致的 `.config`
3. 使用一致的工具链
4. 重新编译模块
5. 确认 `vermagic` 匹配

## 23. 外部模块的标准编译流程

假设有外部模块目录：

```text
hello-module/
├── Makefile
└── hello_module.c
```

Makefile：

```makefile
obj-m += hello_module.o

KDIR ?= /lib/modules/$(shell uname -r)/build
PWD := $(shell pwd)

all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
```

编译：

```bash
make
```

加载：

```bash
sudo insmod hello_module.ko
```

查看：

```bash
lsmod | grep hello_module
dmesg | tail
```

卸载：

```bash
sudo rmmod hello_module
```

清理：

```bash
make clean
```

## 24. 交叉编译模块注意事项

如果在 x86 主机上为 ARM64 开发板编译模块，需要指定目标架构和交叉工具链。

示例：

```bash
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- \
     KDIR=/path/to/target/kernel/build
```

注意重点：

1. `ARCH` 必须是目标板架构
2. `CROSS_COMPILE` 必须是目标架构工具链
3. `KDIR` 必须对应目标板运行的内核
4. `.config` 必须和目标内核一致
5. `Module.symvers` 最好来自目标内核构建结果
6. 编译出来的 `.ko` 要复制到目标板加载

检查模块架构：

```bash
file xxx.ko
```

ARM64 模块应该显示类似：

```text
ELF 64-bit LSB relocatable, ARM aarch64
```

## 25. 开发板上的推荐检查流程

在目标开发板上加载模块前，建议先执行：

```bash
uname -r
ls -l /lib/modules/$(uname -r)/build
modinfo xxx.ko
file xxx.ko
```

加载时执行：

```bash
sudo dmesg -w
```

另一个终端执行：

```bash
sudo insmod xxx.ko
```

加载失败时重点看：

```bash
dmesg | tail -n 100
```

成功加载后查看：

```bash
lsmod | grep xxx
ls /sys/module/xxx
```

卸载前查看引用：

```bash
cat /sys/module/xxx/refcnt
ls /sys/module/xxx/holders
```

卸载：

```bash
sudo rmmod xxx
```

## 26. 常见排查清单

模块加载失败时，可以按以下顺序排查：

1. 当前内核版本：

```bash
uname -r
```

2. 模块版本信息：

```bash
modinfo xxx.ko | grep vermagic
```

3. 模块架构：

```bash
file xxx.ko
```

4. 内核日志：

```bash
dmesg | tail -n 100
```

5. 依赖模块：

```bash
modinfo xxx.ko | grep depends
```

6. 模块是否已经加载：

```bash
lsmod | grep xxx
```

7. 是否存在 `/lib/modules` 构建目录：

```bash
ls -l /lib/modules/$(uname -r)/build
```

8. 是否缺少符号：

```bash
dmesg | grep -i "unknown symbol"
```

9. 是否设备不存在：

```bash
dmesg | grep -i "no such device"
```

10. 是否模块正在使用：

```bash
cat /sys/module/xxx/refcnt
ls /sys/module/xxx/holders
```

## 27. insmod 本地调试示例

开发阶段常见流程：

```bash
make
sudo dmesg -C
sudo insmod hello_module.ko
dmesg | tail -n 50
lsmod | grep hello_module
sudo rmmod hello_module
dmesg | tail -n 50
```

其中：

| 命令 | 作用 |
| --- | --- |
| `make` | 编译模块 |
| `dmesg -C` | 清空当前日志缓冲区，方便观察新日志 |
| `insmod` | 加载模块 |
| `dmesg | tail` | 查看模块日志 |
| `lsmod` | 确认模块已加载 |
| `rmmod` | 卸载模块 |

注意：

`dmesg -C` 只是清空当前显示缓冲区，不代表问题被解决，也不建议在保存问题现场前随便执行。

## 28. modprobe 系统安装示例

如果希望模块通过 `modprobe` 加载，可以按以下流程：

```bash
sudo mkdir -p /lib/modules/$(uname -r)/extra
sudo cp hello_module.ko /lib/modules/$(uname -r)/extra/
sudo depmod -a
sudo modprobe hello_module
```

查看：

```bash
lsmod | grep hello_module
dmesg | tail -n 50
```

卸载：

```bash
sudo modprobe -r hello_module
```

这种方式更接近正式系统模块安装方式。

## 29. 推荐练习

建议完成以下练习：

1. 使用 `lsmod` 查看当前系统已加载模块
2. 使用 `modinfo` 查看一个系统模块的信息
3. 编译并加载 `hello_module.ko`
4. 使用 `dmesg -w` 实时观察模块加载和卸载日志
5. 使用 `modinfo hello_module.ko` 查看 `vermagic`
6. 比较 `uname -r` 和 `modinfo` 中的 `vermagic`
7. 使用 `rmmod` 卸载模块
8. 将模块复制到 `/lib/modules/$(uname -r)/extra/`
9. 执行 `depmod -a`
10. 使用 `modprobe` 加载模块
11. 故意使用不匹配内核版本的模块，观察 `invalid module format`
12. 查看 `/sys/module/<module_name>` 中的信息

## 30. 小结

本文介绍了 Linux 内核模块加载、卸载和查看信息的基础方法。

需要重点掌握：

1. `.ko` 是内核模块文件
2. `lsmod` 查看已加载模块
3. `insmod` 按路径加载模块
4. `rmmod` 按模块名卸载模块
5. `modinfo` 查看模块元信息
6. `vermagic` 用于判断模块和内核是否匹配
7. `modprobe` 按模块名加载，并自动处理依赖
8. `depmod` 用于生成模块依赖索引
9. 模块加载失败时必须查看 `dmesg`
10. 外部模块必须针对目标系统正在运行的内核编译

对于 Linux 驱动开发来说，模块加载和卸载是最基础的调试动作。不要只会写代码，还必须熟练掌握模块版本、依赖、日志和 sysfs 状态的排查方法。
