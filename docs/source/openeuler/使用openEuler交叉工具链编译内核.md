# 使用 openEuler 交叉工具链编译内核

## 1. 场景与目标

* 宿主机：WSL Ubuntu 24.04（x86_64）
* 目标：在 WSL 上使用从 oebuild/Yocto 提取的 **Phytium OpenEuler 交叉工具链**，为 D2000 板子交叉编译
  `openEuler-5.10.0-216` 内核（带飞腾补丁）。
* 要求：

    * 工具链安装在普通用户可写目录
    * 内核编译不依赖板子本机，全部在 WSL 完成
    * 避免之前遇到的权限、GCC 插件和 `menuconfig` 相关错误

---

## 2. 从 oebuild 工程获取交叉工具链

交叉编译工具链已经安装到 `$HOME/toolchains/phytium-24.03` 目录：

目录结构大致如下：

```bash
ls $HOME/toolchains/phytium-24.03
# environment-setup-armv8a-openeuler-linux
# site-config-armv8a-openeuler-linux
# sysroots/
# version-armv8a-openeuler-linux
```

这一套就是可移植的交叉编译工具链。

## 3. 宿主机（WSL）依赖安装

内核编译会用到一些 **host 工具**（`menuconfig` / `fixdep` / `genksyms` 等），这些用的是 **x86_64 本机的 gcc 和库**
，跟交叉工具链无关。

在 WSL 里安装依赖：

```bash
sudo apt update
sudo apt install -y \
    build-essential \
    libncurses-dev \
    bison flex \
    libssl-dev \
    libelf-dev \
    dwarves
# 如要使用 GCC 插件，还需要：
# sudo apt install -y libgmp-dev libmpfr-dev libmpc-dev
```

解决的问题：

* 之前 `make menuconfig` 报 `cannot find libncursesw.so.5` 就是没装 `libncurses-dev`。
* GCC 插件报 `fatal error: gmp.h: No such file or directory` 是缺 `libgmp-dev`。

---

## 4. 正确配置交叉编译环境

### 4.1 不再 `source environment-setup`（重要）

我们总结下来：
**编内核时不需要 Yocto 的 sysroot，只需要交叉 gcc/binutils。**

`environment-setup` 会注入大量 `--sysroot=.../armv8a-openeuler-linux` 和 `-L .../sysroots/.../usr/lib64`，污染 host
工具的链接过程，导致：

* `ld` 先去找 aarch64 的 `libtinfo.so`、`libcrypto.so`，报 `skipping incompatible ...`；
* 再找不到宿主机版本的 `libncursesw.so.5` 时直接失败。

因此我们采用更干净的方式：只改 PATH 和 `CROSS_COMPILE`。

### 4.2 在新 shell 中设置环境

每次编内核时，**新开一个 shell**，执行：

```bash
# 交叉工具链根目录
export TOOLCHAIN=$HOME/toolchains/phytium-24.03

# 只把交叉编译器的 bin 目录加到 PATH
export PATH=$TOOLCHAIN/sysroots/x86_64-openeulersdk-linux/usr/bin:$PATH

# 只设置 CROSS_COMPILE 前缀
export CROSS_COMPILE=aarch64-openeuler-linux-
```

检查：

```bash
which aarch64-openeuler-linux-gcc
aarch64-openeuler-linux-gcc --version
```

确认找到的是 SDK 里的 aarch64 交叉 gcc。

> 如果以后你要在同一 shell 里去用 Yocto sysroot 编用户态应用，可以另外再 `source environment-setup`，但**编内核的那个
shell 尽量保持干净**。

---

## 5. 内核源码准备

假设源码目录为：

```bash
cd ~/openEuler-5.10.0-216-src
```

### 5.1 权限修正

如果源码是从 root 环境拷贝过来的，先修正属主：

```bash
sudo chown -R wuyuhang:wuyuhang ~/openEuler-5.10.0-216-src
```

避免 `unlink include/generated/autoconf.h: Permission denied` 之类错误。

### 5.2 导入/合并好的 `.config`

你前面从服务器 ISO 中“榨取”了 `.config`，然后和 BSP 的 `defconfig` 做了 merge。把最终确认可用的 `.config` 放到源码根目录：

```bash
cp ~/somewhere/your-merged.config .config
```

### 5.3 补齐新选项并关闭不需要的 GCC 插件

补全新 Kconfig 选项，全部采用默认值（通常是 N）

```bash
make ARCH=arm64 olddefconfig
```

如果想再检查一下：

```bash
make ARCH=arm64 menuconfig
```

在 `General setup` 里面把 `GCC plugins` 整体关闭。
之前你把 `GCC_PLUGINS` 和 `RANDOMIZE_LAYOUT`、`LATENT_ENTROPY` 等都开了，又没装 `libgmp-dev`，导致 gcc 插件编译阶段失败。

---

## 6. 编译内核

在刚才设置好环境的 shell 里、源码根目录下：

配置已经 done 的情况下，直接编译：

```bash
make -j$(nproc) ARCH=arm64 CROSS_COMPILE=aarch64-openeuler-linux-
```

如果中间想改配置：

```bash
make ARCH=arm64 menuconfig
make -j$(nproc) ARCH=arm64 CROSS_COMPILE=aarch64-openeuler-linux-
```

编译成功后，会得到：

* `arch/arm64/boot/Image`
* 对应的 `modules` 安装目录（后续你用之前的打包流程，复制到 chroot / p2 分区的 `/lib/modules/$KREL`）

