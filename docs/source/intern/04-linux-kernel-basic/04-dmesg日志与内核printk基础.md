# 04-dmesg日志与内核printk基础

## 1. 文档目标

本文用于说明 Linux 内核日志的基本查看方法，以及内核代码中常用的 `printk()` 打印机制。

学习完成后，应能够回答以下问题：

1. `dmesg` 是什么？
2. 内核日志和普通应用程序日志有什么区别？
3. `printk()` 打印的信息在哪里查看？
4. `KERN_INFO`、`KERN_ERR`、`KERN_DEBUG` 分别是什么意思？
5. 调试驱动或内核模块时，应该如何查看日志？

## 2. 什么是 dmesg

`dmesg` 用于查看 Linux 内核环形缓冲区中的日志。

内核启动、驱动初始化、设备识别、中断异常、模块加载、模块卸载等信息，通常都会进入内核日志缓冲区。

常见场景包括：

1. 查看内核启动过程
2. 查看驱动是否加载成功
3. 查看设备识别信息
4. 查看内核模块打印
5. 查看 panic、oops、warning 等错误信息

例如：

```bash
dmesg
```

查看最近的内核日志：

```bash
dmesg | tail
```

实时跟踪内核日志：

```bash
dmesg -w
```

## 3. 内核日志和用户态日志的区别

普通用户态程序常用 `printf()`、日志文件或 systemd journal 输出日志。

内核代码不能直接使用用户态的 `printf()`。内核中常用的是：

```c
printk()
```

两者区别如下：

| 项目 | 用户态程序 | 内核代码 |
| --- | --- | --- |
| 常用打印函数 | `printf()` | `printk()` |
| 运行权限 | 用户态 | 内核态 |
| 查看方式 | 终端、日志文件、journalctl | `dmesg`、`journalctl -k` |
| 典型用途 | 应用程序调试 | 驱动、内核子系统调试 |

## 4. printk 基本用法

`printk()` 是内核中最常用的日志打印函数。

示例：

```c
printk(KERN_INFO "hello: init\n");
printk(KERN_ERR "hello: error happened\n");
```

其中：

| 部分 | 说明 |
| --- | --- |
| `printk` | 内核打印函数 |
| `KERN_INFO` | 日志等级 |
| `"hello: init\n"` | 实际打印内容 |

注意：

内核日志建议加上模块名或驱动名前缀，方便后续搜索。

例如：

```c
printk(KERN_INFO "hello_module: init\n");
```

比下面这种写法更容易排查问题：

```c
printk(KERN_INFO "init\n");
```

## 5. 常见 printk 日志等级

`printk()` 支持不同日志等级，用来区分信息的重要程度。

| 日志等级 | 含义 | 常见用途 |
| --- | --- | --- |
| `KERN_EMERG` | 系统不可用 | 极严重错误 |
| `KERN_ALERT` | 必须立即处理 | 严重系统问题 |
| `KERN_CRIT` | 临界错误 | 关键子系统故障 |
| `KERN_ERR` | 错误 | 驱动初始化失败、设备访问失败 |
| `KERN_WARNING` | 警告 | 异常但不一定致命 |
| `KERN_NOTICE` | 需要注意的信息 | 状态变化 |
| `KERN_INFO` | 普通信息 | 初始化成功、设备识别 |
| `KERN_DEBUG` | 调试信息 | 开发阶段调试 |

常用的主要是：

1. `KERN_ERR`
2. `KERN_WARNING`
3. `KERN_INFO`
4. `KERN_DEBUG`

## 6. 推荐使用 pr_xxx 系列接口

在较新的内核代码中，更常见的是使用 `pr_info()`、`pr_err()` 等封装接口。

示例：

```c
pr_info("hello_module: init\n");
pr_err("hello_module: failed to init\n");
pr_debug("hello_module: debug value=%d\n", value);
```

常见接口如下：

| 接口 | 大致等价 |
| --- | --- |
| `pr_emerg()` | `printk(KERN_EMERG ...)` |
| `pr_alert()` | `printk(KERN_ALERT ...)` |
| `pr_crit()` | `printk(KERN_CRIT ...)` |
| `pr_err()` | `printk(KERN_ERR ...)` |
| `pr_warn()` | `printk(KERN_WARNING ...)` |
| `pr_notice()` | `printk(KERN_NOTICE ...)` |
| `pr_info()` | `printk(KERN_INFO ...)` |
| `pr_debug()` | 调试日志 |

对于新写的普通内核代码，建议优先使用：

```c
pr_info()
pr_err()
pr_warn()
```

## 7. 驱动中常用的 dev_xxx 系列接口

