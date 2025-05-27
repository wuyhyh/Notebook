继续翻译 U-Boot README，以下是 **第 12 部分** 的翻译，涵盖：

* Freescale QE/FMAN 固件加载支持
* Freescale Layerscape 管理固件支持
* 构建方式与交叉编译说明

---

## ✅ Freescale QE / FMAN 固件支持（Firmware Support）

Freescale 的 QUICC Engine（QE）与 Frame Manager（FMAN）通常需要在 U-Boot 启动阶段加载固件。

配置选项如下：

* `CONFIG_SYS_FMAN_FW_ADDR`
  FMAN 固件所在的存储地址（取决于以下定义的固件位置）

* `CONFIG_SYS_QE_FW_ADDR`
  QE 固件的地址

* `CONFIG_SYS_QE_FMAN_FW_LENGTH`
  固件最大长度（固件本身包含实际长度字段，但可能需要先申请一整块缓冲区）

### 📦 固件位置定义：

* `CONFIG_SYS_QE_FMAN_FW_IN_NOR`
  固件位于 NOR Flash 中，通过 LBC 映射为常规地址

* `CONFIG_SYS_QE_FMAN_FW_IN_NAND`
  固件位于 NAND Flash 中，地址表示为 NAND 中的偏移

* `CONFIG_SYS_QE_FMAN_FW_IN_MMC`
  固件位于 SD/MMC 设备中，地址为字节偏移量

* `CONFIG_SYS_QE_FMAN_FW_IN_REMOTE`
  固件位于远程主机内存空间（通过 SRIO 或 PCIe 映射）

---

## ✅ Layerscape 管理固件支持（Management Complex）

Freescale 的 Layerscape 平台也支持类似的“管理固件”加载。

* `CONFIG_FSL_MC_ENET`
  启用 Layerscape SoC 上的 MC 驱动（Management Complex）

---

## ✅ Layerscape 调试固件与 SP Boot-ROM 启动支持（Debug Server）

用于加载调试服务器固件，并触发辅助处理器（SP）通过 Boot-ROM 启动：

* `CONFIG_SYS_MC_RSV_MEM_ALIGN`
  管理固件所需的保留内存对齐要求

---

## ✅ U-Boot 构建方法（Building the Software）

U-Boot 支持在多个本地与交叉编译环境中构建。推荐使用 ELDK
工具链（[https://www.denx.de/wiki/DULG/ELDK）进行编译验证。](https://www.denx.de/wiki/DULG/ELDK）进行编译验证。)

### 📍 环境变量配置（以 PowerPC 为例）

```bash
export CROSS_COMPILE=ppc_4xx-
```

无需修改 Makefile 即可支持交叉编译。

---

## ✅ 配置开发板（Board Configuration）

```bash
make <BOARD>_defconfig
```

示例：

```bash
make TQM823L_defconfig
```

也支持派生配置，例如：

```bash
make TQM823L_LCD_defconfig
```

用于启用 LCD 显示功能的配置。

---

## ✅ 构建镜像

```bash
make all
```

生成的文件包括：

* `u-boot.bin`：裸二进制镜像
* `u-boot`：ELF 格式镜像
* `u-boot.srec`：Motorola S-Record 格式镜像

可通过设置环境变量传入编译选项：

```bash
make KCFLAGS=-Werror
```

> 注意：U-Boot 使用 GNU make，某些平台（如 NetBSD）需使用 `gmake`。

---

下一部分将翻译开发板移植指南、新开发板目录结构、测试流程（buildman）、U-Boot 启动命令、镜像格式等内容。是否继续？

