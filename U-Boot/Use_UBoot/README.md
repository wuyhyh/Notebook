# Use U-Boot

以下是 U-Boot 官方文档中“Booting from TPL/SPL”小节的内容翻译：([docs.u-boot.org][1])

---

## 从 TPL/SPL 启动

由于主 U-Boot 二进制文件可能过大，无法被 Boot ROM 直接加载，因此最初将 U-Boot 拆分为多个启动阶段。([docs.u-boot.org][1])

U-Boot 通常经历以下启动阶段，其中 TPL、VPL 和 SPL 是可选的。虽然许多开发板使用 SPL，但只有少数使用
TPL。([docs.u-boot.org][2])

* **TPL（三级程序加载器）**：非常早期的初始化，尽可能小。它加载 SPL（如果启用了 VPL，则加载 VPL）。([docs.u-boot.org][3])

* **VPL（验证程序加载器）**：可选的验证步骤，如果启用了 A/B 验证启动，它可以选择多个 SPL 二进制文件。VPL 的实现仍在进行中。目前，它只是启动到
  SPL。([docs.u-boot.org][1])

* **SPL（二级程序加载器）**：设置 SDRAM 并加载 U-Boot 正式版。它也可能加载其他固件组件。([docs.u-boot.org][1])

* **U-Boot 正式版**：这是唯一包含命令的阶段。它还实现了加载操作系统的逻辑，例如通过 UEFI。([docs.u-boot.org][1])

**注意**：在 PowerPC 架构上，命名约定与其他架构不同。此处的启动顺序为 SPL->TPL->U-Boot。([docs.u-boot.org][1])

U-Boot SPL 的其他用途包括：([docs.u-boot.org][1])

* 启动 ARM Trusted Firmware 的 BL31，它将 U-Boot 作为 BL33 调用([docs.u-boot.org][1])

* 启动 EDK II([docs.u-boot.org][1])

* 启动 Linux，例如 Falcon 模式([docs.u-boot.org][1])

* 启动 RISC-V OpenSBI，它调用主 U-Boot([docs.u-boot.org][1])

---

## 目标二进制文件

SPL/TPL 加载的二进制文件可以是：([docs.u-boot.org][1])

* 原始二进制文件，其入口地址等于起始地址。这是 TPL 支持的唯一二进制格式。([docs.u-boot.org][1])

* FIT（Flattened Image Tree）镜像

* 传统的 U-Boot 镜像([docs.u-boot.org][4])

### 配置

* 仅当设置了 `CONFIG_SPL_RAW_IMAGE_SUPPORT=y` 时，SPL 才支持原始镜像。([docs.u-boot.org][1])

* 要加载 FIT 镜像，需要设置 `CONFIG_SPL_FIT=y` 和 `CONFIG_SPL_LOAD_FIT=y`。([docs.u-boot.org][1])

* 要加载传统的 U-Boot 镜像，需要设置 `CONFIG_SPL_LEGACY_IMAGE_FORMAT=y`。设置 `CONFIG_SPL_LEGACY_IMAGE_CRC_CHECK=y` 可启用对传统
  U-Boot 镜像的 CRC32 校验。([docs.u-boot.org][1])

---

## 镜像加载方法

开发板可用的镜像启动方法必须在两个地方定义：([docs.u-boot.org][1])

1. 开发板代码实现一个函数 `board_boot_order()`，枚举最多五种启动方法及其尝试顺序。（启动方法的最大数量当前硬编码为变量
   `spl_boot_list[]`）。如果只有一个启动方法函数，可以实现 `spl_boot_device()` 代替。([docs.u-boot.org][1])

2. 配置控制这些启动方法中哪些实际可用。([docs.u-boot.org][1])

---

有关更多详细信息和后续内容，请参考官方文档的完整章节：

🔗 [Booting from TPL/SPL](https://docs.u-boot.org/en/latest/usage/spl_boot.html)

[1]: https://docs.u-boot.org/en/stable/usage/spl_boot.html?utm_source=chatgpt.com "Booting from TPL/SPL — Das U-Boot unknown version documentation"

[2]: https://docs.u-boot.org/en/v2024.10/develop/spl.html?utm_source=chatgpt.com "Generic SPL framework - The U-Boot Documentation"

[3]: https://docs.u-boot.org/en/latest/develop/spl.html?utm_source=chatgpt.com "Generic xPL framework - The U-Boot Documentation"

[4]: https://docs.u-boot.org/en/stable/develop/falcon.html?utm_source=chatgpt.com "Falcon Mode — Das U-Boot unknown version documentation"