在设备驱动中，如果已经有 `struct device *dev`，更推荐使用 `dev_info()`、`dev_err()` 等接口。

示例：

```c
dev_info(dev, "device initialized\n");
dev_err(dev, "failed to request irq\n");
```

相比 `printk()`，`dev_xxx()` 可以自动带上设备信息，更适合驱动开发。

常见接口：

| 接口 | 用途 |
| --- | --- |
| `dev_info()` | 普通设备信息 |
| `dev_err()` | 设备错误信息 |
| `dev_warn()` | 设备警告信息 |
| `dev_dbg()` | 设备调试信息 |

简单理解：

1. 写普通内核模块，可以先用 `pr_info()`、`pr_err()`
2. 写具体设备驱动，优先用 `dev_info()`、`dev_err()`
3. 阅读老代码时，经常会看到 `printk()`

## 8. dmesg 常用命令

查看全部内核日志：

```bash
dmesg
```

查看最近日志：

```bash
dmesg | tail
```

查看最近 50 行：

```bash
dmesg | tail -n 50
```

实时跟踪日志：

```bash
dmesg -w
```

显示更易读的时间格式：

```bash
dmesg -T
```

按关键字过滤：

```bash
dmesg | grep -i error
dmesg | grep -i eth
dmesg | grep -i usb
dmesg | grep -i nvme
```

查看错误、警告等信息：

```bash
dmesg | grep -i "fail\|error\|warn\|panic\|oops"
```

清空当前内核日志缓冲区：

```bash
sudo dmesg -C
```

注意：

`dmesg -C` 只清空当前缓冲区中的显示内容，不代表问题被解决。

## 9. journalctl 查看内核日志

如果系统使用 systemd，也可以使用 `journalctl` 查看内核日志。

查看本次启动的内核日志：

```bash
journalctl -k
```

实时跟踪内核日志：

```bash
journalctl -k -f
```

查看本次启动中的错误日志：

```bash
journalctl -k -p err
```

查看上一次启动的内核日志：

```bash
journalctl -k -b -1
```

说明：

| 命令 | 作用 |
| --- | --- |
| `journalctl -k` | 只查看内核日志 |
| `-f` | 实时跟踪 |
| `-p err` | 只看错误级别及以上日志 |
| `-b -1` | 查看上一次启动日志 |

如果系统启动后崩溃或重启，`journalctl -k -b -1` 很有用。

## 10. 查看启动阶段日志

内核启动阶段会打印大量硬件和驱动信息。

常用命令：

```bash
dmesg | less
```

搜索网卡相关信息：

```bash
dmesg | grep -i eth
```

搜索 PCIe 相关信息：

```bash
dmesg | grep -i pci
```

搜索设备树相关信息：

```bash
dmesg | grep -i "of\|dtb\|device tree"
```

搜索模块相关信息：

```bash
dmesg | grep -i module
```

在开发板调试中，启动日志非常重要。很多设备没有正常工作时，第一步不是改代码，而是先看启动日志里有没有识别到设备。

## 11. printk 与 hello_module 实验

在上一节 `hello_module` 中，如果代码为：

```c
static int __init hello_module_init(void)
{
    printk(KERN_INFO "hello_module: init\n");
    return 0;
}

static void __exit hello_module_exit(void)
{
    printk(KERN_INFO "hello_module: exit\n");
}
```

加载模块：

```bash
sudo insmod hello_module.ko
```

查看日志：

```bash
dmesg | tail
```

可以看到类似输出：

```text
hello_module: init
```

卸载模块：

```bash
sudo rmmod hello_module
```

再次查看日志：

```bash
dmesg | tail
```

可以看到类似输出：

```text
hello_module: exit
```

## 12. 日志等级与控制台显示

并不是所有 `printk()` 日志都会直接显示在串口控制台上。

是否显示到控制台，和内核的 console loglevel 有关。

查看当前 printk 日志等级：

```bash
cat /proc/sys/kernel/printk
```

可能看到类似内容：

```text
4 4 1 7
```

这几个数字分别表示当前控制台日志等级、默认消息等级、最低控制台日志等级、默认控制台日志等级。

简单理解：

1. 日志一定会进入内核日志缓冲区
2. 但不一定会直接显示到串口或控制台
3. 如果控制台看不到，可以先用 `dmesg` 查看
4. 调试早期启动问题时，可以通过启动参数调整日志输出

常用启动参数：

```text
loglevel=8 ignore_loglevel
```

含义：

| 参数 | 作用 |
| --- | --- |
| `loglevel=8` | 提高控制台输出等级 |
| `ignore_loglevel` | 尽量忽略日志等级限制，输出更多日志 |

## 13. 动态调试与 pr_debug

