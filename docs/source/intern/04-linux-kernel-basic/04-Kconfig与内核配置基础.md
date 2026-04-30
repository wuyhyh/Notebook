# 04-Kconfig与内核配置基础

## 1. 文档目标

Linux 内核不是一次性把所有源码都编译进去，而是通过配置系统选择需要启用的功能、驱动和子系统。

学习 Kconfig 与内核配置，主要是为了理解以下问题：

1. 为什么有些驱动源码存在，但最终没有被编译？
2. `CONFIG_XXX=y`、`CONFIG_XXX=m`、`CONFIG_XXX is not set` 分别是什么意思？
3. `make menuconfig` 修改的内容最终保存在哪里？
4. `defconfig`、`.config`、`Kconfig`、`Makefile` 之间是什么关系？
5. 移植内核或打开某个驱动时，应该修改哪里？

这部分知识是阅读 Linux 内核源码、裁剪系统、打开驱动、制作内核 RPM 或调试 BSP 差异时的基础。

## 2. 内核配置系统的基本概念

Linux 内核源码中包含大量功能模块，例如：

1. CPU 架构支持
2. 文件系统
3. 网络协议栈
4. 设备驱动
5. 调试功能
6. 安全机制
7. 电源管理

不同产品不需要启用全部功能。例如服务器、嵌入式板卡、手机、路由器所需的内核功能差异很大。

因此 Linux 内核使用一套配置系统来决定：

1. 哪些功能启用
2. 哪些功能关闭
3. 哪些驱动编译进内核镜像
4. 哪些驱动编译成内核模块
5. 哪些源码文件参与编译

这套系统的核心由三类文件配合完成：

| 文件 | 作用 |
| --- | --- |
| `Kconfig` | 定义配置选项以及选项之间的依赖关系 |
| `.config` | 当前内核构建所使用的最终配置结果 |
| `Makefile` | 根据配置结果决定哪些源码参与编译 |

## 3. `CONFIG_XXX` 的三种常见状态

内核配置项通常以 `CONFIG_` 开头，例如：

```text
CONFIG_EXT4_FS=y
CONFIG_E1000E=m
# CONFIG_DEBUG_INFO is not set
```

常见状态如下：

| 状态 | 含义 |
| --- | --- |
| `CONFIG_XXX=y` | 启用该功能，并编译进内核镜像 |
| `CONFIG_XXX=m` | 启用该功能，但编译成内核模块 `.ko` |
| `# CONFIG_XXX is not set` | 不启用该功能 |

其中 `y` 和 `m` 的区别非常重要：

1. `y` 表示功能直接编译进内核镜像，例如 `Image` 或 `vmlinux`
2. `m` 表示功能单独编译成模块文件，通常位于 `/lib/modules/<kernel-version>/`
3. 没有启用的功能不会被编译，也不会出现在最终系统中

例如某个网卡驱动配置为 `m`，则系统启动后需要加载对应 `.ko` 模块，该网卡驱动才会工作。

## 4. Kconfig 的作用

`Kconfig` 文件用于描述内核配置菜单和配置项。

一个简单的 Kconfig 配置项可能类似这样：

```text
config SAMPLE_DRIVER
    tristate "Sample driver support"
    depends on PCI
    help
      This is a sample driver.
```

它表达的意思是：

1. 定义了一个配置项 `CONFIG_SAMPLE_DRIVER`
2. 这个配置项可以选择 `y`、`m` 或 `n`
3. 这个选项依赖 `PCI`
4. 在配置菜单中显示为 `Sample driver support`
5. `help` 用于说明该选项的用途

常见字段说明如下：

| 字段 | 说明 |
| --- | --- |
| `config` | 定义一个配置项 |
| `bool` | 该选项只能选择启用或关闭，即 `y` 或 `n` |
| `tristate` | 该选项可以选择 `y`、`m` 或 `n` |
| `depends on` | 表示该选项依赖其他配置项 |
| `select` | 当前选项启用时，强制选择另一个选项 |
| `default` | 默认值 |
| `help` | 帮助说明文本 |

## 5. `bool` 与 `tristate` 的区别

`bool` 表示二选一：

```text
config SMP
    bool "Symmetric multi-processing support"
```

它通常只能是：

```text
CONFIG_SMP=y
# CONFIG_SMP is not set
```

`tristate` 表示三选一：

```text
config E1000E
    tristate "Intel(R) PRO/1000 PCI-Express Gigabit Ethernet support"
```

它通常可以是：

```text
CONFIG_E1000E=y
CONFIG_E1000E=m
# CONFIG_E1000E is not set
```

一般来说：

1. 子系统核心功能常用 `bool`
2. 设备驱动常用 `tristate`
3. 能否编译成模块，取决于该配置项是否支持 `tristate`

## 6. `.config` 的作用

`.config` 是内核当前构建使用的最终配置文件。

它一般位于内核源码根目录或构建输出目录中，例如：

```bash
.config
```

如果使用独立构建目录：

```bash
make O=build menuconfig
```

