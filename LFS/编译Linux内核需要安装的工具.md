# Fedora 上编译内核

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

## ✅ 四、建议

* 推荐使用官方源码：[https://www.kernel.org/](https://www.kernel.org/)
* 或者使用 Fedora 自带的内核源码包：

```bash
sudo dnf install kernel-devel kernel-headers
```

* 另外可以安装 bear 生成编译数据库文件，这样方便使用 IDE 阅读 Linux 内核源码

```shell
sudo dnf install bear
```

# Ubuntu 上编译内核

在 **Ubuntu** 上编译 Linux 内核，同样需要安装一套工具链和依赖库。下面是详细清单和说明：

---

## ✅ 一、安装编译 Linux 内核所需的依赖包

打开终端，执行以下命令：

```bash
sudo apt install -y build-essential libncurses-dev bison flex libssl-dev \
  libelf-dev bc wget dwarves zstd xz-utils
```

### 工具说明：

| 工具/库               | 作用                                                   |
|--------------------|------------------------------------------------------|
| `build-essential`  | 包括 gcc、make、binutils 等基础构建工具                         |
| `libncurses-dev`   | 支持 `make menuconfig` 的字符界面配置                         |
| `bison`, `flex`    | 内核中某些脚本语言生成器所需                                       |
| `libssl-dev`       | 如果启用了加密模块（比如 TLS、TPM）                                |
| `libelf-dev`       | 处理 ELF 格式文件，用于模块支持                                   |
| `bc`               | 内核配置中用于整数运算的脚本语言                                     |
| `wget`             | 下载内核源码                                               |
| `dwarves`          | 提供 `pahole` 命令，用于生成 BTF 信息（CONFIG\_DEBUG\_INFO\_BTF） |
| `zstd`, `xz-utils` | 支持内核映像和模块的压缩格式                                       |

---

## ✅ 三、安装内核源码（可选方式）

1. **从官方 kernel.org 下载内核源码：**

```bash
wget https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-6.6.tar.xz
tar -xvf linux-6.6.tar.xz
cd linux-6.6
```

2. **或使用 Ubuntu 的内核源码包（用于打补丁或学习）：**

```bash
sudo apt install linux-source
cd /usr/src
tar -xvf linux-source-*.tar.bz2
```
