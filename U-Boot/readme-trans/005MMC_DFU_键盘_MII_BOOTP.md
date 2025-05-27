继续翻译 U-Boot README，以下是 **第 5 部分** 的翻译，涵盖：

* MMC 支持
* DFU（USB 设备固件更新）
* 键盘支持
* MII / PHY 支持
* BOOTP（自动获取 IP 启动）相关配置

---

### ✅ MMC 支持（MMC Support）

* `CONFIG_SH_MMCIF`
  启用对 Renesas 片上 MMCIF 控制器的支持。

    * `CONFIG_SH_MMCIF_ADDR`：MMCIF 控制器寄存器的基地址
    * `CONFIG_SH_MMCIF_CLK`：MMCIF 控制器的时钟频率

---

### ✅ USB 设备固件更新（DFU - Device Firmware Update）

* `CONFIG_DFU_OVER_USB`：启用 USB 接口上的 DFU 功能

* `CONFIG_DFU_NAND`：允许通过 DFU 更新 NAND 存储器

* `CONFIG_DFU_RAM`：允许通过 DFU 将内容传输到 RAM

  > 虽然 DFU 规范原本只支持非易失性存储，但使用 RAM 主要用于开发用途

* `CONFIG_SYS_DFU_DATA_BUF_SIZE`：DFU 传输使用的缓冲区大小（单位：字节）

  > 可通过环境变量 `dfu_bufsiz` 设置

* `CONFIG_SYS_DFU_MAX_FILE_SIZE`：当 DFU 处理文件时，会将完整文件复制到此缓冲区再写入目标设备

* `DFU_DEFAULT_POLL_TIMEOUT`：设备返回给主机的轮询超时时间（单位：毫秒）

* `DFU_MANIFEST_POLL_TIMEOUT`：设备进入 `dfuMANIFEST` 状态时，主机需要等待的时间（单位：毫秒）

---

### ✅ 键盘支持（Keyboard Support）

> 支持多种键盘驱动程序，具体请查看 Kconfig 文件中的帮助文档

---

### ✅ MII / PHY 支持（以太网 PHY 层配置）

* `CONFIG_PHY_CLOCK_FREQ`（ppc4xx 专用）：MII 总线的时钟频率

* `CONFIG_PHY_CMD_DELAY`（ppc4xx 专用）：某些 PHY（如 Intel LXT971A）在发送命令后需要额外延时才能读取状态寄存器

---

### ✅ BOOTP 启动恢复模式（BOOTP Recovery Mode）

* `CONFIG_BOOTP_RANDOM_DELAY`
  为避免在网络断电恢复后所有设备同时发送 BOOTP 请求而拥塞网络，可添加随机延迟。

  延迟方案如下：

    * 第 1 次请求：延迟 0 ～ 1 秒
    * 第 2 次请求：延迟 0 ～ 2 秒
    * 第 3 次请求：延迟 0 ～ 4 秒
    * 第 4 次及以后：延迟 0 ～ 8 秒

* `CFG_BOOTP_ID_CACHE_SIZE`
  BOOTP 客户端会缓存一定数量的请求 ID，用于辨别是否是对应的回应。默认缓存 4 个请求的 ID。

---

下一个部分将翻译 DHCP 选项、MAC 地址配置、CDP 选项、状态 LED、GPIO、I2C 配置等内容。是否继续？


