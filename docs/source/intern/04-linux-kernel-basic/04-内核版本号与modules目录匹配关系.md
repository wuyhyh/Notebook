# 04-内核版本号与modules目录匹配关系

## 1. 文档目标

本文用于说明 Linux 内核版本号、模块版本信息和 `/lib/modules/<kernel-release>/` 目录之间的匹配关系。

学习完成后，应能够回答以下问题：

1. `uname -r` 显示的内核版本号从哪里来？
2. `/lib/modules/$(uname -r)/` 为什么这么重要？
3. 外部模块为什么必须匹配当前运行内核？
4. `modinfo` 中的 `vermagic` 是什么？
5. `modules_install` 会把模块安装到哪里？
6. 修改内核版本后，为什么模块目录也必须同步？
7. `invalid module format` 常见原因是什么？

## 2. 基本结论

Linux 内核模块必须和当前运行的内核版本匹配。

当前运行内核版本可以通过下面命令查看：

```bash
uname -r
```

模块目录通常是：

```bash
/lib/modules/$(uname -r)/
```

例如：

```text
5.10.0-136.12.0.86.aarch64
```

则对应模块目录是：

```text
/lib/modules/5.10.0-136.12.0.86.aarch64/
```

最重要的一句话是：

```text
当前运行内核的 uname -r，必须能在 /lib/modules/ 下找到同名目录。
```

如果找不到，就很容易出现模块加载、外部模块编译、驱动依赖等问题。

## 3. 为什么 /lib/modules/$(uname -r) 很重要

Linux 系统会根据当前运行内核的 release 字符串查找模块目录。

例如：

```bash
uname -r
```

输出：

```text
5.10.0-custom
```

那么系统默认会查找：

```text
/lib/modules/5.10.0-custom/
```

该目录中通常包含：

| 内容 | 说明 |
| --- | --- |
| `kernel/` | 内核自带模块 |
| `extra/` | 第三方或外部模块常用目录 |
| `build` | 指向内核构建目录 |
| `source` | 指向内核源码目录 |
| `modules.dep` | 模块依赖索引 |
| `modules.alias` | 模块别名索引 |
| `modules.symbols` | 模块符号索引 |
| `modules.order` | 模块顺序信息 |

很多工具都依赖这个目录，例如：

1. `modprobe`
2. `depmod`
3. 外部模块 Makefile
4. DKMS 类工具
5. 系统自动加载模块机制

如果这个目录缺失或名字不匹配，模块系统就会不正常。

## 4. uname -r 从哪里来

`uname -r` 显示的是当前运行内核的 release 字符串。

它通常由以下部分共同组成：

1. 内核主版本号
2. 补丁版本号
3. 发行版或厂商后缀
4. 本地版本后缀
5. 架构或发行版定制后缀

例如：

```text
5.10.0-136.12.0.86.aarch64
```

或者：

```text
5.10.0-baseline_2026Q1
```

内核源码中影响版本号的常见位置包括：

| 来源 | 说明 |
| --- | --- |
| 顶层 `Makefile` | 定义 `VERSION`、`PATCHLEVEL`、`SUBLEVEL`、`EXTRAVERSION` |
| `.config` | 可能包含 `CONFIG_LOCALVERSION` |
| 构建环境 | 可能启用自动 localversion |
| Git 状态 | 某些配置下可能追加 git 后缀 |
| 发行版补丁 | 可能修改版本生成规则 |

常见顶层 `Makefile` 片段类似：

```makefile
VERSION = 5
PATCHLEVEL = 10
SUBLEVEL = 0
EXTRAVERSION =
```

最终 release 不是只由这几行决定，还可能叠加 `LOCALVERSION` 等信息。

## 5. CONFIG_LOCALVERSION

`.config` 中可能存在：

```text
CONFIG_LOCALVERSION="-custom"
```

这会影响最终内核 release。

例如基础版本是：

```text
5.10.0
```

如果设置：

```text
CONFIG_LOCALVERSION="-custom"
```

则最终可能变成：

```text
5.10.0-custom
```

查看当前配置：

```bash
grep CONFIG_LOCALVERSION .config
```

如果使用独立构建目录：

```bash
grep CONFIG_LOCALVERSION build/.config
```

注意：

`CONFIG_LOCALVERSION` 一旦改变，`uname -r` 就会改变，对应 `/lib/modules/<release>/` 目录也会改变。

## 6. localversion 文件

内核源码树或构建目录中还可能存在类似文件：

```text
localversion
localversion-*
```

这些文件也可能影响最终内核 release。

例如文件内容为：

```text
-test
```

最终版本号可能追加：

```text
-test
```

可以检查：

```bash
find . -maxdepth 2 -name 'localversion*' -type f -print
```

如果使用 `O=build`，也要检查构建目录中是否有 localversion 文件。

