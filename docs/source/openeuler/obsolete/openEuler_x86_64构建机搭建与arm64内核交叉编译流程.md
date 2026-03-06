# openEuler x86_64 构建机搭建与 arm64 内核交叉编译流程

目标：在 x86_64 openEuler 22.03 LTS SP4 上，使用官方提供的 `gcc-cross`（含 `gcc_arm64le` 工具链）交叉编译 arm64 内核，产出
`Image / modules / dtbs`，并形成可长期复用的构建机环境。

适用场景：

* 先在 VMware 虚拟机验证流程
* 假期结束后同样步骤在公司物理机安装并作为专用编译机

---

## 0. 物理机/虚拟机的硬件与安装建议

### 推荐配置（越高越好）

* CPU：多核（编译强依赖 CPU 并行）
* 内存：至少 32GB（更稳）
* 存储：NVMe SSD（影响编译速度与 I/O）
* 网络：能访问公司内网源或你自建的本地源/镜像

### VMware 建议（用于验证）

* 关闭/减少与 Windows 共享目录参与编译（共享目录 I/O 很慢）
* 给足 CPU 核心与内存（例如 8C+ / 16GB+，视宿主机情况）
* 磁盘选择 “预分配/厚置备” 会更稳定

---

## 1. 安装 openEuler x86_64 系统

### 1.1 安装介质

* ISO：`openEuler-22.03-LTS-SP4-x86_64-dvd.iso`

### 1.2 安装要点（VM/物理机都一样）

* 安装模式：Server（最小化或常规均可）
* 分区：

    * `/` 建议至少 100GB（内核源码 + build 目录 + staging + 缓存）
    * 你如果要长期做多个版本内核/多套 sysroot，建议更大
* 网络：保证能联网或至少能访问你准备的本地 yum 源
* 创建 root 密码，启用 SSH（方便你用 MobaXterm 远程操作）
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
tar -xf ~/openeuler-5.10.0-136-src-master.tar.gz
cd openeuler-5.10.0-136-src-master
```

### 5.2 只用 O=build，避免污染源码树

```bash
mkdir -p build
```

把你的 arm64 配置放进 build：

```bash
cp ~/config-5.10.0-136.12.0.86.aarch64 build/.config
```

生成最终配置：

```bash
source ~/env-aarch64.sh
make O=build ARCH=arm64 olddefconfig
```

修改内核配置

```bash
make O=build ARCH=arm64 menuconfig
```

修改内核的版本标签

```text
export LOCALVERSION=-baseline_2026Q1
make O=build ARCH=arm64 olddefconfig
make O=build kernelrelease
```

说明：

* 以后不要再 `cp config .config` 放到源码根目录
* 统一让 `.config` 只存在于 `build/.config`

---

## 6. 正式交叉编译（Image / modules / dtbs）

一行写完，避免交互 shell 的断行问题：

```bash
source ~/env-aarch64.sh
cd ~/src/openeuler-5.10.0-136-src-master

time make O=build ARCH=arm64 \
  CROSS_COMPILE="$CROSS_COMPILE" \
  HOSTCC="$HOSTCC" HOSTAS="$HOSTAS" HOSTLD="$HOSTLD" \
  -j"$(nproc)" Image modules dtbs
```

### 6.1 产物位置

* 内核镜像：`build/arch/arm64/boot/Image`
* 设备树：`build/arch/arm64/boot/dts/**/*.dtb`
* 模块：编译后散布在 build 树中，建议用下一步统一安装收集

---

## 7. 模块安装到 staging 目录（推荐）

用于后续拷贝到 rootfs 或做打包：

```bash
mkdir -p ~/staging
sudo make O=build ARCH=arm64 \
  CROSS_COMPILE="$CROSS_COMPILE" \
  modules_install INSTALL_MOD_PATH=~/staging
```

查看版本号（用于确认 modules 路径）：

```bash
make O=build kernelrelease
```

模块会落在：

* `~/staging/lib/modules/<kernelrelease>/`

---

## 8. 常见问题与规避

### 8.1 `as: unrecognized option '--64'`

原因：host 编译阶段误用了 aarch64 的 `as`（PATH 污染）。
解决：不要把交叉工具链加到 PATH；用绝对路径 `CROSS_COMPILE=/opt/.../aarch64-linux-gnueabi-`；host 工具固定 `/usr/bin/as`。

### 8.2 `The source tree is not clean`

原因：源码树被之前“非 O=build”的构建生成文件污染。
解决：

* 直接删除源码目录重解压（你最终选择的方式）
* 或在源码目录 `make mrproper` 后只用 `O=build`

---

## 9. 从 VM 迁移到物理机的建议

在物理机安装同一个 ISO，整体流程完全一样。为了让“专用编译机”长期稳定，我建议你加上这些：

1. 单独磁盘/分区给源码与 build（例如 `/work` 挂载到大盘）
2. 固定目录：

    * `/opt/toolchains`（工具链）
    * `/work/src`（源码）
    * `/work/build`（build 输出）
    * `/work/staging`（modules_install 输出）
3. 做一个简单的构建脚本（把第 5~7 节命令固化），避免手敲出错
4. 编译机尽量不跑别的服务，减少系统抖动
