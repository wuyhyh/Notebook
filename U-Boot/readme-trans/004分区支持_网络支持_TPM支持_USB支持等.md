以下是 U-Boot README 的 **第 4 部分翻译**，涵盖分区支持、网络支持（PCI 与非 PCI）、TPM 支持、USB 支持等：

---

### ✅ 分区标签支持（Partition Labels）

可选配置，用于支持不同格式的磁盘分区表：

* `CONFIG_MAC_PARTITION`：支持 Apple 的 MacOS 分区表
* `CONFIG_ISO_PARTITION`：支持 ISO 格式（常用于 CD-ROM）
* `CONFIG_EFI_PARTITION`：支持 GPT 分区（EFI 常见格式，注意有 2TB 限制，见 `disk/part_efi.c`）

> 如果启用了 `CONFIG_SCSI`，你还必须配置至少一种非 MTD 的分区类型。

---

### ✅ 网络支持 - PCI 网络芯片（NETWORK Support (PCI)）

* `CONFIG_E1000_SPI`：用于 Intel 8257x 芯片 SPI 总线直接访问的工具代码（需配合 `CONFIG_CMD_E1000` 或
  `CONFIG_E1000_SPI_GENERIC`）

* `CONFIG_NATSEMI`：支持 National Semiconductor dp83815 芯片

* `CONFIG_NS8382X`：支持 National Semiconductor dp83820 / dp83821 千兆以太网芯片

---

### ✅ 网络支持 - 非 PCI 芯片（NETWORK Support (other)）

* `CONFIG_CALXEDA_XGMAC`：支持 Calxeda 的 XGMAC 网络控制器

* `CONFIG_LAN91C96`：支持 SMSC 的 LAN91C96 芯片

    * `CONFIG_LAN91C96_USE_32_BIT`：启用 32 位寻址模式

    * `CFG_SYS_DAVINCI_EMAC_PHY_COUNT`：若有超过 3 个 PHY，需要定义该宏

* `CONFIG_FTGMAC100`：支持 Faraday 的 FTGMAC100 千兆以太网控制器

    * `CONFIG_FTGMAC100_EGIGA`：若连接了千兆 PHY，可启用该项以更新千兆链路状态

      > 如果系统仅有 10/100 PHY，启用该项不会影响功能，但可能会产生无用或超时的数据轮询

* `CONFIG_SH_ETHER`：支持 Renesas 芯片上的 SH 内置以太网控制器

    * `CFG_SH_ETHER_USE_PORT`：定义使用的端口数量
    * `CFG_SH_ETHER_PHY_ADDR`：定义 PHY 的地址
    * `CFG_SH_ETHER_CACHE_WRITEBACK`：启用缓存写回支持

---

### ✅ TPM 支持（TPM Support）

* `CONFIG_TPM`：启用 TPM 支持框架，用于访问 TPM 命令接口

* `CONFIG_TPM_TIS_INFINEON`：支持 Infineon I2C 总线上的 TPM 设备（当前只支持一个设备）

    * `CONFIG_TPM_TIS_I2C_BURST_LIMITATION`：限制 burst 模式读取字节数量

* `CONFIG_TPM_ST33ZP24`：支持 STMicroelectronics 的 ST33ZP24 TPM 芯片（需要启用 `DM_TPM`）

    * `CONFIG_TPM_ST33ZP24_I2C`：支持其 I2C 接口
    * `CONFIG_TPM_ST33ZP24_SPI`：支持其 SPI 接口

* `CONFIG_TPM_ATMEL_TWI`：支持 Atmel TWI 接口的 TPM（需启用 I2C）

* `CONFIG_TPM_TIS_LPC`：支持通用并口 TPM，当前也只支持一个设备

* `CONFIG_TPM_AUTH_SESSIONS`：启用授权命令支持（需配合 `CONFIG_TPM` 和 `CONFIG_SHA1`）

---

### ✅ USB 支持（USB Host）

> 当前仅支持 **UHCI** 控制器：

* `CONFIG_USB_UHCI`：启用 UHCI 控制器（如 PIP405 / MIP405）

* `CONFIG_USB_KEYBOARD`：启用 USB 键盘支持

* `CONFIG_USB_STORAGE`：启用 USB 存储设备支持

  > 支持的 USB 设备包括键盘和 TEAC FD-05PUB USB 软驱

* `CONFIG_USB_DWC2_REG_ADDR`：DWC2 模块寄存器的物理地址

---

### ✅ USB 设备模式（USB Device）

> 若你希望使用 **USB 作为 U-Boot 控制台输入输出（usbtty）**，请参考以下设置：

* 设置环境变量：

  ```bash
  setenv stdin usbtty
  setenv stdout usbtty
  ```

* 接上 USB 线后，可通过主机运行 `dmesg` 查看新设备信息。

* 环境变量 `usbtty` 可设置为：

    * `gserial`：使用 Linux 的 gserial 驱动识别
    * `cdc_acm`：使用标准 USB CDC ACM 类识别为串口设备

* 示例主机加载方式（仅限 gserial）：

  ```bash
  modprobe usbserial vendor=0xVendorID product=0xProductID
  ```

* 可配置以下宏以定义设备身份信息：

    * `CONFIG_USBD_MANUFACTURER`：厂商名称（字符串）
    * `CONFIG_USBD_PRODUCT_NAME`：产品名称（字符串）
    * `CONFIG_USBD_VENDORID`：Vendor ID（必须是 USB 协会分配的合法值）
    * `CONFIG_USBD_PRODUCTID`：Product ID

---

接下来是 **MMC / DFU（USB固件更新）/ 键盘 / MII / BOOTP 等更多模块的翻译**。需要我继续吗？你也可以随时跳到某个特定模块。