则 `.config` 位于：

```bash
build/.config
```

`.config` 是由配置工具生成的结果文件，通常不建议手工大量编辑。

常见操作包括：

```bash
make menuconfig
make oldconfig
make defconfig
make savedefconfig
```

这些命令都会围绕 `.config` 进行处理。

## 7. `defconfig` 的作用

`defconfig` 是一份默认配置模板。

不同架构、不同开发板、不同发行版，通常会准备自己的默认配置。

例如 ARM64 架构中常见位置为：

```text
arch/arm64/configs/defconfig
```

某些厂商 BSP 可能提供自己的板级配置，例如：

```text
arch/arm64/configs/vendor_board_defconfig
```

使用方式示例：

```bash
make ARCH=arm64 defconfig
```

或者：

```bash
make ARCH=arm64 vendor_board_defconfig
```

执行后，内核构建系统会根据对应的 `defconfig` 生成当前构建使用的 `.config`。

需要注意：

1. `defconfig` 通常不是完整配置
2. `.config` 通常是完整配置
3. `defconfig` 更适合作为版本库中保存的基础配置
4. `.config` 更像是一次构建时展开后的完整结果

## 8. `menuconfig` 的作用

`menuconfig` 是一个基于终端菜单的配置界面。

常用命令：

```bash
make ARCH=arm64 menuconfig
```

如果使用独立构建目录：

```bash
make ARCH=arm64 O=build menuconfig
```

在 `menuconfig` 中可以：

1. 搜索配置项
2. 查看依赖关系
3. 启用或关闭功能
4. 将驱动设置为内建或模块
5. 保存修改后的 `.config`

在菜单界面中，常见符号含义如下：

| 符号 | 含义 |
| --- | --- |
| `[*]` | 功能已启用，通常表示 `y` |
| `[ ]` | 功能未启用 |
| `<*>` | 驱动编译进内核，表示 `y` |
| `<M>` | 驱动编译成模块，表示 `m` |
| `< >` | 驱动未启用 |

在 `menuconfig` 中按 `/` 可以搜索配置项。

例如搜索：

```text
DWMAC_PHYTIUM
```

可以看到该配置项的定义位置、依赖关系和当前状态。

## 9. Kconfig 与 Makefile 的配合关系

Kconfig 决定配置项是否启用，Makefile 决定启用后编译哪些文件。

例如某个驱动目录中的 Makefile 可能包含：

```makefile
obj-$(CONFIG_SAMPLE_DRIVER) += sample_driver.o
```

如果配置为：

```text
CONFIG_SAMPLE_DRIVER=y
```

则 `sample_driver.o` 会被编译进内核镜像。

如果配置为：

```text
CONFIG_SAMPLE_DRIVER=m
```

则 `sample_driver.o` 会被编译成模块。

如果配置为：

```text
# CONFIG_SAMPLE_DRIVER is not set
```

则该源码文件不会参与编译。

这就是为什么有些 `.c` 文件虽然存在于源码树中，但最终并没有被编译。

## 10. 新增驱动时通常需要修改什么

如果向内核中添加一个新驱动，通常至少需要修改三个地方：

1. 添加源码文件，例如 `sample_driver.c`
2. 修改当前目录的 `Makefile`
3. 修改当前目录或上级目录的 `Kconfig`

示例目录：

```text
drivers/example/
├── Kconfig
├── Makefile
└── sample_driver.c
```

Makefile 示例：

```makefile
obj-$(CONFIG_SAMPLE_DRIVER) += sample_driver.o
```

Kconfig 示例：

```text
config SAMPLE_DRIVER
    tristate "Sample driver support"
    depends on PCI
    help
      Enable sample driver support.
```

如果这个目录是新加的，还需要确认上级目录是否包含：

```text
source "drivers/example/Kconfig"
```

以及上级 Makefile 是否包含：

```makefile
obj-y += example/
```

否则即使写了 Kconfig 和 Makefile，也可能不会进入配置菜单或不会参与编译。

## 11. 常用配置命令

常用命令如下：

| 命令 | 作用 |
| --- | --- |
| `make defconfig` | 生成默认 `.config` |
| `make menuconfig` | 进入菜单式配置界面 |
| `make oldconfig` | 基于已有 `.config` 补全新增配置项 |
| `make olddefconfig` | 使用默认值自动补全新增配置项 |
| `make savedefconfig` | 从当前 `.config` 生成精简 `defconfig` |
| `make mrproper` | 深度清理源码树，包括 `.config` 等文件 |

ARM64 交叉编译中常见写法：

```bash
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- defconfig
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- menuconfig
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- Image modules dtbs
```

使用独立构建目录时：

```bash
make ARCH=arm64 O=build defconfig
make ARCH=arm64 O=build menuconfig
make ARCH=arm64 O=build Image modules dtbs
```

建议在实际项目中优先使用 `O=build`，这样源码目录更干净。

## 12. 如何查找一个配置项

如果知道配置项名称，可以使用 grep：

