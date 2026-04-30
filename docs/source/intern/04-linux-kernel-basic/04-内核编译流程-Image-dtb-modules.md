# 04-内核编译流程-Image-dtb-modules

## 1. 文档目标

本文用于说明 Linux 内核从源码编译到生成启动产物的基本流程，重点理解三个核心结果：

1. `Image`：ARM64 平台常用的 Linux 内核镜像
2. `dtb`：设备树二进制文件，用于描述硬件信息
3. `modules`：内核模块，通常以 `.ko` 文件形式存在

掌握这部分内容后，应该能够理解：

1. 编译内核时常见的几个 `make` 目标分别做什么
2. 为什么只更新 `Image` 不一定能解决驱动问题
3. 为什么更新内核后还要同步 `/lib/modules/<kernel-release>`
4. `Image`、`dtb`、`rootfs`、`modules` 在启动过程中的关系

## 2. 内核编译的基本输入和输出

Linux 内核编译不是只生成一个文件。一次完整的内核构建通常涉及多个输入和多个输出。

常见输入包括：

| 输入 | 说明 |
| --- | --- |
| 内核源码 | Linux kernel 源码树 |
| `.config` | 当前内核配置文件 |
| 交叉编译工具链 | 例如 `aarch64-linux-gnu-` 或厂商提供的工具链 |
| 设备树源码 | 通常是 `.dts` 和 `.dtsi` 文件 |
| 构建命令参数 | 例如 `ARCH=arm64`、`CROSS_COMPILE=...` |

常见输出包括：

| 输出 | 说明 |
| --- | --- |
| `arch/arm64/boot/Image` | ARM64 内核镜像 |
| `arch/arm64/boot/dts/.../*.dtb` | 编译后的设备树文件 |
| `*.ko` | 内核模块文件 |
| `/lib/modules/<kernel-release>/` | 模块安装目录 |

## 3. `Image` 是什么

`Image` 是 ARM64 平台常见的 Linux 内核镜像文件。

它是内核核心代码编译、链接后的结果，包含：

1. 内核主体代码
2. 被配置为 `CONFIG_XXX=y` 的内核功能
3. 被配置为 `CONFIG_XXX=y` 的驱动
4. 启动早期需要的核心逻辑

在 ARM64 平台上，常见的内核镜像路径是：

```bash
arch/arm64/boot/Image
```

U-Boot 启动 Linux 时，经常会使用类似命令：

```bash
booti ${kernel_addr_r} - ${fdt_addr_r}
```

其中：

| 参数 | 含义 |
| --- | --- |
| `${kernel_addr_r}` | `Image` 加载到内存中的地址 |
| `-` | 表示没有单独提供 initramfs |
| `${fdt_addr_r}` | `dtb` 加载到内存中的地址 |

## 4. `dtb` 是什么

`dtb` 是 Device Tree Blob 的缩写，即设备树二进制文件。

Linux 内核本身不能自动知道板子上所有硬件的连接方式。设备树用于告诉内核：

1. CPU 信息
2. 内存范围
3. UART 控制器地址
4. 网卡控制器地址
5. I2C、SPI、GPIO 等外设信息
6. 中断号、时钟、复位、PHY 等硬件资源

设备树源码通常是：

```text
*.dts
*.dtsi
```

编译后生成：

```text
*.dtb
```

在 ARM64 内核源码中，设备树一般位于：

```bash
arch/arm64/boot/dts/
```

例如飞腾平台常见路径类似：

```bash
arch/arm64/boot/dts/phytium/
```

## 5. `modules` 是什么

内核模块是可以在内核运行时加载或卸载的代码，通常以 `.ko` 文件形式存在。

如果某个功能配置为：

```text
CONFIG_SAMPLE_DRIVER=m
```

那么它不会直接编译进 `Image`，而是会被编译成模块文件：

```text
sample_driver.ko
```

模块通常安装到 rootfs 的以下目录：

```bash
/lib/modules/<kernel-release>/
```

