继续翻译 U-Boot README，以下是 **第 9 部分** 的翻译，涵盖：

* MTD 支持（包括 UBI 和 wear leveling）
* SPL 框架（Secondary Program Loader）
* PPC 架构的中断支持
* 板级初始化配置（Board Initialization）

---

### ✅ MTD 支持（MTD 支持、mtdparts 命令、UBI）

#### 📍 磨损均衡配置（Wear Leveling）

* `CONFIG_MTD_UBI_WL_THRESHOLD`
  控制 UBI 设备中，最大擦除计数差值阈值，超过后 UBI 会触发磨损均衡（将数据从低擦除次数块迁移到高擦除次数块）

    * 默认：4096
    * 对于 SLC NAND、NOR Flash 可以使用默认值
    * 对于 MLC NAND（擦除寿命少于 10000 次），建议设为 128 或 256

#### 📍 坏块管理

* `CONFIG_MTD_UBI_BEB_LIMIT`
  设置 UBI 每 1024 个擦除块中最大期望的坏块数量，默认值为 20（大约保留 1.9% 的块用于坏块处理）

  > 可根据 NAND 数据手册中最小/最大有效块数估算

#### 📍 Fastmap（加快 UBI 挂载速度）

* `CONFIG_MTD_UBI_FASTMAP`：启用 fastmap 机制，避免全盘扫描以提升挂载速度
* `CONFIG_MTD_UBI_FASTMAP_AUTOCONVERT`：自动为旧镜像添加 fastmap
* `CONFIG_MTD_UBI_FM_DEBUG`：启用 fastmap 调试功能

---

### ✅ SPL 框架支持（Secondary Program Loader）

* `CONFIG_SPL`：全局启用 SPL 构建

#### 📍 错误处理

* `CONFIG_SPL_PANIC_ON_RAW_IMAGE`：若 SPL 加载的镜像没有签名，则 panic；适用于无法完全检测读错误的存储控制器

#### 📍 架构/平台专用配置

* `CONFIG_SPL_MPC83XX_WAIT_FOR_NAND`：在 mpc83xx 平台使用 NAND 启动时，启动代码等待 SPL 完整加载

#### 📍 UBI 支持

* `CONFIG_SPL_UBI`：启用 SPL 支持读取 fastmap UBI 镜像的能力

#### 📍 NAND 参数（用于 SPL 加载 U-Boot）

* `CONFIG_SYS_NAND_5_ADDR_CYCLE` 等：定义 NAND 寄存器行为
* `CFG_SYS_NAND_U_BOOT_DST`：U-Boot 加载地址
* `CFG_SYS_NAND_U_BOOT_SIZE`：U-Boot 镜像大小
* `CFG_SYS_NAND_U_BOOT_START`：U-Boot 入口地址

#### 📍 其他 SPL 配置

* `CONFIG_SPL_RAM_DEVICE`：支持从 RAM 中运行的镜像
* `CONFIG_SPL_FIT_PRINT`：在 bootm 启动 FIT 镜像时打印其信息（默认关闭以节省空间）

---

### ✅ 中断支持（Interrupt support for PPC）

适用于 PowerPC 架构：

* `interrupt_init()`：统一的初始化函数，会调用架构相关的 `interrupt_init_cpu()`
* `timer_interrupt()`：统一的中断处理函数，会调用 `timer_interrupt_cpu()`

如开发板包含 watchdog、状态 LED 等，它们会在 `timer_interrupt()` 中自动处理。

---

### ✅ 板级初始化流程（Board Initialization Settings）

在启动过程中，U-Boot 会调用多个板级函数用于硬件准备，例如配置引脚、初始化外设等：

配置宏如下：

* `CONFIG_BOARD_EARLY_INIT_F`：调用 `board_early_init_f()`（早期阶段）
* `CONFIG_BOARD_EARLY_INIT_R`：调用 `board_early_init_r()`（初始化完毕后）
* `CONFIG_BOARD_LATE_INIT`：调用 `board_late_init()`（最后初始化阶段）

这些函数通常定义在各架构的 `board.c` 中，例如 `board_init_f()` 和 `board_init_r()`。

---

下一部分将开始翻译系统配置参数（如命令行提示符、内存基地址、Flash 起始地址、malloc 空间大小等）。是否继续？