## 7. CONFIG_LOCALVERSION_AUTO

有些内核配置中存在：

```text
CONFIG_LOCALVERSION_AUTO=y
```

在这种情况下，如果源码在 Git 仓库中，内核构建系统可能会根据 Git 状态追加类似后缀。

例如：

```text
-gabcdef123456
```

如果工作区有未提交修改，也可能追加额外标记。

这会导致一个问题：

同一份源码，不同构建状态下编译出来的内核 release 可能不同。

对于工程化交付，通常建议明确控制版本后缀，不要让版本字符串随机变化。

可以检查：

```bash
grep CONFIG_LOCALVERSION_AUTO .config
```

如果不希望自动追加 Git 后缀，可以考虑关闭：

```text
# CONFIG_LOCALVERSION_AUTO is not set
```

具体是否关闭，需要结合项目规范决定。

## 8. 查看内核构建得到的 release

在内核源码目录中，可以使用：

```bash
make kernelrelease
```

如果使用独立构建目录：

```bash
make O=build kernelrelease
```

如果是交叉编译：

```bash
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- O=build kernelrelease
```

这个命令可以显示当前配置下将要生成的内核 release。

它应该和目标系统启动后 `uname -r` 对应。

编译、安装模块前，建议先执行：

```bash
make O=build kernelrelease
```

确认版本字符串是否符合预期。

## 9. modules_install 安装到哪里

执行：

```bash
make O=build modules_install
```

默认会安装到当前系统的：

```text
/lib/modules/<kernel-release>/
```

如果指定目标 rootfs：

```bash
make O=build INSTALL_MOD_PATH=/mnt/rootfs modules_install
```

则会安装到：

```text
/mnt/rootfs/lib/modules/<kernel-release>/
```

其中 `<kernel-release>` 来自当前内核构建系统计算出的 release。

例如：

```bash
make O=build kernelrelease
```

输出：

```text
5.10.0-baseline_2026Q1
```

那么：

```bash
make O=build INSTALL_MOD_PATH=/mnt/rootfs modules_install
```

会安装到：

```text
/mnt/rootfs/lib/modules/5.10.0-baseline_2026Q1/
```

## 10. Image 与 modules 版本必须一致

部署内核时，不能只复制 `Image`，还要同步安装对应模块。

错误做法：

```bash
cp build/arch/arm64/boot/Image /mnt/rootfs/boot/Image
```

但没有更新：

```text
/mnt/rootfs/lib/modules/<kernel-release>/
```

这样系统可能能启动，但模块加载会出问题。

正确思路：

1. 编译内核镜像
2. 编译模块
3. 安装模块到目标 rootfs
4. 复制 Image
5. 复制 dtb
6. 启动后检查 `uname -r`
7. 检查 `/lib/modules/$(uname -r)/`

示例：

```bash
make O=build Image dtbs modules -j$(nproc)
make O=build INSTALL_MOD_PATH=/mnt/rootfs modules_install

cp build/arch/arm64/boot/Image /mnt/rootfs/boot/Image
cp build/arch/arm64/boot/dts/<vendor>/<board>.dtb /mnt/rootfs/boot/dtb/
```

## 11. 启动后必须检查

系统启动后，第一步检查：

```bash
uname -r
```

然后检查：

```bash
ls /lib/modules/$(uname -r)
```

如果目录不存在，说明当前运行内核和 rootfs 中的模块目录不匹配。

继续检查：

```bash
ls -l /lib/modules/$(uname -r)/build
ls -l /lib/modules/$(uname -r)/source
```

如果要编译外部模块，`build` 链接尤其重要。

## 12. modinfo vermagic

`modinfo` 可以查看模块中的版本匹配信息。

命令：

```bash
modinfo xxx.ko | grep vermagic
```

可能输出：

```text
vermagic:       5.10.0-baseline_2026Q1 SMP mod_unload aarch64
```

`vermagic` 通常包含：

1. 内核 release
2. SMP 配置
3. preempt 配置
4. mod_unload 配置
5. modversions 配置
6. 架构信息

其中最关键的是内核 release。

如果当前系统：

```bash
uname -r
```

输出：

```text
5.10.0-baseline_2026Q1
```

模块：

```bash
modinfo xxx.ko | grep vermagic
```

也显示：

```text
5.10.0-baseline_2026Q1
```

说明版本号部分至少是匹配的。

## 13. invalid module format

如果模块版本不匹配，加载时常见错误是：

```text
invalid module format
```

命令行可能显示：

```bash
insmod: ERROR: could not insert module xxx.ko: Invalid module format
```

此时必须看内核日志：

```bash
dmesg | tail -n 50
```

常见日志可能类似：