其中 `<kernel-release>` 可以通过目标系统上的命令查看：

```bash
uname -r
```

如果启动的 `Image` 版本和 `/lib/modules/<kernel-release>` 不匹配，就可能出现模块加载失败、驱动缺失、网络设备不可用等问题。

## 6. 常见编译命令

以内核源码根目录为例，ARM64 平台常见构建命令如下。

设置架构和交叉编译器：

```bash
export ARCH=arm64
export CROSS_COMPILE=aarch64-linux-gnu-
```

加载默认配置：

```bash
make defconfig
```

或者使用指定平台的配置：

```bash
make <board_defconfig>
```

进入菜单配置界面：

```bash
make menuconfig
```

编译内核镜像：

```bash
make Image -j$(nproc)
```

编译设备树：

```bash
make dtbs -j$(nproc)
```

编译内核模块：

```bash
make modules -j$(nproc)
```

一次性编译常见目标：

```bash
make Image dtbs modules -j$(nproc)
```

## 7. 使用独立输出目录编译

实际开发中，建议使用 `O=` 参数，把编译输出和源码目录分开。

示例：

```bash
make O=build ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- defconfig
make O=build ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- Image dtbs modules -j$(nproc)
```

使用 `O=build` 后，输出文件路径会变成：

```bash
build/arch/arm64/boot/Image
build/arch/arm64/boot/dts/.../*.dtb
```

这样做的好处是：

1. 源码目录更干净
2. 可以为不同配置准备不同构建目录
3. 便于清理和重新编译
4. 便于 IDE 索引和自动化脚本管理

## 8. 模块安装流程

模块编译完成后，一般需要安装到目标 rootfs 中。

如果目标 rootfs 挂载在 `/mnt/rootfs`，可以执行：

```bash
make O=build ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- \
    INSTALL_MOD_PATH=/mnt/rootfs modules_install
```

安装完成后，目标 rootfs 中会出现类似目录：

```bash
/mnt/rootfs/lib/modules/<kernel-release>/
```

这个目录里通常包含：

| 文件或目录 | 说明 |
| --- | --- |
| `kernel/` | 各子系统的 `.ko` 模块 |
| `modules.dep` | 模块依赖关系 |
| `modules.alias` | 模块别名信息 |
| `modules.builtin` | 编译进内核的模块记录 |
| `build` | 指向内核构建目录的链接 |
| `source` | 指向内核源码目录的链接 |

如果模块依赖信息异常，可以在目标系统上执行：

```bash
depmod -a
```

## 9. 部署到目标板时需要更新哪些文件

一次内核更新通常至少涉及三个部分：

| 文件 | 目标位置 | 说明 |
| --- | --- | --- |
| `Image` | `/boot/Image` 或 U-Boot 指定路径 | 内核镜像 |
| `*.dtb` | `/boot/dtb/` 或 U-Boot 指定路径 | 设备树 |
| modules | `/lib/modules/<kernel-release>/` | 内核模块 |

如果只修改了普通驱动代码，可能需要更新：

1. `Image`，如果驱动是 `CONFIG_XXX=y`
2. `/lib/modules/<kernel-release>/`，如果驱动是 `CONFIG_XXX=m`

如果只修改了设备树，需要更新：

1. 对应的 `.dtb`

如果修改了内核配置，通常需要重新编译并检查：

1. `Image`
2. `dtb`
3. modules
4. `/lib/modules/<kernel-release>` 是否匹配

## 10. `Image`、`dtb`、`modules` 的关系

可以把三者理解为：

| 组成 | 作用 |
| --- | --- |
| `Image` | 内核本体，负责启动 Linux 和运行核心逻辑 |
| `dtb` | 硬件说明书，告诉内核板子上有哪些设备和资源 |
| `modules` | 可动态加载的功能和驱动扩展 |

启动时，U-Boot 通常负责把 `Image` 和 `dtb` 加载到内存，然后跳转到内核入口。

内核启动后，会根据 `dtb` 发现硬件，并根据内核配置和模块情况加载对应驱动。