```bash
grep -R "config DWMAC_PHYTIUM" -n .
```

如果只知道部分名称：

```bash
grep -R "DWMAC" -n drivers/ arch/arm64/
```

如果想知道某个 `CONFIG_XXX` 被哪些 Makefile 使用：

```bash
grep -R "CONFIG_DWMAC_PHYTIUM" -n .
```

在 `menuconfig` 中也可以按 `/` 搜索配置项，通常会显示：

1. 配置项名称
2. 菜单路径
3. 依赖关系
4. 当前状态
5. 定义位置

这是定位驱动配置问题非常常用的方法。

## 13. 常见问题一：源码存在但没有编译

如果发现某个驱动源码存在，但最终没有生成 `.o` 或 `.ko`，常见原因包括：

1. 对应的 `CONFIG_XXX` 没有启用
2. 配置项依赖条件不满足
3. Makefile 没有把该源码加入编译
4. 上级目录没有递归进入该目录
5. 使用了错误的 `.config`
6. 构建目录和源码目录混淆

排查思路：

```bash
grep CONFIG_SAMPLE_DRIVER build/.config
```

查看是否启用：

```text
CONFIG_SAMPLE_DRIVER=y
```

再查看 Makefile：

```bash
grep -R "CONFIG_SAMPLE_DRIVER" -n drivers/
```

确认是否存在类似：

```makefile
obj-$(CONFIG_SAMPLE_DRIVER) += sample_driver.o
```

## 14. 常见问题二：配置项在 menuconfig 中找不到

如果某个配置项在 `menuconfig` 中找不到，常见原因包括：

1. 当前架构不支持该选项
2. 依赖条件不满足，被隐藏了
3. 对应 Kconfig 没有被上级 Kconfig `source`
4. 搜索的配置项名称写错
5. 当前源码版本中没有该配置项

可以先使用：

```bash
grep -R "config SAMPLE_DRIVER" -n .
```

如果能找到定义，再检查它的依赖：

```text
depends on PCI && NETDEVICES
```

如果依赖没有启用，该配置项可能不会出现在菜单中，或者无法选择。

## 15. 常见问题三：改了配置但没有生效

配置没有生效时，常见原因包括：

1. 修改的是源码根目录 `.config`，但实际构建使用的是 `O=build/.config`
2. 修改了 `defconfig`，但没有重新生成 `.config`
3. 修改了 `.config`，但后续又被 `make defconfig` 覆盖
4. 内核镜像更新了，但设备仍然启动旧内核
5. 模块更新了，但 `/lib/modules/<kernel-version>/` 中仍然是旧模块
6. 内核版本号没有变化，导致加载了旧模块

排查时要确认三件事：

1. 当前构建使用的是哪一份 `.config`
2. 当前启动的是哪一个内核镜像
3. 当前系统加载的是哪一套模块目录

常用检查命令：

```bash
uname -a
ls /lib/modules/
cat /proc/config.gz 2>/dev/null | zcat | grep CONFIG_SAMPLE_DRIVER
```

如果内核没有启用 `/proc/config.gz`，则最后一条命令可能不可用。

## 16. 实际项目中的建议

在实际 BSP、驱动移植和内核裁剪中，建议遵循以下原则：

1. 不要只改源码，要同时检查 Kconfig 和 Makefile
2. 不要随意手工维护一份巨大的 `.config`
3. 重要配置变更要记录原因
4. 修改配置后要保存对应的 defconfig 或配置补丁
5. 使用 `O=build` 保持源码目录干净
6. 对比两个内核差异时，要同时比较源码差异和配置差异

配置差异经常会导致非常大的行为差异。

例如同一份驱动源码，在一个内核中工作，在另一个内核中不工作，原因可能不是源码不同，而是：

1. PHY 驱动没有启用
2. PCI 支持没有启用完整
3. DMA、IOMMU、PM、ACPI、Device Tree 相关配置不同
4. 某些调试或安全配置影响了运行行为

所以调试内核问题时，`.config` 是必须检查的关键文件。

## 17. 小结

Kconfig 与内核配置系统可以理解为 Linux 内核的“功能选择系统”。

核心关系如下：

```text
Kconfig 定义有哪些选项
        ↓
menuconfig/defconfig 生成配置结果
        ↓
.config 保存最终配置
        ↓
Makefile 根据 CONFIG_XXX 决定编译哪些源码
        ↓
生成内核镜像和内核模块
```

掌握这套关系后，再阅读内核源码时就能理解：

1. 一个驱动为什么会出现在配置菜单中
2. 一个 `.c` 文件为什么会或不会参与编译
3. 一个功能为什么可以编译进内核或编译成模块
4. 移植驱动时为什么不能只复制 `.c` 文件
5. 调试内核差异时为什么必须比较 `.config`

对于刚开始学习内核的实习生来说，这篇文档的目标不是记住所有 Kconfig 语法，而是建立一个基本判断：

源码是否生效，不只取决于源码是否存在，还取决于配置系统是否把它选中并交给 Makefile 编译。
