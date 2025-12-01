# OpenEuler 交叉工具链

## 1. 场景与目标

* 宿主机：WSL Ubuntu 24.04（x86_64）
* 目标：在 WSL 上使用从 oebuild/Yocto 提取的 **Phytium OpenEuler 交叉工具链**，为 D2000 板子交叉编译 `openEuler-5.10.0-216` 内核（带飞腾补丁）。
* 要求：

    * 工具链安装在普通用户可写目录
    * 内核编译不依赖板子本机，全部在 WSL 完成
    * 避免之前遇到的权限、GCC 插件和 `menuconfig` 相关错误

---

## 2. 从 oebuild 工程获取交叉工具链

在 oebuild 环境下，飞腾给的 Yocto 工程一般会提供 SDK 安装脚本，例如：

```bash
openeuler-glibc-x86_64-openeuler-image-armv8a-phytium-toolchain-24.03-LTS.sh
```

### 2.1 在 WSL 中准备目录

```bash
mkdir -p $HOME/toolchains/phytium-24.03
cd ~/phytium-sdk   # 假设你把 .sh 拷到了这个目录
```

### 2.2 安装 SDK 到用户目录（关键：不用 sudo）

```bash
./openeuler-glibc-x86_64-openeuler-image-armv8a-phytium-toolchain-24.03-LTS.sh \
    -d $HOME/toolchains/phytium-24.03 -y
```

注意点：

* 一开始你装到 `/opt/phytium-sdk` 并用 `sudo`，导致目录属主是 root，普通用户 `source environment-setup...` 会在里面建 `.tmp_xxx` 失败，出现大量 `Permission denied`。
* 正确做法是**装到 `$HOME` 下并用普通用户执行**；如果已经装在 `/opt`，要 `sudo chown -R 你的用户名 /opt/phytium-sdk` 才能正常用。

---

## 3. 宿主机（WSL）依赖安装

内核编译会用到一些 **host 工具**（`menuconfig` / `fixdep` / `genksyms` 等），这些用的是 **x86_64 本机的 gcc 和库**，跟交叉工具链无关。

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

`environment-setup` 会注入大量 `--sysroot=.../armv8a-openeuler-linux` 和 `-L .../sysroots/.../usr/lib64`，污染 host 工具的链接过程，导致：

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

> 如果以后你要在同一 shell 里去用 Yocto sysroot 编用户态应用，可以另外再 `source environment-setup`，但**编内核的那个 shell 尽量保持干净**。

---

## 5. 内核源码准备

假设源码目录为：

```bash
cd ~/tmp-3/openEuler-5.10.0-216-src
```

### 5.1 权限修正

如果源码是从 root 环境拷贝过来的，先修正属主：

```bash
sudo chown -R wuyuhang:wuyuhang ~/tmp-3/openEuler-5.10.0-216-src
```

避免 `unlink include/generated/autoconf.h: Permission denied` 之类错误。

### 5.2 导入/合并好的 `.config`

你前面从服务器 ISO 中“榨取”了 `.config`，然后和 BSP 的 `defconfig` 做了 merge。把最终确认可用的 `.config` 放到源码根目录：

```bash
cp ~/somewhere/your-merged.config .config
```

### 5.3 补齐新选项并关闭不需要的 GCC 插件

```bash
# 补全新 Kconfig 选项，全部采用默认值（通常是 N）
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

```bash
# 配置已经 done 的情况下，直接编译：
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

---

## 7. 整个过程的关键坑点与经验

1. **工具链安装路径与权限**

    * 错误：用 `sudo` 安到 `/opt/phytium-sdk`，普通用户无法在 SDK 目录下创建 `.tmp_xxx`，`source environment-setup` 时一堆 `mkdir: Permission denied`。
    * 解决：安装到 `$HOME/toolchains/...`，不用 sudo；或给 `/opt/phytium-sdk` 做 `chown -R`。

2. **不要让 Yocto 的 sysroot 污染内核编译环境**

    * `environment-setup` 会强行加 `--sysroot=.../armv8a-openeuler-linux`，导致 host 端的 `ld` 去找 aarch64 的 `libtinfo` / `libcrypto`，甚至找不到 `libncursesw.so.5`，`menuconfig` 无法链接。
    * 解决：编内核时不用 `environment-setup`，只设置 PATH 和 `CROSS_COMPILE`。

3. **宿主机必备包**

    * `libncurses-dev`：解决 `mconf`/`menuconfig` 链接失败 (`cannot find libncursesw.so.5`)。
    * `bison` / `flex` / `libssl-dev` / `libelf-dev` / `dwarves`：各种子系统生成代码、BTF、模块签名等都可能用到。
    * 如要开启 `GCC_PLUGINS`：需要 `libgmp-dev` 等。

4. **GCC 插件相关问题**

    * 你一开始把 `GCC_PLUGINS` 全开，结果 `scripts/gcc-plugins/randomize_layout_plugin.c` 编译时报 `gmp.h: No such file or directory`。
    * 当前阶段主要任务是让 BSP 内核稳定启动，不需要这些额外安全强化，可以全部关闭；等系统跑稳了再单独评估是否开启。

5. **源码目录权限**

    * 如果源码树是从 root 环境拷贝，记得 `chown -R`，避免各种 `Permission denied`。

---

## 8. 可以给实习生的简化版命令清单

给他一份最小命令列表就够了：

```bash
# 1. 安装宿主机依赖（只需一次）
sudo apt update
sudo apt install -y \
    build-essential libncurses-dev bison flex \
    libssl-dev libelf-dev dwarves

# 2. 安装交叉工具链（只需一次）
mkdir -p $HOME/toolchains/phytium-24.03
cd ~/phytium-sdk
./openeuler-glibc-x86_64-openeuler-image-armv8a-phytium-toolchain-24.03-LTS.sh \
    -d $HOME/toolchains/phytium-24.03 -y

# 3. 每次编内核的新 shell：
export TOOLCHAIN=$HOME/toolchains/phytium-24.03
export PATH=$TOOLCHAIN/sysroots/x86_64-openeulersdk-linux/usr/bin:$PATH
export CROSS_COMPILE=aarch64-openeuler-linux-

cd ~/tmp-3/openEuler-5.10.0-216-src
sudo chown -R $USER:$USER .

# 第一次配置 .config：
cp 你的合并配置 .config
make ARCH=arm64 olddefconfig
make ARCH=arm64 menuconfig   # 检查并关闭 GCC_PLUGINS
make -j$(nproc) ARCH=arm64 CROSS_COMPILE=aarch64-openeuler-linux-

# 之后改一点配置再重新编：
make ARCH=arm64 menuconfig
make -j$(nproc) ARCH=arm64 CROSS_COMPILE=aarch64-openeuler-linux-
```

后面你要做的，就是把这套流程再跟“打包到 p2 分区、更新 /boot 和 /lib/modules、改 U-Boot 启动项”那部分串起来，就是完整的“WSL 上交叉编译 + 板子部署”流水线了。
如果你愿意，我也可以帮你把这两块合并成一份更完整的部署文档。

