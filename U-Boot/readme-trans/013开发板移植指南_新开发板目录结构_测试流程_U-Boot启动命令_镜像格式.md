继续翻译 U-Boot README，以下是 **第 13 部分** 的翻译，涵盖：

* 添加/移植新开发板的建议
* buildman 构建测试工具
* bootm 命令格式及内核镜像启动
* U-Boot 支持的镜像格式

---

## ✅ 添加新开发板（Adding a new board）

新开发板的添加建议：

* 所有新板子必须有一个 defconfig 文件，并位于 `configs/` 目录。
* 新增目录通常位于 `board/<vendor>/<board>/`，结构如下：

```text
board/<vendor>/<board>/
├── Kconfig
├── MAINTAINERS
├── Makefile
├── board.c           # 板级初始化代码
├── <board>.h         # 头文件
└── README            # 说明文档（可选）
```

* 所有新板必须有维护者（MAINTAINERS 文件中定义），并通过 CI 构建测试（使用 buildman 工具）。

---

## ✅ 使用 buildman 工具进行构建测试

buildman 是 U-Boot 提供的自动批量构建工具，用于：

* 测试多个平台是否构建通过；
* 检测不同提交版本间的构建差异；
* 输出构建体积比较报告。

示例：

```bash
tools/buildman/buildman -o output/ sandbox x86 qemu_arm
```

参数说明：

* `-o output/`：构建输出目录
* 后面跟的是开发板或架构名（可使用 `-a` 构建全部）

---

## ✅ bootm 命令格式（bootm command format）

```bash
bootm <kernel_addr> [ramdisk_addr] [fdt_addr]
```

参数说明：

* `<kernel_addr>`：内核镜像地址（支持 uImage 格式）
* `[ramdisk_addr]`：可选的 ramdisk 镜像地址
* `[fdt_addr]`：可选的设备树地址（如果内核支持 FDT）

> `bootm` 命令会解析镜像头信息，并根据类型决定如何启动。例如：

* 启动 Linux 内核
* 启动 u-boot 自身（嵌套）
* 启动自定义应用

---

## ✅ U-Boot 镜像格式支持（Image Formats）

### 1. **uImage 格式（传统）**

* 使用 `mkimage` 工具打包的格式，包含如下信息：

    * 镜像类型（内核/ramdisk/script 等）
    * 架构（ARM/MIPS/PPC 等）
    * 加载地址
    * 启动入口地址
    * 校验和（CRC）

* 默认文件名：`uImage`

* 可用命令行制作：

  ```bash
  tools/mkimage -A arm -T kernel -C none -a 0x8000 -e 0x8000 -n "Linux" -d zImage uImage
  ```

---

### 2. **FIT 格式（Flattened Image Tree）**

* 支持多个镜像（内核、设备树、initrd）打包为一个结构化的容器
* 支持加密、签名、安全启动
* 推荐用于现代系统

配置：

* `CONFIG_FIT`：启用 FIT 支持
* `CONFIG_FIT_SIGNATURE`：启用签名校验
* `CONFIG_FIT_VERBOSE`：启用详细打印
* `CONFIG_FIT_ENABLE_SHA256_SUPPORT`：启用 SHA-256 校验

---

### 3. **Script 镜像格式**

* 类型为 `script` 的 uImage
* 内含一段 boot 脚本，在 U-Boot 环境中直接运行

制作方法：

```bash
tools/mkimage -A arm -T script -C none -n "Boot Script" -d boot.cmd boot.scr
```

---

下一部分将翻译控制台设备设置、多启动源支持（比如 USB、NAND、网络等）、多核系统协处理器加载、系统时间管理等内容。是否继续？

