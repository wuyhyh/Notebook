# 在 Fedora 上编译内核

在 Fedora 上编译 Linux 内核，需要安装一整套构建工具和依赖包。以下是完整且推荐的步骤：

---

## ✅ 一、安装编译所需的工具和依赖

打开终端，执行以下命令：

```bash
sudo dnf install ncurses-devel bison flex elfutils-libelf-devel openssl-devel \
  dwarves perl gcc make bc wget zstd xz
```

说明：

| 工具                      | 作用                                                    |
|-------------------------|-------------------------------------------------------|
| `gcc`, `make`           | 编译核心工具                                                |
| `ncurses-devel`         | `make menuconfig` 图形配置界面                              |
| `bison`, `flex`         | 编译 `scripts/` 目录下的某些生成器                               |
| `elfutils-libelf-devel` | 处理 `ELF` 格式，内核模块编译所需                                  |
| `openssl-devel`         | 如果内核启用加密模块                                            |
| `perl`                  | 一些构建脚本依赖                                              |
| `bc`                    | 内核版本和时间计算                                             |
| `dwarves`               | `pahole` 工具，生成 BTF 调试信息（如果启用 `CONFIG_DEBUG_INFO_BTF`） |
| `xz`, `zstd`            | 支持压缩内核映像或模块                                           |
| `wget`                  | 下载内核源码用                                               |

---

## ✅ 二、建议

* 推荐使用官方源码：[https://www.kernel.org/](https://www.kernel.org/)
* 或者使用 Fedora 自带的内核源码包：

```bash
sudo dnf install kernel-devel kernel-headers
```

但如果你打算完全从源代码编译，可以从 kernel.org 下载 `.tar.xz` 后手动解压、配置、编译。

---

# ✅ Fedora 上编译 Linux 内核的三种方式总结

| 方式    | 使用目的                         | 特点                                   | 难度    |
|-------|------------------------------|--------------------------------------|-------|
| ✅ 方式一 | 获取纯净主线内核，学习、自定义构建            | 使用 kernel.org 的 vanilla 源码           | ★★★☆☆ |
| ✅ 方式二 | 编译 DKMS 模块或特定驱动              | 使用 `kernel-devel` & `kernel-headers` | ★☆☆☆☆ |
| ✅ 方式三 | 获取 Fedora 补丁过的完整源码，重建系统兼容的内核 | 使用 Fedora 的内核 `.src.rpm` 包           | ★★★★☆ |

---

## ✅ 方式一：使用 kernel.org 的原始 vanilla 内核源码进行编译

**适合人群**：内核学习者、研究新版本内核特性、自定义构建。

### 操作流程：

```bash
# 1. 安装依赖工具
sudo dnf install ncurses-devel bison flex elfutils-libelf-devel openssl-devel \
  dwarves perl gcc make bc zstd xz wget

# 2. 下载内核源码（以 6.9.3 为例）
wget https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-6.9.3.tar.xz
tar -xvf linux-6.9.3.tar.xz
cd linux-6.9.3

# 3. 配置内核（可选：复制当前系统配置）
cp /boot/config-$(uname -r) .config
make olddefconfig      # 或 make menuconfig 进行自定义

# 4. 编译内核（并行编译）
make -j$(nproc)

# 5. 安装模块和内核
sudo make modules_install
sudo make install

# 6. 更新启动项
sudo grub2-mkconfig -o /boot/grub2/grub.cfg
sudo reboot
```

---

## ✅ 方式二：使用 `kernel-devel` 和 `kernel-headers` 构建模块

**适合人群**：开发驱动模块（比如 DKMS）、不修改内核源码本体。

### 操作流程：

```bash
# 1. 安装头文件和构建环境
sudo dnf install kernel-devel kernel-headers

# 2. 确保当前运行的内核与 devel 匹配
uname -r
rpm -q kernel-devel

# 3. 进入驱动源代码目录并构建模块（假设有 Makefile）
make -C /usr/src/kernels/$(uname -r) M=$(pwd) modules

# 或者用 DKMS 方式封装自动构建模块
```

**注意**：此方式不涉及内核源码，不可用于修改内核，只适合模块构建。

---

## ✅ 方式三：使用 Fedora 官方的补丁内核源码进行构建

**适合人群**：在 Fedora 系统上构建兼容的、符合 RPM 构建规则的内核包或测试补丁。

### 操作流程：

```bash
# 1. 安装依赖
sudo dnf install rpmdevtools fedpkg dnf-utils ncurses-devel pesign bison flex elfutils-libelf-devel openssl-devel dwarves perl bc

# 2. 下载 Fedora 官方内核源码包
rpmdev-setuptree
cd ~/rpmbuild/SOURCES
dnf download --source kernel
rpm -ivh kernel-*.src.rpm

# 3. 编辑 spec 文件（可选）
cd ~/rpmbuild/SPECS
rpmbuild -bp kernel.spec     # 解压源码，应用补丁
cd ~/rpmbuild/BUILD/kernel-*/

# 4. 配置内核
cp /boot/config-$(uname -r) .config
make olddefconfig
make menuconfig              # 如需修改配置

# 5. 编译内核（可选构建 RPM 包）
cd ~/rpmbuild/SPECS
rpmbuild -bb kernel.spec     # 构建二进制 RPM 包

# 6. 安装生成的 RPM 包
cd ~/rpmbuild/RPMS/x86_64
sudo dnf install kernel-*.rpm

# 7. 重启并进入新内核
sudo reboot
```

---

## 📌 三种方式适用场景对比

| 需求                    | 推荐方式 | 原因            |
|-----------------------|------|---------------|
| 学习内核源码，理解主线结构         | 方式一  | 纯净、主线结构清晰     |
| 编写第三方驱动（如网卡）          | 方式二  | 快速、无需全套源码     |
| 在 Fedora 上测试补丁，构建兼容内核 | 方式三  | 包含补丁、RPM 打包集成 |

---

是否需要我再帮你准备一个实际例子，比如从 kernel.org 下载源码并构建一个简化内核？或者基于 Fedora `.src.rpm` 打个补丁再构建？

