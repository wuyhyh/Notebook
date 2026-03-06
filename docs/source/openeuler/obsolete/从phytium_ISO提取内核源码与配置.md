# 从 phytium ISO 提取内核源码与配置

本文档记录如何在 **没有 ARM64 物理机** 的情况下，仅依赖 WSL(Ubuntu 24.04) 和一个 phytium ISO 文件，抽取出对应版本的内核源码和发行版使用的
`.config` 配置。

适用示例环境：

* 宿主：Windows + WSL2 Ubuntu 24.04
* ISO：`PSSE-2203-0407.iso`, 从[这里](https://www.phytium.com.cn/developer/44)下载
* 目标：得到

    * 已打 openEuler 补丁 + phytium BSP 的内核源码树
    * 与之匹配的 `.config` 文件

---

## 1. 准备工具

在 WSL 中安装必需工具：

```bash
sudo apt update
sudo apt install -y rpm2cpio cpio libarchive-tools
```

说明：

* `rpm2cpio`：把 RPM 转换为 cpio 流。
* `cpio`：从 cpio 流中还原文件。
* `libarchive-tools`：提供 `bsdtar`，用于解包 ISO

---

## 2.使用 bsdtar 解包出 ISO 内容（不需要 root）

假设 ISO 位于 `~/PSSE-2203-0407.iso`。

```bash
cd ~
mkdir ftiso
bsdtar -C ftiso -xf PSSE-2203-0407.iso
```

解包完成后：

```bash
cd ~/ftiso
ls
# 可以看到：EFI  Packages  RPM-GPG-KEY-openEuler  TRANS.TBL  boot.catalog  images  repodata
```

---

## 3. 找到 `Packages` 目录和内核相关 RPM

在 ISO 根目录下查找 `Packages` 目录：

```bash
cd ~/ftiso
find . -maxdepth 4 -type d -iname 'Packages'
# 示例输出：./Packages
```

如果使用 2.1 节中的 `bsdtar` 工具解包后的 `Packages` 目录是：

```text
~/ftiso/Packages
```

进入 `Packages` 并过滤出内核相关包：

```bash
cd ~/ftiso/Packages
ls | grep '^kernel'
```

会看到类似：

```text
kernel-5.10.0-136.12.0.86.aarch64.rpm
kernel-debuginfo-5.10.0-136.12.0.86.aarch64.rpm
kernel-debugsource-5.10.0-136.12.0.86.aarch64.rpm
kernel-devel-5.10.0-136.12.0.86.aarch64.rpm
kernel-headers-5.10.0-136.12.0.86.aarch64.rpm
kernel-source-5.10.0-136.12.0.86.aarch64.rpm
kernel-tools-5.10.0-136.12.0.86.aarch64.rpm
kernel-tools-debuginfo-5.10.0-136.12.0.86.aarch64.rpm
kernel-tools-devel-5.10.0-136.12.0.86.aarch64.rpm
```

本次只关注：

* `kernel-source-5.10.0-136.12.0.86.aarch64.rpm`（源码）
* `kernel-5.10.0-136.12.0.86.aarch64.rpm`（二进制内核，内含 `/boot/config-*`）

先拷到单独目录便于操作：

```bash
mkdir -p ~/ft-kernel
cp -v kernel-source-5.10.0-136.12.0.86.aarch64.rpm \
   kernel-5.10.0-136.12.0.86.aarch64.rpm \
   ~/ft-kernel/
```

---

## 4. 从 `kernel-source` RPM 解出内核源码树

进入工作目录：

```bash
cd ~/ft-kernel
```

使用 `rpm2cpio + cpio` 解包：

```bash
rpm2cpio kernel-source-5.10.0-136.12.0.86.aarch64.rpm | cpio -idmv
```

解包后，一般得到类似目录：

```text
usr/src/linux-5.10.0-136.12.0.86.aarch64/
```

验证一下：

```bash
tree usr/ -L 3
```

把源码树移到一个单独路径：

```bash
cp -rf usr/src/linux-5.10.0-136.12.0.86.aarch64 \
   ~/openeuler-5.10.0-136-src
```

此时：

* `~/openeuler-5.10.0-136-src/` 即为 openEuler 带补丁的内核源码目录。

---

## 5. 从 `kernel` RPM 提取发行版 `.config`

继续在 `~/ft-kernel` 目录：

```bash
cd ~/ft-kernel
rpm2cpio kernel-5.10.0-136.12.0.86.aarch64.rpm | \
  cpio -idmv './boot/config-*'
```

生成的文件形如：

```text
boot/config-5.10.0-136.12.0.86.aarch64
```

把它作为源码树的 `.config`：

```bash
cd ~/openeuler-5.10.0-136-src
cp -v ~/ft-kernel/boot/config-5.10.0-136.12.0.86.aarch64 .config
```

至此已经完成：

* 源码：`~/openeuler-5.10.0-136-src/`
* 配置：`~/openeuler-5.10.0-136-src/.config`（与官方发行内核一致）

---

## 6. 使用 git 管理源码树

在得到源码和配置之后，我们需要对这个内核源码进行管理，以当前提取出的内核作为 baseline 版本。

从 [kernel.org](https://www.kernel.org/) 的 **mainline** 内核复制 `.clang-format` 和 `.gitignore` 文件，然后初始化仓库

```text
git init
```

查看当前状态，建立第一次提交

```text
git status
```

commit message 如下

```text
Import the openEuler 22.03 LTS with Phytium BSP kernel sources as our
    baseline tree.

    The code is extracted from:
      kernel-source-openeuler-5.10.0-136-src.12.0.86.aarch64.rpm
    and the default configuration from:
      kernel-openeuler-5.10.0-136-src.12.0.86.aarch64.rpm
    (/boot/config-openeuler-5.10.0-136-src.12.0.86.aarch64)

    This commit also adds .gitignore and .clang-format based on
    the upstream Linux kernel so that we can manage this tree
    with git and keep a consistent coding style.

    No functional changes are intended in this commit.
```

## 7. 后续工作（可选）

在得到源码和配置之后，可以在 x86 主机上进行后续操作，例如：

```bash
cd ~/openeuler-5.10.0-136-src

# 查看 / 微调配置
make ARCH=arm64 menuconfig

# 使用交叉工具链编译
make -j$(nproc) ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- Image modules
```

也可以把这棵树直接集成进自己的交叉编译工作流 / RPM 打包流程中。