如果三者不匹配，常见现象包括：

1. 内核能启动，但某些设备不存在
2. 网卡、存储、USB 等设备驱动没有加载
3. `modprobe` 找不到模块
4. 模块版本不匹配
5. 设备树节点存在，但驱动没有 probe
6. 驱动存在，但设备树资源配置错误

## 11. 常见问题排查方向

### 11.1 驱动源码存在，但没有生效

优先检查：

1. 对应 `CONFIG_XXX` 是否启用
2. 是 `y` 还是 `m`
3. 对应 Makefile 是否包含该源码
4. 模块是否安装到 `/lib/modules/$(uname -r)/`
5. 设备树中是否有匹配节点
6. 驱动的 `compatible` 是否与设备树一致

### 11.2 更新了 `Image`，但驱动还是旧的

可能原因：

1. 驱动实际是模块形式，没有更新 `.ko`
2. `/lib/modules/<kernel-release>` 没有同步
3. 系统加载了旧模块
4. U-Boot 实际启动的不是刚更新的 `Image`

可以检查：

```bash
uname -a
modinfo <module_name>
ls /lib/modules/$(uname -r)/
```

### 11.3 更新了设备树，但硬件行为没变化

可能原因：

1. U-Boot 实际加载的不是新 `.dtb`
2. `/boot` 中有多个 dtb，更新错了文件
3. U-Boot 环境变量中指定了其他 dtb 路径
4. 内核启动过程中设备树被 U-Boot 修改过
5. 驱动并没有匹配到对应节点

可以在内核启动后查看：

```bash
ls /proc/device-tree/
cat /proc/device-tree/model
strings /sys/firmware/fdt | less
```

### 11.4 模块加载失败

常见原因：

1. 模块目录和当前内核版本不匹配
2. 模块依赖没有生成
3. 模块使用了当前内核没有导出的符号
4. 编译模块时使用的内核源码或配置不一致

可以检查：

```bash
uname -r
modprobe <module_name>
dmesg | tail -n 50
```

## 12. 推荐的基础编译流程

对于初学者，可以先记住以下流程：

```bash
export ARCH=arm64
export CROSS_COMPILE=aarch64-linux-gnu-

make O=build defconfig
make O=build menuconfig
make O=build Image dtbs modules -j$(nproc)
```

如果要安装模块到 rootfs：

```bash
make O=build INSTALL_MOD_PATH=/mnt/rootfs modules_install
```

然后部署：

```bash
cp build/arch/arm64/boot/Image /mnt/rootfs/boot/Image
cp build/arch/arm64/boot/dts/<vendor>/<board>.dtb /mnt/rootfs/boot/dtb/
```

最后在目标板启动后确认：

```bash
uname -a
ls /lib/modules/$(uname -r)/
dmesg | less
```

## 13. 实习生需要掌握的最低要求

学习完本文后，至少应该能够做到：

1. 知道 `Image`、`dtb`、`modules` 分别是什么
2. 会执行基本的 ARM64 内核编译命令
3. 知道模块需要安装到 `/lib/modules/<kernel-release>`
4. 知道更新设备树时要确认 U-Boot 实际加载的 dtb
5. 遇到驱动没有生效时，能从配置、Makefile、dtb、模块目录四个方向排查

## 14. 小结

Linux 内核编译流程不能只理解为“生成一个内核文件”。

在 ARM64 板级开发中，最核心的三个产物是：

1. `Image`：内核本体
2. `dtb`：硬件描述
3. `modules`：可动态加载的驱动和功能

实际调试时，很多问题都不是单纯的代码错误，而是 `Image`、`dtb`、`modules` 三者没有同步更新，或者 U-Boot 实际启动的文件不是开发者以为的那个文件。

因此，每次更新内核时，都应该明确记录：

1. 本次更新了哪个 `Image`
2. 本次更新了哪个 `dtb`
3. 本次更新了哪个 `/lib/modules/<kernel-release>`
4. U-Boot 实际加载的是哪一组启动文件