```text
xxx: version magic '5.10.0-old SMP mod_unload aarch64' should be '5.10.0-new SMP mod_unload aarch64'
```

这类错误说明：

```text
模块是给另一个内核编译的。
```

解决方法不是强制加载，而是用当前运行内核对应的源码、配置和构建目录重新编译模块。

## 14. 外部模块为什么依赖 /lib/modules/$(uname -r)/build

外部模块 Makefile 中经常写：

```makefile
KDIR ?= /lib/modules/$(shell uname -r)/build
```

含义是：

```text
使用当前运行内核对应的构建目录来编译模块。
```

编译命令通常是：

```bash
make -C $(KDIR) M=$(PWD) modules
```

如果 `/lib/modules/$(uname -r)/build` 不存在，会出现类似错误：

```text
No such file or directory
```

说明系统缺少当前内核对应的构建目录或 kernel-devel 包。

对于开发板来说，可以有几种处理方式：

1. 在开发板安装对应的 kernel-devel
2. 把完整内核构建目录放到开发板
3. 在主机交叉编译外部模块
4. 修正 `/lib/modules/<release>/build` 指向正确目录

## 15. build 和 source 链接

`/lib/modules/<release>/` 下常见两个链接：

```text
build
source
```

通常含义：

| 链接 | 含义 |
| --- | --- |
| `build` | 指向内核构建目录，包含 `.config`、生成头文件等 |
| `source` | 指向内核源码目录 |

有些情况下源码目录和构建目录相同。

如果使用 `O=build` 独立构建，则：

1. `source` 可能指向源码树
2. `build` 应该指向构建输出目录

外部模块更依赖 `build`，因为它需要：

1. `.config`
2. `Module.symvers`
3. 生成头文件
4. 架构相关生成文件
5. 内核构建系统状态

## 16. Module.symvers 的作用

`Module.symvers` 记录内核导出符号及其版本信息。

在启用 `CONFIG_MODVERSIONS` 时，它对外部模块非常重要。

常见作用：

1. 记录 `EXPORT_SYMBOL` 导出的符号
2. 记录符号 CRC
3. 帮助外部模块进行符号版本匹配
4. 避免模块调用不兼容的内核符号

如果外部模块依赖内核导出符号，而 `Module.symvers` 不匹配，可能出现：

```text
Unknown symbol
```

或者符号版本相关错误。

所以外部模块最好使用目标内核完整构建后的目录，而不是只有源码没有构建产物的目录。

## 17. 内核 release 不一致的常见场景

### 17.1 只换了 Image，没有换 modules

现象：

1. 系统能启动
2. `uname -r` 变了
3. `/lib/modules/$(uname -r)` 不存在
4. `modprobe` 找不到模块
5. 外部模块编译失败

排查：

```bash
uname -r
ls /lib/modules
ls /lib/modules/$(uname -r)
```

### 17.2 修改了 CONFIG_LOCALVERSION

现象：

1. 编译出的内核 release 改变
2. modules_install 安装到新目录
3. 旧脚本仍然复制旧目录或旧 Image
4. 版本混乱

排查：

```bash
grep CONFIG_LOCALVERSION build/.config
make O=build kernelrelease
```

### 17.3 打开了 CONFIG_LOCALVERSION_AUTO

现象：

1. 不同 Git 状态产生不同 release
2. 模块目录名字不稳定
3. 同一套脚本多次构建结果不同

排查：

```bash
grep CONFIG_LOCALVERSION_AUTO build/.config
make O=build kernelrelease
```

### 17.4 rootfs 中残留多个 modules 目录

现象：

```bash
ls /lib/modules
```

看到很多目录，但当前 `uname -r` 对应目录不存在或内容不完整。

排查：

```bash
uname -r
ls -lh /lib/modules
du -sh /lib/modules/*
```

### 17.5 使用了错误的 KDIR 编译外部模块

现象：

1. 外部模块能编译成功
2. 复制到目标板后加载失败
3. `vermagic` 和目标板 `uname -r` 不一致

排查：

```bash
uname -r
modinfo xxx.ko | grep vermagic
```

## 18. 推荐部署流程

推荐使用以下流程部署内核和模块。

### 18.1 编译前确认 release

```bash
make O=build kernelrelease
```

确认输出符合预期。

### 18.2 编译内核、设备树和模块

```bash
make O=build Image dtbs modules -j$(nproc)
```

### 18.3 安装模块到 rootfs

```bash
make O=build INSTALL_MOD_PATH=/mnt/rootfs modules_install
```

### 18.4 复制 Image 和 dtb

```bash
cp build/arch/arm64/boot/Image /mnt/rootfs/boot/Image
cp build/arch/arm64/boot/dts/<vendor>/<board>.dtb /mnt/rootfs/boot/dtb/
```

### 18.5 启动后检查

