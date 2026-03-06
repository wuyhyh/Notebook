# 基于 WSL-OpenEuler-22.03 的内核交叉编译环境搭建

> 目标：
>
> 在 x86_64 WSL-OpenEuler-22.03 上，使用官方提供的 `gcc-cross`（含 `gcc_arm64le` 工具链）交叉编译 arm64 内核，产出
> `Image / modules / dtbs`，并形成可长期复用的构建环境。
>
> 适用场景：
>
> * 先在 WSL-OpenEuler-22.03 虚拟机验证编译通过，为后续在 ARM 平台构建机发布版本做准备
> * 生成编译数据库 `compile_commands.json`，支持使用 CLion 进行代码索引与修改，支持内核开发工作流。

---

## 1. 安装 WSL-OpenEuler-22.03 系统

### 1.1 推荐配置（越高越好）

* CPU：多核（编译强依赖 CPU 并行）
* 内存：至少 32GB（更稳）
* 存储：NVMe SSD（影响编译速度与 I/O）
* 网络：能访问外网或你自建的本地源/镜像

### 1.2 安装要点

* 在[这里](https://apps.microsoft.com/detail/9p9rspjdkx9g?hl=zh-CN&gl=US)下载 installer 进行安装
* 网络：保证能联网或至少能访问你准备的本地 yum 源
* 创建用户名和密码，启用 SSH（方便你用 MobaXterm 远程操作）
* 装完后建议更新一次缓存与系统：

  ```bash
  dnf clean all
  dnf makecache
  ```

---

## 2. 启用软件源并安装基础构建依赖

### 2.1 确认 repo 可用

```bash
dnf repolist
dnf makecache
```

你这里已经确认启用了 OS / everything / EPOL / update 等仓库，这是后续能安装 `gcc-cross` 的前提。

### 2.2 安装内核构建基础依赖（host 侧）

```bash
sudo dnf install -y \
  gcc gcc-c++ make bc flex bison perl python3 \
  elfutils-libelf-devel openssl-devel ncurses-devel \
  dwarves rsync git tar xz
```

说明：

* `fixdep/mconf` 等 host 工具会用到这些依赖
* `dwarves` 对 BTF/调试信息相关流程常见需要（你内核配置如果启用 BTF，会用到）

---

## 3. 安装 openEuler 提供的交叉工具链包（关键）

openEuler x86_64 上没有 `gcc-aarch64-linux-gnu` 这种 Debian 风格包名；正确做法是安装 `gcc-cross`，它自带 tar 包形式的交叉工具链。

### 3.1 安装 gcc-cross（来自 EPOL）

```bash
sudo dnf install -y gcc-cross
```

### 3.2 找到 arm64 工具链 tar 包并解压到固定路径

查看包里带了什么：

```bash
rpm -ql gcc-cross | grep -E 'gcc_arm64|arm64le|aarch64'
```

你实际看到的是：

* `/tmp/gcc_arm64le.tar.gz`

解压到 `/opt/toolchains`（不要放 /tmp，避免被清理）：

```bash
sudo mkdir -p /opt/toolchains
cd /opt/toolchains
sudo tar -xzf /tmp/gcc_arm64le.tar.gz
```

确认工具链结构：

```bash
find /opt/toolchains/gcc_arm64le -maxdepth 2 -type d -name bin -print
find /opt/toolchains/gcc_arm64le -maxdepth 2 -type f -name '*gcc' | head
```

你这里最终确认了交叉前缀是：

* `aarch64-linux-gnueabi-`

---

## 4. 固化环境变量（避免 PATH 污染的正确写法）

你踩过的坑：把交叉工具链加到 PATH 前面会导致 host 编译阶段误用 aarch64 的 `as`，出现：

* `as: unrecognized option '--64'`

根治方案：**不污染 PATH**，直接用绝对路径前缀 `CROSS_COMPILE=/opt/.../aarch64-linux-gnueabi-`。

创建环境脚本 `~/env-aarch64.sh`：

```bash
cat > ~/env-aarch64.sh <<'EOF'
# host 工具链：固定用系统 x86_64
export HOSTCC=/usr/bin/gcc
export HOSTCXX=/usr/bin/g++
export HOSTAS=/usr/bin/as
export HOSTLD=/usr/bin/ld

# target 工具链：用绝对路径前缀，避免 PATH 污染
export ARCH=arm64
export TOOLBIN=/opt/toolchains/gcc_arm64le/bin
export CROSS_COMPILE=${TOOLBIN}/aarch64-linux-gnueabi-
EOF
```

使用：

```bash
source ~/env-aarch64.sh
```

验证：

```bash
which as            # 必须是 /usr/bin/as
which gcc           # 必须是 /usr/bin/gcc
"$CROSS_COMPILE"gcc -v | head -n 2
```

---

## 5. 准备内核源码与配置（推荐 O=build 构建）

### 5.1 放置源码与配置文件

建议目录结构（例）：

* `~/src/` 放源码
* `~/build/` 放输出（可选，你也可直接 build 在源码目录下）

解压源码（示例）：

```bash
mkdir -p ~/src
cd ~/src
tar -xf ~/openeuler-5.10.0-136-iso-drop-master.tar.gz
cd openeuler-5.10.0-136-iso-drop-master
```

### 5.2 只用 O=build，避免污染源码树

```bash
mkdir -p build
```

生成配置：

```bash
source ~/env-aarch64.sh
make O=build ARCH=arm64 phytium_defconfig
make O=build ARCH=arm64 olddefconfig
```

修改内核配置

```bash
make O=build ARCH=arm64 menuconfig
```

修改内核的版本标签

```text
export LOCALVERSION=-iso-drop
make O=build kernelrelease
```

说明：

* 以后不要再 `cp config .config` 放到源码根目录
* 统一让 `.config` 只存在于 `build/.config`

---

## 6. 正式交叉编译（Image / modules / dtbs）

确保交叉编译环境 OK，并处于正确的目录

```bash
source ~/env-aarch64.sh
cd ~/src/openeuler-5.10.0-136-src-master
```

直接开始编译

```bash
time make O=build ARCH=arm64 -j"$(nproc)" Image modules dtbs
```

### 6.1 产物位置

* 内核镜像：`build/arch/arm64/boot/Image`
* 设备树：`build/arch/arm64/boot/dts/**/*.dtb`
* 模块：编译后散布在 build 树中，建议用下一步统一安装收集

## 7. 总结

如果编译成功，说明交叉编译环境已经 OK
