以下是 U-Boot README 的 **第 6 部分翻译**，涵盖：

* DHCP 高级选项
* MAC 地址分配
* CDP 协议支持
* 状态 LED 显示
* GPIO 支持
* I/O 追踪（扩展）
* 时间戳功能（简要回顾）

---

### ✅ DHCP 高级选项（DHCP Advanced Options）

#### 📍 本地链路 IP 地址协商（Link-local IP address negotiation）

* 允许设备在没有 DHCP 服务器的网络环境中，与其他客户端协商可用的 IP 地址，确保即使没有集中配置，也能实现通信。

* 更多说明见：`doc/README.link-local`

---

### ✅ 从环境变量读取 MAC 地址（MAC address from environment variables）

* `FDT_SEQ_MACADDR_FROM_ENV`
  U-Boot 可根据设备树中启用的以太网节点，依次从环境变量中读取 MAC 地址填充：

    * `ethaddr`, `eth1addr`, `eth2addr` 等等

  要求：设备树中未启用的节点应被删除或标记为 `"disabled"`。

---

### ✅ CDP 协议配置（CDP Options）

> CDP（Cisco Discovery Protocol）相关配置，适用于设备在网络中自动广播身份和能力。

* `CONFIG_CDP_DEVICE_ID`：设备在 CDP 中的标识 ID
* `CONFIG_CDP_DEVICE_ID_PREFIX`：两个字符组成的前缀，加在 MAC 地址前
* `CONFIG_CDP_PORT_ID`：端口名格式（如 `"eth%d"`）
* `CONFIG_CDP_CAPABILITIES`：设备能力位（如 `0x10` 表示普通主机）
* `CONFIG_CDP_VERSION`：软件版本
* `CONFIG_CDP_PLATFORM`：平台名称
* `CONFIG_CDP_TRIGGER`：触发值（32位）
* `CONFIG_CDP_POWER_CONSUMPTION`：功耗，单位为 0.1 毫瓦
* `CONFIG_CDP_APPLIANCE_VLAN_TYPE`：CDP VLAN 类型 ID

---

### ✅ 状态 LED 显示（Status LED）

* 启用 `CONFIG_LED_STATUS` 后，U-Boot 可通过 LED 显示系统状态：

    * 快速闪烁 → 正在运行 U-Boot
    * 停止闪烁 → 成功接收到 BOOTP 回复
    * 慢速闪烁 → 已启动 Linux（需内核配合）

#### 可选扩展：

* `CONFIG_LED_STATUS_GPIO`：状态 LED 连接到 GPIO 时启用此项，会使用 `gpio_led` 驱动作为后端实现

* `CFG_GPIO_LED_INVERTED_TABLE`：若某些 GPIO LED 逻辑反转（高电平熄灭、低电平点亮），需通过此表列出反转的 GPIO 编号

---

### ✅ GPIO 支持（GPIO Support）

* `CFG_SYS_I2C_PCA953X_WIDTH`：针对 PCA953X 类型芯片，指定每个芯片的引脚数（ngpio）

> 注意：若使用的 GPIO 芯片通过 I2C 接入，还需要同时配置 I2C 接口支持。

---

### ✅ I/O 追踪扩展说明（I/O Tracing）

* 追踪功能在 `sandbox` 和 `arm` 架构中已支持。
* 若希望其他架构支持，需在对应的 `arch/<arch>/include/asm/io.h` 文件底部添加：

  ```c++
  #include <iotrace.h>
  ```

---

### ✅ 时间戳功能补充说明（CONFIG\_TIMESTAMP）

* 打印镜像构建时间
* 自动由 `CONFIG_CMD_DATE` 启用
* 使用 `bootm` 或 `iminfo` 命令加载镜像时，会显示 `Timestamp:` 信息

---

接下来是 **磁盘分区表、网络设备、TPM 设备、USB 固件、键盘、I2C 总线与多路复用配置、软件 I2C 配置等内容**，是否继续？