```bash
uname -r
ls /lib/modules/$(uname -r)
modprobe --show-depends <module_name>
```

如果涉及外部模块：

```bash
modinfo xxx.ko | grep vermagic
```

确认和 `uname -r` 一致。

## 19. 推荐版本命名习惯

为了减少混乱，建议项目中明确内核版本后缀。

例如：

```text
5.10.0-baseline_2026Q1
5.10.0-phytium_fusion_v1
5.10.0-oe136_boardtest
```

建议原则：

1. 版本后缀能体现来源或用途
2. 不要每次构建都随机变化
3. 不要使用太长且难以输入的后缀
4. `Image`、`dtb`、`modules` 要一起交付
5. 发布包中记录对应 Git commit
6. 发布包中记录 `.config`
7. 发布包中记录构建工具链

不建议：

```text
5.10.0-test
```

长期被反复覆盖使用，因为无法判断具体是哪一次构建。

## 20. 开发板排查命令清单

在开发板上遇到模块问题时，先执行：

```bash
uname -a
uname -r
cat /proc/version
cat /proc/cmdline
ls /lib/modules
ls /lib/modules/$(uname -r)
ls -l /lib/modules/$(uname -r)/build
```

查看模块信息：

```bash
modinfo xxx.ko
modinfo xxx.ko | grep vermagic
file xxx.ko
```

加载失败后查看：

```bash
dmesg | tail -n 100
dmesg | grep -i "vermagic\|module\|symbol\|format"
```

查看模块依赖：

```bash
modinfo xxx.ko | grep depends
```

查看模块索引：

```bash
ls /lib/modules/$(uname -r)/modules.dep
ls /lib/modules/$(uname -r)/modules.alias
```

必要时更新索引：

```bash
sudo depmod -a
```

## 21. 常见错误和对应判断

| 现象 | 常见原因 | 优先检查 |
| --- | --- | --- |
| `/lib/modules/$(uname -r)` 不存在 | 只换了 Image，没安装 modules | `uname -r`、`ls /lib/modules` |
| `invalid module format` | 模块和内核版本不匹配 | `modinfo vermagic`、`uname -r` |
| `Unknown symbol` | 依赖模块或符号版本不匹配 | `dmesg`、`Module.symvers`、`depends` |
| `modprobe: module not found` | 模块没安装到当前 release 目录 | `/lib/modules/$(uname -r)`、`depmod` |
| 外部模块无法编译 | build 链接不存在或错误 | `/lib/modules/$(uname -r)/build` |
| `probe` 没执行 | 模块可能加载了，但没匹配设备 | `dmesg`、`/sys/bus`、设备树 |

## 22. 不建议强制加载

有些情况下可以看到类似选项：

```bash
insmod --force xxx.ko
modprobe --force xxx
```

不建议使用。

原因：

1. 版本不匹配可能导致内核崩溃
2. 结构体布局可能已经变化
3. 符号语义可能不同
4. 问题会变得更隐蔽
5. 对文件系统、网络、存储驱动尤其危险

正确做法是重新编译匹配当前内核的模块。

## 23. 和 RPM 包的关系

如果使用 RPM 包安装内核，通常需要保证：

1. kernel 包安装 `Image` 或 `vmlinuz`
2. kernel-modules 包安装 `/lib/modules/<release>/`
3. kernel-devel 包提供外部模块编译所需的构建目录
4. 三者 release 必须一致

如果只安装 kernel，不安装 modules，系统可能能启动，但很多驱动模块不可用。

如果只安装 modules，不启动对应 kernel，也没有意义。

对于工程交付，应把以下内容作为同一版本成套管理：

1. 内核镜像
2. 设备树
3. 内核模块目录
4. kernel-devel 或构建目录
5. `.config`
6. System.map
7. 编译记录

## 24. 小结

本文介绍了 Linux 内核版本号和 modules 目录之间的关系。

需要重点掌握：

1. `uname -r` 表示当前运行内核的 release
2. 模块目录必须是 `/lib/modules/$(uname -r)/`
3. `modules_install` 会根据构建出的 release 安装模块
4. `CONFIG_LOCALVERSION` 会改变内核 release
5. `CONFIG_LOCALVERSION_AUTO` 可能导致 release 随 Git 状态变化
6. `make kernelrelease` 可以提前查看构建出的 release
7. `modinfo xxx.ko` 可以查看模块 `vermagic`
8. `vermagic` 必须和当前运行内核匹配
9. 外部模块依赖 `/lib/modules/$(uname -r)/build`
10. 部署内核时，`Image`、`dtb`、`modules` 必须同步

对内核开发来说，版本号不是表面字符串，而是内核、模块、构建目录、依赖索引之间的连接键。只要这个连接键错了，后面的模块加载和驱动调试都会变得混乱。