`pr_debug()` 默认不一定会输出日志。

这是因为调试日志可能非常多，如果全部打开，会影响性能和阅读。

对于初学者，先记住：

1. `pr_info()` 通常会输出
2. `pr_err()` 通常会输出
3. `pr_debug()` 可能不会输出
4. 如果要使用 `pr_debug()`，需要了解 dynamic debug 或相关内核配置

如果只是做入门实验，建议先使用：

```c
pr_info("message\n");
pr_err("error message\n");
```

不要一开始就依赖 `pr_debug()`。

## 14. 调试内核问题的基本方法

遇到内核或驱动问题时，建议按以下顺序看日志。

### 14.1 先看最近日志

```bash
dmesg | tail -n 100
```

### 14.2 再按关键字过滤

例如网卡问题：

```bash
dmesg | grep -i "eth\|phy\|stmmac\|link"
```

例如 NVMe 问题：

```bash
dmesg | grep -i "nvme\|pcie\|pci"
```

例如模块问题：

```bash
dmesg | grep -i "module\|invalid\|vermagic"
```

### 14.3 再查看完整启动日志

```bash
dmesg > dmesg.log
```

然后用编辑器搜索关键字。

### 14.4 如果系统已经重启

如果系统使用 systemd，可以查看上一次启动日志：

```bash
journalctl -k -b -1
```

## 15. 常见日志关键字

调试时可以重点关注以下关键字：

| 关键字 | 可能含义 |
| --- | --- |
| `error` | 错误 |
| `failed` | 操作失败 |
| `warning` | 警告 |
| `panic` | 内核严重错误 |
| `Oops` | 内核异常 |
| `BUG` | 内核检测到严重问题 |
| `timeout` | 等待超时 |
| `probe` | 驱动探测 |
| `deferred` | 驱动延迟探测 |
| `firmware` | 固件加载 |
| `irq` | 中断相关 |
| `dma` | DMA 相关 |
| `pci` | PCI/PCIe 相关 |
| `phy` | PHY 相关 |
| `link` | 链路状态相关 |

注意：

不要只看最后一行错误。很多真正的原因在更早的位置。

## 16. 写 printk 日志的建议

写内核日志时，建议遵守以下原则：

1. 日志要有明确前缀
2. 错误日志要说明失败原因
3. 不要在高频路径中大量打印
4. 不要打印过多无意义信息
5. 重要变量可以打印出来辅助判断
6. 日志等级要合理

不推荐：

```c
printk("error\n");
```

推荐：

```c
pr_err("hello_module: failed to allocate buffer, ret=%d\n", ret);
```

不推荐在中断处理函数、高频循环、网络收包路径中大量打印，否则可能导致系统变慢，甚至影响问题本身的表现。

## 17. 开发板调试建议

在开发板调试 Linux 内核时，建议保留以下信息：

1. 完整串口启动日志
2. `dmesg` 输出
3. 当前启动参数
4. 当前内核版本
5. 当前设备树文件
6. 当前加载的模块列表

常用命令：

```bash
uname -a
cat /proc/cmdline
lsmod
dmesg > dmesg.log
```

如果要向别人求助或提交问题，最好同时提供：

1. 问题现象
2. 复现步骤
3. 相关日志
4. 内核版本
5. 硬件平台
6. 最近修改过的代码或配置

## 18. 推荐练习

建议完成以下练习：

1. 在 `hello_module` 中加入一条 `printk(KERN_ERR ...)`
2. 将 `printk()` 改成 `pr_info()`
3. 使用 `dmesg -w` 实时观察模块加载和卸载
4. 使用 `dmesg | grep hello_module` 过滤模块日志
5. 使用 `cat /proc/sys/kernel/printk` 查看当前日志等级
6. 使用 `journalctl -k` 查看内核日志
7. 将 `dmesg` 保存成 `dmesg.log` 并用编辑器搜索关键字

## 19. 小结

本文介绍了 `dmesg` 和 `printk()` 的基础用法。

需要重点掌握：

1. `dmesg` 用于查看内核日志
2. `printk()` 是内核中的基础打印函数
3. `pr_info()`、`pr_err()` 是更常用的封装接口
4. 驱动中优先考虑使用 `dev_info()`、`dev_err()`
5. `printk()` 日志有不同等级
6. 日志进入内核缓冲区，不一定直接显示在控制台
7. `dmesg -w` 可以实时观察内核日志
8. `journalctl -k` 可以查看 systemd 保存的内核日志
9. 调试驱动问题时，日志是第一现场证据

对于内核和驱动开发来说，能否正确阅读日志，往往比直接改代码更重要。先看日志，再判断问题方向，是一种必须养成的基本习惯。
